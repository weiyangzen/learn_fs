# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_srq.c

## Purpose
`hns_roce_srq.c` implements shared receive queue creation, destruction, event delivery, buffer allocation, index queues, record doorbells, and SRQ context programming for HNS RoCE.

## Important APIs, Types, And Functions
The main entry points are `hns_roce_create_srq()`, `hns_roce_destroy_srq()`, `hns_roce_srq_event()`, and `hns_roce_init_srq_table()`. Important helpers include `alloc_srqn()`, `alloc_srqc()`, `hns_roce_create_srqc()`, `alloc_srq_idx()`, `alloc_srq_wqe_buf()`, `alloc_srq_db()`, `set_srq_param()`, `proc_srq_sge()`, `free_srqc()`, `free_srq_buf()`, and `free_srq_db()`. It uses `struct hns_roce_srq`, `struct hns_roce_srq_table`, `struct hns_roce_idx_que`, and HNS SRQ uAPI create/response structures.

## Control Flow
Creation initializes SRQ locks, validates and rounds attributes, fills XRC/CQ extension fields, copies userspace queue addresses when present, allocates an MTR-backed index queue, allocates an MTR-backed WQE buffer, optionally allocates kernel WRID storage, maps or allocates record doorbells, allocates an SRQN, allocates SRQC HEM and stores the SRQ in an xarray, writes the SRQC into a command mailbox, creates the hardware SRQ context, initializes event/refcount state, and returns SRQN/capability flags to userspace. Destruction destroys the hardware SRQ context, erases xarray membership, waits for outstanding event references, frees the SRQN, unmaps doorbells, frees buffers, and destroys the mutex. Async SRQ events xarray-lookup the SRQ, take a refcount, translate limit/error events to IB events, and drop the refcount.

## State And Persistence
SRQ state is runtime only: SRQN, WQE count and SGE count, reserved SGE count, SRQ limit, xrcdn/cqn, index queue head/tail and optional bitmap, WQE MTR, optional WRID array, record doorbell mapping, xarray membership, refcount/completion, and callback pointer. Hardware SRQC state is created and destroyed through command mailboxes; no configuration is persisted across device reset or reload.

## Dependencies And Integration Points
The file depends on RDMA SRQ/XRC/CQ helpers, uverbs udata validation/copy, HNS MTR creation from `hns_roce_mr.c`, HEM table APIs, command mailbox helpers, doorbell mapping helpers, and hardware `write_srqc()` support. It is enabled by SRQ capability wiring in `hns_roce_main.c`.

## Risks
Userspace creation validates only through `ib_copy_validate_udata_in(..., que_addr)`, so ABI layout compatibility around optional DB fields must be preserved. `free_srqc()` waits for event references after xarray erase, making refcount initialization and all error paths important. HIP08 reserved-SGE adjustment differs for kernel and userspace and can surprise capacity reporting. Kernel SRQ DB register uses a fixed `SRQ_DB_REG` offset. Attribute validation rejects zero max_sge but permits max_wr to be raised to the minimum, so callers should observe modified caps.

## Test Signals
Test SRQ creation with kernel and userspace queues, minimum-depth rounding, max WR/SGE rejection, HIP08 reserved-SGE behavior, XRC and CQ extension fields, index/WQE MTR allocation failures, record DB capability negotiation, userspace response copy failure after hardware creation, async limit/error event delivery, bogus SRQN events, destroy waiting for event refs, and table init range handling.
