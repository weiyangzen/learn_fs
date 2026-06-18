# subset-b-007696 Research

Grouped source research for the OpenAFS Windows `afsclass` object model, covering the public operation declarations, cache-backed cell/server/aggregate/fileset/service/user/group classes, identity registry, notification plumbing, debug helpers, and identifier-list container. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/afsclassfn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.cpp

## Purpose

`c_agg.cpp` implements `AGGREGATE`, the cached representation of an AFS server partition/aggregate and the filesets hosted on it. It bridges server-side VOS partition and volume enumeration into AfsClass objects, status snapshots, ghost flags, and notifications.

## Important APIs, Types, and Functions

Key methods are the constructor/destructor, `GetIdentifier`, `Invalidate`, `InvalidateAllocation`, `RefreshStatus`, `RefreshFilesets`, `CalculateAllocation`, `OpenCell`, `OpenServer`, `OpenFileset` by name or volume ID, `FilesetFindFirst/Next/Close`, `GetStatus`, `GetGhostStatus`, and `GetID`. Hash key callbacks index `m_lFilesets` by fileset name and `VOLUMEID`.

## Control Flow

Construction captures parent server/cell identifiers, stores the partition name/device, and creates a critical-section-backed hash list with name and ID keys. `RefreshStatus` lazily calls `OpenServer`, opens a VOS object, runs `wtaskVosPartitionGet`, fills total/free storage, then computes allocated quota if allocation is stale. `RefreshFilesets` first refreshes status for the partition ID, sends begin/end notifications, deletes cached filesets with destroy notifications, enumerates VOS volumes with `wtaskVosVolumeGetBegin/GetNext/GetDone`, creates `FILESET` objects, seeds each from VOS, marks `GHOST_HAS_SERVER_ENTRY`, and invalidates allocation. `OpenFileset` and enumeration methods force refresh before returning borrowed objects under the AfsClass enter/leave reference discipline.

## State and Persistence Behavior

State is in-memory only: parent `LPIDENT`s, name/device, ghost flags, cached partition ID, status flags, `AGGREGATESTATUS`, and the fileset hash list. It does not persist data directly; it reflects server VOS state and recalculates allocated quota from read-write fileset quotas.

## Dependencies and Integration Points

The file depends on `SERVER` for VOS handles, `FILESET` for child volumes, `IDENT` for stable handles, `HASHLIST`, `Worker_DoTask`, VOS worker packet variants, string conversion helpers, and `NOTIFYCALLBACK`.

## Risks and Edge Cases

Several failure paths set `rc = FALSE` but the method returns `TRUE` at the end of `RefreshStatus` and `RefreshFilesets`, so callers relying only on the boolean may miss failures unless they inspect status and side effects. Refresh deletes and recreates all fileset objects, so stale child pointers are dangerous unless callers respect `Close` and notifications. `GetID` caches `NO_PARTITION` until name-to-ID succeeds; failure leaves later VOS requests under-specified.

## Test Signals

Tests should cover VOS partition lookup failure, empty and multi-volume aggregates, name and ID lookup after refresh, allocation recalculation using only read-write filesets, notification ordering, and ghost aggregates referenced only by VLDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.h

## Purpose

`c_agg.h` declares `AGGREGATE`, the AfsClass abstraction for a server partition and its fileset cache. It exposes aggregate status, identity, parent navigation, user parameters, and fileset lookup/enumeration APIs.

## Important APIs, Types, and Functions

`AGGREGATESTATUS` carries partition ID, total space, free space, and allocated quota. Public methods include `Close`, invalidation methods, `RefreshStatus`, `RefreshFilesets`, `GetIdentifier`, `OpenCell`, `OpenServer`, `GetName`, `GetDevice`, `GetID`, `GetStatus`, `GetGhostStatus`, user-param accessors, `OpenFileset`, and `FilesetFind*`. Private members include parent identifiers, partition strings, ghost and partition IDs, stale flags, fileset `HASHLIST`, hash keys, and cached status.

## Control Flow

The header establishes a lazy-refresh contract: status and filesets are refreshed only when their stale flags are set. Enumeration methods use `HENUM` handles and require a matching close. Object lifetime follows the wider AfsClass model where `Open*` increments the shared library critical-section/reference context and `Close` releases it.

## State and Persistence Behavior

`AGGREGATE` owns no durable storage. Its state is a memory cache of server partition data and child `FILESET` objects, invalidated by explicit calls and rebuilt from VOS.

## Dependencies and Integration Points

The class is a friend of `CELL`, `SERVER`, `FILESET`, and `IDENT`, allowing those classes to manipulate ghost flags, child lists, and cached status. It integrates with `LPIDENT`, `LPHASHLIST`, `LPHASHLISTKEY`, `VOLUMEID`, and `AGGREGATESTATUS`.

## Risks and Edge Cases

Friend-heavy access makes invariants distributed across `CELL`, `SERVER`, and `FILESET`. `size_t` is used for storage counts and quotas, so ABI assumptions can vary by target bitness. Callers must not hold enumeration objects across refresh/deletion.

## Test Signals

Compile and ABI checks should validate `AGGREGATESTATUS` layout. Behavioral tests should verify stale flag transitions, hash lookup by fileset name and ID, parent navigation, and deletion notification cascades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.cpp -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.h

## Purpose

`c_cell.h` declares `CELL`, the top-level AfsClass object representing one opened AFS cell and its cached servers, services, aggregates, filesets, users, and groups.

## Important APIs, Types, and Functions

`OP_CELL_REFRESH_ACCOUNT` describes single-account refresh events. Static APIs open, close, and reopen cells. Public methods invalidate and refresh server, VLDB, user, status, and whole-cell state; retrieve names, credentials, user params, and raw cell/KAS objects; enumerate/open servers, users, and groups. Private helpers free caches, close worker handles, reconcile VLDB entries, build group lists, and implement hash keys.

## Control Flow

The class contract is lazy and cache-backed. Public `Open*` and `Find*` methods refresh the relevant list before lookup unless a direct identifier is supplied. `RefreshAll` orchestrates server and user refresh according to requested library features.

## State and Persistence Behavior

Persistent AFS state is external. The class stores in-memory handles, credentials, stale flags, request count, server address/name caches, user/group caches, and a static process-wide list of cells.

## Dependencies and Integration Points

The header includes `afsclass.h`, `c_svr.h`, `c_agg.h`, `c_usr.h`, and `c_grp.h`. It grants friendship to all major object classes so they can share identifiers and update internal lists.

## Risks and Edge Cases

Because many fields are directly manipulated by friend classes, stale flags and ghost flags must remain consistent across files. `m_hKas` is deliberately left null to mean any KAS server, which can surprise callers expecting a concrete server handle.

## Test Signals

Header-level tests are compile and include-order checks. Functional tests should validate open/close reference behavior, enumerator contracts, credential replacement, stale flag transitions, and account refresh operation variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_cell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.cpp

## Purpose

`c_debug.cpp` implements debug-only assertion, tracing, debug-window output, and formatted logging helpers for the Windows AfsClass code. All executable content is compiled only under `DEBUG`.

## Important APIs, Types, and Functions

The file defines global `Debugstr debug`, static `Debugstr` window/buffer state, `AssertFn`, `Debugstr` stream operators for strings, numbers, pointers, rectangles, and `LPIDENT`, `Debugstr::Register`, `Initialize`, `OutString`, `Output`, `DebugWndProc`, `cxAvgWidth`, and `LogOut` constructor/destructor formatting support.

## Control Flow

`AssertFn` reports failed assertions to the debug stream and a message box. `Debugstr::operator<<(char*)` handles control tokens (`ANGLES_ON`, `ANGLES_OFF`, `LASTERROR`) or posts copied strings to a lazily created debug window. `OutString` writes to `OutputDebugString`, paints the window, handles newlines and screen wrap, and optionally records lines in the ring-like `gdata` buffer. `DebugWndProc` consumes posted strings, frees the allocated buffer, and repaints recorded lines. `LogOut` stores pointers to varargs on construction and formats them when destructed.

## State and Persistence Behavior

State is process-local debug UI state: window handle, font/brush, cursor positions, screen buffer, angle mode, registered/init flags, and `LogOut` temporary formatting state. There is no file persistence.

## Dependencies and Integration Points

The code depends on Win32 GDI/window APIs, `OutputDebugString`, `FormatMessage`, `MessageBox`, `LPIDENT` name getters, AfsClass allocation helpers, and debug macros from `c_debug.h`.

## Risks and Edge Cases

The debug path uses fixed-size buffers (`xMAX`, `yMAX`, 256-byte format buffers) and unbounded `strcat` into `gdata[gcY]`, so long debug strings can overflow in debug builds. `DebugWndProc` repaint loop never increments `gcY` inside the `for`, which appears to risk an infinite repaint loop. `LogOut` stores raw vararg pointers and assumes the pointed values remain alive until destruction.

## Test Signals

Debug-build smoke tests should exercise assertion failures, `LASTERROR`, `LPIDENT` formatting for each type, newlines, repaint, destruction cleanup, and long strings. Retail-build tests should confirm `ASSERT` still evaluates to a boolean without pulling in debug UI code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.h

## Purpose

`c_debug.h` defines the AfsClass debug interface. In retail builds it supplies a minimal `ASSERT` fallback; in debug builds it declares the debug stream, assertion function, debug output window, and delayed formatting helper.

## Important APIs, Types, and Functions

Retail `ASSERT(b)` evaluates the expression and returns `TRUE` or `FALSE`. Debug builds declare `AssertFn`, `Debugstr` stream operators, `Debugstr::DebugWndProc`, `OutString`, static window helpers, `LogOut`, control tokens `ANGLES_ON`, `ANGLES_OFF`, `LASTERROR`, constants for the debug window buffer, and global `debug`.

## Control Flow

The header only declares behavior. Its main control-flow effect is the `ASSERT` macro: debug builds route failed assertions to `AssertFn`, while retail builds allow failure paths to execute by returning false.

## State and Persistence Behavior

It declares static debug-window state in the `Debugstr` class but owns no storage directly except through the corresponding implementation.

## Dependencies and Integration Points

Debug builds include `windows.h` and use `LPIDENT` from `afsclass.h`. The header is included by debug code and by assertions in the identity/object model.

## Risks and Edge Cases

Changing retail `ASSERT` semantics can alter production control flow because many methods use `if (!ASSERT(...)) return NULL;`. The debug declarations are tightly coupled to Win32 and are not portable.

## Test Signals

Build both debug and retail configurations. Verify assertion expressions are evaluated in retail, debug stream overloads compile for expected types, and including this header does not conflict with platform `ASSERT` definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.cpp

## Purpose

`c_grp.cpp` implements `PTSGROUP`, the cached AfsClass representation of a PTS group. It retrieves group metadata, access bits, member lists, groups owned by the group, and groups to which the group belongs.

## Important APIs, Types, and Functions

Important methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `OpenCell`, `GetName`, `GetStatus`, `GetMembers`, `GetMemberOf`, `GetOwnerOf`, `ChangeIdentName`, and `RefreshStatus`. `PTSGROUPACCESS_TO_ACCOUNTACCESS` maps PTS group access constants to AfsClass account-access enums.

## Control Flow

Construction captures the parent cell identifier and group name, initializes stale status, and clears multisz caches. `RefreshStatus` clears old status and strings, opens the cell, calls `wtaskPtsGroupGet`, maps returned IDs/access fields/owner/creator, then enumerates members, owned groups, and group memberships through PTS begin/next/done worker tasks. Public getters refresh first, then return copied status or cloned multisz strings. `ChangeIdentName` updates the associated `IDENT`, rehashes it, changes the group name, and updates the parent cell group hash.

## State and Persistence Behavior

State is in-memory cached `PTSGROUPSTATUS` plus three allocated multisz lists. No persistence is owned; refresh reflects PTS database state. Rename support updates local identity/cache state after an external operation.

## Dependencies and Integration Points

The file depends on `CELL` for `hCell`, `IDENT`, `NOTIFYCALLBACK`, PTS worker tasks, `FormatMultiString`, `CloneMultiString`, and string conversion helpers.

## Risks and Edge Cases

`RefreshStatus` sets `rc = FALSE` on failures but returns `TRUE` unconditionally, so callers may receive zeroed/partial status without a false return. Enumeration loops ignore status on `GetNext` and treat any failure as end-of-list. `ChangeIdentName` depends on parent hash-list update discipline.

## Test Signals

Tests should cover groups with no members, nested group memberships, owned groups, failed PTS lookups, rename rehashing, cloned multisz ownership, and notification begin/end behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.h

## Purpose

`c_grp.h` declares `PTSGROUP`, the PTS group wrapper in the AfsClass object model.

## Important APIs, Types, and Functions

`PTSGROUPSTATUS` reports member count, PTS IDs, access controls, owner, and creator. The class exposes close/invalidate/refresh, identity and parent-cell access, name/status getters, user-param accessors, and multisz getters for members, memberships, and owned groups. `ChangeIdentName` is public for internal rename handling.

## Control Flow

The public API follows the standard lazy-refresh pattern: getter methods refresh status when stale, then copy cached values to the caller.

## State and Persistence Behavior

The class stores parent cell identity, group name, identifier pointer, stale flag, status snapshot, and three allocated multisz relationship lists. Persistent data lives in PTS.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `LPIDENT`, `ACCOUNTACCESS`, `HENUM` conventions, and friend access from `CELL`, `IDENT`, and `USER`.

## Risks and Edge Cases

The class exposes internally intended `ChangeIdentName` publicly, making incorrect external use possible. Callers own cloned multisz results and must free them with the library's string-freeing convention.

## Test Signals

Compile coverage should ensure `PTSGROUPSTATUS` layout and include order. Runtime tests should validate refresh staleness, identity update on rename, and multisz clone lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_grp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.cpp

## Purpose

`c_ident.cpp` implements `IDENT`, the process-wide stable identifier registry for cells, servers, services, aggregates, filesets, users, and groups. Identifiers preserve enough names and IDs to reopen the current backing object and carry caller user data.

## Important APIs, Types, and Functions

It implements constructors for every object type, type predicates, `Open*` methods, `Get*` hierarchy methods, name/ID getters, user-param accessors, enumeration, static `Find*` helpers, `RemoveIdentsInCell`, `Update`, and hash key callbacks for type/server, fileset ID, fileset name, and account name.

## Control Flow

`InitClass` lazily creates the global `x_lIdents` hash list and keys. Each constructor extracts canonical names/IDs from the source object and adds the identifier to the global list. `Open*` methods reopen the cell and walk through parent objects to find the current backing object. `FindIdent` selects the fastest key: fileset ID for volume lookups, fileset-name key for certain cross-server searches, or type/server key otherwise. Fileset identity handling is special because volumes can move and read-only replicas can share IDs; aggregate matching is required for probable replicas.

## State and Persistence Behavior

All state is in memory: type, cell/server/service/aggregate/fileset/account strings, volume ID, caller user pointer, and manual reference count. Identifiers persist for the life of the process until removed from the hash list or destroyed, and can outlive a particular backing object.

## Dependencies and Integration Points

The file depends on all object classes, `HASHLIST`, `AfsClass_GenFullUserName`, server name shortening, AfsClass assertion semantics, and direct friend access to object internals.

## Risks and Edge Cases

The registry is global and mostly initialized without setting an explicit critical section in this file, so thread safety depends on `HASHLIST` defaults and higher-level `AfsClass_Enter`. `RemoveIdentsInCell` deletes identifiers while iterating the same list. The account-name hash ignores instance in the key and filters afterward, which is correct but collision-heavy for common names. `FindNext` for identifier enumeration only returns filesets after the first item, which makes general `FindFirst/FindNext` enumeration asymmetric.

## Test Signals

Tests should cover identity reuse after fileset move, read-only replica lookup, user names with instances, group/user name collisions, service/aggregate reopen paths, user-param persistence, refcount increments/decrements by owning objects, and global enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.h

## Purpose

`c_ident.h` declares `IDENT`, the typed handle used by AfsClass callers to refer to cached AFS objects without holding direct object pointers.

## Important APIs, Types, and Functions

`IDENTTYPE` enumerates supported object types. Public methods expose type predicates, refcount, reopen methods for each object kind, hierarchy getters, name/ID getters, user-param accessors, global enumeration, and static find helpers for servers, aggregates, filesets, users, and groups. Private members store canonical names, volume ID, user pointer, refcount, global hash list, and hash keys.

## Control Flow

The header defines a value-handle contract backed by a global registry. Callers use `LPIDENT` to reopen objects on demand; object classes create or find identifiers and increment reference counters when exposing them.

## State and Persistence Behavior

Identifiers are process-local state. They mirror object names and IDs and can survive object refreshes, but they are not durable across process restarts.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `VOLUMEID`, `HENUM`, `LPHASHLIST`, and friend access from every major object class.

## Risks and Edge Cases

Manual refcounting is separate from C++ object lifetime and easy to misuse. Because identifiers contain copied names, all rename/move paths must call `Update` after modifying fields that affect hash keys.

## Test Signals

Compile tests should validate public ABI and friend usage. Runtime tests should validate find/open behavior for all types, refcount observations, and hash updates after rename/move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.cpp

## Purpose

`c_identlist.cpp` implements `IDENTLIST`, a small hash-list-backed container for unique `LPIDENT` pointers.

## Important APIs, Types, and Functions

Implemented methods are constructor/destructor, `Add`, `Remove`, `RemoveAll`, `CopyFrom`, `GetCount`, `fIsInList`, `FindFirst`, `FindNext`, and `FindClose`.

## Control Flow

Construction allocates a `HASHLIST`. `Add` inserts uniquely, `Remove` removes a pointer, and `RemoveAll` repeatedly removes the first object until empty. `CopyFrom` clears the current list and enumerates another `IDENTLIST`, adding each identifier. Enumeration wraps `HASHLIST` enumeration and returns `LPIDENT` objects without opening backing objects.

## State and Persistence Behavior

The list owns only the container, not the identifiers. It does not adjust `IDENT::m_cRef` and does not persist data.

## Dependencies and Integration Points

It depends on `HASHLIST`, `LPIDENT`, `HENUM`, `New`, and `Delete`. It is a utility for callers that need sets of object identifiers.

## Risks and Edge Cases

Because identifiers are borrowed, entries can become stale if the global registry deletes an `IDENT` while it is in a list. The list does not set a critical section, so thread safety depends on external synchronization. `CopyFrom` does not close the source enumeration explicitly after natural exhaustion.

## Test Signals

Tests should cover duplicate adds, removing absent/present identifiers, copying from another list, empty enumeration, and behavior when the source list is empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.h

## Purpose

`c_identlist.h` declares `IDENTLIST`, a lightweight unique set of `LPIDENT` handles.

## Important APIs, Types, and Functions

The class exposes add/remove/remove-all, copy, count, membership check, and `HENUM`-style iteration. Its only private member is `LPHASHLIST m_lIdents`.

## Control Flow

There is no executable flow in the header; it establishes the container API used by client code and possibly selection/filter workflows.

## State and Persistence Behavior

The list stores borrowed identity pointers in memory. It owns no persistent data and no backing AFS objects.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `LPIDENT`, `LPIDENTLIST`, `HENUM`, and `HASHLIST` from internal infrastructure.

## Risks and Edge Cases

The ownership contract is implicit: adding an identifier does not retain it. Callers must ensure identifiers remain valid and close enumeration handles.

## Test Signals

Compile checks plus simple unit tests for uniqueness, copy semantics, count, and enumeration close behavior are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.cpp

## Purpose

`c_notify.cpp` implements the global callback registry and dispatch path for AfsClass notifications.

## Important APIs, Types, and Functions

It defines static `NOTIFYCALLBACK::nNotifyList` and `aNotifyList`, constructor/destructor registration, overloads of `SendNotificationToAll`, and instance `SendNotification`.

## Control Flow

Construction stores the supplied function/user value, finds a free slot, and expands the callback array in chunks of four with `REALLOC`. Destruction nulls any matching slot. `SendNotificationToAll` normalizes overloads into a full parameter set, fills `NOTIFYPARAMS`, then calls each registered callback. `SendNotification` invokes the user function inside a C++ exception guard and returns false if the callback fails or throws.

## State and Persistence Behavior

State is a process-global dynamic array of callback object pointers. There is no persistence and no event queue; notifications are synchronous calls on the sender's thread.

## Dependencies and Integration Points

This module is used throughout cell/server/aggregate/fileset/service/user/group refresh and mutation code. It depends on `NOTIFYEVENT`, `NOTIFYPARAMS`, `LPIDENT`, AfsClass allocation macros, and debug `DebugBreak`.

## Risks and Edge Cases

The global callback list is not visibly synchronized here, so concurrent register/unregister/dispatch can race unless callers hold the AfsClass critical section. `lstrcpy` into fixed `MAX_PATH` buffers can overflow if callers pass longer strings. A callback can unregister itself during dispatch, altering later slots.

## Test Signals

Tests should cover multiple callbacks, callback removal, callback failure returning false, thrown exceptions, string parameter propagation, and dispatch during object refresh notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.h

## Purpose

`c_notify.h` defines the AfsClass notification event taxonomy, event parameter structure, callback signature, and callback registration class.

## Important APIs, Types, and Functions

`NOTIFYEVENT` enumerates lifecycle, invalidate, refresh, cell-open, VLDB sync, server file/key/list operations, service operations, fileset operations, command/salvage operations, and user/group operations. `NOTIFYPARAMS` carries up to two identifiers, two strings, a progress/extra DWORD, status, and callback user value. `NOTIFYCALLBACKPROC` is the callback signature. `NOTIFYCALLBACK` registers/unregisters and dispatches through static `SendNotificationToAll` overloads.

## Control Flow

The header documents which fields are meaningful for many event types. Implementations call the overload that matches their context; the `.cpp` funnels these into a full parameter record.

## State and Persistence Behavior

The header declares the global callback list as static class data. Notifications are transient and synchronous.

## Dependencies and Integration Points

Every AfsClass object and operation implementation uses these events to report creation, destruction, refresh progress, and administrative operations to UI or monitoring clients.

## Risks and Edge Cases

Adding events must preserve numeric compatibility because `evtUser = 500` reserves a user range. Misusing parameter fields can break clients that rely on the documented per-event conventions.

## Test Signals

Compile tests should verify enum and struct ABI. Integration tests should assert expected begin/end/create/destroy sequences for server, service, fileset, and account workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.cpp

## Purpose

`c_set.cpp` implements `FILESET`, the cached representation of an AFS volume/fileset on an aggregate. It tracks VOS status, volume IDs, type/state, ghost status, and identifier relationships to read-write/read-only/backup variants.

## Important APIs, Types, and Functions

Key methods include constructor/destructor, `GetIdentifier`, `GetReadWriteIdentifier`, `GetReadOnlyIdentifier`, `GetCloneIdentifier`, `Invalidate`, `RefreshStatus`, parent open methods, `GetStatus`, `GetGhostStatus`, `ProbablyReplica`, and `SetStatusFromVOS`.

## Control Flow

Construction captures parent aggregate/server/cell identifiers, stores the volume ID and name, initializes status, and invalidates aggregate allocation. `GetIdentifier` searches existing file-set identifiers by volume ID and reuses an unreferenced match in the same cell, requiring the same aggregate for probable read-only replicas, then updates moved fileset location/name fields before incrementing refcount. `RefreshStatus` only queries VOS when stale and the fileset has a server-entry ghost flag, opens server and VOS handles, optionally resolves partition ID from the parent aggregate, calls `wtaskVosVolumeGet`, updates status via `SetStatusFromVOS`, and invalidates aggregate allocation. Variant identifier methods refresh and find read-write/read-only/backup identifiers by IDs or `.readonly` naming.

## State and Persistence Behavior

State is an in-memory snapshot of VOS volume metadata and VLDB-derived bits. Persistent volume state is external. The object invalidates parent allocation when quota/status changes can affect aggregate accounting.

## Dependencies and Integration Points

The file depends on `AGGREGATE`, `SERVER`, `CELL`, `IDENT`, VOS worker packets, `NOTIFYCALLBACK`, AfsClass time conversion, and file-set type/state constants from the header.

## Risks and Edge Cases

`RefreshStatus` returns `TRUE` even after setting `rc = FALSE`, matching a recurring pattern in this code. Filesets that exist only in VLDB (`GHOST_HAS_VLDB_ENTRY` without server entry) do not query VOS and may retain VLDB-only status. `ProbablyReplica` relies on `.readonly` naming, while real identity constraints are volume-ID based.

## Test Signals

Tests should cover VOS status mapping for all volume states, read-write/read-only/backup ID lookup, moved fileset identity reuse, VLDB-only ghost status, aggregate allocation invalidation, and failures opening server/VOS handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.h

## Purpose

`c_set.h` declares `FILESET`, the AfsClass wrapper around an AFS volume/fileset.

## Important APIs, Types, and Functions

It defines `FILESETSTATE` bit flags for VOS and VLDB states, `FILESETTYPE` for read-write, replica, and clone, and `FILESETSTATUS` with IDs, timestamps, file count, quota, usage, type, and state. `FILESET` exposes close/invalidate/refresh, parent navigation, identifier getters for related variants, name/ID/status/ghost getters, and user-param accessors.

## Control Flow

The header declares a lazy-refresh object. Status refresh pulls server data, while `RefreshStatus_VLDB` is declared for VLDB refresh integration even though this source set does not show an implementation in `c_set.cpp`.

## State and Persistence Behavior

The class caches volume identity, parent identities, ghost flags, stale status, and the last `FILESETSTATUS`. Durable volume state remains in VOS/VLDB.

## Dependencies and Integration Points

It integrates with `CELL`, `SERVER`, `AGGREGATE`, `IDENT`, `VOLUMEID`, `SYSTEMTIME`, and ghost-state handling performed by `CELL::RefreshVLDB`.

## Risks and Edge Cases

Status bit masks reserve high bits for VLDB state; callers must preserve `fsMASK_VLDB` when updating VOS status. Missing or separately implemented `RefreshStatus_VLDB` should be checked during linking or broader-source review.

## Test Signals

Compile checks should validate `FILESETSTATUS` layout and that all declared methods link. Runtime tests should verify type/state mapping, related identifier lookup, and ghost-status visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.cpp

## Purpose

`c_svc.cpp` implements `SERVICE`, the cached representation of a BOS process/service on an AFS server.

## Important APIs, Types, and Functions

Implemented methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `RefreshStatus`, `GetName`, parent open methods, `GetStatus`, and user-param accessors. `RefreshStatus` handles a synthetic `BOS` service and real BOS process status.

## Control Flow

Construction stores the parent server identifier and service name, initializes stale status, and should store the parent cell identifier. `RefreshStatus` opens the parent server and BOS object, synthesizes a running simple service status for the `BOS` pseudo-service, or calls BOS worker tasks to get process info, execution state, notifier, and parameter list. It concatenates parameters with spaces and strips trailing CR/LF from aux status, params, and notifier before updating the cache.

## State and Persistence Behavior

State is an in-memory `SERVICESTATUS` snapshot and stale flag. The object reflects BOS process configuration and runtime state but does not persist changes itself.

## Dependencies and Integration Points

The file depends on `SERVER` for BOS handles, `IDENT`, BOS worker tasks, `NOTIFYCALLBACK`, time conversion for the synthetic BOS status, and `SERVICESTATUS` from the header.

## Risks and Edge Cases

The constructor contains `m_lpiCell = m_lpiCell;`, leaving the cell identifier uninitialized instead of copying from the parent server. `OpenCell` can therefore dereference invalid state. Parameter concatenation uses fixed `cchRESOURCE` buffers and `lstrcat`, so many/long parameters can overflow. `RefreshStatus` returns `TRUE` even when `rc` is false.

## Test Signals

Tests should cover synthetic BOS status, stopped/missing process state fallback, notifier and parameter enumeration, CR/LF stripping, long parameter lists, failure status propagation, and `OpenCell` on a service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.h

## Purpose

`c_svc.h` declares `SERVICE`, the AfsClass object for a BOS service/process and related status/key types.

## Important APIs, Types, and Functions

It defines `AFSSERVICETYPE`, `SERVICESTATE`, `SERVICESTATUS`, `ENCRYPTIONKEY`, and `ENCRYPTIONKEYINFO`. `SERVICE` exposes close/invalidate/refresh, identity and parent navigation, name/status getters, and user-param accessors.

## Control Flow

The class follows the lazy-refresh pattern and is normally obtained from a `SERVER` service list or opened by name.

## State and Persistence Behavior

The service object caches BOS process status, parent identifiers, service name, and stale flag. Key structs are shared by server-key APIs declared elsewhere.

## Dependencies and Integration Points

It depends on `afsclass.h`, Win32 `SYSTEMTIME`, AfsClass identifiers, and server/service management operations in `afsclassfn.h`.

## Risks and Edge Cases

`SERVICESTATUS` contains fixed-size strings for params/notifier/aux status. Callers should expect truncation or overflow risk in old implementation paths. Service state is a snapshot and must be invalidated or refreshed before use after operations.

## Test Signals

Compile tests should validate status/key ABI. Functional tests should verify service enumeration, status refresh, start/stop/restart operation refresh, and user-param attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.cpp

## Purpose

`c_svr.cpp` implements `SERVER`, the cached representation of an AFS file/database server within a cell. It owns service and aggregate child caches, BOS/VOS server handles, monitor state, reachability probing, and server refresh orchestration.

## Important APIs, Types, and Functions

Important methods include constructor/destructor, `FreeAll`, `FreeAggregates`, `FreeServices`, `SendDeleteNotifications`, `GetIdentifier`, `OpenBosObject`, `CloseBosObject`, `OpenVosObject`, `CloseVosObject`, invalidation methods, `RefreshAggregates`, `RefreshServices`, `RefreshStatus`, `ShortenName`, `SetMonitor`, `CanTalkToServer`, `RefreshAll`, aggregate open/enumeration, service open/enumeration, and hash key callbacks. Static refresh-section helpers implement cancellable reachability probes.

## Control Flow

Construction captures the parent cell ID, initializes BOS/VOS handle counters, child hash lists, monitor flags, and stale flags. `OpenBosObject` and `OpenVosObject` lazily open worker handles and increment request counters; close methods decrement and close when the count reaches zero. Aggregate refresh clears current aggregates, opens VOS, enumerates partitions, creates `AGGREGATE` objects, seeds storage totals/free space, marks server-entry ghost state, and sends create notifications. Service refresh clears services, opens BOS, creates a synthetic `BOS` service, enumerates BOS process names, creates `SERVICE` objects, and notifies. `CanTalkToServer` spawns a worker thread to probe BOS and VOS quickly and allows cancellation through `AfsClass_SkipRefresh`. `RefreshAll` probes reachability, disables monitoring on failure, refreshes aggregates/filesets and services with progress notifications, then optionally triggers scoped VLDB refresh.

## State and Persistence Behavior

Server state is in-memory: names, BOS/VOS handles, request counters, ghost flags, monitor flag, last status, capability flags, child lists, stale flags, address status, and deletion marker. Persistent server configuration is external BOS/VOS/database-server state.

## Dependencies and Integration Points

The file integrates heavily with `CELL`, `AGGREGATE`, `SERVICE`, `IDENT`, `Worker_DoTask`, BOS/VOS/client worker packets, notification events, Win32 threads/critical sections, and global refresh progress state.

## Risks and Edge Cases

Handle counters must balance exactly; leaks or double-close will leave BOS/VOS handles stale. `RefreshAggregates`, `RefreshServices`, and `RefreshStatus` set `rc = FALSE` but return `TRUE`, which can mask failures. The reachability thread may keep running after cancellation, so it uses `pcsRefSec` to guard server pointers; mistakes here can become use-after-free. Monitoring off frees children and changes cell unmonitored count, so repeated toggles need careful tests.

## Test Signals

Tests should cover BOS/VOS open/close nesting, server address refresh and hash update, service/aggregate enumeration, unreachable server monitor disable, refresh cancellation, progress notifications, scoped VLDB refresh after server refresh, short/long server names, and deletion cascades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.h

## Purpose

`c_svr.h` declares `SERVER`, the AfsClass object for a server in a cell, including cached child aggregate/service lists and BOS/VOS handle management.

## Important APIs, Types, and Functions

`SERVERSTATUS` stores up to `AFSCLASS_MAX_ADDRESSES_PER_SITE` socket addresses. Public APIs include close, invalidation, refresh of status/services/aggregates/all, `ShortenName`, monitor get/set, identity/name/status/ghost/user-param accessors, BOS/VOS object open/close, aggregate open/enumeration, and service open/enumeration. Private members store parent cell identity, handles, counters, ghost/monitor state, child hash lists, capability flags, stale flags, status, and deletion marker.

## Control Flow

The header describes a lazy, monitored server cache. When monitoring is disabled, child data is freed and refreshes are skipped; when enabled, refresh can repopulate services, aggregates, filesets, and VLDB-derived information.

## State and Persistence Behavior

Server state is a process-local cache and live worker-handle holder. Persistent server configuration and volume state remain in AFS services.

## Dependencies and Integration Points

It depends on `afsclass.h`, socket structures, `HASHLIST`, `SERVICE`, `AGGREGATE`, `IDENT`, and Win32 worker-thread support in the implementation.

## Risks and Edge Cases

The class combines cache ownership, handle reference counting, and refresh threading, so lifetime correctness depends on balanced `Open*Object`/`Close*Object` and `Open*`/`Close` pairs. `m_fVLDBOutOfDate` is noted in the implementation as a missing-field fix, suggesting historical state consistency risk.

## Test Signals

Compile tests should validate class layout and method linkage. Runtime tests should cover monitor toggling, child enumeration, handle nesting, status address limits, and refresh-all progress/cancel behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_svr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.cpp

## Purpose

`c_usr.cpp` implements `USER`, the cached AfsClass representation of a KAS/PTS user account. It merges authentication database fields, protection database fields, group memberships, and group ownership into one status object.

## Important APIs, Types, and Functions

Implemented methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `OpenCell`, `GetName`, `GetStatus`, user-param accessors, `GetOwnerOf`, `GetMemberOf`, `RefreshStatus`, `SplitUserName`, and `IsMachineAccount`. `USERACCESS_TO_ACCOUNTACCESS` maps PTS access bits to account-access enums.

## Control Flow

Construction captures parent cell identity and principal/instance strings, initializes stale status, and clears multisz caches. `RefreshStatus` clears old state, builds the full user name, opens the cell, queries KAS principal data, maps admin/ticket/encryption/password/key/timestamp fields, queries PTS user data, maps quotas/IDs/owner/creator/access, enumerates PTS memberships and owned groups, and sends refresh notifications. Public list getters clone the cached multisz strings. `SplitUserName` separates principal and instance on the first dot unless the name is a machine account composed only of digits and dots.

## State and Persistence Behavior

The object caches `USERSTATUS`, membership/owner multisz strings, parent identity, user name/instance, and stale flag. It owns no durable state; refresh reflects KAS and PTS databases.

## Dependencies and Integration Points

The file depends on `CELL`, `IDENT`, KAS and PTS worker tasks, `ENCRYPTIONKEY` from service headers, AfsClass string/time helpers, and notifications.

## Risks and Edge Cases

`RefreshStatus` intentionally treats missing PTS as nonfatal but missing KAS as fatal only internally, then returns `TRUE` unconditionally, so callers must inspect `fHaveKasInfo`/`fHavePtsInfo` and status. Machine-account detection preserves dotted IP-like names as principals without instances. `lpiLastMod` may be null if the modifier account is not cached.

## Test Signals

Tests should cover KAS-only, PTS-only, and combined users; principal instances; machine-account split behavior; memberships and owned groups; missing modifier identities; password/key fields; and error status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.h

## Purpose

`c_usr.h` declares `USER`, the AfsClass wrapper for KAS/PTS user accounts.

## Important APIs, Types, and Functions

`USERSTATUS` contains presence flags plus nested `KASINFO` and `PTSINFO` structures for auth settings, expiration/password/key fields, PTS quotas, IDs, owner/creator, and access controls. The class exposes close/invalidate/refresh, identity and cell access, name/status getters, user-param accessors, owner/member group list getters, and static helpers `SplitUserName` and `IsMachineAccount`.

## Control Flow

The class follows lazy refresh: status and relationship lists are loaded on demand and copied/cloned to callers.

## State and Persistence Behavior

The class caches account status and multisz group lists in memory. Persistent account data is external to KAS/PTS.

## Dependencies and Integration Points

It includes `afsclass.h` and `c_svc.h` for `ENCRYPTIONKEY`. It is managed by `CELL`, represented by `IDENT`, and related to `PTSGROUP`.

## Risks and Edge Cases

The single status structure merges KAS and PTS data that can independently exist or fail. Consumers must check `fHaveKasInfo` and `fHavePtsInfo` before using nested fields. Caller ownership of cloned multisz lists must be honored.

## Test Signals

Compile checks should validate `USERSTATUS` ABI. Runtime tests should validate refresh, split-name edge cases, missing KAS/PTS halves, group-list cloning, and identity/user-param behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/c_usr.h -->
