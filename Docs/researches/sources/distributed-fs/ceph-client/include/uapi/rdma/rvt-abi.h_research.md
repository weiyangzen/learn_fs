<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h

## Purpose
Defines the RDMA Verbs Transport shared ABI used by hfi1/qib-style providers for receive work queues, completion queue entries, SGEs, and atomic head/tail wrappers.

## Important APIs, Types, and Functions
Read coverage: 66 lines and 1771 bytes. Visible type families include struct rvt_wqe_sge, struct rvt_cq_wc, struct ib_uverbs_wc, struct rvt_rwqe, struct rvt_rwq. Important macros/constants include RVT_ABI_USER_H, RDMA_ATOMIC_UAPI. Explicit ioctl-style command names include none.

## Control Flow
Userspace maps receive and completion queues, posts `rvt_rwqe` entries containing SGEs, and observes `rvt_cq_wc` completions. Atomic wrapper macros preserve shared head/tail fields in mmaped memory.

## State and Persistence Behavior
State is shared queue memory: RWQ head/tail, max work requests/SGEs, WQE arrays, and CQ completion entries derived from `ib_user_verbs` work completions.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_verbs.h`. It integrates with rdmavt-based providers such as hfi1 and qib. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_verbs.h>.

## Risks and Edge Cases
Queue memory is shared between kernel and userspace, so alignment, atomicity, and producer/consumer ordering are critical. SGE counts and array bounds must be enforced by providers.

## Test Signals
Exercise rdmavt provider receive queues and CQ polling, shared head/tail wraparound, max SGE validation, 32-bit layout, and stress under concurrent post/poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rvt-abi.h -->
