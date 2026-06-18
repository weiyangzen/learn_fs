<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_audit.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_audit.h

## Purpose
This header declares common LSM audit data structures and helpers. It standardizes how security modules pass object, network, IPC, key, inode, file, and other context into audit logging.

## Important APIs, Types, and Functions
It defines `struct lsm_network_audit`, `struct lsm_ioctlop_audit`, InfiniBand audit structures, and `struct common_audit_data` with a type discriminator plus union-like fields for paths, dentries, inodes, tasks, keys, files, capabilities, lockdown, notifications, and netlink types. APIs include `ipv4_skb_to_auditdata`, `ipv6_skb_to_auditdata`, `common_lsm_audit`, and `audit_log_lsm_data`, with no-op stubs when auditing is not enabled.

## Control Flow
Security modules populate `common_audit_data`, optionally extract packet addresses, then call common audit helpers to format fields into audit buffers. Disabled configs compile calls away.

## State and Persistence Behavior
The structures are per-event transient data. Persistent audit records are produced by the audit subsystem, not by this header.

## Dependencies and Integration Points
It depends on audit, paths, keys, sk_buffs, IPv6, spinlocks, RDMA verbs, and security modules. It integrates with SELinux, Smack, AppArmor, lockdown, key, network, and filesystem hooks.

## Risks and Test Signals
Risks include wrong discriminator values, uninitialized union fields, leaking sensitive data, and audit records missing network or object context. Test signals are audit log assertions, LSM denial tests, IPv4/IPv6 packet audit coverage, and build coverage with `CONFIG_AUDIT` off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_audit.h -->
