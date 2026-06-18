# sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.c

## Purpose
Shared NetLabel Generic Netlink and audit helper implementation.

## Important APIs, Types, And Functions
`netlbl_netlink_init()` registers management, CIPSOv4, CALIPSO, and unlabeled Generic Netlink families in order. `netlbl_audit_start_common()` starts an audit record, writes common NetLabel audit fields, and appends the current subject context.

## Control Flow
Netlink initialization stops at the first failed family registration and returns that error. Audit start exits early when auditing is off or allocation fails; otherwise it uses `audit_context()`, `GFP_ATOMIC`, loginuid/session values, and LSM subject properties from the supplied `netlbl_audit`.

## State And Persistence Behavior
No owned persistent state. Successful family registration persists in Generic Netlink core. Audit buffers are returned to callers, which must append event-specific fields and call `audit_log_end()`.

## Dependencies And Integration Points
Depends on management, CIPSOv4, CALIPSO, and unlabeled init functions, audit subsystem, security LSM property formatting, Generic Netlink, and init user namespace UID conversion.

## Risks And Test Signals
Risks include partial Generic Netlink registration without rollback if a later family fails, NULL audit buffers being normal when auditing is disabled, and callers forgetting to end audit records. Test signals include init failure injection, audit-off behavior, and representative add/remove audit log formatting.
