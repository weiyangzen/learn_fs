# subset-b-003948 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mcg.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mcg.c

Purpose: manages Mellanox mthca multicast group membership records (MGMs) for InfiniBand QPs, including hash-bucket MGMs and chained auxiliary MGMs.

Important APIs/functions: defines the packed firmware-facing `struct mthca_mgm`; implements `mthca_multicast_attach`, `mthca_multicast_detach`, `mthca_init_mcg_table`, and `mthca_cleanup_mcg_table`. The internal `find_mgm` hashes a GID with `mthca_MGID_HASH`, follows `next_gid_index` chains via `mthca_READ_MGM`, and reports whether the matching GID, an empty primary slot, or no auxiliary entry exists.

Control flow: attach allocates a mailbox, locks `dev->mcg_table.mutex`, finds or creates the MGM/AMGM entry, installs the QP number with the high valid bit set, writes the entry, and links a newly allocated AMGM from the previous chain element. Detach finds the entry, removes the QP by swapping the final occupied slot into its position, writes the MGM, and if the entry became empty either clears the primary MGM or unlinks/frees an AMGM.

State and persistence: multicast membership is persisted in HCA multicast table entries through firmware commands; the driver only tracks AMGM allocation via `dev->mcg_table.alloc` and serializes updates with the table mutex. The `lid` argument is unused in this implementation.

Dependencies and integration: depends on `mthca_cmd` mailbox commands, the common allocator in `mthca_alloc`, `dev->limits.num_mgms/num_amgms`, and RDMA core multicast attach/detach hooks registered by `mthca_provider.c`.

Risks: chain corruption or firmware command failure can leave hardware membership partially updated; full MGMs return `-ENOMEM`; invalid zero GIDs in AMGM entries are treated as corruption. Cleanup only tears down allocator state and does not verify that all memberships were detached.

Test signals: exercise RDMA multicast join/leave on UD QPs, duplicate attach idempotence, full-group behavior, AMGM chain creation/removal, and firmware failure unwinding under `mthca_multicast_attach`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.c

Purpose: implements "mem-free" Arbel/Sinai context-memory management for mthca, including ICM allocation/mapping, lazy ICM tables, user/kernel doorbell record mapping, and kernel doorbell page allocation.

Important APIs/functions: exports `mthca_alloc_icm`, `mthca_free_icm`, `mthca_alloc_icm_table`, `mthca_free_icm_table`, `mthca_table_get/put/find/get_range/put_range`, `mthca_map_user_db`, `mthca_unmap_user_db`, `mthca_init_user_db_tab`, `mthca_cleanup_user_db_tab`, `mthca_alloc_db`, `mthca_free_db`, `mthca_init_db_tab`, and `mthca_cleanup_db_tab`.

Control flow: ICM allocation builds chunk lists from the largest available orders up to 256 KiB, maps noncoherent chunks with `dma_map_sg`, and zeroes pages because firmware expects cleared context memory. Table get lazily allocates a 256 KiB ICM chunk, maps it with `mthca_MAP_ICM`, increments a refcount, and table put unmaps/free when the refcount reaches zero. User doorbell mapping pins a user page, DMA maps it, maps one ICM page at the UARC virtual address, and defers unmapping until context cleanup. Kernel doorbells allocate coherent pages from two allocation groups so SQ/CQ-arm and RQ/SRQ/CQ-set-CI records grow from opposite ends.

State and persistence: all state is runtime kernel/HCA state: `mthca_icm_table.icm[]` refcounts, pinned user DB pages, coherent kernel DB pages, and firmware ICM mappings. No disk persistence exists.

Dependencies and integration: used by QP, CQ, SRQ, MR, EQ, and UAR paths on mem-free devices; depends on DMA mapping APIs, user page pinning, `mthca_MAP_ICM`, `mthca_UNMAP_ICM`, `mthca_MAP_ICM_page`, and `dev->uar_table`.

Risks: refcount mismatches can leak or prematurely unmap firmware context pages; long-term user page pins must be released on all context paths; `mthca_unmap_user_db` intentionally delays actual unmapping, so cleanup is critical. Doorbell group boundary logic is subtle and can leak pages until table cleanup.

Test signals: probe/unload mem-free HCAs, create/destroy user and kernel QPs/CQs/SRQs, stress doorbell allocation exhaustion, exercise failed `mthca_MAP_ICM*` paths, and run with DMA/debug page-pin diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.h

Purpose: declares the mem-free context-memory and doorbell-record abstractions shared across the mthca driver.

Important APIs/types/functions: defines `MTHCA_ICM_PAGE_SHIFT`, `MTHCA_ICM_PAGE_SIZE`, `MTHCA_DB_REC_PER_PAGE`, `struct mthca_icm_chunk`, `struct mthca_icm`, `struct mthca_icm_table`, `struct mthca_icm_iter`, `struct mthca_db_page`, `struct mthca_db_table`, and `enum mthca_db_type`. It declares ICM allocation/table lookup APIs plus user and kernel doorbell mapping/allocation APIs.

Control flow: inline iterator helpers `mthca_icm_first`, `mthca_icm_last`, `mthca_icm_next`, `mthca_icm_addr`, and `mthca_icm_size` provide firmware command code with a simple page-by-page view over chunked scatterlists. Doorbell types encode firmware record meanings for CQ set-consumer-index, CQ arm, SQ, RQ, SRQ, and group separators.

State and persistence: structures describe in-memory runtime state: ICM chunks carry scatterlist pages and DMA mappings, tables carry object-to-ICM chunk mappings with mutex protection, and doorbell tables track coherent DB pages and bitmap allocation.

Dependencies and integration: included by `mthca_memfree.c`, QP/SRQ/CQ/MR setup, and UAR handling. It depends on Linux lists, mutexes, scatterlists, DMA addresses, and mthca device/uar declarations.

Risks: callers must respect object-size/chunk-size assumptions and mem-free versus Tavor behavior. `mthca_icm_table.icm[]` is a flexible array with `__counted_by(num_icm)`, so allocation size must match `num_icm`. Doorbell indices are shared with userspace ABI data and must remain stable.

Test signals: compile coverage across supported kernel configs, mem-free QP/CQ/SRQ creation, table refcount get/put tests, and sparse/lockdep checks around iterator and mutex use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mr.c

Purpose: manages mthca memory translation tables (MTTs), memory protection table (MPT) entries, memory keys, and memory region lifetime for DMA, physical, user, and fast memory registration paths.

Important APIs/functions: defines firmware-facing `struct mthca_mpt_entry` and private `struct mthca_mtt`; implements MTT buddy allocation (`mthca_buddy_*`), `mthca_alloc_mtt`, `mthca_free_mtt`, `mthca_write_mtt`, `mthca_write_mtt_size`, `mthca_mr_alloc`, `mthca_mr_alloc_notrans`, `mthca_mr_alloc_phys`, `mthca_free_mr`, `mthca_init_mr_table`, and `mthca_cleanup_mr_table`.

Control flow: MTT allocation picks an order large enough for the requested segment count and, on mem-free devices, maps backing ICM ranges. MTT writes either use the firmware `WRITE_MTT` mailbox path or optimized FMR writes directly into ioremapped Tavor/Arbel MTT memory. MR allocation allocates an MPT index, transforms it into the device key format, optionally maps an MPT ICM entry, populates the MPT mailbox, and transitions it with `SW2HW_MPT`. Free reverses with `HW2SW_MPT`, allocator release, table put, and MTT free.

State and persistence: maintains runtime MPT index allocation, MTT buddy bitmaps, optional reserved FMR MTT buddy state, and ioremapped FMR windows. Registered MRs persist only as hardware state until deregistration or device teardown.

Dependencies and integration: used by provider DMA/user MR verbs, PD privileged notrans MR setup, QP/SRQ/CQ buffer registration, and FMR support. Depends on `mthca_cmd`, `mthca_memfree`, PCI BAR ioremap, endian conversions, and mthca key layout quirks for Tavor, Arbel, and Sinai optimization.

Risks: key/index conversion is device-specific; wrong transformation can expose or invalidate memory. Buddy allocation is linear and can fragment under churn. Fast paths use direct MMIO/ioremapped writes with page-size constraints and BUG_ON checks. Cleanup comments note no active-MR leak verification.

Test signals: register/deregister user MRs with varied page counts, stress FMR and regular MTT allocation, validate remote access flags, run RDMA read/write/atomic traffic, and use fault injection for `SW2HW_MPT`, `WRITE_MTT`, and ICM table failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_pd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_pd.c

Purpose: allocates and frees mthca protection domains and initializes the PD number allocator.

Important APIs/functions: exports `mthca_pd_alloc`, `mthca_pd_free`, `mthca_init_pd_table`, and `mthca_cleanup_pd_table`. `mthca_pd_alloc` assigns `pd->privileged`, initializes `sqp_count`, allocates a PD number, and for privileged kernel PDs creates a no-translation local read/write MR in `pd->ntmr`.

Control flow: allocation takes a PD index from `dev->pd_table.alloc`. If the PD is privileged, it calls `mthca_mr_alloc_notrans`; failure releases the PD number. Free tears down the privileged notrans MR before returning the PD number. Table init reserves firmware-reserved PDs and caps the allocator at 24-bit PD numbers.

State and persistence: PD state is held in `struct mthca_pd`: `pd_num`, `privileged`, `sqp_count`, and optional `ntmr`. It is runtime-only and tied to RDMA core PD object lifetime.

Dependencies and integration: called by provider `alloc_pd/dealloc_pd`; the privileged MR is used by special QP management send headers and other kernel-only mappings. Depends on the common mthca allocator and MR allocation code.

Risks: privileged PD setup can fail after PD number allocation and must unwind correctly. The cleanup path explicitly does not check for still-allocated PDs. Kernel consumers rely on `ntmr` being valid for special QP header DMA segments.

Test signals: create/destroy user and kernel PDs, create SMI/GSI QPs requiring privileged PD resources, exhaust PD allocation, and probe/unload with leak/debug allocator checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.c

Purpose: converts requested mthca resource counts into an HCA context-memory layout and fills both device limits and `INIT_HCA` firmware parameters.

Important APIs/functions: exports `mthca_make_profile`; defines resource identifiers for QP, EEC, SRQ, CQ, EQP, EEEC, EQ, RDB, MCG, MPT, MTT, UAR, UDAV, and UARC. Constants set 32 EQs and 32768 PDs.

Control flow: builds a temporary resource array with entry sizes from `mthca_dev_lim` and requested counts from `mthca_profile`, scales sizes by count, enforces at least one page per mem-free resource, chooses memory base/available size for mem-free ICM or Tavor DDR, sorts resources by decreasing size, assigns packed starts, checks total size against available HCA memory, then writes per-resource bases/log sizes into `init_hca` and `dev->limits`.

State and persistence: produces runtime initialization state: resource base addresses, log table sizes, split multicast group counts, MTT/FMR reservation limits, UARC layout, and PD capacity. No persistent storage exists beyond the initialized device.

Dependencies and integration: called during device bring-up before `INIT_HCA`; uses firmware-reported entry sizes and limits, driver flags such as `MTHCA_FLAG_SINAI_OPT`, mem-free detection, and DDR/firmware layout from `dev`.

Risks: bad requested counts can overflow memory budget or produce invalid log sizes. MCG count is split in half between primary MGMs and AMGM overflow entries. Sinai memory-key throughput optimization is disabled when MPT table size is too large. 32-bit Tavor reserves FMR MTTs to avoid excessive vmalloc pressure.

Test signals: probe with Tavor and mem-free devices, vary module/profile resource requests, validate `INIT_HCA` values against firmware acceptance, and test low-memory profile rejection diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.h

Purpose: declares the mthca HCA resource profile request structure and the profile-building entry point.

Important APIs/types/functions: `struct mthca_profile` carries requested counts for QPs, RDBs per QP, SRQs, CQs, multicast groups, MPTs, MTTs, UD address vectors, UARs, UARC size, and reserved FMR MTTs. `mthca_make_profile` maps this request and firmware limits into `struct mthca_init_hca_param`.

Control flow: this header has no executable control flow beyond exposing the single builder prototype; implementation is in `mthca_profile.c`.

State and persistence: profile values are transient bring-up inputs, later copied into `dev->limits`, `dev` table bases, and INIT_HCA parameters. They are not persisted outside the device initialization path.

Dependencies and integration: includes `mthca_dev.h` and `mthca_cmd.h` because the builder needs device state, firmware device limits, and INIT_HCA command structures. Consumers are the main mthca initialization/profile selection code.

Risks: all fields are plain `int`, so callers must bound values before/while building the profile. The ABI between profile fields and firmware resource sizing is implicit and must stay aligned with `mthca_make_profile`.

Test signals: compile coverage, successful driver probe with default and tuned profile values, and failure-path tests for oversized requested resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.c

Purpose: binds the mthca low-level HCA implementation to the Linux RDMA core verbs interface, including device/port queries, ucontext/PD/CQ/QP/SRQ/AH/MR verbs, sysfs attributes, and device registration.

Important APIs/functions: implements RDMA device ops such as `mthca_query_device`, `mthca_query_port`, `mthca_modify_device`, `mthca_modify_port`, `mthca_query_pkey`, `mthca_query_gid`, `mthca_alloc_ucontext`, `mthca_mmap_uar`, `mthca_alloc_pd`, `mthca_create_qp`, `mthca_create_cq`, `mthca_resize_cq`, `mthca_reg_user_mr`, `mthca_dereg_mr`, `mthca_register_device`, and `mthca_unregister_device`.

Control flow: query paths allocate SMP MAD mailboxes and call `mthca_MAD_IFC`. User context allocation creates a UAR, optional mem-free user DB table, and returns ABI data. Object creation validates udata/create flags, maps user doorbell pages when applicable, delegates allocation to lower-level CQ/QP/SRQ/MR/AH code, and copies object ids back to userspace. Registration initializes node data, composes base, SRQ, and Tavor/Arbel-specific `ib_device_ops`, registers with RDMA core, and starts catastrophic error polling.

State and persistence: manages RDMA core object lifetime and runtime mappings: UAR PFNs, user DB pages, CQ resize buffers, MRs with `ib_umem`, and sysfs-visible board/revision strings. No disk persistence exists.

Dependencies and integration: depends on RDMA core/uverbs ABI, MAD/SMP helpers, mthca command interface, mem-free doorbell mapping, lower-level CQ/QP/SRQ/MR/AH modules, and PCI device data.

Risks: userspace ABI validation and cleanup ordering are critical; partial failures after mapping doorbells must unmap both SQ/RQ or CQ DBs. CQ resize has concurrent poll/resize states. `mthca_reg_user_mr` supports old libmthca inputs with warnings. Device ops vary by mem-free versus Tavor and SRQ support, so missing ops would break verbs behavior.

Test signals: rdma-core verbs tests for query/create/modify/destroy, user MR registration and deregistration, CQ resize, mmap UAR, SRQ creation on supported hardware, sysfs attribute reads, and unload after active object churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.h

Purpose: defines the mthca RDMA-provider object wrappers and shared provider-side structures used by verbs implementations.

Important APIs/types/functions: declares access flag bits, `struct mthca_buf_list`, `union mthca_buf`, `struct mthca_uar`, `struct mthca_ucontext`, `struct mthca_mr`, `struct mthca_pd`, `struct mthca_eq`, `struct mthca_ah`, `struct mthca_cq`, `struct mthca_srq`, `struct mthca_wq`, `struct mthca_sqp`, and `struct mthca_qp`. It also provides `to_mucontext`, `to_mmr`, `to_mpd`, `to_mah`, `to_mcq`, `to_msrq`, and `to_mqp` container helpers.

Control flow: the header itself contains no runtime control flow except inline container conversions. Its embedded locking comment describes the CQ/QP table and object reference protocol used by event, completion, and destroy paths.

State and persistence: structures hold runtime state for RDMA objects: object numbers, DMA buffers/MRs, doorbell indices/records, WQ ring positions, WRID arrays, QP state/transport, special-QP headers, CQ resize buffers, refcounts, wait queues, spinlocks, and mutexes.

Dependencies and integration: included by provider, CQ, QP, SRQ, AH, EQ, and MR code; depends on RDMA core `ib_verbs.h` and packet/header packing helpers. The container helpers bridge generic `struct ib_*` objects to mthca private state.

Risks: lock ordering in the comment is part of the concurrency contract; violating it risks deadlock or use-after-free during completion/event/destroy races. Several fields are hardware-generation-specific, so callers must check mem-free/Tavor behavior before use.

Test signals: lockdep under CQ/QP event and destroy stress, RDMA object create/destroy loops, special QP traffic, CQ resize, and compile checks after RDMA core API changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_qp.c

Purpose: implements mthca queue pair allocation, state transitions, querying, send/receive posting, special QP handling, event dispatch, and QP table lifetime management.

Important APIs/functions: exports `mthca_query_qp`, `mthca_modify_qp`, `mthca_alloc_qp`, `mthca_alloc_sqp`, `mthca_free_qp`, `mthca_tavor_post_send`, `mthca_tavor_post_receive`, `mthca_arbel_post_send`, `mthca_arbel_post_receive`, `mthca_free_err_wqe`, `mthca_init_qp_table`, `mthca_cleanup_qp_table`, and `mthca_qp_event`. It defines firmware QP context/path structures, state/transport mappings, and opcode conversion tables.

Control flow: allocation sizes SQ/RQ WQEs, maps mem-free QP/EQP/RDB ICM, allocates/registers kernel WQE buffers, allocates mem-free doorbells, initializes WQE rings, and publishes the QP in `dev->qp_table.qp`. Modify validates RDMA core state transitions, builds a firmware `mthca_qp_param`, handles path/GRH/access/PSN/CQ/SRQ fields, calls `mthca_MODIFY_QP`, updates cached state, and opens/closes the IB port for QP0 transitions. Posting paths lock SQ/RQ rings, check overflow against CQ-updated tails, build WQE segments by transport/opcode, write WRIDs, use memory barriers, then ring Tavor MMIO doorbells or Arbel doorbell records plus MMIO.

State and persistence: QP runtime state includes QPN allocation, hardware QP context, WQE buffers, WRID arrays, SQ/RQ head/tail/next pointers, mem-free doorbell records, cached access/port/state fields, special-QP header DMA buffers, and table refcounts. State persists in HCA context until reset/destroy.

Dependencies and integration: called by provider QP verbs and CQ cleanup; uses `mthca_memfree`, `mthca_wqe`, AH helpers, MR/buffer allocation, RDMA core QP validation, firmware commands (`QUERY_QP`, `MODIFY_QP`, `CONF_SPECIAL_QP`, `INIT_IB`, `CLOSE_IB`), and cached P_Key/GID data.

Risks: WQE construction is highly ordering-sensitive; missing barriers or bad doorbell counts can expose incomplete descriptors to hardware. The code has comments noting missing state checks in post paths. Special QP MLX header construction depends on PD `ntmr` and cached pkeys. Error unwind must coordinate CQ locks and QP table removal to avoid completion use-after-free.

Test signals: RC/UC/UD traffic, QP modify transition matrix, QP0/QP1 MAD traffic, Tavor and Arbel posting paths, send/receive overflow, CQ cleanup after reset/error, path migration events, atomics/RDMA writes/reads, and lockdep around QP destroy versus polling/events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_reset.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_reset.c

Purpose: performs a hardware reset of an mthca PCI/PCI-X/PCIe HCA while preserving and restoring required PCI configuration space.

Important APIs/functions: exports `mthca_reset`. It saves HCA config header dwords, optionally finds and saves the associated Tavor bridge config, writes the reset register at BAR0 offset `0xf0010`, waits for the device to reappear, and restores bridge/HCA PCI-X or PCIe control registers plus core header fields.

Control flow: for non-PCIe devices it searches for a Mellanox bridge with device id `pdev->device + 2` on the parent bus. It allocates header buffers, reads config dwords except offsets 22 and 23, locates PCI-X/PCIe capabilities, ioremaps the reset register, writes the reset value, sleeps one second, polls config space up to ten seconds, then restores bridge split-transaction controls, COMMAND registers last, HCA PCI-X/PCIe controls, and HCA header registers.

State and persistence: transiently stores PCI config headers in heap buffers; the lasting effect is a reset HCA with restored PCI config. It also takes a reference to any bridge via `pci_get_device` and releases it at exit.

Dependencies and integration: used during mthca probe/recovery; depends on Linux PCI, ioremap/writel, sleeps, device flags identifying PCIe, and mthca logging.

Risks: reset is hardware- and bus-topology-sensitive. Failure to restore config can leave the device or bridge unusable. The code only saves 256 bytes and notes uncertainty about full PCIe 4K config space. It skips two dwords with special meaning and assumes bridge discovery by device id.

Test signals: cold probe with reset enabled on Tavor/Arbel/Sinai, PCIe and PCI-X systems, reset failure injection for config reads/writes, and post-reset firmware initialization success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_srq.c

Purpose: implements shared receive queue allocation, firmware context setup, receive posting, event dispatch, querying/modification, and SRQ table lifetime for mthca.

Important APIs/functions: defines Tavor and Arbel SRQ context structures; exports `mthca_alloc_srq`, `mthca_free_srq`, `mthca_modify_srq`, `mthca_query_srq`, `mthca_srq_event`, `mthca_free_srq_wqe`, `mthca_tavor_post_srq_recv`, `mthca_arbel_post_srq_recv`, `mthca_max_srq_sge`, `mthca_init_srq_table`, and `mthca_cleanup_srq_table`.

Control flow: allocation validates requested WR/SGE limits, adjusts max WR for hardware generation, computes WQE stride, allocates SRQN, maps mem-free SRQ ICM and DB record, allocates kernel buffers/WRID array unless userspace owns them, initializes a free-list embedded in WQEs, builds the proper firmware context, transitions with `SW2HW_SRQ`, and publishes the SRQ in the table. Posting pops WQEs from the free list, fills data segments, stores WRIDs, and rings either Tavor receive doorbells or Arbel DB records after write barriers.

State and persistence: runtime state includes SRQN allocation, firmware SRQ context, queue buffer/MR, free-list indices, WQE counter, DB record, WRID array, table pointer, refcount, wait queue, and locks. Hardware state persists until `HW2SW_SRQ` and table cleanup.

Dependencies and integration: provider SRQ verbs call these APIs; CQ completion handling returns WQEs through `mthca_free_srq_wqe`; uses `mthca_memfree`, `mthca_wqe`, buffer/MR allocation, and SRQ firmware commands.

Risks: SRQ free-list manipulation is subtle, especially because Tavor posting can overwrite the previous WQE next segment, so the code stores software links in `imm`. Doorbell ordering requires barriers. SRQ resize is explicitly unsupported. Destruction must wait for event references before freeing.

Test signals: create/query/arm/destroy SRQs, post receive bursts up to capacity, completion recycling, SRQ limit events, Arbel versus Tavor paths, userspace SRQ doorbell mapping, and lockdep/event race testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_uar.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_uar.c

Purpose: manages mthca user access region (UAR) allocation and table initialization, including mem-free doorbell table setup.

Important APIs/functions: exports `mthca_uar_alloc`, `mthca_uar_free`, `mthca_init_uar_table`, and `mthca_cleanup_uar_table`.

Control flow: allocation takes a UAR index from `dev->uar_table.alloc` and computes the page frame number from PCI BAR2 plus the index. Free returns the index. Table initialization initializes the allocator with firmware-reserved UARs plus one extra reserved slot, then initializes the kernel doorbell table. Cleanup tears down the doorbell table and allocator.

State and persistence: `struct mthca_uar` stores `index` and `pfn`; table state lives in `dev->uar_table.alloc` and `dev->db_tab` for mem-free devices. All state is runtime and tied to device/context lifetime.

Dependencies and integration: provider user context allocation calls `mthca_uar_alloc`; mmap maps the resulting PFN to userspace. QP/CQ/SRQ kernel paths use the driver UAR and DB table. Depends on PCI resource layout and `mthca_memfree.c`.

Risks: PFN calculation assumes BAR2 is the UAR aperture and one page per UAR. Cleanup does not verify no UARs remain allocated. Doorbell table init failure must unwind allocator init.

Test signals: allocate/deallocate user contexts, mmap UAR page, create mem-free QPs/CQs/SRQs using DB records, exhaust UAR allocation, and unload with debug allocator checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_uar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_wqe.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_wqe.h

Purpose: defines mthca work queue element segment layouts and helpers used to build send, receive, SRQ, and special QP descriptors.

Important APIs/types/functions: declares WQE flag bits such as `MTHCA_NEXT_DBD`, `MTHCA_NEXT_FENCE`, CQ/event/solicit/checksum bits, MLX VL15/SLR bits, invalid L_Key sentinel, and Tavor/Arbel doorbell batch limits. Defines segment structs: `mthca_next_seg`, `mthca_tavor_ud_seg`, `mthca_arbel_ud_seg`, `mthca_bind_seg`, `mthca_raddr_seg`, `mthca_atomic_seg`, `mthca_data_seg`, and `mthca_mlx_seg`. Provides `mthca_set_data_seg` and `mthca_set_data_seg_inval`.

Control flow: inline helpers encode `ib_sge` into big-endian hardware data segments or mark a data segment invalid with L_Key `0x100`.

State and persistence: no persistent state; structs are hardware descriptor formats written into QP/SRQ WQE rings and consumed by the HCA.

Dependencies and integration: included by `mthca_qp.c` and `mthca_srq.c`; relies on Linux fixed-width/endian types and RDMA `struct ib_sge` being visible through includers.

Risks: segment layout and endian fields are firmware ABI. Any packing, size, or flag mistakes can corrupt DMA operations. Invalid sentinel use must match hardware expectations so unused SGEs are not interpreted as valid DMA.

Test signals: compile layout-sensitive code, run send/receive/RDMA/atomic/UD/special-QP traffic, validate checksum offload flags on Arbel, and inspect failed CQEs for descriptor formatting issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_wqe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Kconfig

Purpose: declares the kernel configuration option for the Emulex OneConnect ocrdma RoCE driver.

Important APIs/types/functions: defines `CONFIG_INFINIBAND_OCRDMA` as a tristate option labeled "Emulex One Connect HCA support".

Control flow: Kconfig dependency resolution requires `ETHERNET`, `NETDEVICES`, `PCI`, and `INET`; selecting the option also selects `NET_VENDOR_EMULEX` and `BE2NET`.

State and persistence: build-time configuration state only. When enabled as built-in or module, the ocrdma objects listed by the Makefile become part of the kernel build.

Dependencies and integration: couples the RDMA driver to the Emulex be2net Ethernet/NIC driver because ocrdma shares OneConnect hardware support and headers.

Risks: missing `BE2NET` or networking dependencies prevents the driver from building. The help text says "InfiniBand over Ethernet", reflecting RoCE support rather than native InfiniBand link-layer behavior.

Test signals: Kconfig allmodconfig/allyesconfig coverage, module build with `CONFIG_INFINIBAND_OCRDMA=m`, and dependency checks when BE2NET is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Makefile

Purpose: builds the ocrdma RoCE driver module and wires in its source objects.

Important APIs/types/functions: adds the be2net include path with `ccflags-y`, builds `ocrdma.o` when `CONFIG_INFINIBAND_OCRDMA` is enabled, and composes it from `ocrdma_main.o`, `ocrdma_verbs.o`, `ocrdma_hw.o`, `ocrdma_ah.o`, and `ocrdma_stats.o`.

Control flow: kernel kbuild evaluates `obj-$(CONFIG_INFINIBAND_OCRDMA)` and links the listed `ocrdma-y` objects into one module/built-in object.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: depends on headers under `drivers/net/ethernet/emulex/benet`, especially `be_roce.h`, and integrates with the RDMA hw driver directory build.

Risks: include path drift between be2net and ocrdma can break builds. Adding a source file without updating `ocrdma-y` would omit it from the driver.

Test signals: kernel `M=drivers/infiniband/hw/ocrdma` builds, allmodconfig, and dependency builds after be2net header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma.h

Purpose: central private header for the Emulex OneConnect RoCE driver, defining device attributes, queue/memory/resource objects, RDMA core wrappers, and utility inline helpers.

Important APIs/types/functions: defines version/name constants, device IDs, `OCRDMA_MAX_AH`, DMA/PBL/queue structs, `ocrdma_dev_attr`, EQ/MQ command context, HW/user MR types, PD resource manager, stats/PHY structs, `ocrdma_dev`, CQ/PD/AH/QP/SRQ/ucontext/mm wrappers, container helpers (`get_ocrdma_*`), CQE predicate helpers, `ocrdma_resolve_dmac`, `hca_name`, EQ lookup, ASIC type/prio/link helpers, and UDP encapsulation support checks.

Control flow: inline functions convert RDMA core objects to private structs, check CQE validity/flags, derive destination MACs from multicast/link-local/roce attributes, map device ids to names, locate EQ table entries, lazily read ASIC id from PCI config, and interpret link/PFC/app-priority state.

State and persistence: structures hold all runtime ocrdma state: firmware limits, EQ/CQ/QP tables, GSI CQs, AV table, mailbox queue context, be2net NIC info, stats/debugfs memory, PD bitmaps, per-object queues, doorbells, DMA addresses, and user mmap metadata.

Dependencies and integration: includes RDMA core headers, `ib_addr.h`, be2net RoCE integration header `be_roce.h`, and `ocrdma_sli.h`. Other ocrdma source files include this for all private driver state.

Risks: this header is a broad shared contract; structure changes affect multiple object lifetimes and userspace interactions. CQE phase logic and MAC resolution must match hardware/RDMA core semantics. Comments show synchronization responsibilities, so misuse can race CQ polling, QP flushing, or GID updates.

Test signals: full ocrdma build, RoCE connection traffic, CQ polling phase wrap tests, link/PFC changes, AH creation for multicast/link-local/routed GIDs, debugfs stats, and be2net integration probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.c

Purpose: implements ocrdma address handle creation, destruction, querying, and basic MAD performance-management processing for RoCE.

Important APIs/functions: internal `ocrdma_hdr_type_to_proto_num` maps RDMA network type to Ethernet protocol; `set_av_attr` fills an ocrdma address vector; exported verbs are `ocrdma_create_ah`, `ocrdma_destroy_ah`, `ocrdma_query_ah`, and `ocrdma_process_mad`.

Control flow: create validates RoCE AH with GRH, refreshes service level if requested, reads VLAN from the SGID attributes, allocates an AV, records the GID network type, and calls `set_av_attr`. AV setup chooses IBoE/IPv4/IPv6 protocol, applies VLAN/PFC service-level tagging, resolves destination MAC, copies Ethernet header, then writes either IPv4 or GRH/IPv6-style fields with SGID/DGID, flow label, traffic class, PD id, next-header, and hop limit. User PDs receive a compact AH id/type/VLAN word in their AH table. Destroy frees the AV. Query reconstructs an `rdma_ah_attr` from the stored AV. MAD processing replies to performance management MADs via `ocrdma_pma_counters`.

State and persistence: AH state lives in `struct ocrdma_ah` and the device AV table; user contexts may get an AH id entry. It persists until AH destroy.

Dependencies and integration: depends on RDMA address/GID helpers, neighbour/netevent headers, `ocrdma_alloc_av/free_av`, service-level init, stats counters, VLAN/PFC state from `ocrdma_dev`, and hardware AV layout from SLI headers.

Risks: protocol and endian handling are critical; `ocrdma_query_ah` infers GRH offset from AV validity/VLAN layout. VLAN 0 with PFC logs warnings but proceeds. Incorrect SGID network type or AH table index can break userspace sends.

Test signals: create/query/destroy AHs for IB GRH, IPv4 RoCEv2, IPv6 RoCEv2, VLAN and non-VLAN paths, multicast and link-local destination MAC resolution, userspace AH table updates, and PMA MAD counter queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.h

Purpose: declares ocrdma address-handle constants and verbs/MAD entry points.

Important APIs/types/functions: defines bit masks and shifts for userspace AH ids: `OCRDMA_AH_ID_MASK`, VLAN-valid mask/shift, and L3 type mask/shift. Declares `ocrdma_create_ah`, `ocrdma_destroy_ah`, `ocrdma_query_ah`, and `ocrdma_process_mad`.

Control flow: no executable control flow; implementation lives in `ocrdma_ah.c`.

State and persistence: constants define how AH metadata is packed into the user context AH table, combining hardware AV id, optional L3 type, and VLAN-valid information.

Dependencies and integration: included by ocrdma verbs registration code and `ocrdma_ah.c`; function prototypes use RDMA core types (`ib_ah`, `rdma_ah_init_attr`, `rdma_ah_attr`, `ib_device`, MAD structures).

Risks: masks and shifts are part of the implicit userspace/kernel ABI for AH table entries. Changing them without coordinating userspace/provider code would break address-vector lookup.

Test signals: compile coverage, userspace AH creation with UDP encapsulation and VLAN, and validation that packed AH table values are decoded correctly by consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.h -->
