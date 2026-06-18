<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlink.c -->
# sources/distributed-fs/ceph-client/security/selinux/netlink.c

## Purpose
Creates the SELinux netlink notification channel and broadcasts SELinux status events to userspace listeners. It handles setenforce and policyload messages for the `NETLINK_SELINUX` family.

## Important APIs, Types, and Functions
Public functions are `selnl_notify_setenforce()`, `selnl_notify_policyload()`, and init `sel_netlink_init()`. Internal helpers are `selnl_msglen()`, `selnl_add_payload()`, and `selnl_notify()`. The static `selnl` socket persists after initialization.

## Control Flow
Event-specific wrappers pass message type and data to `selnl_notify()`. The helper determines payload size, allocates an skb with `nlmsg_new()`, creates the netlink header, fills either `selnl_msg_setenforce` or `selnl_msg_policyload`, sets destination group `SELNLGRP_AVC`, and broadcasts. Unknown message types trigger `BUG()`.

## State and Persistence
The file owns one `struct sock *selnl` marked `__ro_after_init`. Notifications do not store history; delivery depends on active netlink listeners. Payload state is transient per skb.

## Dependencies and Integration Points
Depends on `linux/selinux_netlink.h`, generic netlink socket creation, init namespace, and SELinux status updates from enforcing changes and policy loads. `selinuxfs.c` calls the public notifiers after successful changes.

## Risks
`sel_netlink_init()` panics if the netlink socket cannot be created, making boot failure possible for core allocation/configuration failures. Message-size and payload switches must stay synchronized with the uapi message set. Allocation failures only log and drop notifications.

## Test Signals
Listen on `NETLINK_SELINUX` while toggling enforcing and loading policy, verify payload fields and multicast group, test OOM/drop paths with fault injection, and confirm nonroot receive is allowed by `NL_CFG_F_NONROOT_RECV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlink.c -->
