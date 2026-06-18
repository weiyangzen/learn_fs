<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h

## Purpose
Defines userspace-facing InfiniBand Subnet Administration record payloads for path and service records.

## Important APIs, Types, and Functions
Read coverage: 91 lines and 2522 bytes. Visible type families include struct ib_path_rec_data, struct ib_user_path_rec, struct ib_user_service_rec. Important macros/constants include IB_USER_SA_H. Explicit ioctl-style command names include none.

## Control Flow
SA clients exchange path or service record data with subnet administration interfaces. The structures carry GIDs, LIDs, P_Key, SL/QoS, MTU/rate/lifetime selectors, service IDs, service names, and service data in fixed ABI layouts.

## State and Persistence Behavior
No local state is stored. The structures represent SA database records returned by subnet managers or supplied in SA requests.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with RDMA CM, SA query libraries, subnet managers, and applications that resolve IB paths or services. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Field packing, endian interpretation, and selector semantics must match IBTA SA records. Service name sizes and reserved fields are fixed ABI.

## Test Signals
Validate path and service record sizes, query a live or simulated subnet manager, check endian conversion, and compile rdma-core SA consumers against the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_sa.h -->
