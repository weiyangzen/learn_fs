# subset-b-003920 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/provider.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/provider.c

## Purpose

`provider.c` is the RDMA core provider registration layer for the Chelsio cxgb4 iWARP driver. It binds Chelsio's low-level `c4iw_rdev` resources to `struct ib_device_ops`, exposes device/port attributes and sysfs attributes, manages user contexts and protection domains, implements user mmap dispatch for queues/status pages/BAR mappings, and registers/unregisters the RNIC with the RDMA subsystem.

## Important APIs, Types, and Functions

- `fastreg_support`: module parameter controlling whether `IB_DEVICE_MEM_MGT_EXTENSIONS` is advertised.
- `c4iw_alloc_ucontext` / `c4iw_dealloc_ucontext`: initialize per-process `c4iw_dev_ucontext`, maintain mmap key lists, expose the status page to modern user libraries, and release queued mmap metadata.
- `c4iw_mmap`: consumes a one-shot `c4iw_mm_entry` by key and maps BAR, write-combining BAR, contiguous DMA, or non-contiguous coherent DMA memory into userspace.
- `c4iw_allocate_pd` / `c4iw_deallocate_pd`: allocate and free PD IDs through the resource ID table and update PD statistics.
- `c4iw_query_device`, `c4iw_query_port`, `c4iw_query_gid`: fill RDMA core capability, port, and GID data from the lower-layer cxgb4 device and netdevs.
- Sysfs/stat helpers: `hw_rev_show`, `hca_type_show`, `board_id_show`, `c4iw_alloc_device_stats`, and `c4iw_get_mib`.
- `c4iw_dev_ops`: the central verbs operation table connecting CQ/QP/SRQ/MR/CM/resource-tracking callbacks from the rest of the driver.
- `c4iw_register_device` / `c4iw_unregister_device`: final RDMA device setup, netdev association, and registration lifecycle.

## Control Flow

Registration work sets node GUID/type, port count, completion vectors, parent PCI device, and iWARP interface name, installs `c4iw_dev_ops`, associates each RDMA port with its Ethernet netdev, raises the PCI DMA segment limit, then calls `ib_register_device`. Failure after setup calls `c4iw_dealloc(ctx)` to unwind the Chelsio device context.

User context creation initializes queue-ID sharing lists and mmap state. If userspace is old and cannot receive the status page response, the driver disables status-page support globally; otherwise it allocates an mmap entry, reserves a key, copies the response, and queues a mapping to the physical status page. `c4iw_mmap` later removes exactly one matching mapping and dispatches by `mmap_flag`, so mmap entries are consumed when mapped.

Capability queries are mostly read-only projections of `rdev->lldi`, hardware queue limits, firmware version, and module parameters. PD allocation uses the generic resource table and writes the PDID to userspace when requested.

## State and Persistence Behavior

Persistent state lives in `struct c4iw_dev`, `struct c4iw_rdev`, per-ucontext mmap lists, RDMA core object wrappers, and the low-level driver information (`lldi`). Mmap keys monotonically advance per user context. PD/current/max counters are protected by `rdev->stats.lock`; mmap list operations use `ucontext->mmap_lock`. The file does not persist data beyond kernel memory, but it defines the ABI-visible uverbs response fields and sysfs/stat output.

## Dependencies and Integration Points

This file integrates Linux RDMA core (`ib_device_ops`, uverbs, resource tracking, iWARP CM), netdev/ethtool helpers, cxgb4 lower-layer APIs (`cxgb4_get_tcp_stats`, `ib_get_eth_speed`, BAR mappings), and driver-local helpers from `iw_cxgb4.h`. It depends on `resource.c` for PD/QID allocation, `qp.c`/CQ/MR/CM files for operation callbacks, and the user ABI structs consumed by libcxgb4.

## Risks and Edge Cases

- `c4iw_alloc_ucontext` sets `T4_STATUS_PAGE_DISABLED` on the shared rdev when one old userspace process connects, affecting later contexts.
- `c4iw_mmap` frees the mmap entry before the actual remap call; failed mmap attempts cannot be retried with the same key.
- `c4iw_query_gid` rejects port zero but otherwise trusts the caller-provided port index when indexing `ports[port - 1]`.
- Device stats are marked with a FIXME because TCP MIB counters look port-scoped but are exported through device stats.
- The `rhp = (struct c4iw_dev *)ibdev` cast in PD allocation assumes `struct c4iw_dev` embeds `ib_device` at offset zero or matches historical layout; most other code uses `to_c4iw_dev`.

## Test Signals

Build coverage should verify every callback in `c4iw_dev_ops` matches the RDMA core signatures. Runtime smoke tests should cover device registration/unregistration, `ibv_query_device`, `ibv_query_port`, PD alloc/dealloc, old and new ucontext responses, mmap of queue/status/BAR entries, and sysfs/stat reads. Negative tests should exercise malformed mmap keys, undersized udata, invalid ports, and registration failure after netdev association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/provider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/qp.c

## Purpose

`qp.c` implements Chelsio iWARP queue pair and shared receive queue lifecycle, work request construction, posting, doorbell ringing, QP state transitions, RDMA init/fini/terminate firmware messages, drain completions, and error flushing. It is the main bridge between RDMA core verbs (`create_qp`, `post_send`, `modify_qp`, SRQ verbs) and T4/T5/T6 firmware work request formats.

## Important APIs, Types, and Functions

- Module parameters: `db_delay_usecs`, `ocqp_support`, `db_fc_threshold`, `db_coalescing_threshold`, and `max_fr_immd` tune doorbell and fast-registration behavior.
- Queue allocation: `alloc_sq`, `alloc_oc_sq`, `alloc_host_sq`, `create_qp`, `destroy_qp`, `alloc_srq_queue`, and `free_srq_queue`.
- Work request builders: `build_immd`, `build_isgl`, `build_rdma_send`, `build_rdma_write`, `build_rdma_read`, `build_memreg`, `build_tpte_memreg`, `build_inv_stag`, `build_rdma_recv`, and `build_srq_recv`.
- Fast path: `post_write_cmpl` coalesces a WRITE plus SEND/SEND_WITH_INV chain into one firmware `RDMA_WRITE_CMPL` WR for NVMe-oF-style responses.
- Posting APIs: `c4iw_post_send`, `c4iw_post_receive`, `c4iw_post_srq_recv`.
- QP state/control: `c4iw_modify_qp`, `c4iw_ib_modify_qp`, `rdma_init`, `rdma_fini`, `post_terminate`, `flush_qp`, and `__flush_qp`.
- SRQ support: `c4iw_create_srq`, `c4iw_destroy_srq`, `c4iw_modify_srq`, `c4iw_copy_wr_to_srq`, and deferred pending WR handling for out-of-order SRQ consumption.

## Control Flow

QP creation validates RC-only semantics, CQ handles, inline/WR limits, and optional SRQ use. It sizes SQ/RQ rings with an extra empty slot and status entries, allocates a firmware wait object, obtains QIDs/RQT memory, allocates host or on-chip SQ memory, allocates RQ memory when needed, resolves BAR2 doorbell addresses, and posts `FW_RI_RES_WR` resource commands. For userspace QPs it also returns queue IDs, sizes, flags, and mmap keys for SQ/RQ memory and doorbells.

Posting send WRs takes the QP spinlock, handles already-flushed QPs by generating software drain CQEs, checks SQ capacity, optionally takes the write-completion coalescing fast path, then builds one firmware WR per IB WR. It records a shadow `t4_swsqe`, initializes the firmware header, advances ring indices, and rings the SQ doorbell directly or through doorbell flow-control deferral. Receive posting mirrors this for RQ or SRQ rings and tracks wr_id metadata in software arrays.

QP modification is a mutex-protected state machine. IDLE can update RDMA attributes or transition to RTS via `rdma_init`. RTS can close, terminate, or error, sending FINI/TERMINATE and disconnecting the endpoint as needed. ERROR can return to IDLE only after SQ/RQ are empty. Error paths disassociate the endpoint, mark queues in error, flush CQs, and wake destroy waiters.

## State and Persistence Behavior

Persistent per-QP state includes hardware QIDs, DMA queue memory, BAR2 doorbell mapping, software SQ/RQ shadows, QP attributes, endpoint pointer/refcount, wait queues, and resource-tracking xarray membership. Firmware-visible state persists in Chelsio queue contexts and RI connection state until reset/fini/destroy commands complete. Doorbell state may be deferred in `db_fc_list` when the adapter status page reports doorbells off. SRQs maintain normal ring indices plus pending and out-of-order counters.

## Dependencies and Integration Points

The file depends on `t4.h` ring helpers and CQE macros, `t4fw_ri_api.h` firmware layouts, `resource.c` QID/RQT/OCQP allocation, CQ flush/count helpers, MR invalidation/access conversion, endpoint/CM code for LLP connection ownership, and RDMA core uverbs structures. It integrates with userspace through mmap entries prepared here and consumed by `provider.c`.

## Risks and Edge Cases

- The unwind path under `err_free_rq_db_key` has an unbraced duplicated `kfree(rq_db_key_mm)`, causing a double free when no SRQ is used.
- `build_rdma_read` sets dummy STAG 2 for zero-length reads; tests should confirm firmware and MR semantics accept that sentinel.
- Several builders write directly into circular DMA queues and only some variable-length regions handle wraparound; fixed header size assumptions are enforced for write-completion WRs but should remain guarded.
- `c4iw_post_send` accesses `wr->sg_list[0]` in some opcode paths and fast-path predicates; zero-SGE edge cases need coverage.
- User QP flushing cannot snapshot user queue state, so it marks CQ/QP error and relies on userspace to observe error state rather than generating per-WR flush CQEs.
- Doorbell flow-control paths split locking between xarray lock and QP lock; lock ordering must remain consistent with adapter DB recovery code.

## Test Signals

Tests should cover QP create/destroy for kernel, userspace, SRQ, and on-chip SQ paths; mmap key creation; post-send opcodes including SEND, WRITE, WRITE_WITH_IMM, READ, READ_WITH_INV, REG_MR, LOCAL_INV, and write-completion coalescing; RQ/SRQ posting with wraparound; state transitions IDLE/RTS/CLOSING/TERMINATE/ERROR; flush/drain CQE generation; doorbell-off deferral; resource unwind injection; and RDMA CM connect/disconnect integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/resource.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/resource.c

## Purpose

`resource.c` provides local resource allocation for the cxgb4 iWARP driver. It manages ID tables for TPT/STag, QP/CQ queue IDs, PD IDs, and SRQ indices, plus generic-allocator pools for adapter PBL memory, RQT memory, and on-chip QP memory.

## Important APIs, Types, and Functions

- `c4iw_init_resource` / `c4iw_destroy_resource`: initialize and free resource ID tables.
- `c4iw_get_resource` / `c4iw_put_resource`: thin wrappers around driver ID allocation that use zero as the public failure sentinel.
- `c4iw_get_cqid`, `c4iw_put_cqid`, `c4iw_get_qpid`, `c4iw_put_qpid`: allocate QIDs while sharing groups of IDs that map to one doorbell/GTS page.
- Pool allocators: `c4iw_pblpool_alloc/free/create/destroy`, `c4iw_rqtpool_alloc/free/create/destroy`, and `c4iw_ocqp_pool_alloc/free/create/destroy`.
- SRQ index APIs: `c4iw_alloc_srq_idx` and `c4iw_free_srq_idx`.

## Control Flow

Resource initialization allocates the TPT table with randomization, builds a QID table from the adapter virtual resource window while freeing IDs that do not align with `qpmask`, then creates PDID and SRQ tables. CQID/QPID allocation first tries the per-ucontext cached list. If empty, it allocates a base QID from the global table, accounts the whole `qpmask + 1` group, and populates both CQ and QP lists because all IDs in the group share one doorbell page.

PBL, RQT, and OCQP pools are Linux `gen_pool` regions backed by adapter virtual-resource address ranges. Creation attempts to add the full range and halves chunks on failure until a minimum threshold; allocation/free update stats and, for PBL/RQT, hold a kref so pool destruction waits until outstanding allocations are returned.

## State and Persistence Behavior

ID tables persist for the rdev lifetime. QID leftovers persist in per-ucontext `cqids` and `qpids` lists protected by `uctx->lock`. Pool allocations return adapter-relative addresses used in firmware resource commands, not CPU pointers. Usage/failure/max counters persist in `rdev->stats` under `stats.lock`. PBL and RQT pool destruction is reference-counted and completes via `pbl_compl`/`rqt_compl`; OCQP destruction directly destroys the pool.

## Dependencies and Integration Points

The file depends on driver ID-table helpers from `iw_cxgb4.h`, Linux `genalloc`, and low-level virtual resource descriptors in `rdev->lldi.vr`. `qp.c` consumes QIDs, RQT memory, SRQ indices, and OCQP memory; MR code consumes PBL pool allocations; `provider.c` consumes PDIDs.

## Risks and Edge Cases

- `c4iw_get_cqid` and `c4iw_get_qpid` can partially populate per-ucontext lists if `kmalloc` fails after a base QID is allocated, returning a QID while not caching the full group.
- QID stats increment by `qpmask + 1` when a base group is allocated but do not appear to decrement when cached IDs are later recycled to lists; stats are high-water/resource-use indicators, not exact global table occupancy.
- `c4iw_destroy_resource` frees TPT/QID/PDID tables but omits `srq_table`, which may leak table storage or rely on a separate lifecycle not visible in this file.
- Pool create functions may return success after only part of a hardware range is added, trading capacity for probe success.
- Address arithmetic uses 32-bit `unsigned` for virtual resource windows; larger adapter windows would need audit.

## Test Signals

Exercise power-of-two and zero SRQ resource initialization, QID allocation/free across multiple ucontexts, allocation failure in the middle of group-list population, PBL/RQT/OCQP exhaustion and stats, pool create with fragmented add failures, kref-delayed destroy while allocations are outstanding, and SRQ index allocation/free with unsupported SRQ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/restrack.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/restrack.c

## Purpose

`restrack.c` exports cxgb4 driver-specific RDMA resource information through RDMA netlink resource tracking. It snapshots kernel QP, CQ, CM ID, and MR state into nested `RDMA_NLDEV_ATTR_DRIVER` attributes for diagnostics and tooling.

## Important APIs, Types, and Functions

- QP dump helpers: `fill_sq`, `fill_rq`, `fill_swsqe`, `fill_swsqes`, and `c4iw_fill_res_qp_entry`.
- CM dump: `c4iw_fill_res_cm_id_entry`, including listen endpoint and connected endpoint variants.
- CQ dump helpers: `fill_cq`, `fill_cqe`, `fill_hwcqes`, `fill_swcqes`, and `c4iw_fill_res_cq_entry`.
- MR dump: `c4iw_fill_res_mr_entry`, which reads the hardware TPTE with `cxgb4_read_tpte`.
- `union union_ep`: temporary storage large enough to copy either endpoint type while dropping the endpoint mutex before netlink emission.

## Control Flow

QP and CQ dumps skip userspace objects because their producer/consumer state is not available in kernel memory. Kernel QP dumping starts a driver netlink nest, takes the QP lock, copies the `t4_wq` and first/last pending SQEs, releases the lock, then emits SQ, selected SQE, and RQ fields. CQ dumping similarly snapshots the CQ and selected hardware/software CQEs under the CQ lock.

CM ID dumping resolves the iWARP CM ID, checks provider data, allocates temporary storage, copies the endpoint under `epcp->mutex`, and emits common state/flags/history plus listen-specific `stid/backlog` or connection-specific `hwtid/ord/ird/emss/atid`.

MR dumping opens a driver nest, reads the firmware TPTE for the MR's STAG, and decodes validity, key, state, PDID, permissions, page size, length, and PBL address.

## State and Persistence Behavior

This file does not mutate RDMA resources except for transient allocation and netlink skb construction. It deliberately snapshots state under the relevant spinlock/mutex and emits from the copy to avoid long lock hold times. Hardware TPTE state is read live, so MR output reflects current adapter state rather than only software shadow state.

## Dependencies and Integration Points

It depends on RDMA resource tracking callbacks installed in `provider.c`, RDMA netlink driver attribute helpers, `rdma_iw_cm_id`, Chelsio endpoint/QP/CQ/MR structures, `t4.h` CQE/TPTE macros, and `cxgb4_read_tpte`. It is diagnostic-only but valuable for production support and CI failure triage.

## Risks and Edge Cases

- `c4iw_fill_res_mr_entry` returns `0` on TPTE read error without cancelling the already-started netlink nest, which can produce malformed or incomplete nested output.
- Snapshotting first/last CQEs assumes queue indices are valid; corrupted CQ state can still index queue arrays before emitting.
- User QPs/CQs are skipped, so resource reports can look incomplete on uverbs-heavy workloads.
- CM provider data is copied based on state after casting from common endpoint; layout assumptions must match `struct c4iw_listen_ep` and `struct c4iw_ep`.
- All helpers return `-EMSGSIZE` on netlink append failure, so callers should be tested with small skb limits.

## Test Signals

Run `rdma res show` style coverage for kernel QPs, CQs, MRs, and CM IDs; verify user objects are skipped intentionally; test small-skb error paths; inject TPTE read failure; race resource dumps with QP/CQ progress and CM transitions; and validate emitted field names remain stable for diagnostic consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/restrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4.h

## Purpose

`t4.h` defines Chelsio T4/T5/T6 RDMA queue, CQE, status-page, work-request, and ring-management primitives used by the cxgb4 iWARP driver. It is the shared low-level contract between QP/CQ/SRQ code and firmware work request layouts from `t4fw_ri_api.h`.

## Important APIs, Types, and Functions

- Limits and sizing macros: `T4_MAX_*`, `T4_EQ_ENTRY_SIZE`, SQ/RQ slot counts, inline/SGL depth calculations, and page-size masks.
- Firmware WR unions: `union t4_wr` and `union t4_recv_wr` overlay all supported send/receive/status work request formats.
- CQE support: `struct t4_cqe`, CQE status/opcode/type/gen macros, `struct t4_swsqe`, and error code constants.
- Queue state: `struct t4_sq`, `struct t4_rq`, `struct t4_wq`, `struct t4_srq`, `struct t4_cq`, and status-page structures.
- Ring helpers: `t4_sq_produce/consume`, `t4_rq_produce/consume`, `t4_srq_*`, `t4_swcq_*`, `t4_hwcq_consume`, and CQ polling helpers.
- Doorbells: `pio_copy`, `t4_ring_sq_db`, `t4_ring_rq_db`, `t4_ring_srq_db`, `write_gts`, and `t4_arm_cq`.

## Control Flow

Producer helpers update software `in_use`, producer indices, host work-queue indices, and status-page fields, wrapping by queue size. Doorbell helpers first issue `wmb()` to make queue writes visible, then either copy a single 64-byte WR through the write-combining BAR2 doorbell path, write a BAR2 kernel doorbell, or fall back to the legacy doorbell register. CQ helpers validate hardware CQEs by generation bit, detect overflow by comparing the previous CQE timestamp/generation snapshot, consume CQEs with periodic GTS updates, and arm completion interrupts with accumulated consumer increments.

## State and Persistence Behavior

All structures are in-memory shadows of hardware queues and status pages. Queue `pidx/cidx/wq_pidx/in_use` fields persist for the object lifetime and must stay synchronized with hardware-visible queue memory. Status-page bytes such as `qp_err`, `db_off`, host indices, and SRQ index are shared with firmware/hardware. CQ `gen`, `bits_type_ts`, `cidx_inc`, and `flags` drive completion validity and interrupt moderation.

## Dependencies and Integration Points

The header includes adapter register/value definitions, RI firmware API structures, and Linux DMA/MMIO primitives. `qp.c`, CQ code, resource tracking, and MR code all consume its layouts. User mmap paths expose parts of the queue/status memory whose layout is defined here, so changes are ABI-sensitive.

## Risks and Edge Cases

- Ring helpers assume callers have already checked capacity; underflow/overflow corrupts indices and hardware-visible status fields.
- Doorbell paths depend on memory barriers and BAR2 capability detection; missing barriers can produce hardware fetches of incomplete WRs.
- `t4_next_hw_cqe` marks CQ error on overflow and suppresses future CQEs; recovery paths must flush affected QPs.
- `t4_set_wq_in_error` writes through pointers configured differently for normal QP versus SRQ-backed QP; create paths must initialize them before errors can occur.
- Inline WR size macros depend on packed firmware struct sizes; firmware ABI layout changes can silently lower real capacity if tests do not cover BUILD_BUG-style checks.

## Test Signals

Unit-style ring tests should cover wraparound, full/empty boundaries, SRQ pending/out-of-order counters, CQ generation flips, CQ overflow detection, and CQ arm batching. Hardware tests should verify BAR2 write-combining and non-BAR2 doorbells, status-page doorbell-off handling, CQ interrupt arming, and user mmap ABI compatibility for status pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4fw_ri_api.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4fw_ri_api.h

## Purpose

`t4fw_ri_api.h` is the Chelsio firmware ABI definition for RDMA/iWARP resource and data-path work requests. It defines RI opcodes, flags, MPA/QP capabilities, memory permissions, STag/TPTE bitfields, resource WRs for SQ/RQ/CQ/SRQ contexts, send/write/read/recv/bind/fast-register/invalidate WR layouts, and RDMA init/fini/terminate messages.

## Important APIs, Types, and Definitions

- Opcode and flag enums: `fw_ri_wr_opcode`, `fw_ri_wr_flags`, `fw_ri_mpa_attrs`, `fw_ri_qp_caps`, `fw_ri_addr_type`, `fw_ri_mem_perms`, `fw_ri_stag_type`, `fw_ri_data_op`, and `fw_ri_sgl_depth`.
- Data segment formats: `fw_ri_dsgl`, `fw_ri_isgl`, `fw_ri_immd`, `fw_ri_sge`, and DSGL pair structures.
- TPTE definition: `struct fw_ri_tpte` and `FW_RI_TPTE_*` masks for validity, key, state, type, PDID, permissions, page size, QPID, PBL address, DCA, and MW bind count.
- Resource WRs: `struct fw_ri_res`, `struct fw_ri_res_wr`, and `FW_RI_RES_WR_*` fields for queue context creation/reset.
- Data-path WRs: `fw_ri_rdma_write_wr`, `fw_ri_send_wr`, `fw_ri_rdma_write_cmpl_wr`, `fw_ri_rdma_read_wr`, `fw_ri_recv_wr`, `fw_ri_bind_mw_wr`, `fw_ri_fr_nsmr_wr`, `fw_ri_fr_nsmr_tpte_wr`, and `fw_ri_inv_lstag_wr`.
- Connection control: `struct fw_ri_wr` with INIT, FINI, and TERMINATE union payloads.

## Control Flow

The header has no executable control flow. Its structures are populated by `qp.c` when creating resources, posting RDMA operations, registering memory, and moving a connection into or out of RI mode. The firmware consumes these big-endian fields from DMA queues or skb control messages and returns CQEs defined in `t4.h`.

## State and Persistence Behavior

The definitions describe firmware-persistent state: queue contexts, TPTE memory registrations, QP RDMA capabilities, ORD/IRD limits, MPA attributes, and connection sequence numbers. Bitfield macros are used both to program firmware and to decode live TPTE state in resource tracking.

## Dependencies and Integration Points

This header depends on `t4fw_api.h` for common firmware WR fields and is included by `t4.h`. It is tightly coupled to Chelsio firmware, endian conversion in call sites, RDMA core operation mapping in `qp.c`, MR registration code, and diagnostic decoding in `restrack.c`.

## Risks and Edge Cases

- This is ABI-sensitive: field order, sizes, and bit positions must match firmware exactly.
- Some macro definitions are duplicated (`FW_RI_TPTE_PS_S`, `FW_RI_RES_WR_IQESIZE_G`) in this source snapshot; duplicate identical defines are benign for preprocessing but indicate generated-header drift.
- Several structures use flexible arrays and overlays; builders must compute `len16` precisely and ensure fixed headers fit in queue slots.
- `FW_RI_WRITE_IMMEDIATE` aliases `FW_RI_RDMA_INIT`, so opcode interpretation depends on context.
- TPTE permission/page-size/key fields are manually composed by callers; invalid combinations can create memory protection bugs that firmware may reject only asynchronously.

## Test Signals

Compile-time layout checks should cover struct sizes, offsets used by queue builders, and maximum inline/SGL calculations. Integration tests should post each WR type, create/reset SQ/RQ/CQ/SRQ resources, fast-register with immediate and DSGL PBLs, decode TPTEs through resource tracking, and verify firmware rejects malformed lengths/flags without hanging queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4fw_ri_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Kconfig

## Purpose

`Kconfig` declares the Amazon Elastic Fabric Adapter RDMA driver configuration symbol `INFINIBAND_EFA`. It controls whether the EFA provider is built into the kernel, built as `efa.ko`, or omitted.

## Important APIs, Types, and Functions

- `config INFINIBAND_EFA`: tristate user-visible option labelled "Amazon Elastic Fabric Adapter (EFA) support".
- Dependencies: `PCI_MSI`, `64BIT`, little-endian CPU, and `INFINIBAND_USER_ACCESS`.
- Help text: documents that the module name is `efa`.

## Control Flow

There is no runtime control flow. During kernel configuration, this symbol is available only when MSI-capable PCI, 64-bit little-endian architecture, and RDMA userspace access support are enabled. Kbuild then uses the symbol in the EFA Makefile to include or exclude the driver object.

## State and Persistence Behavior

The selected tristate value persists in the kernel `.config` and determines build artifacts. It does not create runtime state by itself.

## Dependencies and Integration Points

This file integrates with the RDMA subsystem Kconfig tree and `drivers/infiniband/hw/efa/Makefile`. The architecture constraints match EFA's userspace/DMA ABI expectations and the generated admin headers' little-endian bitfield use.

## Risks and Edge Cases

- The `!CPU_BIG_ENDIAN` dependency prevents accidental builds on big-endian systems where admin and queue formats are not supported.
- Missing `INFINIBAND_USER_ACCESS` disables the driver even if kernel-only users might exist, reflecting EFA's uverbs-oriented design.
- Kconfig does not explicitly depend on PCI itself here; it relies on `PCI_MSI` implying the needed PCI infrastructure in normal kernel configs.

## Test Signals

Build matrix checks should cover `n`, `m`, and `y` where dependencies are available, verify `efa.ko` is produced for module builds, and confirm the option is hidden on big-endian, non-64-bit, or no-PCI-MSI configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Makefile

## Purpose

`Makefile` wires the EFA driver into Kbuild. It declares the composite `efa` object and the source objects that form the module or built-in driver.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_INFINIBAND_EFA) += efa.o`: builds the driver only when the Kconfig symbol is enabled.
- `efa-y := efa_com_cmd.o efa_com.o efa_main.o efa_verbs.o`: lists the communication command wrappers, admin queue core, PCI/main driver, and verbs implementation objects.

## Control Flow

Kbuild evaluates the `CONFIG_INFINIBAND_EFA` tristate. For `m`, the listed objects are linked into `efa.ko`; for `y`, they are linked into the kernel image; for `n`, nothing in this directory is built.

## State and Persistence Behavior

The file has no runtime state. It persists build composition and therefore affects which symbols and init/exit paths are present in the final kernel/module.

## Dependencies and Integration Points

It depends on the corresponding `Kconfig` symbol and on the source files named in `efa-y`. Header-only files in this subset are included transitively by those objects rather than listed here.

## Risks and Edge Cases

- Adding a new EFA source file without updating `efa-y` can leave code unbuilt.
- Renaming generated admin command or communication files requires synchronized Makefile updates.
- Object order is normally not significant here, but init/exit symbol availability still depends on all objects being linked into the composite.

## Test Signals

Run kernel/module builds with EFA enabled, inspect that `efa_com_cmd.o`, `efa_com.o`, `efa_main.o`, and `efa_verbs.o` are linked, and confirm no stale object names remain after file moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa.h

## Purpose

`efa.h` is the main internal header for the Amazon EFA RDMA driver. It defines driver constants, device/object wrapper structures, statistics, IRQ/EQ state, and function prototypes for the verbs, mmap, address-handle, memory-registration, query, and stats operations implemented by the EFA driver.

## Important APIs, Types, and Functions

- Constants: `DRV_MODULE_NAME`, `DEVICE_NAME`, IRQ naming limits, and MSI-X vector index layout.
- `struct efa_dev`: top-level RDMA/PXI device wrapper containing `ib_device`, `efa_com_dev`, PCI BAR metadata, IRQ vectors, device attributes, stats, EQ array, and interrupt-enabled CQ xarray.
- Object wrappers: `efa_ucontext`, `efa_pd`, `efa_mr`, `efa_cq`, `efa_qp`, `efa_ah`, and `efa_eq`.
- `struct efa_stats`: atomic error/keepalive counters used by device stats.
- Function prototypes: query, PD, QP, CQ, MR, ucontext, mmap, AH, QP modify, link-layer, and hardware stats entry points.

## Control Flow

The header has no executable control flow. It defines the object model used when RDMA core allocates embedded driver objects via `ib_device_ops`; operation implementations cast from `ib_*` objects to these wrappers and call EFA admin commands through `efa_com_cmd.h`/`efa_com`.

## State and Persistence Behavior

`efa_dev` persists for the PCI device lifetime. User contexts store a UAR number. PDs store a device PD number. CQs own DMA or umem-backed completion memory plus mmap entries and optional EQ association. QPs own RQ DMA memory, doorbell/LLQ mmap entries, admin `qp_handle`, capacities, and software `state`. MRs retain `ib_umem` and optional interconnect IDs returned by firmware. Stats are atomic64 and intended for concurrent updates from verbs/error paths and async keepalive handling.

## Dependencies and Integration Points

The header depends on Linux PCI/interrupt APIs, RDMA core/uverbs ABI (`rdma/efa-abi.h`, `ib_verbs.h`), and EFA admin command wrappers. It is included by EFA main, verbs, communication command, and interrupt code. Userspace-visible mmap entries and response fields must remain coordinated with the EFA userspace ABI.

## Risks and Edge Cases

- Structure fields such as mmap entries and DMA buffers encode ownership contracts; destroy paths must release every optional entry exactly once.
- `efa_qp.state` is a software IB state cache and must stay consistent with firmware state transitions issued by admin commands.
- `cqs_xa` stores only interrupt-enabled CQs, so lookup code must not assume all CQs are present.
- Atomic stats avoid locking but provide no grouping consistency across counters.
- BAR address/length fields must be validated by PCI probe before use by mmap and doorbell paths.

## Test Signals

Compile all EFA objects after RDMA core signature changes, create/destroy each RDMA object type, exercise CQ interrupt and polling modes, map/free all mmap entry types, verify stats increments on failure paths, and run ABI tests with rdma-core EFA userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_cmds_defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_cmds_defs.h

## Purpose

`efa_admin_cmds_defs.h` defines the EFA admin command ABI: command opcodes, feature IDs, QP states/types, stats formats, command and response payloads for QP/CQ/MR/PD/UAR/AH/EQ operations, feature get/set payloads, AENQ groups, MMIO read response format, host-info format, and bit masks for packed fields.

## Important APIs, Types, and Definitions

- Version/opcode enums: `EFA_ADMIN_API_VERSION_*`, `efa_admin_aq_opcode`, `efa_admin_aq_feature_id`, QP type/state, stats type/scope, AENQ groups, and OS type.
- QP ABI: `efa_admin_create_qp_cmd/resp`, `modify_qp`, `query_qp`, and `destroy_qp` structures plus create/modify masks.
- Address and memory: AH create/destroy, `reg_mr`, `dereg_mr`, `alloc_mr`, interconnect ID validity, and permission/page-size masks.
- CQ/EQ ABI: create/destroy CQ and EQ command/response structures with doorbell offsets, sub-CQ depth, UAR, interrupt, and event-bitmask fields.
- Feature/stats ABI: device attributes, queue attributes, network attributes, AENQ config, event queue attributes, hardware hints, and basic/messages/RDMA/network stats.
- Host/MMIO: `efa_admin_mmio_req_read_less_resp` and `efa_admin_host_info`.

## Control Flow

The header has no runtime control flow. Command wrapper code fills these structures, submits them through `efa_com_cmd_exec`, and decodes completion responses. Feature descriptors are retrieved during probe and govern later verbs limits and capabilities.

## State and Persistence Behavior

The structures define firmware-persistent resources: QP handles/numbers/state, PD/UAR IDs, AH handles, lkey/rkey registrations, CQ/EQ indices, doorbell offsets, feature capabilities, and stats counters. Host info persists in firmware after a set-feature command. Packed masks define stable ABI bits and must remain synchronized with firmware.

## Dependencies and Integration Points

It depends on common admin queue descriptors from `efa_admin_defs.h`, memory address structures from `efa_common_defs.h`, and `GENMASK`/`BIT` macros. It is consumed by `efa_com.c` for EQ commands, `efa_com_cmd.*` for most admin command wrappers, `efa_verbs.*` for RDMA object operations, and userspace ABI translation paths.

## Risks and Edge Cases

- This snapshot contains duplicate named fields (`aq_common_desc` in `efa_admin_create_ah_cmd` and `page_size_cap` in `efa_admin_feature_device_attr_desc`), which would be compile-blocking in C unless repaired or generated differently.
- ABI structs include many MBZ/reserved fields; callers must zero-initialize commands before filling fields.
- Feature evolution is sparse (`QUEUE_ATTR_2` jumps to ID 9), so code must check supported feature bits before using newer descriptors.
- MR registration supports physical mode only for privileged clients; command wrappers must enforce privilege and PBL shape.
- Large MR and indirect PBL support depends on control-buffer descriptors and page-list chaining, which are easy to size incorrectly.

## Test Signals

Build tests should catch duplicate field names and layout drift. ABI tests should validate command sizes, offsets, and masks against firmware documentation. Runtime tests should cover create/query/modify/destroy QP, CQ/EQ lifecycle, MR registration variants, stats scopes/types, feature probing/fallback, AENQ configuration, host info set, and negative firmware responses for unsupported or malformed commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_cmds_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_defs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_defs.h

## Purpose

`efa_admin_defs.h` defines EFA admin, async event, and event queue descriptor formats shared by admin command code and hardware queues. It covers common AQ/ACQ descriptors, control-buffer descriptors, AENQ entries, EQ completion events, completion statuses, and masks for phase/opcode/event fields.

## Important APIs, Types, and Definitions

- `enum efa_admin_aq_completion_status`: firmware completion status codes and their semantic categories.
- Admin queue descriptors: `efa_admin_aq_common_desc`, `efa_admin_ctrl_buff_info`, `efa_admin_aq_entry`, `efa_admin_acq_common_desc`, and `efa_admin_acq_entry`.
- Async events: `efa_admin_aenq_common_desc` and `efa_admin_aenq_entry`.
- Event queues: `efa_admin_eqe_event_type`, `efa_admin_comp_event`, and `efa_admin_eqe`.
- Masks: command ID, phase, control data, control data indirect, AENQ phase, EQE phase, and EQE event type.

## Control Flow

The header has no executable code. `efa_com.c` uses phase bits in ACQ/AENQ/EQE descriptors to decide which entries hardware has produced, uses command IDs to match completions to outstanding contexts, and uses control-buffer descriptors for commands that require payloads larger than inline AQ space.

## State and Persistence Behavior

Descriptor fields live in coherent DMA rings shared with the device. Producer/consumer counters and phase bits in `efa_com` structures interpret these descriptors. Control buffer descriptors may point directly to DMA payloads or to indirect page-list chunks, so they are part of command lifetime and DMA mapping state.

## Dependencies and Integration Points

It depends on `efa_common_mem_addr` from common definitions and Linux bit macros. It is included by `efa_com.h` and command definition headers. Hardware, firmware, `efa_com_cmd_exec`, AENQ interrupt handling, and EQ interrupt handling all rely on these layouts.

## Risks and Edge Cases

- Phase-bit handling requires DMA read barriers before reading the rest of an entry; consumers must not bypass the pattern used in `efa_com.c`.
- Command IDs are only 12 bits, with low bits used for completion-context indexing; queue depth must remain compatible with that encoding.
- Control-buffer indirect chaining has no helper in this header, so wrapper code must validate lengths and DMA addresses carefully.
- Unknown completion statuses collapse to generic `-EINVAL` in `efa_com.c`, potentially hiding firmware-specific diagnostics unless extended status is logged elsewhere.

## Test Signals

Tests should validate descriptor sizes, phase wrap behavior, command ID masking, direct and indirect control-buffer commands, AENQ/EQE parsing, and status-to-errno mapping in the communication layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_admin_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.c

## Purpose

`efa_com.c` implements the EFA communication layer around device MMIO registers, admin submission/completion queues, asynchronous event queue, event queues, admin command execution, version/DMA capability validation, and device reset. It is the low-level command transport used by EFA probe and verbs command wrappers.

## Important APIs, Types, and Functions

- MMIO readless path: `efa_com_mmio_reg_read_init`, `efa_com_reg_read32`, `efa_com_mmio_reg_read_destroy`.
- Admin queue lifecycle: `efa_com_admin_init`, `efa_com_admin_destroy`, `efa_com_admin_init_sq`, `efa_com_admin_init_cq`, and `efa_com_admin_init_aenq`.
- Command contexts: `efa_comp_ctx`, `efa_com_alloc_comp_ctx`, `efa_com_dealloc_comp_ctx`, and command ID mapping helpers.
- Command execution: `efa_com_cmd_exec`, `efa_com_submit_admin_cmd`, `__efa_com_submit_admin_cmd`, `efa_com_wait_and_process_admin_cq`, and polling/interrupt wait variants.
- Interrupt/event handling: `efa_com_admin_q_comp_intr_handler`, `efa_com_aenq_intr_handler`, `efa_com_eq_comp_intr_handler`, and `efa_com_arm_eq`.
- Device control: `efa_com_validate_version`, `efa_com_get_dma_width`, `efa_com_dev_reset`, `efa_com_eq_init`, and `efa_com_eq_destroy`.

## Control Flow

Admin init first verifies device-ready status through the MMIO readless register path, sets queue depth and polling mode, initializes completion contexts and semaphore capacity, allocates coherent ASQ/ACQ/AENQ rings, programs their base/capability registers, unmasks admin interrupts, reads timeout capability, and marks the queue running.

`efa_com_cmd_exec` sleeps on the available-command semaphore, allocates a completion context, writes a command into the ASQ under the SQ lock, assigns a command ID that combines context index and producer-counter entropy, rings the producer doorbell, then waits for completion. Completion processing scans ACQ entries by phase bit under the CQ lock, validates command ID/status, copies the completion into the caller buffer, and completes the wait event unless polling mode is active. Timeouts clear the running bit to prevent further submissions.

AENQ/EQ interrupt handlers scan phase-valid entries, invoke registered callbacks, advance consumer counters/phase, and ring consumer/arm doorbells. Reset writes the reset reason to device control, restores the MMIO read response address, waits for reset-in-progress on/off, and refreshes admin timeout.

## State and Persistence Behavior

Persistent state includes coherent DMA rings for ASQ/ACQ/AENQ/EQs, completion context pool/status, queue producer/consumer counters, phase bits, admin running/polling state bits, semaphore slots, atomic admin stats, MMIO read response buffer/sequence number, and device DMA width. Hardware register programming persists until reset or device removal; reset clears MMIO response address and requires reprogramming.

## Dependencies and Integration Points

This file depends on EFA register definitions, admin descriptor/command definitions, DMA coherent allocation, completions, semaphores, spinlocks, MMIO `readl/writel`, and RDMA device logging. Higher-level command wrappers call `efa_com_cmd_exec`; PCI probe calls version/DMA/admin init and reset; IRQ handlers call the admin/AENQ/EQ handlers.

## Risks and Edge Cases

- `efa_com_alloc_ctx_id` assumes the semaphore prevents pool underflow/overflow; any caller bypassing `efa_com_cmd_exec` could corrupt `comp_ctx_pool_next`.
- `efa_com_admin_init` cleanup frees `comp_ctx` but not `comp_ctx_pool` on one error path, while destroy frees both; init failure paths need leak checks.
- The source contains duplicated statements (`comp_size` assignment and nested `if (err)`), harmless but a signal for generated-code review.
- Timeout paths clear the running bit, causing later commands to fail with `-ENODEV`; recovery must reset/reinitialize admin queues.
- MMIO readless polling busy-waits with `udelay(1)` up to 50 ms under a spinlock, serializing all register reads.
- EQ completion handler always arms the EQ even when no entries were processed; this is probably intentional but should be validated against interrupt moderation semantics.

## Test Signals

Tests should cover admin init/destroy success and each allocation failure path, command execution in polling and interrupt modes, missing MSI-X completion fallback, no-completion timeout, bad command ID completion, status-to-errno mapping, AENQ unknown group callback, EQ create/destroy/interrupt handling, MMIO read timeout/wrong-offset handling, version/DMA width validation, and reset timeout/error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.h

## Purpose

`efa_com.h` declares the EFA communication-layer data structures and APIs for admin queues, async event queues, MMIO readless register access, event queues, device reset/version/DMA validation, and admin command execution.

## Important APIs, Types, and Functions

- Admin queues: `efa_com_admin_sq`, `efa_com_admin_cq`, `efa_com_admin_queue`, state bits, and `efa_com_stats_admin`.
- Async/event queues: `efa_com_aenq`, `efa_aenq_handlers`, `efa_com_eq`, and callback typedefs.
- Device wrapper: `efa_com_dev` with admin/AENQ state, register BAR, DMA device, supported features, DMA width, and MMIO read state.
- EQ command parameters/results: `efa_com_create_eq_params`, `efa_com_create_eq_result`, and `efa_com_destroy_eq_params`.
- Public APIs: DMA address splitting, admin init/destroy, EQ init/destroy, reset, polling mode, admin/AENQ/EQ interrupt handlers, MMIO read init/destroy, version/DMA validation, and `efa_com_cmd_exec`.

## Control Flow

The header defines the call graph used by probe and verbs command code: initialize MMIO read response storage, validate device versions and DMA width, initialize admin/AENQ queues, execute admin commands, optionally create EQs, handle interrupts, reset on errors, and destroy queues during removal.

## State and Persistence Behavior

Admin queue counters, phase bits, completion contexts, semaphore availability, state bits, and stats persist in `efa_com_dev` for the device lifetime. AENQ and EQ consumer counters/phase persist per queue. MMIO read state serializes register reads with a sequence number and DMA response buffer. These structures are kernel-resident shadows of coherent DMA rings and hardware registers.

## Dependencies and Integration Points

It includes Linux delay/device/DMA/semaphore/scheduler headers, RDMA verbs logging context, common EFA admin and register definitions. It is consumed by `efa_com.c`, `efa_com_cmd.*`, EFA PCI probe/remove, IRQ setup, and verbs object creation paths.

## Risks and Edge Cases

- `EFA_MAX_HANDLERS` fixes AENQ handler table size; firmware event groups beyond 255 require ABI/header changes.
- Queue depths are expected to be powers of two by implementation masks in `efa_com.c`; callers should not pass arbitrary EQ depths.
- `efa_com_admin_queue.dmadev` and `efa_dev` are `void *`, so type safety is deferred to call sites.
- Polling mode state controls both interrupt masking and wait strategy; inconsistent state can cause missed completions or unnecessary polling.

## Test Signals

Build tests should catch API signature drift. Runtime tests should initialize/destroy admin and EQ structures, execute commands through `efa_com_cmd_exec`, toggle polling mode, process AENQ/EQ interrupts, validate callback dispatch, reset the device, and verify stats counters under command success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_com.h -->
