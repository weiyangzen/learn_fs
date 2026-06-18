# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.h

## Purpose

`qed_cxt.h` declares the context manager's public and internal contract: context lookup structures, TID memory views, dynamic ILT element types, exported initialization/allocation/CID APIs, ILT block layout structures, CID maps, SRC T2 metadata, and the top-level `struct qed_cxt_mngr` stored on each hardware function.

## Important APIs, Types, and Functions

- `struct qed_cxt_info` is an in/out lookup object containing the requested `iid`, resolved protocol `type`, and returned context pointer.
- `struct qed_tid_mem` returns storage-offload task memory geometry: task size, TIDs per block, page waste, and up to `MAX_TID_BLOCKS` block pointers.
- `enum qed_cxt_elem_type` identifies dynamic allocation targets: connection context, SRQ, task, and XRC SRQ.
- Public lifecycle APIs include `qed_cxt_mngr_alloc()`, `qed_cxt_tables_alloc()`, `qed_cxt_mngr_setup()`, and `qed_cxt_mngr_free()`.
- Hardware init APIs include `qed_cxt_cfg_ilt_compute()`, `qed_cxt_cfg_ilt_compute_excess()`, `qed_cxt_hw_init_common()`, `qed_cxt_hw_init_pf()`, `qed_qm_init_pf()`, and `qed_qm_reconf()`.
- Runtime APIs include CID acquire/release for PF and VF queues, protocol CID/TID count getters, dynamic ILT allocation/free, task context lookup, CDUT page count helpers, ILT page-size lookup, and total SRQ count lookup.
- Internal layout structures `qed_tid_seg`, `qed_conn_type_cfg`, `qed_ilt_cli_blk`, and `qed_ilt_client_cfg` model protocol resource counts and ILT client block boundaries.
- `struct qed_cxt_mngr` is the persistent owner of protocol config, ILT clients, task sizes, VF metadata, acquired CID bitmaps, ILT shadow, dynamic allocation mutex, SRC T2 metadata, SRQ counts, ARFS count, and cached size/page counters.

## Control Flow

The header defines the state graph used by `qed_cxt.c`: callers allocate a manager, set PF parameters, compute ILT layout, allocate tables, initialize hardware, and then acquire/release CIDs or dynamically allocate ILT entries as protocols run. Storage and RDMA call sites use the helper APIs to discover task memory, context pointers, and resource counts without knowing ILT client internals.

## State and Persistence Behavior

`struct qed_cxt_mngr` is a long-lived in-memory object, not a serialized artifact. It persists for the active `qed_hwfn` lifetime and is the only owner of allocated ILT/SRC/CID state. Its register values and DMA addresses are mirrored into hardware during init, but the structure itself is rebuilt on driver reload.

## Dependencies and Integration Points

The header depends on Linux types/slab, QED public interface types, hardware status/interface structures from `qed_hsi.h`, and core device definitions from `qed.h`. It is consumed by QED core initialization, slowpath, protocol offloads, RDMA, storage offloads, SR-IOV code, and DCBX/QM paths that need context or queue-manager resource counts.

## Risks and Edge Cases

- Constants such as `MAX_CONN_TYPES`, `TASK_SEGMENTS`, `ILT_CLI_PF_BLOCKS`, and CDUT block index macros must stay aligned with firmware protocol IDs and hardware register expectations.
- `struct qed_tid_mem` has a fixed `MAX_TID_BLOCKS`; callers rely on implementation-side line counts not exceeding it.
- The manager exposes many fields directly to implementation files, so layout changes are cross-cutting and can affect allocation, hardware programming, and teardown.
- `dynamic_line_offset` is present in `qed_ilt_cli_blk` but not central in the observed implementation; future users need to distinguish it from `dynamic_line_cnt`.

## Test Signals

Build coverage is the main signal for declaration consistency. Runtime validation comes from probe initialization across personalities, SR-IOV configurations, RDMA dynamic allocation, CID lifecycle tests, and any users of `qed_cxt_get_task_ctx()`/`qed_cxt_get_tid_mem_info()` successfully consuming the exposed memory geometry.
