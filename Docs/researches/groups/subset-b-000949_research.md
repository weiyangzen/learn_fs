# subset-b-000949 Research

Grouped research report for the requested Habanalabs MMU, PCI, security, state-dump, sysfs, and Gaudi build subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu.c

Purpose: provides the common Habanalabs MMU front-end and shared helper library. It dispatches map/unmap/translation work to ASIC-version-specific MMU implementations, manages device-resident and host-resident page-table pools, performs cache invalidation and prefetch requests through ASIC callbacks, and provides common PTE/HOP helpers used by `mmu_v1.c`, `mmu_v2.c`, and `mmu_v2_hr.c`.

Important APIs/types/functions: `hl_mmu_init()` and `hl_mmu_fini()` initialize and release `hdev->mmu_func[MMU_DR_PGT]` and `hdev->mmu_func[MMU_HR_PGT]`. `hl_mmu_ctx_init()` and `hl_mmu_ctx_fini()` initialize per-context page-table state. `hl_mmu_map_page()`, `hl_mmu_unmap_page()`, `hl_mmu_map_contiguous()`, and `hl_mmu_unmap_contiguous()` are the public mapping wrappers. `hl_mmu_va_to_pa()` and `hl_mmu_get_tlb_info()` inspect page-table HOPs. `hl_mmu_if_set_funcs()` selects v1, v2, and optional v2 host-resident function tables based on ASIC type. Shared helpers include `hl_mmu_get_hop_pte_phys_addr()`, `hl_mmu_get_next_hop_addr()`, `hl_mmu_scramble_addr()`, `hl_mmu_descramble_addr()`, `hl_mmu_dr_*()` for device-resident tables, and `hl_mmu_hr_*()` for host-resident tables.

Control flow: initialization starts by honoring `hdev->mmu_disable`, setting `hdev->mmu_lock`, and calling available function-table `init` hooks, rolling back DR setup if HR setup fails. Mapping first classifies the virtual address as DRAM or host address, chooses `dmmu`, `pmmu`, or `pmmu_huge` properties, derives a real hardware page size through `asic_funcs->mmu_get_real_page_size`, and invokes the selected residency-specific `map` callback once per real page. On partial map failure it unmaps successfully mapped subpages and flushes. Unmap follows the same address classification and callback dispatch, optionally flushing only after the caller's last page. Contiguous wrappers choose page size from fixed virtual ranges and use the single-page functions with a final flush. Translation locks the global MMU lock, asks the backend for HOP information, then computes the page offset, including a non-power-of-two DRAM-page special case.

State and persistence behavior: persistent runtime state lives in `hdev->mmu_priv.dr`, `hdev->mmu_priv.hr`, per-context hash tables, page-table reference counts, and hardware/device page-table memory. There is no filesystem persistence. Device-resident tables use device memory plus shadow host allocations; host-resident tables use DMA-coherent memory from a gen_pool and preallocated ASID HOP0 entries. `hl_mmu_prefetch_cache_range()` takes a context reference before queueing work and releases it from the workqueue callback. Flushes use memory barriers and, for device-resident page tables, a PTE read to force PCI write visibility.

Dependencies and integration points: the file depends on `struct hl_device`, `struct hl_ctx`, ASIC fixed properties, `hdev->asic_funcs` callbacks, Linux `gen_pool`, DMA-coherent allocation helpers, tracepoints under `trace/events/habanalabs.h`, and context reference management. It integrates with memory allocation paths, userptr/device memory mapping, debug translation paths, device reset/hw init ordering, and firmware MMU cache operations.

Risks and test signals: high-risk areas are page-size/range classification, lock coverage around page-table mutation, rollback after partial map failure, refcount underflow in PTE accounting, double-finalization after reset failures, and address scrambling for DRAM mappings. Test signals include map/unmap stress across DRAM, host, and host-huge ranges; fault injection for gen_pool and DMA allocations; reset and context teardown with live mappings; `hl_mmu_va_to_pa()`/debugfs TLB inspection; MMU cache invalidation failures; tracepoint coverage for map/unmap; and workqueue prefetch during context close or device non-operational transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v1.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v1.c

Purpose: implements the first-generation Habanalabs device-resident MMU backend used by Goya and Gaudi-class ASICs. It builds and tears down multi-hop page tables through the generic device-resident helpers in `mmu.c`, supports host and DRAM mappings, handles huge-page versus normal-page HOP depth, and optionally pre-populates DRAM virtual memory with a default zero-page mapping.

Important APIs/types/functions: `hl_mmu_v1_set_funcs()` installs the backend into `struct hl_mmu_funcs`. `hl_mmu_v1_ctx_init()` initializes the per-context shadow hash and calls `dram_default_mapping_init()`. `hl_mmu_v1_ctx_fini()` tears down default mappings and reports leaked PGT nodes. `hl_mmu_v1_map()` and `hl_mmu_v1_unmap()` walk HOP0 through HOP4 using `get_hop_pte_addr()`, `hl_mmu_dr_get_alloc_next_hop_addr()`, `hl_mmu_dr_write_pte()`, `hl_mmu_dr_write_final_pte()`, and PTE reference helpers. `hl_mmu_v1_get_tlb_info()` reads hardware PTEs for debug/translation.

Control flow: context init creates a shadow hash and, when DRAM virtual memory and default page mapping are enabled for a non-kernel ASID, allocates hop1, hop2, and the needed hop3 tables. It wires them below HOP0 and fills every hop3 PTE with `mmu_dram_default_page_addr | LAST_MASK | PAGE_PRESENT_MASK`. Mapping chooses `dmmu`, `pmmu_huge`, or `pmmu` based on address type and page size. Huge mappings stop one HOP earlier than normal host mappings. New intermediate HOPs are allocated as needed, final PTEs are written first, then parent PTEs are linked and reference counts updated. Unmap walks to the final PTE, rejects non-huge DRAM unmaps, restores the default DRAM PTE when that mode is active, otherwise clears the leaf PTE and recursively frees empty parent HOPs.

State and persistence behavior: state is per-context `mmu_shadow_hash`, `ctx->dram_default_hops`, shadow PTE pages, device-resident PGT pool allocations, and HOP PTE counts. The mappings live only for the running driver context and are destroyed during context close or reset. `hl_mmu_v1_swap_out()` and `hl_mmu_v1_swap_in()` are empty placeholders, so swap state is not tracked here.

Dependencies and integration points: this file depends on the common device-resident helpers from `mmu.c`, `mmu_general.h` HOP constants, ASIC properties such as `dram_supports_virtual_memory`, `dram_page_size`, `pmmu_huge.page_size`, `mmu_dram_default_page_addr`, and hardware PTE read/write callbacks. It is selected by `hl_mmu_if_set_funcs()` for ASIC_GOYA, ASIC_GAUDI, and ASIC_GAUDI_SEC.

Risks and test signals: risks include stale default DRAM mappings, incorrect HOP refcounts when restoring the default page, partial allocation cleanup mistakes, misuse of huge page depth, and leaking PGT nodes on context teardown. Test signals include context init/fini with default DRAM mapping enabled and disabled, mapping over an existing default PTE, unmapping a default-only DRAM VA, host normal and huge page map/unmap, `get_tlb_info()` on present and absent mappings, and fault injection for hop allocation failure at each HOP level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2.c

Purpose: implements the second-generation device-resident MMU backend for Gaudi2-family DRAM/HMMU mappings. In v2, device-resident page tables are allowed only for DRAM addresses; host PMMU mappings are expected to use the host-resident backend when the ASIC properties request it.

Important APIs/types/functions: `hl_mmu_v2_set_funcs()` installs `hl_mmu_dr_init()`, `hl_mmu_dr_fini()`, `hl_mmu_v2_ctx_init()`, `hl_mmu_v2_ctx_fini()`, `hl_mmu_v2_map()`, `hl_mmu_v2_unmap()`, `hl_mmu_dr_flush()`, and `hl_mmu_v2_get_tlb_info()` into `struct hl_mmu_funcs`. `hl_mmu_v2_map()` and `hl_mmu_v2_unmap()` use `MMU_ARCH_6_HOPS` arrays, ASIC address scrambling, common HOP PTE address calculation, and device-resident helper routines.

Control flow: context init only initializes `ctx->mmu_shadow_hash`; context fini reports and frees any leftover PGT nodes. Map rejects non-DRAM addresses, scrambles virtual and physical addresses, walks from HOP0 to the configured last HOP, allocating missing HOPs through `hl_mmu_dr_get_alloc_next_hop_addr()`. It rejects an already-present final PTE, writes the scrambled physical leaf with `last_mask | PAGE_PRESENT_MASK`, links newly allocated intermediate HOPs from their parents, and updates PTE counts. Unmap also rejects non-DRAM, walks through the configured HOPs until a `last_mask` PTE marks a huge mapping, requires DRAM mappings to be huge, clears the leaf, and frees empty parent HOPs while unwinding toward HOP0. TLB info reads hardware PTEs and descrambles the final PTE when the VA was scrambled.

State and persistence behavior: runtime state is per-context shadow hash entries and device-resident page-table allocations from the shared DR pool. Address scrambling means stored PTEs may not be direct physical addresses; `hops->unscrambled_paddr` is populated for consumers that need original addresses. There is no persistent state beyond hardware and driver memory lifetime.

Dependencies and integration points: depends on `mmu_v2_0.h`, `mmu_general.h`, common device-resident MMU helpers, and ASIC callbacks for `scramble_addr`, `descramble_addr`, `read_pte`, and `write_pte`. It is selected for Gaudi2-family ASICs as the DRAM side of the MMU function table.

Risks and test signals: major risks are accidental use for host mappings, scrambling/descrambling mismatch, HOP count or `last_mask` mismatches with ASIC properties, and cleanup of partially allocated HOPs. Test signals include DRAM-only map/unmap success, host-address rejection, huge-page enforcement for DRAM unmap, TLB info on scrambled mappings, allocation-failure unwind tests, and teardown leak warnings from `hl_mmu_v2_ctx_fini()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2_hr.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2_hr.c

Purpose: implements the Gaudi2-family host-resident MMU backend. It stores page tables in DMA-coherent host memory, hashes PGT metadata by physical HOP address, handles host normal and huge PMMU mappings as well as DRAM mappings when routed to host-resident tables, and provides the host-resident callback table consumed by common `hl_mmu_hr_*()` helpers.

Important APIs/types/functions: `hl_mmu_v2_hr_set_funcs()` installs init/fini, context init/fini, map/unmap, flush, TLB info, and `hr_funcs` callbacks. `hl_mmu_v2_hr_init()` and `hl_mmu_v2_hr_fini()` wrap the common host-resident pool lifecycle. `hl_mmu_v2_hr_get_pgt_info()`, `hl_mmu_v2_hr_add_pgt_info()`, and `hl_mmu_v2_hr_get_hop0_pgt_info()` manage lookup and ASID HOP0 selection. `_hl_mmu_v2_hr_map()` and `_hl_mmu_v2_hr_unmap()` perform HOP walking. `hl_mmu_v2_hr_get_tlb_mapping_params()` classifies VA ranges for debug translation.

Control flow: init delegates to `hl_mmu_hr_init()` with the PMMU HOP table size and total PGT size, which preallocates one HOP0 per ASID. Context init creates `ctx->hr_mmu_phys_hash`. Mapping chooses `dmmu`, `pmmu_huge`, or `pmmu`, computes the final HOP via `hl_mmu_v2_get_last_hop()`, scrambles VA and PA, walks from ASID HOP0 through allocated or newly allocated HOPs, rejects existing present mappings, writes the final PTE into DMA-coherent memory, links new parent PTEs, and increments refcounts. Unmap walks the same structure using physical-address hash lookup, detects huge mappings through `last_mask`, rejects non-huge DRAM unmaps, clears PTEs, and frees empty HOPs back to the host-resident pool. TLB info is delegated to the generic `hl_mmu_hr_get_tlb_info()` with v2-specific range classification.

State and persistence behavior: state lives in `hdev->mmu_priv.hr.mmu_pgt_pool`, `hdev->mmu_priv.hr.mmu_asid_hop0`, per-context `hr_mmu_phys_hash`, and `pgt_info` refcounts. DMA-coherent pages are visible to the device and are freed on MMU fini or when empty HOPs are removed. There is no disk persistence. Flush is a memory barrier through `hl_mmu_hr_flush()`.

Dependencies and integration points: depends on the common host-resident helpers in `mmu.c`, Linux hash and DMA memory APIs, ASIC fixed PMMU/DMMU range properties, and address scrambling callbacks. It is installed by `hl_mmu_if_set_funcs()` for Gaudi2-family devices when `prop->pmmu.host_resident` is true, and it services host/userptr mapping paths that cannot use the v2 device-resident backend.

Risks and test signals: risks include physical-address hash mismatch, HOP0 ASID indexing errors, wrong final-HOP choice for mixed page sizes, freeing PGT nodes while still referenced by parent PTEs, and missing memory ordering before device use. Test signals include host and host-huge map/unmap, DRAM HR map/unmap if configured, TLB info for each VA range type, ASID isolation tests, pool growth beyond the initial allocation, allocation failure cleanup, and context teardown leak logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/mmu_v2_hr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/Makefile

Purpose: contributes the common Habanalabs PCI support object to the driver build.

Important APIs/types/functions: defines `HL_COMMON_PCI_FILES := common/pci/pci.o`. There are no runtime functions, variables, or generated artifacts in this Makefile.

Control flow: the parent Habanalabs build includes this variable when composing the complete module object list, causing `common/pci/pci.c` to be compiled into the driver.

State and persistence behavior: no runtime state or persistence; this is build metadata only.

Dependencies and integration points: depends on the surrounding kernel Kbuild fragments that collect `HL_COMMON_PCI_FILES`. It integrates `hl_pci_init()`, BAR mapping, ELBI, iATU, and DMA setup code into the Habanalabs module.

Risks and test signals: the only meaningful risk is build composition drift if `pci.o` is omitted or renamed. Test signals are kernel/module builds with Habanalabs enabled and link failures for common PCI symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/pci.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/pci.c

Purpose: provides common PCI infrastructure for Habanalabs devices: PCI device enablement, BAR reservation and ioremap, ELBI configuration-space access, inbound/outbound iATU programming, DMA mask setup, and PCI cleanup.

Important APIs/types/functions: `hl_pci_init()` and `hl_pci_fini()` are the lifecycle entry points. `hl_pci_bars_map()` maps three 64-bit BARs through normal or write-combined mappings and stores them in `hdev->pcie_bar`. `hl_pci_elbi_read()` and static `hl_pci_elbi_write()` implement ELBI register access through PCI config registers with polling timeouts. `hl_pci_iatu_write()` redirects the DBI window and writes iATU registers. `hl_pci_set_inbound_region()` and `hl_pci_set_outbound_region()` program PCI address translation windows. `hl_get_pci_memory_region()` resolves device addresses into configured `pci_mem_region` entries.

Control flow: `hl_pci_init()` enables PCI memory decoding, sets bus mastering, delegates BAR mapping to ASIC-specific `pci_bars_map`, calls ASIC-specific `init_iatu`, optionally waits for firmware-owned iATU completion, sets coherent DMA masks from `asic_prop.dma_mask`, and sets the maximum DMA segment size. Error paths unwind BAR mappings and disable the PCI device. ELBI reads and writes clear status, program address/data/control config dwords, poll until done/error/timeout, emit tracepoints on success, and return `-EIO` on errors. iATU programming uses ELBI writes to access DesignWare DBI registers and restores the auxiliary DBI selector to default where needed.

State and persistence behavior: runtime state includes requested PCI regions, mapped BAR virtual addresses, physical BAR base values used for inbound region calculations, PCI translation windows, and DMA mask configuration. These persist only while the device is enabled and are released by `hl_pci_fini()`. No filesystem persistence exists.

Dependencies and integration points: depends on Linux PCI and DMA APIs, Habanalabs ASIC callbacks, generated PCI register offsets from `pci_general.h`, tracepoints, and `asic_fixed_properties` fields such as `pcie_aux_dbi_reg_addr`, `pcie_dbi_base_address`, `iatu_done_by_fw`, and `dma_mask`. It integrates with probe/remove, firmware boot sequencing, BAR-backed MMIO, and memory-region selection code.

Risks and test signals: risks include BAR leak on partial map failure, ELBI timeout sensitivity, DBI window not restored after iATU writes, firmware security blocking DBI selector writes, incorrect inbound BAR/address-match mode fields, and DMA mask mismatch with device capabilities. Test signals include probe/remove loops, PCI resource conflict handling, ELBI read/write tracepoints, iATU region validation via MMIO reachability, PLDM timeout behavior, DMA mapping tests above and below the configured mask, and hot reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.c

Purpose: implements common protection-bit and global security-error helpers for Habanalabs ASICs. It builds protection register images, unsecures selected registers or ranges, writes global security arrays to protection blocks across dcores/instances, acknowledges protection violations, and iterates ASIC-described special blocks to report global access errors.

Important APIs/types/functions: `hl_unsecure_register()` and `hl_unsecure_registers()` clear protection bits for explicit registers. `hl_init_pb_with_mask()`, `hl_init_pb()`, `hl_init_pb_ranges_with_mask()`, `hl_init_pb_ranges()`, `hl_init_pb_single_dcore()`, and `hl_init_pb_ranges_single_dcore()` program protection blocks. `hl_config_glbl_sec()` writes global security register arrays. `hl_ack_pb_with_mask()`, `hl_ack_pb()`, and `hl_ack_pb_single_dcore()` print and clear protection violations. `hl_check_for_glbl_errors()` and `hl_iterate_special_blocks()` scan special-block metadata. Internal helpers include `hl_get_pb_block()`, `hl_unset_pb_in_block()`, `hl_unsecure_register_range()`, `hl_ack_pb_security_violations()`, and block-exclusion checks.

Control flow: protection initialization allocates an array of `struct hl_block_glbl_sec`, clears it to a secure baseline through `hl_secure_block()`, unsecures caller-supplied registers or ranges by locating their protection block and clearing the matching bit, then writes the same computed security image to each selected dcore/instance offset, honoring a mask for enabled instances. Acknowledgement loops over the same block layout, reads cause/address registers, delegates ASIC-specific printing to `pb_print_security_errors`, and writes the cause value back to clear it. Global-error checking builds an iterator context and calls `hl_iterate_special_blocks()`, which walks `special_blocks` by major/minor/sub_minor indices while honoring skip-by-type, skip-by-range, and optional hook exclusions.

State and persistence behavior: temporary protection arrays are allocated per call and freed before return. Hardware protection state is persisted in ASIC registers until reset or reprogramming. Error cause registers are cleared by writing the observed cause. Driver state comes from `hdev->asic_prop` and does not persist to disk.

Dependencies and integration points: depends on `security.h`, Habanalabs register access macros `RREG32`/`WREG32`, ASIC fixed properties, generated protection-bit block arrays, `struct range`, block skip configuration, and ASIC-specific `pb_print_security_errors`. It integrates with device security setup, firmware/security-enabled modes, register access policy, error interrupt/polling paths, and per-ASIC special-block descriptions.

Risks and test signals: risks include unsecuring the wrong register due to block-base or offset mistakes, range handling that crosses block boundaries without recalculating the block, mask overflow for more than 64 instances, ignored return values in some single-dcore range initialization, and global error cause indexes beyond the string table if ASIC metadata is inconsistent. Test signals include protection violation injection, PB init with sparse masks, register-range tests at block boundaries, skip hook/range/type tests for special blocks, global error logs with correct addresses, and secure firmware configurations where some DBI/security writes are blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.h

Purpose: declares the common Habanalabs security/protection-bit data contracts used by ASIC-specific security setup code and the generic implementation in `security.c`.

Important APIs/types/functions: constants define global error address/cause offsets and address masks. `struct hl_special_block_info` describes repeated ASIC special-block addressing by block type, base, major/minor/sub_minor counts, and offsets. `struct hl_automated_pb_cfg` models generated protection-bit programming for a block type, including `prot_map`, `data_map`, and data arrays. `struct hl_special_blocks_cfg` groups privileged/secured automated PB configuration and skip policy. `struct hl_skip_blocks_cfg` defines block-type, range, and hook-based exclusions. `struct iterate_special_ctx` carries an iterator callback and opaque data. The header declares `hl_iterate_special_blocks()` and `hl_check_for_glbl_errors()`.

Control flow: consumers populate these structures from generated per-ASIC security data, then pass them to generic iteration and checking code. The iterator callback receives block id and major/minor/sub_minor coordinates for each included special-block instance. Skip hooks can suppress individual instances dynamically before the callback runs.

State and persistence behavior: the header defines in-memory metadata only. The structures point to generated arrays and callback hooks owned by ASIC-specific code. Hardware persistence is handled by code that consumes these definitions, not by the header.

Dependencies and integration points: depends on Linux `io-64-nonatomic-lo-hi.h`, `struct range`, and forward-declared `struct hl_device`. It is included by the common security implementation and ASIC-specific security sources such as Gaudi/Gaudi2/Goya security files.

Risks and test signals: risks are ABI-style structure drift between generated headers and generic code, incorrect interpretation of FW-facing base addresses, and callback signature mismatch. Test signals are successful builds of all ASIC security files, iteration over known generated special-block tables, skip hook coverage, and global error address decoding matching ASIC register maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/state_dump.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/state_dump.c

Purpose: generates a dynamic textual hardware state dump for Habanalabs devices, focused on sync objects, monitor objects, and engine fences. The output is stored through debugfs for diagnostics after hangs, resets, or command submission failures.

Important APIs/types/functions: `hl_state_dump()` is the top-level dump producer. `hl_snprintf_resize()` and `resize_to_fit()` build vmalloc-backed strings that grow by page-sized increments. `hl_format_as_binary()` formats bitfields. `hl_sync_engine_to_string()`, `hl_state_dump_get_sync_name()`, and `hl_state_dump_get_monitor_name()` resolve diagnostic names. `hl_state_dump_free_sync_to_engine_map()` frees ASIC-generated sync-engine maps. Internal dump paths include `hl_state_dump_print_syncs()`, `hl_state_dump_print_monitors()`, `hl_state_dump_print_fences()`, and per-block/per-engine helpers.

Control flow: `hl_state_dump()` starts a growable buffer with a timestamp, prints non-zero sync objects, valid monitors, and active fences, then hands the complete buffer to `hl_debugfs_set_state_dump()`. Sync dumping asks the ASIC-specific `gen_sync_to_engine_map()` callback for an address-to-engine map, iterates named sync managers or `SP_NUM_CORES`, reads sync object arrays from register blocks, skips zero values, appends optional sync names and engine mappings, and frees the map. Monitor dumping allocates and reads a monitor array per sync-manager block, filters through `sds->funcs.monitor_valid`, and delegates formatting to `print_single_monitor`. Fence dumping iterates TPC, MME, and DMA engine counts and calls `print_fences_single_engine` with computed command-queue/status register addresses.

State and persistence behavior: temporary dump data is allocated with `vmalloc()` and freed on errors; a successful buffer is transferred to debugfs state-dump ownership. The source data is live hardware registers plus name/hash tables under `hdev->state_dump_specs`. There is no disk persistence. The timestamp is in kernel nanoseconds from `ktime_get()`.

Dependencies and integration points: depends on `uapi/drm/habanalabs_accel.h`, Habanalabs debugfs, register access macros, `struct hl_state_dump_specs`, ASIC-specific callbacks for map generation, monitor validation/printing, and fence printing, plus name hash tables. It integrates with debugfs diagnostics and device-specific state dump specs set during ASIC initialization.

Risks and test signals: risks include buffer growth failure, dereferencing incomplete `state_dump_specs`, reading registers while the device is inaccessible, sync-manager name arrays not matching property counts, and very large dumps consuming memory. Test signals include debugfs state dump after workload hangs, empty versus active sync/monitor/fence cases, forced allocation failure, ASIC callback error propagation, binary formatting output, and validating that generated dumps include expected engine IDs and named sync/monitor objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/state_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/sysfs.c

Purpose: exposes common Habanalabs device information and controls through sysfs, including firmware versions, PCI address, device status, power/frequency controls, reset triggers, EEPROM data, security state, module identity, and optional inference soft-reset attributes.

Important APIs/types/functions: `hl_sysfs_init()` and `hl_sysfs_fini()` add/remove sysfs groups. Attribute handlers include `clk_max_freq_mhz_show/store`, `clk_cur_freq_mhz_show`, firmware version show functions, `soft_reset_store`, `hard_reset_store`, `device_type_show`, `pci_addr_show`, `status_show`, reset counter show functions, `max_power_show/store`, `eeprom_read_handler`, `security_enabled_show`, `module_id_show`, and `parent_device_show`. Extension hooks `hl_sysfs_add_dev_clk_attr()` and `hl_sysfs_add_dev_vrm_attr()` populate optional clock/VRM groups.

Control flow: init sets `hdev->max_power` to the default, lets ASIC-specific `add_device_attr` fill optional clock and VRM groups, adds the base attribute groups, and conditionally adds the inference group if `allow_inference_soft_reset` is true. Failure adding the inference group removes the base groups. Show/store handlers generally retrieve `hdev` through `dev_get_drvdata()`, check `hl_device_operational()` for firmware-dependent operations, parse numeric input with `kstrtoull()`/`kstrtoul()`, and delegate to firmware or reset helpers. Fini removes base groups and, when present, inference groups.

State and persistence behavior: sysfs writes affect runtime driver/device state: max frequency cache in `asic_prop.max_freq_value`, `hdev->max_power`, firmware max-power and frequency settings, and reset counters/status via the reset flow. Values are not persisted to disk by this code and may reset across driver reload, firmware reset, or reboot. EEPROM reads allocate a temporary buffer and copy firmware-provided data to the sysfs bin read buffer.

Dependencies and integration points: depends on Linux device/sysfs APIs, PCI helpers, Habanalabs firmware helpers (`hl_fw_get_frequency`, `hl_fw_set_frequency`, `hl_fw_get_max_power`, `hl_fw_set_max_power`), reset flow (`hl_device_reset`), ASIC properties and callbacks, and EEPROM retrieval. It integrates directly with userspace observability and administration under the device's sysfs node.

Risks and test signals: risks include user-triggered reset while other operations are active, accepting parsed reset values without checking semantic value, firmware-dependent sysfs calls during non-operational states, fixed PAGE_SIZE EEPROM bin size versus requested offset semantics, and exposing stale firmware version strings. Test signals include sysfs group creation/removal on probe/remove and failure unwind, read/write tests for max power and clocks, reset trigger behavior and counters, non-operational device reads returning `-ENODEV`, EEPROM binary reads, and ASIC-specific optional clock/VRM attribute visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/Makefile

Purpose: defines the Gaudi ASIC-specific object files that are included in the Habanalabs driver build.

Important APIs/types/functions: declares `HL_GAUDI_FILES := gaudi/gaudi.o gaudi/gaudi_security.o gaudi/gaudi_coresight.o`. There are no runtime functions in this Makefile.

Control flow: the parent Kbuild logic consumes `HL_GAUDI_FILES` so Gaudi device support, Gaudi security/protection setup, and Gaudi CoreSight support are linked when the driver is built with Gaudi support.

State and persistence behavior: no runtime state or persistence; this is build metadata only.

Dependencies and integration points: depends on neighboring Gaudi source files and the parent Habanalabs Kbuild composition. It integrates ASIC-specific Gaudi code with the common driver core, including the common security helper layer researched in this subset.

Risks and test signals: risks are build breakage or missing runtime support if object names drift or a needed object is omitted. Test signals are Habanalabs module builds with Gaudi enabled and symbol availability for Gaudi security and CoreSight initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/Makefile -->
