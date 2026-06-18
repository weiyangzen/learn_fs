# Research: subset-b-003990

Grouped research report for the source files assigned to `subset-b-003990`. Each section preserves the source path in its title and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/x1e80100.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/x1e80100.c

## Purpose

This file is the Qualcomm X1E80100 RPMh Network-on-Chip interconnect provider description. It contains the static topology, bandwidth clock manager groupings, device-tree compatible bindings, and platform driver registration needed by the common Qualcomm RPMh interconnect driver. It does not implement new bandwidth algorithms; instead it supplies `struct qcom_icc_node`, `struct qcom_icc_bcm`, and `struct qcom_icc_desc` data to `qcom_icc_rpmh_probe()` from the shared Qualcomm interconnect stack.

## Important APIs, Types, And Data

The central type is `struct qcom_icc_node`, one instance per NoC endpoint or bridge. Each node records `.name`, `.channels`, `.buswidth`, `.num_links`, and `.link_nodes`; the link pointers form the provider-local graph walked by the interconnect core when clients vote for paths. The file defines masters for QSPI, QUP, SDCC, UFS, crypto, debug, GPU, LPASS, multimedia, NSP, PCIe, USB, system fabric, LLCC, and memory-controller paths, plus slave/configuration nodes for CNOC, SNOC, GEM_NOC, MMSS, LPASS, PCIe, USB, and EBI.

`struct qcom_icc_bcm` instances group nodes that share an RPMh bandwidth clock manager vote. Notable BCMs include `bcm_cn0` and `bcm_mc0` with `.keepalive = true`, QUP BCMs with `.vote_scale = 1`, memory/media BCMs such as `bcm_mm0`/`bcm_mm1`, and fabric BCMs such as `bcm_sh0`, `bcm_sh1`, `bcm_sn0`, `bcm_sn2`, `bcm_sn3`, and `bcm_sn4`. `struct qcom_icc_desc` instances bind node arrays and BCM arrays for individual providers such as `x1e80100_aggre1_noc`, `x1e80100_gem_noc`, `x1e80100_mmss_noc`, `x1e80100_mc_virt`, `x1e80100_pcie_*_anoc`, and `x1e80100_usb_*_anoc`.

## Control Flow

There is no runtime control flow beyond module registration. `qnoc_driver_init()` registers a `platform_driver` at `core_initcall()` time. Matching is driven by `qnoc_of_match[]`, where each `qcom,x1e80100-...` compatible points to the corresponding `qcom_icc_desc`. On probe, the shared `qcom_icc_rpmh_probe()` consumes that descriptor, creates interconnect providers/nodes, registers BCM voters, and wires votes into RPMh. Removal is delegated to `qcom_icc_rpmh_remove()`, and `.sync_state = icc_sync_state` lets the interconnect core synchronize initial provider state after consumers have probed.

## State And Persistence

The file's state is static kernel data. Runtime mutable state, aggregation, RPMh transactions, and provider registration state live in the common Qualcomm interconnect code. Persistent external identity is the DT ABI: compatible strings in `qnoc_of_match[]` and numeric master/slave indexes from `dt-bindings/interconnect/qcom,x1e80100-rpmh.h`. Changing array indexes, node names used for diagnostics, BCM membership, keepalive flags, or link relationships can change bandwidth voting behavior for every DT consumer.

## Dependencies And Integration Points

The file depends on Linux interconnect provider APIs, OF platform matching, `icc_sync_state`, Qualcomm RPMh BCM voter code, and the generated/maintained X1E80100 DT binding constants. It integrates with device tree providers named for specific NoCs, client drivers that call `icc_get()`/`icc_set_bw()`, and RPMh hardware resources. The file is also coupled to `drivers/interconnect/qcom/icc-rpmh.c`, `bcm-voter.h`, and `icc-common.h` for descriptor interpretation.

## Risks

The main risks are data-table correctness risks: missing links break paths, wrong bus widths or channels skew votes, wrong BCM grouping can under-vote or over-vote clocks, and mismatched DT IDs can bind clients to the wrong fabric endpoint. Empty BCM arrays for some intermediate providers are intentional in this topology, but they increase reliance on adjacent providers and links being correct. Keepalive BCMs are power-sensitive: removing them may cause early boot or always-on fabric failures; adding them may waste power. Because probe is generic, most failures surface as path lookup errors, device performance issues, or power-management regressions rather than obvious compile failures.

## Test Signals

Compile coverage requires the Qualcomm interconnect driver and the DT binding header. Runtime signals include successful platform probe for every X1E80100 NoC compatible, absence of `icc` lookup failures from consumers, stable boot with storage/USB/PCIe/display/media devices active, and trace/debugfs evidence that votes reach RPMh. Device-tree binding checks should verify compatible names and interconnect cell IDs. Stress tests should exercise high-bandwidth clients such as UFS, PCIe, USB4, GPU/display/media, and memory traffic while checking for throttling, stalls, or unexpected power collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/qcom/x1e80100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Kconfig

## Purpose

This Kconfig fragment exposes Samsung interconnect support and the generic Exynos interconnect provider. `INTERCONNECT_SAMSUNG` is the umbrella boolean for Samsung SoC interconnect drivers and is available on `ARCH_EXYNOS` or `COMPILE_TEST`. `INTERCONNECT_EXYNOS` is the tristate for the generic Exynos provider and defaults to `y` when building for Exynos.

## Important Symbols And Dependencies

`INTERCONNECT_SAMSUNG` gates the submenu-level family support. `INTERCONNECT_EXYNOS` depends on that umbrella option and controls compilation of `exynos-interconnect.o` in the local Makefile. The help text identifies supported Exynos generations such as Exynos3250, Exynos4210, Exynos4412, Exynos542x, and Exynos5433.

## Control Flow And Integration

Kconfig choice affects build inclusion only. When `INTERCONNECT_EXYNOS=y` or `m`, the Makefile builds the platform driver in `exynos.c`. The symbol also participates in distribution and randconfig coverage through `COMPILE_TEST`.

## State, Risks, And Test Signals

There is no runtime state in this file. The main risk is dependency drift: if `INTERCONNECT_EXYNOS` is enabled without required interconnect, PM QoS, OF, or platform bus support, build failures appear elsewhere; if dependency constraints are too strict, compile coverage drops. Test signals are `olddefconfig`/`randconfig` success, correct module/builtin selection for Exynos builds, and successful probe of the generic Exynos interconnect platform device when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Makefile

## Purpose

This Makefile maps the Exynos interconnect Kconfig symbol to the actual object composition. `exynos-interconnect-objs := exynos.o` creates a composite object from the provider implementation, and `obj-$(CONFIG_INTERCONNECT_EXYNOS) += exynos-interconnect.o` includes it when the symbol is built in or as a module.

## Integration And Control Flow

The file participates only in kbuild. Kconfig determines whether the composite object is omitted, built into vmlinux, or emitted as a module. Its object name determines module naming and must stay in sync with `MODULE_ALIAS("platform:exynos-generic-icc")` in `exynos.c`.

## State, Risks, And Test Signals

There is no runtime state. Risks are limited but direct: a symbol mismatch would silently omit the driver, while object-name churn can affect module packaging and autoload expectations. Test signals are successful `make drivers/interconnect/samsung/` builds across builtin and module configurations and the presence of the expected `exynos-interconnect` module when `CONFIG_INTERCONNECT_EXYNOS=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/exynos.c -->
# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/exynos.c

## Purpose

This file implements a generic Exynos interconnect provider used by Exynos bus/devfreq devices. It presents each bus device as a single interconnect node and translates interconnect bandwidth requests into `DEV_PM_QOS_MIN_FREQUENCY` constraints on the parent bus device. The driver is intentionally small: it relies on the interconnect core for aggregation and on PM QoS/devfreq for frequency enforcement.

## Important APIs, Types, And Functions

`struct exynos_icc_priv` stores the platform device pointer, embedded `struct icc_provider`, the single `struct icc_node`, a `dev_pm_qos_request`, and the `bus_clk_ratio` used to translate bandwidth to frequency. `exynos_icc_get_parent()` reads the optional `interconnects` phandle from the bus node and resolves it through `of_icc_get_from_provider()`. `exynos_generic_icc_set()` is the provider `.set` callback; it computes source and destination minimum frequencies from `max(avg_bw, peak_bw) / bus_clk_ratio` and updates PM QoS for both endpoint devices. `exynos_generic_icc_xlate()` returns the provider's single node only when the phandle target matches the parent bus device OF node.

`exynos_generic_icc_probe()` allocates state, configures provider callbacks (`set`, `aggregate = icc_std_aggregate`, `xlate`, `inter_set = true`), creates one `icc_node` named from the parent OF node, reads optional `samsung,data-clock-ratio`, adds a PM QoS request to the parent bus device, links to an optional parent interconnect node, and registers the provider. `exynos_generic_icc_remove()` deregisters the provider and removes nodes.

## Control Flow

The module platform driver binds to platform devices named `exynos-generic-icc`. Probe works bottom-up from the parent bus device: create provider state, register a node, install PM QoS, link to parent if present, then register with the interconnect core. Bandwidth requests flow from client drivers through the interconnect framework, which aggregates requests and calls `.set`; the driver then updates source and destination PM QoS constraints. Error paths unwind the PM QoS request and node registration.

## State And Persistence

Runtime state is per platform device and devm-managed except for interconnect node and PM QoS request cleanup. The bus clock ratio is effectively persistent DT policy, defaulting to `EXYNOS_ICC_DEFAULT_BUS_CLK_RATIO` when unspecified. No on-disk state exists. The externally persistent interface is device tree: parent/child `interconnects` links and `samsung,data-clock-ratio` determine path shape and frequency scaling.

## Dependencies And Integration Points

The driver depends on the interconnect provider core, OF phandle parsing, PM QoS, platform devices, and devfreq-capable bus parents. It integrates with Exynos bus nodes created elsewhere, with clients that request interconnect bandwidth, and with `icc_sync_state` for late provider synchronization. The node ID is `pdev->id`, so platform-device ID allocation must be stable and unique for each provider instance.

## Risks

Frequency conversion is approximate and sensitive to `bus_clk_ratio`; an incorrect ratio can underclock or overclock buses. `exynos_generic_icc_set()` updates source PM QoS first and destination second; if the destination update fails after source succeeds, the source constraint remains changed. Parent links are optional, so missing DT links can reduce path coverage without failing probe. `xlate()` strictly matches `spec->np` against the parent OF node, making DT provider placement important. Remove unregisters provider/nodes but relies on PM QoS devm/device lifetime to avoid stale constraints.

## Test Signals

Useful tests include Exynos boot with the driver builtin and modular, DT validation for `interconnects` and `samsung,data-clock-ratio`, interconnect client bandwidth changes reflected in PM QoS/devfreq frequency requests, parent-child path creation across multi-bus topologies, and fault injection for PM QoS update failures. `COMPILE_TEST` builds catch API drift in interconnect and PM QoS usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/samsung/exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/trace.h -->
# sources/distributed-fs/ceph-client/drivers/interconnect/trace.h

## Purpose

This header defines tracepoints for interconnect bandwidth setting. It is included by the interconnect core trace compilation unit and uses Linux trace event macros to expose path, device, node, bandwidth request, aggregate bandwidth, and return-code information to ftrace/perf tooling.

## Important APIs And Events

`TRACE_SYSTEM` is `interconnect`. `TRACE_EVENT(icc_set_bw)` records a single node update in a path with `struct icc_path *p`, `struct icc_node *n`, request index `i`, and requested `avg_bw`/`peak_bw`. Its payload stores `path_name`, requesting device name from `p->reqs[i].dev`, node name, requested average/peak bandwidth, and aggregate node average/peak bandwidth. `TRACE_EVENT(icc_set_bw_end)` records path-level completion with path name, first request device, and return code.

`TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` align with the local include pattern used by the C file that instantiates trace definitions through `<trace/define_trace.h>`.

## Control Flow And Integration

The header itself has no executable flow. When the interconnect core calls the generated tracepoint hooks, enabled trace consumers receive formatted entries. The header depends on `struct icc_path` internals, especially `p->name` and `p->reqs[]`, and on `struct icc_node` bandwidth aggregate fields.

## State, Risks, And Test Signals

Tracepoints persist as ABI-like observability interfaces: changing field names or print formats can break user scripts. `icc_set_bw_end` assumes `p->reqs[0].dev` is valid; call sites must only trace initialized paths. `icc_set_bw` depends on index `i` matching an existing request. Test signals include successful trace header compilation, `tracefs` event presence under `events/interconnect/`, enabling events while running interconnect clients, and entries showing expected path/device/node names and return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/Kconfig

## Purpose

This Kconfig file is the main configuration surface for the Linux IOMMU subsystem. It defines generic IOMMU support, page-table format options, debugfs and debug-pagealloc options, default domain policy, common DMA/SVA/IOPF support, and a broad set of architecture/vendor IOMMU drivers.

## Important Symbols And Dependencies

Core symbols include `IOMMU_IOVA`, `IOMMU_API`, `IOMMUFD_DRIVER`, and `IOMMU_SUPPORT`. Generic page-table support is selected through `IOMMU_IO_PGTABLE`, with concrete formats such as `IOMMU_IO_PGTABLE_LPAE`, `IOMMU_IO_PGTABLE_ARMV7S`, and `IOMMU_IO_PGTABLE_DART`; LPAE KUnit and ARMv7s selftests provide validation hooks. `IOMMU_DEBUGFS` depends on `DEBUG_FS`.

The default-domain `choice` selects strict translated DMA, lazy translated DMA, or passthrough, with architecture-specific defaults. `IOMMU_DMA` selects DMA helper dependencies and the IOVA allocator on ARM64, X86, and S390. `IOMMU_SVA` and `IOMMU_IOPF` provide shared virtual addressing and page-fault support selected by drivers such as AMD IOMMU.

The file sources vendor submenus for AMD, ARM, Intel, IOMMUFD, and RISC-V, then defines platform drivers such as IRQ remapping, OMAP, Rockchip, Sun50i, Tegra SMMU, Exynos, Renesas IPMMU, Apple DART, s390, MediaTek, Hyper-V, virtio-iommu, Unisoc, and debug-pagealloc.

## Control Flow And Integration

Kconfig controls compilation and selected capabilities. Many symbols are selected by platform drivers rather than directly by users, so dependency correctness determines whether the IOMMU core, DMA mapping layer, page-table allocators, debugfs support, IRQ remapping, and vendor drivers are built together. The final `source "drivers/iommu/generic_pt/Kconfig"` exposes generic page-table infrastructure outside the `IOMMU_SUPPORT` block.

## State, Risks, And Test Signals

There is no runtime state in this file, but its symbols shape boot-time DMA isolation and security posture. The default-domain choice has direct security/performance tradeoffs: lazy invalidation and passthrough can improve performance while reducing isolation. Dependency errors can create build failures, missing DMA ops, absent page-table formats, or runtime feature gaps. Test signals include broad `allyesconfig`, `allmodconfig`, `randconfig`, architecture defconfigs, KUnit page-table tests, boot tests for strict/lazy/passthrough defaults, and verification that selected drivers pull in required core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/Makefile

## Purpose

This Makefile maps IOMMU Kconfig symbols to built objects and subdirectories. It is the kbuild integration point for the generic IOMMU core, IOMMUFD, page-table formats, DMA helpers, debug facilities, IRQ remapping, and vendor/platform IOMMU drivers.

## Important Build Rules

Unconditional subdirectories include `arm/` and `iommufd/`. Vendor subdirectories are controlled by symbols such as `CONFIG_AMD_IOMMU`, `CONFIG_INTEL_IOMMU`, `CONFIG_RISCV_IOMMU`, and `CONFIG_GENERIC_PT`. Core objects are gated by `CONFIG_IOMMU_API` (`iommu.o`, `iommu-traces.o`, `iommu-sysfs.o`), `CONFIG_IOMMU_SUPPORT` (`iommu-pages.o`), `CONFIG_IOMMU_DEBUGFS`, `CONFIG_IOMMU_DMA`, page-table format symbols, and platform driver symbols.

## Control Flow And Integration

There is no runtime flow, but object ordering and symbol gating affect link composition. The Makefile must stay aligned with Kconfig symbols and file names; for example `CONFIG_AMD_IOMMU` descends into `amd/`, and `CONFIG_IRQ_REMAP` builds `irq_remapping.o`, which AMD code includes through shared headers.

## State, Risks, And Test Signals

State is limited to build inclusion. Risks are missing objects for selected Kconfig features, stale object names after source renames, and accidental omission of helper objects needed by builtin code. Test signals include `make drivers/iommu/`, architecture defconfigs, `allmodconfig`, module install packaging, and link checks for both builtin and modular driver combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/Kconfig

## Purpose

This fragment configures AMD IOMMU support and optional AMD-specific IOMMUFD and debugfs functionality. The main `AMD_IOMMU` symbol enables AMD-Vi DMA remapping, interrupt-remapping dependencies, PCI ATS/PRI/PASID support, SVA/IOPF, generic page-table infrastructure, and AMD-specific page-table formats.

## Important Symbols And Dependencies

`AMD_IOMMU` is a boolean depending on `X86_64`, `PCI`, `ACPI`, and `HAVE_CMPXCHG_DOUBLE`. It selects `SWIOTLB`, `PCI_MSI`, `PCI_ATS`, `PCI_PRI`, `PCI_PASID`, `IRQ_MSI_LIB`, `MMU_NOTIFIER`, `IOMMU_API`, `IOMMU_IOVA`, `IOMMU_SVA`, `IOMMU_IOPF`, `GENERIC_PT`, `IOMMU_PT`, `IOMMU_PT_AMDV1`, and `IOMMU_PT_X86_64`, plus `IOMMUFD_DRIVER` when `IOMMUFD` is enabled. `AMD_IOMMU_IOMMUFD` depends on both `IOMMUFD` and `AMD_IOMMU` and enables experimental vIOMMU/nested support. `AMD_IOMMU_DEBUGFS` depends on `AMD_IOMMU` and generic `IOMMU_DEBUGFS`.

## Control Flow, Risks, And Test Signals

Kconfig selection determines whether the AMD subdirectory is entered and whether optional nested/debugfs objects are built. The debugfs option is intentionally warning-heavy because it exposes low-level device internals. Risks include under-selecting required core features for PASID/PRI/SVA/IOPF paths, accidentally enabling experimental IOMMUFD features in production configs, and enabling debugfs on hardened systems. Test signals include x86_64 AMD defconfig builds, `CONFIG_AMD_IOMMU=y` boot with IVRS hardware, `CONFIG_AMD_IOMMU_IOMMUFD` compile coverage, and debugfs object inclusion only when both AMD and generic IOMMU debugfs are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/Makefile

## Purpose

This Makefile defines the AMD IOMMU object set. Core AMD IOMMU support always builds `iommu.o`, `init.o`, `quirks.o`, `ppr.o`, and `pasid.o` when the parent directory is selected. Optional IOMMUFD support adds `iommufd.o` and `nested.o`; optional debugfs support adds `debugfs.o`.

## Integration, Risks, And Test Signals

The object set mirrors the Kconfig feature split: initialization, runtime IOMMU ops, quirks, page request handling, PASID/SVA, nested/IOMMUFD, and debugfs inspection. Risks are object omissions that produce unresolved symbols or disabled features, especially because headers declare functions conditionally used across these files. Test signals include `CONFIG_AMD_IOMMU=y` builds with and without `CONFIG_AMD_IOMMU_IOMMUFD` and `CONFIG_AMD_IOMMU_DEBUGFS`, plus module/builtin link checks for IRQ remapping and PPR/PASID paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu.h

## Purpose

This header is the internal AMD IOMMU interface shared by AMD initialization, runtime domain operations, interrupt remapping, PPR/PASID/IOPF, debugfs, quirks, and nested/IOMMUFD code. It includes `amd_iommu_types.h`, declares exported internal state, and provides small helpers for feature checks, address encryption handling, device lookup, domain conversion, and DTE clearing.

## Important APIs And Helpers

Initialization and interrupt-remapping entry points include `amd_iommu_prepare()`, `amd_iommu_enable()`, `amd_iommu_disable()`, `amd_iommu_reenable()`, and `amd_iommu_enable_faulting()`. Interrupt/log handling is declared through `amd_iommu_int_thread*()` variants and log restart helpers. Domain APIs include identity-domain initialization, protection-domain allocation/free, SVA allocation, PASID attach/remove, GCR3 set/clear, page-response, IOPF device add/remove, PPR log allocation/enabling/polling/completion, cache flushes, and nested-domain allocation.

Helpers include `check_feature()` and `check_feature2()` over global EFR/EFR2 masks, `amd_iommu_v2_pgtbl_supported()`, `amd_iommu_gt_ppr_supported()`, SME-aware `iommu_virt_to_phys()`/`iommu_phys_to_virt()`, `get_pci_sbdf_id()`, post-probe `get_amd_iommu_from_dev()`, `get_amd_iommu_from_dev_data()`, `to_pdomain()`, and `amd_iommu_make_clear_dte()`. The DTE clear helper preserves IVRS-derived persistent DTE bits by consulting `amd_iommu_get_ivhd_dte_flags()`.

## State And Dependencies

The header exposes global configuration such as event/PPR log sizes, guest interrupt remapping mode, selected page-table mode, guest/host page-table levels, supported page-size bitmap, and HAT disable state. It depends on Linux IOMMU APIs, PCI types, AMD type definitions, generic page-table hardware info, IRQ remapping when configured, DMI quirks, and IOMMUFD user data for nested allocation.

## Risks And Test Signals

This file is a cross-module contract; signature drift can break multiple AMD objects. Feature helpers assume global EFR values have been initialized before use. Address helpers must preserve SME encryption-bit semantics or hardware receives wrong physical addresses. `amd_iommu_make_clear_dte()` must keep IVRS persistent flags or firmware-required pass-through/system-management bits may be lost during detach. Test signals include AMD IOMMU builds across debugfs, IRQ remap, IOMMUFD, SVA/IOPF, and DMI configurations; boot tests with SME/SNP; PASID/PPR attach tests; and DTE inspection after attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu_types.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu_types.h

## Purpose

This header defines the AMD IOMMU driver's register constants, feature bits, hardware table formats, global lists, state structures, and interrupt-remapping data types. It is the low-level data contract that lets `init.c`, runtime domain code, PASID/PPR handling, debugfs, IRQ remapping, and IOMMUFD nested code agree on AMD-Vi hardware layout.

## Important Constants And Macros

The file defines MMIO register offsets for device tables, command/event/PPR/GA logs, MSI data, interrupt capability extension registers, status, and performance counters. Feature masks cover EFR/EFR2 bits such as PPR, x2APIC, guest translation, GA/GAM, PASID max, SNP, SEV-TIO, GCR3 trap mode, SNP AVIC support, HT range ignore, and 2K interrupt remap support. Command, event, PPR, GA log, DTE, interrupt-table, page-mode, protection, capability, IVINFO, and timeout constants encode the hardware ABI.

Iteration macros traverse `amd_iommu_pci_seg_list`, `amd_iommu_list`, protection-domain device lists, and IVHD DTE flag lists. SBDF conversion macros convert between PCI segment/device identifiers and the packed form used by command-line and debugfs code.

## Important Structures

`struct protection_domain` embeds generic page-table domain variants, device lists, lock, domain ID, mode, dirty tracking flag, per-IOMMU xarray, SVA notifier, PASID attachment list, and vIOMMU list. `struct amd_iommu_pci_seg` stores per-PCI-segment device table, reverse lookup table, IRQ lookup table, old kdump device table copy, alias table, and unity mappings. `struct amd_iommu` stores per-hardware-IOMMU list membership, locks, PCI device pointers, MMIO ranges, ACPI flags, EFRs, device ID, PCI segment, exclusion range, command/event/PPR/GA buffers, IRQ names, interrupt state, command completion semaphore, sysfs/core `iommu_device`, resume register snapshots, performance counter limits, debugfs offsets, and IOPF queue.

Other key types include `struct gcr3_tbl_info`, `struct pdom_dev_data`, `struct pdom_iommu_info`, `struct amd_iommu_viommu`, `struct nested_domain`, `struct iommu_dev_data`, `struct dev_table_entry`, `struct iommu_cmd`, `struct ivhd_dte_flags`, `struct unity_map_entry`, `struct irq_remap_table`, 32-bit and 128-bit IRTE unions, `struct amd_ir_data`, and `struct amd_irte_ops`.

## State And Persistence

The persistent external contract is AMD IOMMU hardware and ACPI IVRS layout. Runtime state is stored in global lists and per-IOMMU/per-segment structures initialized once at boot and reused during suspend/resume and kdump paths. Some state mirrors firmware data, such as IVHD DTE flags, unity maps, IOAPIC/HPET/ACPI HID maps, and pre-enabled translation state.

## Dependencies, Risks, And Test Signals

The header depends on kernel bitfield helpers, IOMMU APIs, MMU notifiers, MSI/PCI/list/spinlock infrastructure, IOMMUFD uapi, generic page-table code, and IRQ remapping. Risks are high because bit positions and packed table formats directly program hardware; wrong masks can corrupt device table entries, command buffers, interrupt remapping, or log processing. Structure changes affect debugfs and runtime code. Test signals include AMD hardware boot, IVRS parsing, DMA remapping, PASID/PPR/IOPF, interrupt remapping in xAPIC/x2APIC/vAPIC modes, SNP/SEV-TIO feature gating, kdump reuse, suspend/resume, and debugfs dumps of DTE/IRTE state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/debugfs.c

## Purpose

This file exposes AMD IOMMU diagnostic state through debugfs when `CONFIG_AMD_IOMMU_DEBUGFS` is enabled. It provides per-IOMMU files for reading arbitrary MMIO and PCI capability registers and dumping command buffers, plus global files for selecting a device ID and dumping that device's DTE and interrupt-remapping table.

## Important APIs And Functions

`amd_iommu_debugfs_setup()` creates `debug/iommu/amd`, per-IOMMU directories named `iommuNN`, and files `mmio`, `capability`, `cmdbuf`, `devid`, `devtbl`, and `irqtbl`. `iommu_mmio_write()` validates and stores an MMIO offset in `iommu->dbg_mmio_offset`; `iommu_mmio_show()` reads a 64-bit register with `readq()`. `iommu_capability_write()` stores a PCI capability offset in `iommu->dbg_cap_offset`, and `iommu_capability_show()` reads a config dword at `cap_ptr + offset`.

`iommu_cmdbuf_show()` locks `iommu->lock`, reads command-buffer head/tail registers, and prints all `CMD_BUFFER_ENTRIES`. `devid_write()` parses `seg:bus:slot.func` or `bus:slot.func`, validates it against PCI segment tables and reverse lookup, and stores the packed SBDF in global `sbdf`; `devid_show()` reports the selected device. `dump_dte()` prints the selected device table entry. `dump_irte()` obtains the IRQ lookup table and DTE interrupt-table length, locks the remap table, and delegates to `dump_128_irte()` or `dump_32_irte()` based on guest interrupt mode. `iommu_irqtbl_show()` also checks global `irq_remapping_enabled`.

## Control Flow And State

The setup function runs after AMD IOMMU initialization. User interaction is two-step for device-specific files: write a device ID to `devid`, then read `devtbl` or `irqtbl`. Per-IOMMU MMIO/capability files similarly store the selected offset before readback. State is diagnostic-only but mutable: `sbdf` is a single global selector shared across readers, and per-IOMMU debug offsets are stored in `struct amd_iommu`.

## Dependencies And Integration Points

The file depends on generic IOMMU debugfs root `iommu_debugfs_dir`, AMD global IOMMU/PCI-segment lists, DTE accessors, IRQ remapping state, and IRTE type definitions. It integrates with debugfs seq-file show/store helpers and PCI config access.

## Risks

The primary risk is information exposure and unsafe low-level introspection, which is why Kconfig warns against production use. The global `sbdf` selector is not per-open and can race between concurrent users. MMIO reads are bounded by `mmio_phys_end` but still allow broad register inspection. Command-buffer and IRTE dumps can be stale relative to hardware activity. The IRTE dump trusts DTE length fields after validation against known 512/2K encodings.

## Test Signals

Test with `CONFIG_IOMMU_DEBUGFS=y` and `CONFIG_AMD_IOMMU_DEBUGFS=y`; verify directory creation after AMD IOMMU init, valid/invalid writes to `mmio`, `capability`, and `devid`, command-buffer dumps under load, DTE dumps for known PCI devices, and graceful messages when IRQ remapping is disabled or no valid device is selected. Concurrency testing should check that locks prevent torn command/IRTE dumps while acknowledging the global selector semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/init.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/amd/init.c

## Purpose

This file performs AMD IOMMU discovery, ACPI IVRS parsing, hardware setup, PCI integration, interrupt/log setup, command-line parsing, suspend/resume handling, SNP integration, and performance-counter access. It is the boot-time state machine for AMD-Vi and also exposes several runtime helpers used by IRQ remapping, PPR/PASID, performance counters, and SNP teardown.

## Important APIs, Types, And Globals

Local packed ACPI overlays `struct ivhd_header`, `struct ivhd_entry`, and `struct ivmd_header` parse IVRS hardware and memory-definition blocks. Global exported state includes `amd_iommu_evtlog_size`, `amd_iommu_pprlog_size`, `amd_iommu_dump`, `amd_iommu_irq_remap`, `amd_iommu_pgtable`, `amd_iommu_hpt_level`, `amd_iommu_gpt_level`, `amd_iommu_guest_ir`, `amd_iommu_efr`, `amd_iommu_efr2`, `amd_iommu_hatdis`, `amd_iommu_snp_en`, `amd_iommu_np_cache`, `amd_iommu_iotlb_sup`, `amdr_ivrs_remap_support`, `amd_iommu_force_isolation`, and `amd_iommu_pgsize_bitmap`. Global lists hold PCI segments, IOMMUs, and persistent IVHD DTE flags.

External entry points include `amd_iommu_detect()`, IRQ-remapping hooks `amd_iommu_prepare()`, `amd_iommu_enable()`, `amd_iommu_disable()`, `amd_iommu_reenable()`, `amd_iommu_enable_faulting()`, feature helpers `amd_iommu_pasid_supported()`, `get_amd_iommu()`, performance-counter accessors, and SNP exports `amd_iommu_snp_disable()` and `amd_iommu_sev_tio_supported()` when SEV support is enabled.

## Control Flow

Initialization is driven by `enum iommu_init_state` and `iommu_go_to_state()`. `amd_iommu_detect()` runs from x86 IOMMU detection, checks global disable conditions and SME compatibility, moves to `IOMMU_IVRS_DETECTED`, marks `iommu_detected`, and installs `amd_iommu_init()` as the x86 IOMMU initializer. `amd_iommu_init()` advances to `IOMMU_INITIALIZED` and sets up debugfs on success.

`state_next()` implements the boot sequence: detect IVRS, parse ACPI through `early_amd_iommu_init()`, early-enable hardware, register syscore and SNP support, allocate/remap event buffers, initialize PCI/core IOMMU devices through `amd_iommu_init_pci()`, enable interrupts through `amd_iommu_enable_interrupts()`, then mark initialized. Error handling frees DMA resources and either tears hardware down or leaves interrupt-remapping state flushed when IRQ remapping has already been enabled.

ACPI parsing happens in multiple passes. `get_highest_supported_ivhd_type()` chooses the most capable IVHD type. `find_last_devid_acpi()` and `find_last_devid_from_ivhd()` size per-segment tables. `init_iommu_all()` allocates `struct amd_iommu`, calls `init_iommu_one()`, computes global EFR masks, then runs `init_iommu_one_late()` to allocate command buffers and IRQ domains. `init_iommu_from_acpi()` parses device entries, aliases, special IOAPIC/HPET devices, ACPI HID mappings, persistent DTE flags, and reverse lookup entries. `init_memory_definitions()` records IVMD unity/exclusion mappings.

Hardware programming is split across helper phases. Early enable disables stale state, applies ACPI control flags, programs device table and command buffer, exclusion/CWWB range, GT/GA/XT/IRT cache controls, 2K interrupt remapping, enables the IOMMU, and flushes caches. PCI init obtains the PCI device, reads capability/EFR data, enables GT/PPR/IOPF, handles NP cache strict mode, stores RD890 resume state, applies errata, adds sysfs, registers `iommu_device`, initializes identity domain and DTE DMA blocking, then flushes caches. Interrupt setup chooses INTCAPXT x2APIC-style domains or MSI, requests threaded IRQs, and enables event/PPR/GA logging.

## State And Persistence

Most state is boot-persistent kernel memory: IOMMU list, PCI segment tables, DTEs, alias/rlookup/IRQ lookup tables, unity maps, event/command/PPR/GA buffers, sysfs/debugfs registration, command completion semaphores, and per-IOMMU feature flags. Kdump paths can remap and reuse prior kernel command/event/CWB buffers and device tables when translation was already enabled. Firmware-derived state from IVRS is persistent across initialization and restored into DTEs on later operations. Suspend disables IOMMUs before firmware interaction; resume reapplies RD890 quirks, reloads hardware, reenables event buffers and interrupts.

## Dependencies And Integration Points

The file integrates with ACPI IVRS, x86 IOMMU detection, PCI/MSI, x86 IRQ remapping, IOAPIC/HPET mappings, generic IOMMU core/sysfs, AMD runtime `iommu_ops`, PPR/PASID/IOPF code, generic page-table infrastructure, SME/SNP memory encryption APIs, KVM SEV/SNP RMP handling, GART fallback, debugfs setup, and kernel command-line `__setup()` hooks. Hardware integration is direct MMIO and PCI config programming.

## Risks

Risk is high because this file programs DMA isolation hardware early in boot. Incorrect IVRS parsing can size tables wrongly or route devices to the wrong IOMMU. DTE flag handling must preserve firmware-required pass-through/system-management bits. Kdump reuse paths must validate old tables and SME encryption bits or DMA faults and command timeouts can follow. SNP requires V1 page-table mode, enabled IOMMU, RMP initialization, and shared-buffer handling; partial failures can leave security-sensitive state. Interrupt setup must choose compatible MSI/INTCAPXT/GA/vAPIC modes. Error unwinds are complex and differ depending on IRQ-remapping state. Command-line overrides can mask firmware bugs but also mis-map IOAPIC/HPET/ACPI HID devices.

## Test Signals

Essential signals include x86 AMD boot with IVRS present, `amd_iommu=off`, `force_enable`, `pgtbl_v1`, `pgtbl_v2`, `irtcachedis`, page-size options, and IVRS IOAPIC/HPET/ACPI HID overrides; DMA remapping in strict/lazy/passthrough modes; IRQ remapping in xAPIC, x2APIC XT, GA legacy, and vAPIC modes; PPR/PASID/IOPF device attach; IOMMUFD nested builds; SNP host boot and `amd_iommu_snp_disable()`; kdump with pre-enabled translation; suspend/resume on RD890 and modern systems; debugfs/sysfs presence; event/PPR/GA log overflow restart; and performance-counter get/set bounds checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/amd/init.c -->
