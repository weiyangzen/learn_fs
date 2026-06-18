<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_audit.c -->
# sources/distributed-fs/ceph-client/security/lsm_audit.c

## Purpose

`lsm_audit.c` provides common audit helpers used by LSMs to format network, path, task, capability, key, lockdown, and other security-relevant data into audit records.

## Important APIs, Types, and Functions

- `ipv4_skb_to_auditdata()` fills `common_audit_data` from IPv4 skb headers and optional layer-4 ports.
- `ipv6_skb_to_auditdata()` does the same for IPv6, including extension-header skipping, when IPv6 is enabled.
- `audit_log_lsm_data()` serializes a `common_audit_data` union based on its `type`.
- `dump_common_audit_data()` adds current process pid/comm and common LSM data.
- `common_lsm_audit()` opens an `AUDIT_AVC` buffer, runs optional LSM-specific pre/post callbacks, dumps common data, and closes the record.

## Control Flow

Packet helpers copy addresses first, optionally report protocol, and avoid parsing non-initial IPv4 fragments. For TCP, UDP, and SCTP they extract source/destination ports; unknown protocols return `-EINVAL` after address population. IPv6 uses `skb_header_pointer()` for safe transport header reads after extension-header traversal.

Audit formatting switches on `a->type`. Path, file, ioctl, dentry, and inode cases emit pathname plus device/inode details. Task cases emit target pid and command. Network cases prefer socket-local details when an sk is present, including AF_UNIX pathname or abstract name hex, then also format address-family fields and netif names from `init_net`. Optional sections cover keys, InfiniBand, lockdown, anonymous inode class, and netlink message type.

`common_lsm_audit()` uses `GFP_ATOMIC | __GFP_NOWARN`, so audit can be attempted from restricted contexts without sleeping; if no buffer is available, it silently drops the record.

## State and Persistence Behavior

The file has no persistent mutable state. It reads current task data, skb headers, inode/dentry state, socket state, and optional audit context at the time of logging.

## Dependencies and Integration Points

It depends on audit core APIs, networking headers, AF_UNIX internals, IPv4/IPv6 helpers, LSM audit data types, lockdown reason strings, and optional key support. LSMs call `common_lsm_audit()` or `audit_log_lsm_data()` to avoid duplicating formatting logic.

## Risks and Edge Cases

Audit formatting touches many object types and must avoid sleeping or dereferencing unstable pointers. IPv6 extension parsing may fail and intentionally returns partial data. AF_UNIX abstract names can contain null bytes and are logged as hex when needed. The `BUILD_BUG_ON` guards `common_audit_data` union size to prevent stack bloat.

## Test Signals

Audit tests should cover path/file/dentry/inode/task records, IPv4/IPv6 TCP/UDP/SCTP and fragmented packets, AF_UNIX pathname and abstract sockets, key and lockdown data, netif lookup, no-audit-buffer behavior, and LSM-specific pre/post callbacks producing a well-formed `AUDIT_AVC` record.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_audit.c -->
