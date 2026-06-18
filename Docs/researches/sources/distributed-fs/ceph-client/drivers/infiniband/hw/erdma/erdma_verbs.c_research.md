<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c

## Purpose

This file implements the Alibaba Elastic RDMA provider's ib_verbs-facing operations. It handles device and port queries, protection domains, user contexts and mmap doorbells, queue pair and completion queue creation/destruction, memory registration, QP state transitions, RoCEv2 address handles, GID and pkey hooks, port events, MTU programming, and hardware stats. The implementation bridges RDMA core objects to ERDMA command queue requests and to PCI DMA resources.

## Important APIs, types, and functions

The main entry points are `erdma_alloc_ucontext()`, `erdma_dealloc_ucontext()`, `erdma_query_device()`, `erdma_query_port()`, `erdma_get_port_immutable()`, `erdma_alloc_pd()`, `erdma_create_qp()`, `erdma_destroy_qp()`, `erdma_modify_qp()`, `erdma_query_qp()`, `erdma_create_cq()`, `erdma_destroy_cq()`, `erdma_reg_user_mr()`, `erdma_get_dma_mr()`, `erdma_ib_alloc_mr()`, `erdma_map_mr_sg()`, `erdma_dereg_mr()`, `erdma_mmap()`, `erdma_add_gid()`, `erdma_del_gid()`, `erdma_create_ah()`, `erdma_destroy_ah()`, and `erdma_get_hw_stats()`.

Important internal helpers include `erdma_alloc_idx()` and `erdma_free_idx()` for bitmap-backed resource IDs, `create_qp_cmd()`, `create_cq_cmd()`, and `regmr_cmd()` for hardware command encoding, `get_mtt_entries()` and `put_mtt_entries()` for user memory translation tables, `erdma_map_user_dbrecords()` for shared doorbell record pinning, and `erdma_init_mod_qp_params_rocev2()` for converting RDMA core QP attributes to device masks.

## Control Flow

User context allocation increments `dev->num_ctx`, allocates either legacy BAR doorbells or extended doorbell pages through `CMDQ_OPCODE_ALLOC_DB`, inserts three RDMA mmap entries, and returns mmap offsets to userspace. `erdma_mmap()` later resolves those entries and maps the hardware doorbell page with device page protections. Deallocation removes mmap entries, frees extended doorbells, and decrements the context count.

QP creation validates capabilities and type support, reserves a QPN in `dev->qp_xa`, rounds queue depths to powers of two, then follows separate user and kernel setup paths. Kernel QPs allocate coherent SQ/RQ buffers, software WR tables, and DMA-pool doorbell records. User QPs pin the userspace queue buffer into SQ and RQ MTTs and map a userspace doorbell record page. `create_qp_cmd()` then posts the hardware create command with inline or one-level MTT addresses. CQ creation follows the same pattern: reserve CQN, initialize user MTT or kernel coherent memory, return userspace response data, then post `CMDQ_OPCODE_CREATE_CQ`.

MR registration pins user memory, computes page size and MTT entries, allocates an STAG, encodes access/type/page layout in `CMDQ_OPCODE_REG_MR`, and releases resources on any failure edge. Fast-registration MRs allocate a pre-sized MTT and are populated later by `erdma_map_mr_sg()`. QP modification serializes with `qp->state_lock`, validates RDMA core state rules for RoCEv2, maps IB states to ERDMA protocol states, and calls protocol-specific state transition helpers defined elsewhere.

## State and Persistence

State is in RDMA core objects, ERDMA private wrappers, xarrays, bitmaps, pinned `ib_umem`, DMA mappings, command-queue programmed hardware tables, and PCI BAR/doorbell resources. Nothing persists to disk. Resource ID bitmaps are protected by spinlocks. QP state transitions are protected by `state_lock`; QP lifetime uses `kref` plus `safe_free` completion. User doorbell record pages are tracked per context with a mutex and reference count so one pinned page can serve multiple QP/CQ records.

## Dependencies and Integration Points

The file depends on RDMA core (`ib_device`, `ib_pd`, `ib_qp`, `ib_cq`, `ib_umem`, uverbs copy helpers, RDMA mmap helpers, AH/GID helpers), Linux DMA and PCI APIs, xarray resource lookup, netdevice MTU/link helpers, IPv6 address helpers, and ERDMA hardware command definitions from local headers. It integrates with ERDMA CM for iWARP QP teardown, with `erdma_post_send()`, `erdma_post_recv()`, and `erdma_poll_cq()` declared in the header but implemented elsewhere, and with userspace ABI structs from `rdma/erdma-abi.h`.

## Risks

The highest-risk areas are resource unwind paths and hardware layout encoding. QP/CQ creation mixes xarray IDs, user pinned memory, DMA mappings, mmap offsets, and command queue state; a missing unwind can leak pinned pages or leave stale xarray entries. MTT code supports continuous and scatter multi-level tables, so page-size selection, high-count fields, and DMA unmap symmetry are critical. `alloc_db_resources()` appears to assign `ctx->cdb` from `rdb_off` and `ctx->rdb` from `cdb_off`, which should be treated as a review point against the hardware ABI. QP state validation is stricter for RoCEv2 than iWARP because iWARP state is largely delegated to connection-manager helpers. Destroy paths return early if hardware destroy commands fail, intentionally preserving software resources but making caller retry semantics important.

## Test Signals

Useful signals include `ibv_devinfo` capability output, uverbs context allocation and mmap tests, PD/QP/CQ/MR create-destroy stress with fault injection, kernel and userspace RC traffic, RoCEv2 UD/GSI AH creation, GID add/delete through netdevice address changes, FRMR map/unmap workloads, QP state transition tests, concurrent CQ/QP destroy during traffic, and hardware stats reads. Kernel logs should be checked for DMA mapping failures, command queue errors, refcount waits, leaked pinned pages, and WARNs from freeing unused resource bitmap IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c -->
