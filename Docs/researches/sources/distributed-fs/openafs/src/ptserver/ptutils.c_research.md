# sources/distributed-fs/openafs/src/ptserver/ptutils.c research

## Purpose
`ptutils.c` is the core database manipulation layer for the Protection Server. It validates names and access rights, creates/deletes/changes entries, manages ids and quotas, updates hash and owner chains, walks membership lists and continuation records, initializes the protection database, and implements optional supergroup traversal/cache invalidation.

## Important APIs, types, and functions
Name and access helpers include `CorrectUserName`, `CorrectGroupName`, and `AccessOK`. Main mutation helpers are `CreateEntry`, `DeleteEntry`, `ChangeEntry`, `AddToEntry`, `RemoveFromEntry`, optional `AddToSGEntry`/`RemoveFromSGEntry`/`ChangeIDEntry`, and `SetMax`. Listing helpers include `AddToPRList`, `GetList`, `GetList2`, optional `GetListSG2`/`GetSGList`, `GetOwnedChain`, and `GetMax`. Database cache/init helpers are `UpdateCache`, `read_DbHeader`, `Initdb_check`, and `Initdb`. Foreign-id helpers are `allocNextId`, `inRange`, and `AddAuthGroup`. With `SUPERGROUPS`, `pt_mywrite` and `pt_hook_write` invalidate in-memory supergroup maps when group records are written.

## Control flow, state, and persistence
All database changes occur under caller-supplied Ubik transactions. `CreateEntry` validates names, handles explicit or allocated ids, constructs normal users/groups, foreign cell groups, and foreign users, adjusts quotas, writes the new entry, inserts id/name hashes, updates owner chains, and increments header counters. `DeleteEntry` removes reciprocal memberships, handles foreign-user quota restoration, removes owner/orphan-chain links, removes id/name hash entries, refunds group quota when appropriate, decrements header counters, and frees the record.

Membership lists live in fixed slots in `struct prentry` and overflow into `struct contentry` chains. `AddToEntry` and `RemoveFromEntry` reuse `PRBADID` holes, allocate/free continuation blocks, maintain `count`, and update timestamps. Supergroup variants use the `prentryg` overlay with `supergroup`, `nextsg`, and `countsg`. `GetList` and `GetList2` build sorted `prlist` results and, for CPS calls, append built-in identities such as `ANYUSERID`, `AUTHUSERID`, and the subject id. `GetOwnedChain` pages owner-chain traversal through a mutable next pointer.

`Initdb` first checks the header under a read-any transaction. If the database is empty, it opens a write transaction, initializes header fields, creates built-in entries (`system:administrators`, `system:backup`, `system:anyuser`, `system:authuser`, `system:ptsviewers`, `anonymous`), and resets max user id to zero.

## Dependencies and integration points
The file depends on Ubik, `ptserver.h` structures/macros, `pterror.h`, `ptprototypes.h`, AFS config for noauth mode, and generated PT list types. It is called primarily by `ptprocs.c`; standalone database tools can also reuse it through the `ptubik.c` shim.

## Risks and test signals
This is the highest-risk persistence file in the set. Any bug can corrupt hash chains, free lists, owner chains, quotas, membership reciprocity, or built-in entries. Byte-order mistakes are easy because header and entry fields are often stored in network order. Long membership and owner lists need continuation-block tests, including deletion, id change, and block-freeing cases. Foreign users need tests for `system:authuser@cell`, allocated id ranges, quota decrement/refund, and deletion of foreign cell groups with remaining users. Supergroup builds need recursion-depth, cache invalidation, group-to-group add/remove, and structure-size coverage. Database initialization should be tested on empty, valid, and non-empty invalid headers.
