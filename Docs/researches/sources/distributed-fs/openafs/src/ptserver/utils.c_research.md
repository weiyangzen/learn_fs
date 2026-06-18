# sources/distributed-fs/openafs/src/ptserver/utils.c

Purpose: utility layer for the OpenAFS protection server database, providing ubik-backed record I/O, host/network byte-order conversion, free-block allocation, ID/name hash management, owner/orphan chains, ID allocation, and membership checks.

Important APIs/types/functions: `NameHash`, internal `IDHash`, `pr_Read`, `pr_Write`, `pr_ReadEntry`, `pr_WriteEntry`, `pr_ReadCoEntry`, `pr_WriteCoEntry`, `AllocBlock`, `FreeBlock`, `FindByID`, `FindByName`, `AllocID`, `AddToIDHash`, `RemoveFromIDHash`, `AddToNameHash`, `RemoveFromNameHash`, `AddToOwnerChain`, `RemoveFromOwnerChain`, `AddToOrphan`, `RemoveFromOrphan`, `IsOwnerOf`, `OwnerOf`, `IsAMemberOf`, and optional `IsAMemberOfSG`.

Control flow: callers operate inside a `struct ubik_trans`; helpers seek and read/write fixed offsets in database file 0, update `cheader`, traverse linked hash chains, then persist modified entries or header words. Membership first handles built-in groups (`ANYUSERID`, `AUTHUSERID`, `SYSADMINID`), then scans inline `prentry.entries` and continuation `contentry` blocks; with `SUPERGROUPS`, recursive group membership is bounded by `depthsg`.

State/persistence: persistent state is the protection database header, entry blocks, continuation blocks, hash buckets, free list, max user/group/foreign IDs, owner lists, and orphan list. Endianness is normalized explicitly when reading or writing database records.

Dependencies/integration: depends on `ubik`, `ptserver.h`, `pterror.h`, `afs_lock`, `opr_Assert`, and global `cheader`. It is used by higher-level ptserver mutation and lookup paths.

Risks: fixed header offsets are fragile; linked-list corruption can loop unless caught by assertions; `FreeBlock` stores `tentry.next = ntohl(cheader.freePtr)`, which relies on later byte swapping semantics; membership scans trust zero terminators; recursive supergroups can be expensive or cyclic without depth control. Tests should exercise endian round trips, hash collision removal, free-list reuse, ID exhaustion, owner/orphan transitions, and direct plus supergroup membership.
