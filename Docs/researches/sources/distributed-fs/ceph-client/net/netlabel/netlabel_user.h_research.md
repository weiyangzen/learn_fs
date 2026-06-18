# sources/distributed-fs/ceph-client/net/netlabel/netlabel_user.h

## Purpose
Shared declarations for NetLabel netlink initialization and common audit helpers.

## Important APIs, Types, And Functions
Defines inline `netlbl_netlink_auditinfo()` to populate `struct netlbl_audit` from current LSM subject properties, loginuid, and audit session. Declares `netlbl_netlink_init()` and `netlbl_audit_start_common()`.

## Control Flow
The inline helper is called by netlink command handlers before audited mutations. It snapshots current credentials/audit identity for later use in event-specific audit records.

## State And Persistence Behavior
No persistent state. It fills caller-provided stack or heap audit metadata.

## Dependencies And Integration Points
Depends on security, audit, netlink, Generic Netlink, and `net/netlabel.h`. Used by all NetLabel Generic Netlink families and by domain/unlabeled audit paths.

## Risks And Test Signals
Risks include missing audit identity initialization before audited operations and assumptions about current task context. Test signals include audit field checks for management, DOI, and unlabeled commands.
