# subset-b-005369 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-svs.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-svs.c

## Purpose
MediaTek Smart Voltage Scaling (SVS) platform driver. It calibrates per-domain operating voltages from efuse data, SVS hardware measurements, OPP tables, regulators, clocks, resets, thermal zones, and PM runtime dependencies. The driver supports MT8183, MT8186, MT8188, MT8192, and MT8195 through static `svs_platform_data` and `svs_bank` tables.

## Important APIs, Types, And Functions
Core types are `struct svs_platform`, `struct svs_platform_data`, `struct svs_bank_pdata`, `struct svs_bank`, `enum svsb_phase`, `enum svsb_sw_id`, `enum svsb_type`, and `enum svs_reg_index`. Register access is wrapped by `svs_readl_relaxed()`, `svs_writel_relaxed()`, and `svs_switch_bank()`. OPP voltage conversion uses `svs_bank_volt_to_opp_volt()` and `svs_opp_volt_to_bank_volt()`. Voltage calculation is split between v2 helpers (`svs_get_bank_volts_v2()`, `svs_set_bank_freq_pct_v2()`) and v3 two-line helpers (`svs_get_bank_volts_v3()`, `svs_set_bank_freq_pct_v3()`).

Main runtime entry points are `svs_probe()`, `svs_start()`, `svs_init01()`, `svs_init02()`, `svs_mon_mode()`, `svs_isr()`, `svs_suspend()`, and `svs_resume()`. Efuse handling flows through `svs_get_efuse_data()`, `svs_get_fuse_val()`, `svs_common_parse_efuse()`, and the MT8183-specific `svs_mt8183_efuse_parsing()`. Debugfs support, when enabled, exposes `dump`, per-bank `enable`, and per-bank `status` views.

## Control Flow
`svs_probe()` selects platform data from OF match data, runs the SoC-specific probe to resolve reset controls, thermal-sensor links, CPU/CCI/GPU OPP devices, reads SVS and thermal calibration nvmem cells, parses efuses, initializes bank resources and OPP tables, maps registers, requests the IRQ, then starts SVS.

Startup runs phases in order. `svs_init01()` pauses cpuidle, enables buck regulators, optionally powers domains through PM runtime, constrains OPPs around the vboot voltage, programs bank registers for INIT01, waits on an IRQ completion, then restores OPP availability, regulators, and PM runtime state. `svs_init02()` programs each eligible bank for INIT02, waits for completion, then synchronizes two-line high/low bank voltage tables from current OPP state. `svs_mon_mode()` enables monitor mode for eligible banks so later thermal-sensitive interrupts can update OPP voltages.

`svs_isr()` scans banks to identify the interrupting bank, selects the hardware bank under `svs_lock`, dispatches to INIT01, INIT02, MON, or error handlers, then calls `svs_adjust_pm_opp_volts()`. The voltage adjustment path locks the bank mutex, chooses the OPP range for one-line or two-line banks, applies thermal offsets when thermal zones are valid, clamps against bank `vmin` and default OPP voltage, and calls `dev_pm_opp_adjust_voltage()`.

Suspend disables all banks, restores default voltages, asserts reset, and disables the main clock. Resume enables the main clock, deasserts reset, repeats INIT02, and re-enters monitor mode.

## State And Persistence
Persistent state is hardware and firmware backed: efuse arrays from nvmem, thermal efuse values, register programming, OPP voltage tables, regulator state, reset/clock state, thermal-zone readings, and PM runtime power state. In-memory state lives in static SoC bank tables copied by reference into the platform object and mutable per-bank fields such as `phase`, `volt[]`, `freq_pct[]`, `opp_dfreq[]`, `opp_dvolt[]`, `dc_voffset_in`, `age_voffset_in`, `temp`, and saved `reg_data`. There is no filesystem persistence; debugfs only reports or disables active banks.

## Dependencies And Integration Points
The driver integrates with platform bus, OF match data, nvmem, OPP, regulator, thermal, reset, clock, PM runtime, CPU device lookup, device links for thermal/CCI/GPU dependencies, IRQ handling, cpuidle, and optional debugfs. It consumes SoC device-tree nodes and named nvmem cells `svs-calibration-data` and `t-calibration-data`.

## Risks
Incorrect efuse maps, OPP counts, thermal zone names, or bank tables can program invalid voltages. INIT01 temporarily disables OPPs and changes regulator state, so failure cleanup is critical. Two-line high/low bank handling depends on `turn_pt` calculations and can produce inconsistent voltages if OPP ordering changes. IRQ matching relies on bank `int_st` bits and shared hardware register selection under a global spinlock. Thermal errors intentionally move banks to `SVSB_PHASE_ERROR` and restore defaults, reducing optimization. Resource lifetime for `of_iomap()` is manually unwound on probe failure; successful probe does not register an explicit remove path, matching many always-on SoC drivers but making unload behavior dependent on devres/module lifecycle.

## Test Signals
Useful signals are successful probe logs, efuse parse logs, absence of `init01/init02 completion timeout`, OPP count matching platform tables, regulator and PM runtime cleanup on INIT01 failure, monitor interrupts changing OPP voltages, suspend/resume cycling INIT02 and monitor mode, and debugfs `svs/dump` plus per-bank `status` values matching expected OPP voltage bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-svs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/Kconfig

## Purpose
Defines build-time configuration for Microchip PolarFire SoC support drivers: GPIO IRQ muxing, the mailbox-backed system controller, and required syscon/MFD helpers.

## Important APIs, Types, And Functions
This is Kconfig only. It declares `POLARFIRE_SOC_IRQ_MUX`, `POLARFIRE_SOC_SYS_CTRL`, and `POLARFIRE_SOC_SYSCONS`.

## Control Flow
`POLARFIRE_SOC_IRQ_MUX` is a bool default-y option for `ARCH_MICROCHIP` that selects `REGMAP` and `REGMAP_MMIO`. `POLARFIRE_SOC_SYS_CTRL` is tristate and depends on `POLARFIRE_SOC_MAILBOX` and `MTD`. `POLARFIRE_SOC_SYSCONS` is a default-y bool for `ARCH_MICROCHIP` and selects `MFD_CORE`.

## State And Persistence
No runtime state. The selections determine which objects are compiled into the kernel or modules.

## Dependencies And Integration Points
Connects the Microchip SoC drivers to architecture selection, mailbox, MTD, regmap, MMIO regmap, and MFD infrastructure. It feeds the sibling Makefile object selection.

## Risks
Default-y syscon and IRQ mux options assume PolarFire SoC platforms need these early. Missing `POLARFIRE_SOC_MAILBOX` or `MTD` prevents the system controller driver from being built, which also blocks subdevice services that depend on it.

## Test Signals
Kconfig resolution should select `mpfs-irqmux.o`, `mpfs-control-scb.o`, `mpfs-mss-top-sysreg.o`, and optionally `mpfs-sys-controller.o` with the expected dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/Makefile

## Purpose
Maps Microchip PolarFire SoC Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
No C APIs. Object rules are `mpfs-irqmux.o`, `mpfs-sys-controller.o`, and syscon children `mpfs-control-scb.o mpfs-mss-top-sysreg.o`.

## Control Flow
Kernel build includes each object when its matching `CONFIG_POLARFIRE_SOC_*` symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the symbols declared in the local Kconfig and defines which source files participate in the Microchip SoC driver build.

## Risks
The syscon symbol builds both MFD/syscon wrapper drivers as a pair. Splitting either file without changing this Makefile would change runtime child-device availability.

## Test Signals
Expected objects appear in built-in or module link output according to enabled config symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-control-scb.c -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-control-scb.c

## Purpose
Small platform driver for the PolarFire SoC control SCB syscon. It instantiates an MFD child named `mpfs-tvs`.

## Important APIs, Types, And Functions
Uses `struct mfd_cell`, `devm_mfd_add_devices()`, OF match table, and `module_platform_driver()`. The only runtime function is `mpfs_control_scb_probe()`.

## Control Flow
When a device compatible with `microchip,mpfs-control-scb` probes, the driver adds the `mpfs-tvs` child device with `PLATFORM_DEVID_NONE`.

## State And Persistence
No private state is allocated. Child registration is devm-managed by the parent device.

## Dependencies And Integration Points
Integrates with platform bus, OF matching, syscon/MFD infrastructure, and the eventual `mpfs-tvs` child driver.

## Risks
Probe has no fallback or optional child handling; if `devm_mfd_add_devices()` fails, the syscon child is unavailable. The driver assumes its parent syscon/regmap setup is already represented by device tree and MFD/syscon infrastructure.

## Test Signals
Probe success should create an `mpfs-tvs` platform child under a `microchip,mpfs-control-scb` device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-control-scb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-irqmux.c -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-irqmux.c

## Purpose
Programs the PolarFire SoC GPIO interrupt mux register from device-tree `interrupt-map` data, selecting direct versus non-direct routing between GPIO controllers and the PLIC.

## Important APIs, Types, And Functions
Important functions are `mpfs_irqmux_is_direct_mode()` and `mpfs_irqmux_probe()`. It uses `of_imap_parser`, `of_imap_item`, bitmap duplicate detection, parent syscon regmap lookup with `device_node_to_regmap()`, and `regmap_read()/regmap_write()`.

## Control Flow
Probe validates `#interrupt-cells = <1>` and `#address-cells = <0>`, initializes an interrupt-map parser, and iterates every map item. It validates parent interrupt ranges, child controller indexes, duplicate child lines, and duplicate direct parent lines. It builds a 32-bit mux value: direct-mode entries leave bits cleared, non-direct GPIO0 entries set bits 0-13, and non-direct GPIO1 entries set bits 14-31. GPIO2 entries are skipped because their counterpart entries determine the shared bit. Finally it writes `MPFS_IRQMUX_CR` and logs if firmware state was overwritten.

## State And Persistence
Runtime state is transient except the hardware mux register at offset `0x54`. Bitmaps track duplicate validation only during probe.

## Dependencies And Integration Points
Depends on parent syscon regmap, OF interrupt-map bindings, platform bus, and the PolarFire GPIO/PLIC interrupt topology. Kconfig selects regmap support.

## Risks
Strict binding validation returns `-EINVAL` on malformed maps, so DT errors disable mux setup. Firmware mux settings are overwritten when DT differs. The logic encodes PolarFire-specific assumptions about 70 GPIO interrupts, 41 PLIC lines, 38 direct lines, and the special GPIO1 lines 18-23.

## Test Signals
Boot logs should show no duplicate or invalid interrupt-map errors. A one-time info message indicates the driver corrected a firmware mux value. GPIO interrupts from all three controllers should route according to the DT map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-irqmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-mss-top-sysreg.c -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-mss-top-sysreg.c

## Purpose
Platform/MFD wrapper for the PolarFire SoC MSS top sysreg block. It creates an `mpfs-reset` child and populates OF children.

## Important APIs, Types, And Functions
Uses `mpfs_mss_top_sysreg_probe()`, `devm_mfd_add_devices()`, `devm_of_platform_populate()`, and an OF match for `microchip,mpfs-mss-top-sysreg`.

## Control Flow
On probe, the driver registers one MFD cell named `mpfs-reset`. If that succeeds, it populates child platform devices described below the sysreg node in device tree.

## State And Persistence
No private state. Child devices are devm-managed or OF-populated under the parent.

## Dependencies And Integration Points
Integrates with platform bus, MFD core, OF platform population, and Microchip reset/sysreg child drivers.

## Risks
Failure to create the reset child aborts OF child population. The file assumes sysreg register access is provided by the broader syscon infrastructure rather than handled here.

## Test Signals
Probe should register `mpfs-reset` and any DT child devices under `microchip,mpfs-mss-top-sysreg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-mss-top-sysreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-sys-controller.c -->
# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-sys-controller.c

## Purpose
Mailbox-backed PolarFire SoC system controller core. It provides blocking service transactions, optional bitstream flash access, consumer lifetime management, and registers platform subdevices for RNG, generic service, and auto-update features depending on compatible data.

## Important APIs, Types, And Functions
Exports `mpfs_blocking_transaction()`, `mpfs_sys_controller_get_flash()`, and `mpfs_sys_controller_get()`. Main private type is `struct mpfs_sys_controller` with mailbox client/channel, completion, optional `mtd_info`, and `kref` consumers. `struct mpfs_syscon_config` chooses subdevices for `microchip,mpfs-sys-controller` and `microchip,pic64gx-sys-controller`.

## Control Flow
Probe allocates the controller, optionally resolves `microchip,bitstream-flash` to an MTD device, configures a blocking mailbox client with a 30-second timeout, requests mailbox channel 0, initializes completion and kref, stores driver data, then registers configured subdevices with the controller as parent. The RX callback only completes the pending transaction.

`mpfs_blocking_transaction()` serializes all transactions with `transaction_lock`, reinitializes the completion, sends the mailbox message, and waits for a completion. Because hardware only interrupts on service success, send completion without RX completion is treated as `-EBADMSG` and callers inspect the message response status. Remove drops the controller reference, and final kref release frees the mailbox channel and memory.

`mpfs_sys_controller_get()` is used by subdevices. It validates the parent compatible, fetches parent drvdata, increments the kref unless zero, and attaches a devm cleanup action to put the reference.

## State And Persistence
Persistent external state includes system-controller firmware services, mailbox state, and optional MTD flash. Driver state is heap-allocated, reference-counted, and shared by subdevices. The global `transaction_lock` enforces one in-flight transaction across all instances.

## Dependencies And Integration Points
Depends on mailbox framework, `soc/microchip/mpfs.h` message ABI, MTD for bitstream flash, OF phandles, platform device registration, completions, and krefs. Subdevice names are consumed by Microchip RNG, generic service, and auto-update drivers.

## Risks
The global transaction mutex serializes all controller transactions and can become a bottleneck. Timeout behavior depends on mailbox send semantics and firmware status being written into `msg->response`. Probe error paths after successful mailbox channel acquisition and before devm ownership are limited; subdevice registration warns but does not fail the parent. `mpfs_sys_controller_get()` calls `of_node_put(dev->parent->of_node)` after `of_match_node()`, which is sensitive because it does not acquire that node locally.

## Test Signals
Expected signals are successful mailbox channel request, `Registered MPFS system controller`, working subdevice probes, correct `-EBADMSG` on failed services without RX completion, and stable kref behavior when subdrivers probe and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-sys-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Kconfig

## Purpose
Defines the Nuvoton WPCM450 SoC information driver build option.

## Important APIs, Types, And Functions
Kconfig `menuconfig WPCM450_SOC` is tristate, defaults to y on `ARCH_WPCM450`, and selects `SOC_BUS`.

## Control Flow
When enabled, the Makefile builds the WPCM450 SoC identification driver, which registers SoC model and revision data.

## State And Persistence
No runtime state in this file.

## Dependencies And Integration Points
Connects architecture selection to the Linux SoC bus framework.

## Risks
If disabled, user space loses standardized SoC identification for WPCM450 even though the platform may otherwise boot.

## Test Signals
With `ARCH_WPCM450`, config should default to enabled and select `SOC_BUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Makefile

## Purpose
Build glue for the Nuvoton WPCM450 SoC driver.

## Important APIs, Types, And Functions
No C APIs. `obj-$(CONFIG_WPCM450_SOC) += wpcm450-soc.o`.

## Control Flow
The object is compiled into the kernel/module when `WPCM450_SOC` is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the local Kconfig symbol and links the WPCM450 SoC identification source.

## Risks
None beyond normal config/object mismatches.

## Test Signals
`wpcm450-soc.o` appears in build output when the config is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/wpcm450-soc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/wpcm450-soc.c

## Purpose
Registers Nuvoton WPCM450 SoC identity and revision through the Linux SoC bus.

## Important APIs, Types, And Functions
Key pieces are `struct revision`, `get_revision()`, `wpcm450_soc_init()`, `wpcm450_soc_exit()`, `soc_device_register()`, `soc_device_unregister()`, and `syscon_regmap_lookup_by_compatible()`.

## Control Flow
At module init, the driver exits quietly unless the machine is compatible with `nuvoton,wpcm450`. It looks up the GCR syscon, reads `GCR_PDID`, verifies the chip ID equals `CHIP_WPCM450`, maps the revision byte to a known name, allocates `soc_device_attribute`, and registers the SoC device. Exit unregisters the SoC device and frees the attribute if registration happened.

## State And Persistence
Global pointers `wpcm450_attr` and `wpcm450_soc` hold registered SoC bus state until module exit. Hardware state is read-only from the GCR product ID register.

## Dependencies And Integration Points
Depends on OF machine compatibility, syscon/regmap for `nuvoton,wpcm450-gcr`, and the SoC bus framework. User space can observe the resulting family, SoC ID, and revision through sysfs.

## Risks
Unknown chip or revision returns `-ENODEV` and prevents SoC registration. A missing GCR syscon defers or fails init. The revision table is finite and must be updated for new silicon IDs.

## Test Signals
On WPCM450, `/sys/devices/soc0` should report family `Nuvoton NPCM`, soc_id `WPCM450`, and one of revisions `Z1`, `Z2`, `Z21`, `A1`, `A2`, or `A3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/nuvoton/wpcm450-soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/pxa/Kconfig

## Purpose
Defines legacy PXA platform support symbols for multi-function pins and SSP helpers.

## Important APIs, Types, And Functions
Declares `PLAT_PXA` as a bool and `PXA_SSP` as a tristate helper for PXA2xx SSP ports.

## Control Flow
Other architecture configs select these symbols; the local Makefile builds `mfp.o` and `ssp.o` based on them and on PXA/MMP arch symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Provides config symbols consumed by PXA/MMP platform and peripheral drivers.

## Risks
`PXA_SSP` has no prompt here, so it is intended as an internal selectable symbol. Missing selection breaks client drivers using the exported SSP request/free API.

## Test Signals
Expected symbols resolve when PXA or MMP platforms are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/pxa/Makefile

## Purpose
Build glue for PXA/MMP SoC support helpers.

## Important APIs, Types, And Functions
No C APIs. Builds `mfp.o` for `CONFIG_PXA3xx` or `CONFIG_ARCH_MMP`, and `ssp.o` for `CONFIG_PXA_SSP`.

## Control Flow
Kernel build includes objects according to architecture and helper selections.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects architecture configs to shared PXA pinmux and SSP support code.

## Risks
Both `CONFIG_PXA3xx` and `CONFIG_ARCH_MMP` can request `mfp.o`; build system coalesces the object, but source changes need to remain compatible with both users.

## Test Signals
Configured PXA/MMP builds include the expected object files without duplicate symbol issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/mfp.c -->
# sources/distributed-fs/ceph-client/drivers/soc/pxa/mfp.c

## Purpose
Implements legacy PXA/MMP Multi-Function Pin register programming for run mode and low-power mode.

## Important APIs, Types, And Functions
Exports in-file functions used by platform code: `mfp_config()`, `mfp_read()`, `mfp_write()`, `mfp_init_base()`, `mfp_init_addr()`, `mfp_config_lpm()`, and `mfp_config_run()`. Main state is `struct mfp_pin` and the global `mfp_table[MFP_PIN_MAX]`. Register encodings are derived from `linux/soc/pxa/mfp.h` macros.

## Control Flow
Early platform setup calls `mfp_init_base()` to store the MFPR MMIO base and mark all pins unconfigured, then `mfp_init_addr()` to fill per-pin register offsets from address maps. `mfp_config()` decodes each packed pin config into alternate function, drive strength, low-power state, edge wake settings, and pull mode. It computes separate run and low-power register values when explicit pull mode conflicts with low-power bits, writes run-mode values immediately, and does a readback sync. `mfp_config_lpm()` and `mfp_config_run()` iterate configured pins and write saved low-power or run values.

## State And Persistence
State is global and hardware-facing: `mfpr_mmio_base`, `mfpr_off_readback`, and per-pin cached config/run/lpm values. Hardware MFPR registers retain the active mode until changed or reset.

## Dependencies And Integration Points
Depends on PXA MFP packed config definitions, raw MMIO access, init-time platform address maps, and suspend/resume or PM code that calls low-power/run reconfiguration.

## Risks
The code uses `BUG_ON()` for invalid pins, which turns bad platform data into a fatal failure. Raw accessors and global state assume single initialized MMIO base. `mfp_config_lpm()` and `mfp_config_run()` iterate without taking `mfp_spin_lock`, relying on external serialization during power transitions. Wake edge clearing order in `__mfp_config_lpm()` is important to avoid stale edge status.

## Test Signals
Platform boot should show correct pin functions and drive states. Suspend/resume testing should verify low-power pin levels, wake edges, and run-mode restoration. Invalid address maps or pin IDs should be caught during board bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/mfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/ssp.c -->
# sources/distributed-fs/ceph-client/drivers/soc/pxa/ssp.c

## Purpose
Registers PXA/Marvell SSP controller instances and provides a simple global request/free API for client drivers needing exclusive SSP port access.

## Important APIs, Types, And Functions
Exports `pxa_ssp_request()`, `pxa_ssp_request_of()`, and `pxa_ssp_free()`. Platform-driver functions are `pxa_ssp_probe()`, `pxa_ssp_remove()`, `pxa_ssp_init()`, and `pxa_ssp_exit()`. Global state is `ssp_list` protected by `ssp_lock`.

## Control Flow
Probe allocates `struct ssp_device`, obtains the clock, claims and maps MMIO, reads IRQ, determines controller type from OF match data or platform device ID, sets port ID for non-DT PXA devices, adds the device to the global list, and stores drvdata. Clients request a port by numeric port or OF node; if a matching entry has `use_count == 0`, it is marked in use and labeled. Free decrements use count and clears the label. Remove deletes the controller from the global list.

## State And Persistence
Global list entries persist while platform devices are bound. Each `ssp_device` stores MMIO base, physical base, IRQ, clock, type, OF node, label, and use count. No filesystem persistence.

## Dependencies And Integration Points
Depends on platform bus, clocks, IO resources, IRQ resources, OF match table, legacy platform IDs, and external clients using `linux/pxa2xx_ssp.h`.

## Risks
`pxa_ssp_request()` and `pxa_ssp_request_of()` initialize `ssp` to NULL and then test `&ssp->node == &ssp_list` after the loop; if the list is empty this pattern depends on list iteration semantics and can be unsafe. There is no module reference taken for clients holding an SSP. Remove does not reject active users. OF compatible strings include historical `mvrl` typos that may be ABI-preserving but surprising.

## Test Signals
SSP clients should successfully acquire one controller, fail concurrent acquisition, release cleanly, and operate with expected MMIO/IRQ/clock resources. Empty-list and active-remove behavior deserve targeted tests or review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/pxa/ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/Kconfig

## Purpose
Defines build options for Qualcomm SoC support drivers, including command DB, APR/GPR, interconnect bandwidth monitor, inline crypto engine, and Kryo L2 accessors covered by this subset.

## Important APIs, Types, And Functions
Kconfig symbols relevant here are `QCOM_COMMAND_DB`, `QCOM_KRYO_L2_ACCESSORS`, `QCOM_APR`, `QCOM_ICC_BWMON`, and `QCOM_INLINE_CRYPTO_ENGINE`. The file also declares many adjacent Qualcomm subsystem options.

## Control Flow
Each symbol gates the corresponding Makefile object. Dependencies encode required frameworks: command DB needs OF reserved memory; APR needs RPMSG and NET and selects PDR helpers; BWMON selects PM OPP and REGMAP_MMIO; ICE selects QCOM SCM; Kryo accessors require ARM64.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
This file binds Qualcomm architecture or compile-test builds to mailbox/RPMSG, PM OPP, reserved memory, SCM, MTD-like platform services, and remoteproc-related helpers.

## Risks
Several entries are helper symbols without prompts or are selected by other drivers, so dependency mistakes can surface as link errors in unrelated Qualcomm subsystems. `QCOM_RPMH` explicitly allows command DB built-in/module combinations through `(QCOM_COMMAND_DB || !QCOM_COMMAND_DB)`.

## Test Signals
Kconfig tests should verify enabled symbols produce the matching objects and required selected dependencies without circular or unmet dependency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/Makefile

## Purpose
Maps Qualcomm SoC Kconfig symbols to object files and composite modules.

## Important APIs, Types, And Functions
Relevant rules build `cmd-db.o`, `apr.o`, `icc-bwmon.o`, `kryo-l2-accessors.o`, and composite `qcom_ice-objs += ice.o` linked under `CONFIG_QCOM_INLINE_CRYPTO_ENGINE`. It also sets local include CFLAGS for several objects.

## Control Flow
The kernel build includes each object according to the selected `CONFIG_QCOM_*` symbol. Composite modules such as `qmi_helpers-y` and `qcom_rpmh-y` aggregate multiple objects.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the local Kconfig symbols and participates in module naming, e.g. the ICE source becomes the `qcom_ice` module rather than `ice`.

## Risks
Object naming matters for module aliases and exported symbols. Moving `ice.o` out of `qcom_ice-objs` would change module identity.

## Test Signals
Build output should contain expected Qualcomm objects/modules for each config permutation, especially module builds of APR, BWMON, command DB, and ICE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/apr.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/apr.c

## Purpose
Implements the Qualcomm APR/GPR packet-router bus over RPMSG for QDSP6 services. It creates APR/GPR child devices from device tree, routes inbound packets to registered service drivers or dynamic GPR ports, and integrates with PDR service availability notifications.

## Important APIs, Types, And Functions
Exports `apr_send_pkt()`, `gpr_alloc_port()`, `gpr_free_port()`, `gpr_send_pkt()`, `gpr_send_port_pkt()`, `aprbus`, `__apr_driver_register()`, and `apr_driver_unregister()`. Main private state is `struct packet_router` with RPMSG endpoint, service IDR, PDR handle, RX workqueue, and RX list. RX buffers use flexible `struct apr_rx_buf`. Service state is represented by `struct pkt_router_svc` embedded in APR devices and GPR ports.

## Control Flow
`apr_init()` registers `aprbus` then the RPMSG driver. `apr_probe()` reads `qcom,domain` or legacy `qcom,apr-domain`, determines APR versus GPR from compatible, initializes locks/IDR/workqueue/PDR, adds PDR lookups from child nodes, and immediately registers child devices without protection-domain dependencies.

Inbound RPMSG messages enter `apr_callback()`, which validates minimum length, copies the packet into an allocated RX buffer, appends it under `rx_lock`, and queues `apr_rxwq()`. The worker dispatches to `apr_do_rx_callback()` or `gpr_do_rx_callback()`. APR validates header fields, finds the destination service ID in the IDR, builds `apr_resp_pkt`, and calls the bound APR driver callback. GPR validates its header, finds destination port, and invokes the registered port callback.

Child registration is controlled by `of_register_apr_devices()`. It creates APR/GPR devices for children with matching protection-domain state, and `apr_pd_status()` adds or unregisters devices as remote services go up or down. Device removal unregisters child devices and drops IDR entries.

## State And Persistence
Runtime state is in the `packet_router` per RPMSG endpoint: service IDR, RX workqueue/list, PDR handle, and child devices on `aprbus`. Dynamic GPR ports allocate IDs in `0x10000000..0x20000000`. There is no persistent storage.

## Dependencies And Integration Points
Depends on RPMSG, OF child nodes, Qualcomm APR/GPR packet ABI headers, PDR helpers, IDR, workqueues, and Linux driver core bus registration. Audio and DSP service drivers bind to `aprbus`.

## Risks
RX processing copies packets in atomic context and can drop packets on allocation failure. Header validation rejects malformed remote data, but optional header size handling must remain correct. The worker iterates `rx_list` while briefly locking only for deletion, so list mutation ordering relies on single worker plus producer append discipline. Service removal while packets are queued can lead to callback lookup failures. `apr_add_device()` error paths after successful IDR allocation do not visibly remove the IDR entry before returning.

## Test Signals
Probe should create APR/GPR child devices for DT services, PDR up/down should register/unregister protection-domain services, inbound packets should reach the correct callbacks, malformed packets should log and be rejected, and dynamic GPR port allocation should avoid static service ID collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/apr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/cmd-db.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/cmd-db.c

## Purpose
Maps Qualcomm Command DB reserved memory and exports lookup helpers so other drivers can translate resource key strings into RPMh/shared-resource addresses, slave IDs, and auxiliary data.

## Important APIs, Types, And Functions
Exports `cmd_db_ready()`, `cmd_db_read_addr()`, `cmd_db_read_aux_data()`, `cmd_db_match_resource_addr()`, and `cmd_db_read_slave_id()`. Database layout types are `struct cmd_db_header`, `struct rsc_hdr`, and `struct entry_header`. Internal helpers include `cmd_db_magic_matches()`, `rsc_to_entry_header()`, `rsc_offset()`, and `cmd_db_get_header()`.

## Control Flow
The core initcall registers a platform driver for `qcom,cmd-db`. Probe looks up the reserved memory attached to the DT node, maps it write-combining with `devm_memremap()`, validates the magic bytes, creates a debugfs dump file, and marks PM as not required. Query APIs first call `cmd_db_ready()`, pad the requested ID to the fixed 8-byte entry ID field, scan each populated resource header and its entry array, then return the requested address, aux data pointer/length, or decoded slave ID.

## State And Persistence
Global `cmd_db_header` points at reserved memory owned by firmware/bootloader. The data is read-only from this driver’s perspective after mapping. Debugfs exposes a live dump; no data is persisted by Linux.

## Dependencies And Integration Points
Depends on OF reserved memory, platform bus, debugfs, little-endian layout conversion, and `soc/qcom/cmd-db.h`. RPMh, interconnect, regulator, clock, and other Qualcomm resource drivers consume the exported lookup helpers.

## Risks
There is a single global database pointer, so multiple instances are not modeled. The scanner trusts offsets and counts after magic validation; malformed firmware data could point entries outside the reserved memory. Query IDs are fixed-width and padded, so longer logical names would not match. Debugfs file operations are partially conditional on `CONFIG_DEBUG_FS`, but the file operations object exists either way.

## Test Signals
`cmd_db_ready()` should return `-EPROBE_DEFER` before probe, zero after valid probe, and `-EINVAL` on bad magic. Known resource IDs should produce expected addresses and aux blobs. Debugfs `cmd-db` should list ARC/VRM/BCM entries when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/cmd-db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/icc-bwmon.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/icc-bwmon.c

## Purpose
Qualcomm interconnect bandwidth monitor driver. It programs BWMON hardware thresholds, handles bandwidth zone interrupts, and adjusts PM OPP bandwidth votes to match measured interconnect demand.

## Important APIs, Types, And Functions
Private types are `struct icc_bwmon_data` and `struct icc_bwmon`. Register abstractions are `enum bwmon_fields`, SoC-specific `reg_field` arrays, and regmap configs for BWMON v4/v5/global register layouts. Runtime functions include `bwmon_clear_counters()`, `bwmon_clear_irq()`, `bwmon_disable()`, `bwmon_enable()`, `bwmon_set_threshold()`, `bwmon_start()`, `bwmon_intr()`, `bwmon_intr_thread()`, `bwmon_init_regmap()`, `bwmon_probe()`, and `bwmon_remove()`.

## Control Flow
Probe allocates state, maps monitor registers and optional global registers, bulk-allocates regmap fields, gets the IRQ, loads the OPP table, discovers min/max peak bandwidth OPPs, disables the monitor, requests a shared threaded IRQ, stores drvdata, and starts monitoring.

`bwmon_start()` clears counters, writes the sample window, initializes high/medium thresholds to the minimum bandwidth OPP, programs threshold counts and zone actions, clears interrupts, and enables zone 1 and zone 3 interrupts. The hard IRQ reads status, ignores unrelated interrupts, disables the monitor, reads the relevant zone max counter, converts it to `target_kbps`, and wakes the threaded handler. The thread finds the nearest OPP, computes up/down thresholds around it, clears counters/IRQs, reenables appropriate interrupts, traces the update, and calls `dev_pm_opp_set_opp()` when target bandwidth changes.

Remove disables the monitor and frees the IRQ.

## State And Persistence
Per-device state stores current/target/min/max bandwidth, IRQ, register fields, and SoC data. Hardware state consists of BWMON counters, thresholds, zone actions, IRQ masks, and enable state. No persistent storage.

## Dependencies And Integration Points
Depends on platform bus, MMIO regmap, regmap fields, PM OPP bandwidth APIs, IRQ threading, tracepoint `trace_icc-bwmon.h`, and device-tree compatibles such as `qcom,msm8998-bwmon`, `qcom,sdm845-bwmon`, `qcom,sdm845-llcc-bwmon`, and `qcom,sc7280-llcc-bwmon`.

## Risks
Register ordering is delicate; comments call out required clear ordering across regions. Some SoCs need force-clearing of clear registers. Spurious zone 2 interrupts are ignored, which can miss useful max values. Regmap locking is disabled because the driver expects no concurrent access beyond its IRQ flow. OPP tables must contain bandwidth entries; otherwise probe fails.

## Test Signals
Probe should find min/max bandwidth OPPs and request the IRQ. Trace events should show measured/up/down bandwidth transitions. OPP votes should change under memory traffic and settle to min/max bounds. Shared IRQ testing should verify unrelated status returns `IRQ_NONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/icc-bwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ice.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/ice.c

## Purpose
Qualcomm Inline Crypto Engine support for storage inline encryption. It discovers ICE hardware, chooses raw-key versus hardware-wrapped-key mode, initializes low-power/optimization/HWKM registers, and exports key programming and wrapped-key lifecycle helpers to storage drivers.

## Important APIs, Types, And Functions
Exports `qcom_ice_enable()`, `qcom_ice_resume()`, `qcom_ice_suspend()`, `qcom_ice_program_key()`, `qcom_ice_evict_key()`, `qcom_ice_get_supported_key_type()`, `qcom_ice_derive_sw_secret()`, `qcom_ice_generate_key()`, `qcom_ice_prepare_key()`, `qcom_ice_import_key()`, and `devm_of_qcom_ice_get()`. Main private type is `struct qcom_ice` with device, base, core clock, HWKM flags, and HWKM version. Important internals are `qcom_ice_check_supported()`, `qcom_ice_hwkm_init()`, `qcom_ice_wait_bist_status()`, `qcom_ice_program_wrapped_key()`, `qcom_ice_create()`, and `of_qcom_ice_get()`.

## Control Flow
`qcom_ice_create()` waits for SCM availability, checks SCM ICE support, obtains one of the legacy or node-local clocks, reads hardware version and fuse state, determines HWKM version, and chooses HWKM only if the module parameter `qcom_ice.use_wrapped_keys=1` and SCM wrapped-key support are present.

Consumers call `devm_of_qcom_ice_get()`. For legacy bindings, it maps an `ice` resource from the consumer device and creates an instance. For modern bindings, it follows the `qcom,ice` phandle, gets the provider platform device, reads its drvdata, and creates a device link. Provider probe maps resource 0 and stores a created ICE instance.

`qcom_ice_enable()` enables low-power and optimization sequences, initializes HWKM if selected, then waits for BIST completion. Resume reenables the clock and repeats HWKM/BIST setup; suspend disables the clock and marks HWKM init incomplete. Key programming accepts only AES-256-XTS. Wrapped keys are programmed through SCM into translated HWKM slots and then enable `CRYPTOCFG`; raw keys are endian-converted and sent through `qcom_scm_ice_set_key()`, then zeroed.

## State And Persistence
State includes the mapped ICE registers, enabled clock, module parameter policy, HWKM mode/version, and `hwkm_init_complete`. Key material is passed to SCM and keyslots; raw key stack copies are wiped with `memzero_explicit()`. No filesystem persistence.

## Dependencies And Integration Points
Depends on Qualcomm SCM firmware APIs, blk-crypto key types and sizes, platform/OF resource lookup, clocks, device links, MMIO, and storage consumers such as UFS/eMMC drivers. The Makefile builds it as `qcom_ice`.

## Risks
Mode selection is global/module-parameter driven and must happen before storage drivers advertise crypto capabilities. HWKM and legacy raw-key mode are mutually exclusive. If HWKM self-test fails after capabilities were exposed, the driver can only log the error. TrustZone/SCM errors directly affect key programming. Slot translation differs between HWKM v1 and v2. Legacy consumer-created instances and provider-node instances have different put semantics.

## Test Signals
Expected logs identify ICE version and HWKM version/mode. Probe should defer until SCM is available. Storage drivers should advertise raw or wrapped key support consistently with `qcom_ice_get_supported_key_type()`. Key generation/prepare/import/program/evict paths should succeed with valid SCM firmware and reject wrong modes, wrong sizes, and invalid wrapped keys with appropriate errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/ice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/kryo-l2-accessors.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/kryo-l2-accessors.c

## Purpose
Provides serialized indirect read/write helpers for Qualcomm Kryo L2 system registers on ARM64.

## Important APIs, Types, And Functions
Exports `kryo_l2_set_indirect_reg()` and `kryo_l2_get_indirect_reg()`. Uses raw spinlock `l2_access_lock` and system register definitions `L2CPUSRSELR_EL1` and `L2CPUSRDR_EL1`.

## Control Flow
Both helpers take the raw spinlock with IRQ save, write the target indirect register selector, execute `isb()`, then write or read the data register. Writes execute a second `isb()` before unlocking.

## State And Persistence
No heap state. Hardware state is the selected L2 indirect register and its value. The lock serializes selector/data register pairs across CPUs.

## Dependencies And Integration Points
Depends on ARM64 system-register accessors and is gated by `QCOM_KRYO_L2_ACCESSORS`. Other Qualcomm CPU/cache drivers use these exported symbols to configure Kryo-specific L2 registers.

## Risks
Incorrect register selectors or values can affect CPU/cache behavior. Serialization is mandatory because selector and data registers form a shared indirect access pair. Callers must know whether they are allowed to access these implementation-defined registers on the running CPU.

## Test Signals
Unit-level validation is limited; practical signals are successful callers on supported Kryo systems, no concurrent indirect access corruption under multi-CPU stress, and no undefined-instruction faults on configured platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/kryo-l2-accessors.c -->
