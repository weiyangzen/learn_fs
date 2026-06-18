<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c

## Purpose
Maps userspace-generated netlink message types to SELinux permissions for route, tcpdiag/sockdiag, XFRM, and audit netlink socket classes. It provides the policy-facing decision used by SELinux netlink send checks.

## Important APIs, Types, and Functions
The public API is `selinux_nlmsg_lookup()`. `struct nlmsg_perm` stores message type and permission. Static tables cover route messages, tcpdiag/sockdiag messages, XFRM messages, and audit messages. Helper `nlmsg_perm()` linearly searches a table.

## Control Flow
`selinux_nlmsg_lookup()` switches on socket class. If policy capability `netlink_xperm` is enabled, it returns the generic `NLMSG` permission for extended-permission checking. Otherwise it table-lookups fixed message permissions. Audit user-message ranges map to relay permission without table entries. Unknown or unsupported classes return `-ENOENT`; unknown messages in handled classes return `-EINVAL`.

## State and Persistence
State is static read-only mapping tables. Runtime behavior changes when policy capability `POLICYDB_CAP_NETLINK_XPERM` is enabled, shifting checks from coarse fixed table permissions to extended permissions keyed by `nlmsg_type`.

## Dependencies and Integration Points
Depends on kernel netlink uapi constants, generated SELinux class/permission macros, and policycap accessors. Build-time `BUILD_BUG_ON()` checks force table updates when `RTM_MAX` or `XFRM_MSG_MAX` changes.

## Risks
Missing table updates after adding kernel netlink message types can deny legitimate operations or map them incorrectly. Extended permissions cannot be applied blindly to generic netlink because message type values are dynamic. Audit user-message range handling is special and must stay aligned with audit uapi ranges.

## Test Signals
Test each supported netlink class with read/write/relay messages, unknown message denial, policycap `netlink_xperm` enabled/disabled behavior, audit user message ranges, and compile failures when route/XFRM max constants move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c -->
