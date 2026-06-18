# subset-b-007792 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptprocs.c -->
# sources/distributed-fs/openafs/src/ptserver/ptprocs.c research

## Purpose
`ptprocs.c` implements the Protection Server RPC procedure layer. It translates generated `SPR_*` RPC entry points into database transactions against the Ubik-backed protection database, performs caller identification and authorization, emits audit/ViceLog records, and delegates record-level mutations to `ptutils.c`.

## Important APIs, types, and functions
The public surface is the `SPR_*` procedure family used by rxgen dispatch: entry creation (`SPR_INewEntry`, `SPR_NewEntry`), lookup (`SPR_NameToID`, `SPR_IDToName`, `SPR_WhereIsIt`, `SPR_DumpEntry`), membership mutation (`SPR_AddToGroup`, `SPR_RemoveFromGroup`), membership expansion (`SPR_GetCPS`, `SPR_GetCPS2`, `SPR_GetHostCPS`), administration (`SPR_ListMax`, `SPR_SetMax`, `SPR_UpdateEntry`, `SPR_ChangeEntry`, `SPR_SetFieldsEntry`), listing (`SPR_ListEntry`, `SPR_ListEntries`, `SPR_ListElements`, `SPR_ListOwned`, `SPR_ListSuperGroups`), deletion, and membership predicates. Each public function calls a static implementation with a `cid` output so audit logs can report the resolved caller.

`ReadPreamble` and `WritePreamble` are the central transaction openers. They call `Initdb`, begin a Ubik read or write transaction, lock byte range `1,1`, and refresh the cached database header via `read_DbHeader`. `WhoIsThis` and `WhoIsThisWithName` map Rx security identities to PT ids, including null security, rxkad identities, local-realm checks, `AUTH_SUPERUSER`, foreign `name@cell` registration, and superuser identities from newer Rx security classes. `CreateOK` centralizes creation policy under `restricted`, `pr_noAuth`, anonymous, admin, group, user, and foreign-entry cases.

## Control flow, state, and persistence
The file is transaction-oriented: read-only operations use `ReadPreamble`; mutations use `WritePreamble`; errors generally use `ABORT_WITH(tt, code)` to abort the Ubik transaction and return a PT error. Database state is not directly persisted here except through helpers such as `CreateEntry`, `DeleteEntry`, `AddToEntry`, `RemoveFromEntry`, `ChangeEntry`, `SetMax`, and `GetList`. Those helpers update `cheader`, hash chains, owner chains, quota fields, membership lists, and continuation blocks.

The create path lowercases names, authenticates the caller, checks admin status via `IsAMemberOf(..., SYSADMINID)`, validates explicit id reuse for `SPR_INewEntry`, supports cross-cell autoregistration in `SPR_NewEntry`, and delegates actual record construction to `CreateEntry`. The delete path refuses built-in ids, validates owner/admin rights, removes continuation-block memberships in bounded transactions, moves owned groups to the orphan chain, handles optional supergroup continuation records, and finally calls `DeleteEntry`. Membership mutation reads both user and group entries, enforces group type and access bits, and updates both sides of the relationship; with `SUPERGROUPS`, group-to-group membership uses `AddToSGEntry`/`RemoveFromSGEntry` on the member group.

Membership expansion uses `GetList`, `GetList2`, and host wildcard support. `SPR_GetCPS2` can combine a user CPS and host entry groups, then `addWildCards` augments the list from wildcard host names. Listing APIs allocate XDR result arrays and cap bulk `ListEntries` replies at `PR_MAXENTRIES`. `ListOwned` implements paged owner-chain walking through `lastP`.

## Dependencies and integration points
This file depends on Rx/RxKad/Rx identity APIs for authentication, Ubik for replicated transactions, `afsconf` for local realm and auth policy, audit logging, `ptserver.h` for on-disk structures/constants, `pterror.h` for error codes, and `ptprototypes.h` for database helpers. It is invoked by the Rx service created in `ptserver.c` through `PR_ExecuteRequest`, and it serves client calls made by `ptuser.c` and tools such as `pts`, `readpwd`, `readgroup`, and `testpt`.

## Risks and test signals
This is high-risk security and consistency code. Changes need tests for anonymous restrictions, `-restricted` behavior, sysadmin and ptsviewer access, owner-chain permissions, foreign-user autoregistration, id/name lookup across local and foreign realms, and transaction abort paths. Deletion is especially sensitive because it splits long continuation-chain cleanup across several transactions and must preserve reciprocal membership and owner/orphan invariants. Supergroups add conditional behavior that can diverge from normal group rules, so builds with and without `SUPERGROUPS` need coverage. Host CPS paths should be tested with exact host entries and wildcard address entries. Existing signals include `testpt` membership stress tests, `pts` CLI workflows, and import utilities that exercise creation and membership mutation at scale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptprototypes.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptprototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/pts.c -->
# sources/distributed-fs/openafs/src/ptserver/pts.c research

## Purpose
`pts.c` implements the interactive and command-line Protection Server administration client. It registers the user-facing `pts` subcommands, parses global authentication/configuration options, calls the public `ptuser.c` API, and formats results for operators.

## Important APIs, types, and functions
Command handlers include `CreateGroup`, `CreateUser`, `AddToGroup`, `RemoveFromGroup`, `ListMembership`, `Delete`, `CheckEntry`, `ListEntries`, `ChownGroup`, `ChangeName`, `ListMax`, `SetMaxCommand`, `SetFields`, and `ListOwned`. Interactive helpers are `pts_Interactive`, `pts_Quit`, `pts_Source`, `pts_Sleep`, and `popsource`. `GetGlobals` is the command before-proc that initializes or refreshes the ptuser client according to `-cell`, `-noauth`, `-auth`, `-encrypt`, `-localauth`, `-config`, `-rxgk`, and retry rules.

`GetNameOrId` is a central resolver: it accepts mixed names and numeric ids, calls `pr_NameToId` and `pr_IdToName`, and returns aligned `idlist`/`namelist` arrays for downstream commands. Access-bit presentation and parsing are driven by `flags_upcase`, `flags_dncase`, and `flags_shift`.

## Control flow, state, and persistence
The process maintains a small mutable `authstate` with security level, initialization status, and selected cell. Every command goes through `GetGlobals`, which tears down and recreates the global `pruclient` when security or configuration changes. Persistent PT database changes happen only through `ptuser.c` wrappers such as `pr_CreateUser`, `pr_CreateGroup`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetMax*`, and `pr_SetFieldsEntry`.

Interactive mode sets `source` to stdin and loops through parsed command lines until `quit`, EOF, or a source-stack unwind. The source command supports nested command files with `MAX_SOURCE_STACK_SIZE` to avoid unbounded recursion. `force` is global per command and lets batch operations continue after reasonable per-item failures.

## Dependencies and integration points
The file depends on the OpenAFS command parser, Rx, AFS config paths, `ptclient.h`, `ptuser.h`, `pterror.h`, and XDR free routines. It is the main operator entry point for the RPCs implemented in `ptprocs.c`. It also mirrors server-side access-bit encoding from `ptserver.h`, so flag parsing must remain consistent with `PRP_*` definitions and `PRIVATE_SHIFT`.

## Risks and test signals
Input handling is security-relevant because names are copied into fixed PT buffers and mixed name/id parsing has to preserve alignment between ids and names. The code relies on lower-level `ptuser.c` length checks for many operations but still allocates local fixed-size name arrays. Source-file recursion, authentication refresh, and fallback from client to server config directories should be tested. CLI regression tests should cover all subcommands, `-force`, `-rxgk`, interactive/source execution, access-string parsing, list pagination through `ListOwned`, supergroup display on servers with and without the opcode, and cleanup of XDR allocations after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/pts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptserver.c -->
# sources/distributed-fs/openafs/src/ptserver/ptserver.c research

## Purpose
`ptserver.c` is the daemon entry point for the OpenAFS Protection Server. It parses server options, initializes logging/auditing/configuration, sets global ptserver policy, initializes Rx and Ubik, registers the Protection Server and RX statistics services, and starts the Rx server loop.

## Important APIs, types, and functions
Global daemon state includes `cheader`, `dbase`, `prdir`, `restricted`, `restrict_anonymous`, `rxMaxMTU`, `rxBind`, `rxkadDisableDotCheck`, and optional `depthsg`. `prp_access_mask` parses textual default access masks into `PRP_*` bits. `pr_rxstat_userok` authorizes RX statistics management via `afsconf_SuperUser`. `pr_IsLocalRealmMatch` adapts `afsconf_IsLocalRealmMatch` for audit user checks.

The `main` function owns all runtime setup: directory initialization, option registration and parsing, default access parsing, supergroup depth, restriction flags, audit options, database path, thread count bounds, syslog/file log setup, Rx stats toggles, Rx bind/max-MTU options, rxkad dotted principal behavior, rxgk server-to-server crypt selection, config open, host/server discovery, Ubik security procedure setup, Rx initialization, Ubik server initialization, security object construction, service registration, and `rx_StartServer`.

## Control flow, state, and persistence
The daemon starts by validating OpenAFS server paths and defaulting the protection database and config directory. It applies CLI/config options before opening audit and log outputs. It opens the server config dir into global `prdir`, determines whether `NoAuth` is present, discovers the local host and protection server cell info, and sets audit local-realm callbacks.

Ubik is configured with client and server security procedures, then initialized with `ubik_ServerInitByInfo` using the protection database path. The persistent protection database itself is managed by Ubik and initialized lazily by `Initdb` in `ptutils.c` when RPCs begin transactions. `ubik_nBuffers` is increased to handle worst-case delete transactions involving continuation blocks and reciprocal membership cleanup. With `SUPERGROUPS`, `pt_hook_write` is installed after Ubik initialization to invalidate supergroup maps when group records are written.

## Dependencies and integration points
This file integrates AFS directory/path initialization, OpenAFS command parsing, logging, audit, Rx, Rx stats, Rx security classes, rxkad/rxgk configuration, Ubik replication, `afsconf` cell/server data, and generated `PR_ExecuteRequest`. It owns the global variables consumed by `ptprocs.c` and `ptutils.c`.

## Risks and test signals
Startup option interactions are the main risk: `-syslog` versus `-logfile`/`-transarc-logs`, thread bounds, invalid `-s2scrypt`, invalid `-default_access`, bad config directories, and Rx bind/netinfo behavior must fail clearly. Security-sensitive tests should cover noauth mode, restricted mode, anonymous restriction, dotted principal toggles, rxgk server-to-server crypt configuration, and RX stats authorization. Database safety depends on structure-size checks under `SUPERGROUPS`, correct `ubik_nBuffers`, and successful Ubik initialization before the service accepts requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptserver.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptubik.c -->
# sources/distributed-fs/openafs/src/ptserver/ptubik.c research

## Purpose
`ptubik.c` is a lightweight Ubik compatibility shim for standalone protection-database tooling. It provides enough Ubik, Rx, and configuration globals/functions for ptserver database code to operate against a local file descriptor instead of a live replicated Ubik server.

## Important APIs, types, and functions
Stubbed transaction and server functions include `ubik_ServerInit`, `ubik_BeginTrans`, `ubik_BeginTransReadAny`, `ubik_AbortTrans`, `ubik_EndTrans`, `ubik_Tell`, `ubik_Truncate`, `ubik_SetLock`, and `ubik_CheckCache`. Real local file I/O is handled by `ubik_Seek`, `ubik_Write`, and `ubik_Read`, which address the backing file at `pos + HDRSIZE`. `panic` prints and aborts. `afsconf_GetNoAuthFlag` always returns true for local tooling.

The file defines Ubik globals (`ubik_quorum`, `ubik_dbase`, `ubik_stats`, `ubik_host`, `ubik_epochTime`, `urecovery_state`, `ubik_sc`), ptserver globals (`dbase`, `cheader`), and a placeholder `prdir`.

## Control flow, state, and persistence
On first `ubik_BeginTrans`, the shim writes a minimal Ubik header with magic/version/size to `dbase_fd` and fsyncs it. Subsequent transaction functions are no-ops, so local pt database operations rely on direct seek/read/write and do not get real locking, replication, quorum, abort, or rollback semantics. `ubik_Read` zero-fills short reads, matching expectations for initializing empty database regions.

## Dependencies and integration points
This file is used by local utilities that reuse ptserver database code without linking the full Ubik server stack. It includes `ptint.h` and `ptserver.h` and expects an external `dbase_fd`. It intentionally makes `pr_noAuth`-style paths succeed by returning noauth from `afsconf_GetNoAuthFlag`.

## Risks and test signals
The shim is not equivalent to production Ubik. It has no transactional rollback, no concurrency control, and only coarse write error checks, so it should stay confined to offline tools and tests. Any ptutils change that assumes real Ubik transaction side effects may break standalone utilities. Tests should exercise database initialization on an empty file, read/write offset correctness relative to `HDRSIZE`, short-read zero filling, and compatibility with tools that import/export or repair protection databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptubik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptuser.c -->
# sources/distributed-fs/openafs/src/ptserver/ptuser.c research

## Purpose
`ptuser.c` implements the public libprot client API declared in `ptuser.h`. It initializes authenticated or unauthenticated Ubik RPC clients for the Protection Server and provides convenience wrappers that translate names to ids, enforce fixed-string safety, call generated `ubik_PR_*` RPCs, and convert ids back to names for callers.

## Important APIs, types, and functions
Initialization is handled by `pr_Initialize` and `pr_Initialize2`, which open AFS configuration, resolve cell info for `afsprot`, choose Rx security classes for noauth/token/localauth/encrypt/rxgk cases, create Rx connections to all protection servers, and initialize global `pruclient`. `pr_End` destroys that client.

CRUD and membership wrappers include `pr_CreateUser`, `pr_CreateGroup`, `pr_Delete`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetFieldsEntry`, and `pr_IsAMemberOf`. Lookup/listing wrappers include `pr_NameToId`, `pr_SNameToId`, `string_PR_IDToName`, `pr_IdToName`, `pr_SIdToName`, `pr_GetCPS`, `pr_GetCPS2`, `pr_GetHostCPS`, `pr_ListMembers`, `pr_IDListMembers`, `pr_IDListExpandedMembers`, `pr_ListOwned`, `pr_ListEntry`, `pr_ListEntries`, `pr_CheckEntryByName`, `pr_CheckEntryById`, and `pr_ListSuperGroups`.

The local `idhash`/`idchain` structures support expanded membership traversal without duplicates.

## Control flow, state, and persistence
The only durable state affected by this file is remote ptserver state reached through RPCs. Local state is the global `pruclient`, cached security level `lastLevel`, cached config directory/cell strings, and static `afsconf_dir`/cell info. `check_length` protects APIs from non-NUL-terminated or too-long `prname` values before they reach RPC code or after fixed-width names return from the server.

Many name-based operations first call `pr_NameToId` to convert one or two names, check `ANONYMOUSID` as the not-found sentinel, then call an id-based generated RPC. Listing operations often receive `prlist` ids, cast or copy them into `idlist`, call `pr_IdToName`, and free XDR allocations. `pr_IDListExpandedMembers` traverses nested groups/supergroups with a stack and hash set, tolerating `RXGEN_OPCODE` for servers without supergroup support.

## Dependencies and integration points
The file depends on Rx, Ubik client APIs, AFS config/auth/token APIs, rxgk interfaces, generated `ptclient.h`, `ptuser.h`, and `pterror.h`. It is consumed by the `pts` CLI, import tools, tests, and other OpenAFS components needing protection data.

## Risks and test signals
Global client state makes repeated initialization sensitive to cell/config/security changes and not obviously thread-local. Security-level behavior should be tested for noauth, token auth, localauth, encrypt, and rxgk paths, including fallback when tokens are unavailable. String-length checks are critical because the wire protocol carries fixed-size character vectors; tests should include boundary-length names and malformed server replies. Expanded membership traversal needs cycle/duplicate tests, supergroup and non-supergroup server tests, and memory cleanup checks for XDR results on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptuser.h -->
# sources/distributed-fs/openafs/src/ptserver/ptuser.h research

## Purpose
`ptuser.h` declares the public libprot client API for interacting with the OpenAFS Protection Server. It is the supported header for callers that need to create/delete users and groups, manage memberships, list entries, inspect quotas/access flags, and initialize or tear down the protection client.

## Important APIs, types, and functions
Connection lifecycle APIs are `pr_Initialize`, `pr_Initialize2`, and `pr_End`. Creation/deletion/mutation APIs are `pr_CreateUser`, `pr_CreateGroup`, `pr_Delete`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetFieldsEntry`, `pr_SetMaxUserId`, and `pr_SetMaxGroupId`. Lookup and listing APIs are `pr_NameToId`, `pr_SNameToId`, `pr_IdToName`, `pr_SIdToName`, `pr_GetCPS`, `pr_GetCPS2`, `pr_GetHostCPS`, `pr_ListMembers`, `pr_IDListMembers`, `pr_IDListExpandedMembers`, `pr_ListOwned`, `pr_ListEntry`, `pr_ListEntries`, `pr_CheckEntryByName`, `pr_CheckEntryById`, `pr_IsAMemberOf`, `pr_ListMaxUserId`, `pr_ListMaxGroupId`, and `pr_ListSuperGroups`.

Several declarations include `AFS_NONNULL` annotations to document required pointers and help static analysis.

## Control flow, state, and persistence
The header does not define state, but the declared functions operate through the global client maintained in `ptuser.c`. Callers must initialize the library before issuing operations and free XDR-allocated result buffers according to the conventions of the underlying generated types. Persistent changes happen remotely on the ptserver through RPCs.

## Dependencies and integration points
The header includes `afs/ptint.h` for generated PT types such as `prname`, `namelist`, `idlist`, `prlist`, `prcheckentry`, and `prlistentries`. It is used by command-line tools (`pts`, `readpwd`, `readgroup`, `testpt`) and can be used by other OpenAFS components.

## Risks and test signals
The API shape depends on fixed-size PT names and generated XDR ownership conventions; callers can leak memory or pass invalid buffers if they ignore those rules. Because the header exposes both name-based and id-based operations, tests should cover not-found mapping through `ANONYMOUSID`, output list ownership, max-id setters, supergroup fallback behavior, and lifecycle behavior across repeated `pr_Initialize`/`pr_End` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptuser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptutils.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/ptutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/readgroup.c -->
# sources/distributed-fs/openafs/src/ptserver/readgroup.c research

## Purpose
`readgroup.c` is an import utility that reads a textual group file, creates protection groups, and adds listed users or expanded members from referenced groups. It is intended for bulk population or migration of PT group membership data.

## Important APIs, types, and functions
`main` parses `[-v] [-c cellname] groupfile`, initializes libprot with `pr_Initialize(2, AFSDIR_CLIENT_ETC_DIRPATH, cellname)`, opens the input file, parses group headers and continuation member lines, calls `pr_CreateGroup`, `pr_AddToGroup`, and `pr_ListMembers`, and reports errors with `report_error`. `skip` advances over whitespace-delimited tokens. A local `osi_audit` stub satisfies auth-library linkage in a non-server program.

## Control flow, state, and persistence
The input format treats a non-indented line as a new group declaration: group name, numeric id, then optional members on the same line. Leading space or tab means additional members for the current group. The utility lowercases group names, derives an owner prefix from the group name before `:`, maps owner `system` to `system:administrators`, and attempts to create the group with the parsed id. If the group already exists, membership import may continue; if creation fails for other reasons, later member lines are skipped until the next group. Members without `:` are added directly. Tokens containing `:` are treated as groups, expanded with `pr_ListMembers`, and each returned member is added to the target group.

Persistent state changes are remote ptserver group creation and membership additions through `ptuser.c`.

## Dependencies and integration points
The file depends on `ptuser.h`, generated client types, `pterror.h`, `ptprototypes.h`, AFS config paths, Rx/XDR, and `pr_ErrorMsg`. It is a batch client of the same RPCs exposed through `pts`.

## Risks and test signals
Parsing is simple and fragile: it uses fixed buffers, assumes `:` exists in group names before deriving the owner, and treats any token containing `:` as a group reference. It should be tested with missing colons, long lines, empty lines, existing groups, nonexistent referenced groups, duplicate members, verbose mode, and explicit cell selection. Because it expands referenced groups by current server state, import results can depend on ordering and preexisting memberships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/readgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/readpwd.c -->
# sources/distributed-fs/openafs/src/ptserver/readpwd.c research

## Purpose
`readpwd.c` is a small import utility that reads a passwd-format file and creates Protection Server user entries with the passwd uid as the requested PT id.

## Important APIs, types, and functions
`main` parses `[-v] [-c cellname] passwdfile`, initializes libprot with localauth-style security through `pr_Initialize(2, AFSDIR_CLIENT_ETC_DIRPATH, cellname)`, opens the input file, extracts username and uid fields from colon-separated lines, and calls `pr_CreateUser`. It prints `pr_ErrorMsg` diagnostics on failures. A local `osi_audit` stub satisfies non-server linkage.

## Control flow, state, and persistence
For each line, the utility copies the substring before the first colon into `name`, skips to the uid field, copies it into a small `uid` buffer, converts it with `atoi`, and passes that id by pointer to `pr_CreateUser`. A nonzero id requests `SPR_INewEntry` behavior on the server side. Persistent state changes are remote user entries in the protection database.

## Dependencies and integration points
The file depends on OpenAFS config paths, Rx/XDR headers, `ptuser.h`, and `ptprototypes.h`. It exercises the same client initialization and create-user path used by `pts createuser -id`.

## Risks and test signals
The parser assumes valid passwd lines with enough colon fields and has fixed-size buffers, including an 8-byte uid string. It should be tested with malformed lines, long usernames, large uid values, duplicate users/ids, missing files, verbose mode, and explicit cell selection. Since all persistence is delegated to the ptserver, server-side validation still protects name legality and id conflicts, but the utility can fail unclearly on malformed local input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/readpwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/testpt.c -->
# sources/distributed-fs/openafs/src/ptserver/testpt.c research

## Purpose
`testpt.c` is a command-driven Protection Server test and stress utility. It validates id usage, name validation, membership correctness, owner-chain behavior, and large membership mutation scenarios against a live ptserver.

## Important APIs, types, and functions
Command handlers are `ListUsedIds`, `TestPrServ`, and `TestManyMembers`. `ListUsedIds` scans user or group id ranges with `pr_IdToName` and compares returned names to numeric ids to classify used/free ids. `TestPrServ` validates name length and illegal-character behavior for users and groups, creates/deletes entries, and confirms creator lookup. `TestManyMembers` creates many users and groups, adds/removes memberships according to a generated matrix, validates membership and CPS results, validates owner lists, then deletes entries.

Supporting functions include `IdCmp`, `GetGroupLimit`, `CreateUser`, `CreateGroup`, `DeleteRandomId`, `AddUser`, `RemUser`, `ka_ConvertBytes`, and command before/after procs `MyBeforeProc`/`MyAfterProc`. `add_std_args` provides test configuration options for confdir, cell, noauth, and server list.

## Control flow, state, and persistence
`MyBeforeProc` builds or opens AFS configuration for tests. If a confdir is not supplied, it creates temporary CellServDB/ThisCell/NoAuth files derived from local config and command arguments. `MyAfterProc` removes those temporary files. Tests initialize libprot against that config and then perform real ptserver operations.

`TestManyMembers` builds arrays for users, groups, group owners, and a `number x number` membership matrix. It randomly creates entries, adds memberships, removes some memberships, verifies server lists against the matrix with either `ubik_PR_ListElements` or `ubik_PR_GetCPS`, checks expected CPS extras, checks that groups appear on the correct owner chains, and cleans up by deleting random remaining ids.

## Dependencies and integration points
The file depends on `ptuser.h`, generated `ptclient.h`, command parsing, AFS auth/config/token APIs, Rx/XDR, and PT/Rx/KTC error tables. It directly calls both public libprot APIs and generated `ubik_PR_*` functions, making it useful for testing client wrappers and server RPC behavior.

## Risks and test signals
Because it mutates a real protection database, it should be run only against test cells or disposable databases. Randomized ownership and membership patterns are valuable for continuation blocks, owner chains, and reciprocal membership consistency, but failures terminate with `exit`, so harnesses should isolate runs. Important coverage includes boundary-length names, illegal characters, duplicate handling, large CPS/list elements, owner lists, group deletion, id-range scanning, noauth temporary config, and reproducibility through the `-seed` argument.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/ptserver/testpt.c -->
