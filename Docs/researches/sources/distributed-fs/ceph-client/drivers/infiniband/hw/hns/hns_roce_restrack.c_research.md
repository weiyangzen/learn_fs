# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_restrack.c

## Purpose
`hns_roce_restrack.c` provides RDMA netlink resource-tracking detail for HNS CQ, QP, MR, and SRQ objects. It exposes driver-specific summary attributes and optional raw hardware context dumps for diagnostics.

## Important APIs, Types, And Functions
The exported callbacks are `hns_roce_fill_res_cq_entry()`, `hns_roce_fill_res_cq_entry_raw()`, `hns_roce_fill_res_qp_entry()`, `hns_roce_fill_res_qp_entry_raw()`, `hns_roce_fill_res_mr_entry()`, `hns_roce_fill_res_mr_entry_raw()`, `hns_roce_fill_res_srq_entry()`, and `hns_roce_fill_res_srq_entry_raw()`. They use RDMA netlink helpers such as `nla_nest_start()`, `rdma_nl_put_driver_u32()`, `rdma_nl_put_driver_u32_hex()`, and `nla_put()`.

## Control Flow
Summary callbacks open a `RDMA_NLDEV_ATTR_DRIVER` nest, append selected software fields, close the nest, and cancel it on size errors. Raw callbacks check that the corresponding hardware query callback exists, issue a query for the CQC/QPC/SCCC/MPT/SRQC context, and put the raw context blob under `RDMA_NLDEV_ATTR_RES_RAW`. QP raw output combines QPC with optional SCCC data; DIP congestion uses the DIP index when present.

## State And Persistence
The file does not own persistent state. It snapshots live object fields such as CQ depth/consumer index, QP WQE counts, MR PBL layout, and SRQ identifiers. Raw dumps reflect hardware context at query time. Failed SCCC queries are rate-limited warnings and leave the SCCC part zeroed.

## Dependencies And Integration Points
These callbacks are installed in `hns_roce_main.c` through `hns_roce_dev_restrack_ops`. They depend on RDMA netlink resource tracking, HNS object conversion helpers, hardware query callbacks from the selected HNS generation, and context structures from the v2 hardware header.

## Risks
Raw context layout is driver/kernel ABI diagnostic data; structure-size changes can affect user tooling that expects exact blobs. Summary fields are read without object-local locks, so rapidly changing indices or QP attributes may be slightly stale. `hns_roce_fill_res_mr_entry_raw()` passes `hr_mr->key` to `query_mpt()` while other paths often use hardware indexes, so query callback expectations are important. Optional SCCC failure is nonfatal, which can hide flow-control diagnostic gaps.

## Test Signals
Test netlink dump size exhaustion, summary and raw dumps for CQ/QP/MR/SRQ, missing hardware query callbacks returning `-EINVAL`, QP raw dumps with and without flow control, DIP congestion with missing/present DIP object, SCCC query failure warning behavior, and concurrent destroy/dump races under RDMA restrack references.
