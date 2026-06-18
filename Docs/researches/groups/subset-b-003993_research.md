# Research: subset-b-003993

Grouped research for nine IOMMU/SMMU source files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom-debug.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom-debug.c

## Purpose
Qualcomm debug support for the Arm SMMU driver. It adds TBU registration, TBU halt/resume control, hardware address-translation probing through ATOS/ECATS registers, enhanced fault diagnostics, and Qualcomm-specific TLB sync timeout logging. It is compiled behind `CONFIG_ARM_SMMU_QCOM_DEBUG`; otherwise the header exposes no-op stubs.

## Important APIs, Types, And Functions
`struct qcom_tbu` tracks each translation buffer unit with its device, SMMU DT node, stream-ID range, clock, interconnect path, MMIO base, halt spinlock, and nested `halt_count`. Global state is `tbu_list`, protected by `tbu_list_lock`, plus global `atos_lock` to serialize ATOS transactions. `qcom_tbu_probe()` parses `qcom,stream-id-range`, maps the TBU registers, gets optional clock/interconnect resources, and appends the TBU to the global list. `qcom_smmu_tlb_sync_debug()` reads secure Qualcomm implementation registers through SCM after a TLB sync timeout and rate-limits logging. `qcom_find_tbu()` resolves a fault SID to a TBU. `qcom_tbu_halt()`/`qcom_tbu_resume()` stop and restart TBU traffic, including stalled-fault cleanup. `qcom_tbu_trigger_atos()` performs the hardware translation attempt. `qcom_smmu_context_fault()` replaces the generic context fault path when the Qualcomm debug impl is selected.

## Control Flow
On TBU probe, DT links each TBU to a parent SMMU node and SID range. During a Qualcomm context fault, the handler reads `FSR`, `FSYNR0`, `FAR`, and `CBFRSYNRA`, reports the fault to the IOMMU core, and if the normal client path did not handle it, compares software page-table walk output with ATOS hardware translation. ATOS flow enables interconnect bandwidth and clocks, halts the TBU, temporarily disables context fault interrupt/reporting bits, clears pending faults, serializes through `atos_lock`, writes SID/IOVA/AXUSER/transaction trigger registers, polls for completion or PAR fault/timeout, restores context SCTLR, resumes the TBU, disables resources, and returns a physical address or zero.

## State And Persistence
The file keeps only runtime kernel state: the global TBU list, per-TBU halt count, locks, and hardware register state while operations run. There is no disk persistence. Correctness depends on always unwinding clocks/interconnect votes and restoring SMMU context control state after debug operations.

## Dependencies And Integration Points
It depends on `arm-smmu.h` register helpers and `arm_smmu_domain`, the Qualcomm wrapper in `arm-smmu-qcom.h`, SCM IO reads, interconnect bandwidth APIs, runtime clocks, DT phandles, and IOMMU fault reporting. `arm-smmu-qcom.c` installs `qcom_smmu_context_fault()` and `qcom_smmu_tlb_sync_debug()` through `struct arm_smmu_impl` when debug support is enabled.

## Risks
The debug path manipulates live fault state, SCTLR fault bits, TBU halt control, clocks, and interconnect votes from IRQ/threaded IRQ context. Bugs could deadlock the TBU, hide faults, leave context interrupts disabled, or return misleading physical translations. The `icc_set_bw()` error path returns an integer as `phys_addr_t`, so callers must treat nonzero carefully. Global `atos_lock` avoids concurrent ATOS register races but can serialize all debug translations. Probe has no remove path to unlink TBUs from `tbu_list`, so it assumes devm lifetime and platform-device lifetime are sufficient.

## Test Signals
Exercise `CONFIG_ARM_SMMU_QCOM_DEBUG` builds, DT TBU binding parsing, missing TBU behavior, TLB sync timeout logging, fault handling with and without registered TBUs, ATOS success/fault/timeout cases, nested halt/resume counting, and fault handler return values for `report_iommu_fault()` results `0`, `-EBUSY`, `-EAGAIN`, and `-ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.c

## Purpose
Qualcomm implementation layer for the generic Arm SMMU v1/v2 driver. It selects Qualcomm-specific `arm_smmu_impl` hooks, works around firmware and SoC quirks, programs implementation-defined ACTLR settings for selected clients, exposes private Adreno GPU callbacks, and registers the optional TBU debug platform driver.

## Important APIs, Types, And Functions
The core dispatch type is `struct qcom_smmu_match_data`, which points to a generic impl, an Adreno impl, client ACTLR match table, and optional debug register config. `qcom_smmu_impl_init()` matches DT or ACPI and wraps the generic `arm_smmu_device` into `struct qcom_smmu`. `qcom_smmu_tlb_sync()` overrides TLB sync polling and calls debug diagnostics on timeout. Adreno helpers include `qcom_adreno_smmu_get_fault_info()`, `qcom_adreno_smmu_set_stall()`, `qcom_adreno_smmu_set_ttbr0_cfg()`, PRR accessors, GPU SID detection, and context-bank allocation forcing the GPU to CB0. `qcom_smmu_cfg_probe()` trims bad context-bank counts, detects S2CR bypass write quirks, reserves a bypass context bank, and imports bootloader-programmed SMRs. `qcom_smmu_write_s2cr()` translates BYPASS/FAULT writes for affected firmware.

## Control Flow
During generic SMMU probe, `arm_smmu_impl_init()` calls into this file for Qualcomm-compatible nodes. `qcom_smmu_create()` defers until SCM is ready, reallocates the SMMU object to include Qualcomm fields, and installs the selected impl. Later, generic config probing calls the Qualcomm `cfg_probe`, context initialization calls Qualcomm ACTLR/GPU setup, S2CR writes flow through the quirk-aware writer, and TLB syncs use the Qualcomm poll wrapper. For Adreno SMMUs, GPU devices are identified by SID 0, receive context bank 0, may enable TTBR1 split page tables, and get an `adreno_smmu_priv` callback table allowing the GPU driver to inspect faults, toggle stall behavior, and switch TTBR0.

## State And Persistence
Persistent runtime state lives in `struct qcom_smmu`: match data, bypass quirk flag, reserved bypass CB index, and per-CB stall bitmap. Hardware state includes ACTLR, SCTLR, S2CR, CBAR, TTBR, PRR, and wait-for-safe settings. There is no disk persistence.

## Dependencies And Integration Points
This file integrates the generic `arm-smmu.c` implementation hooks, Qualcomm SCM (`qcom_scm_is_available()`, `qcom_scm_qsmmu500_wait_safe_toggle()`), Adreno private API (`linux/adreno-smmu-priv.h`), OF/ACPI matching, runtime PM, and optional debug helpers in `arm-smmu-qcom-debug.c`. It is selected by compatible strings such as `qcom,smmu-500`, SoC-specific SMMU-500 strings, and older `qcom,*-smmu-v2` entries.

## Risks
The bypass quirk deliberately rewrites S2CR semantics, so incorrect detection could either expose unintended bypass or fault valid devices. GPU split page-table handling requires precise ordering around TCR/TTBR writes. Stall toggling modifies SCTLR while the device may be active and relies on PM and `cb_lock`. ACTLR values are encoded in match data; incorrect client matching can cause performance or correctness issues. SCM unavailability defers probe, so boot ordering matters.

## Test Signals
Build with and without debug support and ACPI. Boot representative Qualcomm SoCs covering SMMUv2, SMMU-500, Adreno and non-Adreno nodes, bypass quirk detection, >128 SMR limiting, `sdm845` wait-safe reset, and ACTLR client programming. GPU tests should cover TTBR1 enablement, TTBR0 switching, stall toggling, PRR callbacks, and context fault threaded IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.h

## Purpose
Private Qualcomm header shared by the Qualcomm Arm SMMU implementation and debug files. It defines the Qualcomm wrapper state, debug register configuration metadata, match-data contract, and conditional debug entry points.

## Important APIs, Types, And Functions
`struct qcom_smmu` embeds `struct arm_smmu_device` as its first field so generic code can be converted with `container_of()`. Its fields store selected match data, the bypass quirk flag and bypass context bank, and the `stall_enabled` bitmap used by Adreno stall control. `enum qcom_smmu_impl_reg_offset` indexes implementation-defined debug registers for TBU power and sync progress. `struct qcom_smmu_config` holds the register-offset table. `struct qcom_smmu_match_data` binds SoC compatible entries to a normal impl, Adreno impl, optional client ACTLR table, and optional debug config. The header declares `qcom_smmu_context_fault()` and conditionally declares or stubs `qcom_smmu_tlb_sync_debug()` and `qcom_tbu_probe()`.

## Control Flow
`arm-smmu-qcom.c` allocates/wraps a generic SMMU as `struct qcom_smmu` and stores `qcom_smmu_match_data`. Debug code uses the config offsets only when present. The generic Arm SMMU driver reaches the Qualcomm implementation through `struct arm_smmu_impl`; this header is the type bridge for those hooks.

## State And Persistence
The header defines in-memory driver state only. It creates no storage and has no persistence. The embedded-struct layout is important because callers rely on safe conversion between `arm_smmu_device` and `qcom_smmu`.

## Dependencies And Integration Points
It depends on `arm-smmu.h` being included first for `struct arm_smmu_device`, `struct arm_smmu_impl`, and related declarations. It is consumed by both Qualcomm source files and indirectly by module init/exit registration paths.

## Risks
Any change to `struct qcom_smmu` embedding would break `container_of()` assumptions. `stall_enabled` is a 32-bit bitmap, so it assumes context-bank indices used for stall fit the bitmap. Stubbed debug functions return no diagnostics and `qcom_tbu_probe()` returns `-EINVAL` when debug is disabled; callers must keep that conditional behavior in mind.

## Test Signals
Compile both `CONFIG_ARM_SMMU_QCOM_DEBUG=y` and disabled variants. Check that all Qualcomm impl data initializers match the header shape and that debug-disabled builds still register the TBU platform driver path without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-qcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.c

## Purpose
Main Linux IOMMU driver for Arm SMMU v1/v2 and MMU-400/401/500 style implementations. It discovers hardware capabilities, registers an IOMMU device, translates firmware stream IDs into stream-map entries, allocates context banks and page tables for domains, implements map/unmap/iova-to-phys/fault handling, and provides runtime/system PM.

## Important APIs, Types, And Functions
The public IOMMU contract is `arm_smmu_ops` with identity and blocked domains, `domain_alloc_paging`, `probe_device`, `release_device`, `device_group`, `of_xlate`, reserved region handling, and default domain ops. Domain state is `struct arm_smmu_domain`, device state is `struct arm_smmu_device`, master routing state is `struct arm_smmu_master_cfg`, and stream entries are `arm_smmu_smr`/`arm_smmu_s2cr`. Key functions include TLB invalidation helpers, `arm_smmu_read_context_fault_info()`, `arm_smmu_context_fault()`, `arm_smmu_init_domain_context()`, `arm_smmu_write_context_bank()`, `arm_smmu_master_alloc_smes()`, `arm_smmu_attach_dev()`, map/unmap wrappers, hardware ATOS `arm_smmu_iova_to_phys_hard()`, `arm_smmu_device_cfg_probe()`, reset/probe/remove/shutdown, and PM callbacks.

## Control Flow
Platform probe parses DT or ACPI model data, maps registers, selects implementation hooks, collects IRQs and clocks, enables clocks, probes ID registers, requests global fault IRQs, installs firmware reserved memory region bypass SMRs, resets the SMMU, registers the IOMMU device, and enables runtime PM when appropriate. Device probe resolves an SMMU from `iommu_fwspec`, validates SID/mask bits, creates master config, allocates stream map entries, and links PM to the SMMU. Domain attach lazily allocates a context bank, selects stage and page-table format, allocates io-pgtable ops, writes context bank registers, requests the context fault IRQ, then routes the master's S2CR entries to the context bank. Map/unmap delegate to io-pgtable ops under runtime PM and synchronize TLBs through stage-specific flush ops.

## State And Persistence
All state is runtime kernel memory plus SMMU registers: context bank bitmaps, stream-map entries, context bank register caches, feature flags, IRQ indices, page-table ops, group pointers, and module parameters `force_stage` and `disable_bypass`. There is no disk persistence. Runtime PM resets hardware on resume, so software state must be sufficient to reprogram stream maps and context banks.

## Dependencies And Integration Points
It integrates with Linux IOMMU core, io-pgtable formats, OF/ACPI IORT firmware, PCI and fsl-mc grouping, reserved-memory regions, DMA-IOMMU MSI reservations, platform drivers, clocks, runtime PM, and vendor implementations through `struct arm_smmu_impl`. Qualcomm, Nvidia, Cavium, MMU-500, and generic implementations can override register access, reset, context init, S2CR writes, TLB sync, context faults, and default domain type.

## Risks
Stream-map overlap detection and reference counts must be exact or devices may share/overwrite translations. The `disable_bypass` default is security-sensitive. Domain initialization publishes `pgtbl_ops` only after IRQ/context setup; ordering mistakes would race map/unmap. Runtime PM wraps register access, but paths that ignore errors could touch suspended hardware. Fault handlers clear FSR and resume stalled transactions, so return-code handling from `report_iommu_fault()` matters. Hardware capability parsing and implementation quirks can alter page sizes, context counts, and bypass behavior.

## Test Signals
Boot tests on SMMUv1, SMMUv2, MMU-500, stream-indexing and stream-matching systems; DT and ACPI probing; forced stage module parameter; bypass disabled/enabled; RMR bypass installation; PCI alias SIDs; context fault and global fault injection; runtime suspend/resume with active domains; map/unmap stress with DMA API; iova-to-phys hard/soft fallback; vendor impl hook coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.h

## Purpose
Shared private header for the Arm SMMU v1/v2 driver family. It defines architectural register offsets, bitfields, constants, core data structures, io-pgtable register conversion helpers, MMIO access wrappers, implementation hook contracts, and exported helpers used by implementation-specific files.

## Important APIs, Types, And Functions
The header enumerates global, stream mapping, context bank, fault, TLB, ATS, TCR, TTBR, MAIR, CBAR/CBA2R, and SCTLR registers. Important structures include `arm_smmu_device`, `arm_smmu_domain`, `arm_smmu_cfg`, `arm_smmu_cb`, `arm_smmu_smr`, `arm_smmu_s2cr`, `arm_smmu_master_cfg`, `arm_smmu_impl`, and `arm_smmu_context_fault_info`. Helpers `arm_smmu_lpae_tcr()`, `arm_smmu_lpae_tcr2()`, and `arm_smmu_lpae_vtcr()` translate io-pgtable config into SMMU register values. `arm_smmu_readl/writel/readq/writeq()` route register accesses through implementation overrides when present. Macros define GR0, GR1, and context-bank page addressing.

## Control Flow
This header does not run control flow itself, but it shapes the core driver's flow. `arm-smmu.c` uses it to probe features, initialize context banks, program stream routing, issue TLB invalidations, and decode faults. Qualcomm and Nvidia implementation files use `arm_smmu_impl` hooks and exported prototypes to customize behavior without duplicating the generic driver.

## State And Persistence
It defines volatile runtime state only. `arm_smmu_device` persists for platform-device lifetime and contains feature bits, register base, context and stream maps, IRQs, clocks, and IOMMU registration state. `arm_smmu_domain` persists for IOMMU domain lifetime and contains selected stage, config, locks, and io-pgtable ops. No disk persistence exists.

## Dependencies And Integration Points
The header depends on kernel bitfield, device, I/O, clock, IOMMU, io-pgtable, IRQ, mutex, and spinlock APIs. It exposes prototypes for generic, Nvidia, and Qualcomm impl init/module hooks and shared functions such as `arm_smmu_write_context_bank()`, `arm_mmu500_reset()`, and context fault info helpers.

## Risks
Register definitions are architectural contracts; wrong masks or duplicate definitions can corrupt hardware programming. `arm_smmu_lpae_tcr()` handles TTBR1 quirks by shifting TCR fields and disabling TTBR0, so changes can break GPU split page tables. Implementation override paths mean every access helper must preserve semantics for both generic and vendor-mediated register spaces. Fixed maxima such as `ARM_SMMU_MAX_CBS` and 32-bit stall users in vendor code must remain compatible.

## Test Signals
Compile all `arm-smmu` variants, including vendor impls. Run sparse/build coverage for 32-bit and 64-bit, big endian, AArch32 short descriptor, and TTBR1 quirk configurations. Hardware tests should verify register programming through generic and overridden MMIO accessors, context-bank setup, fault decoding, and TLB operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/qcom_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/qcom_iommu.c

## Purpose
Legacy Qualcomm secure IOMMU driver, based on Arm SMMU concepts but managing Qualcomm MSM IOMMU v1/v2 devices with child context-bank devices. It registers its own IOMMU ops, initializes secure page-table memory through SCM when needed, programs stage-1 32-bit LPAE context banks, and handles faults, runtime PM, and DT `of_xlate` for ASIDs.

## Important APIs, Types, And Functions
`struct qcom_iommu_dev` owns the parent IOMMU, clocks, local base, secure ID, max ASID, and flexible array of context pointers. `struct qcom_iommu_ctx` represents one context bank with MMIO base, ASID, secure flags, and attached domain. `struct qcom_iommu_domain` wraps `iommu_domain` with io-pgtable ops, page-table lock, init mutex, IOMMU pointer, and fwspec. Key functions include `qcom_iommu_init_domain()`, domain alloc/free, attach/identity attach, map/unmap, TLB flush ops, fault handler, `qcom_iommu_sec_ptbl_init()`, context probe/remove, parent probe/remove, runtime PM callbacks, and `qcom_iommu_of_xlate()`.

## Control Flow
The initcall registers context and parent platform drivers. Parent probe determines max ASID from child nodes, allocates the parent object, gets clocks and secure ID, optionally allocates secure page-table memory via SCM, enables runtime PM, populates child context devices, registers sysfs and IOMMU core, and configures non-secure interrupt selection. Child probes map context-bank registers, request shared fault IRQs, detect secure contexts, clear stale FSR, compute ASID, and store the context pointer. Device `of_xlate` binds a client to one parent IOMMU and appends ASID IDs. Attach initializes the domain once, restores secure config for each ASID, programs non-secure context banks, and leaves secure context banks unprogrammed but associated. Map/unmap are serialized by `pgtbl_lock` and unmap forces runtime PM to keep TLB invalidations safe.

## State And Persistence
Runtime state includes parent context array, per-context `secure_init`/`secured_ctx`/domain fields, domain page-table ops and fwspec, clocks, secure page-table one-time allocation state, and hardware registers. There is no disk persistence. Secure page-table allocation uses a static `allocated` boolean, making it global and one-time for the kernel lifetime.

## Dependencies And Integration Points
It depends on `arm-smmu.h` register definitions, io-pgtable `ARM_32_LPAE_S1`, Qualcomm SCM calls (`qcom_scm_restore_sec_cfg`, secure page-table size/init), OF platform population, runtime PM, IOMMU core, clocks, device links, and DMA allocation for secure tables.

## Risks
ASID from DT must match context array bounds. Secure contexts cannot be programmed; mistakes can touch protected registers. Domain initialization publishes `pgtbl_ops` after programming contexts, so failure paths must clear `iommu`. Unmap/free paths use runtime PM because clients can unmap after power-off. The TLB invalidation loop writes every context in the fwspec; missing context pointers would crash. The static secure allocation assumes one global secure table setup.

## Test Signals
Boot MSM IOMMU v1/v2 DTs with non-secure and secure contexts; verify child population order; attach clients with one and multiple ASIDs; map/unmap and TLB sync under runtime suspend; fault IRQ reporting and resume; secure page-table SCM failures; parent remove; invalid/multiple-IOMMU `of_xlate` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/qcom_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.c

## Purpose
Generic DMA API to IOMMU API glue layer. It prepares IOMMU domains for DMA mappings, owns IOVA allocation, reserved-region handling, MSI doorbell remapping, optional deferred IOVA freeing through flush queues, coherent/noncoherent allocation helpers, scatterlist mapping, SWIOTLB bounce integration, and exported `dma_iova_*` batching APIs.

## Important APIs, Types, And Functions
`struct iommu_dma_cookie` stores the IOVA domain, MSI page list, flush queues, flush counters, timer, flush-queue domain pointer, and options. `struct iommu_dma_msi_cookie` supports MSI-only unmanaged domains. Public functions include `iommu_get_dma_cookie()`, `iommu_get_msi_cookie()`, put functions, `iommu_setup_dma_ops()`, `iommu_dma_get_resv_regions()`, map/unmap/sync/allocation helpers, `iommu_dma_sw_msi()`, and `dma_iova_try_alloc/link/sync/unlink/destroy()`. Internal paths include flush queue management, domain initialization, IOVA allocation/free, SWIOTLB bounce mapping, scatterlist finalization/invalidation, and MSI page caching.

## Control Flow
DMA setup creates a cookie and initializes the IOVA domain on first device use, reserving PCI windows, firmware reserved regions, MSI regions, and choosing deferred-flush options. Map of a physical buffer checks deferred attach, alignment, DMA mask, SWIOTLB need, cache maintenance, IOVA allocation, and `iommu_map()`. Unmap resolves physical address for cache/SWIOTLB cleanup, unmaps IOMMU entries, syncs or queues TLB flushing, and frees IOVA. Scatterlist mapping reversibly rewrites SG offsets/lengths to page-granule-aligned form, handles P2PDMA bus addresses, allocates one contiguous IOVA span, maps the SG through the IOMMU, then compacts DMA-visible output segments. Allocations either build noncontiguous page arrays with remap/vmap support or contiguous/atomic mappings. MSI setup maps physical doorbell pages to cached IOVAs and writes the IOVA into MSI descriptors.

## State And Persistence
All state is runtime kernel memory. Cookies persist for domain lifetime; IOVA rcaches persist inside `iova_domain`; flush queues hold pending IOVA/page freelists until a domain-wide flush completes; MSI page lists cache doorbell mappings; `iommu_deferred_attach_enabled` is a static key enabled in kdump kernels; `iommu_dma_forcedac` is set by early param `iommu.forcedac`.

## Dependencies And Integration Points
The file integrates IOMMU core, DMA map ops, IOVA allocator, io page freelists, ACPI IORT and OF reserved regions, PCI host windows and P2PDMA, SWIOTLB, scatterlists, vmalloc/remap, cache maintenance hooks, MSI descriptors, tracepoints, kdump behavior, and generic page-table support (`iommupt_from_domain()`).

## Risks
Alignment and size calculations are security-sensitive for untrusted devices and SWIOTLB padding. Deferred flush queues rely on memory barriers and flush counters; ordering mistakes can free pages before IOTLB invalidation completes. Scatterlist in-place rewriting must be perfectly reversible on errors. DMA mask and 32-bit PCI workaround behavior can expose firmware/device bugs. MSI cookie allocation is monotonic for MSI-only domains. The `dma_iova_*` APIs require callers to sync and unlink correctly.

## Test Signals
Stress map/unmap with strict and DMA_FQ domains, per-CPU and single flush queues, untrusted PCI and kmalloc bounce paths, noncoherent cache maintenance, highmem/remap allocations, SG lists with unaligned entries and P2PDMA bus addresses, MSI remapping, reserved regions, deferred attach in kdump, forced DAC early param, and `dma_iova_*` partial failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.h

## Purpose
Public internal header for IOMMU drivers using the generic DMA-IOMMU glue. It declares the DMA setup, cookie, reserved-region, flush-queue, MSI, and forced-DAC interfaces when `CONFIG_IOMMU_DMA` is enabled and provides harmless stubs otherwise.

## Important APIs, Types, And Functions
Enabled declarations include `iommu_setup_dma_ops()`, `iommu_get_dma_cookie()`, `iommu_put_dma_cookie()`, `iommu_put_msi_cookie()`, `iommu_dma_init_fq()`, `iommu_dma_get_resv_regions()`, `iommu_dma_sw_msi()`, and `extern bool iommu_dma_forcedac`. Disabled stubs make setup and reserved-region helpers no-ops, return `-EINVAL` for flush queue init, and return `-ENODEV` for cookie/MSI setup.

## Control Flow
Drivers such as `arm-smmu.c` and `exynos-iommu.c` include this header to add generic reserved regions and DMA setup support. The actual control flow lives in `dma-iommu.c`; this header gates link-time availability and keeps non-DMA-IOMMU builds compiling.

## State And Persistence
The header itself stores no state. The only declared state is `iommu_dma_forcedac`, defined in `dma-iommu.c` and initialized by the early kernel parameter.

## Dependencies And Integration Points
It depends on `linux/iommu.h` and is consumed by IOMMU drivers and DMA mapping code. Its stub behavior is part of the build contract for configurations without `CONFIG_IOMMU_DMA`.

## Risks
Callers must handle `-ENODEV`/`-EINVAL` from stubs correctly. Adding new DMA-IOMMU APIs requires matching enabled declarations and disabled stubs to avoid configuration-specific build failures.

## Test Signals
Compile with `CONFIG_IOMMU_DMA=y` and disabled. Exercise drivers that call reserved-region helpers and DMA setup in both configurations and verify no unresolved symbols or ignored stub errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/exynos-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/exynos-iommu.c

## Purpose
Samsung Exynos SYSMMU IOMMU driver. It manages one or more SYSMMU controllers per master device, implements Exynos-specific two-level 32-bit IOVA page tables, handles hardware version differences from v1 through v7, controls clocks/runtime PM, reports faults, and registers generic IOMMU domain operations.

## Important APIs, Types, And Functions
`struct sysmmu_drvdata` holds one controller's registers, clocks, active state, version, variant ops, master link, and domain list nodes. `struct exynos_iommu_owner` is per-master state with controller list, current domain, and RPM mutex. `struct exynos_iommu_domain` owns the level-1 table, level-2 free-entry counters, attached controller list, and locks. `struct sysmmu_variant` abstracts register offsets and fault decoding for v1, v5, v7, and v7 VM layouts. Key functions cover version detection, block/unblock, TLB invalidation, enable/disable, IRQ fault handling, platform probe, PM suspend/resume, page-table allocation/free, identity and translated attach, map/unmap, iova-to-phys, device probe/release, OF xlate, and `exynos_iommu_init()`.

## Control Flow
Core init creates an aligned kmem cache and zero L2 table, then registers the SYSMMU platform driver if matching DT nodes exist. Controller probe maps registers, requests IRQ, gets clocks, detects hardware version and variant, initializes global page-entry shift/protection tables on first probe, sets DMA mask for v5+, chooses a DMA device for page-table cache syncs, enables runtime PM, and registers the IOMMU. OF xlate builds per-master owner state and links controllers. Attach first returns the old domain to identity, then assigns the new page-table physical address to each controller and enables active controllers. Map writes section, large page, or small page PTEs with cache sync; unmap clears entries, updates counters, and invalidates attached controllers. Fault IRQ decodes variant-specific status, reports to IOMMU core, panics if unrecovered, clears interrupt, and unblocks the SYSMMU.

## State And Persistence
Runtime state includes global `PG_ENT_SHIFT`, protection tables, `dma_dev`, `lv2table_kmem_cache`, `zero_lv2_table`, per-controller active/version/domain fields, per-owner controller lists, and per-domain page tables/counters. There is no disk persistence. Page tables are DMA-synced through the selected `dma_dev` because hardware walks them directly.

## Dependencies And Integration Points
It integrates with platform/OF probing, IOMMU core, DMA-IOMMU reserved regions, runtime PM and device links, clock framework, DMA mapping/cache sync, kmem caches, iommu-pages allocation, fault reporting, and generic device grouping. Client devices reference SYSMMU phandles through DT.

## Risks
Global `PG_ENT_SHIFT` assumes all controllers share address format. Page-table updates depend on `dma == phys` for the page table DMA mapping and use BUG_ON for violations. Faults panic if not handled by a client. Hardware v3.x FLPD cache workarounds require holes/alignment and explicit invalidation; missing them can cause false faults. Attach/detach and PM use multiple locks across owner/domain/controller state. Lack of driver remove cleanup for global caches is normal for core init but matters for test isolation.

## Test Signals
Boot Exynos platforms with v1/v3/v5/v7 SYSMMUs, one and multiple controllers per master, runtime suspend/resume while attached, identity attach/detach, 1 MiB/64 KiB/4 KiB map/unmap, FLPD cache workaround paths, fault injection and client fault handlers, DMA mask setup, page-table cache sync validation, and CONFIG_EXYNOS_IOMMU_DEBUG logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/exynos-iommu.c -->
