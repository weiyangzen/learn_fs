# Research: subset-b-004227

Grouped research for memory-controller sources under `sources/distributed-fs/ceph-client/drivers/memory`. Each section preserves the original source path for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/brcmstb_memc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/brcmstb_memc.c

## Purpose
`brcmstb_memc.c` is a Broadcom STB DDR memory-controller helper focused on DDR self-refresh power-down (SRPD). It exposes a small sysfs control plane for the inactivity timeout that triggers SRPD and keeps the setting coherent across suspend and resume.

## Important APIs, Types, And Functions
The main private state is `struct brcmstb_memc`, which stores the device, mapped DDR controller base, configured timeout cycles, advertised memory frequency, and the SoC-version-specific SRPD register offset. `struct brcmstb_memc_data` carries that offset from the OF match table.

`brcmstb_memc_srpd_config()` validates the 16-bit inactivity count, updates `timeout_cycles`, writes the SRPD enable/count field, and reads back the register to flush the posted write. `brcmstb_memc_uses_lpddr45()` reads `REG_MEMC_CNTRLR_CONFIG` to block runtime SRPD changes on LPDDR4/LPDDR5 because those memories depend on dynamic tuning affected by the same timeout. Sysfs attributes are `frequency` read-only and `srpd` read/write. `brcmstb_memc_probe()` allocates state, maps resource 0, reads optional `clock-frequency`, and creates the sysfs group. PM callbacks disable SRPD before system suspend and restore it on resume.

## Control Flow
Probe selects the SRPD offset using `device_get_match_data()`, maps the controller registers, and publishes sysfs files. A user write to `srpd` parses a decimal cycle count, rejects LPDDR4/5 controllers, then writes the timeout and enable bit. Suspend clears only the enable bit when a nonzero timeout exists; resume calls the same programming helper to restore the saved setting.

## State And Persistence
Persistent driver state is in `timeout_cycles`, `frequency`, and the hardware SRPD register. The timeout survives suspend in RAM and is reprogrammed on resume, but it is not persisted across reboot. Sysfs removal is explicit in remove. Hardware writes use relaxed I/O plus a readback barrier.

## Dependencies And Integration Points
The driver integrates with platform-device probing, device tree compatibles for Broadcom DDR controller revisions, sysfs, MMIO helpers, and simple device PM. It depends on the `clock-frequency` device-tree property only for reporting.

## Risks
The LPDDR4/5 check depends on controller configuration values matching the macros. There is no lock around sysfs writes versus suspend/resume, so concurrent writes and PM transitions rely on normal device PM serialization rather than a private mutex. Invalid match data would dereference `memc_data`, though all supported compatibles provide `.data`.

## Test Signals
Useful tests are sysfs read/write of `srpd`, rejection of values above `0xffff`, `-EOPNOTSUPP` on LPDDR4/5 hardware, register value inspection after writes, and suspend/resume verification that SRPD is disabled during suspend and restored afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/brcmstb_memc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/da8xx-ddrctl.c -->
# sources/distributed-fs/ceph-client/drivers/memory/da8xx-ddrctl.c

## Purpose
`da8xx-ddrctl.c` is a small TI DA8xx DDR2/mDDR controller tuning driver. It applies hard-coded board-specific performance register settings where Linux lacks a general framework for these controller knobs.

## Important APIs, Types, And Functions
`struct da8xx_ddrctl_config_knob` describes a named register field: register offset, mask, and shift. `struct da8xx_ddrctl_setting` binds a knob name to a value, and `struct da8xx_ddrctl_board_settings` maps machine compatibles to setting arrays. The only present knob is `da850-pbbpr` at offset `0x20`, and the only board configuration is `ti,da850-lcdk` setting that field to `0x20`.

`da8xx_ddrctl_match_knob()` resolves a setting name to the supported knob table. `da8xx_ddrctl_get_board_settings()` checks `of_machine_is_compatible()` against board settings. `da8xx_ddrctl_probe()` maps the controller resource, validates register offsets against resource size, masks and inserts each setting value, then writes the result.

## Control Flow
Probe first selects a settings array based on the root machine compatible. Without a supported board it returns `-EINVAL`. For each setting it finds a knob, checks the register fits in the mapped resource, reads the current register value, clears or preserves bits according to `mask`, inserts `val << shift`, and writes the register.

## State And Persistence
There is no private runtime state after probe. The only persistent effect is the hardware register programming, which is not saved/restored by this driver and is expected to be reapplied by reprobe after reboot.

## Dependencies And Integration Points
The driver is a platform driver matched by `ti,da850-ddr-controller`, but policy is gated by root-machine compatible. It uses device tree, platform MMIO mapping, and normal Linux module/platform-driver registration.

## Risks
The mask semantics are easy to misread: the code keeps bits covered by `mask` and ORs the shifted value, so adding knobs needs careful review. Unsupported boards fail probe noisily. There is no PM restore path if low-power states reset the DDR controller register.

## Test Signals
Tests should boot on `ti,da850-lcdk`, confirm register `0x20` receives the expected field value, verify unsupported boards return `-EINVAL`, and exercise the resource-size guard by checking that out-of-range knob offsets are skipped with warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/da8xx-ddrctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/dfl-emif.c -->
# sources/distributed-fs/ceph-client/drivers/memory/dfl-emif.c

## Purpose
`dfl-emif.c` implements the Intel FPGA Device Feature List (DFL) private EMIF feature driver. It exposes per-memory-interface sysfs status for initialization and calibration failure, and revision-0-only write triggers for clearing memory.

## Important APIs, Types, And Functions
`struct dfl_emif` contains the device, mapped feature base, and a spinlock protecting `EMIF_CTRL`. `struct emif_attr` embeds a `device_attribute` plus bit shift and channel index, allowing one show/store implementation for all interface attributes.

`emif_state_show()` reads `EMIF_STAT` and returns one bit for `init_done` or `cal_fail`. `emif_clear_store()` accepts only `"1"`, writes the channel clear-enable bit under lock, then polls `EMIF_STAT` until that channel's clear-busy bit clears. Attribute-generation macros create `inf0` through `inf7` status and clear files. `dfl_emif_visible()` hides attributes for absent channels and hides clear attributes for feature revisions greater than zero. `dfl_emif_probe()` maps the DFL MMIO resource and initializes driver data.

## Control Flow
DFL core matches feature id `0x9`. Probe maps resources and sysfs groups are installed via `dev_groups`. Attribute visibility reads the capability/channel mask from offset `0x10`, interpreting it as the revision-0 control register or later capability register. Writes to `infN_clear` serialize the control-register update, then poll with a 5-second timeout.

## State And Persistence
The driver keeps only MMIO base and lock state. Hardware status and clear state live in EMIF registers. Sysfs attributes are dynamically visible based on channel mask and feature revision.

## Dependencies And Integration Points
It depends on DFL device infrastructure, 64-bit MMIO accessors, `readq_poll_timeout()`, sysfs groups, and spinlocks. The ABI is per-channel sysfs under the DFL device.

## Risks
The clear path assumes `EMIF_CTRL_CLEAR_EN` is write-only but preserves other read/write bits by clearing the whole clear field before setting one bit. Incorrect revision or capability interpretation could expose invalid channels. The 5-second polling timeout is the main failure signal for hung hardware.

## Test Signals
Test by probing revision 0 and revision greater than 0 devices, verifying channel-specific visibility, reading `infN_init_done` and `infN_cal_fail`, writing invalid values to `infN_clear`, and checking timeout/error handling when clear-busy never drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/dfl-emif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif-asm-offsets.c -->
# sources/distributed-fs/ceph-client/drivers/memory/emif-asm-offsets.c

## Purpose
`emif-asm-offsets.c` is a tiny build helper used to emit TI EMIF SRAM/assembly offsets. It exists so generated assembly constants stay synchronized with C structure layouts from `linux/ti-emif-sram.h`.

## Important APIs, Types, And Functions
The file includes `linux/ti-emif-sram.h` and calls `ti_emif_asm_offsets()` from `main()`. It defines no runtime driver state and no kernel entry point.

## Control Flow
The generated host/build program starts at `main()`, invokes `ti_emif_asm_offsets()`, and exits with zero. The called helper is expected to print or emit offset definitions as part of the kernel build.

## State And Persistence
There is no runtime state, persistence, MMIO, or device-tree behavior. Its output is a build artifact consumed by low-level EMIF PM assembly code.

## Dependencies And Integration Points
The only integration point is the EMIF SRAM header and the build system rule that compiles and runs offset generators. It is logically coupled to `emif.h` and TI EMIF suspend/resume assembly.

## Risks
Any mismatch between this generator and the assembly consumers can break suspend/resume or self-refresh code at runtime. Because the file is minimal, most risk is in the included header and build-system invocation rather than this source body.

## Test Signals
Build tests should confirm the offset generator compiles for the target configuration and that assembly files consuming the generated offsets assemble successfully. Runtime PM tests indirectly validate that generated offsets match the C layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif-asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif.c -->
# sources/distributed-fs/ceph-client/drivers/memory/emif.c

## Purpose
`emif.c` is the TI EMIF SDRAM controller driver. It configures LPDDR2 SDRAM power-management, ZQ calibration, temperature-alert handling, interrupt reporting, debugfs inspection, and platform or device-tree derived memory timing metadata for EMIF 4D and 4D5 controllers.

## Important APIs, Types, And Functions
`struct emif_data` is the central per-controller state: mapped base, device pointer, platform data, DDR node, temperature level, selected low-power mode, register-cache pointers, debugfs root, and list linkage. Global `emif1`, `device_list`, and `emif_lock` coordinate duplicate EMIF instances and multi-controller frequency-update workarounds.

Key helpers include `get_emif_bus_width()`, `set_lpmode()`, `do_freq_update()`, `get_addressing_table()`, `get_zq_config_reg()`, `get_temp_alert_config()`, and `get_pwr_mgmt_ctrl()`. Temperature logic is in `get_temperature_level()`, `setup_temperature_sensitive_regs()`, `handle_temp_alert()`, and `emif_threaded_isr()`. Device description paths are `of_get_memory_device_details()` and `get_device_details()`. Probe maps MMIO, performs one-time programming, initializes debugfs, disables stale interrupts, and requests a threaded IRQ.

## Control Flow
Probe builds `emif_data` from OF or platform data, validates DDR type/density/IO width/PHY combination, adds it to the global device list, maps registers, gets the IRQ, programs one-time settings, creates debugfs files, clears interrupts, and enables error/temperature IRQs. One-time programming chooses conservative low-power settings, writes ZQ calibration, reads MR4 temperature, writes temperature alert config, and programs fixed IntelliPHY shadow values.

On interrupts, the hard handler clears SYS and optional LL status registers. SYS temperature alerts call `handle_temp_alert()`. Rising temperature can immediately derate shadow timing registers and force a frequency-update sequence; falling temperature and very-high shutdown events are deferred to the threaded handler. The thread either powers off/restarts on over-temperature or reapplies temperature-sensitive timings under `emif_lock`.

## State And Persistence
Driver state is memory-resident and hardware-backed. `temperature_level`, `lpmode`, `curr_regs`, and `regs_cache` track derived runtime state. Debugfs exposes register-cache data and MR4 level. Hardware state includes power-management, ZQ, temperature-alert, interrupt-enable, and shadow timing registers. There is no explicit suspend/resume implementation here, but shutdown disables and clears interrupts. The driver adds EMIFs to `device_list` and sets `emif1`; remove only tears down debugfs, so list/global cleanup is a notable lifecycle gap.

## Dependencies And Integration Points
It depends on `emif.h` register definitions, `jedec_ddr.h` JEDEC tables, `of_memory.c` helpers, platform data from `linux/platform_data/emif_plat.h`, debugfs, IRQ threading, reboot/poweroff APIs, and device-tree properties such as `device-handle`, `phy-type`, `cs1-used`, `cal-resistor-per-cs`, `low-power-mode`, and `extended-temp-part`.

## Risks
Unsupported DDR geometry or PHY revisions fail probe. Missing or malformed DT timing data falls back to JEDEC defaults, which may be conservative but not board-optimal. Temperature handling can shut the system down for non-extended-temperature parts. Global list and `emif1` state are not unwound on remove. Some frequency-update functionality remains TODO, so low-power errata workarounds are partial. Register-cache calculation is represented by structures but not fully populated in this file, making integration with external PM/DVFS code important.

## Test Signals
Signals include probe success on `ti,emif-4d` and `ti,emif-4d5`, debugfs `regcache_dump` and `mr4`, interrupt tests for access errors and temperature alerts, validation of low-power-mode custom properties, fallback warnings for default timings, and over-temperature paths that call poweroff or restart. Removal and reprobe tests should watch stale `device_list` and `emif1` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif.h -->
# sources/distributed-fs/ceph-client/drivers/memory/emif.h

## Purpose
`emif.h` is the private register, bitfield, timing, and SRAM-PM contract header for the TI EMIF driver and related low-level assembly/SRAM code.

## Important APIs, Types, And Functions
The header defines EMIF driver limits such as `EMIF_MAX_NUM_FREQUENCIES`, voltage and timing derating constants, low-power timeout defaults, ZQ calibration constants, temperature polling defaults, PHY magic values, and register offsets for the EMIF MMIO block. It also defines masks and shifts for SDRAM configuration, refresh, timing, power management, LPDDR2 mode register access, interrupts, ZQ, temperature alert, OCP error logs, leveling, and PHY control registers.

The central data type is `struct emif_regs`, which caches frequency-specific shadow register values used for initialization, derating, and DVFS/PM. The header also declares SRAM-related objects and functions: `ti_emif_sram`, `ti_emif_sram_sz`, `ti_emif_pm_sram_data`, `ti_emif_regs_amx3`, and PM routines such as `ti_emif_save_context()`, `ti_emif_restore_context()`, `ti_emif_enter_sr()`, and `ti_emif_exit_sr()`.

## Control Flow
The header has no runtime control flow by itself. Its definitions drive `emif.c` register writes and low-level suspend/resume assembly generated through `emif-asm-offsets.c`.

## State And Persistence
`struct emif_regs` models cached shadow state for several frequencies and temperature derating variants. External SRAM symbols represent persistent low-power code/data areas that survive or operate during EMIF self-refresh transitions.

## Dependencies And Integration Points
The header is consumed by the EMIF platform driver, TI SRAM PM code, and assembly offset generation. It is tightly coupled to `linux/ti-emif-sram.h`, platform data structures, JEDEC timing types, and hardware-specific EMIF 4D/4D5 register layouts.

## Risks
Bitfield constants must exactly match hardware documentation; mistakes can corrupt SDRAM timings or power-management behavior. Magic PHY values are opaque and board/SoC sensitive. The header exposes low-level PM symbols, so structure layout changes require offset-regeneration and suspend/resume validation.

## Test Signals
Compile coverage with EMIF, SRAM PM, and assembly-offset generation enabled is the first signal. Runtime validation includes SDRAM stability during frequency changes, self-refresh entry/exit, context save/restore, and temperature derating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/emif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/fsl-corenet-cf.c -->
# sources/distributed-fs/ceph-client/drivers/memory/fsl-corenet-cf.c

## Purpose
`fsl-corenet-cf.c` reports Freescale/NXP CoreNet Coherency Fabric errors. It enables fabric error interrupts, decodes captured address/source metadata, and logs critical diagnostics.

## Important APIs, Types, And Functions
`enum ccf_version` distinguishes CCF1 and CCF2 hardware. `struct ccf_info` stores version, error-register offset, and whether the BRR register exists. `struct ccf_err_regs` maps the error register block, and `struct ccf_private` stores match info, device, MMIO base, error-register pointer, and T1040 detection.

`ccf_irq()` reads big-endian error-detect, capture attribute, address, and secondary attribute registers, rate-limits logging, decodes LAE/CV/UTID/MCST and source id, clears errors by writing `errdet`, and returns IRQ status. `ccf_probe()` maps registers, selects match data, detects T1040 through `CCF_BRR`, requests the IRQ, and enables appropriate error bits. `ccf_remove()` disables CCF1 or CCF2 interrupts.

## Control Flow
Probe maps the controller, computes the error-register base from the selected hardware version, installs an IRQ, then enables LAE/CV and optional T1040-specific errors. Interrupt handling reads and logs details only when the rate limiter allows, but it always writes `errdet` back to clear captured events.

## State And Persistence
Driver state is `struct ccf_private`; persistent hardware state is interrupt-enable and error-capture registers. There is no suspend/resume support and no sysfs/debugfs surface.

## Dependencies And Integration Points
It integrates with OF compatibles `fsl,corenet1-cf` and `fsl,corenet2-cf`, platform IRQs, big-endian MMIO accessors, Linux ratelimit state, and platform-driver registration.

## Risks
Error metadata interpretation differs by CCF version and T1040 variant. Logging is rate-limited, which protects the system but can hide repeated unique errors. Clearing by writing `errdet` means diagnostic state is consumed by the handler. No PM restore exists if interrupt enables reset.

## Test Signals
Injectable fabric errors should produce critical logs with `errdet`, `cecar`, `cecar2`, address, and source id. Probe tests should cover both compatibles and T1040 BRR detection. Remove should clear interrupt enable paths for both versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/fsl-corenet-cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/fsl_ifc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/fsl_ifc.c

## Purpose
`fsl_ifc.c` is the Freescale Integrated Flash Controller core driver. It maps global and runtime IFC registers, initializes common event reporting, exposes helper symbols for child flash/NAND drivers, dispatches IFC and NAND interrupts, and populates child devices.

## Important APIs, Types, And Functions
The file exports global `fsl_ifc_ctrl_dev`, `convert_ifc_address()`, and `fsl_ifc_find()`. `fsl_ifc_find()` walks CSPR chip-select registers to locate a bank by physical base address. `fsl_ifc_ctrl_init()` clears common chip-select errors and enables common event/error interrupts. `check_nand_stat()` serializes access to NAND event status with `nand_irq_lock`, clears events, stores `ctrl->nand_stat`, and wakes `ctrl->nand_wait`.

`fsl_ifc_ctrl_irq()` handles common IFC chip-select transaction errors, logs read/write, AXI ID, SRC ID, and error address, then also checks NAND status. `fsl_ifc_nand_irq()` handles the dedicated NAND IRQ. Probe maps registers with `of_iomap()`, determines endian mode, reads IFC version, selects bank count and runtime-register offset, maps IRQs, initializes wait queues, requests interrupts, and populates children.

## Control Flow
The driver registers at `subsys_initcall()` so it is available before child flash drivers. Probe maps global registers, configures endian access via fields in `struct fsl_ifc_ctrl`, computes `rregs` from version-specific offsets, initializes common events, requests controller and optional NAND IRQs, then calls `of_platform_default_populate()`. Remove depopulates children, frees IRQs, disposes IRQ mappings, unmaps registers, and clears drvdata.

## State And Persistence
The global controller pointer is shared with child drivers. Hardware state includes common event enable/status registers and NAND runtime event status. Runtime wait state is stored in `nand_wait` and `nand_stat`. State is not persisted or restored across power management in this file.

## Dependencies And Integration Points
It depends on `linux/fsl_ifc.h`, OF address/IRQ helpers, irqdomain mappings, child platform device population, and IFC endian accessor macros. Child NAND/NOR drivers use the exported controller pointer and bank lookup helpers.

## Risks
The single global `fsl_ifc_ctrl_dev` assumes one IFC controller. Error paths manually free IRQs and unmap resources, so ordering is sensitive. `remove()` calls `free_irq()` even for `nand_irq` values that may be zero if absent, so platform behavior should be verified. No PM restore path means event enables may be lost across deep suspend.

## Test Signals
Probe logs IFC version and bank count. Tests should verify endian property handling, bank lookup with valid/invalid CSPR entries, common transaction error logging, NAND IRQ wakeups, child population, and clean unwind when IRQ mapping or request fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/fsl_ifc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr.h -->
# sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr.h

## Purpose
`jedec_ddr.h` provides JEDEC DDR and LPDDR metadata shared by memory-controller drivers and device-tree parsing helpers. It defines density/type/width encodings, mode-register constants, timing structures, and exported JEDEC LPDDR2 table declarations.

## Important APIs, Types, And Functions
The header defines DDR density macros from 64Mb through 32Gb, memory type macros for DDR2/DDR3/LPDDR2/LPDDR3, IO width encodings, row/column/bank constants, refresh and tRFC constants, mode-register numbers, LPDDR2 MR4 temperature masks, manufacturer IDs, and LPDDR2 architecture types.

Important structures are `struct lpddr2_addressing`, `struct lpddr2_timings`, `struct lpddr2_min_tck`, `union lpddr2_basic_config4`, `struct lpddr2_info`, `struct lpddr3_timings`, and `struct lpddr3_min_tck`. It declares `lpddr2_jedec_addressing_table`, `lpddr2_jedec_timings`, `lpddr2_jedec_min_tck`, and `lpddr2_jedec_manufacturer()`.

## Control Flow
The header has no control flow. Consumers use the encoded constants to convert device-tree or mode-register values into controller-specific register settings.

## State And Persistence
It declares immutable JEDEC data tables implemented in `jedec_ddr_data.c`. Structures represent memory part properties and timing state but do not store global mutable state.

## Dependencies And Integration Points
It is used by `emif.c`, `of_memory.c`, and any DDR-capable memory controller needing LPDDR2/LPDDR3 timing descriptions. It depends only on `linux/types.h`.

## Risks
Consumers must consistently distinguish raw JEDEC encodings, device-tree human units, and controller encodings. Density/index conversion mistakes can select the wrong addressing-table row. LPDDR3 structures have no built-in default table in this header.

## Test Signals
Compile coverage plus consumers parsing LPDDR2 and LPDDR3 DT nodes are the main signals. Unit-style checks can validate density and IO-width conversions against expected table indexes and manufacturer names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr_data.c -->
# sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr_data.c

## Purpose
`jedec_ddr_data.c` implements exported LPDDR2 JEDEC addressing, timing, minimum-cycle, and manufacturer-name data used as defaults or reference data by memory-controller drivers.

## Important APIs, Types, And Functions
It defines and exports `lpddr2_jedec_addressing_table`, `lpddr2_jedec_timings`, `lpddr2_jedec_min_tck`, and `lpddr2_jedec_manufacturer()`. The addressing table maps density classes to bank count, refresh interval, and all-bank refresh timing. The timing table covers LPDDR2 speed bins 400, 533, 800, and 1066. The minimum-tCK structure supplies cycle minima for timings such as tRPab, tRCD, tWR, tRRD, tWTR, and tFAW.

## Control Flow
There is no dynamic control flow except `lpddr2_jedec_manufacturer()`, which switches on manufacturer ID constants and returns a static string, defaulting to `"invalid"`.

## State And Persistence
All data is immutable `const` global state exported to other GPL kernel code. There is no runtime allocation or persistence.

## Dependencies And Integration Points
The file includes `jedec_ddr.h` and `linux/export.h`. `emif.c` uses the tables for default timings and addressing calculations; `of_memory.c` falls back to `lpddr2_jedec_min_tck` and `lpddr2_jedec_timings` when DT data is incomplete.

## Risks
The addressing array declares `NUM_DDR_ADDR_TABLE_ENTRIES` as 11 while this initializer provides 10 entries, leaving a zero-filled row if indexed. Consumers must avoid unsupported density/type combinations. Timing values are JEDEC defaults and may not match board-specific margins.

## Test Signals
Tests should confirm exported symbols link, default timing fallback produces four frequency entries, manufacturer IDs return expected names, and each supported EMIF density/type conversion lands on an initialized addressing entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jz4780-nemc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/jz4780-nemc.c

## Purpose
`jz4780-nemc.c` drives the Ingenic JZ4740/JZ4780 NAND/external memory controller. It configures static-memory bank timing and exposes helper APIs for child NAND/SRAM drivers to count banks, select bank type, and assert NAND chip enable.

## Important APIs, Types, And Functions
`struct jz4780_nemc` stores lock, device, SoC info, base, clock, calculated clock period, and banks-present bitmap. `struct jz_soc_info` supplies maximum tAS/tAH cycle counts per SoC.

Exported functions are `jz4780_nemc_num_banks()`, `jz4780_nemc_set_type()`, and `jz4780_nemc_assert()`. Timing helpers include `jz4780_nemc_clk_period()`, `jz4780_nemc_ns_to_cycles()`, and `jz4780_nemc_configure_bank()`. Probe requests only the used register prefix, maps it, clears `NEMC_NFCSR`, enables the clock, parses child address banks, rejects conflicts, configures bank timings, and creates child platform devices.

## Control Flow
Probe iterates available child nodes. For each child it scans `reg` entries via `of_get_address()`, validates bank numbers, checks conflicts with earlier children, applies timing properties to each referenced bank, and creates a child platform device if configuration succeeded. Invalid children are skipped rather than failing the whole controller.

## State And Persistence
Hardware state is SMCR timing/config registers and NFCSR NAND/SRAM/chip-enable state. Runtime state includes clock period and `banks_present`. The clock remains prepared while the driver is bound and is disabled on remove. Child helper calls directly mutate NFCSR.

## Dependencies And Integration Points
It integrates with OF child address parsing, platform child creation, clock framework, and exported `linux/jz4780-nemc.h` types. It registers at `subsys_initcall()` so child drivers can depend on it early.

## Risks
Only 8-bit bus width is accepted despite comments about older SoCs supporting 16-bit. Probe does not depopulate created children on remove. NFCSR helper writes are not protected by the declared spinlock, so concurrent child access can race. Timing conversion depends on a nonzero clock rate.

## Test Signals
Tests should verify invalid/duplicate bank rejection, timing overflow errors for tAS/tAH/tBP/tAW/tSTRV, child creation for valid banks, exported helper behavior, and removal clock disable. NAND tests should verify chip-enable toggling through NFCSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/jz4780-nemc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/mtk-smi.c -->
# sources/distributed-fs/ceph-client/drivers/memory/mtk-smi.c

## Purpose
`mtk-smi.c` is the MediaTek Smart Multimedia Interconnect driver. It manages SMI common and local-arbiter (larb) blocks, configures IOMMU port routing, bus selection, outstanding transaction limits, sleep control, clocks, runtime PM, and component binding to the MediaTek IOMMU stack.

## Important APIs, Types, And Functions
`struct mtk_smi_common_plat` describes common/sub-common SoC data, including generation, GALS clocks, bus selection, and init register table. `struct mtk_smi_larb_gen` describes larb port layout, port-configuration callback, direct-to-common mask, feature flags, and outstanding-limit tables. `struct mtk_smi` holds common state and clocks; `struct mtk_smi_larb` embeds it and adds larb base, common-device link, larb generation data, larb id, MMU bitmap, and bank array.

Larb config functions are generation-specific: gen1 writes secure config in the always-on common region, MT8167/MT8173 write a single MMU-enable register, and gen2-general handles throttling, software flags, OSTD limits, secure-world SMC configuration, and per-port `SMI_LARB_NONSEC_CON` MMU/bank fields. Probe paths are `mtk_smi_larb_probe()` and `mtk_smi_common_probe()`. Runtime PM callbacks enable clocks and restore register programming.

## Control Flow
Both common and larb drivers are registered together. Common probe selects SoC data, gets required clocks, maps either AO or gen2 base, optionally links a sub-common to its parent common, enables runtime PM, and stores drvdata. Larb probe maps registers, gets clocks, device-links to common, enables runtime PM, and registers a component. Component bind receives IOMMU larb metadata and stores the larb id plus MMU/bank pointers. Larb resume enables clocks, disables sleep protection when required, then configures ports.

## State And Persistence
Runtime state is mostly clock/runtime-PM and pointers to IOMMU-provided bitmaps. Hardware state includes common init registers, `SMI_BUS_SEL`, larb sleep-control bits, OSTD limits, secure config, non-secure MMU enable bits, and bank selection. These are restored on runtime resume, not persisted across reboot.

## Dependencies And Integration Points
The driver depends on platform devices, OF compatibles for many MediaTek SoCs, component framework, MediaTek IOMMU data structures from `<soc/mediatek/smi.h>`, runtime PM, clock bulk APIs, device links, and ARM SMCCC secure monitor calls for SoCs with secure port control.

## Risks
Correctness is heavily SoC-table-driven; wrong `bus_sel`, OSTD, flags, or larb masks can break display/camera/media DMA. Secure monitor failures abort port configuration. The source contains a duplicated `for` line in `mtk_smi_larb_config_port_gen2_general()`, which would be a compile-time error if present exactly as read. `put_device(common->smi_common_dev)` is called even when that pointer may be NULL for non-sub-common paths, which should be checked against kernel helper tolerance.

## Test Signals
Tests should include compile coverage, probe order with deferred common devices, component bind with IOMMU larb metadata, runtime suspend/resume clock balancing, secure SMC return handling, and per-SoC register traces for bus selection and larb MMU/bank programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/mtk-smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/mvebu-devbus.c -->
# sources/distributed-fs/ceph-client/drivers/memory/mvebu-devbus.c

## Purpose
`mvebu-devbus.c` configures the Marvell EBU/Orion device bus controller for attached NOR, NAND, SRAM, or FPGA-like devices. It converts device-tree timing properties from picoseconds to controller ticks and programs Orion or Armada register layouts before creating child devices.

## Important APIs, Types, And Functions
`struct devbus` stores device, mapped base, and clock tick in picoseconds. `struct devbus_read_params` and `struct devbus_write_params` hold decoded timing and bus-width values. `get_timing_param_ps()` reads one DT timing property and converts it to ticks. `devbus_get_timing_params()` parses required bus width and timing properties, with extra read setup/hold and sync-enable fields for `marvell,mvebu-devbus`. `devbus_orion_set_timing_params()` and `devbus_armada_set_timing_params()` encode the parsed values for different hardware layouts.

## Control Flow
Probe allocates state, maps registers, enables the clock, computes `tick_ps`, optionally skips programming when `devbus,keep-config` is set, otherwise parses timing data and writes either Orion or Armada registers. It then calls `of_platform_populate()` so children probe after bus timing is programmed.

## State And Persistence
The driver does not keep state after probe beyond devm allocations. Hardware timing registers are persistent until reset or reprogramming. Clock enable is devm-managed.

## Dependencies And Integration Points
It uses platform driver probing, OF timing properties, clock framework, MMIO writes, and child platform population. Supported compatibles are `marvell,mvebu-devbus` and `marvell,orion-devbus`.

## Risks
Timing fields are not range-checked against their register widths before shifting; invalid DT values can truncate into hardware fields. Missing required properties fail probe. The `devbus,keep-config` escape hatch relies on bootloader setup and can hide incorrect DT data.

## Test Signals
Tests should validate tick conversion at expected clock rates, missing-property failures, 8-bit and 16-bit bus-width encoding, Orion extended-bit encoding, Armada read/write register values, `devbus,keep-config` behavior, and child creation ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/mvebu-devbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/of_memory.c -->
# sources/distributed-fs/ceph-client/drivers/memory/of_memory.c

## Purpose
`of_memory.c` provides exported OpenFirmware/device-tree helpers for DDR memory descriptions. It parses LPDDR2 and LPDDR3 timing, minimum-cycle, and chip identity properties into JEDEC structures for memory-controller drivers.

## Important APIs, Types, And Functions
Exported APIs are `of_get_min_tck()`, `of_get_ddr_timings()`, `of_lpddr3_get_min_tck()`, `of_lpddr3_get_ddr_timings()`, and `of_lpddr2_get_info()`. Internal helpers `of_do_get_timings()` and `of_lpddr3_do_get_timings()` parse one timing child node.

LPDDR2 helpers allocate devm structures, read required properties, and fall back to `lpddr2_jedec_min_tck` or `lpddr2_jedec_timings` when allocation or parsing fails. LPDDR3 helpers return NULL on failure rather than a JEDEC default table. `of_lpddr2_get_info()` parses revision IDs, IO width, density, architecture type from compatible strings, and manufacturer from compatible vendor prefixes.

## Control Flow
Timing collection counts compatible child nodes first, allocates an array, then loops again to populate entries. Any missing required property frees the allocation and goes to fallback. LPDDR2 info parsing first handles the newer `revision-id` array with fallback to `revision-id1`/`revision-id2`, then validates mandatory `io-width` and `density`, determines architecture type, scans compatible strings for known vendors, and returns a devm-allocated copy.

## State And Persistence
All returned dynamic structures are devm-managed against the requesting device. Fallback LPDDR2 data points to global const JEDEC tables. The helpers do not persist state across calls.

## Dependencies And Integration Points
The file depends on OF property helpers, `jedec_ddr.h`, `of_memory.h`, devm allocation, and exported symbols. `emif.c` uses these APIs to build platform data from memory device nodes.

## Risks
The helpers require complete timing child nodes; one missing property discards all custom timings. LPDDR2 density and IO-width conversions assume power-of-two values and specific DT units. LPDDR3 has no default fallback, so callers must handle NULL. Vendor detection depends on compatible strings formatted as `vendor,...`.

## Test Signals
Tests should parse complete and incomplete LPDDR2/LPDDR3 nodes, verify fallback warnings and frequency counts, validate deprecated LPDDR3 `reg` max-frequency fallback, and confirm `of_lpddr2_get_info()` encodes manufacturer, density, IO width, and revisions as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/of_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/of_memory.h -->
# sources/distributed-fs/ceph-client/drivers/memory/of_memory.h

## Purpose
`of_memory.h` declares the device-tree DDR parsing helper API and supplies NULL-returning stubs when `CONFIG_OF` or `CONFIG_DDR` is disabled.

## Important APIs, Types, And Functions
The header declares LPDDR2 APIs `of_get_min_tck()`, `of_get_ddr_timings()`, and `of_lpddr2_get_info()`, plus LPDDR3 APIs `of_lpddr3_get_min_tck()` and `of_lpddr3_get_ddr_timings()`. The disabled-configuration stubs preserve buildability for callers but return NULL for all helper calls.

## Control Flow
There is no runtime control flow in enabled builds beyond external function calls. In disabled builds, inline stubs immediately return NULL.

## State And Persistence
The header defines no state. Returned object ownership and persistence are controlled by `of_memory.c` through devm allocations or global const fallbacks.

## Dependencies And Integration Points
It is used by memory-controller drivers such as TI EMIF and depends on type visibility for `struct device_node`, `struct device`, LPDDR2/LPDDR3 timing structures, and `u32` from included kernel headers in consumers.

## Risks
Callers must handle NULL stubs when OF or DDR support is disabled. The include guard closing comment has a typo, but the guard macro itself is correct. Because the header does not include `jedec_ddr.h`, consumers must include required type definitions before or alongside it.

## Test Signals
Build both enabled and disabled `CONFIG_OF`/`CONFIG_DDR` combinations. Static analysis should verify all callers handle NULL timing/info pointers from stubs or parsing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/of_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c

## Purpose
`omap-gpmc.c` is the Texas Instruments General-Purpose Memory Controller driver. It manages chip-select address windows, GPMC timing programming, NAND/OneNAND integration, wait-pin GPIOs, a nested IRQ domain, device-tree child probing, and context save/restore for OMAP core power transitions.

## Important APIs, Types, And Functions
Global controller state includes `gpmc_base`, `gpmc_l3_clk`, `gpmc_cs[]`, `gpmc_mem_root`, `gpmc_cs_num`, `gpmc_nr_waitpins`, `gpmc_capability`, and `gpmc_irq_domain`. `struct gpmc_device` stores device, IRQ, irq/gpio chips, CPU PM notifier, saved context, wait pins, IRQ count, suspend flag, and optional data resource.

Exported APIs include `gpmc_cs_write_reg()`, `gpmc_calc_divider()`, `gpmc_cs_set_timings()`, `gpmc_cs_request()`, `gpmc_cs_free()`, `gpmc_configure()`, `gpmc_omap_get_nand_ops()`, `gpmc_omap_onenand_set_timings()`, `gpmc_calc_timings()`, `gpmc_cs_program_settings()`, and `gpmc_read_settings_dt()`. Major internal areas are chip-select memory allocation/remap, timing conversion and programming, IRQ domain setup, DT child probing, wait-pin GPIO registration, and OMAP3 context save/restore.

## Control Flow
Probe maps configuration registers, stores an optional data window resource, gets IRQ and `fck`, reads DT `gpmc,num-cs` and `gpmc,num-waitpins`, allocates wait-pin state, enables runtime PM, reads revision/capabilities, initializes the memory resource tree from existing bootloader chip-select mappings, registers wait-pin GPIOs, creates the IRQ domain and parent IRQ, probes DT children, and registers a CPU PM notifier.

Child probing parses `reg`, requests/remaps a chip-select, reads GPMC settings/timings from DT, optionally preserves bootloader timings if no `cs-rd-off` timing exists, handles NAND-specific bus width and write-protect, reserves wait pins, programs non-timing settings, programs timing registers, clears limited-address mode, enables the CS, and creates child platform devices.

## State And Persistence
Chip-select mappings are represented both in hardware CONFIG7 registers and in Linux resource objects under `gpmc_mem_root`. Wait pins are tracked as GPIO descriptors to allow sharing only with matching polarity. IRQ enable/status is managed through a nested irq domain. OMAP3 context save/restore records global and per-CS registers across CPU cluster PM and system sleep. Runtime PM gates the controller around suspend/resume.

## Dependencies And Integration Points
The driver integrates with OF, platform devices, MTD NAND platform data, GPMC public headers, GPIO provider APIs, irqdomain/generic IRQ APIs, CPU PM notifiers, runtime PM, clock framework, and child NAND/OneNAND/NOR drivers. It exports symbols consumed by memory and flash child drivers.

## Risks
The driver relies on several global single-controller variables, so multiple GPMC instances would be unsafe. Timing conversions mix ps and ns and retain legacy conversion paths. Child-probe failures can leave partially configured chip selects if cleanup misses a path. IRQ handling calls `generic_handle_irq()` even after warning about unmapped virqs, so virq-zero behavior should be considered. `gpmc_cs_set_reserved()` ignores its `reserved` argument and only sets the flag, so `gpmc_cs_free()` does not actually clear reservation through that helper. DT timing omissions intentionally preserve bootloader setup but can hide incomplete descriptions.

## Test Signals
Strong signals include DT probe with valid/invalid `num-cs` and waitpins, chip-select allocation/remap/resource collision tests, timing overflow errors, NAND register map retrieval, OneNAND sync timing programming, wait-pin GPIO reads and sharing validation, nested IRQ delivery for NAND and wait pins, context save/restore across suspend and CPU cluster PM, and child cleanup on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/pl172.c -->
# sources/distributed-fs/ceph-client/drivers/memory/pl172.c

## Purpose
`pl172.c` drives ARM PrimeCell MPMC/EMC variants PL172, PL175, and PL176 for static memory chip-select configuration. It programs bus width, static memory mode flags, and per-chip-select timing registers from device tree, then populates child devices.

## Important APIs, Types, And Functions
`struct pl172_data` stores mapped base, clock rate in kHz-like units for timing conversion, and the `mpmcclk`. `pl172_timing_prop()` reads an ns timing property, converts it to cycles using the clock rate, subtracts the hardware-specific start offset, validates against register maximum, and writes the wait register. `pl172_setup_static()` programs config flags and all timing properties for one CS. `pl172_parse_cs_config()` reads `mpmc,cs` and validates it. `pl172_probe()` enables the clock, requests AMBA regions, maps registers, sets drvdata, configures each available child node, and populates successful children.

## Control Flow
AMBA probe identifies revision strings by PrimeCell part/revision, allocates state, gets `mpmcclk`, requests and maps AMBA resources, then loops through child nodes. Each child must have a valid chip select and `mpmc,memory-width`; failed children are skipped, not fatal to the controller.

## State And Persistence
The only long-lived runtime state is mapped base and clock. Hardware static config and wait registers persist until reset or reprogramming. AMBA region release is registered with `devm_add_action_or_reset()`.

## Dependencies And Integration Points
The driver integrates with AMBA bus matching, clock framework, OF child nodes, and platform child population. Supported IDs cover PL172, PL175, and PL176.

## Risks
Timing conversion depends on clock-rate units and can reject valid boards if the rate is unexpected. Missing `mpmc,memory-width` or `mpmc,cs` skips children. Existing child devices are not explicitly depopulated on remove because the driver has no remove callback.

## Test Signals
Tests should include probe on each AMBA ID/revision, valid 8/16/32-bit widths, timing maximum overflow detection, optional flag programming, child population only after successful CS setup, and AMBA region release on probe error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/pl172.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/pl353-smc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/pl353-smc.c

## Purpose
`pl353-smc.c` is the ARM PL353 static memory controller wrapper used by Xilinx platforms. It enables required clocks, instantiates one supported child device, and handles clock gating for suspend/resume.

## Important APIs, Types, And Functions
`struct pl353_smc_data` stores `memclk` and `aclk`. `pl353_smc_probe()` obtains enabled `apb_pclk` and `memclk`, stores drvdata, scans available child nodes, accepts `cfi-flash` or `arm,pl353-nand-r2p1`, creates the first matching child platform device, and fails if none match. PM callbacks disable clocks on suspend and re-enable `aclk` then `memclk` on resume with rollback if memory clock enable fails.

## Control Flow
AMBA probe allocates state and enables clocks through devm clock helpers. It loops over children with scoped OF iteration, warns for unsupported children, creates the first supported child, and breaks. Suspend/resume only handles clock state; no SMC register programming is performed here.

## State And Persistence
Runtime state is clock pointers. Hardware register state is not saved/restored by this file. Child devices own their own flash/NAND state.

## Dependencies And Integration Points
The driver integrates with AMBA matching ID `0x00041353`, OF child nodes, clock framework, platform child creation, and simple dev PM ops. It is a parent for CFI flash and PL353 NAND children.

## Risks
Only a single child is supported; additional valid children are ignored after the first match. No child depopulation is implemented in remove because there is no remove callback. Resume depends on clock enable ordering and rolls back only `aclk` if `memclk` fails.

## Test Signals
Tests should verify probe with flash and NAND child nodes, failure with no supported children, warning for unsupported children, clock enable/disable balance, and resume failure rollback when `memclk` cannot be enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/pl353-smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if-regs.h -->
# sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if-regs.h

## Purpose
`renesas-rpc-if-regs.h` defines register offsets and bitfield constructors for the Renesas R-Car/RZ RPC Interface memory controller used by SPI, HyperFlash, and Octa/DDR-capable direct or manual access paths.

## Important APIs, Types, And Functions
The header defines offsets for common control/status (`RPCIF_CMNCR`, `RPCIF_SSLDR`, `RPCIF_CMNSR`), direct-read path registers (`RPCIF_DRCR`, `RPCIF_DRCMR`, `RPCIF_DREAR`, `RPCIF_DROPR`, `RPCIF_DRENR`, `RPCIF_DRDMCR`, `RPCIF_DRDRENR`), manual mode registers (`RPCIF_SMCR`, `RPCIF_SMCMR`, `RPCIF_SMADR`, `RPCIF_SMOPR`, `RPCIF_SMENR`, read/write data registers, `RPCIF_SMDMCR`, `RPCIF_SMDRENR`), and PHY control/status (`RPCIF_PHYADD`, `RPCIF_PHYWR`, `RPCIF_PHYCNT`, `RPCIF_PHYOFFSET1`, `RPCIF_PHYOFFSET2`, `RPCIF_PHYINT`).

Most macros are field constructors, for example command/opcode insertion, bus-width selection, dummy-cycle programming, burst length, PHY memory mode, Octa/DDR/high-speed options, and RZ/G2L-specific clock selection.

## Control Flow
The header has no control flow. It is included by the RPC-IF implementation that performs regmap/MMIO programming.

## State And Persistence
It defines no state. The macros describe hardware register state managed by the consuming driver.

## Dependencies And Integration Points
It depends on `linux/bits.h` for `BIT()` and `GENMASK()`. The corresponding implementation file `renesas-rpc-if.c` uses these definitions for hardware initialization, direct mapping, manual transactions, PHY setup, and PM restore.

## Risks
Field constructors mask inputs but do not validate semantic ranges such as burst length before subtracting one. Some fields are documented as only valid on specific SoCs, so consumers must select macros according to compatible data. Register offset comments reflect availability differences across R-Car and RZ/G2 variants.

## Test Signals
Compile coverage of RPC-IF consumers is the main direct signal. Hardware tests should verify manual read/write transactions, direct-map reads, dummy-cycle programming, PHY calibration bits, Octa/DDR mode setup, and SoC-specific fields on R-Car versus RZ/G2L devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if-regs.h -->
