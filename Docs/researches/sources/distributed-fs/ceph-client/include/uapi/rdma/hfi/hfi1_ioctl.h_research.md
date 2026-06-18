<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h

## Purpose
Defines the HFI1 character-device ioctl payload structures for assigning contexts, querying context/base information, and managing expected TID mappings.

## Important APIs, Types, and Functions
Read coverage: 174 lines and 6618 bytes. Visible type families include struct hfi1_user_info, struct hfi1_ctxt_info, struct hfi1_tid_info, struct hfi1_base_info. Important macros/constants include _LINUX__HFI1_IOCTL_H. Explicit ioctl-style command names include _LINUX__HFI1_IOCTL_H.

## Control Flow
Userspace supplies `hfi1_user_info` to request a context and capabilities, retrieves context and base mapping information, then updates or frees TID mappings through `hfi1_tid_info` arrays used for expected receive buffers.

## State and Persistence Behavior
Driver state includes allocated user contexts, subcontext mappings, receive header/eager buffers, runtime flags, credits, and TID pages. The structures expose offsets, sizes, counts, and IDs needed to mmap and manage that state.

## Dependencies and Integration Points
It depends on Linux fixed-width types and is consumed by ioctl numbers in `rdma_user_ioctl.h`. It integrates with Intel Omni-Path HFI1 userspace drivers and PSM/libfabric stacks. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
TID arrays carry user pointers and page counts, so bounds and pinning are critical. Version/capability negotiation must prevent old userspace from misinterpreting context mapping layouts.

## Test Signals
Exercise assign-context, context/base info queries, TID update/free/invalidation, subcontext sharing, invalid count/address handling, and compat layout against PSM/libfabric users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_ioctl.h -->
