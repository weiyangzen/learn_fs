<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h

## Purpose
Defines RDMA netlink families, client/op encoding helpers, iWARP port mapper attributes, local service resolution headers, NLDEV command and attribute IDs, counter modes, device types, name assignment, and notification events.

## Important APIs, Types, and Functions
Read coverage: 669 lines and 16882 bytes. Visible type families include struct rdma_ls_resolve_header, struct rdma_ls_ip_resolve_header, struct rdma_nla_ls_gid, enum rdma_nldev_command, enum rdma_nldev_print_type, enum rdma_nldev_attr, enum rdma_nl_counter_mode, enum rdma_nl_counter_mask, enum rdma_nl_dev_type, enum rdma_nl_name_assign_type, enum rdma_nl_notify_event_type. Important macros/constants include _UAPI_RDMA_NETLINK_H, RDMA_NL_GET_CLIENT, RDMA_NL_GET_OP, RDMA_NL_GET_TYPE, IWPM_UABI_VERSION_MIN, IWPM_UABI_VERSION, IWPM_NLA_MAPINFO_SEND_MAX, IWPM_NLA_REMOVE_MAPPING_MAX, RDMA_NL_LS_F_ERR, LS_DEVICE_NAME_MAX, RDMA_NLA_F_MANDATORY, RDMA_NLA_TYPE_MASK. Explicit ioctl-style command names include none.

## Control Flow
Userspace sends netlink messages whose type encodes RDMA client and operation. IWPM flows register/query/add/remove mappings; LS flows resolve IB path or IP data; NLDEV flows query and configure devices, ports, resources, links, statistics, counters, system parameters, char devices, and notifications using the enumerated commands and attributes.

## State and Persistence Behavior
The header names netlink state exposed by RDMA core: device/port identities, resource handles, QP/MR/CQ/CM_ID/counter records, namespace/netdev links, stat modes, char-device paths, and notification events. Persistent state is maintained in kernel RDMA core and drivers.

## Dependencies and Integration Points
It depends on Linux netlink attribute conventions and integrates with rdma-core tools (`rdma`), kernel RDMA netlink, iwcm/iwarp port mapping, LS resolution, network namespaces, and driver stats. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Netlink attribute IDs are stable ABI. Mandatory attribute bits, nested/net-byteorder flags, command ID growth, and large enum tables require careful append-only changes. Misreporting resource IDs or namespace data can break management tools.

## Test Signals
Run rdma netlink selftests and `rdma` tool queries, fuzz missing/wrong mandatory attributes, test IWPM version negotiation, LS resolve success/failure, NLDEV dump consistency under device hotplug, and counter mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_netlink.h -->
