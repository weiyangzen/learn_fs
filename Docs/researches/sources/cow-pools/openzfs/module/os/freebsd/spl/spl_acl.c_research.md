# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_acl.c

FreeBSD ACL bridge between ZFS ACE structures and FreeBSD `struct acl`.

Key behavior:
- Static mapping tables translate ZFS ACE permission bits and flags to FreeBSD ACL permission/entry flags.
- `acl_from_aces()` validates count, fills `struct acl`, maps ACE principal flags to FreeBSD tags, copies IDs for named users/groups, and maps ACE type to allow/deny/audit/alarm.
- `aces_from_acl()` performs the reverse conversion from FreeBSD ACL entries to ZFS ACEs.

It panics on unexpected ACE or FreeBSD ACL entry types because callers should provide validated ACLs.
