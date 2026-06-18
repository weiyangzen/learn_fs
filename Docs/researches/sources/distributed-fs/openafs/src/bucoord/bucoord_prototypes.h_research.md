# sources/distributed-fs/openafs/src/bucoord/bucoord_prototypes.h

`bucoord_prototypes.h` is the installed/public-ish prototype header for backup coordinator support library functions. It exposes double-linked queue utilities, status queue operations, VLDB lookup, backup database text/dump/tape/volume wrappers, client initialization, and single-server BUDB ubik call wrappers.

Important declarations include `dlqEmpty`, `dlqInit`, `dlqUnlink`, `dlqLinkb`, `dlqLinkf`, `dlqTraverseQueue`; status functions `initStatus`, `findStatus`, `lock_Status`, `unlock_Status`, `deleteStatusNode`, `createStatusNode`; `bc_GetEntryByID`; multiple `bcdb_*` wrappers; `udbClientInit`; `vldbClientInit`; and `ubik_Call_SingleServer_BUDB_GetVolumes`/`DumpDB`.

The header has no direct control flow or persistence. Its contracts mediate persistent backup database operations, text-file locks/saves, dump/tape/volume records, and status queue ownership. Dependencies are `dlqlinkP`, `statusP`, `udbClientTextP`, `budb_*` types, `ubik_client`, `vldbentry`, and token/time types supplied by consumers.

Risks include installed API stability, overlap with `bucoord_internal.h`, callback typing for `dlqTraverseQueue`, and ownership/error-code conventions not visible in prototypes. Test signals are external consumer builds, archive symbol availability, queue operation unit tests, and integration tests for BUDB wrapper calls.
