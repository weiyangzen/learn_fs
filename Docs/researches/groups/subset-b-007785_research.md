# Research Report: subset-b-007785

This grouped report covers the OpenAFS `src/libadmin/test` KAS/PTS/util/VOS command wrappers and the `src/libadmin/vos` public volume-admin library interface and implementation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/kas.c -->
# sources/distributed-fs/openafs/src/libadmin/test/kas.c

## Purpose

`kas.c` implements the KAS-related commands for the `afscp` libadmin test client. It is not the KAS library itself; it is a command-line adapter around `afs_kasAdmin` APIs. Each `DoKas*` function reads parsed `cmd_syndesc` parameters, maps them into libadmin structs such as `kas_identity_t`, calls a `kas_*` API through the global `cellHandle`, and prints returned structures for manual inspection.

## Important APIs, Types, and Functions

The file exposes command handlers for principal lifecycle (`DoKasPrincipalCreate`, `DoKasPrincipalDelete`, `DoKasPrincipalGet`, `DoKasPrincipalList`), credential/key management (`DoKasPrincipalKeySet`, `DoKasPrincipalLockStatusGet`, `DoKasPrincipalUnlock`, `DoKasPrincipalFieldsSet`), and server inspection (`DoKasServerStatsGet`, `DoKasServerDebugGet`, `DoKasServerRandomKeyGet`). `SetupKasAdminCmd` registers the user-facing command names and their parameters with the AFS command package.

Important local helpers are `GetIntFromString`, `Print_kas_principalEntry_p`, `Print_kas_serverStats_p`, and `Print_kas_serverDebugInfo_p`. They convert text arguments and serialize libadmin return structures to stdout. The command handlers rely on `ERR_EXT` and `ERR_ST_EXT` from `common.h` for fatal error reporting.

## Control Flow

All KAS command handlers first reject `existing_tokens`, because the test client records that tokens came from `afsclient_TokenGetExisting`, which this wrapper treats as incompatible with KAS operations. Principal commands populate a `kas_identity_t` from `-principal` and optional `-instance`, call the matching `kas_Principal*` API, and return zero on success. List commands follow the begin/next/done iterator convention and treat `ADMITERATORDONE` as normal termination. Server stats/debug commands open a KAS server handle with `kas_ServerOpen`, query it, print the result, and close the handle.

`DoKasPrincipalFieldsSet` is the densest path. It parses mutually exclusive flag pairs into optional pointer arguments for `kas_PrincipalFieldsSet`. The API contract is pointer-based: a null pointer means no update, and a non-null pointer carries the new setting.

## State and Persistence Behavior

This test wrapper has no local persistence. It mutates remote KAS database state through libadmin calls: creating/deleting principals, setting keys, unlocking accounts, and changing account policy fields. Server stats/debug/random-key commands are read-only except for the remote RPC work they trigger.

## Dependencies and Integration Points

The file includes `kas.h`, which pulls in OpenAFS admin, KAS, util, client, RX, and command headers. Runtime integration depends on globals from the larger test program: `cellHandle` and `existing_tokens`. The registered commands become part of `afscp` via `SetupKasAdminCmd`.

## Risks and Edge Cases

Several command-adapter defects are visible. `DoKasPrincipalDelete` and `DoKasPrincipalGet` copy `as->parms[PRINCIPAL]` into `user.instance` when `-instance` is present, so instance-qualified operations can target the wrong identity. `DoKasPrincipalFieldsSet` has repeated conflict-check mistakes: the `-noencrypt` and `-nochangepassword` paths check `have_tgs` instead of the corresponding setting, and the second reuse-password block tests `REUSEPASSWORD` instead of `NOREUSEPASSWORD`, making `-noreusepassword` unreachable and making `-reusepassword` immediately conflict with itself. The code uses `strcpy` into fixed-size KAS fields, so it relies on upstream command/API limits rather than local bounds checks.

`GetIntFromString` returns from `ERR_EXT` paths only if the macro exits nonlocally; as plain C it has no final return after the error path. Numeric parsing uses `strtoul` into `int`, so negative and overflow handling is weak.

## Test Signals

Useful tests are command-level integration tests that create principals with and without instances, list them, fetch them, set keys, and exercise each mutually exclusive field pair. A focused regression should verify that `-instance` reaches `kas_identity_t.instance` and that `-noreusepassword`, `-noencrypt`, and `-nochangepassword` reject only their true opposites. Manual server tests can validate iterator completion on `KasPrincipalList` and handle closure for server stats/debug queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/kas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/kas.h -->
# sources/distributed-fs/openafs/src/libadmin/test/kas.h

## Purpose

`kas.h` is the local header for the KAS portion of the `afscp` libadmin test client. It gathers the OpenAFS headers needed by `kas.c` and exposes the single setup entry point used by the main test program.

## Important APIs, Types, and Functions

The header includes standard C headers, pthreads, RX/RX stats, `afs_Admin.h`, `afs_kasAdmin.h`, `afs_utilAdmin.h`, `afs_clientAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupKasAdminCmd(void)` and imports `existing_tokens`, which is set by `afscp.c` when the client obtains pre-existing tokens.

## Control Flow

There is no executable control flow in the header. Its main integration role is making `SetupKasAdminCmd` visible and sharing the `existing_tokens` guard state with the KAS command handlers.

## State and Persistence Behavior

The header declares external process state but stores none itself. The `existing_tokens` flag affects whether KAS commands are allowed to reach remote KAS database state.

## Dependencies and Integration Points

This file is tightly coupled to the libadmin test harness. `common.h` is expected to provide `cellHandle`, error macros, and common command argument helpers used by `kas.c`.

## Risks and Test Signals

The comment notes that existing tokens are "incompatable" with KAS operations; callers need tests ensuring that `SetupKasAdminCmd` commands consistently reject that mode. Because the header includes many heavy dependencies, build tests should cover both Unix and any supported pthread/RX configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/kas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/pts.c -->
# sources/distributed-fs/openafs/src/libadmin/test/pts.c

## Purpose

`pts.c` implements PTS-related command handlers for the `afscp` libadmin test client. It adapts parsed command arguments to `afs_ptsAdmin` calls and prints group/user entries and iterator results for manual validation.

## Important APIs, Types, and Functions

The file covers group membership and metadata operations (`DoPtsGroupMemberAdd`, `DoPtsGroupOwnerChange`, `DoPtsGroupCreate`, `DoPtsGroupGet`, `DoPtsGroupDelete`, `DoPtsGroupModify`, `DoPtsGroupRename`, `DoPtsGroupMemberList`, `DoPtsGroupMemberRemove`, `DoPtsGroupMaxGet`, `DoPtsGroupMaxSet`) and user operations (`DoPtsUserCreate`, `DoPtsUserDelete`, `DoPtsUserGet`, `DoPtsUserRename`, `DoPtsUserModify`, `DoPtsUserMaxGet`, `DoPtsUserMaxSet`, `DoPtsUserMemberList`, `DoPtsOwnedGroupList`). `SetupPtsAdminCmd` binds all handlers to command names and parameter specifications.

Local helpers parse numeric ids (`GetIntFromString`), parse access labels into `pts_groupAccess_t` and `pts_userAccess_t`, and print `pts_GroupEntry_t` / `pts_UserEntry_t` structures.

## Control Flow

Handlers are thin and synchronous. They fetch required command parameters by enum index, convert text where needed, call a libadmin function using the global `cellHandle`, and report errors through `ERR_ST_EXT`. List operations use begin/next/done iterators and expect `ADMITERATORDONE` after the final item. `DoPtsUserModify` uses an update flag bitmask: quota changes set `PTS_USER_UPDATE_GROUP_CREATE_QUOTA`, permission changes set `PTS_USER_UPDATE_PERMISSIONS`, and partial permission updates are rejected unless all three user permission fields are supplied.

## State and Persistence Behavior

There is no local persistence. Group/user create, delete, rename, owner-change, membership, max-id, and permission calls mutate the remote protection database through libadmin. Get/list commands are read-only.

## Dependencies and Integration Points

`pts.c` includes `pts.h`, which supplies admin and command headers plus `common.h`. The file integrates with the shared test-client command registry through `SetupPtsAdminCmd` and with the global `cellHandle`.

## Risks and Edge Cases

`DoPtsGroupCreate` reports `pts_GroupMemberAdd` on group-create failure, which makes diagnostics misleading. `DoPtsGroupMaxGet` and `DoPtsUserMaxGet` retrieve values but do not print them, reducing the usefulness of those commands. `GetIntFromString` has the same weak overflow/negative handling and missing plain-C error-path return shape seen in other test files.

The group permission parser accepts `"owner"`, `"group"`, and `"any"` for all group permission fields, but the command help for some fields advertises narrower sets. Enforcement is entirely by parser, so this may accept values the command text implies should be invalid. The group update command requires all five group permissions and has a typo in the enum name (`LISTDELTE`), although the enum index still matches registration order.

## Test Signals

Regression coverage should create a user and group, add/remove membership, list both directions, rename objects, update group and user permissions, and verify iterator termination. Negative tests should cover invalid access strings, partial user permission updates, and max-id commands producing useful observable output if behavior is improved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/pts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/pts.h -->
# sources/distributed-fs/openafs/src/libadmin/test/pts.h

## Purpose

`pts.h` is the local include surface for `pts.c`, the PTS command group in the `afscp` libadmin test client.

## Important APIs, Types, and Functions

It includes standard C headers, pthreads, `afs_Admin.h`, `afs_ptsAdmin.h`, `afs_utilAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupPtsAdminCmd(void)`.

## Control Flow

The file contains no executable logic. It supports command registration by exposing the setup function to the test-client main program.

## State and Persistence Behavior

No state is stored here. State changes occur only in `pts.c` through calls to the remote protection database APIs.

## Dependencies and Integration Points

The header couples the PTS command wrapper to the shared libadmin test harness and the OpenAFS PTS admin API. `common.h` provides shared globals and error/argument helpers.

## Risks and Test Signals

Build coverage should ensure the header remains compatible with the PTS admin headers and command package. Since only one function is exported, accidental signature drift in `SetupPtsAdminCmd` would be caught by compiling the test program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/pts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/util.c -->
# sources/distributed-fs/openafs/src/libadmin/test/util.c

## Purpose

`util.c` implements utility commands for the `afscp` libadmin test client. These commands expose error-code translation, database server discovery, and hostname-to-address conversion from `afs_utilAdmin`.

## Important APIs, Types, and Functions

`DoUtilErrorTranslate` calls `util_AdminErrorCodeTranslate` and prints the numeric code and text. `DoUtilDatabaseServerList` uses `util_DatabaseServerGetBegin`, `util_DatabaseServerGetNext`, and `util_DatabaseServerGetDone` to enumerate database servers for a named cell. `DoUtilNameToAddress` calls `util_AdminServerAddressGetFromName` and prints the IPv4 address. `SetupUtilAdminCmd` registers these three commands.

## Control Flow

The control flow is linear. The database-server list command follows the standard libadmin iterator pattern and treats `ADMITERATORDONE` as normal completion. Address output converts host-order integer addresses to network order before passing them to `inet_ntoa`.

## State and Persistence Behavior

These commands are read-only. They do not mutate local files or OpenAFS databases. The only state is transient iterator state allocated by the util admin library.

## Dependencies and Integration Points

The file includes `util.h`, which provides OpenAFS util admin declarations, socket address headers on Unix, and test-harness helpers. Only `UtilDatabaseServerList` adds common cell/auth arguments; error translation and name lookup intentionally omit common arguments because they do not need a cell handle.

## Risks and Edge Cases

`DoUtilErrorTranslate` parses errors with `atoi`, so malformed input silently becomes zero. `DoUtilDatabaseServerList` assumes the iterator is cleaned up only on successful begin; if a later next call fails, it reports through the fatal macro before explicitly reaching done. `inet_ntoa` returns static storage, which is fine for immediate printing but not reusable.

## Test Signals

Useful checks include translating known admin errors, resolving a valid server name, rejecting an invalid server name with the expected status, and listing database servers for a test cell while confirming iterator completion and address formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/util.h -->
# sources/distributed-fs/openafs/src/libadmin/test/util.h

## Purpose

`util.h` declares the utility command handlers and setup function for the `afscp` libadmin test client.

## Important APIs, Types, and Functions

The header includes OpenAFS admin/util headers, command parsing, RX headers, socket/IP headers for non-Windows builds, pthreads, and `common.h`. It declares `DoUtilErrorTranslate`, `DoUtilDatabaseServerList`, `DoUtilNameToAddress`, and `SetupUtilAdminCmd`.

## Control Flow

There is no executable control flow. The declarations allow the test-client command registration code and individual command implementations to share signatures.

## State and Persistence Behavior

No state is stored here. Utility command state is transient and read-only.

## Dependencies and Integration Points

This header is part of the shared test-client build. Its comment says "bos" functions, but the declarations are util functions; that mismatch is documentation drift rather than functional behavior.

## Risks and Test Signals

The header mixes networking headers with OpenAFS admin headers, so portability tests should compile it on Windows and Unix configurations. Command registration tests catch signature mismatches for exported handler declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/vos.c -->
# sources/distributed-fs/openafs/src/libadmin/test/vos.c

## Purpose

`vos.c` implements VOS-related commands for the `afscp` libadmin test client. It is a broad CLI adapter over `afs_vosAdmin`: volume backup/create/delete/move/release/dump/restore, partition lookup/list, VLDB listing and mutation, fileserver address operations, transaction status inspection, and low-level volume-info commands.

## Important APIs, Types, and Functions

Input helpers include `GetIntFromString`, `GetVolumeIdFromString`, `GetPartitionIdFromString`, `GetAddressFromString`, and `GetServer`. Print helpers serialize partition entries, file-server entries, transaction status, VLDB entries, `vos_volumeEntry_t`, and raw `volintInfo`.

The command handlers map directly to public VOS admin calls: `vos_BackupVolumeCreate`, `vos_BackupVolumeCreateMultiple`, `vos_PartitionGet/List`, `vos_ServerSync`, `vos_FileServerAddressChange/Remove/Get*`, `vos_ServerTransactionStatusGet*`, `vos_VLDBGet/List/EntryRemove/Unlock/EntryLock/EntryUnlock/ReadOnlySiteCreate/Delete/Sync`, `vos_VolumeCreate/Delete/Rename/Dump/Restore/Online/Offline/Get/List/Move/Release/Zap/QuotaChange/Get2`, partition conversion helpers, and `vos_ClearVolUpdateCounter`. `SetupVosAdminCmd` registers all command names and parameter schemas.

## Control Flow

Most handlers open a server handle when a `-server` argument is present, convert partitions and volume names to numeric ids, invoke a single libadmin function, and print results if the operation is a read. Iterator commands use begin/next/done and check for `ADMITERATORDONE`. `GetVolumeIdFromString` first accepts numeric ids; otherwise it resolves a name through `vos_VLDBGet` and returns the RW id. `GetPartitionIdFromString` accepts numeric ids or normalizes `a`, `vicepa`, and `/vicepa`-style names into `/vicep*` before calling `vos_PartitionNameToId`.

## State and Persistence Behavior

The file has no local persistence, but many commands mutate remote AFS state. Volume and VLDB commands can create/delete/move/release/zap volumes, change quotas, add/remove replication sites, alter VLDB locks, modify fileserver addresses, and clear volume update counters. Dump/restore commands interact with local dump files through the library.

## Dependencies and Integration Points

`vos.c` includes `vos.h`, `afsutil.h`, and uses libadmin VOS/util APIs plus RX and host utilities. It depends on test-harness globals from `common.h`, especially `cellHandle`, command registration helpers, and fatal error macros.

## Risks and Edge Cases

Several adapter bugs are present. `DoVosFileServerAddressChange` reads `OLDADDRESS` for both old and new addresses, so the requested new address is ignored. `SetupVosAdminCmd` registers `VosVLDBEntryLock` with `DoVosVLDBList` instead of `DoVosVLDBEntryLock`, so the lock command lists entries rather than locking a single entry. Some handlers dereference required parameters in status messages after conditional parsing; they are safe only because command registration marks those arguments required.

`GetPartitionIdFromString` builds a 20-byte buffer with `sprintf`/`strcat` and assumes partition names remain short. `GetAddressFromString` treats `inet_addr` returning `-1` as failure, which also rejects `255.255.255.255`. Server handles opened by commands are generally not closed in this test wrapper, so repeated command execution can leak cached references in a long-lived process. Numeric parsing again lacks robust overflow and negative handling.

## Test Signals

High-value tests include command registration dispatch checks, especially `VosVLDBEntryLock`; address-change tests verifying old and new address arguments; partition parsing for `a`, `vicepa`, `/vicepa`, numeric ids, and invalid strings; iterator tests for partition, fileserver, transaction, VLDB, and volume lists; and destructive-operation tests in an isolated cell covering create/delete/move/release/restore/zap and quota/update-counter changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/vos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/vos.h -->
# sources/distributed-fs/openafs/src/libadmin/test/vos.h

## Purpose

`vos.h` is the local header for VOS command support in the `afscp` libadmin test client.

## Important APIs, Types, and Functions

It includes standard headers, pthreads, RX/RX stats, `afs_Admin.h`, `afs_vosAdmin.h`, `afs_utilAdmin.h`, cell configuration, command parsing, and `common.h`. It declares `SetupVosAdminCmd(void)`.

## Control Flow

The header has no executable control flow. It exposes the command-registration function implemented by `vos.c`.

## State and Persistence Behavior

No state is stored in the header. Remote volume/VLDB state changes happen through handlers in `vos.c`.

## Dependencies and Integration Points

The file connects the test client to the public VOS admin API. Its top comment says "bos" functions, but this is stale copy text; the include set and declaration are VOS-specific.

## Risks and Test Signals

Build tests should compile this header with the VOS admin library headers available. Because the header only exports setup, integration tests should verify that all VOS commands are registered through `SetupVosAdminCmd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/vos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/vos/Makefile.in

## Purpose

`Makefile.in` builds and installs the OpenAFS VOS admin static library, `libvosadmin.a`, and installs its public header `afs_vosAdmin.h`.

## Important APIs, Types, and Functions

The makefile defines object groups for local admin code (`afs_vosAdmin.o`, `vosutils.o`, `vsprocs.o`, `lockprocs.o`) and generated/cross-directory RPC stubs from `vlserver`, `volser`, and `fsint` (`vldbint.*`, `volint.*`, `afsint.xdr.o`, `afscbint.xdr.o`). `LIBOBJS` combines those into `libvosadmin.a`. The `all`, `install`, `dest`, and `clean` targets are the primary entry points.

## Control Flow

Build flow installs the public header into `${TOP_INCDIR}/afs`, archives all library objects with `$(AR)`, and runs `$(RANLIB)`. Cross-directory `.c` files are compiled with `$(AFS_CCRULE)`. `install` and `dest` create include/library directories and copy the header and archive into packaging or destination trees.

## State and Persistence Behavior

The makefile creates build artifacts: object files, `libvosadmin.a`, and installed copies of the library/header. It does not manage runtime state.

## Dependencies and Integration Points

It includes OpenAFS config and pthread make fragments. The library depends on generated VLDB, volserver, and fsint RPC code and on the local `vsprocs`/`lockprocs` helpers. `afs_vosAdmin.o` explicitly depends on `afs_vosAdmin.h`.

## Risks and Test Signals

The archive directly includes generated RPC client/XDR objects, so stale generated sources or cross-directory path changes can break the build. `clean` removes `*.o` and `libvosadmin*` but not installed artifacts. Test signals are successful `make`, header installation, archive symbol availability for all declared VOS admin APIs, and clean rebuild after generated RPC files change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.c

## Purpose

`afs_vosAdmin.c` is the public VOS administration library implementation. It validates libadmin cell/server handles, translates public `vos_*` API calls into VLDB and volserver RPC/procedure calls, exposes iterator APIs for multi-result queries, and maps internal OpenAFS volume/VLDB structures into public structs from `afs_vosAdmin.h`.

## Important APIs, Types, and Functions

The private `file_server_t` wraps an RX volserver connection with magic/is-valid fields. `IsValidServerHandle` and `IsValidCellHandle` enforce handle validity. `GetServerAndPart`, `copyVLDBEntry`, and `copyvolintXInfo` perform important internal-to-public mapping.

Major exported API families include backup creation, partition get/list, server open/close/sync, fileserver address change/remove/list, transaction status iteration, VLDB get/list/remove/unlock/entry-lock/site-create/site-delete/sync, volume create/delete/rename/dump/restore/online/offline/get/list/move/release/zap/quota-change, partition name/id conversion, `vos_VolumeGet2`, and `vos_ClearVolUpdateCounter`.

Iterator families use `afs_admin_iterator_t` with per-family state structs: `partition_get_t`, `server_get_t`, `transaction_get_t`, `vldb_entry_get_t`, and `volume_get_t`. Each supplies RPC-fill, cache-copy, and sometimes destroy callbacks to `IteratorInit`.

## Control Flow

Most exported functions follow the same pattern: validate arguments, optionally normalize server/partition/volume state, call a lower-level `UV_*`, `AFSVol*`, or `ubik_VL_*` function, set `*st`, and return 1/0. Server handles are opened with `util_AdminServerAddressGetFromName`, token security from the cell handle, and `rx_GetCachedConnection`; they are closed with `rx_ReleaseCachedConnection`.

Read iterators first fetch a bulk list or count from the server/VLDB, initialize an iterator, and lazily copy cached entries to callers via `IteratorNext`. Empty result sets mark the iterator as already done with `ADMITERATORDONE`.

Destructive or persistent operations delegate to established volume-server procedures. For example, create/delete/move/release/zap use `UV_CreateVolume`, `UV_DeleteVolume`, `UV_MoveVolume`, `UV_ReleaseVolume`, and `UV_VolumeZap`/`UV_NukeVolume`. Quota and update-counter changes open explicit volserver transactions with `AFSVolTransCreate`, call `AFSVolSetInfo`, and always attempt `AFSVolEndTrans` if a transaction was opened.

## State and Persistence Behavior

Local state is heap-allocated handles and iterator caches. Persistent state lives remotely in VLDB and volume servers. Functions can change VLDB entries, locks, server addresses, volume placement, volume metadata, volume contents via restore, and quota/update-counter fields. Local dump/restore paths read or write files through `UV_DumpVolume` and `UV_RestoreVolume`.

## Dependencies and Integration Points

This file integrates the libadmin public ABI with `vsprocs`, `vosutils`, `lockprocs`, RX, ubik VLDB RPCs, volserver RPCs, and adminutil iterator/cell-handle infrastructure. It requires valid AFS tokens in the cell handle before opening volserver connections.

## Risks and Edge Cases

`vos_ServerOpen` allocates `file_server_t` before validation and does not free it on failure, so invalid arguments or failed name/connection lookups leak memory. `vos_VolumeMove` computes `from_server_addr` and `to_server_addr` from `from_server->serv` and `to_server->serv` before validating either handle; null/invalid handles can crash before the error path. `vos_VolumeRestore` allows a null `serverHandle` through its conditional validation but then unconditionally dereferences `f_server->serv`, so null server handles can crash.

`GetTransactionFromCache` copies `sizeof(vos_serverTransactionStatus_p)` instead of `sizeof(vos_serverTransactionStatus_t)`, so callers can receive only pointer-sized prefixes of transaction status entries. `vos_VLDBGetBegin` failure cleanup checks `entry->entries` before checking `entry != NULL`, which can dereference null after allocation failure. `vos_VolumeGetBegin` failure cleanup frees `entry` without freeing `entry->vollist` if `UV_XListVolumes` succeeded but later iterator setup failed. `vos_VLDBEntryRemove` deletes a named volume first, then can continue into bulk delete validation and fail with `ADMVOSVLDBDELETEALLNULL`, which makes the single-delete path report failure after already mutating state.

Some exported functions ignore `callBack`, despite accepting it. Partition bounds checks vary between `ADMVOSPARTITIONTOOLARGE` and `ADMVOSPARTITIONIDTOOLARGE`. `copyVLDBEntry` copies all `VOS_MAX_REPLICA_SITES` slots rather than only `nServers`, which is safe only if source structures are initialized.

## Test Signals

Unit tests should cover null and invalid handles for every public API, especially `vos_VolumeMove`, `vos_VolumeRestore`, and iterator begin failure paths under allocation fault injection. Integration tests should exercise each iterator family through empty, single-entry, multi-entry, and done states. Destructive operation tests need an isolated cell to verify create/delete/move/release/zap/restore, VLDB lock/unlock/site mutation, server address changes, and transaction cleanup on errors. ABI tests should validate that every `afs_vosAdmin.h` declaration is implemented and that transaction status entries copy complete data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.h

## Purpose

`afs_vosAdmin.h` is the public C API for OpenAFS VOS administration through libadmin. It defines public constants, enums, structs, callback types, and function prototypes used by test clients and other callers to manipulate volumes, partitions, fileserver address records, and VLDB entries.

## Important APIs, Types, and Functions

Important constants define maximum public sizes: partition names, volume names, volume types, replica sites, and server addresses. Public enums cover force/exclude options, volume status/type, volume read/write and time-stat buckets, VLDB entry status bits, replica-site flags, transaction attach/active/status states, restore type, online type, and message callback type.

Core structs are `vos_fileServerEntry_t`, `vos_volumeEntry_t`, `vos_partitionEntry_t`, `vos_vldbEntry_t`, and `vos_serverTransactionStatus_t`. `vos_MessageCallBack_t` lets APIs report debug/error/verbose messages, although the implementation uses it only in limited paths.

The prototype surface covers backup, partition, server, fileserver address, transaction status, VLDB, volume lifecycle, partition conversion, quota, raw volume info, and update-counter APIs.

## Control Flow

The header has no executable flow, but it defines the begin/next/done iterator contract for partitions, fileservers, transaction statuses, VLDB entries, and volumes. Callers open server handles with `vos_ServerOpen`, pass those handles to server-scoped APIs, and close them with `vos_ServerClose`.

## State and Persistence Behavior

The API surface includes many persistent mutators: volume create/delete/rename/move/release/zap/restore/quota/update-counter, VLDB entry remove/lock/unlock/site changes/sync, server sync, and fileserver address changes. Structs returned by read calls are caller-owned output values, while iterator handles are opaque heap-backed state owned by the library until done.

## Dependencies and Integration Points

The header depends on OpenAFS base/admin types, `volint.h`, system sockets, and Windows winsock when needed. It is installed as `afs/afs_vosAdmin.h` and is built into `libvosadmin.a`.

## Risks and Test Signals

Because the header is the ABI contract, risks include enum value drift, struct layout changes, and prototype/implementation mismatch. `vos_VolumeGet2` exposes raw `volintInfo`, making callers more coupled to volserver internals than the normalized `vos_volumeEntry_t` path. Compatibility tests should compile a client that calls every prototype and verify struct sizes/field expectations across supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/afs_vosAdmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.c -->
# sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.c

## Purpose

`lockprocs.c` provides helper routines for locating and editing VLDB server/partition entries and for managing a small linked-list queue used by VOS volume-operation code. Despite the filename, the file does not acquire pthread or OS locks; it manipulates VLDB entry fields and queue structures.

## Important APIs, Types, and Functions

The central helper is `FindIndex`, which searches an `nvldbentry` for a matching server, partition, and volume type flag. `SetAValue` updates or removes a matching entry. Exported wrappers include `Lp_SetRWValue`, `Lp_SetROValue`, `Lp_Match`, `Lp_ROMatch`, and `Lp_GetRwIndex`.

Queue helpers are `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`, operating on `struct qHead` and `struct aqueue` from volserver lockdata headers.

## Control Flow

`FindIndex` iterates over VLDB server slots. It uses `VLDB_IsSameAddrs` to account for multihomed/equivalent server addresses. For RW lookups it returns early after failing a matching RW slot, based on the invariant that a VLDB entry has only one RW site. `SetAValue` calls `FindIndex`, writes the new server/partition, and if the new server and partition are both zero, shifts later entries left to remove the site.

The queue functions implement a simple push-front list. `Lp_QEnumerate` pops the head, copies fixed fields into a caller-supplied element, frees the stored node, and reports success.

## State and Persistence Behavior

The VLDB helpers mutate only the in-memory `nvldbentry` passed by the caller; persistence occurs only if the caller later writes the entry back to the VLDB. Queue helpers allocate no memory themselves, but `Lp_QEnumerate` frees queue nodes that were previously allocated by callers.

## Dependencies and Integration Points

The file includes `lockprocs.h`, which pulls in VLDB, volserver, RX, fsint, util admin, admin internals, and `vosutils.h`. `FindIndex` depends on `VLDB_IsSameAddrs` from `vosutils.c`.

## Risks and Edge Cases

`SetAValue` shifts entries left when removing a site but does not decrement `entry->nServers` or clear the trailing slot, so callers must compensate or risk stale duplicate entries. `FindIndex` suppresses status details from `VLDB_IsSameAddrs` other than stopping on `tst`; exported match functions mostly ignore the `st` pointer. Queue operations are not synchronized and assume single-threaded use or external locking. `Lp_QEnumerate` uses `strncpy` with `VOLSER_OLDMAXVOLNAME` and does not explicitly terminate `elem->name`.

## Test Signals

Tests should construct synthetic `nvldbentry` records with RW, RO, backup, multihomed-equivalent, and no-match cases. Removal tests should verify `nServers` and trailing slots in the caller's final write path. Queue tests should cover empty enumeration, LIFO order, scan success/failure, and copied id/copyDate/isValid fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.h -->
# sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.h

## Purpose

`lockprocs.h` declares the helper API implemented by `lockprocs.c` for VLDB entry site manipulation and queue handling used by VOS admin internals.

## Important APIs, Types, and Functions

It includes system networking, RX/XDR, VLDB, NFS, fsint, volint, volser, `lockdata.h`, util admin, admin internals, and `vosutils.h`. It declares `Lp_SetRWValue`, `Lp_SetROValue`, `Lp_Match`, `Lp_ROMatch`, `Lp_GetRwIndex`, `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`.

## Control Flow

No executable control flow is present. The declarations define the interface used by `vsprocs` and VOS admin support code.

## State and Persistence Behavior

The declared functions operate on caller-owned `nvldbentry`, `qHead`, and `aqueue` objects. They only persist changes if higher-level code writes modified VLDB entries or consumes queues into persistent operations.

## Dependencies and Integration Points

This header creates a broad dependency surface on volserver/VLDB internals. It is not a public installed header like `afs_vosAdmin.h`; it is internal to the VOS admin build.

## Risks and Test Signals

The header exposes internal OpenAFS structs directly, so changes in `lockdata.h`, VLDB entry layout, or volserver constants can break users. Compile tests for `lockprocs.c`, `vsprocs.c`, and `afs_vosAdmin.c` are the primary signal. Unit tests should confirm declarations match definitions exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vosutils.c -->
# sources/distributed-fs/openafs/src/libadmin/vos/vosutils.c

## Purpose

`vosutils.c` provides compatibility and utility routines for the VOS admin library. It bridges old and new VLDB RPC formats, wraps VLDB list/get/create/replace calls, resolves equivalent server addresses, finds volume placement, validates volume names, strips readonly/backup suffixes, and filters unwanted addresses on Windows.

## Important APIs, Types, and Functions

Private conversion helpers are `OldVLDB_to_NewVLDB` and `NewVLDB_to_OldVLDB`. Public/internal wrappers include `VLDB_CreateEntry`, `aVLDB_GetEntryByID`, `aVLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`, `GetVolumeInfo`, `ValidateVolumeName`, `vsu_ExtractName`, `AddressMatch`, and `RemoveBadAddresses`.

## Control Flow

The VLDB wrappers prefer the new `*N` RPCs when `cellHandle->vos_new` is true. On `RXGEN_OPCODE`, they mark `vos_new` false and retry with old-format RPCs, converting old entries into `nvldbentry` where needed. `VLDB_ListAttributes` also normalizes returned entry counts to the actual XDR array length and allocates converted `nbulkentries` for old responses.

`VLDB_IsSameAddrs` first handles exact address equality, then queries `VL_GetAddrsU` for all addresses associated with `serv1` and checks whether `serv2` appears in that set. `GetVolumeInfo` uses `aVLDB_GetEntryByID` and `Lp_GetRwIndex` to determine server, partition, and volume type for RW/RO/BACK volume ids.

`RemoveBadAddresses` uses `pthread_once` to initialize an optional Windows registry-driven wildcard address pattern and compacts address arrays in place when filtering is enabled.

## State and Persistence Behavior

`cellHandle->vos_new` is mutable compatibility state: a failed new-RPC opcode permanently switches that cell handle to old VLDB calls. VLDB create/replace wrappers persist remote VLDB entries. Other utilities are read-only except for caller-owned output buffers and in-place address-array filtering.

## Dependencies and Integration Points

The file depends on admin error codes, `vosutils.h`, `vsprocs.h`, `lockprocs.h`, ubik VLDB RPC stubs, XDR free routines, pthread once, and Windows registry APIs under `AFS_NT40_ENV`. `afs_vosAdmin.c` relies on these helpers for name validation, volume lookup, VLDB listing, and server-address equivalence.

## Risks and Edge Cases

`OldVLDB_to_NewVLDB` and `NewVLDB_to_OldVLDB` use `strncpy` with destination size but do not explicitly force null termination for names. `VLDB_ListAttributes` sets `rc = 1` after old-format conversion even if `OldVLDB_to_NewVLDB` fails during an individual conversion, unless memory allocation fails. `VLDB_IsSameAddrs` does not free the `bulkaddrs` array returned by `ubik_VL_GetAddrsU`, which can leak memory. `GetVolumeInfo` leaves `tst` not explicitly initialized before all paths and can return success without setting server/partition for unexpected volume ids that are neither RW, RO, nor BACK.

`ValidateVolumeName` only checks suffixes and `ISNAMEVALID`; it does not enforce all possible naming policy by itself. `vsu_ExtractName` returns `-1` for unsuffixed names while still copying the original name, so callers must understand that return convention.

## Test Signals

Tests should simulate new-RPC success, `RXGEN_OPCODE` fallback, old-format conversion, and old-format overflow beyond `OMAXNSERVERS`. Address tests should cover exact equality, multihomed equivalence, no-match, and Windows bad-address filtering if supported. Volume lookup tests should cover RW, RO with multiple sites and `VLSF_DONTUSE`, BACK, missing RW index, and invalid ids. Name validation tests should include null, empty, too-long, `.readonly`, `.backup`, and valid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vosutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vosutils.h -->
# sources/distributed-fs/openafs/src/libadmin/vos/vosutils.h

## Purpose

`vosutils.h` declares the internal utility functions used by the VOS admin implementation and related helper code.

## Important APIs, Types, and Functions

The header exposes VLDB wrapper functions (`VLDB_CreateEntry`, `aVLDB_GetEntryByID`, `aVLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`), volume lookup/name helpers (`GetVolumeInfo`, `ValidateVolumeName`, `vsu_ExtractName`), and address helpers (`AddressMatch`, `RemoveBadAddresses`).

## Control Flow

There is no executable control flow in the header. Its function declarations describe the internal control surface used by `afs_vosAdmin.c`, `lockprocs.c`, and `vsprocs.c`.

## State and Persistence Behavior

The declared VLDB wrappers can read or mutate remote VLDB state, and some mutate compatibility state on the cell handle. Address/name helpers operate on caller-provided memory.

## Dependencies and Integration Points

It depends on `afs_Admin.h`, VLDB types, XDR/RX types through includers, and internal admin cell-handle definitions. It is internal to the VOS admin source directory rather than an installed public API.

## Risks and Test Signals

Because this header exposes old/new VLDB compatibility helpers, prototype drift would affect multiple VOS admin modules. Build tests should compile all VOS admin objects together, and focused unit tests should verify each declared helper's status-code behavior and ownership rules for allocated XDR arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vosutils.h -->
