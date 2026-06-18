# subset-b-003999 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iova.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iova.c

## Purpose
`iova.c` implements the kernel I/O virtual address allocator used by IOMMU DMA paths. It manages allocated and reserved PFN ranges in an `iova_domain` rbtree and provides a fast path with per-CPU magazine caches for recently freed power-of-two sized ranges. The module is generic IOMMU infrastructure rather than a hardware driver.

## Important APIs, Types, and Functions
Key exported APIs are `init_iova_domain()`, `alloc_iova()`, `find_iova()`, `__free_iova()`, `free_iova()`, `alloc_iova_fast()`, `free_iova_fast()`, `reserve_iova()`, `put_iova_domain()`, `iova_domain_init_rcaches()`, `iova_cache_get()`, and `iova_cache_put()`. The code depends on `struct iova_domain` and `struct iova` from `<linux/iova.h>`, with local cache types `struct iova_magazine`, `struct iova_cpu_rcache`, and `struct iova_rcache`.

`__alloc_and_insert_iova_range()` is the core allocator. It walks the rbtree from a cached node downward, computes a top-down gap below `limit_pfn`, applies natural alignment when requested, inserts the new range, and updates cached search nodes. `private_find_iova()`, `remove_iova()`, and `iova_insert_rbtree()` implement lookup, deletion, and insertion under `iova_rbtree_lock`. `iova_rcache_get()` and `iova_rcache_insert()` route fast allocations through size-classed magazines, while `iova_depot_work_func()` drains excess global cache entries asynchronously.

## Control Flow and State
Domain initialization creates an anchor node at `IOVA_ANCHOR`, initializes rbtree locks, start PFN, granule, 32-bit DMA PFN boundary, cached nodes, and allocation-size hints. Slow allocation allocates an `iova` object from the slab cache, searches for a gap, inserts the node, and returns the object. Fast allocation rounds small sizes up to powers of two, tries the per-CPU rcache, then falls back to `alloc_iova()`. Fast free tries to push the PFN into the rcache and falls back to rbtree removal if the cache is unsuitable or full.

Persistent runtime state is all in memory: the rbtree, cached rbtree cursors, `max32_alloc_size`, per-CPU loaded/previous magazines, global depot lists, delayed work items, CPU hotplug hlist node, and two slab caches. There is no disk persistence. CPU hotplug teardown calls `free_cpu_cached_iovas()` to return cached ranges to the rbtree allocator. `put_iova_domain()` drains rcaches and postorder-frees the rbtree.

## Dependencies and Integration Points
The file integrates with Linux rbtree, slab, percpu allocation, CPU hotplug (`CPUHP_IOMMU_IOVA_DEAD`), delayed work, spinlocks, and kmemleak. IOMMU DMA code relies on the exported allocator APIs to reserve and recycle IOVA ranges. It also depends on `iova_shift()` and the `iova_domain` layout from the public IOVA header.

## Risks and Test Signals
Primary risks are allocator off-by-one errors around `limit_pfn + 1`, incorrect 32-bit boundary handling, stale cached rbtree cursors after deletion, and concurrency bugs between per-CPU magazines, depot work, CPU hotplug, and domain teardown. The rcache deliberately only caches small power-of-two ranges; callers freeing mismatched sizes can cause fragmentation or reuse failures. Test signals include allocation/free stress with randomized ranges, 32-bit-limited devices, high CPU hotplug churn, delayed work cancellation during domain destruction, reserve overlap cases, and IOMMU DMA workloads that exercise both slow and fast paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iova.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/ipmmu-vmsa.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/ipmmu-vmsa.c

## Purpose
`ipmmu-vmsa.c` is the Renesas VMSA-compatible IPMMU driver. It registers an `iommu_ops` implementation, creates ARM LPAE stage-1 page tables, manages IPMMU contexts and micro-TLBs, handles faults, and supports SoC-specific register layouts for R-Car Gen2/Gen3/Gen4 and related RZ/G2 parts.

## Important APIs, Types, and Functions
Important types are `struct ipmmu_features`, `struct ipmmu_vmsa_device`, and `struct ipmmu_vmsa_domain`. Feature data describes context counts, uTLB count, register offsets, secure alias behavior, cache snooping, reserved contexts, and generation-specific control bits. The device tracks MMIO base, root/leaf relationship, context bitmap, active domain table, uTLB-to-context map, optional ARM DMA mapping, and embedded `iommu_device`. Domains track page-table configuration, `io_pgtable_ops`, context ID, associated MMU, and a mutex.

Core functions include `ipmmu_probe()`, `ipmmu_remove()`, `ipmmu_domain_alloc_paging()`, `ipmmu_attach_device()`, `ipmmu_iommu_identity_attach()`, `ipmmu_map()`, `ipmmu_unmap()`, `ipmmu_iova_to_phys()`, `ipmmu_domain_init_context()`, `ipmmu_domain_setup_context()`, `ipmmu_tlb_invalidate()`, `ipmmu_utlb_enable()`, `ipmmu_utlb_disable()`, and `ipmmu_irq()`.

## Control Flow and State
Probe allocates device state, maps registers, applies non-secure alias offsets when required, identifies whether the instance is a root IPMMU or leaf/cache IPMMU, requests the root IRQ, resets contexts, reserves context 0 on affected SoCs, and registers leaf-capable instances with the IOMMU core. Device tree `of_xlate` validates SoC allow/deny policy, records uTLB IDs in the fwspec, and attaches the device to the platform IPMMU.

On attach, the domain lazily initializes a context on the root IPMMU, creates `ARM_32_LPAE_S1` page-table ops with non-secure quirks, programs TTBR/TTBCR/MAIR/IMBUSCR/IMCTR, then enables each uTLB from the fwspec. Detaching to the identity domain disables the associated uTLBs but leaves context lifetime tied to domain free. Map and unmap delegate to io-pgtable; TLB operations flush the whole context. Resume resets the root and reprograms active contexts and micro-TLBs.

Runtime state is volatile hardware and kernel memory: context bitmap, `domains[]`, `utlb_ctx[]`, `mapping`, page-table ops, and saved domain references. No persistent storage is used.

## Dependencies and Integration Points
The driver integrates with platform devices, device tree, `iommu_device_register()`, io-pgtable `ARM_32_LPAE_S1`, generic device groups, ARM legacy `dma_iommu_mapping` when `CONFIG_ARM && !CONFIG_IOMMU_DMA`, PCI device checks, SoC matching, runtime register access, and IRQ fault reporting through `report_iommu_fault()`.

## Risks and Test Signals
Important risks include root discovery ordering, reserved context handling, uTLB sharing without reference counting, whole-context flush granularity, context lifetime while devices detach, SoC allowlist/denylist drift, secure/non-secure alias assumptions, and resume correctness. Test signals include probe deferral on leaf before root, multiple device attach to the same domain, fault interrupt reporting, suspend/resume with active uTLBs, Gen2 versus Gen3/Gen4 register offsets, denied SoCs/devices, and DMA map/unmap workloads validating TLB flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/ipmmu-vmsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.c

## Purpose
`irq_remapping.c` is x86 interrupt-remapping orchestration code. It parses boot parameters, selects an Intel, AMD, or Hyper-V IRQ remapping backend, enables/disables remapping, exposes capability checks, and adjusts crash/boot IRQ restoration behavior when interrupt remapping is active.

## Important APIs, Types, and Functions
Global exported state includes `irq_remapping_enabled`, `irq_remap_broken`, `disable_sourceid_checking`, `no_x2apic_optout`, `disable_irq_post`, and `enable_posted_msi`. The backend is `static struct irq_remap_ops *remap_ops`, defined by the internal header.

Important functions are `setup_nointremap()`, `setup_irqremap()`, `irq_remapping_prepare()`, `irq_remapping_enable()`, `irq_remapping_disable()`, `irq_remapping_reenable()`, `irq_remap_enable_fault_handling()`, `irq_remapping_cap()`, `set_irq_remapping_broken()`, and `panic_if_irq_remap()`.

## Control Flow and State
Early parameters `nointremap` and `intremap=` update static policy flags before normal init. `intremap=` supports enabling/disabling remapping, disabling source-ID checks, forcing x2APIC optout behavior, disabling posted interrupts, and enabling posted MSI when configured. During preparation, the code skips work if remapping is disabled, then tries Intel, AMD, and Hyper-V `prepare()` methods in order based on Kconfig. The selected backend remains in `remap_ops`.

Enable calls the selected backend `enable()` and, if `irq_remapping_enabled` becomes true, replaces `x86_apic_ops.restore` with a virtual-wire-A-oriented restore path for crash dump simplicity. Fault handling installs a CPU hotplug online callback and invokes backend faulting setup on the current CPU. State is entirely boot/runtime kernel memory.

## Dependencies and Integration Points
The file integrates with x86 APIC setup, early boot parameters, backend IOMMU drivers, CPU hotplug, HPET/APIC headers, MSI and irqdomain infrastructure, and exported capability checks consumed by other IRQ/MSI code.

## Risks and Test Signals
Risks include backend selection order surprises when multiple IOMMU drivers are present, boot parameter parsing with comma-separated options, global posted-interrupt disablement hiding backend capabilities, and crash-kernel restore behavior. Test signals include booting with `intremap=on/off/nosid/nopost/posted_msi`, Intel/AMD/Hyper-V remapping paths, CPU online fault-handler setup, capability queries with and without `disable_irq_post`, and panic paths that must fire only when remapping is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.h

## Purpose
`irq_remapping.h` is the private IOMMU-layer interface shared by x86 interrupt-remapping backends and the common orchestration code. It keeps backend hooks internal to the IOMMU implementation rather than exposing them as public kernel API.

## Important APIs, Types, and Functions
When `CONFIG_IRQ_REMAP` is enabled, the header declares global policy/status variables and `struct irq_remap_ops`. The ops structure contains a capability bitmask and callbacks for `prepare`, `enable`, `disable`, `reenable`, and `enable_faulting`. It declares backend instances `intel_irq_remap_ops`, `amd_iommu_irq_ops`, and `hyperv_irq_remap_ops`.

When `CONFIG_IRQ_REMAP` is disabled, it supplies constant macro fallbacks for `irq_remapping_enabled`, `irq_remap_broken`, and `disable_irq_post`, allowing code to compile away remapping checks.

## Control Flow and State
There is no executable control flow in the header. Its main state effect is compile-time: enabled builds share mutable global variables across backend/common files; disabled builds collapse state into constants.

## Dependencies and Integration Points
The header forward-declares IRQ/MSI-related types and is included by `irq_remapping.c` and backend implementations. It relies on Kconfig to select the real declarations. The capability bit positions are defined by the wider x86 IRQ remapping interfaces, while the ops objects are provided by Intel, AMD, and Hyper-V code.

## Risks and Test Signals
Risks are ABI-like drift between the common code and backend ops, misuse outside the intended IOMMU layer, and subtle differences between disabled-build constants and enabled-build globals. Test signals include building with `CONFIG_IRQ_REMAP=y/n`, each backend enabled independently, and verifying that capability and enable paths compile and link with all callback combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.c

## Purpose
`msm_iommu.c` is the Qualcomm/APQ8064-era MSM IOMMU driver. It registers an IOMMU provider, discovers context-bank masters from device tree, allocates ARM v7s page tables, programs MSM context banks and machine-ID routing, handles TLB invalidation, and logs context faults.

## Important APIs, Types, and Functions
The main private domain state is `struct msm_priv`, containing attached IOMMU list, `iommu_domain`, `io_pgtable_cfg`, `io_pgtable_ops`, owning device, and page-table spinlock. Hardware state is `struct msm_iommu_dev` from `msm_iommu.h`, with MMIO base, clocks, IRQ, context-bank bitmap, context list, and `iommu_device`. Masters are `struct msm_iommu_ctx_dev`, holding OF node, context-bank number, and MIDs.

Core functions include `msm_iommu_probe()`, `qcom_iommu_of_xlate()`, `insert_iommu_master()`, `msm_iommu_probe_device()`, `msm_iommu_attach_dev()`, `msm_iommu_identity_attach()`, `msm_iommu_domain_config()`, `msm_iommu_map()`, `msm_iommu_unmap()`, `msm_iommu_sync_map()`, `msm_iommu_iova_to_phys()`, `msm_iommu_fault_handler()`, `msm_iommu_reset()`, `config_mids()`, and `__program_context()`.

## Control Flow and State
Probe prepares clocks, maps MMIO, reads `qcom,ncb`, resets global and context registers, performs a PAR sanity check through context 0, requests the shared fault IRQ, adds the device to the global `qcom_iommu_devices` list, and registers the IOMMU. OF xlate finds the IOMMU provider by phandle and accumulates stream/MID IDs into the first master object for the consumer.

Attach initializes page-table ops for `ARM_V7S`, finds matching IOMMU devices, enables clocks, allocates context-bank numbers, configures MID-to-context routing, programs context registers with TTBR/TCR/PRRR/NMRR and fault controls, then records the IOMMU in the domain attachment list. Map/unmap call io-pgtable under `pgtlock`. TLB flushes iterate attached IOMMUs and their masters, enable clocks, issue context or range invalidations, and disable clocks. Identity attach frees page-table ops and resets contexts.

Runtime state is held in the global device list, context bitmaps, per-domain attachment lists, io-pgtable memory, master MID arrays, clocks, and hardware registers. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on the MSM register macro header, ARM v7s io-pgtable, platform device resources, clocks, device tree `of_xlate`, generic device groups, fault IRQs, and the IOMMU core. It exports `msm_iommu_fault_handler()` through the header for context interrupt hookup.

## Risks and Test Signals
Risks include global lock coverage over clocked hardware operations, limited cleanup in attach failure paths after partial context allocation, duplicate domain configuration on repeated attach, assumptions that a device maps to the first context-list entry, and fault handler returning `0` rather than `IRQ_HANDLED`. Test signals include multi-MID OF entries, duplicate stream IDs, attach/detach cycles, map/unmap with range invalidation, PAR-based `iova_to_phys()`, shared IRQ fault logging, clock enable failures, and `qcom,ncb` boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.h

## Purpose
`msm_iommu.h` defines shared Qualcomm MSM IOMMU data structures and constants used by the MSM driver and any interrupt/fault integration. It describes hardware instances, context-bank masters, mapping attributes, and the exported fault handler.

## Important APIs, Types, and Functions
Constants include shareability attributes (`MSM_IOMMU_ATTR_NON_SH`, `MSM_IOMMU_ATTR_SH`), cacheability attributes (`MSM_IOMMU_ATTR_NONCACHED`, write-back/write-through variants, `MSM_IOMMU_CP_MASK`), and sizing limits (`MAX_NUM_MIDS`, `IOMMU_MAX_CBS`).

`struct msm_iommu_dev` represents one hardware block: MMIO base, number of context banks, device pointer, IRQ, clocks, global/domain list nodes, context list, context allocation bitmap, and embedded `iommu_device`. `struct msm_iommu_ctx_dev` represents a context-bank master: OF node, context number, array of machine IDs, count, and list node. The header declares `irqreturn_t msm_iommu_fault_handler(int irq, void *dev_id)`.

## Control Flow and State
The header has no runtime control flow, but its structures define the state owned by `msm_iommu.c`: global registration, domain attachment, context-bank allocation, and MID routing. The `mids` array is bounded and filled from `#iommu-cells` arguments during OF translation.

## Dependencies and Integration Points
The header includes interrupt, IOMMU, and clock definitions. It is tightly coupled to the MSM driver and the hardware macro header. The structures are not a stable external ABI; they are internal kernel driver state.

## Risks and Test Signals
Risks include fixed-size MID and context-bank arrays, implicit assumption that context mappings are design-time/static, and shared structures modified under the driver's global spinlock. Test signals include compile coverage for the MSM driver, OF parsing with maximum MIDs, context-bank counts near `IOMMU_MAX_CBS`, and fault handler declaration consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu_hw-8xxx.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu_hw-8xxx.h

## Purpose
`msm_iommu_hw-8xxx.h` is the register-definition and bitfield access layer for Qualcomm 8xxx-generation MSM IOMMU hardware. It provides read/write helpers, field setters/getters, page-table descriptor constants, register offsets, masks, and shifts consumed by `msm_iommu.c`.

## Important APIs, Types, and Functions
The header is macro-only. Generic primitives are `GET_GLOBAL_REG`, `GET_CTX_REG`, `SET_GLOBAL_REG`, `SET_CTX_REG`, numbered register wrappers, `GET_FIELD`, and `SET_FIELD`. Higher-level macros cover global registers (`M2VCBR_N`, `CBACR_N`, `CR`, `ESR`, `IDR`, TLB test/invalidate registers), context registers (`SCTLR`, `ACTLR`, `CONTEXTIDR`, `TTBR0/1`, `TTBCR`, `PAR`, `FSR`, `FAR`, `FSYNR0/1`, `PRRR`, `NMRR`, TLB invalidation and V2P registers), and field-specific setters/getters such as `SET_M`, `SET_TRE`, `SET_CONTEXTIDR_ASID`, `GET_FSR`, `GET_FAULT`, and `SET_TLBIVA`.

It also defines page-table descriptor constants for first-level and second-level ARM v7 mappings, memory/cache policy values, `CTX_SHIFT`, and masks/shifts for every exposed field.

## Control Flow and State
The macros perform direct MMIO reads/writes and read-modify-write operations. State is entirely hardware register state at the supplied base address and context index. `SET_FIELD()` reads the current register, clears a shifted mask, and writes the updated value; callers must provide any required serialization.

## Dependencies and Integration Points
The header depends on Linux MMIO primitives `readl()` and `writel()`. It is integrated by `msm_iommu.c` for reset, context programming, MID routing, TLB invalidation, fault decoding, and PAR translation. The field layout must match the APQ8064/MSM 8xxx hardware manual.

## Risks and Test Signals
Risks include macro argument ordering mistakes, read-modify-write races if used without locking, typo-prone field names, inconsistent names such as `TLBLCKR`/`TLBLKCR`, and silent corruption if masks or shifts are wrong. Test signals include compile-time coverage of all macros used by the driver, boot-time context reset/programming, fault register decode sanity, TLB invalidation side effects, and hardware validation against known register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu_hw-8xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu.c

## Purpose
`mtk_iommu.c` is the modern MediaTek M4U/IOMMU driver for many MT27xx/MT67xx/MT81xx/MT83xx SoCs and MM/INFRA/APU variants. It registers the IOMMU provider, parses SMI larb topology, manages shared or per-bank page tables, supports multiple IOVA regions, programs hardware, handles faults, and restores hardware state across runtime PM.

## Important APIs, Types, and Functions
Platform feature data is encoded in `struct mtk_iommu_plat_data`, which describes SoC flags, register selection, hardware lists, IOVA regions, bank counts, enabled banks, bank port masks, and larb remapping. Runtime state is `struct mtk_iommu_data`, `struct mtk_iommu_bank_data`, and `struct mtk_iommu_domain`.

Core functions include `mtk_iommu_probe()`, `mtk_iommu_remove()`, `mtk_iommu_mm_dts_parse()`, `mtk_iommu_of_xlate()`, `mtk_iommu_probe_device()`, `mtk_iommu_release_device()`, `mtk_iommu_attach_device()`, `mtk_iommu_identity_attach()`, `mtk_iommu_domain_finalise()`, `mtk_iommu_map()`, `mtk_iommu_unmap()`, `mtk_iommu_iotlb_sync()`, `mtk_iommu_sync_map()`, `mtk_iommu_iova_to_phys()`, `mtk_iommu_get_resv_regions()`, `mtk_iommu_hw_init()`, `mtk_iommu_isr()`, and runtime suspend/resume callbacks.

## Control Flow and State
Probe allocates driver state, creates an aligned protect buffer for translation faults, detects 4GB mode when applicable, maps banked MMIO resources, initializes enabled bank descriptors and IRQ numbers, obtains clocks/regmaps, parses MM larbs and SMI common topology, registers with the IOMMU core, and optionally becomes a component master. Shared-page-table SoCs insert devices into global hardware lists so sibling IOMMUs can share a domain.

OF translation stores the IOMMU data pointer and fwspec IDs. Probe-device links MM clients to larb devices. Attach chooses an IOVA region and bank from fwspec IDs and platform masks, finalizes or reuses an ARM v7s io-pgtable with MediaTek quirks, programs bank TTBR and hardware registers on first use, optionally raises the DMA mask for >4G regions, and enables the relevant SMI or infra-master routing. Identity attach disables routing.

Map/unmap delegate to io-pgtable, with 4GB mode physical remap on map and reverse remap on `iova_to_phys()`. TLB range invalidation iterates all IOMMUs sharing the hardware list, skips inactive PM domains when allowed, polls `REG_MMU_CPE_DONE`, and falls back to full flush on timeout. Fault handling decodes IOVA/PA, larb/port, layer, and write/read direction, reports the fault, clears interrupts, and flushes all TLBs. Runtime suspend saves global and per-bank registers; resume restores them, rewrites TTBRs, and flushes TLBs.

## Dependencies and Integration Points
The driver integrates with the IOMMU core, io-pgtable `ARM_V7S`, MediaTek SMI larb components, device links, runtime PM, clocks, syscon/regmap, secure monitor calls for some infra masters, device tree bindings, PCI checks, and platform IRQs. The many `mtk_iommu_plat_data` instances are critical integration points for per-SoC behavior.

## Risks and Test Signals
Risks include feature-flag combinations, multi-region group assignment, shared page-table lifetime, bank selection, PM-aware TLB flushing that may skip inactive devices, IRQ request during first bank initialization, device-link cleanup, and 4GB/34-bit/35-bit address handling. Test signals include attach/map/unmap on every compatible, multi-larb devices, multi-region devices, infra/APU paths, runtime suspend/resume with existing mappings, TLB timeout fallback, fault injection with decoded larb/port, PCI infra configuration, and reserved-region reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu_v1.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu_v1.c

## Purpose
`mtk_iommu_v1.c` is the older MediaTek MT2701 M4U v1 IOMMU driver. Unlike the modern driver, it supports a single shared 4GB IOVA domain with 4K-only mappings and manually managed first-level page-table entries.

## Important APIs, Types, and Functions
Runtime state is `struct mtk_iommu_v1_data`, which stores MMIO base, IRQ, device, clock, protect buffer address, active domain, embedded `iommu_device`, legacy ARM DMA mapping, SMI larb data, and suspend registers. Domains are `struct mtk_iommu_v1_domain`, with a spinlock, `iommu_domain`, coherent page-table VA/PA, and owning data pointer.

Core functions include `mtk_iommu_v1_probe()`, `mtk_iommu_v1_remove()`, `mtk_iommu_v1_create_mapping()`, `mtk_iommu_v1_probe_device()`, `mtk_iommu_v1_probe_finalize()`, `mtk_iommu_v1_attach_device()`, `mtk_iommu_v1_identity_attach()`, `mtk_iommu_v1_domain_finalise()`, `mtk_iommu_v1_map()`, `mtk_iommu_v1_unmap()`, `mtk_iommu_v1_iova_to_phys()`, `mtk_iommu_v1_hw_init()`, `mtk_iommu_v1_isr()`, and suspend/resume callbacks.

## Control Flow and State
Probe allocates data, creates a DMA-capable protect buffer, maps registers, obtains IRQ and `bclk`, discovers larb devices, initializes hardware, registers the IOMMU, and becomes a component master. Device probing walks the consumer's `iommus` phandles itself, creates/updates the fwspec, creates a single legacy ARM DMA mapping if needed, validates all ports are in one larb, and adds a runtime-PM device link to that larb. Probe-finalize attaches the device to the ARM DMA mapping.

Attach only operates on the internally created domain. The first attach allocates a 4MB coherent page table, writes its physical address to `REG_MMU_PT_BASE_ADDR`, and stores the domain as `data->m4u_dom`; every attach enables SMI MMU bits for the relevant ports. Map writes one 32-bit descriptor per 4K page under `pgtlock`, flushes the mapped range, and returns `-EEXIST` if an existing PTE is encountered. Unmap zeroes PTEs and flushes. ISR reads fault status, IOVA, PA, and larb/port, reports a read fault, clears interrupts, and flushes all TLBs. Suspend saves selected registers; resume restores registers, TTBR, and protect address.

## Dependencies and Integration Points
The driver integrates with legacy ARM `dma_iommu_mapping`, the IOMMU core, SMI larb component framework, device links, platform resources, clocks, DT memory-port bindings, and generic device groups. It does not use `io_pgtable_ops`; page-table management is local.

## Risks and Test Signals
Risks include assuming one global domain, no write/read fault distinction, manual PTE management, possible NULL `m4u_dom` on resume if suspend occurs before attach, partial map behavior after encountering an existing PTE, and strict single-larb validation. Test signals include 4K map/unmap, duplicate map returning `-EEXIST`, fault injection, suspend/resume after attach, DMA mapping creation on ARM, device-link cleanup, and larb phandle probe deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/of_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/of_iommu.c

## Purpose
`of_iommu.c` provides device-tree helpers for the IOMMU core. It translates `iommus` and `iommu-map` properties into device fwspec data, invokes provider-specific `of_xlate()` callbacks, simulates device probing when needed, and provides reserved-region parsing from reserved-memory `iommu-addresses`.

## Important APIs, Types, and Functions
The primary exported functions are `of_iommu_configure()` and `of_iommu_get_resv_regions()`. Internal helpers include `of_iommu_xlate()`, `of_iommu_configure_dev_id()`, `of_iommu_configure_dev()`, `of_pci_iommu_init()`, `of_iommu_configure_device()`, `of_pci_check_device_ats()`, and `iommu_resv_region_get_type()`.

## Control Flow and State
`of_iommu_configure()` serializes against `iommu_probe_device_lock` so `dev->iommu` and fwspec state stay stable. It exits early if a fwspec already exists, records whether `dev->iommu` was initially present, and then configures PCI devices through DMA aliases and `iommu-map`, or non-PCI devices through repeated `iommus` phandles. On errors it frees the fwspec or device IOMMU state depending on whether the device had existing IOMMU state. If configuration succeeds outside the normal probe-device path, it invokes `iommu_probe_device()`.

Reserved-region parsing walks `memory-region` phandles, optionally parses a physical `reg`, then reads `iommu-addresses` tuples. Tuples matching the device node become `iommu_resv_region` entries. If the IOVA region exactly maps the physical region, it is direct; otherwise it is a reserved-only region. DMA-coherent devices get `IOMMU_CACHE` in the protection flags. No durable storage is used; all state is fwspec/device memory and list entries.

## Dependencies and Integration Points
The file integrates with OF core, OF address translation, OF PCI aliasing, fsl-mc headers, PCI ACS requests, module ownership for provider ops, the private IOMMU probe lock, fwspec allocation/free, and reserved-memory bindings.

## Risks and Test Signals
Risks include cleanup asymmetry between pre-existing and newly allocated `dev->iommu`, provider module lifetime around `of_xlate`, PCI alias handling, `iommu-map-mask` translation, reserved-memory tuples with missing or malformed `reg`, zero-length reservations, and non-direct physical-to-IOVA mapping warnings. Test signals include PCI and platform OF devices, EPROBE_DEFER propagation, repeated configure calls, ATS flag setting, reserved-memory direct and reserved cases, and disabled IOMMU provider nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/of_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c

## Purpose
`omap-iommu-debug.c` implements debugfs support for OMAP IOMMU devices. It exposes read-only files for register dumps, TLB entries, page-table contents, and TLB-entry count under a global `omap_iommu` debugfs directory.

## Important APIs, Types, and Functions
Public entry points are `omap_iommu_debugfs_init()`, `omap_iommu_debugfs_exit()`, `omap_iommu_debugfs_add()`, and `omap_iommu_debugfs_remove()`. Internal read/show helpers are `debug_read_regs()`, `tlb_show()`, `pagetable_show()`, `omap_iommu_dump_ctx()`, `omap2_iommu_dump_ctx()`, `__dump_tlb_entries()`, `omap_dump_tlb_entries()`, and `dump_ioptable()`. The `pr_reg` macro formats register values from `iommu_read_reg()`.

## Control Flow and State
Init creates the root debugfs directory. Each OMAP IOMMU device gets a child directory with `nr_tlb_entries`, `regs`, `tlb`, and `pagetable`. Reads first reject detached devices (`!obj->domain`). Register dumping uses runtime PM get/put around hardware access. TLB dumping saves the current iotlb lock state, walks valid TLB entries, restores the lock state, and prints CAM/RAM pairs. Page-table dumping locks `obj->page_table_lock`, walks first-level and second-level OMAP page-table entries, and prints populated mappings.

State is debug-only: a global root dentry, each object's `debug_dir`, transient buffers, and read serialization through `iommu_debug_lock`. It does not persist data.

## Dependencies and Integration Points
The file depends on OMAP-specific headers `omap-iommu.h` and `omap-iopgtable.h`, debugfs, seq_file helpers, runtime PM, uaccess helpers, and platform data register definitions. It is an observability companion to the OMAP IOMMU driver rather than part of the fast map/unmap path.

## Risks and Test Signals
Risks include reading hardware while detached, large user `count` allocations for the register file, runtime PM failures ignored by `pm_runtime_get_sync()`, page-table walks racing with updates outside the local lock protocol, and debugfs availability in production builds. Test signals include debugfs creation/removal, register reads while attached/detached, valid TLB dump formatting, populated 1-level and 2-level page-table output, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c -->
