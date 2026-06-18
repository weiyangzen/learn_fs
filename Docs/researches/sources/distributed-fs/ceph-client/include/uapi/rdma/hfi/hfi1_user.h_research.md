<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h

## Purpose
Defines the HFI1 userspace shared ABI: software version fields, capability and event bits, status flags, SDMA completion and request formats, packet/KDETH headers, and user register offsets.

## Important APIs, Types, and Functions
Read coverage: 268 lines and 9298 bytes. Visible type families include enum hfi1_sdma_comp_state, struct hfi1_sdma_comp_entry, struct hfi1_status, enum sdma_req_opcode, struct sdma_req_info, struct hfi1_kdeth_header, struct hfi1_pkt_header, enum hfi1_ureg. Important macros/constants include _LINUX__HFI1_USER_H, HFI1_USER_SWMAJOR, HFI1_USER_SWMINOR, HFI1_SWMAJOR_SHIFT, HFI1_CAP_DMA_RTAIL, HFI1_CAP_SDMA, HFI1_CAP_SDMA_AHG, HFI1_CAP_EXTENDED_PSN, HFI1_CAP_HDRSUPP, HFI1_CAP_TID_RDMA, HFI1_CAP_USE_SDMA_HEAD, HFI1_CAP_MULTI_PKT_EGR, HFI1_CAP_NODROP_RHQ_FULL, HFI1_CAP_NODROP_EGR_FULL, HFI1_CAP_TID_UNMAP, HFI1_CAP_PRINT_UNIMPL, HFI1_CAP_ALLOW_PERM_JKEY, HFI1_CAP_NO_INTEGRITY, HFI1_CAP_PKEY_CHECK, HFI1_CAP_STATIC_RATE_CTRL, HFI1_CAP_OPFN, HFI1_CAP_SDMA_HEAD_CHECK, HFI1_CAP_EARLY_CREDIT_RETURN, HFI1_CAP_AIP, HFI1_RCVHDR_ENTSIZE_2, HFI1_RCVHDR_ENTSIZE_16, HFI1_RCVDHR_ENTSIZE_32, _HFI1_EVENT_FROZEN_BIT, ... (+26 more). Explicit ioctl-style command names include HFI1_SDMA_REQ_IOVCNT_MASK, HFI1_SDMA_REQ_IOVCNT_SHIFT.

## Control Flow
After ioctl context setup, userspace mmaps shared pages, reads status and event bits, programs SDMA request descriptors, polls completion entries, acknowledges events, and uses register offsets to interact with assigned context resources.

## State and Persistence Behavior
Shared state includes hardware status words, context events, SDMA completion rings, request descriptors, packet headers, and mapped user registers. These structures persist in shared memory between kernel and userspace for the context lifetime.

## Dependencies and Integration Points
It depends on Linux integer types and the HFI1 ioctl setup path. It integrates with HFI1 hardware, PSM/libfabric, SDMA queues, receive header queues, and accelerated IP/TID RDMA capabilities. Direct includes are #include <linux/types.h>, #include <rdma/rdma_user_ioctl.h>.

## Risks and Edge Cases
Shared-memory ABIs are sensitive to version, alignment, volatile producer/consumer ordering, and bit definitions. Capability bits must match kernel setup, and SDMA iovec counts and opcode/version fields must be validated before DMA.

## Test Signals
Run HFI1 userspace stack tests across SW major/minor negotiation, capability masks, SDMA submit/completion/error paths, event ack, register mmap offsets, and memory-ordering stress on shared rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hfi/hfi1_user.h -->
