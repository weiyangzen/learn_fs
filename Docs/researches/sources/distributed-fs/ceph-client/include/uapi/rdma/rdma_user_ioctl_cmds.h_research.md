<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h

## Purpose
Defines the generic RDMA ioctl syscall envelope: magic number, ioctl command encoding, `ib_uverbs_attr`, attribute flags, and `ib_uverbs_ioctl_hdr`.

## Important APIs, Types, and Functions
Read coverage: 87 lines and 2617 bytes. Visible type families include struct ib_uverbs_attr, struct ib_uverbs_ioctl_hdr. Important macros/constants include RDMA_USER_IOCTL_CMDS_H, RDMA_IOCTL_MAGIC, RDMA_VERBS_IOCTL. Explicit ioctl-style command names include RDMA_USER_IOCTL_CMDS_H, RDMA_IOCTL_MAGIC, RDMA_VERBS_IOCTL.

## Control Flow
Userspace calls ioctl with `RDMA_VERBS_IOCTL`, passing a header containing length, object ID, method ID, number of attributes, and driver ID. The kernel copies the attribute array, interprets each `ib_uverbs_attr` as pointer/object/ID data according to command metadata, and dispatches to the uverbs handler.

## State and Persistence Behavior
No state is stored in the header. The envelope references uverbs objects and user buffers that the kernel validates and may create, destroy, or mutate during dispatch.

## Dependencies and Integration Points
It depends on Linux ioctl and integer types. It is the low-level container used by `ib_user_ioctl_cmds.h`, `ib_user_ioctl_verbs.h`, and provider-specific ioctl headers. Direct includes are #include <linux/types.h>, #include <linux/ioctl.h>.

## Risks and Edge Cases
Length/count arithmetic, pointer alignment, mandatory flags, attr data union interpretation, and driver-id filtering are safety-critical. The ioctl magic and structure layout cannot change.

## Test Signals
Fuzz ioctl headers and attributes, test zero/large attr counts, wrong driver IDs, unknown object/method IDs, 32-bit pointer layouts, and object lifetime under failing dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl_cmds.h -->
