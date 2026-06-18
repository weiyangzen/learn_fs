# subset-b-007706 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.c

## Purpose

`cm_volume.c` implements the Windows OpenAFS cache manager's volume table. It maps volume names and IDs to cached `cm_volume_t` objects, refreshes location data from VLDB servers, tracks RW/RO/backup server lists and availability state, recycles volume objects through an LRU, validates persisted cache metadata, and drives status notifications for volume online/offline/busy/down transitions.

## Important APIs, Types, and Functions

The main public entry points are `cm_InitVolume()`, `cm_ShutdownVolume()`, `cm_FindVolumeByName()`, `cm_FindVolumeByID()`, `cm_FindVolumeByFID()`, `cm_GetVolumeByFID()`, `cm_GetVolServers()`, `cm_ForceUpdateVolume()`, `cm_RefreshVolumes()`, `cm_CheckOfflineVolumes()`, `cm_UpdateVolumeStatus()`, `cm_VolumeRenewROCallbacks()`, hash/LRU helpers, and volume-state lookup helpers. `cm_UpdateVolumeLocation()` is the central refresh routine. It calls `VL_GetEntryByNameU`, then falls back to `N` and old `O` VLDB forms, expands UUID/multihomed server entries through `cm_GetAddrsU()`, installs file-server refs, and updates all three per-volume states.

## Control Flow

Lookup first searches global name or ID hash tables under `cm_volumeLock`. If a name lookup misses and creation is allowed, it either allocates a new slot from `cm_data.volumeBaseAddress` or recycles an unreferenced LRU object after removing it from name and ID hashes. The candidate is initialized, reference-counted, made visible in the name hash, then refreshed under the per-volume write lock unless `CM_GETVOL_FLAG_NO_RESET` suppresses it.

Refresh is serialized with `CM_VOLUMEFLAG_UPDATING_VL`; contending threads sleep on `volp->flags` and reuse the completed result. The code avoids repeated VLDB storms with 60-second retry throttling and a 10-minute negative-cache window for nonexistent volumes. Successful VLDB data is normalized to the base volume name, inserted into RW/RO/BK ID hashes, converted to server-ref lists, randomized for replicated RO access, and mapped to `vl_online` or `vl_alldown`. Failure maps no-such-volume into `CM_VOLUMEFLAG_NOEXIST`; other failures mark all variants down.

Offline checks run from daemon context over the LRU. They reset busy/offline server-ref states, optionally force a VLDB refresh, issue `RXAFS_GetVolumeStatus()` against a root fid, cache RO size when available, and move volume state back online when a server reports an online volume. Status recalculation counts server refs as down, busy, offline, deleted, or usable and emits notifications on transitions.

## State and Persistence Behavior

Volume objects live in `cm_data` shared cache memory and are revalidated on restart with pointer range and magic checks. Persistent-ish fields include the all-volume list, hash chains, LRU queue, base name, cell pointer, per-type IDs, dotdot fids, flags, callback metadata, and RO size. Server-ref lists are live references into the server table and are freed/rebuilt on every successful VLDB refresh. The file does not persist VLDB state itself; it caches remote volume-location state and invalidates it by flags, lifetime, VNOVOL/VMOVED force-refresh, mixed RO-release polling, and shutdown.

## Dependencies and Integration Points

The module depends on cache-manager globals in `cm_data`, `cm_cell_t`, `cm_serverRef_t`, `cm_server_t`, Rx/VLDB RPCs, multihomed address resolution, server ranking/randomization, `cm_Analyze()` retry logic, callback/scache APIs, Windows synchronization and interlocked operations, and volume-status notification hooks. File operations consume it through `cm_GetServerList()`, `cm_ConnFromVolume()`, mount-root generation changes, and VNOVOL/VMOVED handling.

## Risks and Edge Cases

Concurrency is delicate: global hash/LRU state and per-volume state use different locks, and `cm_UpdateVolumeLocation()` intentionally drops the volume lock during RPCs. Recycling must remove every old hash and server-list reference before exposing a reused object. Numeric volume names, `.readonly` fallback, renamed volumes looked up by ID, linked cells, fake freelance root volumes, old VLDB opcodes, UUID mismatch logging, mixed RO releases, all-deleted refs, and negative-cache throttling are all special cases. There is a suspicious `if (code = 0)` assignment in the offline status path that would suppress the status RPC block.

## Test Signals

Good tests include name and ID lookup, LRU recycling under max-volume pressure, restart validation, concurrent refresh waiters, VLDB U/N/O fallback, multihomed UUID expansion, `.readonly` lookup when the base name is absent, rename recovery by ID, linked-cell fallback, RO replica randomization, server-rank change reorder, negative-cache expiration, mixed RO-release refresh every five minutes, VNOVOL/VMOVED forced refresh, offline/busy/down transitions, RO callback renewal, and shutdown notification/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.h

## Purpose

`cm_volume.h` defines the Windows cache manager volume object contract. It declares the in-memory structures, flags, hash macros, and APIs used by cache-manager lookup, server selection, refresh, validation, status notification, and RO callback renewal code.

## Important APIs, Types, and Functions

`cm_vol_state_t` represents one RW, RO, or backup volume variant. It carries the volume ID, root parent fid, server-ref list, `enum volstatus`, per-state flags, and hash-chain metadata. `cm_volume_t` is the owning volume group object with LRU/all/name queues, cell binding, base name, three `vol[]` states, per-volume RW lock, reset/update/noexist/DFS/mixed flags, interlocked reference count, RO callback metadata, last VLDB update time, and cached RO size. The header exposes lookup APIs (`cm_FindVolumeByName()`, `cm_FindVolumeByID()`, `cm_FindVolumeByFID()`, `cm_GetVolumeByFID()`), lifecycle APIs, refresh/status APIs, hash/LRU helpers, and state/type helpers.

## Control Flow

Callers generally find or create a held `cm_volume_t`, optionally causing a VLDB refresh unless `CM_GETVOL_FLAG_NO_RESET` is set. Server-selection code calls `cm_GetVolServers()` or `cm_ChecksumVolumeServerList()` and later frees returned server lists. Daemon and error paths use `cm_RefreshVolumes()`, `cm_ForceUpdateVolume()`, `cm_CheckOfflineVolumes()`, and `cm_UpdateVolumeStatus()` to mark cached entries stale or recompute availability.

## State and Persistence Behavior

The declared fields are stored in the cache manager's shared `cm_data` arena and can survive process restart depending on cache-file mode. The magic number and validation API support sanity checking that persisted pointers still point into expected arenas. Flags split between per-volume metadata (`CM_VOLUMEFLAG_*`) and queue/hash membership (`CM_VOLUME_QFLAG_*`) so object lifetime and refresh state can be tracked separately.

## Dependencies and Integration Points

The header depends on `opr/jhash.h`, fid, cell, server, user, and request types from the cache manager, plus `enum volstatus` and RW/RO/BK constants from surrounding OpenAFS headers. It is consumed by volume, scache, callback, server-list, pioctl, and diagnostic paths.

## Risks and Edge Cases

Hash macros rely on `cm_data.volumeHashTableSize` being initialized and power/size-compatible with the ID mask expression. Lock annotations in comments matter: `serversp` belongs with `cm_serverLock`, `vol[]` and `flags` with the volume RW lock, and queue/hash metadata with `cm_volumeLock`. Any future field change must preserve restart validation and interlocked reference-count assumptions.

## Test Signals

Compile-time tests should catch prototype drift. Runtime tests should exercise all public lookup modes, per-type state selection by ID/name/type, hash insertion/removal, LRU movement/removal, replicated flag reporting, status transitions, and validation after cache reuse or restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ctokens.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/ctokens.c

## Purpose

`ctokens.c` is a small Windows command-line utility that lists Kerberos/AFS tokens currently held by the cache manager. It is equivalent in role to a `tokens` command: enumerate token services and print client identity, service principal, and expiration status.

## Important APIs, Types, and Functions

The program's single `main()` initializes Winsock, validates that only optional help-style usage is requested, loops with `ktc_ListTokens()`, fetches each token with `ktc_GetToken()`, and formats `ktc_principal` and `ktc_token` data. It handles `KTC_NOENT` as end-of-list, `KTC_NOCM` as cache-manager-not-started, and any other nonzero code as unexpected.

## Control Flow

After printing a heading, the program starts at token index zero. `ktc_ListTokens()` returns the next service principal and updates the cursor. For each service, `ktc_GetToken()` retrieves the token and client principal. The display name is built from client name and optional instance, with special formatting for empty users, `AFS ID...`, and `Unix UID...`. Expired tokens are detected by comparing `token.endTime` with `time(NULL)`; unexpired tokens use `ctime()` with day/seconds/year trimmed.

## State and Persistence Behavior

The program is read-only. It does not store tokens, mutate cache-manager state, or persist configuration. All state is stack-local except for the cache manager token state accessed through the `ktc_*` API.

## Dependencies and Integration Points

It depends on Windows Winsock initialization, OpenAFS auth/ktc libraries, roken/stds compatibility headers, and the running AFS cache manager. It integrates with users and scripts as a diagnostic CLI.

## Risks and Edge Cases

String assembly uses fixed 100-byte `userName` with `strcpy()`/`strcat()`, so unexpectedly long principal pieces would be unsafe. `ctime()` returns a shared static buffer and the code mutates it in place, which is fine for this single-threaded utility but brittle. Command-line handling prints usage for any extra argument rather than interpreting `-help` specifically. Errors fetching one token are reported and enumeration continues.

## Test Signals

Tests should cover no cache manager, no tokens, one valid token, one expired token, token with instance, anonymous/empty display, `AFS ID` and `Unix UID` formatting, `ktc_GetToken()` failure for a listed service, and long principal/cell names if hardened.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/ctokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cunlog.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cunlog.c

## Purpose

`cunlog.c` implements the Windows `unlog` utility for discarding AFS/Kerberos tokens from the cache manager. It can forget tokens for selected cells or forget all cached tokens.

## Important APIs, Types, and Functions

`CommandProc()` is the command handler registered through the OpenAFS `cmd` package. It builds an `afs` service principal per `-cell` item and calls `ktc_ForgetToken()`, or calls `ktc_ForgetAllTokens()` when no cells are supplied. `main()` initializes Winsock, defines the syntax with optional `-cell` list, dispatches the command, and returns the dispatch status.

## Control Flow

If `-cell` is present, the handler iterates each cell item, clears the service instance, sets service name `afs`, and forgets just that service token. Failures are printed and the final nonzero code is retained. Without `-cell`, it requests a global token purge and reports a single failure if present.

## State and Persistence Behavior

This utility mutates cache-manager token state but does not maintain its own files or registry values. The only persistent effect is that future authenticated AFS requests from the current token set lose the discarded credentials.

## Dependencies and Integration Points

It depends on the OpenAFS auth/ktc library, command parser, AFS integer/protocol headers, and Winsock startup. It integrates with user login/logout workflows and any scripts that need to clear cell-specific credentials.

## Risks and Edge Cases

Cell names are copied directly into `server.cell` without a visible bounds check, so safety depends on command parser limits and `ktc_principal` sizing. Multi-cell mode returns only the last error, which can hide earlier failures from callers. The utility does not distinguish missing tokens from cache-manager communication failures in its output beyond the returned code.

## Test Signals

Tests should cover no-argument full token purge, one-cell purge, multiple cells with mixed success/failure, long cell names, cache-manager-not-running errors, and command parser behavior for malformed `-cell` lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cunlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs.c

## Purpose

`fs.c` is the Windows OpenAFS `fs` command implementation. It registers dozens of subcommands and translates command-line requests into cache-manager pioctls, VLDB lookups, protection-server lookups, registry/service operations, and formatted diagnostics. It covers ACL editing, cache flushing, volume and quota reporting, mount-point management, server preference management, cell configuration, cache options, tracing/debugging, encryption and data-verification flags, and Unix-like owner/group/mode operations.

## Important APIs, Types, and Functions

`wmain()` initializes Winsock, converts the wide command line to UTF-8, registers command syntaxes via `cmd_CreateSyntax()`, then runs `cmd_Dispatch()`. ACL commands use `SetACLCmd()`, `CopyACLCmd()`, `CleanACLCmd()`, `ListACLCmd()`, `PRights()`, `Convert()`, and helpers from `fs_acl.c`. File/volume commands include `GetCallerAccess()`, `FlushCmd()`, `FlushAllCmd()`, `FlushVolumeCmd()`, `SetVolCmd()`, `ExamineCmd()`, `ListQuotaCmd()`, `WhereIsCmd()`, `DiskFreeCmd()`, `QuotaCmd()`, `GetFidCmd()`, `ChOwnCmd()`, `ChGrpCmd()`, and `ChModCmd()`. Mount/cell/server commands include `ListMountCmd()`, `MakeMountCmd()`, `RemoveMountCmd()`, `CheckServersCmd()`, `CheckVolumesCmd()`, `ListCellsCmd()`, `NewCellCmd()`, `WhichCellCmd()`, `WSCellCmd()`, `SetCellCmd()`, `GetCellCmd()`, `SetPrefCmd()`, and `GetPrefCmd()`. Diagnostics and settings include `SysNameCmd()`, `StoreBehindCmd()`, `SetCryptCmd()`, `GetCryptCmd()`, `TraceCmd()`, `UuidCmd()`, `MemDumpCmd()`, `MiniDumpCmd()`, `CSCPolicyCmd()`, `RxStatProcCmd()`, `RxStatPeerCmd()`, `SmbUnicodeCmd()`, `SetDataVerifyCmd()`, `GetDataVerifyCmd()`, and hidden `TestVolStatCmd()`.

## Control Flow

Most subcommands follow a common pattern: default path lists to `.`, build a `ViceIoctl` with `space` as the shared transfer buffer, optionally prefetch a fid and literal-resolution options with `VIOCGETFID`, call one or more `pioctl_utf8()` operations, print formatted results, and accumulate per-item errors rather than aborting the whole list. ACL commands fetch serialized ACLs with `VIOCGETAL`, parse and normalize them, modify `AclEntry` lists, serialize back with `AclToString()`, and store through `VIOCSETAL`. Volume/quota/status commands exchange `VolumeStatus` plus trailing strings. Mount commands split parent directory and final component, handle Windows UNC/NetBIOS AFS paths and freelance root permissions, and use mount-specific pioctls to create/stat/delete mount points. Server preference commands batch hostname/rank pairs into pioctl buffers, flushing when near `MAXINSIZE`.

## State and Persistence Behavior

The process itself is stateless apart from global command buffer `space`, `uclient`, `gblob`, and `rxInitDone`. It mutates cache-manager state through pioctls: ACLs, cache flush state, volume status/quota messages, mount points, server preferences, cell definitions, setuid cell flags, sysname, store-behind defaults, Rx security level, trace state, UUID generation, data verification, Unicode setting, callback address, and volume-status test hooks. It also mutates Windows registry CSC policy values and can ask the AFSD service to generate a minidump. VLDB checks in `mkmount` are advisory unless `-fast` is omitted and VLDB initialization succeeds.

## Dependencies and Integration Points

The file depends on OpenAFS command parsing, `pioctl_utf8()` and Windows cache-manager ioctl contracts, `fs_utils`, ACL helpers, `parsemode`, cell config, protection server, VLDB/ubik client initialization, host lookup utilities, Rx stats flags, Windows registry/service APIs, Winsock, and admin/root checks. It is the primary administrative CLI surface for the Windows AFS client.

## Risks and Edge Cases

The shared `space` buffer and many hand-packed variable-length pioctl payloads make length accounting critical. Some code still uses old pointer/assignment idioms and fixed buffers, so long names, malformed cache-manager replies, or unexpected pioctl sizes are high-risk. Several admin commands are Windows-only or non-Windows-only behind preprocessor branches. Numeric owner/group parsing treats `atoi()==0` as "name lookup", making true ID 0 ambiguous. `NewCellCmd()` appears to read `-fsport`/`-vlport` from the wrong parameter indexes in its integer conversions. Error reporting sometimes passes pioctl return code instead of `errno` to `fs_Die()`. Mount-point path handling has many Windows UNC and freelance special cases.

## Test Signals

Useful tests include command registration and aliases, UTF-8 command-line conversion, every pioctl payload size and out-size validation, ACL set/list/copy/clean for AFS and DFS ACLs, literal mountpoint options, offline volume status mapping, quota formatting, mount create/list/remove under normal AFS and freelance root, server-preference batching and VL-only mode, cell add/list/status/set, sysname multi-value set/get, store-behind file/default modes, crypt and verify flags, trace/uuid/memdump/minidump/admin denial paths, chown/chgrp name-to-ID resolution, chmod symbolic and octal parsing, and hidden volume-status test inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs.h

## Purpose

`fs.h` is a minimal include guard and shared declaration header for the Windows `fs` command family. It exposes `Die(int code, char *filename)` to translation units that need the command's common error-reporting routine.

## Important APIs, Types, and Functions

The only API is `Die()`. In this source subset, `fs.c` primarily uses `fs_Die()` from `fs_utils.h`, but the header remains part of the command-line utility interface and may support other build variants or older users.

## Control Flow

There is no runtime control flow in the header. Including it provides the prototype before command handlers call error-reporting code.

## State and Persistence Behavior

The header declares no state and has no persistence behavior.

## Dependencies and Integration Points

It depends only on C linkage compatibility from the including compilation unit. It is included by `fs.c` alongside `fs_utils.h`, `fs_acl.h`, command parsing, AFSD, and pioctl headers.

## Risks and Edge Cases

The risk is interface drift: if `Die()` is removed, renamed, or made incompatible while some platform-specific object still expects this prototype, builds can fail or silently pick an unintended declaration. The sparse header also suggests legacy API overlap with `fs_Die()`.

## Test Signals

Build all Windows and non-Windows variants that include `fs.h`, and check for warnings about missing or conflicting `Die()` declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.c

## Purpose

`fs_acl.c` implements the ACL parser, serializer, mutator, cleanup, and validation helpers used by the `fs` command. It supports both traditional AFS ACL text and DFS ACL variants, including positive and negative lists, relative add/remove semantics, and numeric-name pruning through the protection server.

## Important APIs, Types, and Functions

Memory management is handled by `ZapAcl()` and `ZapList()`. `ParseAcl()` converts cache-manager ACL text into `struct Acl`; `EmptyAcl()` creates an empty ACL while preserving DFS metadata if present; `AclToString()` serializes an ACL into the wire/text form accepted by `VIOCSETAL`. `FindList()` locates entries case-insensitively. `ChangeList()` adds, replaces, relative-adds, relative-removes, denies, or destroys rights. `PruneList()` removes zero or `-1` entries. `CleanAcl()` removes bad numeric usernames for AFS ACLs, using `BadName()` and PRDB lookups.

## Control Flow

Parsing reads the plus count and optional `dfs:<type> <cell>` tag, skips to the minus count, then allocates plus and minus entries from successive lines. On partial parse failure it frees any entries already allocated. Mutation first searches the selected list; existing entries are updated according to `rtype`, then pruned. New entries are inserted at list head unless the operation is a relative delete of a non-existing entry. Serialization writes counts and optional DFS metadata, then appends plus and minus entries as `name rights` lines.

## State and Persistence Behavior

The module owns heap-allocated `Acl` and `AclEntry` objects during command execution. It has no durable storage by itself; persistence happens when `fs.c` sends serialized ACL text back to the cache manager. `AclToString()` uses a static `AFS_PIOCTL_MAXSIZE` buffer, so callers must consume or copy it before the next serialization call.

## Dependencies and Integration Points

It depends on AFS constants and rights bits, Windows string-safety APIs, `afs/ptuser.h` and `afs/ptserver.h` for name validation, `cm_GetConfigDir()` for PRDB configuration, and `fs_acl.h` for structure definitions. Its primary consumer is `fs.c` ACL subcommands.

## Risks and Edge Cases

ACL text is trusted only after bounded string length checks, but the code still exits the process on string-copy failures. `AclToString()` can overflow logically if too many entries fit in memory but not in one pioctl buffer; it exits on `StringCbCat()` failure. `BadName()` has an uninitialized `code` path when no cell name is provided, which can make numeric-name validation undefined. DFS cleanup is intentionally skipped, and DFS invalid combinations are mostly discovered only when the cache manager/fileserver rejects the stored ACL.

## Test Signals

Tests should cover empty input, malformed counts, truncated plus/minus lists, AFS and DFS ACL parse/serialize round trips, `read`/`write`/`all`/`none`/`null` conversions via `fs.c`, relative add/remove pruning, negative rights, duplicate names with case differences, large ACLs near `AFS_PIOCTL_MAXSIZE`, numeric-name cleanup with valid and anonymous PRDB results, and parse-failure memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.h

## Purpose

`fs_acl.h` defines the ACL data structures, rights constants, mutation operation enum, and helper prototypes shared between `fs.c` and `fs_acl.c`.

## Important APIs, Types, and Functions

`struct Acl` stores ACL type (`dfs`), DFS default cell, plus/minus counts, and linked lists. `struct AclEntry` stores one principal name and rights mask. The header defines DFS wire-protocol rights bits, application-defined DFS user bits, `DFS_SEPARATOR`, and `enum rtype` values: `add`, `destroy`, `deny`, `reladd`, and `reldel`. Public helpers include `ParseAcl()`, `AclToString()`, `EmptyAcl()`, `CleanAcl()`, `ChangeList()`, `FindList()`, `PruneList()`, `ZapAcl()`, and `ZapList()`.

## Control Flow

There is no executable control flow, but the structures drive the ACL command lifecycle: parse text into linked lists, modify entries with an `rtype`, prune invalid zero/deleted entries, serialize text, then free all list memory.

## State and Persistence Behavior

The header defines transient in-process ACL state. Persistent ACL changes occur only when serialized text is passed to cache-manager pioctls by callers. `sec_rgy_name_t` and `ACL_MAXNAME` establish fixed limits that shape accepted ACL names and DFS cell strings.

## Dependencies and Integration Points

It relies on AFS integer types and rights constants from including files. It integrates with the Windows `fs` command ACL implementation and preserves DFS rights values that are part of the translator wire protocol.

## Risks and Edge Cases

Rights constants are protocol-sensitive and must not be renumbered. `ACL_MAXNAME` truncation or mismatch with parser `%100s` limits can affect principal names. The `dfs` field doubles as a Boolean and ACL subtype, so callers must preserve values 0 through 3 rather than treating it as arbitrary truth.

## Test Signals

Build tests should cover all include sites. Behavioral tests should verify every rights bit prints and parses correctly, `rtype` operations mutate lists as expected, and DFS object/initial-directory/initial-object ACL types survive parse and serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/fs_acl.h -->
