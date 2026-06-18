<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h

## Purpose
Defines the access vector table data model and public API for SELinux type enforcement rules. It describes how rules are keyed by source type, target type, target class, and a specified rule kind.

## Important APIs, Types, and Functions
Core types are `struct avtab_key`, `struct avtab_extended_perms`, `struct avtab_datum`, `struct avtab_node`, and `struct avtab`. Rule flags include `AVTAB_ALLOWED`, `AVTAB_AUDITALLOW`, `AVTAB_AUDITDENY`, transition/member/change type rules, xperm rule kinds, and conditional `AVTAB_ENABLED`. APIs cover init, allocation, duplication, destruction, read/write, nonunique insertion, node search, and next-node search.

## Control Flow
Consumers construct an `avtab_key` and search a table to accumulate decisions. Policy load allocates a table, reads items, and inserts nodes. Conditional policy code stores multiple matching nodes and toggles `AVTAB_ENABLED` without removing nodes. Policy write walks the table and serializes each node.

## State and Persistence
The header defines in-memory hash table state and the datum union for either 32-bit permissions/type values or heap-backed extended permissions. The same shapes are serialized by `avtab.c` into binary policies.

## Dependencies and Integration Points
Depends on `security.h` for extended permission bitmaps and policy constants. Integrated by policydb, services decision computation, and conditional policy handling.

## Risks
`specified` mixes rule kind bits and conditional enabled bits; callers must mask correctly. Extended permissions allow multiple entries for a key, unlike regular AV/type rules. Changing `SEL_VEC_MAX` or xperm layout affects decision computation and binary compatibility.

## Test Signals
Compile policydb/services users, load policies with each rule kind, verify conditional enabled toggling, test xperm driver windows, and confirm serialization round trips match the expected rule counts and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h -->
