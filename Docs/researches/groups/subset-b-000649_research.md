# subset-b-000649 Research

Grouped source research for subset B work item `subset-b-000649`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c

## Purpose
Registers the single OMAP1 I2C controller as an `omap_i2c` platform device and supports boot-command overrides for bus speed. It bridges board files and the generic `i2c-omap` driver by supplying fixed OMAP1 register, IRQ, mux, and IP-version data.

## Important APIs, Types, and Functions
Exports `omap_i2c_add_bus()`, `omap_register_i2c_bus()`, and `omap_register_i2c_bus_cmdline()`. Important state is `i2c_pdata[]`, the one-element `omap_i2c_devices[]`, `i2c_resources[]`, and the `OMAP_I2C_CMDLINE_SETUP` flag stored in `clkrate`.

## Control Flow
`omap_register_i2c_bus()` first registers `i2c_board_info`, records the default clock rate unless the command line already set one, clears the command-line marker, and calls `omap_i2c_add_bus()`. `omap_i2c_add_bus()` muxes SDA/SCL, fills MEM and IRQ resources, sets OMAP1 driver flags, attaches platform data, and registers the device. The `i2c_bus=` setup hook records deferred bus requests that `subsys_initcall` later materializes.

## State and Persistence Behavior
Persistent kernel state is the static platform-data array, the command-line marker bit, and registered platform devices. Hardware state includes muxed I2C pins and the driver's later register programming; this file itself does not retain runtime transfer state.

## Dependencies and Integration Points
Depends on the platform bus, `i2c_register_board_info()`, `platform_device_register()`, `INT_I2C`, OMAP1 mux entries `I2C_SDA`/`I2C_SCL`, and `linux/platform_data/i2c-omap.h` flag definitions.

## Risks
`bus_id > 1` returns `-EINVAL` even though the static pdata array has four entries, so OMAP1 effectively supports one controller here. Shared `i2c_resources[]` and `omap_i2c_devices[]` assume no duplicate registration. Bad `i2c_bus=` parsing silently ignores malformed options.

## Test Signals
Boot an OMAP1 config with and without `i2c_bus=1,<kHz>` and confirm one `omap_i2c` platform device, IRQ `INT_I2C`, MEM `0xfffb3800-0xfffb383f`, and expected `i2c-omap` probe flags. A negative test should pass `bus_id=2` or malformed command-line values and verify no stray controller registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h

## Purpose
Provides the OMAP1 board-facing declarations for I2C controller registration while compiling to harmless stubs when `CONFIG_I2C_OMAP` is disabled or modularly unavailable.

## Important APIs, Types, and Functions
Declares `struct i2c_board_info`, `struct omap_i2c_bus_platform_data`, `omap_i2c_add_bus()`, `omap_register_i2c_bus()`, and `omap_register_i2c_bus_cmdline()`. The enabled path exposes real functions; the disabled path returns success from inline stubs.

## Control Flow
There is no runtime flow in the header. Its control path is compile-time selection based on `CONFIG_I2C_OMAP` or `CONFIG_I2C_OMAP_MODULE`, allowing board code to call registration helpers without open-coding `#ifdef` blocks.

## State and Persistence Behavior
The header owns no state. It defines the call contract that lets `i2c.c` maintain command-line and platform-device state.

## Dependencies and Integration Points
Integrates OMAP1 board files with the I2C core and `i2c-omap` platform data. It relies on `u32` being visible from includers or earlier kernel headers.

## Risks
Disabled stubs return `0`, so board code cannot tell that no I2C device was registered. This is intentional for optional subsystem builds but can hide missing config dependencies in board bring-up.

## Test Signals
Compile OMAP1 with `CONFIG_I2C_OMAP=y`, `m`, and `n`; board files should build in all cases and only enabled builds should produce registered platform devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c

## Purpose
Identifies OMAP1 CPU family, variant, die revision, and serial ID from hardware ID registers during early boot. The resulting `omap_revision` drives CPU feature macros used by the rest of the mach-omap1 code.

## Important APIs, Types, and Functions
Exports `omap_rev()`. Main internals are `struct omap_id`, the `omap_ids[]` lookup table, `omap_get_jtag_id()`, `omap_get_die_rev()`, and `omap_check_revision()`.

## Control Flow
`omap_check_revision()` reads JTAG ID, die revision, and OMAP32 ID, saves die IDs into `system_serial_high/low`, then refines `omap_revision` in three passes: major JTAG match, JTAG plus die revision, and full JTAG/die/omap_id match. It appends class bits for 7xx, 15xx, or 16xx and prints the detected SoC.

## State and Persistence Behavior
State is the static `omap_revision` exported through `omap_rev()` and global ARM `system_serial_*` values. It also consumes immutable hardware identity registers.

## Dependencies and Integration Points
Uses OMAP1 raw register helpers from `omap1-io.h`, addresses from `hardware.h`, and common CPU predicates in `soc.h`/`common.h`. Other files such as IRQ, mux, PM, USB, and SRAM depend on the revision result.

## Risks
Several chips have broken or ambiguous production and die ID registers, so fallback logic is critical. A missing table entry can classify only by broad family or emit `Unknown OMAP cpu type`, which can select wrong IRQ banks or SRAM size.

## Test Signals
Boot known OMAP1510, 1610/1611/5912, 1710, and 7xx hardware or emulated register sets and assert `omap_rev()` class bits and log output. Unit-style tests can stub `omap_readl()` to cover broken PROD_ID and DIE_ID fallbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c

## Purpose
Sets up the static OMAP1 IO mappings and exposes legacy physical-address read/write helpers used by older mach-omap1 code.

## Important APIs, Types, and Functions
Defines `omap1_map_io()`, `omap1_init_early()`, `omap1_init_late()`, and exported `omap_readb/w/l()` plus `omap_writeb/w/l()` helpers.

## Control Flow
`omap1_map_io()` installs common IO, DSP, and DSP register mappings. `omap1_init_early()` calls `omap_check_revision()` and clears TIPB bridge control registers for an OMAP5910 erratum. `omap1_init_late()` initializes serial wake support. Accessor helpers translate physical addresses through `OMAP1_IO_ADDRESS()` and issue raw MMIO operations.

## State and Persistence Behavior
Static mappings persist for the life of the kernel. Early init writes TIPB bridge state once; late init may set up serial wake IRQs through `serial.c`.

## Dependencies and Integration Points
Uses ARM `iotable_init()`, `map_desc`, `OMAP1_IO_ADDRESS`, DSP mapping constants, `tc.h`, and common revision/serial wake helpers.

## Risks
The exported raw physical-address helpers bypass ioremap lifetime tracking and ordering semantics. Bad addresses can fault or touch unintended registers. The TIPB workaround is early and unconditional for OMAP1, so address definitions must match actual silicon.

## Test Signals
Boot smoke tests should verify early printk/serial still work, no mapping faults occur, and `/proc/iomem` or debug traces show expected device mappings. Static checks should ensure no new drivers depend on these legacy helpers when normal `ioremap()` is possible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h

## Purpose
Defines the common physical, virtual, and size constants for the OMAP1 IO window used by early static mappings and direct physical-address helpers.

## Important APIs, Types, and Functions
Provides `OMAP1_IO_PHYS`, `OMAP1_IO_SIZE`, and `OMAP1_IO_VIRT`. It is a constants-only header.

## Control Flow
No runtime flow. `io.c` consumes these constants to populate `map_desc`, while low-level address macros use the same window for register access.

## State and Persistence Behavior
No software state. The constants describe the persistent static mapping contract for the OMAP1 IO region.

## Dependencies and Integration Points
Requires `OMAP1_IO_OFFSET` from the broader OMAP hardware headers. It integrates with ARM MMU setup and `OMAP1_IO_ADDRESS()` translations.

## Risks
A wrong offset or size corrupts all OMAP1 register access. Because many files use absolute register addresses, this header is a central boot-critical dependency.

## Test Signals
Build-time coverage is inclusion in OMAP1 configs. Runtime validation is early boot through revision detection, timer init, and serial init without data aborts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c

## Purpose
Implements the OMAP1 MPU interrupt controller integration, including bank selection per SoC, legacy irqdomain creation, interrupt dispatch, masking, wake support, and bank-specific trigger setup.

## Important APIs, Types, and Functions
Key entry points are `omap1_init_irq()` and IRQ entry `omap1_handle_irq()`. Internal helpers include `omap_ack_irq()`, `omap_mask_ack_irq()`, `omap_irq_set_cfg()`, `omap_alloc_gc()`, and bank MMIO accessors.

## Control Flow
Initialization chooses interrupt banks based on `cpu_is_*`, ioremaps each bank, allocates legacy IRQ descriptors/domain, masks and clears banks, programs ILR trigger/priority values from `trigger_map`, installs generic irqchips, unmasks the L2 cascade, and sets the ARM IRQ handler. The IRQ handler loops pending L1 interrupts, resolves FIQ/IRQ source registers, follows the L2 cascade when needed, and calls `generic_handle_domain_irq()`.

## State and Persistence Behavior
Static state tracks `irq_banks`, `irq_bank_count`, `omap_l2_irq`, and `domain`; each bank tracks mapped base, trigger map, and wake-enable cache via generic irqchip.

## Dependencies and Integration Points
Depends on `irqs.h` numbering, `hardware.h` register offsets, ARM exception dispatch, generic irqchip, irqdomain legacy mapping, and revision detection from `id.c`.

## Risks
Wrong CPU detection or trigger maps can leave interrupts masked, mis-triggered, or routed to wrong Linux IRQs. The code assumes at least two banks when clearing L2/control state. Ioremap failure returns early without a full IRQ controller.

## Test Signals
Boot each enabled OMAP1 family and verify timer, GPIO, UART, DMA, I2C, and cascade IRQs arrive. Suspend tests should cover `irq_set_wake`. Negative testing can force ioremap/allocation failure in fault-injection builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h

## Purpose
Defines the legacy Linux IRQ number map for OMAP1510, OMAP1610, and OMAP7xx interrupt handler banks, including cascaded GPIO and MPUIO ranges.

## Important APIs, Types, and Functions
Exports `INT_*` macros, `IH2_BASE`, `IH_GPIO_BASE`, `IH_MPUIO_BASE`, `OMAP_IRQ_END`, `OMAP_IRQ_BIT()`, and optional `FIQ_START`.

## Control Flow
No runtime flow. The macros are consumed at compile time by platform-device resource tables, IRQ controller setup, PM wake masks, timers, serial, I2C, MMC, DMA, and USB code.

## State and Persistence Behavior
No state; it is the shared interrupt numbering contract for OMAP1.

## Dependencies and Integration Points
Depends on `NR_IRQS_LEGACY`. Integrates with `irq.c` legacy domain allocation, platform resources, and board files.

## Risks
Macro collisions or off-by-one cascade offsets cause drivers to request the wrong IRQ. The header mixes variants, so callers must choose CPU-specific names carefully.

## Test Signals
Compile all OMAP1 variant configs and boot hardware smoke tests for core device IRQs. Static checks should verify platform resources use variant-appropriate interrupt names.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c

## Purpose
Registers OMAP1 McBSP audio/serial port platform devices with fixed memory, IRQ, DMA resources and OMAP1-specific DSP clock request/free operations.

## Important APIs, Types, and Functions
Defines OMAP1 `omap_mcbsp_ops` with `.request`/`.free`, resource tables for 15xx and 16xx, `omap_mcbsp_register_board_cfg()`, and `arch_initcall` `omap1_mcbsp_init()`.

## Control Flow
Initialization exits on non-OMAP1, selects 15xx or 16xx resource tables, allocates a platform-device pointer array, creates `omap-mcbsp` devices, adds resources, sets register width/step, attaches platform data, and registers each device. McBSP1/3 request paths enable `api_ck` and `dsp_ck` on first use and release them on last free.

## State and Persistence Behavior
Persistent state includes `dsp_use`, cached `api_clk`/`dsp_clk`, and the allocated `omap_mcbsp_devices` array. Hardware state includes DSP reset-control bits and enabled clocks for DSP public peripherals.

## Dependencies and Integration Points
Depends on clock framework names `api_ck`/`dsp_ck`, IRQ macros, DMA request numbers, `asoc-ti-mcbsp` platform data, and CPU revision predicates.

## Risks
Clock get failures are tolerated but can leave DSP public McBSP access broken. `dsp_use` is not protected by a lock and assumes serialized McBSP request/free paths. Resource tables must match SoC variant exactly.

## Test Signals
Probe ASoC McBSP on OMAP15xx and OMAP16xx, exercise McBSP1/2/3 playback/capture, and verify clock enable counts return to zero after close. Resource validation should check IRQ/DMA names `rx` and `tx`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mcbsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h

## Purpose
Provides OMAP1 MMC controller constants and the optional `omap1_init_mmc()` declaration used by board files.

## Important APIs, Types, and Functions
Defines controller counts, base addresses, register size, and a real or stub `omap1_init_mmc(struct omap_mmc_platform_data **, int)` depending on `CONFIG_MMC_OMAP`.

## Control Flow
No runtime flow in the header. Board code calls `omap1_init_mmc()` and either registers controllers in enabled builds or compiles to a no-op when the driver is absent.

## State and Persistence Behavior
No state. Runtime state is owned by the implementation and MMC core.

## Dependencies and Integration Points
Depends on `linux/mmc/host.h` and `linux/platform_data/mmc-omap.h`; consumers rely on the base/size constants for OMAP1 controller registration.

## Risks
The no-op stub can hide missing MMC support. Fixed controller counts differ between OMAP15xx and OMAP16xx, so board code must pass the right number of platform-data entries.

## Test Signals
Build with `CONFIG_MMC_OMAP` enabled and disabled. On OMAP16xx, verify both base addresses can be registered when requested; on OMAP15xx, verify only one controller is exposed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h

## Purpose
Supplies OMAP1 architecture primitives for MTD execute-in-place delay and idle handling without relying on normal kernel services that may be unavailable while flash is busy.

## Important APIs, Types, and Functions
Defines `xip_omap_mpu_timer_regs_t`, `xip_omap_mpu_timer_read()`, `xip_irqpending()`, `xip_currtime()`, `xip_elapsed_since()`, and `xip_cpu_idle()`.

## Control Flow
XIP delay code reads MPU timer 0, computes elapsed time from the inverted down-counter, checks pending unmasked IH1 interrupts, and can idle the CPU with ARM CP15 wait-for-interrupt.

## State and Persistence Behavior
No persistent software state. It directly observes MPU timer and interrupt-controller hardware state through OMAP1 IO mappings.

## Dependencies and Integration Points
Included indirectly by `linux/mtd/xip.h`; depends on `hardware.h`, `omap1-io.h`, MPU timer register layout, and IH1 interrupt registers.

## Risks
The elapsed-time conversion is explicitly approximate and timer-frequency dependent. Because it is used in constrained XIP contexts, calling normal kernel APIs here would be unsafe; all macros must remain low-level.

## Test Signals
Build XIP-enabled OMAP1 kernels and run flash erase/program operations while confirming timer delays, interrupt pending detection, and idle wake behavior do not hang.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.c

## Purpose
Contains the OMAP1 pin multiplexing table and applies mux, pull, and pull-up/down register settings for board and subsystem initialization.

## Important APIs, Types, and Functions
Exports `omap_cfg_reg()`. Init/API helpers are `omap_mux_register()`, `omap1_mux_init()`, and internal `omap1_cfg_reg()`. The data table `omap1xxx_pins[]` lists named mux entries for UART, USB, GPIO, MPUIO, MMC, camera, I2C, keypad, and other functions.

## Control Flow
`omap1_mux_init()` installs the OMAP15xx/16xx mux table. `omap_cfg_reg(index)` validates CPU class, table presence, and index range, then calls `omap1_cfg_reg()`. The low-level function writes mux bits, optional 1610 pull-up/down select bits, and pull-enable bits under a spinlock, emitting warnings/debug when a setting changes.

## State and Persistence Behavior
Static state is `mux_cfg` and `arch_mux_cfg`. Hardware state is persistent pin configuration in FUNC_MUX, PULL_DWN, and PU_PD registers.

## Dependencies and Integration Points
Depends on `linux/soc/ti/omap1-mux.h`, register constants from `hardware.h`, raw `omap_readl/writel`, CPU predicates, and entry indexes generated by mux headers.

## Risks
Wrong mux indexes can break board pins, UART console, wake lines, or USB/MMC routing. Pull-register semantics are inverted in places, and some entries document silicon errata, so table changes are high risk.

## Test Signals
Boot with `CONFIG_OMAP_MUX_WARNINGS`/`DEBUG` to audit changed pins, then verify UART, I2C, MMC, USB, keypad, and GPIO board functions. Negative tests should call invalid indexes in debug builds and expect errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h

## Purpose
Defines the OMAP1 pin-mux table schema, helper macros for mux/pull register fields, and declarations for mux initialization.

## Important APIs, Types, and Functions
Provides `MUX_CFG`, `MUX_CFG_7XX`, `struct pin_config`, `struct omap_mux_cfg`, `omap1_mux_init()`, `omap_mux_register()`, and `omap2_mux_init()` declarations.

## Control Flow
Compile-time macros expand concise table entries into `pin_config` initializers. Runtime flow is implemented in `mux.c`, which consumes the structures and register metadata generated here.

## State and Persistence Behavior
No state; it defines the structure of mux state that `mux.c` stores globally and writes to hardware.

## Dependencies and Integration Points
Depends on `linux/soc/ti/omap1-mux.h` for register constants and on optional debug config for register-name fields.

## Risks
Macro argument order is dense and easy to misuse: mux register, bit offset, mode, pull register, pull bit, pull state, pu/pd select, and debug flag. Incorrect metadata can silently program the wrong register bits.

## Test Signals
Compile with and without `CONFIG_OMAP_MUX_DEBUG` to ensure structure layout consumers match. Validate new table entries against TRM register fields and with runtime mux debug output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c

## Purpose
Provides minimal OMAP16xx OCPI interconnect setup, primarily to allow OHCI USB access through the OCP bridge.

## Important APIs, Types, and Functions
Exports `ocpi_enable()`. Module lifecycle functions are `omap_ocpi_init()` and `omap_ocpi_exit()`.

## Control Flow
`omap_ocpi_init()` exits on non-16xx, gets and enables `l3_ocpi_ck`, calls `ocpi_enable()`, and logs availability. `ocpi_enable()` clears low protection/security bits in OCPI registers to allow peripheral bus access. Exit disables and releases the clock.

## State and Persistence Behavior
State is the retained `ocpi_ck` pointer and modified OCPI protection/security registers. The code does not restore OCPI register values on module exit.

## Dependencies and Integration Points
Uses the clock framework, OMAP1 raw IO helpers, CPU predicates, and is called by USB OHCI platform data through `usb.c`.

## Risks
Only OMAP16xx is supported. The protection/security writes are broad (`~0xff`) and affect access policy for the bridge. Clock acquisition failure prevents OCPI setup and can break USB host DMA/register access.

## Test Signals
On OMAP16xx with OHCI enabled, verify `l3_ocpi_ck` enablement, `ocpi_enable()` success, and USB host enumeration. Non-16xx tests should return `-ENODEV`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ocpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c

## Purpose
Implements the legacy OMAP system DMA platform API and OMAP1 system DMA platform driver, including channel allocation, register programming helpers, start/stop, interrupt dispatch, and command-line channel reservation.

## Important APIs, Types, and Functions
Exports `omap_request_dma()`, `omap_free_dma()`, `omap_set_dma_transfer_params()`, source/destination parameter and burst/pack helpers, `omap_start_dma()`, `omap_stop_dma()`, position queries, `omap_get_dma_active_status()`, `omap_dma_running()`, and `omap_get_plat_info()`.

## Control Flow
The platform driver probe consumes `omap_system_dma_plat_info`, applies channel reservation and 1510 mode flags, allocates `dma_chan[]`, clears channel registers, maps named IRQs, and requests per-channel IRQ handlers. Clients request a free channel under `dma_chan_lock`, configure DMA registers through `p->dma_read/write`, start transfers with IRQ enable and memory barriers, and stop by clearing CCR with errata-specific drain handling. IRQ dispatch reads CSR, handles 1510 shadow channels, logs timeout/drop events, clears active state on block IRQ, and calls client callbacks.

## State and Persistence Behavior
Global state includes platform info `p`, attributes `d`, `errata`, `dma_chan[]`, counts, `enable_1510_mode`, command-line `omap_dma_reserve_channels`, and per-channel dev_id/callback/IRQ/link/saved CSR fields. Hardware state is all SDMA logical channel registers and OMAP16xx dynamic GDMA mux registers.

## Dependencies and Integration Points
Depends on `linux/omap-dma.h`, platform resources named by channel, OMAP1 TC priority registers, clock/device errata flags, LCD DMA helper `omap_lcd_dma_running()`, USB-OMAP consumers, and command-line `omap_dma_reserve_ch=`.

## Risks
This is a deprecated platform DMA API and warns unless the client is `DMA engine`. Channel arrays are global and low-level register writes are SoC-specific. Several paths use `BUG()` on invalid burst modes. Position reads can race running channels unless callers disable interrupts as documented.

## Test Signals
Probe with OMAP15xx and OMAP16xx platform data, request/free all channels, run memory/peripheral DMA through USB or audio clients, verify callbacks and CSR status bits, test `omap_dma_reserve_ch=`, and run suspend idle checks that `omap_dma_running()` blocks deep idle while active.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h

## Purpose
Defines the OMAP1 MPU operating-point/rate-table structure shared by clock setup code and the OMAP1 rate data file.

## Important APIs, Types, and Functions
Provides `struct mpu_rate` with MPU rate, crystal rate, PLL rate, CKCTL value, DPLL_CTL value, and flags, plus extern `omap1_rate_table[]`.

## Control Flow
No runtime flow. Clock code iterates the table declared here to select valid OMAP1 clock register settings.

## State and Persistence Behavior
No state in the header. It describes immutable rate-table entries held in `opp_data.c`.

## Dependencies and Integration Points
Uses Linux integer types and flag values such as `CK_1710`, `CK_16XX`, `CK_1510`, and `CK_7XX` from clock headers.

## Risks
Structure field order is hardware-sensitive: wrong CKCTL or DPLL_CTL values can destabilize CPU, DSP, peripheral, or LCD clocks.

## Test Signals
Build clock code that consumes `omap1_rate_table[]`; runtime cpufreq/clock tests should verify selected rates match crystal frequency and SoC flags.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c

## Purpose
Provides the static OMAP1 MPU clock rate table used by legacy clock/cpufreq code to program DPLL and divider registers for supported SoCs and crystals.

## Important APIs, Types, and Functions
Defines `omap1_rate_table[]`, a sentinel-terminated array of `struct mpu_rate` entries.

## Control Flow
No active control flow in this file. Consumers scan entries by SoC flag and crystal rate, then program `CKCTL` and `DPLL_CTL` with the selected values.

## State and Persistence Behavior
Read-only data persists in kernel memory. Hardware state changes happen in clock code that uses the table.

## Dependencies and Integration Points
Depends on `clock.h` flag definitions and `opp.h` structure layout.

## Risks
The table encodes hardware timing policy. Incorrect flag coverage or divider values can overclock/underclock subsystems, break SDRAM timing assumptions, or select unsupported rates for a board crystal.

## Test Signals
For each supported crystal and SoC class, verify table lookup selects expected MPU/DPLL rates and that clock reprogramming keeps timers, serial, and memory stable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c

## Purpose
Implements OMAP1 idle and suspend-to-RAM support, including dynamic idle sysfs control, wake-source masking, register save/restore, SRAM suspend function installation, and debugfs PM register reporting.

## Important APIs, Types, and Functions
Exports/defines `omap1_pm_idle()` and `omap1_pm_suspend()`. Kernel integration points include `platform_suspend_ops`, `arm_pm_idle`, sysfs `power/sleep_while_idle`, debugfs `pm_debug/omap_pm`, and `__initcall omap_pm_init()`.

## Control Flow
Idle disables FIQ, adjusts IDLECT masks for timers and DMA activity, either performs shallow WFI with temporary IDLECT writes or calls the SRAM suspend routine. Suspend enables serial wake muxing, disables IRQ/FIQ, saves MPUI/ARM/ULPD/DSP registers, stops DSP clocks, programs wake masks, disables watchdog, calls SRAM assembly, restores clocks/registers/masks, re-enables interrupts, and restores serial muxing. Init installs SRAM-copied suspend code, sets idle/suspend ops, requests wake IRQ, configures ULPD/IDLECT3, creates debugfs/sysfs, and muxes `LOW_PWR` on 16xx.

## State and Persistence Behavior
Static save arrays hold ARM, DSP, ULPD, and MPUI register snapshots. `enable_dyn_sleep` persists the sysfs idle policy, and `omap_sram_suspend` points at executable SRAM code. Hardware state includes interrupt masks, clock/idlect registers, DSP reset/clock state, watchdog mode, ULPD power control, and serial wake muxing.

## Dependencies and Integration Points
Depends on DMA activity checks, timer capability macros, `sleep.S` routines copied by `sram-init.c`, mux entries, serial wake helpers, interrupt numbers, clocksource timer helpers, suspend core, debugfs, and CPU predicates.

## Risks
Suspend touches many always-on and memory-controller registers with IRQs disabled; wrong save/restore ordering can hang resume. Dynamic idle is only enabled when 32k and DMTIMER support exist. Wake masks are board-generic and may miss board-specific wake sources.

## Test Signals
Run suspend/resume and idle tests on OMAP15xx and OMAP16xx with serial, GPIO/keypad, UART2, and peripheral wake. Validate `sleep_while_idle` accepts only 0/1, debugfs register snapshots update, and active DMA prevents deep idle.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h

## Purpose
Defines OMAP1 PM register addresses, bit masks, sleep constants, save-state enumerations, save/restore macros, and suspend/idle declarations shared by C and assembly PM code.

## Important APIs, Types, and Functions
Important APIs are `ARM_SAVE/RESTORE/SHOW`, `DSP_SAVE/RESTORE/SHOW`, `ULPD_SAVE/RESTORE/SHOW`, `MPUI1510_*`, `MPUI1610_*`, declarations for `omap1_pm_idle()`, `omap1_pm_suspend()`, `omap1510_cpu_suspend()`, and `omap1610_cpu_suspend()`.

## Control Flow
Compile-time constants guide both `pm.c` and `sleep.S`. Save/restore macros index the static arrays in `pm.c`; assembly offset constants let SRAM code write IDLECT and memory-controller registers.

## State and Persistence Behavior
No own state, but enumerations define the layout of PM save arrays. The assembly-visible constants must stay in sync with the C suspend code.

## Dependencies and Integration Points
Depends on OMAP1 IO address translation, clock/PM register definitions, and optional `CONFIG_OMAP_SERIAL_WAKE` stubs.

## Risks
Changing enum order or constants without updating consumers corrupts suspend save/restore. Assembly constants use physical-to-virtual encoded addresses and are boot-critical.

## Test Signals
Build with OMAP15xx and OMAP16xx PM enabled, assemble `sleep.S`, and run suspend/resume. Debugfs output from `pm.c` should match the enum-backed save slots.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c

## Purpose
Installs a default runtime PM domain for OMAP1 platform devices using the PM clock framework, so devices can gate interface/function clocks named `ick` and `fck`.

## Important APIs, Types, and Functions
Defines a `dev_pm_domain` using `USE_PM_CLK_RUNTIME_OPS` and `USE_PLATFORM_PM_SLEEP_OPS`, a `pm_clk_notifier_block`, and `core_initcall omap1_pm_runtime_init()`.

## Control Flow
At core init, OMAP1-only code registers a PM clock notifier on `platform_bus_type`. Devices later bound to the platform bus can have clocks associated and managed through the default PM domain.

## State and Persistence Behavior
Persistent state is the registered notifier and default PM domain. Clock state is managed by PM core callbacks rather than this file directly.

## Dependencies and Integration Points
Depends on runtime PM, PM clock framework, platform bus, clock names `ick` and `fck`, and `cpu_class_is_omap1()`.

## Risks
Devices without matching clocks or with nonstandard clock names get limited benefit. Registering this too broadly would affect non-OMAP1 devices, hence the CPU-class guard.

## Test Signals
Boot OMAP1 with runtime PM enabled and verify platform devices can runtime suspend/resume with `ick`/`fck` clocks toggled. Non-OMAP1 builds should return `-ENODEV`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c

## Purpose
Provides OMAP1 restart and last-reset-source decoding for reboot and watchdog integration.

## Important APIs, Types, and Functions
Defines `omap1_restart(enum reboot_mode, const char *)` and `omap1_get_reset_sources()`.

## Control Flow
Restart applies an OMAP5912/1611B workaround by disabling a DPLL control bit and writing `ARM_RSTCT1`, then triggers global software reset. Reset-source decoding reads `ARM_SYSST` and maps POR, external reset, ARM watchdog, and global software reset bits into standardized OMAP reset-source IDs.

## State and Persistence Behavior
No persistent software state. It writes reset control registers and reads retained reset status bits.

## Dependencies and Integration Points
Depends on OMAP1 hardware register definitions, `omap_readw/writew`, `OMAP1_IO_ADDRESS`, common CPU predicates, and reboot/watchdog consumers.

## Risks
Restart is final and does not return. The OMAP5912 workaround affects traffic-controller frequency behavior and must happen before reset. Reset-source mapping depends on ARM_SYSST bit definitions.

## Test Signals
Trigger cold, warm, watchdog, and external resets where possible and verify watchdog-reported reset-source bits. Reboot OMAP5912-class hardware repeatedly to check the workaround avoids bad post-reset frequency state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c

## Purpose
Initializes OMAP1 internal UARTs as 8250 platform ports, manages UART clocks and reset/autoconfiguration, and optionally reroutes UART RX pins to GPIO wake inputs during deep sleep.

## Important APIs, Types, and Functions
Defines `omap_serial_init()`, platform registration `arch_initcall omap_init()`, and under `CONFIG_OMAP_SERIAL_WAKE`, `omap_serial_wake_trigger()` plus `omap_serial_wakeup_init()`.

## Control Flow
Early serial init adjusts baud clocks for 15xx, ioremaps each UART, gets/enables its clock, programs clock rates, and resets UART registers for 8250 autoconfig. The later arch init registers the `serial8250` platform device. Wake support requests GPIO wake descriptors/IRQs and toggles mux entries between UART RX and GPIO before/after suspend.

## State and Persistence Behavior
Static clock pointers record which UARTs were initialized. `serial_platform_data[]` persists mapbase, membase, IRQ, and clock settings. Wake GPIO descriptors are acquired during wake init and IRQ wake is enabled.

## Dependencies and Integration Points
Depends on 8250 platform driver, clock names `uart1_ck`/`uart2_ck`/`uart3_ck`, mux entries, GPIO descriptors named `wakeup`, IRQ macros, and PM hooks in `pm.c`.

## Risks
UART2 pins can conflict with USB2 on Innovator-1510. Clock get failures are logged but port reset still proceeds if mapped. Wake muxing only supports OMAP16xx and assumes GPIO lookup tables are provided.

## Test Signals
Boot with early console and 8250 console on each UART, verify clock rates on 15xx/16xx, suspend/resume with serial wake enabled, and test USB2/UART2 pin-conflict board configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h

## Purpose
Defines OMAP1 serial constants used by debug low-level code and UART platform setup, including scratch offset, register shifts, base baud values, and encoded UART IDs.

## Important APIs, Types, and Functions
Provides `OMAP_UART_INFO_OFS`, `OMAP_PORT_SHIFT`, `OMAP7XX_PORT_SHIFT`, `OMAP1510_BASE_BAUD`, `OMAP16XX_BASE_BAUD`, `OMAP1UART1/2/3`, and declaration `omap_serial_init()`.

## Control Flow
No runtime flow. Boot/decompress/debug code and `serial.c` consume the constants to locate and configure UARTs.

## State and Persistence Behavior
No state. The `OMAP_UART_INFO_OFS` describes a RAM scratch location used by debug/uncompress paths.

## Dependencies and Integration Points
Integrates with DEBUG_LL `uncompress.h` and `debug-macro.S`, plus OMAP1 8250 registration.

## Risks
The scratch offset must not overlap decompressor memory. Wrong base baud or register shift breaks early console and 8250 autoconfig.

## Test Signals
Build DEBUG_LL for UART1/2/3 and confirm early `printascii` output before paging and normal 8250 console after boot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S

## Purpose
Implements the low-level OMAP1510 and OMAP1610 CPU suspend routines that are copied to internal SRAM and executed while external memory or clocks may be unavailable.

## Important APIs, Types, and Functions
Exports assembly entries `omap1510_cpu_suspend`, `omap1510_cpu_suspend_sz`, `omap1610_cpu_suspend`, and `omap1610_cpu_suspend_sz` when the corresponding SoC configs are enabled.

## Control Flow
Each routine saves registers, programs traffic-controller and SDRAM self-refresh state, writes ARM IDLECT registers to request deep sleep, executes CP15 wait-for-interrupt, then resumes at the next instruction, restores IDLECT and memory-controller state, restores registers, and returns. The 1610 path drains write cache and includes 74 NOPs for a documented wake erratum.

## State and Persistence Behavior
Uses the caller's stack and hardware register state only. It relies on `pm.c` passing saved `ARM_IDLECT1/2` values in `r0/r1` and on being copied to SRAM by `omap_sram_push()`.

## Dependencies and Integration Points
Depends on constants from `pm.h`, `iomap.h`, and `hardware.h`; called indirectly through `omap_sram_suspend` in `pm.c`.

## Risks
This code runs in the most fragile suspend context. Any stack, address, or timing error can hang resume. Constants must remain assembly-safe and match actual mapped IO addresses.

## Test Signals
Suspend/resume on OMAP1510 and OMAP1610-class devices, including repeated cycles and wake IRQ sources. Disassembly checks should confirm size symbols cover the intended function bodies for SRAM copy.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h

## Purpose
Small compatibility include that pulls OMAP1 hardware and IRQ definitions together while noting that `linux/soc/ti/omap1-soc.h` can replace it once drivers are fixed.

## Important APIs, Types, and Functions
No new symbols. It includes `hardware.h`, `irqs.h`, and `asm/irq.h`.

## Control Flow
No runtime flow. It is an include aggregation point.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Provides transitive access to hardware and IRQ constants for many mach-omap1 files.

## Risks
Because it is a broad include, removing or changing it can expose hidden include-order dependencies. It also perpetuates legacy local header coupling.

## Test Signals
Compile all mach-omap1 users after any include cleanup and check that CPU predicates, IRQ constants, and register definitions remain visible where needed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c

## Purpose
Detects, maps, protects, and allocates internal OMAP1 SRAM, then installs the SRAM-resident clock reprogramming routine used by low-level clock changes.

## Important APIs, Types, and Functions
Defines `omap_sram_push()`, `omap_sram_reprogram_clock()`, and `omap1_sram_init()`. Internal helpers include `omap_sram_push_address()` and `omap_detect_and_map_sram()`.

## Control Flow
Init determines SRAM size from CPU type, maps physical SRAM executable with `__arm_ioremap_exec`, preserves the bootloader area, clears the rest, marks it read-only/executable, copies `omap1_sram_reprogram_clock` into the top of SRAM using `fncpy`, and stores the function pointer. `omap_sram_push()` allocates downward, temporarily makes target pages writable, copies code, then restores ROX permissions.

## State and Persistence Behavior
Static SRAM allocator state tracks base, physical start, skip, size, and ceiling. `_omap_sram_reprogram_clock` is the installed callable SRAM function pointer.

## Dependencies and Integration Points
Depends on CPU revision detection, ARM `fncpy`, executable mappings, `set_memory_rw/rox`, cache/TLB helpers, and assembly symbols from `sram.S`.

## Risks
SRAM size probing is avoided because secure SRAM writes can hang; wrong CPU classification can overrun SRAM. The allocator is simple and not reclaiming. Function copy alignment and page permissions are boot-critical.

## Test Signals
Boot OMAP15xx and OMAP16xx, verify SRAM mapping succeeds, clock reprogramming through `omap_sram_reprogram_clock()` works, and suspend code can also be pushed without `Not enough space in SRAM`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S

## Purpose
Provides the OMAP1 SRAM-resident clock reprogramming routine that safely updates DPLL_CTL and ARM_CKCTL while executing from internal SRAM.

## Important APIs, Types, and Functions
Exports `omap1_sram_reprogram_clock` and size symbol `omap1_sram_reprogram_clock_sz`.

## Control Flow
The routine saves registers, computes virtual addresses for DPLL_CTL and ARM_CKCTL, optionally clears the DPLL lock bit to enter bypass, writes CKCTL and DPLL values, delays for settling, polls lock when requested, then restores registers and returns.

## State and Persistence Behavior
No software state beyond registers and stack. Hardware state is DPLL and clock-control register programming.

## Dependencies and Integration Points
Copied and called by `sram-init.c`; depends on OMAP1 IO address macros and register constants.

## Risks
Clock reprogramming from normal memory could fail while clocks/memory are unstable, hence SRAM execution. Incorrect argument order, lock polling, or address constants can hang the CPU.

## Test Signals
Compare copied size against symbol, call through `omap_sram_reprogram_clock()` for known safe rate transitions, and verify DPLL lock and timer/serial continuity after changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h

## Purpose
Declares OMAP1 SRAM helpers and assembly symbols used by clock and PM initialization.

## Important APIs, Types, and Functions
Declares `omap_sram_reprogram_clock()`, `omap1_sram_init()`, `omap_sram_push()`, `omap1_sram_reprogram_clock()`, and `omap1_sram_reprogram_clock_sz`.

## Control Flow
No runtime flow. It exposes the C-level callable wrappers and warns consumers not to call raw assembly symbols directly.

## State and Persistence Behavior
No state; state is held in `sram-init.c`.

## Dependencies and Integration Points
Requires `u32` and size types from includers. Bridges C code with `sram.S` symbols.

## Risks
The raw assembly declaration order in the comment area is easy to misuse; callers should use the wrapper so the function has been copied to SRAM first.

## Test Signals
Compile all clock/PM users and verify unresolved assembly symbols are present only when OMAP1 SRAM support is linked.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h

## Purpose
Defines OMAP1 Traffic Controller register addresses, external memory chip-select ranges, and EMIFS helper bit macros.

## Important APIs, Types, and Functions
Provides `TCMIF_BASE`, priority/config registers, `EMIFS_CCS(n)`, `EMIFS_ACS(n)`, chip-select physical/size constants, and EMIFS config bits.

## Control Flow
No runtime flow. DMA priority, suspend assembly, PM save/restore, and board memory setup consume the constants to program memory/interconnect behavior.

## State and Persistence Behavior
No state. Describes memory-controller and traffic-controller hardware layout.

## Dependencies and Integration Points
Used by `pm.c`, `sleep.S`, `omap-dma.c`, `io.c`, and memory/flash board code. Requires size macros such as `SZ_64M` from kernel headers when used.

## Risks
Wrong addresses or chip-select sizes can corrupt memory timing, flash mappings, or DMA bus priority. Assembly users rely on constants remaining integer-literal friendly.

## Test Signals
Compile C and assembly consumers; on hardware, validate flash/SDRAM access, suspend self-refresh, and DMA priority changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c

## Purpose
Initializes OMAP1 timer infrastructure, preferring the 32 kHz timer when available and falling back to MPU timers for clockevents, clocksource, and sched_clock.

## Important APIs, Types, and Functions
Defines `omap1_timer_init()` plus MPU timer clockevent/clocksource helpers under `CONFIG_OMAP_MPU_TIMER`.

## Control Flow
`omap1_timer_init()` initializes OMAP1 clocks and mux, calls `omap_32k_timer_init()`, and falls back to `omap_mpu_timer_init()` on failure. MPU timer init gets `ck_ref`, halves its rate for PTV, configures timer1 as clockevent with IRQ `INT_TIMER1`, and timer2 as a free-running down-count clocksource and sched_clock.

## State and Persistence Behavior
Static clockevent structure persists after registration. Hardware state includes MPU timer control/load registers and requested timer IRQ.

## Dependencies and Integration Points
Depends on clock framework, clockevents/clocksource/sched_clock, `omap_32k_timer_init()`, IRQ macros, and `omap1_clk_init()`/`omap1_mux_init()`.

## Risks
A missing `ck_ref` triggers `BUG_ON`. Incorrect rate division skews timekeeping. If neither 32k nor MPU timer works, boot timekeeping fails.

## Test Signals
Boot with 32k timer available and unavailable, verify clocksource selection, tick interrupts, oneshot/periodic modes, and stable sched_clock. Run timer interrupt and delay calibration checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c

## Purpose
Registers OMAP16xx dual-mode timer platform devices and provides a low-level hook for selecting each timer input clock source.

## Important APIs, Types, and Functions
Defines `omap1_dm_timer_set_src()` and `arch_initcall omap1_dm_timer_init()` that creates eight `omap_timer` platform devices.

## Control Flow
Init exits unless CPU is OMAP16xx. It loops timer IDs 1-8, maps each ID to a base address and IRQ, allocates a platform device, adds MEM/IRQ resources, allocates DMTIMER platform data, sets `set_timer_src` and capability flags, attaches data, and registers the device. Clock-source selection updates two-bit fields in `MOD_CONF_CTRL_1` based on timer ID.

## State and Persistence Behavior
No global state after registration beyond platform devices and their copied platform data. Hardware state changes when clients call `set_timer_src`.

## Dependencies and Integration Points
Depends on DMTIMER platform data, `clocksource/timer-ti-dm.h`, OMAP16xx IRQ macros, `MOD_CONF_CTRL_1`, and platform bus.

## Risks
Partial failure stops registration and frees only the current pdev/pdata; already registered timers remain. Timer base/IRQ mapping must match OMAP16xx documentation.

## Test Signals
On OMAP16xx, verify eight `omap_timer` devices probe, each IRQ fires, and clock-source changes update `MOD_CONF_CTRL_1`. Non-16xx boot should skip registration cleanly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer32k.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer32k.c

## Purpose
Implements the OMAP16xx 32 kHz OS timer clockevent and synchronized 32 kHz counter clocksource/persistent clock.

## Important APIs, Types, and Functions
Defines `omap_32k_timer_init()` plus clockevent callbacks, IRQ handler, sched_clock reader, `omap_read_persistent_clock64()`, and `omap_init_clocksource_32k()`.

## Control Flow
Init maps the 32k sync counter on OMAP16xx, enables `omap_32ksync_ick` if present, selects the counter register offset based on revision scheme bits, registers `32k_counter` as clocksource/sched_clock/persistent clock, then registers the OS timer clockevent and IRQ `INT_OS_TIMER`. Clockevent callbacks write load/control registers for periodic or oneshot operation.

## State and Persistence Behavior
Static state includes `sync32k_cnt_reg`, `persistent_ts`, previous `cycles`, and conversion mult/shift. Hardware state includes 32k timer load/control registers and sync counter clock.

## Dependencies and Integration Points
Depends on OMAP16xx only, clocksource/clockevents/sched_clock, persistent clock registration, clock `omap_32ksync_ick`, and IRQ macros.

## Risks
1510 and 730 lack the continuous sync counter and return `-ENODEV`. Persistent time is monotonic only across reads using a 32-bit counter delta. Register-offset detection must match IP revision.

## Test Signals
Boot OMAP16xx and verify `32k_counter` clocksource at 32768 Hz, tick interrupts, oneshot mode, suspend/resume persistent time advancement, and fallback to MPU timers on unsupported CPUs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer32k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c

## Purpose
Performs platform-level OMAP1 full-speed USB initialization for UDC, OHCI, and OTG, including pin muxing, transceiver mode programming, clock/power setup, and platform-device registration.

## Important APIs, Types, and Functions
Exports `omap1_usb_init()`. Important helpers are `omap_otg_init()`, `omap1_usb0_init()`, `omap1_usb1_init()`, `omap1_usb2_init()`, OMAP1510 local-bus setup/reset helpers, and device init functions for UDC/OHCI/OTG.

## Control Flow
`omap1_usb_init()` clones board USB config, installs port-init callbacks and platform-device pointers, then dispatches to OMAP16xx OTG init or OMAP1510 init. Port helpers mux pins and update `USB_TRANSCEIVER_CTRL`/SYSCON mode bits according to wire count, device/host role, alternate pin group, and CPU variant. OMAP16xx OTG init programs OTG_SYSCON registers, gates clocks idle, and registers UDC/OHCI/OTG devices as requested. OMAP1510 init programs HMC mode, DPLL/APLL USB clocking, optional local-bus MMU offset for OHCI DMA, and registers devices.

## State and Persistence Behavior
State persists in allocated copied `omap_usb_config`, static platform devices/resources, DMA masks, and hardware mux/transceiver/clock registers. OMAP1510 OHCI also uses local-bus MMU table state.

## Dependencies and Integration Points
Depends on board-supplied `omap_usb_config`, mux entries, `ocpi_enable()` for OHCI, USB UDC/OHCI/OTG configs, DMA direct offset APIs, IRQ macros, ULPD/MOD/OTG register definitions, and CPU predicates.

## Risks
USB pin wiring is board-specific and many wire counts are invalid for ports. UART/USB pin conflicts and documented USB2 errata can break devices. DPLL lock polling can hang if USB clock setup is wrong. OMAP1510 local-bus memory-size assumption is fixed at 32 MB.

## Test Signals
Test UDC, OHCI, and OTG modes on 1510, 1611/5912, and 1710 boards with 2/3/4/6-wire configs. Verify platform devices register only when requested, DPLL locks, OHCI DMA works, and invalid wire counts log errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h

## Purpose
Provides OMAP1 USB declarations and constants for board code and USB platform initialization.

## Important APIs, Types, and Functions
Defines `is_usb0_device(config)` depending on `CONFIG_USB_OMAP`, declares or stubs `omap1_usb_init()`, and provides OHCI base constants with `OMAP_OHCI_BASE` set to the OMAP1 address.

## Control Flow
No runtime flow. Compile-time config chooses whether USB init is callable and whether USB0 should be treated as device-capable.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on OMAP1 USB platform-data headers and the USB support configuration.

## Risks
The comment notes `is_usb0_device()` is a simplification and the correct answer depends on HMC/OTG mode. This can affect transceiver pull-up/pull-down setup.

## Test Signals
Build with USB support enabled and disabled. Board tests should verify USB0 role handling for the configured HMC mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Kconfig

## Purpose
Defines the OMAP2+ architecture, SoC, board, PM, AVS, errata, and typical-configuration options that control which mach-omap2 code and platform features are built.

## Important APIs, Types, and Functions
Key symbols include `ARCH_OMAP2`, `ARCH_OMAP3`, `ARCH_OMAP4`, `SOC_OMAP5`, `SOC_AM33XX`, `SOC_AM43XX`, `SOC_DRA7XX`, `ARCH_OMAP2PLUS`, `ARCH_OMAP2PLUS_TYPICAL`, `SOC_HAS_OMAP2_SDRC`, SmartReflex options, board options such as `MACH_NOKIA_N8X0`, and errata options.

## Control Flow
Kconfig selection controls compile-time dependency flow: SoC choices select shared `ARCH_OMAP2PLUS`, CPU architecture support, interrupt controllers, PM/OPP, interconnect, timers, reset, and board features. Menus scope options under OMAP2+ and variant-specific dependencies.

## State and Persistence Behavior
No runtime state; selected symbols persist in the kernel `.config` and drive object inclusion and preprocessor branches.

## Dependencies and Integration Points
Interacts with ARM multi-platform symbols, PM, OPP, GIC, interconnect, pinctrl, reset controller, clocksource, regulator, MFD, CPU idle, and board symbols.

## Risks
Incorrect `select` chains can build code without required frameworks or hide missing dependencies. Board defaults such as Nokia N8x0 enabling N810 variants affect legacy platform data.

## Test Signals
Run `make olddefconfig` and build representative OMAP2, OMAP3, OMAP4, AM33xx, AM43xx, OMAP5, and DRA7 configs. Check that selected objects in `Makefile` match the intended symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile

## Purpose
Maps OMAP2+ Kconfig symbols to the architecture objects that implement common setup, clocks, PRCM, power/voltage/clock domains, PM, restart, board support, hwmod data, and platform quirks.

## Important APIs, Types, and Functions
Exports no C API but defines build composition variables such as `hwmod-common`, `clock-common`, `secure-common`, `omap-4-5-common`, PM common groups, PRCM groups, and per-SoC `obj-*` object lists.

## Control Flow
Kbuild evaluates symbols and adds common objects first, then SoC-specific restart, SRAM, PM, PRCM, voltage/power/clockdomain, clock, OPP, hwmod, board, PHY, USB, and IOMMU objects. It also generates `pm-asm-offsets.h` for AM33xx/AM43xx sleep assembly.

## State and Persistence Behavior
No runtime state. Build output state is the object set linked into `vmlinux` and generated offset headers.

## Dependencies and Integration Points
Depends directly on Kconfig symbols from this directory and subsystem configs such as MCBSP, TWL4030, CPCAP, PM_OPP, CPU_IDLE, OMAP_IOMMU, and TUSB6010.

## Risks
Object inclusion order and conditional grouping are critical; missing common objects can break unresolved symbols only in specific SoC configs. Generated PM offsets must be available before sleep objects build.

## Test Signals
Build matrix across OMAP2/3/4/5, AM33xx, AM43xx, DRA7, with PM and CPU_IDLE toggled. Use `make W=1` to catch stale object dependencies and generated-header ordering issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c

## Purpose
Implements AM33xx restart behavior, including a pinmux workaround for Advisory 1.0.36 before issuing a PRM system reset.

## Important APIs, Types, and Functions
Defines `am33xx_restart(enum reboot_mode, const char *)` and internal `am33xx_advisory_1_0_36()`.

## Control Flow
Restart first reads EMU0/EMU1 pin control registers. If either pin is not in EMU mode, it clears the mux mode bits to switch GPIO3_7/GPIO3_8 back to EMU inputs, delays 5 ms for pull-ups, stores reboot mode in `prm_reboot_mode`, and calls `omap_prm_reset_system()`.

## State and Persistence Behavior
Persistent hardware state before reset is the EMU pin mux mode. Software state is `prm_reboot_mode`, consumed by PRM reset handling.

## Dependencies and Integration Points
Depends on AM335x pinctrl register offsets, control-module read/write helpers, PRM reset APIs, and `mdelay()`.

## Risks
If EMU pins are driven low as GPIO outputs at reset sampling, the SoC may reboot into the wrong mode; this workaround must run very late and quickly. It cannot fully control external board pull-ups.

## Test Signals
Reboot AM33xx systems with EMU pins previously muxed as GPIO low/high and verify normal boot mode. Confirm `reboot_mode` reports warm behavior from board-generic machine descriptor.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h

## Purpose
Collects AM33xx and AM43xx base physical addresses for slow L4, control module, PRCM, and TAP blocks.

## Important APIs, Types, and Functions
Defines `L4_SLOW_AM33XX_BASE`, `AM33XX_SCM_BASE`, `AM33XX_CTRL_BASE`, `AM33XX_PRCM_BASE`, `AM43XX_PRCM_BASE`, and `AM33XX_TAP_BASE`.

## Control Flow
No runtime flow. Address constants are consumed by map/control/PRCM/TAP setup code.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrates with AM33xx/AM43xx IO mapping and register access helpers.

## Risks
Incorrect base addresses break early control-module and PRCM access and can prevent boot or reset.

## Test Signals
Build AM33xx/AM43xx configs and verify early init can map/read control and PRCM registers without data aborts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c

## Purpose
Provides generic Device Tree machine descriptors for OMAP2/3/4/5, AM33xx, AM43xx, DRA7, TI81xx, and special N900 handling, wiring early init, IO mapping, timers, IRQs, restart, and machine init callbacks.

## Important APIs, Types, and Functions
Defines many `DT_MACHINE_START` descriptors, `omap_generic_init()`, `omap_init_time_of()`, optional `tick_broadcast()`, N900 ATAG helpers, and compatibility arrays.

## Control Flow
For each compatible family, the ARM machine descriptor calls reserve/map_io/init_early/init_irq/init_machine/init_late/init_time/restart callbacks appropriate for that SoC. `omap_generic_init()` applies pdata quirks and registers the SoC device. `omap_init_time_of()` initializes clocks and probes DT timers. N900 reserve saves ATAGs and system revision before normal OMAP reserve.

## State and Persistence Behavior
Machine descriptors are init data. Runtime state affected includes saved ATAGs for N900, `system_rev`, registered SoC device, clocks, timers, and pdata quirks.

## Dependencies and Integration Points
Depends on common OMAP init functions, DT compatible strings, irqchip init, timer probe, L2 cache secure write hooks, SMP ops, restart functions, and pdata quirks.

## Risks
Compatible-string ordering determines which machine descriptor matches. Wrong callbacks can select wrong IO map, restart, timer, or IRQ path. N900 preserves legacy userspace contracts via `/proc/atags` and board name.

## Test Signals
Boot DTBs for each compatible family and verify selected machine name, clock/timer init, irqchip, restart behavior, and SoC device registration. N900 tests should verify ATAG export and `system_rev`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c

## Purpose
Provides legacy platform-data initialization for Nokia N800/N810/N810 WiMAX OMAP2420 boards, covering TUSB6010 USB, SPI WLAN, Menelaus PMIC, MMC slot multiplexing/power, and GPIO lookup tables.

## Important APIs, Types, and Functions
Key entry points are `n8x0_legacy_init()` and `omap_late_initcall n8x0_late_initcall()`. Important helpers include `board_check_revision()`, `n8x0_usb_init()`, MMC power/bus/cover callbacks, Menelaus late-init voltage/sleep setup, and callback registration.

## Control Flow
Legacy init identifies the board by DT compatible, registers SPI board info, and returns MMC platform data. Late init initializes MMC slot data, TUSB6010 USB interface, and ASoC GPIO lookups. MMC late init programs Menelaus slot selection, power rails, slot modes, initial cover state, and card-change callback. Power callbacks route slot 0 through Menelaus on all boards and slot 1 through Menelaus or GPIO depending on N800/N810.

## State and Persistence Behavior
Static state includes `board_caps`, cover-open flags, `mmc_device`, `mmc1_data`, GPIO lookup tables, Menelaus platform data, and board SPI info. Hardware state includes PMIC regulators, MMC slot muxing, GPIO power controls, and TUSB6010 interface setup.

## Dependencies and Integration Points
Depends on Menelaus MFD APIs, OMAP MMC platform data, GPIO lookup tables, TUSB6010 setup, MUSB platform data, SPI board registration, and DT machine compatible checks.

## Risks
Board variant detection drives slot naming and power behavior; a wrong compatible can power the wrong rail. Menelaus callbacks can `BUG()` on unexpected MMC voltage or bus mode. Cover-state bits are inverted until first switch change and handled specially.

## Test Signals
Boot N800, N810, and N810 WiMAX DTs; verify board_caps, SPI p54spi registration, TUSB6010 enumeration, MMC slot power/cover events, Menelaus regulator sleep setup, and N810 internal MoviNAND `ban_openended` behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c

## Purpose
Defines OMAP2xxx DPLL clock hardware operations for allowing or denying automatic DPLL idle.

## Important APIs, Types, and Functions
Provides `const struct clk_hw_omap_ops clkhwops_omap2xxx_dpll` with `.allow_idle` and `.deny_idle` callbacks.

## Control Flow
`_allow_idle()` validates the clock and DPLL data pointer, then programs CM to allow DPLL automatic low-power stop. `_deny_idle()` similarly disables DPLL autoidle.

## State and Persistence Behavior
No private state. Hardware state is the CM DPLL autoidle setting.

## Dependencies and Integration Points
Depends on OMAP2xxx CM helper functions and TI OMAP clock hardware structures.

## Risks
Callbacks silently do nothing for missing DPLL data, which avoids crashes but can hide clock registration problems. Wrong autoidle state can affect latency or power.

## Test Signals
Clock framework tests should call allow/deny idle on OMAP2xxx DPLLs and verify CM autoidle bits. Invalid/null DPLL-data paths should be harmless.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c

## Purpose
Implements OMAP2xxx composite DPLL/core clock rate calculation and reprogramming, coordinating DPLL settings with SDRC timing changes.

## Important APIs, Types, and Functions
Defines `omap2xxx_clk_get_core_rate()`, `omap2_dpllcore_recalc()`, `omap2_reprogram_dpllcore()`, and `omap2xxx_clkt_dpllcore_init()`.

## Control Flow
Init stores the DPLL/core clock hardware pointer. Core-rate calculation reads the DPLL rate and CORE clock source, handling 32 kHz, DPLL, or DPLL x2. Reprogramming handles simple x1/x2 source flips with SDRC reprogramming, or validates a new rate, builds temporary PLL/SDRC settings from `curr_prcm_set`, switches SDRC to safe timing, calls SRAM PRCM programming, reinitializes SDRC DLL state, and restores the final source.

## State and Persistence Behavior
Static `dpll_core_ck` persists for rate queries. It consumes global `curr_prcm_set` and hardware DPLL/CM/SDRC state.

## Dependencies and Integration Points
Depends on OMAP clock framework, `opp2xxx` PRCM rate tables, CM helpers, SDRC helpers, and SRAM `omap2_set_prcm()`.

## Risks
DPLL and CORE are acknowledged as a composite clock that should be split, increasing coupling. Invalid rate rounding returns `-EINVAL`. Incorrect SDRC sequencing can corrupt memory during frequency changes.

## Test Signals
Exercise cpufreq/clock rate changes across low/high OMAP2xxx rates, verify `clk_get_rate()` for core, confirm SDRC DLL lock/unlock handling, and run memory stress during transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c

## Purpose
Implements the virtual OMAP2xxx `virt_prcm_set` clock used for legacy DVFS/cpufreq rate-set changes across MPU, DPLL, module dividers, and SDRC timing.

## Important APIs, Types, and Functions
Exports globals `curr_prcm_set` and `rate_table`, and defines `omap2xxx_clkt_vps_init()` for DT clock init. Clock ops include recalc, determine_rate, and set_rate helpers.

## Control Flow
Late init captures immutable `sys_ck` rate, checks bootloader-selected DPLL/core rate to choose `curr_prcm_set`, registers a synthetic `virt_prcm_set` clock parented by `mpu_ck`, and creates a `cpufreq_ck` clkdev alias. Rate determination scans `rate_table` for the highest allowed MPU rate no greater than requested, matching CPU mask and crystal. Set-rate picks the PRCM config, updates module dividers, switches SDRC to safe x2 timing, calls SRAM PRCM programming, reinitializes SDRC DLL state, and switches to final core source under IRQ disable.

## State and Persistence Behavior
Global state includes `cpu_mask`, `curr_prcm_set`, `rate_table`, and captured `sys_ck_rate`. Hardware state includes CM dividers, DPLL, SDRC refresh/DLL state, and IRQ-disabled transition window.

## Dependencies and Integration Points
Depends on clock framework, clkdev, cpufreq consumers, OMAP2xxx PRCM config tables, CM helpers, SDRC, SRAM PRCM programming, and CPU detection.

## Risks
If `sys_ck` lookup fails, rate matching can fail. `curr_prcm_set` and `rate_table` must be initialized by SoC clock data before use. Frequency changes are tightly coupled to memory timing and can hang if a table entry is wrong.

## Test Signals
Verify `cpufreq_ck` registration and rate changes on OMAP2420/2430 with different crystal rates. Test bootloader-rate detection, invalid requested rates, and memory/timer stability through transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.c

## Purpose
Provides OMAP2+ clock low-level operation registration and SoC-specific TI clock feature initialization, especially DPLL frequency limits, bypass modes, idlest semantics, and errata flags.

## Important APIs, Types, and Functions
Defines global `omap_clk_ll_ops`, `omap2_clk_setup_ll_ops()`, and `ti_clk_init_features()`.

## Control Flow
`omap2_clk_setup_ll_ops()` registers OMAP CM/clockdomain callbacks with the TI clock driver. `ti_clk_init_features()` builds a `ti_clk_features` struct based on CPU/SoC predicates, setting DPLL Fint ranges, allowed bypass values, jitter/freqsel support, GP-device flag, idlest ready value, DPLL4 reprogram denial for OMAP3430 ES1.0, and OMAP5/DRA7 errata I810 before passing it to `ti_clk_setup_features()`.

## State and Persistence Behavior
Global low-level ops persist in the TI clock subsystem. Feature flags configure clock driver behavior for the rest of boot.

## Dependencies and Integration Points
Depends on clockdomain and CM helper functions, OMAP revision/type predicates, TI clock framework, and CM register-bit constants.

## Risks
Feature selection is SoC-revision sensitive. Wrong Fint limits or bypass masks cause invalid DPLL programming; wrong idlest polarity can make modules appear stuck ready/not ready.

## Test Signals
Boot each OMAP2+ SoC family and verify `ti_clk` registration, DPLL rate changes, module enable readiness waits, and errata flags. Unit-style tests can stub CPU predicates to confirm feature structs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h

## Purpose
Defines OMAP2+ clock shared constants, rate-table flags, DPLL mode encodings, and declarations for low-level clock setup and feature initialization.

## Important APIs, Types, and Functions
Provides `RATE_IN_*` flags, `CORE_CLK_SRC_*` values, OMAP2/3/4 DPLL mode encodings, extern `omap_clk_ll_ops`, `omap2_clk_setup_ll_ops()`, and `ti_clk_init_features()`.

## Control Flow
No runtime flow in the header. Its constants guide clock data tables and feature setup in `clock.c` and OMAP2xxx clock files.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on Linux clk provider/devres and TI clock framework headers. Used by OMAP2+ clock, PRCM, and OPP data code.

## Risks
Mode encodings must match hardware CM register fields. Rate flags determine which table entries are valid for SoC revisions; mistakes can expose unsupported clock rates.

## Test Signals
Compile all OMAP2+ clock tables and run clock rate enumeration on each SoC revision. Static checks should compare DPLL mode constants with TRM values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h

## Purpose
Small OMAP2xxx clock header that exposes the CORE clock rate query for OMAP2xxx-specific clock and DVFS code.

## Important APIs, Types, and Functions
Declares `omap2xxx_clk_get_core_rate()` and includes shared `clock.h`.

## Control Flow
No runtime flow. Implemented in `clkt2xxx_dpllcore.c` and consumed by virtual PRCM set/rate code.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on the OMAP2+ clock headers and Linux clock provider definitions.

## Risks
The single exported helper relies on `omap2xxx_clkt_dpllcore_init()` having stored the DPLL/core clock pointer before use.

## Test Signals
Build OMAP2xxx clock code and verify callers can query a nonzero core rate after clock init.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clock2xxx.h -->
