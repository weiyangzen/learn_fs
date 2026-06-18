# sources/distributed-fs/openafs/src/ptserver/ptprototypes.h research

## Purpose
`ptprototypes.h` is the internal prototype header for the ptserver implementation. It exposes database helper routines shared across the RPC layer, server utilities, and standalone tooling while deliberately leaving the public client API in `ptuser.h`.

## Important APIs, types, and functions
The header declares the low-level record I/O wrappers (`pr_Read`, `pr_Write`, `pr_ReadEntry`, `pr_WriteEntry`, `pr_ReadCoEntry`, `pr_WriteCoEntry`), storage allocation helpers (`AllocBlock`, `FreeBlock`), hash lookup/update functions (`FindByID`, `FindByName`, `AddToIDHash`, `RemoveFromIDHash`, `AddToNameHash`, `RemoveFromNameHash`), id allocation/comparison (`AllocID`, `IDCmp`), owner/orphan-chain helpers (`AddToOwnerChain`, `RemoveFromOwnerChain`, `AddToOrphan`, `RemoveFromOrphan`, `OwnerOf`, `IsOwnerOf`), membership checks (`IsAMemberOf` and optional `IsAMemberOfSG`), membership-list mutations (`AddToEntry`, `RemoveFromEntry`, optional supergroup variants), access and creation helpers (`AccessOK`, `CreateEntry`, `DeleteEntry`, `ChangeEntry`), list extraction (`GetList`, `GetList2`, optional `GetSGList`, `GetOwnedChain`, `AddToPRList`), global max-id access (`GetMax`, `SetMax`), and database initialization/cache functions (`read_DbHeader`, `Initdb`).

## Control flow, state, and persistence
The prototypes describe the internal contract for manipulating the on-disk protection database under an existing Ubik transaction. Callers are expected to have already opened the correct read or write transaction and lock through `ptprocs.c` or equivalent tooling. The declared functions operate on persistent `struct prentry`, `struct contentry`, and `struct prheader` state from `ptserver.h`, updating hash buckets, free lists, continuation chains, counts, quota fields, owner chains, and special header counters.

The conditional `SUPERGROUPS` declarations expose a second membership axis for group-to-group containment and, when enabled, the `pt_hook_write` cache-invalidation hook that rewires Ubik writes. That makes this header a compile-time integration boundary: callers must guard supergroup-only calls exactly the same way as the implementations.

## Dependencies and integration points
This header depends on `ubik_trans`, `prentry`, `contentry`, `prlist`, and `PR_MAXNAMELEN` types supplied by surrounding ptserver headers and generated interfaces. It is included by `ptprocs.c`, `ptutils.c`, `ptserver.c`, `pts.c`, import tools, and test tools. It is not a stable external API; public consumers should use `ptuser.h`.

## Risks and test signals
Because this header exposes internal helpers without ownership annotations beyond a few type signatures, callers can misuse read helpers under write assumptions or mutate database structures without maintaining reciprocal indexes. Prototype drift between this file and `ptutils.c` would cause build failures or, worse, ABI mismatches in old-style C environments. Test signals are mostly compile/link coverage across normal and `SUPERGROUPS` builds plus behavioral coverage through `ptprocs.c` RPC tests, `pt_util`-style database tooling, and `testpt` stress operations.
