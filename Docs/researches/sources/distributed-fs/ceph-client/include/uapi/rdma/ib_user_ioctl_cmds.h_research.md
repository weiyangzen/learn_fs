<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h

## Purpose
Defines the generic RDMA uverbs ioctl object, method, and attribute ID namespace used by modern ioctl-based verbs APIs.

## Important APIs, Types, and Functions
Read coverage: 437 lines and 11155 bytes. Visible type families include enum uverbs_default_objects, enum uverbs_methods_device, enum uverbs_attrs_invoke_write_cmd_attr_ids, enum uverbs_attrs_query_port_cmd_attr_ids, enum uverbs_attrs_query_port_speed_cmd_attr_ids, enum uverbs_attrs_get_context_attr_ids, enum uverbs_attrs_query_context_attr_ids, enum uverbs_attrs_create_cq_cmd_attr_ids, enum uverbs_attrs_destroy_cq_cmd_attr_ids, enum uverbs_attrs_create_flow_action_esp, enum uverbs_attrs_modify_flow_action_esp, enum uverbs_attrs_destroy_flow_action_esp, enum uverbs_attrs_create_qp_cmd_attr_ids, enum uverbs_attrs_destroy_qp_cmd_attr_ids, enum uverbs_methods_qp, enum uverbs_attrs_create_srq_cmd_attr_ids, enum uverbs_attrs_destroy_srq_cmd_attr_ids, enum uverbs_methods_srq, enum uverbs_methods_cq, enum uverbs_attrs_create_wq_cmd_attr_ids, enum uverbs_attrs_destroy_wq_cmd_attr_ids, enum uverbs_methods_wq, enum uverbs_methods_actions_flow_action_ops, enum uverbs_attrs_alloc_dm_cmd_attr_ids, enum uverbs_attrs_free_dm_cmd_attr_ids, enum uverbs_methods_dm, enum uverbs_attrs_alloc_dmah_cmd_attr_ids, enum uverbs_attrs_free_dmah_cmd_attr_ids, ... (+31 more). Important macros/constants include IB_USER_IOCTL_CMDS_H, UVERBS_ID_NS_MASK, UVERBS_ID_NS_SHIFT. Explicit ioctl-style command names include IB_USER_IOCTL_CMDS_H.

## Control Flow
Userspace builds an `ib_uverbs_ioctl_hdr` containing object/method IDs from this file and an array of typed attributes. The uverbs core dispatches by object and method, validates mandatory attributes, and calls driver/core handlers for device, CQ, QP, SRQ, WQ, MR, DM, counter, PD, AH, flow, event, and query operations.

## State and Persistence Behavior
The header itself is stateless, but IDs map to persistent uverbs objects and file-descriptor/object-handle lifetimes in the kernel. Attribute IDs define how request/response state is copied, referenced, created, or destroyed.

## Dependencies and Integration Points
It defines the namespace consumed by `rdma_user_ioctl_cmds.h`, `ib_user_ioctl_verbs.h`, provider ioctl headers, the uverbs core, and rdma-core. Direct includes are none.

## Risks and Edge Cases
ID stability is the central ABI risk. Reusing object/method/attribute numbers, changing mandatory/optional interpretation, or crossing namespace bits can break all providers. Mandatory netlink-style attribute flags must be preserved.

## Test Signals
Run uverbs ioctl selftests, rdma-core ABI tests, attribute fuzzer coverage for missing/extra/wrong-size attrs, object lifetime tests, and provider command coverage across old and new kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_cmds.h -->
