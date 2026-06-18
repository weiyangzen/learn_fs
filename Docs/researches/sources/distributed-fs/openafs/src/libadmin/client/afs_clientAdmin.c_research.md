# sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.c

## Purpose
This file implements client-oriented OpenAFS admin APIs: initialization, token acquisition/use, cell handle creation, mountpoint and ACL editing, server enumeration, RPC stats connections, cache-manager stats connections, and rxdebug handle creation.

## Important APIs, Types, and Functions
- Initialization and validation: `afsclient_Init`, `client_once`, and `IsTokenValid`.
- Token APIs: `afsclient_TokenGetExisting`, `afsclient_TokenPrint`, `afsclient_TokenSet`, `afsclient_TokenGetNew`, `afsclient_TokenQuery`, and `afsclient_TokenClose`, with static `GetAFSToken` and `GetKASToken`.
- Cell APIs: `afsclient_CellOpen`, `afsclient_NullCellOpen`, `afsclient_CellClose`, `afsclient_CellNameGet`, and `afsclient_LocalCellGet`.
- Filesystem helpers: `afsclient_MountPointCreate`, `afsclient_ACLEntryAdd`, and platform-specific `Parent` helpers.
- Server enumeration: `afsclient_AFSServerGet`, `afsclient_AFSServerGetBegin`, `afsclient_AFSServerGetNext`, `afsclient_AFSServerGetDone`, and iterator callbacks over cached server data.
- Stats/debug APIs: `afsclient_RPCStatOpen`, `afsclient_RPCStatOpenPort`, `afsclient_RPCStatClose`, `afsclient_CMStatOpen`, `afsclient_CMStatOpenPort`, `afsclient_CMStatClose`, `afsclient_RXDebugOpen`, `afsclient_RXDebugOpenPort`, and `afsclient_RXDebugClose`.

## Control Flow and State
`afsclient_Init` uses `pthread_once`, initializes path state, RX, and KAS cell config. Token creation either wraps existing kernel tokens, prints server-key tokens from a config dir, creates unauthenticated rxnull tokens, or obtains KAS/AFS rxkad tokens from the auth service. `afsclient_CellOpen` validates tokens, opens ubik clients for KAS, PTS, and VOS, stores token and server-list cache state in `afs_cell_handle_t`, and marks the handle valid. Server enumeration merges database-server data from util admin with file-server data from VOS, deduplicates addresses, reverse-resolves names, caches the result with a ten-minute TTL, and serves it through the common admin iterator.

## Persistence and Side Effects
Token APIs can read kernel tokens and set kernel tokens. Cell open creates RX/Ubik client state. Mountpoint creation creates a symlink on Unix or uses `VIOC_AFS_CREATE_MT_PT` on Windows. ACL addition reads and writes directory ACLs via pioctl. Stats and rxdebug functions open sockets/RX cached connections and close or release them. Server enumeration may populate a per-cell-handle cache.

## Dependencies and Integration Points
The implementation depends on RX/RXKAD/RX null, KAS auth utilities, ktc token APIs, afsconf, VOS admin, util admin, pt/vl headers, pioctl, pthread global locks, and admin iterator utilities. KAS and PTS admin modules consume cell handles created here. cfg modules use null-cell and regular cell handles for host and BOS operations.

## Risks
Callers must invoke `afsclient_Init` first. Many output buffers are assumed large enough. Token security objects are allocated but failure paths mostly free only the token handle, so object ownership must be audited carefully. `afsclient_TokenClose` frees the token handle without destroying individual security classes. `afsclient_NullCellOpen` does not free the partially allocated cell handle if token creation fails. ACL manipulation uses fixed 2 KB buffers, string parsing, and concatenation, creating overflow/truncation risk on large ACLs. Server enumeration relies on global locking around resolver calls and has race handling for the shared cache. `afsclient_RXDebugOpen` stores host-order address/port while `afsclient_RXDebugOpenPort` stores network-order values, a behavioral inconsistency worth testing.

## Test Signals
Tests should cover initialization requirements, authenticated/unauthenticated/existing/server-key token paths, token query fields, cell open/close cleanup on partial failures, null-cell lifecycle, mountpoint creation with/without VLDB checking, ACL replacement for existing users and large ACLs, server enumeration deduplication and cache expiry, stats connection port/type selection, KAS token requirements for KAS stats, and rxdebug open/close byte-order behavior.
