<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h

## Purpose
Defines the legacy write-based uverbs ABI: command numbers, command/response structures, work requests, flow specs, object lifecycle payloads, query responses, and device capability flags.

## Important APIs, Types, and Functions
Read coverage: 1380 lines and 29479 bytes. Visible type families include enum ib_uverbs_write_cmds, enum ib_placement_type, enum ib_selectivity_level, struct ib_uverbs_async_event_desc, struct ib_uverbs_comp_event_desc, struct ib_uverbs_cq_moderation_caps, struct ib_uverbs_cmd_hdr, struct ib_uverbs_ex_cmd_hdr, struct ib_uverbs_get_context, struct ib_uverbs_get_context_resp, struct ib_uverbs_query_device, struct ib_uverbs_query_device_resp, struct ib_uverbs_ex_query_device, enum ib_uverbs_odp_general_cap_bits, enum ib_uverbs_odp_transport_cap_bits, struct ib_uverbs_odp_caps, struct ib_uverbs_rss_caps, struct ib_uverbs_tm_caps, struct ib_uverbs_ex_query_device_resp, struct ib_uverbs_query_port, struct ib_uverbs_query_port_resp, struct ib_uverbs_alloc_pd, struct ib_uverbs_alloc_pd_resp, struct ib_uverbs_dealloc_pd, struct ib_uverbs_open_xrcd, struct ib_uverbs_open_xrcd_resp, struct ib_uverbs_close_xrcd, struct ib_uverbs_reg_mr, ... (+100 more). Important macros/constants include IB_USER_VERBS_H, IB_USER_VERBS_ABI_VERSION, IB_USER_VERBS_CMD_THRESHOLD, IB_USER_VERBS_CMD_COMMAND_MASK, IB_USER_VERBS_CMD_FLAG_EXTENDED, IB_USER_VERBS_MAX_LOG_IND_TBL_SIZE, IB_DEVICE_NAME_MAX. Explicit ioctl-style command names include none.

## Control Flow
Userspace writes command structures to the uverbs file to get context, query device/port/GID/P_Key, allocate/deallocate PD/MR/MW/CQ/QP/AH/SRQ/WQ/flows, post send/receive work requests, poll or arm CQs, attach multicast, and query/modify objects. Responses return handles, capabilities, object numbers, and bad-WR indices.

## State and Persistence Behavior
State is in persistent uverbs objects bound to the file/context: PDs, MRs, MWindows, CQs, QPs, AHs, multicast membership, flow steering rules, SRQs, WQs, and receive indirection tables. Work request structures describe transient queue entries copied or consumed by providers.

## Dependencies and Integration Points
It depends on Linux integer and ioctl types and is the compatibility layer beneath rdma-core's older command path. It integrates with all RDMA providers and coexists with the newer ioctl ABI. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is a broad stable ABI with many deprecated but preserved fields. Risks include 32/64-bit pointer encoding through aligned u64 values, command-number stability, structure alignment comments, flow-spec length validation, bad WR reporting, and capability flag bits reserved due to old kernels.

## Test Signals
Run rdma-core verbs tests across all major providers, 32-bit compat command tests, create/query/modify/destroy lifecycle tests, post-send/recv bad-WR handling, flow steering filters, multicast attach/detach, and ABI structure size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_verbs.h -->
