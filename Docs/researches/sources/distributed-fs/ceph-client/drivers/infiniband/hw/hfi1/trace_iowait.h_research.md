# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_iowait.h

## Purpose

`trace_iowait.h` defines tracepoints for `struct iowait` flag changes. Iowait state coordinates deferred send work, pending IB/TID work, and wakeups when transmit resources become available.

## Important Events

`hfi1_iowait_template` records the iowait object address, current wait flags, the single flag being changed as a bit mask, and the owning QP number. It instantiates `hfi1_iowait_set` and `hfi1_iowait_clear`.

## Control Flow and State

The tracepoints observe state changes but do not mutate state. Callers in the send and scheduling paths can emit events around `iowait_set_flag()` and clear operations, making it possible to trace why a QP is sleeping or waking.

## Dependencies and Integration Points

The header depends on `iowait.h`, `verbs.h`, `iowait_to_qp()`, and Linux tracepoint APIs. It is relevant to the TID RDMA send path because `hfi1_make_tid_rdma_pkt()` and `hfi1_schedule_tid_send()` set pending TID/IB iowait flags when tx requests or IO resources are unavailable.

## Risks and Test Signals

Risks are low but include tracing an iowait object before it has a valid owner QP or interpreting `flag` incorrectly if enum positions change. Test signals include paired set/clear events around resource starvation, TID send pending state, and later wakeup.
