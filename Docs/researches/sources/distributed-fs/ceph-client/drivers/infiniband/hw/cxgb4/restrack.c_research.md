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
