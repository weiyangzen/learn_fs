# subset-b-001270 Research

Grouped research for the listed EDAC files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/edac/Kconfig Research

## Purpose
This Kconfig file defines the Linux EDAC subsystem configuration surface and all memory-controller, cache, PCI, firmware-first, scrub, ECS, memory-repair, and SoC-specific EDAC driver options under `drivers/edac`. It is the policy layer that decides which EDAC core features and hardware drivers can be selected for a build.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. The key exported symbols are `EDAC`, `EDAC_DEBUG`, `EDAC_DECODE_MCE`, `EDAC_GHES`, `EDAC_SCRUB`, `EDAC_ECS`, `EDAC_MEM_REPAIR`, and the hardware driver symbols consumed by the Makefile, including `EDAC_AMD64`, `EDAC_AL_MC`, `EDAC_AMD76X`, `EDAC_ALTERA`, `EDAC_ALTERA_*`, and `EDAC_CORTEX_A72`. `EDAC_ATOMIC_SCRUB` and `EDAC_SUPPORT` are helper booleans used by architecture/platform code.

## Control Flow
Kconfig processing first requires `HAS_IOMEM`, `EDAC_SUPPORT`, and `RAS` before exposing the `EDAC` menu. When `EDAC` is enabled, feature booleans and driver tristates/bools become available subject to architecture, bus, and subsystem dependencies. Driver symbols gate compilation through `drivers/edac/Makefile`.

## State and Persistence
The persistent output is kernel build configuration in `.config`. At runtime, this file has no state, but its selected symbols determine whether EDAC sysfs, debugfs, scrub, ECS, memory repair, MCE decoding, firmware-first GHES reporting, and hardware drivers exist in the built kernel or modules.

## Dependencies and Integration Points
The top-level EDAC menu integrates with RAS, architecture support for I/O memory, ACPI/GHES, PCI, x86 MCE decoding, ARM64, LoongArch, PowerPC, SoC platform symbols, and many peripheral subsystem symbols such as `CACHE_L2X0`, `SRAM`, `GENERIC_ALLOCATOR`, `MTD_NAND_DENALI`, `PL330_DMA`, `USB_DWC2`, `SPI_CADENCE_QUADSPI`, and `MMC_DW`. The AMD64 option depends on `AMD_NB`, `AMD_NODE`, and `EDAC_DECODE_MCE`, and implies `AMD_ATL` for normalized-address translation on newer AMD systems.

## Risks and Edge Cases
Configuration mismatches are the main risk. Enabling GHES may suppress native hardware-driven reporting in firmware-first systems. Several Altera options are bool-only and depend on `EDAC=y`, so they are not module-friendly. Platform dependencies can hide drivers during compile testing if `COMPILE_TEST` is absent. Incorrect dependency changes can either expose unbuildable drivers or hide valid EDAC support.

## Test Signals
Useful tests are `make olddefconfig`, `make menuconfig`, and targeted builds with representative symbols enabled. Cross-architecture build tests should confirm each enabled config reaches the expected object in the Makefile. Runtime signals include EDAC devices under `/sys/devices/system/edac`, GHES/EDAC ownership behavior, and debugfs/sysfs feature files when the corresponding feature symbols are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/edac/Makefile Research

## Purpose
This Makefile maps EDAC Kconfig symbols to kernel objects. It builds the EDAC core, optional core feature objects, MCE decoder support, and individual hardware EDAC drivers.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build targets are `edac_core.o`, `edac_mce_amd.o`, `amd64_edac.o`, `al_mc_edac.o`, `amd76x_edac.o`, `altera_edac.o`, and `a72_edac.o`. Composite objects include `mpc85xx_edac_mod-y`, `layerscape_edac_mod-y`, `skx_edac_common-y`, `skx_edac-y`, `i10nm_edac-y`, and `imh_edac-y`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments after Kconfig selection. `CONFIG_EDAC` builds `edac_core.o` from memory-controller, device, module, sysfs, and workqueue sources. `CONFIG_PCI` conditionally adds EDAC PCI core files. Optional feature symbols append debugfs, scrub, ECS, and memory repair objects. Hardware-specific symbols then append their driver object files.

## State and Persistence
The Makefile persists no runtime state. It determines build artifacts: built-in objects for `y`, modules for `m` where allowed by Kconfig, and omitted objects for unset symbols.

## Dependencies and Integration Points
The file integrates directly with the symbols declared in `drivers/edac/Kconfig`. It also encodes shared-object relationships, such as Intel SKX/I10NM/IMH drivers sharing `skx_edac_common.o`, and Freescale/Layerscape drivers sharing `fsl_ddr_edac.o`.

## Risks and Edge Cases
Symbol/object drift is the main risk: adding a Kconfig option without a Makefile entry yields an unbuildable or unreachable driver, while a Makefile entry with missing Kconfig gating can build on unsupported platforms. Shared objects can create link surprises if multiple related drivers are built with incompatible built-in/module settings.

## Test Signals
Run targeted kernel builds with `CONFIG_EDAC=y`, `CONFIG_EDAC_DEBUG=y`, `CONFIG_EDAC_AMD64=m`, `CONFIG_EDAC_AL_MC=m`, `CONFIG_EDAC_AMD76X=m`, `CONFIG_EDAC_ALTERA=y`, and `CONFIG_EDAC_CORTEX_A72=m` as architecture-appropriate. Kbuild output should include the expected `.o` or `.ko` files and no unresolved symbols from optional core pieces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/a72_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/a72_edac.c Research

## Purpose
This driver reports ARM Cortex-A72 L1 CPU RAM and L2 cache ECC/parity syndrome state through the EDAC device framework. It polls compatible CPUs, reads architectural implementation-defined syndrome registers, clears valid reports, and reports correctable versus fatal events.

## Important APIs, Types, and Functions
Key register definitions are `SYS_CPUMERRSR_EL1` and `SYS_L2MERRSR_EL1`, with valid/fatal bits and fields for L1 RAM ID and L2 CPUID/WAY. `struct mem_err_synd_reg` carries per-CPU CPU/L2 syndrome snapshots. `report_errors()` decodes and reports EDAC CE/UE events. `read_errors()` runs on the target CPU via SMP call and clears valid syndrome registers. `a72_edac_check()` iterates online compatible CPUs under `cpus_read_lock()`. `a72_edac_probe()` allocates and registers `struct edac_device_ctl_info`; `a72_edac_driver_init()` discovers compatible CPU device-tree nodes with `edac-enabled`.

## Control Flow
Module init scans all possible CPUs for `compatible = "arm,cortex-a72"` and an `edac-enabled` property, records them in `compat_mask`, creates a simple platform device, then registers the platform driver. Probe allocates one EDAC device named `cpu` with one instance per possible CPU and two blocks per instance (`L` block 0 for L1 and block 1 for L2). EDAC polling calls `a72_edac_check()`, which synchronously invokes `read_errors()` on each online CPU in `compat_mask`; `report_errors()` then emits `edac_device_handle_ce()` or `edac_device_handle_ue()` based on the fatal bit.

## State and Persistence
Persistent driver state is small: the global `compat_mask`, global `a72_pdev`, and the EDAC device control object stored in platform drvdata. Hardware syndrome state exists in CPU system registers until read and cleared. The driver does not persist counters itself; EDAC core tracks reported events.

## Dependencies and Integration Points
The driver depends on ARM64 system register access, SMP cross-calls, Open Firmware CPU nodes, platform-device registration, and EDAC device APIs from `edac_module.h`. Device-tree integration requires CPU nodes to opt in with `edac-enabled`; without that property the driver silently does not register a device.

## Risks and Edge Cases
The driver only scans possible CPUs at module init, so CPU nodes or properties must be present then. It skips offline CPUs during checks, so errors on offline CPUs are not read until they come online and are polled. Syndrome registers are cleared immediately after a valid read; if reporting later failed, the hardware status would already be consumed. Fatal cache errors are reported as EDAC UEs but no panic policy is implemented here.

## Test Signals
Build with `CONFIG_EDAC_CORTEX_A72` on ARM64. Runtime smoke tests need Cortex-A72 CPU DT nodes with `edac-enabled` and should show an EDAC device for `a72-edac`. Hardware or firmware-assisted error injection can validate that L1 RAM IDs map to the expected messages and that L2 CPUID/WAY is included. Hotplug tests should verify `cpus_read_lock()` iteration remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/a72_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/al_mc_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/al_mc_edac.c Research

## Purpose
This platform driver reports ECC errors from Amazon Annapurna Labs Alpine memory controllers. It supports correctable and uncorrectable DRAM ECC events, reporting syndrome/address fields through the EDAC memory-controller framework using either interrupts or polling.

## Important APIs, Types, and Functions
`struct al_mc_edac` stores the MMIO base, spinlock, and CE/UE IRQ numbers. Register definitions cover ECC config, clear, count, CE/UE address, and syndrome registers. `prepare_msg()` formats rank/row/bank-group/bank/column/syndrome details. `handle_ce()` and `handle_ue()` read count/address/syndrome registers, clear status bits, and call `edac_mc_handle_error()`. `al_mc_edac_check()` is the polling hook for missing IRQs. `al_mc_edac_irq_handler_ce()` and `_ue()` dispatch interrupt handling. `get_scrub_mode()` maps the controller scrub-disabled bit to EDAC scrub mode. Probe allocates one chip-select layer and configures DIMM metadata.

## Control Flow
Probe maps resource 0, allocates `mem_ctl_info` with private `struct al_mc_edac`, records optional named IRQs `ue` and `ce`, and chooses EDAC interrupt or polling opstate. If either IRQ is absent, the missing side is handled in `al_mc_edac_check()`; if both are present, the driver uses interrupt mode. It initializes EDAC capabilities, scrub mode, and DIMM grain, registers the memory controller, then requests any available IRQs. CE and UE paths read the count first; zero count returns `IRQ_NONE` or no polling event, nonzero count snapshots address/syndrome data, clears hardware count/error bits, formats a message, and reports to EDAC under a spinlock.

## State and Persistence
Driver state is per-controller MMIO base, IRQ numbers, and spinlock stored in `mci->pvt_info`. Hardware holds error counts and first/latest address/syndrome registers until cleared. EDAC core persists event counters in its normal sysfs state. Device-managed cleanup actions free the EDAC allocation and delete the MC registration on teardown.

## Dependencies and Integration Points
The driver depends on device-tree compatible `amazon,al-mc-edac`, platform MMIO resources, optional named IRQs, relaxed MMIO accessors, EDAC MC APIs, and OF IRQ lookup. It reports DDR3/DDR4 SECDED capability and exposes hardware scrub status to EDAC.

## Risks and Edge Cases
The handler clears hardware status before calling EDAC, so a crash during reporting could lose the hardware snapshot. Only one address/syndrome tuple is reported per CE or UE batch count; multiple accumulated errors may be counted but not individually localized. Partial IRQ configurations are intentional but depend on EDAC polling for the missing side. The spinlock serializes EDAC reporting but does not cover the full read/clear sequence.

## Test Signals
Build with `CONFIG_EDAC_AL_MC` and a DT node with MMIO resource and optional `ue`/`ce` IRQs. Runtime signals are successful `edac_mc_add_mc()`, interrupt request success, EDAC CE/UE counters increasing, and messages containing rank/row/bg/bank/column/syndrome fields. Tests should cover both full IRQ mode and missing-IRQ polling fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/al_mc_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/altera_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/altera_edac.c Research

## Purpose
This driver provides EDAC support for Altera/Intel SoCFPGA memories: SDRAM controllers, L2 cache, OCRAM, and several Arria10/Stratix10 peripheral ECC blocks such as Ethernet, NAND, DMA, USB, QSPI, and SDMMC. It uses both EDAC memory-controller and EDAC device frameworks and handles legacy Cyclone5/Arria5 style devices as well as Arria10/Stratix10 ECC-manager interrupt aggregation.

## Important APIs, Types, and Functions
SDRAM support is driven by `struct altr_sdram_prv_data` tables `c5_data` and `a10_data`, `altr_sdram_mc_err_handler()`, `altr_sdr_mc_err_inject_write()`, `get_total_mem()`, `a10_init()`, `a10_unmask_irq()`, and `altr_sdram_probe()`. Generic EDAC-device support uses `struct edac_device_prv_data`, `altr_edac_device_handler()`, `altr_edac_device_trig()`, `altr_edac_device_probe()`, and `altr_create_edacdev_dbgfs()`. Arria10/Stratix10 support uses `altr_init_memory_port()`, `altr_init_a10_ecc_block()`, per-device setup tables, `altr_edac_a10_irq_handler()`, `altr_edac_a10_device_add()`, `a10_eccmgr_irqdomain_map()`, `s10_edac_dberr_handler()`, and `altr_edac_a10_probe()`.

## Control Flow
When SDRAM support is enabled, `altr_sdram_probe()` obtains the SDRAM syscon regmap, verifies ECC is already enabled, computes memory size from DT `memory` nodes, clears counts, registers an EDAC MC, requests SDRAM IRQs, enables ECC interrupts, and optionally exposes a debugfs injection trigger. The legacy ECC-manager parent `altr_edac_probe()` populates child platform devices for simple L2/OCRAM nodes. `altr_edac_device_probe()` maps each child register resource, runs the per-device dependency setup callback, requests SB/DB IRQs, registers an EDAC device, and creates debugfs injection hooks.

For Arria10/Stratix10, `altr_edac_a10_probe()` obtains the system-manager regmap, masks sensitive pending IRQs, creates a 64-entry IRQ domain, chains shared SBE/DBE parent IRQs, registers a Stratix10 panic notifier on 64-bit builds, reports sticky previous-boot UE state, and walks child nodes. Each matching child is registered through `altr_edac_a10_device_add()`, which maps the child resource, validates parent availability, runs device setup, requests logical IRQs, registers EDAC state, and links the device into the ECC-manager list. The chained handler reads system-manager SBE or DBE status and dispatches set bits through the IRQ domain.

## State and Persistence
Per-device state lives in `struct altr_sdram_mc_data`, `struct altr_edac_device_dev`, and the top-level `struct altr_arria10_edac`. Persistent hardware state includes ECC enable bits, pending interrupt status, sticky Stratix10 UE value/address registers, initialized ECC memory contents, and ECC-manager masks. EDAC core persists counters and sysfs/debugfs visibility. The driver also changes system state by refusing suspend for SDRAM EDAC and by panicking on selected uncorrectable errors.

## Dependencies and Integration Points
The driver depends on platform device-tree compatibles, syscon/regmap access to SDRAM and system-manager registers, IRQ domains, chained IRQ handlers, EDAC core APIs, debugfs when `CONFIG_EDAC_DEBUG` is enabled, genalloc SRAM pools for OCRAM injection, cache flush support for L2 injection, ARM SMCCC calls for Stratix10 secure register/ECC notification paths, and panic notifiers. Kconfig gates each peripheral block through `CONFIG_EDAC_ALTERA_*` symbols and related subsystem dependencies.

## Risks and Edge Cases
Many paths assume firmware or bootloader initialized memory and enabled ECC before Linux probes; enabling ECC after memory is live can cause immediate CE/UE events. Several UE paths call `panic()`, so false-positive DBE routing or stale status can be fatal. Debugfs injection intentionally corrupts ECC-protected data and must remain debug-only. The Arria10/Stratix10 path has architecture-specific IRQ parsing branches and a FIXME around compatibles for SDMMC. Resource cleanup uses devres groups and extra synthetic devices for SDMMC PortB, which are easy to regress. Sticky UE registers are cleared at probe after reporting previous-boot errors.

## Test Signals
Build matrix coverage should enable `EDAC_ALTERA` plus each `EDAC_ALTERA_*` option on suitable ARM/ARM64 SoCFPGA configs. Runtime tests need DT nodes for the SDRAM controller, ECC manager, and child ECC blocks; successful signals include EDAC MC/device registration, parent IRQ-domain dispatch, CE/UE counter increments, debugfs `altr_trigger` operation under `CONFIG_EDAC_DEBUG`, and correct previous-boot UE logging on Stratix10. Suspend attempts should fail with `-EPERM` when SDRAM EDAC is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/altera_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/altera_edac.h -->
# sources/distributed-fs/ceph-client/drivers/edac/altera_edac.h Research

## Purpose
This header is the register-map and private-data contract for `altera_edac.c`. It centralizes SDRAM, ECC-manager, OCRAM, L2, Arria10, Stratix10, and peripheral ECC offsets, bit masks, injection constants, and driver-private structures.

## Important APIs, Types, and Functions
The header defines register offsets and masks such as `CV_CTLCFG_ECC_EN`, `A10_ECCCTRL1_ECC_EN`, `ALTR_A10_ECC_*`, `A10_SYSMGR_ECC_INTMASK_*`, `ALTR_S10_ECC_*`, sticky S10 UE registers, and ECC block transaction registers. `struct altr_sdram_prv_data` describes SDRAM register layout and injection controls. `struct altr_sdram_mc_data` holds the SDRAM regmap, IRQs, and layout pointer. `struct edac_device_prv_data` describes per-device setup, clear masks, allocation hooks, injection hooks, and panic policy. `struct altr_edac_device_dev` is per-child EDAC device state. `struct altr_arria10_edac` is the top-level ECC-manager state with regmap, IRQ domain, IRQ chip, child list, and panic notifier.

## Control Flow
The header has no executable flow. Its data structures drive `altera_edac.c`: match tables select an `edac_device_prv_data` or `altr_sdram_prv_data`, probe code uses the offsets and masks to validate/enable ECC, IRQ handlers use clear/status masks, and debugfs injection uses allocation and file-operation callbacks.

## State and Persistence
No state is allocated in the header. It defines the shapes of runtime state allocated by the C file and the constants used to read or mutate persistent hardware ECC state in memory-controller and system-manager registers.

## Dependencies and Integration Points
It includes `linux/arm-smccc.h`, `linux/edac.h`, and `linux/types.h`, and forward-declares internal driver structures. It is tightly coupled to Intel/Altera SoCFPGA device-tree bindings and register manuals. The structures are not exported as a generic subsystem API; they are private to the Altera EDAC implementation.

## Risks and Edge Cases
Incorrect offsets or bit masks can cause missed interrupts, unwanted ECC disable/enable, or writes to unrelated system-manager fields. Some physical addresses are hardcoded for older SDRAM interface registers, so SoC-specific use must match the documented platform. Repeated generic field names for Cyclone5 and Arria10 variants make accidental table mixups possible.

## Test Signals
Compile tests catch structure and macro drift against `altera_edac.c`. Runtime validation requires reading known ECC registers on supported SoCFPGA hardware, confirming match-table data writes the intended bits, and exercising debug injection and IRQ clear paths for each enabled device type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/altera_edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.c Research

## Purpose
This is the AMD64/Hygon memory-controller EDAC driver. It discovers AMD northbridge/data-fabric memory controllers, reads DCT/UMC/GPU HBM topology registers, exposes EDAC memory-controller instances, decodes AMD MCE ECC events, maps reported addresses to chip-select/channel/page information, optionally controls hardware scrub rate, and exposes debug-only ECC injection on older supported families.

## Important APIs, Types, and Functions
Global state includes `pci_ctl`, `ecc_enable_override`, per-CPU `msrs`, per-node `ecc_stngs`, and `pci_ctl_dev`. Register-access helpers are `__amd64_read_pci_cfg_dword()`, `__amd64_write_pci_cfg_dword()`, `amd64_read_dct_pci_cfg()`, and SMN reads through AMD NB APIs. Hardware-data collection is organized through `struct low_ops` implementations `dct_ops`, `umc_ops`, and `gpu_ops`. Major helpers include scrub functions `set_scrub_rate()`/`get_scrub_rate()`, address translators `find_mc_by_sys_addr()`, `sys_addr_to_dram_addr()`, `dram_addr_to_input_addr()`, `f1x_translate_sysaddr_to_cs()`, `k8_map_sysaddr_to_csrow()`, and `f1x_map_sysaddr_to_csrow()`, syndrome decoding via `decode_syndrome()` and `get_channel_from_ecc_syndrome()`, and MCE decoders `decode_bus_error()` and `decode_umc_error()`.

Initialization and lifecycle are handled by `per_family_init()`, `probe_one_instance()`, `init_one_instance()`, `remove_one_instance()`, `setup_pci_device()`, `amd64_edac_init()`, and `amd64_edac_exit()`. Debug-only injection sysfs attributes are `inject_section`, `inject_word`, `inject_ecc_vector`, `inject_read`, and `inject_write`.

## Control Flow
Module init first refuses to bind if GHES firmware-first devices exist, if another EDAC owner is active, if the CPU family is unsupported, or if AMD northbridge enumeration is absent. It initializes EDAC opstate, allocates per-node ECC settings and MSR buffers, then probes each AMD NB node. Per-node probe selects DCT/UMC/GPU ops based on CPU family/model, reads hardware registers, skips nodes with no enabled chip selects, verifies ECC enablement or optionally attempts legacy force-enable through `ecc_enable_override`, allocates an EDAC MC with chip-select/channel layers, registers it, and dumps debug register state.

For pre-family-17h systems, MCE registration uses `decode_bus_error()`: it filters observed/non-ECC events, extracts an error address, maps system address to node/channel/csrow through DCT rules, decodes chipkill syndrome when needed, and calls `edac_mc_handle_error()`. For family 17h and newer systems, `decode_umc_error()` handles UMC-style MCA banks, fixes up GPU node IDs, extracts channel/csrow from MCA IPID/SYND fields, converts normalized UMC MCA address to system address using `amd_convert_umc_mca_addr_to_sys_addr()`, and reports EDAC errors. Exit unregisters the decoder, removes all MC instances, restores legacy ECC reporting state, releases generic PCI EDAC state, and frees allocations.

## State and Persistence
Per-node `struct amd64_pvt` stores family/model, PCI functions, register snapshots, chip-select bases/masks, DRAM ranges, UMC data, ECC symbol size, controller name, and debug injection parameters. `struct ecc_settings` records original NBCTL and ECC/MCE-enable state so forced legacy changes can be restored. Hardware state includes PCI config registers, SMN UMC registers, MSRs, scrub-control registers, and MCE banks. EDAC core persists MC devices, DIMM metadata, counters, and optional debug/sysfs attributes.

## Dependencies and Integration Points
The driver depends on AMD NB and node topology APIs, x86 MCE infrastructure, AMD SMCA/MCA helpers from `mce_amd.h`, `amd_register_ecc_decoder()`, AMD ATL address conversion, PCI config space, MSR helpers, EDAC MC/PCI APIs, RAS/GHES ownership checks, and x86 CPU matching. It integrates with Kconfig through `EDAC_AMD64`, `EDAC_DECODE_MCE`, `AMD_NB`, `AMD_NODE`, and optional `CONFIG_EDAC_DEBUG`.

## Risks and Edge Cases
Address decoding is highly family/model-specific and includes special handling for K8, F10h, F15h model 30h/60h, F16h, Zen UMC generations, MI200/MI300 GPU or APU HBM nodes, DRAM holes, node/channel interleaving, swapped interleaved regions, online spare rows, and normalized-address conversion. A register-layout mistake can misattribute a hardware error to the wrong DIMM. `ecc_enable_override` can mutate legacy ECC reporting state and is intentionally blocked for newer families. Debug injection disables CPU caches briefly and writes NB injection registers, so it is available only for older families and only under `CONFIG_EDAC_DEBUG`. GHES ownership blocks native binding to avoid races with firmware-first reporting.

## Test Signals
Build on supported x86 configs with AMD/Hygon CPU matching. Runtime smoke signals are successful EDAC MC registration per AMD NB node, correct DIMM sizes/types in sysfs, MCE decoder registration, and no binding when GHES owns EDAC. Hardware or firmware injection should validate CE, UE, and deferred event reporting; older debug builds can use injection sysfs. Regression tests should include family/model coverage for DCT, UMC, DDR5 register v2, and GPU HBM paths, plus unload/reload to ensure ECC settings and decoder registration unwind correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.h -->
# sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.h Research

## Purpose
This header defines the private data model, register constants, and helper interfaces used by the AMD64 EDAC driver. It captures AMD DCT, UMC, chip-select, DRAM range, error injection, ECC settings, and per-family operation abstractions.

## Important APIs, Types, and Functions
Important constants include AMD PCI device IDs, DCT/DRAM range registers, chip-select base/mask offsets, North Bridge ECC capability bits, scrub and injection registers, UMC channel offsets, and UMC ECC capability bits. Core structures are `struct error_injection`, `struct reg_pair`, `struct dram_range`, `struct chip_select`, `struct amd64_umc`, `struct amd64_family_flags`, `struct amd64_pvt`, `struct err_info`, `struct ecc_settings`, and `struct low_ops`. Inline helpers include `get_umc_base()`, `get_dram_base()`, `get_dram_limit()`, `extract_syndrome()`, `dct_sel_interleave_addr()`, cache-disable/enable helpers for injection, `dram_intlv_en()`, `dhar_valid()`, and `dct_sel_baseaddr()`. It declares the PCI config access wrappers implemented in `amd64_edac.c`.

## Control Flow
The header itself has no runtime control flow. Its `low_ops` callback table defines how the C file dispatches family-specific behavior for sysaddr-to-csrow mapping, DBAM-to-chip-select sizing, hardware discovery, ECC enablement checks, MC attribute setup, register dumps, and MCE error-info extraction.

## State and Persistence
No state is allocated in the header. It defines the persistent per-node private state retained while each EDAC MC instance is registered. The fields mirror hardware registers and include mutable injection staging values and ECC restore bookkeeping.

## Dependencies and Integration Points
The header depends on Linux PCI, EDAC, bitfield, MSR, CPU-device, and AMD MCE headers. It is private to `amd64_edac.c` and integrates with `mce_amd.h`, AMD NB PCI enumeration, x86 topology, and EDAC MC structures.

## Risks and Edge Cases
The register constants encode many AMD family-specific layouts; incorrect reuse across family/model boundaries can corrupt decoding. `struct amd64_pvt` is large and central, so adding fields requires careful initialization and teardown. Inline helpers read PCI config in some cases, which means apparent pure calculations can fail or depend on hardware access.

## Test Signals
Compile coverage with `amd64_edac.c` is the first signal. Runtime validation should compare decoded DRAM ranges, chip-select sizes, UMC register snapshots, syndrome extraction, and injection attributes against hardware documentation on representative AMD families. Static review should focus on whether new family/model logic updates both this header and `per_family_init()` consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd64_edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd76x_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/amd76x_edac.c Research

## Purpose
This PCI driver reports ECC memory errors from legacy AMD 76x chipsets, specifically AMD761 and AMD762 front-end bridge devices. It polls chipset PCI config status bits, maps chip-select rows from chipset memory-base registers, and reports CE/UE events through the EDAC memory-controller framework.

## Important APIs, Types, and Functions
Register definitions cover `AMD76X_ECC_MODE_STATUS`, `AMD76X_DRAM_MODE_STATUS`, and `AMD76X_MEM_BASE_ADDR`. `struct amd76x_error_info` snapshots ECC mode/status. `amd76x_get_error_info()` reads and clears pending CE/UE bits. `amd76x_process_error_info()` maps status bits to EDAC corrected or uncorrected events. `amd76x_check()` is the polling callback. `amd76x_init_csrows()` initializes EDAC csrow/dimm metadata from memory base/mask registers. `amd76x_probe1()`, `amd76x_init_one()`, and `amd76x_remove_one()` manage PCI probe/remove. The PCI ID table matches AMD FE gate devices and maps them to AMD761/AMD762 controller names.

## Control Flow
Module init calls `opstate_init()` and registers the PCI driver. Probe reads ECC mode, allocates an EDAC MC with eight virtual chip-select rows and one channel, fills capability fields, initializes csrows from PCI config, clears stale ECC status, registers the MC, and optionally creates a generic EDAC PCI control object. EDAC polling invokes `amd76x_check()`, which snapshots the ECC mode/status register, clears CE/UE status bits by writing back individual bits, then reports uncorrectable and correctable errors using the csrow encoded in the status register. Remove releases generic PCI EDAC state, deletes the MC, and frees it.

## State and Persistence
Driver state is minimal: a global `amd76x_pci` generic PCI EDAC control pointer and the EDAC MC instance attached to the PCI device. Hardware status bits persist in PCI config space until cleared by `amd76x_get_error_info()`. EDAC core persists counters and csrow/dimm metadata.

## Dependencies and Integration Points
The driver depends on PCI, x86 32-bit Kconfig gating, EDAC MC APIs, EDAC PCI generic control support, and legacy AMD chipset PCI IDs. It exposes the module parameter `edac_op_state` for poll/NMI reporting state consistent with other EDAC drivers.

## Risks and Edge Cases
The driver assumes only one instance of this memory-controller type and hardcodes EDAC MC index 0. The chipset only provides row-level location, so reports lack detailed address/channel/syndrome information. It clears status before processing reports, and `amd76x_process_error_info()` trusts row values from hardware status; corrupt row fields could index invalid csrows. The driver is old 32-bit x86 chipset support, so build and runtime coverage is likely sparse.

## Test Signals
Build with `CONFIG_EDAC_AMD76X` on an x86_32 PCI config. Runtime signals are PCI probe on AMD761/AMD762 IDs, EDAC MC registration with populated csrows, polling callbacks, and CE/UE counters changing when chipset ECC status bits are injected or observed. Removal should release both the generic PCI control and MC cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/amd76x_edac.c -->
