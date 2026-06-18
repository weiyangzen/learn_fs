# sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.cpp

## Purpose

`c_cell.cpp` implements `CELL`, the root cache object for an AFS cell. It owns the opened cell handle, server cache, user/group cache, global cell list, credential handle, and VLDB reconciliation logic that links server/aggregate/fileset objects with VLDB volume sites.

## Important APIs, Types, and Functions

Important methods include `InitClass`, constructor/destructor, `OpenCell`, `CloseCell`, `ReopenCell`, `GetDefaultCell`, `GetCellObject`, credential setters, invalidation methods, `RefreshServerList`, `RefreshServers`, `RefreshStatus`, `RefreshVLDB`, `RefreshVLDB_RemoveReferences`, `RefreshVLDB_OneEntry`, `RefreshAll`, user/group open/enumeration methods, `RefreshUsers`, `BuildGroups`, `RefreshAccount`, and `RefreshAccounts`. Hash callbacks index servers by shortened name and primary address, users by principal, and groups by name.

## Control Flow

`OpenCell` enters the library, reuses an existing cell by name when possible, or creates a new `CELL` and opens a worker cell object with `wtaskClientCellOpen`. `CloseCell` decrements request count and destroys the cell when no callers remain. Server refresh can either replace the full list or mark current servers for deletion, enumerate database servers with `wtaskClientAFSServerGetBegin/GetNext/GetDone`, update addresses, create new `SERVER` objects, remove missing ones, and rebuild an ANSI server-name array. `RefreshVLDB` scopes by cell/server/aggregate/fileset, removes old VLDB ghost references, enumerates VLDB entries or fetches one volume, and `RefreshVLDB_OneEntry` ensures ghost or real server/aggregate/fileset objects exist for each replication site. User refresh enumerates KAS principals, derives groups from ownership/membership, optionally probes PTS-only debris, and then sends create notifications. `RefreshAccount` updates a single account after create/change/delete operations.

## State and Persistence Behavior

The class caches `m_hCell`, an always-null KAS server selector, credentials, request count, server list, user/group lists, stale flags, and `m_apszServers`. It does not persist state itself, but it opens real AFS cell handles and reflects VLDB/KAS/PTS/database-server state. Ghost flags preserve references to objects present in either server state or VLDB state.

## Dependencies and Integration Points

`CELL` integrates with `SERVER`, `AGGREGATE`, `FILESET`, `USER`, `PTSGROUP`, `IDENT`, `NOTIFYCALLBACK`, `Worker_DoTask`, `HASHLIST`, VOS/KAS/PTS/client worker tasks, address conversion, multisz/string helpers, and global knobs such as `dwWant`, `cRefreshAllReq`, and `AFSCLASS_WANT_*`.

## Risks and Edge Cases

`ReopenCell` returns with `AfsClass_Enter` still held on success and leaves only on failure, so callers must follow the expected `Close` pattern. `OpenServer` by address has a likely bug in the brute-force branch: after finding a matching secondary address it breaks only the inner loop, then still closes the server and continues. VLDB refresh can create ghost servers/aggregates/filesets with partial status. User refresh is expensive and mixes KAS and PTS results; PTS-only accounts may be incomplete. Several enumeration loops remove objects while iterating and depend on `HASHLIST` iterator behavior.

## Test Signals

Tests should cover repeated open/close request counts, default-cell lookup failure, server add/remove refreshes, multihomed server lookup, VLDB ghost creation/removal, scoped VLDB refresh for a single fileset, KAS-only/PTS-only accounts, group discovery from memberships, and notification ordering for refresh begin/end/create/destroy events.
