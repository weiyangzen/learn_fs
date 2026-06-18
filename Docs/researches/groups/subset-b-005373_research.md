# subset-b-005373 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5420-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5420-pmu.c

## Purpose

`exynos5420-pmu.c` supplies the Exynos5420/5422 PMU policy table and initialization hooks used by the common Samsung Exynos PMU driver. It describes how major CPU, clock, memory, pad-retention, and IP power domains should be programmed for AFTR, LPA, and SLEEP modes, then performs chip-specific one-time PMU setup.

## Important APIs, Types, and Functions

The main data object is `exynos5420_pmu_config[]`, an array of `struct exynos_pmu_conf` entries ending with `PMU_TABLE_END`. Each entry maps a PMU register offset from `exynos-regs-pmu.h` to three mode values. `exynos5420_list_disable_pmu_reg[]` lists local CMU clock-stop, sysclk, and reset PMU registers that must be cleared initially. `exynos5420_powerdown_conf()` writes the current CPU cluster id to `EXYNOS_IROM_DATA2`. `exynos5420_pmu_init()` applies low-level workaround/configuration writes. `exynos5420_pmu_data` exports the table and callbacks to the common PMU layer.

## Control Flow

During PMU driver setup, the common Exynos PMU code consumes `exynos5420_pmu_data`, iterates `pmu_config` when entering system power states, and calls `pmu_init`. Initialization clears selected local-power CMU entries, enables standby-WFI for all cores, disables L2 retention bits for both clusters, masks LPI paths for ISP/KFC ATB bridges, sets ACE/ACP deactivation skip bits for ARM and KFC common blocks, programs reset-duration and interrupt-spread registers, and enables the upstream scheduler. Before powerdown, `powerdown_conf` records the current cluster from MPIDR affinity level 1 so resume returns through the expected cluster.

## State and Persistence Behavior

The file has no heap state or file-backed persistence. Its static tables are immutable kernel data. Persistent effects are MMIO writes into PMU registers that survive across suspend/resume according to SoC reset and retention rules. `EXYNOS_IROM_DATA2` is used as firmware-visible scratch state for wakeup routing.

## Dependencies and Integration Points

It depends on the Exynos PMU core, raw PMU accessors (`pmu_raw_readl`, `pmu_raw_writel`), ARM MPIDR helpers, and SoC register definitions. It integrates with Samsung suspend/resume code through `struct exynos_pmu_data`.

## Risks and Edge Cases

The configuration is register-table driven; wrong offsets or mode columns can silently break suspend, clocks, or retention. `exynos5420_powerdown_conf()` assumes affinity level 1 maps directly to the cluster id expected by IROM. The L2 retention and LPI mask workarounds are hardware-specific and risky to generalize. The initial clearing loop has no readback or error path, so validation depends on hardware behavior.

## Test Signals

Useful signals are boot logs showing PMU initialization, suspend/resume across AFTR/LPA/SLEEP, wakeup from both ARM and KFC clusters, no LPI hang when ISP-related clocks are gated, and no regression in CPU hotplug or cluster powerdown. Build coverage should include `CONFIG_SOC_EXYNOS5420` paths and register-definition drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5420-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.c

## Purpose

`exynos5422-asv.c` implements Adaptive Supply Voltage setup for Exynos5422 CPU clusters. It chooses ASV voltage tables from chip-id fuse fields, derives an ASV group from IDS/HPM or special-speed-grade bits, applies per-cluster voltage offsets, and exposes an OPP voltage callback to the shared Exynos ASV core.

## Important APIs, Types, and Functions

The large `asv_arm_table` and `asv_kfc_table` arrays encode frequency-to-voltage rows for the Cortex-A15 ARM cluster and Cortex-A7 KFC cluster. Constants such as `ASV_GROUPS_NUM`, `ASV_ARM_DVFS_NUM`, and bin2 row counts bound table dimensions. `__asv_limits[]` maps IDS/HPM thresholds to ASV groups. `exynos5422_asv_get_group()` reads `EXYNOS_CHIPID_REG_PKG_ID` and `EXYNOS_CHIPID_REG_AUX_INFO`. `exynos5422_asv_offset_voltage_setup()` configures high/low offsets. `exynos5422_asv_opp_get_voltage()` is the exported per-OPP adjustment callback. `exynos5422_asv_init()` is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

Initialization reads package id, decides whether bin2 mode is forced by DT (`of_bin == 2`) or parsed from package fuses, parses whether special speed-grade math is used, computes `asv->group`, table selector, and offsets, then binds subsystem metadata. ARM gets `cpu_dt_compat = "arm,cortex-a15"` and KFC gets `"arm,cortex-a7"`. Bin2 selects shorter bin2 tables and table index 3; otherwise package table values 2 or 3 select alternate tables, and all other values use table 0. Later, the ASV core calls `opp_get_voltage`, which bounds the OPP level, fetches the voltage column for the selected group, and applies high or low offset based on the OPP's original voltage relative to a 1,000,000 uV base.

## State and Persistence Behavior

All runtime state is stored in the caller-provided `struct exynos_asv`: selected group/table, `use_sg`, per-subsystem base and offsets, table pointers, row/column counts, and callback pointer. The driver does not persist data; it interprets SoC fuse state and updates OPP voltages during boot.

## Dependencies and Integration Points

It depends on the Samsung chip-id regmap, `exynos-asv.h` shared structures, Exynos5422 fuse bit definitions from `exynos5422-asv.h`, and the OPP/ASV framework that applies updated CPU OPP voltages. It integrates with DT CPU compatible strings rather than directly touching cpufreq.

## Risks and Edge Cases

The first KFC table uses frequency values in Hz-like units while later tables use MHz-style values; this is presumably intentional but easy to misread. Table dimensions are hard-coded, so any row-count mismatch can corrupt OPP lookup. If fuse reads fail, the current code does not check regmap return values. ASV group calculation stops when either IDS or HPM crosses a threshold; boundary behavior must match vendor calibration. Offset application uses the original OPP voltage compared with a fixed base, so unexpected DT voltages can select the wrong offset side.

## Test Signals

Boot should log and apply valid OPP voltages for both A15 and A7 clusters across normal, bin2, and special-speed-grade parts. Tests should compare generated OPP voltages against vendor tables for representative `pkg_id`/`aux_info` values, verify `of_bin = 2` overrides fuse parsing, and run cpufreq stress plus thermal throttling on Exynos5422 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.h -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.h

## Purpose

`exynos5422-asv.h` is the small private header for Exynos5422 ASV support. It defines ASV subsystem ids and provides the build-time declaration or stub for `exynos5422_asv_init()`.

## Important APIs, Types, and Functions

The anonymous enum assigns `EXYNOS_ASV_SUBSYS_ID_ARM`, `EXYNOS_ASV_SUBSYS_ID_KFC`, and `EXYNOS_ASV_SUBSYS_ID_MAX`. The header forward-declares `struct exynos_asv`. With `CONFIG_EXYNOS_ASV_ARM`, it declares `int exynos5422_asv_init(struct exynos_asv *asv)`. Without that config, it supplies an inline stub returning `-ENOTSUPP`.

## Control Flow

Callers can invoke `exynos5422_asv_init()` unconditionally and receive either the real SoC implementation or a clear unsupported error depending on kernel configuration. The subsystem ids index the `asv->subsys[]` array populated by the C file.

## State and Persistence Behavior

This header owns no runtime state. Its enum values are ABI-like within the Exynos ASV implementation because they determine array indexing for ARM/KFC subsystem state.

## Dependencies and Integration Points

It depends on `linux/errno.h` for `-ENOTSUPP` and integrates the Exynos5422 implementation with the generic Exynos ASV code while avoiding link errors when ASV ARM support is disabled.

## Risks and Edge Cases

The enum order must stay synchronized with `exynos5422-asv.c`. Adding another subsystem requires updating `EXYNOS_ASV_SUBSYS_ID_MAX`, table setup, and callers. The stub makes unsupported builds fail at runtime rather than compile time, so callers must propagate nonzero return codes.

## Test Signals

Compile both `CONFIG_EXYNOS_ASV_ARM=y` and disabled variants. Runtime tests should verify unsupported configurations do not attempt to use uninitialized ASV subsystem data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5422-asv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/gs101-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/gs101-pmu.c

## Purpose

`gs101-pmu.c` describes the Google Tensor GS101 PMU register access policy and secure-access hooks for PMU_ALIVE registers. It provides regmap readable/writable ranges and SMC-backed read/write/update functions for PMU registers that Linux can read directly but must write through EL3 firmware.

## Important APIs, Types, and Functions

`gs101_pmu_registers[]` enumerates readable PMU register ranges. `gs101_pmu_ro_registers[]` enumerates ranges excluded from writes. `gs101_pmu_rd_table` and `gs101_pmu_wr_table` wrap those arrays as regmap access tables. `gs101_pmu_data` sets `.pmu_secure = true`, `.pmu_cpuhp = true`, and exposes the tables. Secure helpers are `tensor_sec_reg_write()`, `tensor_sec_reg_read()`, and `tensor_sec_update_bits()`. `tensor_sec_reg_rmw()`, `tensor_set_bits_atomic()`, and `tensor_is_atomic()` implement update strategy selection.

## Control Flow

The Exynos PMU core binds `gs101_pmu_data` and configures a regmap that honors the range tables. Reads call `tensor_sec_reg_read()`, which uses normal PMU MMIO reads because all PMU registers are read-accessible to Linux. Writes call `tensor_sec_reg_write()`, which invokes SMC function `0x82000504` with the physical PMU address, write operation id, and value. Update-bits calls use atomic set/clear register aliases for PMU_ALIVE offsets when supported, otherwise a secure read-modify-write SMC. Atomic updates iterate all bits in the mask and issue one secure write per bit with set or clear alias bits folded into the register offset.

## State and Persistence Behavior

There is no driver-private mutable state. Register access tables are constant. Persistent effects are PMU register writes mediated by firmware. The SMC context is the PMU base address supplied by the regmap bus context.

## Dependencies and Integration Points

The file depends on ARM SMCCC, Linux regmap access tables, Exynos PMU core data structures, and GS101 PMU register macros. It integrates with EL3 firmware implementing the Tensor PMU secure register SMC ABI and with CPU hotplug/power management through `pmu_cpuhp`.

## Risks and Edge Cases

The register range tables are large and must match hardware exactly; an overly broad writable range can expose destructive PMU writes. `tensor_set_bits_atomic()` mutates `offset` inside the bit loop but masks alias bits each iteration, which relies on aliases only occupying `BIT(15)|BIT(14)`. SMC failures are only warned and returned; callers must handle errors. Atomic updates issue many SMC calls for wide masks, which can be slow. Registers excluded by `tensor_is_atomic()` must stay synchronized with hardware that lacks set/clear aliases.

## Test Signals

Boot on GS101 should create a PMU regmap with expected readable/writable behavior, show successful SMC writes, and avoid warnings from secure calls. Tests should cover update-bits on PMU_ALIVE atomic registers, non-atomic exceptions, read-only ranges, CPU hotplug, suspend/resume, and firmware denial paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/gs101-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/s3c-pm-check.c -->
# sources/distributed-fs/ceph-client/drivers/soc/samsung/s3c-pm-check.c

## Purpose

`s3c-pm-check.c` implements an optional suspend/resume memory corruption checker for Samsung S3C-style platforms. It computes CRC32 checksums over system RAM chunks before suspend and compares them after resume to detect memory retention or restore failures.

## Important APIs, Types, and Functions

Public functions are `s3c_pm_check_prepare()`, `s3c_pm_check_store()`, `s3c_pm_check_restore()`, and `s3c_pm_check_cleanup()`. Internal traversal uses `s3c_pm_run_res()` and `s3c_pm_run_sysram()` over `iomem_resource`. Callback type `run_fn_t` returns the next CRC pointer. `s3c_pm_countram()` sizes the CRC buffer, `s3c_pm_makecheck()` stores CRCs, `s3c_pm_runcheck()` validates them, and `in_region()` skips volatile memory areas. Global state is `crc_size` and `crcs`.

## Control Flow

Prepare counts all `IORESOURCE_SYSTEM_RAM` resources in `CHECK_CHUNKSIZE` blocks and allocates the CRC array before late suspend. Store traverses the same RAM resources and writes one CRC per chunk using `crc32_le(~0, phys_to_virt(addr), left)`. Restore traverses again, skips chunks containing the current stack page or CRC buffer, recalculates CRCs, and logs mismatches. Cleanup frees the allocated CRC buffer separately because restore may run in a context that cannot sleep.

## State and Persistence Behavior

`crcs` persists only across one suspend/resume cycle in kernel heap memory. The checker intentionally avoids persistent storage. It reads physical RAM through direct mappings and reports errors to the kernel log; it does not repair memory.

## Dependencies and Integration Points

It depends on kernel resource trees, suspend hooks from Samsung PM code, CRC32, direct `phys_to_virt` mappings, `CONFIG_SAMSUNG_PM_CHECK_CHUNKSIZE`, and `S3C_PMDBG` logging. It integrates with platform suspend sequencing.

## Risks and Edge Cases

The code casts stack addresses through `u32`, which is only safe for legacy 32-bit platforms. `in_region()` performs arithmetic on `void *`, relying on compiler extensions. The chunk loop uses `addr < res->end` and `left = res->end - addr`, while resource ends are inclusive, so boundary coverage deserves scrutiny. Allocating `crc_size + 4` has no explicit overflow check. Memory modified legitimately during resume, beyond stack and CRC buffer, can trigger false positives.

## Test Signals

Run suspend/resume with PM debug enabled on supported 32-bit Samsung systems, verify no CRC mismatches on healthy hardware, inject controlled RAM corruption if possible, and test small/large chunk sizes. Static analysis should flag pointer-width assumptions if this code is built outside its intended architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/samsung/s3c-pm-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/sophgo/Kconfig

## Purpose

This Kconfig file defines build options for Sophgo SoC support drivers under `drivers/soc/sophgo`.

## Important APIs, Types, and Functions

`SOPHGO_CV1800_RTCSYS` is a tristate option for the CV1800 RTC subsystem MFD parent and selects `MFD_CORE`. `SOPHGO_SG2044_TOPSYS` is a tristate option for the SG2044 TOP system-controller MFD parent and also selects `MFD_CORE`. The menu appears only when `ARCH_SOPHGO || COMPILE_TEST`.

## Control Flow

Kconfig evaluation exposes a "Sophgo SoC drivers" menu for native Sophgo builds or compile-test builds. Selecting either option causes the Makefile to build its corresponding module/object.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time inclusion and module availability.

## Dependencies and Integration Points

It integrates the Sophgo MFD parent drivers with the kernel configuration system and the MFD subsystem dependency. Help text documents module names `cv1800-rtcsys` and `sg2044-topsys`.

## Risks and Edge Cases

Both options select MFD core but do not express OF or platform-bus dependencies explicitly, relying on broader kernel infrastructure. The CV1800 help text has a wording issue ("get support the"). Compile-test coverage is permitted even without Sophgo architecture.

## Test Signals

Run Kconfig generation for `ARCH_SOPHGO`, non-Sophgo with `COMPILE_TEST`, built-in, module, and disabled combinations. Confirm Makefile object selection matches the config symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/sophgo/Makefile

## Purpose

This Makefile maps Sophgo SoC Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SOPHGO_CV1800_RTCSYS) += cv1800-rtcsys.o` builds the CV1800 RTC subsystem MFD parent. `obj-$(CONFIG_SOPHGO_SG2044_TOPSYS) += sg2044-topsys.o` builds the SG2044 TOP syscon MFD parent.

## Control Flow

During kbuild, enabled or modular config symbols expand into built-in objects or modules according to standard `obj-*` rules.

## State and Persistence Behavior

There is no runtime state. The file controls build graph membership only.

## Dependencies and Integration Points

It depends on the Kconfig symbols in the same directory and integrates with the top-level `drivers/soc` build.

## Risks and Edge Cases

Object names must remain synchronized with source filenames and Kconfig module help. No ordering constraints are encoded; both drivers are independent.

## Test Signals

Build all four combinations of the two Sophgo symbols as built-in/modules and verify expected `.o` or `.ko` outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/cv1800-rtcsys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/sophgo/cv1800-rtcsys.c

## Purpose

`cv1800-rtcsys.c` is an MFD parent for the Sophgo CV1800 RTC subsystem. It creates a child RTC device and forwards the named alarm interrupt resource.

## Important APIs, Types, and Functions

`cv1800_rtcsys_irq_resources[]` contains one named IRQ resource, `"alarm"`. `cv1800_rtcsys_subdev[]` defines one child cell named `"cv1800b-rtc"`. `cv1800_rtcsys_probe()` resolves the platform IRQ by name and calls `devm_mfd_add_devices()`. The OF match table binds `"sophgo,cv1800b-rtc"`. Module metadata names the driver and license.

## Control Flow

When a matching platform device probes, the driver obtains the `"alarm"` IRQ, writes the resolved IRQ number into the static resource, and registers the RTC child with `PLATFORM_DEVID_AUTO`. Device-managed MFD registration handles cleanup on detach.

## State and Persistence Behavior

The only mutable state is the static IRQ resource start/end values. There is no persistent storage. Runtime child-device state is owned by the child RTC driver.

## Dependencies and Integration Points

It depends on platform-device probing, OF matching, the MFD core, and a child driver matching `"cv1800b-rtc"`. It assumes the DT node provides an interrupt named `"alarm"`.

## Risks and Edge Cases

Because the resource array is static, multiple instances would share and overwrite the same resource values; this is probably acceptable only if the hardware is singleton. Probe fails hard if the named IRQ is absent. The parent compatible is the same string as the child name, so binding documentation must make the parent/child relationship clear.

## Test Signals

Probe with valid DT and confirm a child `cv1800b-rtc` platform device appears with the correct alarm IRQ. Test missing IRQ name, module unload/reload, and deferred child driver probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/cv1800-rtcsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/sg2044-topsys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/sophgo/sg2044-topsys.c

## Purpose

`sg2044-topsys.c` is an MFD parent for the Sophgo SG2044 TOP system controller. Its role is to instantiate the PLL clock child device.

## Important APIs, Types, and Functions

`sg2044_topsys_subdev[]` contains one MFD cell named `"sg2044-pll"`. `sg2044_topsys_probe()` calls `devm_mfd_add_devices()` with that cell. The OF match table binds `"sophgo,sg2044-top-syscon"`. `sg2044_topsys_driver` is registered with `module_platform_driver()`.

## Control Flow

On matching platform probe, the driver registers the child PLL platform device with no extra resources. Cleanup is device-managed.

## State and Persistence Behavior

The file has no mutable driver-private state and no persistence. Child state is owned by the PLL driver.

## Dependencies and Integration Points

It depends on the platform bus, OF matching, and MFD core. It integrates SG2044 top system-controller DT nodes with the clock/PLL implementation through the `"sg2044-pll"` child name.

## Risks and Edge Cases

The child receives no explicit MMIO resource here, so it must obtain registers from the parent device, syscon/regmap, or another binding mechanism. Probe has no validation beyond MFD registration. Any future children need careful resource partitioning.

## Test Signals

Boot with an SG2044 top-syscon DT node and verify `sg2044-pll` child creation and PLL driver probe. Test module unload/reload and missing child driver behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sophgo/sg2044-topsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/sunxi/Kconfig

## Purpose

This Kconfig file defines Allwinner sunXi SoC support options for MBUS DMA quirks and SRAM controller support.

## Important APIs, Types, and Functions

`SUNXI_MBUS` is a bool defaulting to `ARCH_SUNXI`, depending on `ARM || ARM64`. `SUNXI_SRAM` is a bool defaulting to `ARCH_SUNXI` and selecting `REGMAP_MMIO`.

## Control Flow

When enabled, these symbols cause the Makefile to build `sunxi_mbus.o` and/or `sunxi_sram.o`. The defaults enable both for Allwinner platforms while permitting explicit disable if dependencies allow.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time inclusion.

## Dependencies and Integration Points

It integrates with architecture selection, DMA quirk setup, SRAM controller code, and regmap MMIO support.

## Risks and Edge Cases

`SUNXI_MBUS` is not user-visible in the snippet and depends on platform matching at runtime; wrong defaults could omit DMA offset fixups for old DTs. `SUNXI_SRAM` selects regmap support because the driver exposes syscon-style regmaps for selected registers.

## Test Signals

Validate ARM and ARM64 Allwinner defconfigs, non-Sunxi builds, and compile-test combinations. Confirm expected objects appear in build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/sunxi/Makefile

## Purpose

This Makefile connects sunXi Kconfig symbols to driver objects.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SUNXI_MBUS) += sunxi_mbus.o` and `obj-$(CONFIG_SUNXI_SRAM) += sunxi_sram.o` are the only build rules.

## Control Flow

Kbuild includes the two objects when their bool symbols are enabled.

## State and Persistence Behavior

There is no runtime state.

## Dependencies and Integration Points

It depends on the symbols defined in `Kconfig` and integrates with the parent `drivers/soc` build.

## Risks and Edge Cases

Object names must track source filenames. Since both symbols are bool, these drivers are built-in rather than modules in normal configurations.

## Test Signals

Build with each symbol enabled and disabled and confirm object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_mbus.c -->
# sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_mbus.c

## Purpose

`sunxi_mbus.c` installs DMA offset quirks for older Allwinner devices that perform DMA over the MBUS and lack modern interconnect descriptions in device tree.

## Important APIs, Types, and Functions

`sunxi_mbus_devices[]` lists compatible strings for display-engine virtual devices and MBUS-connected DMA clients. `sunxi_mbus_notifier()` handles platform bus add-device notifications. `sunxi_mbus_nb` registers that callback. `sunxi_mbus_platforms[]` limits activation to known Allwinner machine compatibles. `sunxi_mbus_init()` is an `arch_initcall`.

## Control Flow

At arch init, the driver checks whether the running machine matches a supported Allwinner platform. If so, it registers a platform bus notifier. For each newly added platform device, the notifier ignores non-add events, ignores devices whose OF compatible is not in `sunxi_mbus_devices`, and ignores devices that already have an `interconnects` property. For old bindings, it calls `dma_direct_set_offset(dev, PHYS_OFFSET, 0, SZ_4G)` so DMA address 0 maps to physical `PHYS_OFFSET` across a 4 GiB window.

## State and Persistence Behavior

State is limited to the registered notifier. The DMA offset becomes persistent per device for the device lifetime and affects all subsequent direct DMA mapping operations.

## Dependencies and Integration Points

It depends on OF machine/device compatible matching, platform bus notifiers, direct DMA mapping internals, and `PHYS_OFFSET`. It integrates legacy Allwinner display/video/camera devices with the DMA API.

## Risks and Edge Cases

The compatibility lists are manually curated; missing a device can produce broken DMA on old DTs. Applying the quirk to a device with a correct interconnect path would be wrong, hence the `interconnects` skip. Notifier registration has no unregister path because this is built-in init code. The 4 GiB window and `PHYS_OFFSET` assumptions must match the SoC memory map.

## Test Signals

Boot older and newer Allwinner DTs and verify devices without `interconnects` receive the expected DMA offset while modern DTs do not. Exercise DRM, video-engine, and CSI DMA, especially on systems with nonzero RAM base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_mbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_sram.c -->
# sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_sram.c

## Purpose

`sunxi_sram.c` controls Allwinner SRAM routing between CPU and hardware clients, exposes selected SRAM-controller registers as a syscon/regmap, populates SRAM child devices, and provides debugfs visibility of SRAM section ownership.

## Important APIs, Types, and Functions

Core data types are `struct sunxi_sram_func`, `struct sunxi_sram_data`, `struct sunxi_sram_desc`, and `struct sunxi_sramc_variant`. Static descriptors define routeable SRAM sections such as A3-A4, C1, D, and A64 C. Public exported APIs are `sunxi_sram_claim()` and `sunxi_sram_release()`. `sunxi_sram_of_parse()` reads `allwinner,sram` phandles. `sunxi_sram_show()` implements debugfs display. `sunxi_sram_regmap_accessible_reg()` gates regmap access to EMAC clocks, LDO control, and THS offset registers. `sunxi_sram_probe()` maps MMIO, registers optional syscon regmap, populates child devices, and creates debugfs.

## Control Flow

At built-in platform-driver probe, the driver records the device, obtains variant data, maps the controller register block, optionally registers a regmap for variant-specific registers, populates child nodes, and creates `/sys/kernel/debug/sram`. A client calls `sunxi_sram_claim(dev)`, which parses its `allwinner,sram` phandle and function value, rejects unavailable or unknown SRAM nodes, checks the section's `claimed` flag under `sram_lock`, writes the function selection bits into the SRAM control register, and marks the section claimed. Release parses the same phandle and clears the claimed flag without changing the hardware mux.

## State and Persistence Behavior

Global state includes `sram_dev`, `base`, the spinlock, and static section descriptors with `claimed` flags. Hardware mux register writes persist until changed or reset. Regmap accesses share the same spinlock to serialize with claim/release writes.

## Dependencies and Integration Points

It depends on OF phandles, `mmio-sram` child layout, platform MMIO resources, regmap MMIO, syscon registration, debugfs, and the exported `<linux/soc/sunxi/sunxi_sram.h>` API used by device drivers such as EMAC, USB OTG, display, or video engines.

## Risks and Edge Cases

The singleton globals mean multiple SRAM controllers would conflict. `release()` clears only software ownership, not hardware routing back to CPU. Debugfs walks OF nodes and addresses without extensive NULL checks. Clients that fail to release can permanently block a section. Function descriptors are static and must match DT binding values exactly. The regmap access callback relies on `dev_get_drvdata()` being variant data.

## Test Signals

Test client claim/release paths, double-claim `-EBUSY`, invalid phandles, unavailable SRAM nodes, and debugfs output. Hardware tests should verify SRAM mux changes for EMAC/USB/VE/DE clients and regmap access restrictions on each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/Kconfig

## Purpose

This Kconfig file defines NVIDIA Tegra SoC family support symbols and common SoC driver options for fuse, flow controller, PMC, voltage couplers, and CBB error handling.

## Important APIs, Types, and Functions

Architecture options cover 32-bit `ARCH_TEGRA_2x_SOC`, `3x`, `114`, `124` and ARM64 `132`, `210`, `186`, `194`, `234`, `238`, `241`, and `264`. Common symbols include `SOC_TEGRA_FUSE`, `SOC_TEGRA_FLOWCTRL`, `SOC_TEGRA_PMC`, `SOC_TEGRA20_VOLTAGE_COUPLER`, `SOC_TEGRA30_VOLTAGE_COUPLER`, and `SOC_TEGRA_CBB`.

## Control Flow

Under `ARCH_TEGRA`, users select SoC families by architecture. Each family selects required pinctrl, timer, errata, mailbox, PMC, flowctrl, and regulator support as appropriate. `SOC_TEGRA_CBB` is enabled by default for Tegra194 or Tegra234 families and builds the Control Backbone error-reporting drivers.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time platform feature inclusion.

## Dependencies and Integration Points

It integrates Tegra SoC drivers with ARM/ARM64 architecture menus, pinctrl, mailbox, timers, PM domains, OPP, regmap, generic pinconf, IRQ domains, and SoC bus support.

## Risks and Edge Cases

Selections encode hardware assumptions; missing `select` entries can cause boot-time subsystem failures, while over-selection increases build footprint. Several ARM64 CBB-capable newer SoCs use the Tegra234 CBB implementation despite the symbol name. Big-endian exclusion is explicit for several ARM64 SoCs.

## Test Signals

Run old 32-bit Tegra and modern ARM64 defconfigs, randconfig with `ARCH_TEGRA`, and module/built-in CBB builds. Verify selected dependencies match object files in Makefiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/Makefile

## Purpose

This Makefile builds common Tegra SoC support and conditionally includes feature-specific objects.

## Important APIs, Types, and Functions

It always descends into `fuse/` and `cbb/` and builds `common.o`. Conditional objects include `flowctrl.o`, `pmc.o`, Tegra20/30 voltage couplers, and `ari-tegra186.o`.

## Control Flow

Kbuild includes subdirectories first, then object files based on the Kconfig symbols. The CBB subdirectory internally checks `CONFIG_SOC_TEGRA_CBB`.

## State and Persistence Behavior

There is no runtime state. This is build orchestration only.

## Dependencies and Integration Points

It depends on Tegra Kconfig symbols and integrates the SoC directory with fuse, CBB, PMC, flowctrl, OPP/regulator, and ARI code.

## Risks and Edge Cases

`obj-y += cbb/` always enters the directory, so its Makefile must guard object selection correctly. `common.o` always builds for Tegra SoC support and must keep dependencies broadly available.

## Test Signals

Build Tegra configs with and without flowctrl, PMC, voltage couplers, Tegra186, and CBB to confirm expected object graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/ari-tegra186.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/ari-tegra186.c

## Purpose

`ari-tegra186.c` registers a panic notifier for Tegra186 that reads uncore machine-check registers through firmware SMC calls and logs pending SError/MCA state during panic.

## Important APIs, Types, and Functions

`read_uncore_mca()` wraps `arm_smccc_smc()` using `SMC_SIP_INVOKE_MCE | MCE_SMC_READ_MCA`. `tegra186_ari_panic_handler()` loops over `bank_names[]` and prints status, address, and misc registers when `SERR_STATUS_VAL` is set. `tegra186_ari_panic_nb` is registered by `tegra186_ari_init()` using `atomic_notifier_chain_register()` if the machine is compatible with `"nvidia,tegra186"`.

## Control Flow

At early init, Tegra186 systems register the panic notifier. During panic, the handler reads the status subindex for each uncore MCA bank. Banks with valid SError status trigger additional reads of address, MSC1, and MSC2 subindices and emit `pr_crit()` diagnostics.

## State and Persistence Behavior

The file keeps only the static notifier and bank-name table. It does not clear MCA state or persist logs beyond the kernel console/log buffer.

## Dependencies and Integration Points

It depends on ARM SMCCC, the Tegra186 firmware MCE SMC ABI, OF machine matching, and the kernel panic notifier chain. It integrates with platform crash diagnostics rather than normal error recovery.

## Risks and Edge Cases

SMC return status is not checked; `res.a2` is trusted. Panic notifier context is fragile, so calls must not sleep. If firmware ABI changes, decoded values can be wrong. Only instance 0 is read for all banks.

## Test Signals

On Tegra186, trigger controlled panic paths with injected MCA/SError state and verify bank diagnostics appear. Confirm non-Tegra186 systems do not register the notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/ari-tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/Makefile

## Purpose

This Makefile builds Tegra Control Backbone error handling drivers when CBB support is enabled.

## Important APIs, Types, and Functions

Inside `ifdef CONFIG_SOC_TEGRA_CBB`, it builds common `tegra-cbb.o`, Tegra194-specific `tegra194-cbb.o` when `CONFIG_ARCH_TEGRA_194_SOC` is enabled, and CBB2 `tegra234-cbb.o` when `CONFIG_ARCH_TEGRA_234_SOC` is enabled.

## Control Flow

The parent Tegra Makefile always descends into `cbb/`, but this file emits objects only when the CBB symbol is active.

## State and Persistence Behavior

There is no runtime state.

## Dependencies and Integration Points

It connects the common CBB helper layer with SoC-specific implementations and Kconfig architecture symbols.

## Risks and Edge Cases

The CBB2 implementation supports compatible data for newer SoCs too, but object selection is tied to `ARCH_TEGRA_234_SOC`; configs for newer SoCs must ensure this object is available through Kconfig selection or shared symbol behavior.

## Test Signals

Build Tegra194, Tegra234, and non-CBB Tegra configurations and verify object inclusion/exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra-cbb.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra-cbb.c

## Purpose

`tegra-cbb.c` is the common helper layer for Tegra Control Backbone error drivers. It centralizes diagnostic printing, debugfs registration, IRQ lookup, and calls through `struct tegra_cbb_ops`.

## Important APIs, Types, and Functions

Exported helper-style functions include `tegra_cbb_print_err()`, `tegra_cbb_print_cache()`, `tegra_cbb_print_prot()`, `tegra_cbb_stall_enable()`, `tegra_cbb_fault_enable()`, `tegra_cbb_error_clear()`, `tegra_cbb_get_status()`, `tegra_cbb_get_irq()`, and `tegra_cbb_register()`. `tegra_cbb_err_show()` delegates debugfs reads to SoC-specific `debugfs_show`. `tegra_cbb_err_debugfs_init()` creates a single `tegra_cbb_err` debugfs file.

## Control Flow

SoC-specific probe code fills a `struct tegra_cbb` with ops and calls `tegra_cbb_register()`. Registration optionally initializes debugfs, asks the SoC driver to request interrupts, enables errors through SoC ops, and issues a full-system barrier. At runtime, SoC ISRs and debugfs show callbacks use the common print helpers for consistent console/seq_file output.

## State and Persistence Behavior

Common state is limited to a static debugfs root/file guard. Hardware state is manipulated through SoC callbacks. The debugfs file stores the `cbb` pointer from the first registration as private data, while SoC debugfs callbacks may iterate their own global lists.

## Dependencies and Integration Points

It depends on debugfs, platform IRQ APIs, seq_file, printk, and the CBB public header. It integrates Tegra194 and CBB2 drivers through the ops table.

## Risks and Edge Cases

`tegra_cbb_get_irq()` accepts one or two IRQs and treats one IRQ as secure; callers passing a NULL `nonsec_irq` are safe only when platform IRQ count is one. The debugfs creation helper uses `debugfs_create_file()` once and does not create a directory. If ops are missing, wrapper functions silently no-op or return zero, which can hide incomplete SoC implementations.

## Test Signals

Test one-IRQ and two-IRQ platform devices, debugfs read paths with and without pending errors, and ops tables with all required callbacks. Verify printed cache/protection decoding matches AXI attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra-cbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra194-cbb.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra194-cbb.c

## Purpose

`tegra194-cbb.c` handles Control Backbone/FlexNoC errors on Tegra194. It registers per-NoC platform devices, enables CBB error logging, decodes ErrLogger registers with route/aperture lookup tables, reports AXI/APB transaction details, and escalates fatal in-band CCPLEX errors.

## Important APIs, Types, and Functions

Key structures are `tegra194_cbb_packet_header`, `tegra194_cbb_aperture`, `tegra194_cbb_userbits`, `tegra194_cbb_noc_data`, `tegra194_axi2apb_bridge`, and `tegra194_cbb`. Large static tables map initiators, target flows, route ids, apertures, and error codes for CBB central, BPMP, AON, RCE, and SCE NoCs. Parse helpers include `cbbcentralnoc_parse_routeid()`, `bpmpnoc_parse_routeid()`, `aonnoc_parse_routeid()`, `scenoc_parse_routeid()`, `cbbcentralnoc_parse_userbits()`, and `clusternoc_parse_userbits()`. Runtime operations are exposed through `tegra194_cbb_ops`.

## Control Flow

Probe obtains SoC data from OF compatible strings, masks in-band SError through `tegra194_miscreg_mask_serror()` for CBB central, maps the ErrLogger register resource, resolves secure/nonsecure IRQs, optionally maps shared AXI2APB bridge status resources, adds the instance to a global `cbb_list`, and calls common CBB registration. Registration requests IRQs, enables stall and fault bits on three ErrLoggers, and creates debugfs. On interrupt or debugfs read, the driver scans all registered NoCs, reads three ErrVld bits, selects the first active ErrLogger, reads ErrLog0/1/2/3/4/5, decodes transaction type, error code, route id, target flow/subrange, reconstructed address, user bits, cache/protection attributes, and optional AXI2APB bridge raw status. It clears the ErrLogger after printing. Fatal SLV errors from CCPLEX can trigger `BUG()`, while DEC/SEC/UNS/DISC paths warn instead.

## State and Persistence Behavior

Each instance stores mapped registers, resource identity, IRQ numbers, decoded ErrLog snapshots, NoC metadata, and optional shared AXI2APB bridge mappings. A global spinlocked `cbb_list` tracks instances. Hardware error logger state persists until cleared via ErrClr. On resume noirq, error reporting is re-enabled.

## Dependencies and Integration Points

It depends on platform/OF resources, Tegra fuse/miscreg helpers, common CBB helpers, debugfs, IRQ handling, MMIO accessors, and FlexNoC register semantics. It integrates with DT compatibles such as `"nvidia,tegra194-cbb-noc"` and the `nvidia,axi2apb` phandle.

## Risks and Edge Cases

The file contains large hand-maintained lookup tables; wrong entries produce misleading diagnostics. `clusternoc_parse_userbits()` appears to extract `axprot` using `CLUSTER_NOC_AXCACHE` rather than `CLUSTER_NOC_AXPROT`, which is a bug signal. Several decoded indexes are used to index string arrays without full bounds checks. The ISR holds a spinlock while printing extensive diagnostics and may call `BUG()`. Only one active ErrLogger is printed because `print_errlog()` uses `else if`. Shared bridge mapping is reused from the first instance with bridges.

## Test Signals

Validate probe for all Tegra194 NoC compatibles, one/two IRQ layouts, AXI2APB phandle mapping, suspend/resume re-enable, debugfs reads, and injected SLV/DEC/SEC/UNS/TMO errors. Static review should check field masks, table bounds, and the suspected `CLUSTER_NOC_AXPROT` extraction issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra194-cbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra234-cbb.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra234-cbb.c

## Purpose

`tegra234-cbb.c` implements Control Backbone 2.0 error reporting for Tegra234-derived and newer NVIDIA SoCs. It decodes fabric notifier/monitor registers, supports DT and ACPI matching, maps target ids to fabric target blocks, reports transaction attributes, masks SError for selected fabrics, and warns on CCPLEX in-band errors.

## Important APIs, Types, and Functions

Key types are `tegra234_target_lookup`, `tegra234_fabric_lookup`, `tegra234_cbb_fabric`, and `tegra234_cbb`. Register helpers include `tegra234_cbb_fault_enable()`, `tegra234_cbb_error_clear()`, `tegra234_cbb_get_status()`, and `tegra234_cbb_mask_serror()`. Decode/print paths include `tegra234_cbb_print_error()`, `print_errlog_err()`, `print_errmonX_info()`, and `print_err_notifier()`. Timeout helpers include `tegra234_sw_lookup_target_timeout()`, `tegra234_hw_lookup_target_timeout()`, and `tegra234_cbb_lookup_apbslv()`. The file contains fabric/error/initiator/target tables for Tegra234, Tegra238, Tegra241, Tegra264, and T254 ACPI UID variants.

## Control Flow

Probe selects fabric data from OF match data or ACPI HID/UID, allocates an instance, maps fabric registers, obtains the secure IRQ, checks firewall write access, adds the instance to the global list, optionally masks SError through the ERD mask offset, and registers with the common CBB layer. Error enable writes the fabric notifier interrupt-enable mask. On IRQ, the driver scans registered fabrics, reads notifier status, maps each active error monitor address through notifier address-index registers, reads monitor status/overflow and logged address/attributes/user bits, decodes error type and initiator, optionally performs software or hardware target timeout lookup, clears monitor status, and emits a warning for CCPLEX errors on fabrics with ERD masking.

## State and Persistence Behavior

Each instance stores immutable fabric metadata, mapped MMIO, resource base, IRQ, current monitor pointer, current error type/mask, decoded access address and attribute registers. A global spinlocked `cbb_list` tracks active fabrics. Hardware notifier and monitor status persists until `tegra234_cbb_error_clear()` writes force/status-clear registers. Resume noirq reapplies SError masking and fault enable.

## Dependencies and Integration Points

It depends on platform resources, OF and ACPI matching, common Tegra CBB helpers, NUMA helpers, MMIO accessors, IRQ APIs, debugfs, and SoC-specific firewall/notifier register layouts. It integrates with CBB2 fabrics for multiple SoC generations via data tables rather than separate drivers.

## Risks and Edge Cases

Table correctness is critical across many SoCs; out-of-range fabric ids can index `fab_list` before validation in some print paths. `sprintf()` into fixed 64-byte stack buffers relies on target names staying short. The ISR holds a spinlock while printing large diagnostics. If firewall write access is blocked, probe returns success without adding the instance or enabling errors, which can look like a silent no-op. NUMA filtering suppresses some remote-socket errors. ACPI support depends on exact UID strings.

## Test Signals

Test DT matching for all listed compatibles and ACPI `NVDA1070` UIDs, firewall-allowed and firewall-blocked probes, single secure IRQ handling, debugfs dumping, suspend/resume re-enable, timeout lookups for AXI and AXI2APB targets, NUMA filtering, and injected error types including overflow bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra234-cbb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/common.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/common.c

## Purpose

`common.c` provides shared Tegra SoC helpers: machine detection and OPP table initialization for core devices that need process/speedo-aware operating points.

## Important APIs, Types, and Functions

`soc_is_tegra()` checks the machine compatible against older Tegra families. `tegra_core_dev_init_opp_state()` initializes a device's current OPP/performance state from its clock rate. `devm_tegra_core_dev_init_opp_table()` is exported and configures OPP supported-hardware filtering, optional OPP table loading, and optional initial state sync.

## Control Flow

Callers pass a device and `struct tegra_core_opp_params`. The helper sets a dummy clock-name config so even devices without DT OPPs can use the same rate path. For Tegra20 it uses `tegra_sku_info.soc_process_id`; for Tegra30/Tegra114 it uses `soc_speedo_id` to set `supported_hw`. It registers OPP config, returns `-ENODEV` on Tegra124+ where old supported-hw filtering is not used, otherwise loads the DT OPP table. If requested, it temporarily enables runtime PM, calls `dev_pm_opp_set_rate()` with the current clock rate to establish a GENPD performance vote, and restores runtime PM state.

## State and Persistence Behavior

No global mutable state is owned here. Device-managed OPP config/table allocations persist for the device lifetime. Runtime PM may be briefly enabled to cache GENPD performance state.

## Dependencies and Integration Points

It depends on OF machine matching, clocks, runtime PM, PM OPP, Tegra fuse SKU data, and `soc/tegra/common.h`. It integrates core Tegra devices with OPP and generic power-domain performance voting.

## Risks and Edge Cases

Returning `-ENODEV` for unsupported/newer paths is expected but callers must treat it correctly. If a device has no clock or zero clock rate, initialization fails. Temporarily enabling runtime PM can interact with drivers that assume RPM state is untouched. Supported-hardware bit shifts rely on fuse ids being in range.

## Test Signals

Test Tegra20/Tegra30/Tegra114 OPP filtering by process/speedo id, devices with empty OPP tables, `init_state` true/false, missing clock, zero clock, and runtime PM initially enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/flowctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/flowctrl.c

## Purpose

`flowctrl.c` manages the Tegra flow controller used on older Tegra SoCs for CPU halt and power-gating entry/exit sequences.

## Important APIs, Types, and Functions

Global MMIO state is `tegra_flowctrl_base`. Offset arrays map CPU ids to halt and CSR registers. Public functions are `flowctrl_read_cpu_csr()`, `flowctrl_write_cpu_csr()`, `flowctrl_write_cpu_halt()`, `flowctrl_cpu_suspend_enter()`, and `flowctrl_cpu_suspend_exit()`. `tegra_flowctrl_probe()` remaps the controller through the platform driver. `tegra_flowctrl_init()` performs early mapping from DT or a 32-bit fallback physical address.

## Control Flow

Early init checks `soc_is_tegra()`, finds a compatible flowctrl node, or falls back to `0x60007000` on 32-bit Tegra if no node exists. It ioremaps the resource so low-level CPU suspend code can run before the platform driver probes. Later, the built-in platform driver remaps via devm and unmaps the early mapping. Suspend enter reads the target CPU CSR, clears WFE/WFI bitmaps according to chip id, chooses WFE for Tegra20 and Tegra30 and WFI for Tegra114/124, sets interrupt/event flags and enable, writes the CSR, then clears event/interrupt flags on other CPUs. Suspend exit clears power-gating enable and WFE/WFI selection.

## State and Persistence Behavior

The mapped base pointer persists globally. Hardware CSR/halt writes persist in the flow controller until updated. No heap state is allocated beyond managed mapping.

## Dependencies and Integration Points

It depends on OF address parsing, platform resources, Tegra chip-id fuse helpers, CPU masks, and `soc/tegra/flowctrl.h` register definitions. It integrates with CPU idle/suspend and power-gating paths.

## Risks and Edge Cases

Offset arrays cover four CPUs; callers must not pass larger CPU ids. Functions warn and no-op if called before initialization. The early fallback mapping is ARM-only and hard-coded. The platform probe unmaps the old base after replacing it, so call ordering during probe must avoid concurrent flowctrl users.

## Test Signals

Test early init with DT node, 32-bit fallback, and Tegra186+ no-flowctrl path. Exercise CPU suspend/resume on Tegra20/30/114/124, CPU hotplug, and invalid initialization ordering. Inspect CSR bits around suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/flowctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/Makefile

## Purpose

This Makefile builds Tegra fuse, speedo, and APBMISC support objects.

## Important APIs, Types, and Functions

Always-built objects are `fuse-tegra.o`, `fuse-tegra30.o`, and `tegra-apbmisc.o`. Conditional speedo/fuse objects are selected for Tegra20, Tegra30, Tegra114, Tegra124/132, and Tegra210.

## Control Flow

Kbuild includes base fuse/APBMISC support for Tegra, then adds SoC-family-specific calibration/speedo files according to architecture config symbols.

## State and Persistence Behavior

There is no runtime state in the Makefile. The built objects provide runtime fuse/SKU/speedo data used by other Tegra drivers.

## Dependencies and Integration Points

It integrates with Tegra SoC Kconfig and supplies objects consumed indirectly by common SoC code, OPP setup, chip-id helpers, and platform identification.

## Risks and Edge Cases

Tegra132 reuses `speedo-tegra124.o`, so source compatibility must remain intentional. Missing a speedo object can break voltage/OPP decisions. Always-built objects must avoid depending on unavailable SoC-specific symbols.

## Test Signals

Build all supported Tegra family configs and verify fuse/speedo symbols link. Runtime tests should confirm `tegra_sku_info` and chip-id helpers are populated before dependent drivers call them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/Makefile -->
