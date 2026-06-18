# sources/distributed-fs/openafs/src/ptserver/ptserver.h research

## Purpose
`ptserver.h` defines the Protection Server's core database constants, built-in ids, access-bit layout, on-disk record structures, and header mutation macros. It is the structural contract shared by the daemon, RPC handlers, database utilities, client compatibility helpers, and tests.

## Important APIs, types, and functions
Key constants include service id `PRSRV`, fixed record size `ENTRYSIZE`, hash table size `HASHSIZE`, sentinel `PRBADID`, built-in ids (`SYSVIEWERID`, `SYSADMINID`, `SYSBACKUPID`, `ANYUSERID`, `AUTHUSERID`, `ANONYMOUSID`), and database version `PRDBVERSION`.

`struct prheader` is the database header. It stores version/header size, free-list and EOF pointers, max user/group/foreign/instance ids, orphan owner chain head, entry counts, reserved space, and name/id hash tables. `set_header_word` and `inc_header_word` update cached `cheader` fields and persist the network-order value through `pr_Write`.

`struct prentry` is the fixed-size database record for users and groups. It includes flags, id, cell id, continuation pointer, timestamps, primary membership/member slots, hash-chain pointers, owner/creator, quota/count fields, ownership chains, future instance fields, and fixed-size name. When `SUPERGROUPS` is enabled, `struct prentryg` overlays the same record size with `countsg`, `nextsg`, and `supergroup[SGSIZE]`. `struct contentry` represents continuation blocks.

## Control flow, state, and persistence
The structures are persisted directly in the Ubik database. Most fields are stored in network byte order when read/written through lower-level helpers, and callers frequently convert with `htonl`/`ntohl`. Hash buckets in `prheader` point to `prentry` record offsets. Membership lists start in `prentry.entries` and continue through `contentry` blocks. Owner lists use `owned` and `nextOwned`; orphaned groups are anchored from the header. Access bits are stored in the upper half of `flags` via `PRIVATE_SHIFT`, while RPC/client interfaces expose right-shifted values.

## Dependencies and integration points
The header includes generated `ptint.h`, declares `cheader`, and declares `string_PR_IDToName` as a sanitized client helper implemented in `ptuser.c`. It is included by both server and local tooling, so any structure change affects persistent database compatibility and must keep `ENTRYSIZE` invariants.

## Risks and test signals
This file is persistence-critical. Changing field order, sizes, constants, byte-order assumptions, or access-bit definitions can corrupt existing protection databases or break wire/client compatibility. `SUPERGROUPS` builds explicitly verify `sizeof(struct prentry)` and `sizeof(struct prentryg)` against `ENTRYSIZE`; similar compile/runtime checks are important after any structural change. Tests should cover database initialization, dump/restore or upgrade tooling, membership continuation blocks, owner chains, access flag round trips, and id/name hash lookups.
