# sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.h

## Purpose

`afsclassfn.h` is the public operation header for the Windows AfsClass library. It declares the higher-level administrative verbs that callers use for server, service, fileset, user, group, key, admin-list, host-list, VLDB, and PTS operations. The header explicitly documents the library threading contract: these routines are intended for background threads while the application main thread stays dedicated to UI work.

## Important APIs, Types, and Functions

The server API includes log retrieval, authorization toggles, file install/uninstall/pruning/date lookup, command execution, salvage, VLDB sync, and address-change helpers. Admin and database host list APIs expose `ADMINLISTENTRY`, `ADMINLIST`, `HOSTLISTENTRY`, and `HOSTLIST` with load/copy/save/free/add/delete operations and deferred add/delete semantics. Key APIs use `SERVERKEY` and `KEYLIST` and can add keys from raw `ENCRYPTIONKEY` or a string. Service APIs create/delete/start/stop/restart BOS services and manage restart schedules. Fileset APIs create, delete, move, clone, release, dump, restore, lock, unlock, rename, set quota, and manage replicas. Account APIs define `USERPROPERTIES`, `GROUPPROPERTIES`, and `PTSPROPERTIES` with bitmask constants controlling partial updates.

## Control Flow

This header has no executable flow. It defines the call surface that implementation files route through `LPIDENT` handles into the class graph and worker-task layer. Most functions take an optional `ULONG *pStatus` to report lower-level OpenAFS/BOS/VOS/KAS/PTS errors.

## State and Persistence Behavior

No state is stored here, but the declared operations mutate persistent AFS server state: BOS configuration, VLDB entries, volume quotas and replicas, KAS/PTS accounts, keys, and server lists. List add/delete helpers stage local changes until the corresponding save function commits them.

## Dependencies and Integration Points

The file depends on `LPIDENT`, `SYSTEMTIME`, `SOCKADDR_IN`, service/fileset/account enums and structures from `afsclass.h` and sibling class headers. It is the procedural facade over the object cache implemented by `CELL`, `SERVER`, `AGGREGATE`, `FILESET`, `SERVICE`, `USER`, and `PTSGROUP`.

## Risks and Edge Cases

Callers must obey the background-thread expectation or risk blocking UI threads on network/RPC operations. The bitmask constants define partial-update contracts; a bad mask silently changes which account properties are committed. `MASK_GROUPPROP_aaDeleteMember` is `0x00000012`, overlapping `aaListStatus` and `aaAddMember` bits rather than being a distinct power of two, which is a compatibility-sensitive risk.

## Test Signals

Compile coverage should verify this header with the public `afsclass.h` include set. Integration tests should exercise status propagation for failed BOS/VOS/KAS/PTS calls, deferred admin/host list save behavior, account-property masks, and representative create/delete/refresh flows through `LPIDENT`.
