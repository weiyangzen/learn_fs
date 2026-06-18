# sources/distributed-fs/openafs/src/WINNT/afsd/smb3.c lines 1-7668

## Scope

This chunk covers the first 7,668 lines of the Windows OpenAFS SMB/CIFS v3 server implementation. It includes global SMB3 transaction state, authentication/session setup, tree connect, SMB_COM_TRANSACTION/RAP/named-pipe dispatch, Transaction2 dispatch, open/query/set handlers, DFS referral support, directory enumeration, OpenAndX, byte-range locking, attribute get/set, ReadAndX/WriteAndX, and the beginning of NTCreateX. The source file continues after this chunk; `smb_ReceiveNTCreateX` is only partially visible here.

## Purpose

The code translates SMB1/v3 and Transaction2 wire requests into OpenAFS cache-manager operations on users, tree IDs, FIDs, scaches, buffers, locks, and directory search objects. Its main responsibilities in this span are:

- authenticate or identify SMB sessions and attach them to `smb_user_t`, `smb_username_t`, and `cm_user_t` records;
- create tree connections to AFS submounts, root shares, and IPC$;
- assemble multi-packet Transaction and Transaction2 requests, dispatch them, and format SMB-compatible responses or errors;
- expose AFS filesystem and share metadata in SMB/RAP/NT query layouts;
- open files, create files, truncate existing files, and create special synthetic IOCTL/RPC FIDs;
- enumerate directories with wildcard matching, 8.3 short-name support, hidden-dotfile filtering, delayed metadata patching, and bulk status calls;
- enforce byte-range locks and dispatch read/write traffic to normal files, the AFS ioctl sentinel, or MSRPC named pipes.

## Important state and types

- `smb_Directory_Watches` and `smb_Dir_Watch_Lock` are global directory notification state declared at lines 42-43, but the notification implementation is outside this chunk except for create notifications and watch flags.
- `smb_tran2DispatchTable` and `smb_rapDispatchTable` are global dispatch arrays used by `smb_ReceiveV3Tran2A` and `smb_ReceiveV3Trans` to map opcodes to handlers.
- `smb_tran2AssemblyQueuep` is a global queue of partially assembled transaction packets, protected by `smb_globalLock`.
- `smb_ExecutableExtensions` backs `smb_IsExecutableFileName`, which checks case-insensitive filename suffixes.
- `struct smb_ext_context` stores SSPI credential/context handles plus a partial token during multi-leg extended authentication.
- RAP packed structs (`smb_rap_share_info_*`, `smb_rap_wksta_info_10_t`, `smb_rap_server_info_*`) mirror legacy LAN Manager response layouts and intentionally use ANSI-packed fields.
- `struct smb_ShortNameRock` carries a target normalized name/vnode and output buffer for generated 8.3 names.
- `struct smb_v2_referral` describes DFS referral v2 response fields.
- The visible NTCreateX constants define create dispositions, request flags, and create options used by the NT create handler starting at line 7492.

Most persistent behavioral state is not stored in this file directly; this code mutates shared objects owned by the SMB and cache-manager layers: `vcp->flags`, `vcp->secCtx`, `vcp->uidCounter`, `vcp->tidCounter`, `smb_user_t.flags`, `smb_username_t.flags/userp`, `smb_tid_t.pathname/userp/flags`, `smb_fid_t.flags/scp/userp`, `cm_scache_t.flags/mask/clientModTime`, directory search cookies, lock queues, and Windows registry configuration.

## Authentication and sessions

`smb_GetTran2User` resolves a Transaction2 packet UID to a held `cm_user_t` by finding the SMB UID and calling `smb_GetUserFromUID`.

`smb_NegotiateExtendedSecurity` creates an initial SSPI "Negotiate" token using inbound credentials and `AcceptSecurityContext`, copies any returned token to heap memory, and immediately destroys the partial security context. `smb_AuthenticateUserExt` continues the real session setup handshake: it reuses `vcp->secCtx` when `SMB_VCFLAG_AUTH_IN_PROGRESS` is set, optionally reassembles partial tokens, calls SSPI, stores continuation context back on the VC, emits a reply token, and on success queries the authenticated name and SID string. It returns cache-manager errors such as `CM_ERROR_GSSCONTINUE` and `CM_ERROR_BADPASSWORD`.

`smb_AuthenticateUserLM` constructs an `MSV1_0_LM20_LOGON` blob, fills LM/NT challenge responses from the SMB packet, calls `LsaLogonUser`, and maps failures to `CM_ERROR_BADLOGONTYPE` or `CM_ERROR_BADPASSWORD`. `smb_GetNormalizedUsername` canonicalizes `[domain]\[user]` or `user@domain` forms into lowercase client strings.

`smb_ReceiveV3SessionSetupX` is the main session setup handler. It validates client buffer/mpx sizes, resets all VCs when `VCNumber` is zero, chooses the extended, NTLM, or no-auth path based on negotiated flags and `smb_authType`, records client capabilities (`SMB_VCFLAG_STATUS32`, `SMB_VCFLAG_USEUNICODE`), and either continues GSS authentication or creates/reuses an SMB UID. If an SSPI SID was available, the SID string becomes the username and `SMB_USERNAMEFLAG_SID` is set. The handler deliberately reuses existing per-session usernames to avoid losing tokens from repeated Windows 2000 setup calls. `smb_ReceiveV3UserLogoffX` marks the UID for deletion but does not immediately destroy it because the VC may still reference it.

## Tree connect and shares

`smb_ReceiveV3TreeConnectX` parses password, UNC path, and service strings; extracts the share name; recognizes IPC$; allocates a new TID; and attaches either an IPC tree or a share path found via `smb_FindShare`. For NT clients it advertises search support, optional DFS share status from the `AdvertiseDFS` registry value, and client-side caching policy from `smb_FindShareCSCPolicy`. The returned service string is `A:`/`AFS` for normal shares and `IPC` for IPC.

RAP share enumeration is implemented in `smb_ReceiveRAPNetShareEnum` and `smb_ReceiveRAPNetShareGetInfo`. Enumeration combines the synthetic `all` submount, registry submounts under `...\Submounts`, and root AFS directory entries collected through `cm_ApplyDir`. Names are truncated into legacy 13-byte RAP fields, with comments/path strings represented by offsets into the data buffer. `smb_ReceiveRAPNetWkstaGetInfo` and `smb_ReceiveRAPNetServerGetInfo` provide workstation/server identity fields such as local NetBIOS name, current UID username, `WORKGROUP`, server domain, version 5.1, and "OpenAFS Client".

## Transaction assembly and dispatch

`smb_FindTran2Packet`, `smb_NewTran2Packet`, and `smb_FreeTran2Packet` manage partial Transaction/Transaction2 assembly records. New records hold a VC reference, copy SMB identity fields, allocate parameter/data buffers, and preserve Unicode preference for string parsing. `smb_GetTran2ResponsePacket`, `smb_SendTran2Packet`, and `smb_SendTran2Error` construct response views and enforce the parallel parameter/data offset calculations required by SMB transaction framing.

`smb_ReceiveV3Trans` handles `SMB_COM_TRANSACTION` and secondary packets. It copies parameter/data fragments by displacement, removes complete requests from the assembly queue, and dispatches either RAP calls (`setupCount == 0`) through `smb_rapDispatchTable` or named-pipe setup/transaction calls (`setupCount == 2`) to `smb_nmpipeSetState` and `smb_nmpipeTransact`. Non-RPC pipe operations mostly return `CM_ERROR_BADOP` or `CM_ERROR_BADFD`.

`smb_ReceiveV3Tran2A` handles `SMB_COM_TRANSACTION2` and secondary packets similarly, dispatching opcode values through `smb_tran2DispatchTable`. It logs request context if a dispatched operation takes more than 45 seconds, including user, TID path, optional FID path, and AFS fid fields. This slow-request logging is a useful operational test signal.

## Open, query, and set operations

`smb_ReceiveTran2Open` parses `TRANS2_OPEN2`, resolves the TID-relative path, handles IPC/IOCTL/RPC special files, validates client strings, then uses `cm_NameI`, `cm_Lookup`, `cm_CheckOpen`, `cm_Create`, and `cm_SetAttr` to implement existing-file open, exclusive open failure, truncate-on-open, and create-if-missing semantics. Successful creates notify directory watchers with `smb_NotifyChange` when the parent scache has `CM_SCACHEFLAG_ANYWATCH`. Normal opens allocate an SMB FID, attach the scache and user, set read/write/created flags, call `cm_Open`, and return SMB open metadata.

`smb_ReceiveTran2QFSInfo` returns synthetic volume/allocation/device/attribute information for AFS. Capacity is hard-coded to large fixed values, the volume label and filesystem name are `AFS`, the device type is network filesystem, and long-name/case-preserving flags are advertised. Unix and Mac FS info levels are rejected.

`cm_GetShortName` and `cm_GetShortNameProc` locate a directory entry matching the normalized last component and vnode, then generate an 8.3 short name via `cm_Gen8Dot3Name`.

`smb_ReceiveTran2QPathInfo` supports path-based standard, basic, standard NT, EA, name, all, alternate name, and stream info. It has a special synthetic metadata path for the AFS ioctl filename, a defensive `desktop.ini` avoidance path to prevent expensive lookups in unevaluated mount points or unfetched directories, DFS-link handling, status fetch through `cm_SyncOp`, and output marshalling from `cm_scache_t` fields. Delete-pending and access flags may be inferred from an existing FID found by scache.

`smb_ReceiveTran2SetPathInfo` implements path-based legacy standard/EA-size setting. It rejects most info levels, applies the same `desktop.ini` avoidance logic, looks up the path, obtains current status, sets length, optional client modification time, and read-only mode-bit transitions via `cm_SetAttr`. It returns `CM_ERROR_EAS_NOT_SUPPORTED` for EA queries.

`smb_ReceiveTran2QFileInfo` is the FID-based query counterpart. It validates deleted/unknown FIDs, synchronizes scache status, and returns basic, standard, EA, name, or stream info. IOCTL FIDs get synthetic hidden/system zero-length metadata; normal FIDs use scache length, link count, file type, delete-on-close state, and `NTopen_wholepathp`.

`smb_ReceiveTran2SetFileInfo` handles FID-based basic attributes, delete disposition, allocation size, and EOF. It enforces delete/write open rights based on FID flags, updates client mtime and read-only Unix mode bits, marks or clears `SMB_FID_DELONCLOSE` after `cm_CheckNTDelete`, and truncates/extends via `cm_SetAttr`.

FSCTL, IOCTL2, find-notify, create-directory, and transaction2 session-setup handlers in this chunk are stubs returning unsupported errors.

## DFS and IPC integration

When `DFS_SUPPORT` is enabled, `smb_ReceiveTran2GetDFSReferral` handles Unicode IPC$ DFS referral requests. It accepts requests under the local NetBIOS name, recognizes `all` and `*.` shares, tests AFS names through `cm_NameI`, handles `CM_ERROR_PATH_NOT_COVERED` by walking backward to locate an `msdfs:` link, and falls back to share lookup. It returns version 1 or version 2 referral records depending on build flags. Without DFS support it returns `CM_ERROR_NOSUCHDEVICE`. `smb_ReceiveTran2ReportDFSInconsistency` is a logged unsupported operation.

IPC integration also appears in open paths: `TRANS2_OPEN2`, `OpenAndX`, and the visible start of `NTCreateX` recognize `SMB_IOCTL_FILENAME` for AFS pioctl transport and well-known MSRPC services under IPC$, allocate a FID, and initialize it through `smb_SetupIoctlFid` or `smb_SetupRPCFid`.

## Directory enumeration

`smb_ApplyV3DirListPatches` is the second pass for directory output records. Enumeration first writes names and placeholders while walking AFS directory pages; patching later fills timestamps, lengths, and attributes after status can be fetched safely. The patcher checks directory ACLs, may mark results as fake on no access, batches cache misses through `cm_TryBulkStatRPC`, falls back to per-entry `cm_SyncOp` when bulk stat fails, resolves symlinks, preserves hidden-dotfile flags, and frees the patch list.

`smb_T2SearchDirSingle` optimizes no-wildcard `FindFirst` by doing one directory lookup instead of scanning. It supports the same info levels as the full search, optional short names, AFS ioctl synthetic entries, hidden/directory filtering, record alignment, and then calls `smb_ApplyV3DirListPatches`.

`smb_ReceiveTran2SearchDir` implements `TRANS2_FIND_FIRST2` and `TRANS2_FIND_NEXT2`. It creates or looks up `smb_dirSearch_t`, stores attributes/mask/TID-relative path, caps returned names at 500, syncs directory status, scans AFS3 directory pages through buffers, skips header/free/deleted entries, converts filesystem names to client and normalized forms, matches masks with exact/inexact retry behavior, optionally emits resume keys and 8.3 names, enforces max-return-data alignment, periodically applies patches every `AFSCBMAX` entries, and stops early if the request nears `RDRtimeout`. It closes searches based on flags, end-of-search, empty results, or errors. `smb_ReceiveV3FindClose` deletes an open search handle; find-notify close is a no-op success.

## OpenAndX, locking, attributes, and I/O

`smb_ReceiveV3OpenX` is an older open path parallel to `TRANS2_OPEN2`. It handles AFS ioctl/RPC sentinel opens, validates names, resolves or creates files, rejects directories for file opens, allocates an FID, attaches scache/user, sets access flags, invokes `cm_Open`, updates chained request FID, and returns open metadata.

`smb_GetLockParams` decodes 10-byte or 20-byte SMB lock records depending on `LOCKING_ANDX_LARGE_FILES`. `smb_ReceiveV3LockingX` validates the FID, rejects ioctl FIDs, syncs the scache with lock state, downgrades exclusive locks on read-only opens to shared locks, rejects atomic lock-type changes, processes cancel requests against `smb_allWaitingLocks`, unlocks requested ranges, locks requested ranges through `cm_Lock`, queues waitable failed locks as `smb_waitingLockRequest_t` with copied packets and held scache/VC references, rolls back partial locks on failure, and suppresses immediate response for queued waits.

`smb_ReceiveV3GetAttributes` and `smb_ReceiveV3SetAttributes` implement `QUERY_INFORMATION2` and `SET_INFORMATION2`. They reject deleted/ioctl/unknown FIDs, sync status for queries, return DOS search times, size/allocation size, and attributes, and set mtime only when a nonzero valid search time is present.

`smb_ReceiveV3WriteX` supports 32-bit and 64-bit offsets, routes IOCTL/RPC FIDs to specialized handlers, checks write byte-range locks, preserves explicit mtime-setting intent by not updating `clientModTime` after `SMB_FID_MTIMESETDONE`, loops over `smb_WriteData` until complete or partial write, and returns total written. `smb_ReceiveV3ReadX` similarly handles IOCTL/RPC FIDs, validates 64-bit offsets, checks read locks, formats the AndX response data offset/length, calls `smb_ReadData`, and corrects the final byte count.

## Partial NTCreateX coverage

The chunk includes constants and the start of `smb_ReceiveNTCreateX`. The visible portion parses name length, flags, requested oplocks, desired access, extended attributes, share access, create disposition, create options, directory/non-directory intent, and a possibly unterminated path string copied into `realPathp`. It resolves the base TID path when `baseFid == 0`, detects IPC trees, and begins special-case IOCTL/RPC FID setup. The normal NT create/open/create-directory/share-mode/delete-on-close/prefetch behavior continues after line 7668 and is not covered in this chunk.

## Dependencies and integration points

- Windows security APIs: SSPI (`AcquireCredentialsHandle`, `AcceptSecurityContext`, `CompleteAuthToken`, `QueryContextAttributesW`, `QuerySecurityContextToken`), SID helpers, LSA network logon, registry APIs, and Windows `FILETIME`/NT status constants.
- OpenAFS cache manager: `cm_NameI`, `cm_Lookup`, `cm_Create`, `cm_SetAttr`, `cm_Open`, `cm_SyncOp`, `cm_GetBuffer`, `cm_ApplyDir`, `cm_GetSCache`, `cm_TryBulkStatRPC`, lock APIs, scache fields, callbacks, DFS mapping notification, name conversion, and request context fields.
- SMB server core: packet formatting/parsing, UID/TID/FID lookup/reference management, string parse/unparse helpers, error mapping, dispatch-table initialization outside this chunk, directory search management, SMB lock wait queues, IOCTL/RPC FID handlers, and notification delivery.
- Configuration: registry values `AllSubmount`, `AdvertiseDFS`, and `Submounts`; compile-time flags such as `SMB_UNICODE`, `DFS_SUPPORT`, `SPECIAL_FOLDERS`, `AFS_FREELANCE_CLIENT`, and `NOFINDFIRSTOPTIMIZE`.

## Risks and edge cases

- Many packet fields are trusted after minimal validation. Malformed counts, offsets, or string lengths can affect heap allocation, `memcpy`, and response-buffer writes; transaction assembly and directory record alignment are especially sensitive.
- `smb_IsExecutableFileName` computes `&name[j]` where `j` can be negative if an extension is longer than the filename.
- Several cleanup paths mix held references, mutexes, and early returns. Open/create paths deliberately leave scaches held in FIDs, but error paths need careful auditing for leaked `cm_user_t`, `cm_scache_t`, `smb_fid_t`, transaction packet, and heap string references.
- `smb_ReceiveTran2SetPathInfo` obtains a write lock but releases it with `lock_ReleaseRead`, which is a notable lock-mode risk visible in this chunk.
- Directory patching may present fake timestamps/attributes on no-access or no-callback entries to avoid client errors; this is compatible behavior but can hide freshness or access failures from callers.
- Legacy compatibility behavior is broad: `desktop.ini` avoidance, truncated RAP share names, fake volume sizes, fake IOCTL metadata, special handling for Windows 2000 repeated session setup, and NT client mtime workaround all need regression tests before refactoring.
- The locking path has asynchronous wait state with copied input/output packets and explicit VC/scache holds; cancellation, timeout, rollback, and response suppression are high-risk concurrency areas.
- DFS referral behavior depends on path-prefix parsing, Unicode assumptions, and mountpoint string interpretation; edge cases can produce either `PATH_NOT_COVERED` or `NOSUCHPATH` depending on client flags.

## Test signals

Useful validation should include SMB clients or protocol tests for:

- extended SSPI session setup continuation, NTLM session setup, anonymous/no-auth setup, SID username mapping, Unicode capability negotiation, and repeated setup on one VC;
- tree connect to normal shares, `all`, registry submounts, invalid shares, IPC$, and DFS-advertised shares;
- fragmented Transaction/Transaction2 requests, invalid opcodes, RAP NetShareEnum/GetInfo, NetWkstaGetInfo, NetServerGetInfo, and named-pipe RPC transact;
- open/create/truncate/exclusive-create paths through `TRANS2_OPEN2` and `OpenAndX`, including invalid names, symlinks, DFS links, IOCTL sentinel, and MSRPC endpoint names;
- all supported path/FID query info levels, stream info, alternate names/8.3 names, delete-pending state, read-only attribute transitions, EOF/allocation changes, and unsupported EA levels;
- directory enumeration exact match, wildcard match, case-inexact fallback, short names, dotfile hiding, buffer-size exhaustion, resume keys, find close, bulkstat fallback, no-access fake metadata, and RDR timeout early exit;
- byte-range lock/unlock/cancel/wait flows, rollback on partial lock failure, read/write lock enforcement, and read-only exclusive-lock downgrade;
- ReadAndX/WriteAndX normal file I/O, 64-bit offsets, partial write detection, IOCTL/RPC routing, deleted FID behavior, and explicit mtime preservation.
