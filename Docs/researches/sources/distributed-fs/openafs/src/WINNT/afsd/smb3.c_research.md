# Research: sources/distributed-fs/openafs/src/WINNT/afsd/smb3.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007712`: lines 1-7668, `Docs/researches/chunks/subset-b-007712_research.md`
- `subset-b-007713`: lines 7669-9921, `Docs/researches/chunks/subset-b-007713_research.md`

## Chunk Research

### subset-b-007712: lines 1-7668

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

### subset-b-007713: lines 7669-9921

# sources/distributed-fs/openafs/src/WINNT/afsd/smb3.c lines 7669-9921

## Scope And Purpose

This chunk covers the OpenAFS Windows SMB server's NT create/open path from the middle of `smb_ReceiveNTCreateX()`, the full `smb_ReceiveNTTranCreate()` implementation, NT transaction dispatch for create/change-notify/security-descriptor operations, directory change notification delivery and cancellation, NT rename/hardlink dispatch, SMB3 initialization of the directory-watch lock, and user lookup helpers.

The code is the SMB1/NT dialect bridge between Windows client requests and the cache manager vnode layer. It translates NT create dispositions, access masks, share modes, directory/file create options, and transaction layouts into cache-manager lookups, opens, creates, truncates, mkdirs, byte-range/share locks, FID state, and response packets. It also implements the server-side state needed for `NT_TRANSACT_NOTIFY_CHANGE`: incoming notify requests are saved as pending SMB packets, later completed by local filesystem mutations or callback breaks, and cancelled by `SMB_COM_NT_CANCEL`.

The assigned range starts after the special `NTCreateX` RPC/IOCTL FID fast path has returned, so lines 7669-8445 are the regular AFS file/directory `NTCreateX` path. `smb_ReceiveNTTranCreate()` is largely duplicated from `NTCreateX`, but parses the NT transaction parameter block instead of SMB AndX words and formats an NT transaction response instead of the direct CreateX response.

## Important APIs, Types, And Functions

Key SMB-facing entry points in this range:

- `smb_ReceiveNTCreateX(smb_vc_t *vcp, smb_packet_t *inp, smb_packet_t *outp)`: handles regular NT Create AndX file and directory opens after the special RPC/IOCTL case. It resolves the path relative to a TID or base FID, creates or opens the target, installs an SMB FID, and fills the CreateX response.
- `smb_ReceiveNTTranCreate(smb_vc_t *vcp, smb_packet_t *inp, smb_packet_t *outp)`: handles `NT_TRANSACT_CREATE` inside `SMB_COM_NT_TRANSACT`. It follows the same cache-manager open/create flow as CreateX but uses transaction parameter/data offsets and transaction response framing.
- `smb_ReceiveNTTranNotifyChange()`: registers a pending directory change watch against an open FID and suppresses the immediate response with `SMB_PACKETFLAG_NOSEND`.
- `smb_ReceiveNTTranQuerySecurityDesc()`: returns a fixed self-relative security descriptor containing owner/group SIDs and a null DACL, subject to a small supported `securityInformation` mask.
- `smb_ReceiveNTTransact()`: dispatches NT transaction function numbers to create, notify-change, and query-security handlers; unimplemented functions return `CM_ERROR_BADOP`.
- `smb_NotifyChange()`: scans pending directory watches, matches by watched scache and notify filter, converts saved request packets into transaction responses, sends them, and frees them.
- `smb_ReceiveNTCancel()`: finds a matching pending notify request by SMB UID/PID/MID/TID, removes it from the watch list, clears watch flags on the scache, and completes the saved packet with NT `STATUS_CANCELLED`.
- `smb_ReceiveNTRename()`: parses old/new path ASCII blocks and dispatches to `smb_Rename()` or `smb_Link()` depending on the NT rename flag.
- `smb3_Init()`: initializes `smb_Dir_Watch_Lock`.
- `smb_FindCMUserByName()` and `smb_FindCMUserBySID()`: map SMB username records to cache-manager `cm_user_t` instances, lazily creating `cm_NewUser()` records.

Core data structures and state:

- `smb_vc_t`: SMB virtual circuit/session state. This range uses it to find users/FIDs, derive share-lock keys from `vcID`, and decide whether long-name response flags should be set.
- `smb_packet_t`: incoming/outgoing SMB packet buffer. Notify-change saves a copy of an incoming packet and later mutates it into the outgoing response.
- `smb_fid_t`: open-handle state. The create paths populate `fidp->scp`, `fidp->userp`, `fidp->flags`, `fidp->NTopen_dscp`, `fidp->NTopen_pathp`, and `fidp->NTopen_wholepathp`.
- `cm_scache_t`: cache-manager file/directory vnode. The create paths transfer a held scache into `fidp->scp`, set `CM_SCACHEFLAG_SMB_FID`, and use scache flags for deleted, watched, watched-subtree, and prefetching state.
- `cm_user_t`: authenticated cache-manager user associated with the SMB request and saved on the FID.
- `cm_req_t`: per-operation request context initialized with `smb_InitReq()`.
- `cm_lock_data_t *ldp`: opaque lock/open validation state returned by `cm_CheckNTOpen()` and released through `cm_CheckNTOpenDone()`.
- `smb_Directory_Watches` and `smb_Dir_Watch_Lock`: global linked list and mutex for pending directory notify packets.

Important cache-manager APIs:

- `cm_RootSCachep()`, `smb_LookupTIDPath()`, `cm_NameI()`, and `cm_Lookup()` resolve SMB paths to parent and target scaches.
- `cm_Create()`, `cm_MakeDir()`, and `cm_SetAttr()` create files, create directories, and truncate existing files for overwrite dispositions.
- `cm_CheckNTOpen()` and `cm_CheckNTOpenDone()` enforce NT open/share rules at the cache-manager/file-server layer while the FID number is already reserved.
- `cm_EvaluateSymLink()` resolves symlink scaches when the requested object must be a regular file or when truncating through a symlink.
- `cm_Lock()` creates a synthetic byte-range share lock when share-write is not allowed.
- `cm_Open()` finalizes the cache-manager open after the FID state is installed.
- `cm_QueueBKGRequest(..., cm_BkgPrefetch, ...)` queues whole-file prefetch for executable files.

Important SMB helpers:

- `smb_ParseStringCb()`, `smb_ParseASCIIBlock()`, `smb_StripLastComponent()`, `smb_IsLegalFilename()`, and `cm_IsValidClientString()` parse and validate client paths.
- `smb_SetInitialModeBitsForFile()` and `smb_SetInitialModeBitsForDir()` map NT extended attributes into initial Unix mode bits.
- `smb_ExtAttributes()` maps cache-manager scache state back to SMB extended attributes.
- `smb_FindFID()`, `smb_ReleaseFID()`, and `smb_CloseFID()` allocate, hold, release, and clean up SMB FID records.
- `smb_SetSMBParm*()`, `smb_GetSMBParm*()`, `smb_SetSMBDataLength()`, `smb_GetSMBData()`, `smb_UnparseString()`, `smb_CopyPacket()`, `smb_SendPacket()`, and `smb_FreePacket()` manipulate SMB packet fields.

## Control Flow

### NT CreateX regular open/create path

The visible portion of `smb_ReceiveNTCreateX()` begins by freeing the special RPC/IOCTL path buffer and returning when that earlier branch succeeds. For regular file service, it rejects IPC TIDs when DFS support is disabled, validates the copied path string, finds the request user from the virtual circuit, and resolves a nonzero base FID into a base directory. If the base FID's scache is already marked deleted, the base FID is closed and the request returns `CM_ERROR_NOSUCHPATH`.

The function computes internal `fidflags` from NT desired access, create options, and share mode. DELETE sets `SMB_FID_OPENDELETE`; read/execute sets `SMB_FID_OPENREAD_LISTDIR`; write sets `SMB_FID_OPENWRITE`; delete-on-close, sequential/random access, executable-name detection, and share-read/share-write each set their corresponding FID flags. `FILE_OPEN_REPARSE_POINT` is only logged in this range; symlink evaluation still happens later for overwrite/type checks.

Path lookup differs by create disposition. For `FILE_CREATE`, `FILE_OVERWRITE`, and `FILE_OVERWRITE_IF`, the parent path is found case-insensitively, but the final component is first looked up case-sensitively so exclusive create can distinguish case collisions. If that misses, a case-folded lookup is attempted. For other dispositions, the full path is looked up case-folded through `cm_NameI()`. DFS links short-circuit to `CM_ERROR_PATH_NOT_COVERED` or `CM_ERROR_NOSUCHPATH` depending on DFS request state and mapping notification.

If the target was not found, or if the open needs delete/write parent state, the parent directory is resolved. Directory tree creation is supported only for `FILE_CREATE` with `FILE_DIRECTORY_FILE`: the code repeatedly strips the last component from `spacep->wdata` until it finds an existing parent, records the first missing path segment in `treeStartp`, and later creates each nested directory component. The final component is validated with `smb_IsLegalFilename()` before creating or re-looking-up it.

After lookup, a new FID is allocated before the cache-manager NT open check so the FID number can participate in `cm_CheckNTOpen()`. The user is held and saved on the FID. If the target exists and this is not tree creation, `cm_CheckNTOpen()` enforces the requested access/share/create disposition. `FILE_CREATE` against an existing target returns `CM_ERROR_EXISTS`. `FILE_OVERWRITE` and `FILE_OVERWRITE_IF` truncate length to zero through `cm_SetAttr()`, following symlinks and re-running `cm_CheckNTOpen()` against the resolved target.

If the target does not exist and the disposition is `FILE_OPEN` or `FILE_OVERWRITE`, the request fails with `CM_ERROR_NOSUCHFILE`. Otherwise the function creates a file with `cm_Create()` or one or more directories with `cm_MakeDir()`. Newly-created file and directory entries send `smb_NotifyChange(FILE_ACTION_ADDED, ...)` to watched parent directories. Races where another client created the object first are tolerated for non-exclusive creates: the code case-folds a lookup of the new object and, for overwrite-if, truncates it.

After creation/opening, the function verifies requested object type. A non-directory request that resolves to a symlink follows the symlink before returning `CM_ERROR_ISDIR` for non-files. A directory request against a regular file returns `CM_ERROR_NOTDIR`. Any outstanding `cm_CheckNTOpen()` state is dropped before returning from these failure paths.

For regular files opened without `FILE_SHARE_WRITE`, the code installs a synthetic one-byte lock at the reserved `SMB_FID_QLOCK_*` offset. Read-only or share-read opens use `LOCKING_ANDX_SHARED_LOCK`; write opens without share-read use an exclusive lock. Failure becomes `CM_ERROR_SHARING_VIOLATION`.

Once all checks pass, `cm_CheckNTOpenDone()` releases the file-server lock/open state. The FID mutex is acquired, the held scache is transferred into `fidp->scp`, `CM_SCACHEFLAG_SMB_FID` is set under the scache write lock, `fidp->flags` is populated, newly-created state is recorded with `SMB_FID_CREATED`, and `SMB_FID_NTOPEN` plus parent/name fields are saved for delete-on-close and change notification when delete or write access was requested. `fidp->NTopen_wholepathp` takes ownership of `realPathp`, so the path buffer is intentionally not freed on success.

The response is formatted as the standard NT CreateX response even when the client asked for an extended response, because the comment notes Explorer shell failures with the extended form. The code returns oplock level zero, the FID, open action (`1` existing, `2` created, `3` truncated), four identical times derived from `scp->clientModTime`, attributes, allocation size/EOF from `scp->length`, no reparse/substreams/EAs device state, and a directory flag for directory/mountpoint/invalid scache types. Executable files with nonzero length and no ongoing prefetch get a background whole-file prefetch request.

### NT Transaction Create

`smb_ReceiveNTTranCreate()` repeats the CreateX logic with transaction-specific parsing. It reads the parameter block at the offset stored in SMB words 11/12, interprets it as `ULONG` fields, rejects base FIDs with high 16 bits set, and parses the path after thirteen `ULONG` values plus one setup byte. `nameLength` is treated as bytes despite a spec note about characters. Unlike `NTCreateX`, this routine uses `cm_GetSpace()` and frees it with `cm_FreeSpace()` after parent lookup is no longer needed.

It rejects directory creates combined with `FILE_SUPERSEDE`, `FILE_OVERWRITE`, or `FILE_OVERWRITE_IF`, validates the path, gets the user, resolves either the root/TID path or base FID, computes the same FID flags, then resolves the parent and target. This implementation does not include the nested `treeCreate` path from `NTCreateX`; it only creates the final directory component through `cm_MakeDir()`.

Existing targets go through `cm_CheckNTOpen()`, exclusive-create failure, symlink-aware truncate for overwrite dispositions, type validation, synthetic share-locking, FID installation, and optional executable prefetch in the same pattern as CreateX. Missing targets are created as files or directories depending on `realDirFlag`; `FILE_OPEN` and `FILE_OVERWRITE` still fail if missing. Parent/name state is saved in the FID for delete/write opens. `realPathp` is retained by `fidp->NTopen_wholepathp` on success.

The response is transaction-framed. When `EXTENDED_RESPONSE_REQUIRED` is not set, it returns a 70-byte parameter payload. When set, it returns the extended payload with response type `1`, zeroed GUID bytes because nonzero GUIDs were observed to break Cygwin, maximal access rights `0x001f01ff`, and guest access rights zero. Both branches populate FID, action, times, attributes, allocation/EOF sizes, device state, and directory flag.

### Notify Change Registration And Completion

`smb_ReceiveNTTranNotifyChange()` extracts the notify filter, FID, and watch-tree flag from SMB parameter words 19-22. It resolves the FID, rejects deleted scaches by closing the FID and returning `CM_ERROR_NOSUCHFILE`, then holds the watched scache. It copies the incoming request packet, ensures the copy references the current virtual circuit, pushes the copy onto `smb_Directory_Watches` under `smb_Dir_Watch_Lock`, marks the scache with either `CM_SCACHEFLAG_WATCHED` or `CM_SCACHEFLAG_WATCHEDSUBTREE`, releases local holds, and sets `outp->flags |= SMB_PACKETFLAG_NOSEND` so the request remains pending.

`smb_NotifyChange()` is called by create/delete/rename/write paths in SMB code and by callback-break code. It locks the global watch list, scans pending copied packets, reads each saved request's filter, FID, watch-tree flag, and maximum parameter length, and applies an NT compatibility hack: a subtree watch asking only for file-name and directory-name changes is treated as also interested in last-write and attribute changes. It then resolves the saved packet's FID in the saved packet's virtual circuit and matches only watches whose FID scache equals the changed directory scache, is not deleted, has an overlapping filter, and either watches the direct parent or requested subtree notifications.

Matching watches are one-shot. The saved packet is removed from `smb_Directory_Watches`, the corresponding watch flag is cleared on the directory scache, and the saved request packet is converted into a server-to-client NT transaction response. If a filename is known, the response includes a `FILE_NOTIFY_INFORMATION`-style parameter payload with action, UTF-16 name length, and filename. For a rename within one directory, a `FILE_ACTION_RENAMED_OLD_NAME` call with `otherFilename` produces two entries: old name followed by new name. If the client's maximum parameter buffer is too small, `parmCount` is set to zero.

When `filename == NULL`, typically for a callback break where the precise cause is unknown, the response carries no data and manually sets NT status `STATUS_NOTIFY_ENUM_DIR` using the legacy SMB error fields plus `SMB_FLAGS2_32BIT_STATUS`. The packet is then sent on its saved virtual circuit and freed.

`smb_ReceiveNTCancel()` implements cancellation for pending notify requests. It scans `smb_Directory_Watches` under the mutex for a saved packet matching the incoming UID, PID, MID, and TID. On match it removes the saved packet, releases the watch-list mutex, resolves the watch FID, clears the watched or watched-subtree flag on the scache, and completes the saved packet with NT `STATUS_CANCELLED` (`0xC0000120`) before sending and freeing it. If no match is found, cancel is a successful no-op.

### Security Descriptor Query And Dispatch

The fixed `nullSecurityDesc` is a self-relative security descriptor with owner and group SIDs set to everyone and a null DACL-present control flag. `smb_ReceiveNTTranQuerySecurityDesc()` parses the transaction parameter/data counts and offsets, extracts the FID and requested security information mask, validates the FID and deleted state, and rejects requests outside owner/group/DACL information with `CM_ERROR_BAD_LEVEL`.

The response sizing logic returns the descriptor when `maxData` can hold it, returns only the four-byte descriptor length and `CM_ERROR_BUFFERTOOSMALL` when the parameter buffer can hold that length but data cannot hold the descriptor, or returns `CM_ERROR_BUFFER_OVERFLOW` with no SMB data when even the length cannot fit. The function releases the FID before composing the descriptor response because it does not need live file metadata after validation/logging.

`smb_ReceiveNTTransact()` reads the NT transaction function from SMB word 18 and dispatches function 1 to create, 4 to notify-change, and 6 to query-security. IOCTL, set-security, NT transact rename, quota query, and quota set are logged as not implemented and return `CM_ERROR_BADOP`.

### NT Rename And User Helpers

`smb_ReceiveNTRename()` supports only `RENAME_FLAG_RENAME` and `RENAME_FLAG_HARD_LINK`. Other NT rename types, including copy and move-cluster-information, return `CM_ERROR_NOACCESS`. It parses two ASCII-block paths from SMB data, logs the operation, and delegates to existing SMB rename/link helpers. Attribute filtering is passed only to `smb_Rename()`.

`smb_FindCMUserByName()` and `smb_FindCMUserBySID()` call `smb_FindUserByName()`, lazily attach a `cm_NewUser()` to the returned username record under that record's mutex, hold the user, release the username record, and return the held `cm_user_t`. The SID variant marks `SMB_USERNAMEFLAG_SID` before installing the new user.

## State And Persistence Behavior

This chunk does not write on-disk metadata directly. Its persistence is runtime SMB server state and cache-manager state:

- Successful create/open operations allocate an SMB FID and keep it live in the virtual circuit until close. The FID owns a held `cm_scache_t`, a held `cm_user_t`, FID flag bits derived from NT access/share/create options, and path strings used later for close, delete-on-close, writes, and notifications.
- `fidp->NTopen_wholepathp` owns the `realPathp` allocation on successful CreateX/NTTranCreate. Error paths free it. `smb_CloseFID()` later frees this whole-path string.
- `fidp->NTopen_dscp` holds the parent directory scache when delete or write access requires later close-time delete/change processing. The last component is duplicated into `fidp->NTopen_pathp`. Ownership transfers from local `dscp` into the FID when `SMB_FID_NTOPEN` is set.
- `CM_SCACHEFLAG_SMB_FID` is set on opened scaches, indicating at least one SMB FID references the scache.
- `CM_SCACHEFLAG_WATCHED` and `CM_SCACHEFLAG_WATCHEDSUBTREE` are set when a notify-change request is pending and cleared when the watch is completed or cancelled. These are advisory flags for deciding whether mutation paths need to call `smb_NotifyChange()`.
- `smb_Directory_Watches` stores copied incoming SMB packets as pending response state. These packets own their copied buffers and a virtual-circuit reference. They are freed only on notification completion or cancellation.
- Synthetic share-denial locks use a reserved byte range (`SMB_FID_QLOCK_HIGH`, `SMB_FID_QLOCK_LOW`, length `SMB_FID_QLOCK_LENGTH`) and a key generated from the VC ID, fixed PID zero, and FID. This represents NT share mode in the cache-manager byte-range lock subsystem.
- File/directory creation and truncation mutate AFS/cache-manager state through `cm_Create()`, `cm_MakeDir()`, and `cm_SetAttr()`. Created objects may trigger notify-change responses before the create response returns.
- Executable open prefetch queues a background cache fetch request; this persists as asynchronous work rather than packet/FID state.

The code relies on strict reference ownership. On success, the target scache hold is deliberately transferred to `fidp->scp`; on most errors, local scache/user/FID/path references are released immediately. `cm_CheckNTOpenDone()` must pair with every successful `cm_CheckNTOpen()`, including symlink replacement and late error paths.

## Dependencies And Integration Points

This range is coupled to the rest of the Windows AFS client in several ways:

- SMB command dispatch calls `smb_ReceiveNTCreateX()`, `smb_ReceiveNTTransact()`, `smb_ReceiveNTCancel()`, and `smb_ReceiveNTRename()` from the SMB request-processing layer.
- Close-time behavior is in `smb_CloseFID()` in `smb.c`. That code consumes `NTopen_dscp`, `NTopen_pathp`, `NTopen_wholepathp`, delete-on-close flags, and notification flags established here.
- Mutation paths in `smb.c`, `smb3.c`, and `cm_ioctl.c` call `smb_NotifyChange()` after create, remove, rename, link, mount-point, and write/attribute changes. Callback-break code calls it with `filename == NULL` when the exact changed child is unknown.
- The cache manager vnode layer provides path traversal, creation, directory creation, symlink evaluation, attribute setting, NT open/share validation, byte-range locks, and background fetch scheduling.
- DFS support changes IPC/TID and DFS link behavior. With DFS support, DFS link scaches can return path-not-covered responses and IPC TIDs may be used for referral-like paths; without DFS support, regular CreateX rejects IPC TIDs.
- The packet layer's transaction framing is hand-built with SMB word offsets and byte-count alignment. The code assumes the classic `8*4 + 39` transaction response parameter offset plus one byte of padding in several handlers.
- Windows compatibility is explicit: extended CreateX responses are suppressed due to Explorer issues; transaction-create GUIDs are zeroed due to Cygwin failures; subtree notify filters are widened to emulate NT client/server behavior; query-security returns a permissive null-DACL descriptor rather than real AFS ACL data.

## Risks And Edge Cases

The largest maintainability risk is duplicated create/open logic. `smb_ReceiveNTCreateX()` and `smb_ReceiveNTTranCreate()` implement nearly the same NT semantics but differ in parsing, nested directory creation support, invalid disposition checks, space-buffer ownership, response formatting, and some error cleanup. A behavioral fix in one path can easily be missed in the other.

Reference ownership is delicate. Success transfers `scp`, `dscp`, `realPathp`, and `userp` ownership into the FID in different combinations, while error paths call `cm_CheckNTOpenDone()`, `smb_CloseFID()`, `smb_ReleaseFID()`, `cm_ReleaseSCache()`, `cm_ReleaseUser()`, `cm_FreeSpace()`, and `free(realPathp)` conditionally. Symlink overwrite paths release an open check on the symlink, replace `scp`, and run a new open check on the target; missing a paired `cm_CheckNTOpenDone()` would leak server-side lock/open state.

The CreateX tree-create path mutates `spacep->wdata` while walking backward to find an existing parent, then computes `treeStartp` as an offset into `realPathp`. This depends on `spacep->wdata` being a component-stripped copy that remains byte/character aligned with `realPathp`. Changes to `smb_StripLastComponent()` or path normalization could break nested directory creation.

The transaction-create path does not implement the same tree-create behavior as CreateX. Directory requests that require multiple missing components can succeed through `NTCreateX` but fail through `NT_TRANSACT_CREATE`. That may be intentional compatibility drift, but it is worth preserving or testing explicitly.

The notify watch list uses saved SMB request packets as list nodes. While protected by `smb_Dir_Watch_Lock`, `smb_NotifyChange()` calls `smb_SendPacket()` while still holding the mutex. If sending can block or re-enter code that needs the same lock, this is a potential latency/deadlock audit point. The code also clears `CM_SCACHEFLAG_WATCHED` or `WATCHEDSUBTREE` when one watch completes, even if multiple pending watches exist on the same scache and same watch mode; that can make mutation paths skip later notifications if they rely solely on the scache flag rather than also checking the watch list.

`smb_NotifyChange()` assumes `lastWatch` is valid when removing a non-head watch. It is assigned on every skipped iteration, so normal flow is safe, but changes to early-continue logic could break list removal. `smb_ReceiveNTCancel()` uses the same pattern.

Notify response length handling is conservative but lossy. If the client's `maxLen` cannot hold the notification payload, `parmCount` becomes zero and the response is sent without the name rather than returning a more explicit overflow status. For `filename == NULL`, the code manually writes NT status fields without changing word count or byte count, which is intentional but brittle.

`smb_ReceiveNTTranQuerySecurityDesc()` returns a fixed null-DACL descriptor for all files and directories. This is compatible with clients expecting a security descriptor shape, but it does not reflect AFS ACLs or per-object ownership. Security-sensitive UI/tests must understand that this SMB server is exposing a compatibility descriptor, not authoritative access-control state.

Several NT fields are parsed but unused or only logged: requested oplocks, batch oplocks, `mustBeDir`, allocation size, security descriptor length, EA length, impersonation level, security flags, and many create options. The returned oplock level is always zero. Clients depending on these features will see simplified semantics.

The fixed response offsets and direct casts like `*((ULONG *)outData)` assume alignment and little-endian layout consistent with the Windows build. Porting or hardening this code would need endian/alignment helpers instead of raw stores.

There is a code comment in the NT transaction create share-lock failure path asking whether `smb_CloseFID()` should be used; the current code does call `smb_CloseFID()`. That suggests this area has had cleanup ambiguity and should be regression-tested after changes to FID teardown.

## Test Signals

Useful tests and diagnostics for this chunk include:

- Create/open matrix tests for `FILE_OPEN`, `FILE_CREATE`, `FILE_OPEN_IF`, `FILE_OVERWRITE`, and `FILE_OVERWRITE_IF` against missing files, existing files, existing directories, symlinks to files, and case-only filename conflicts.
- Type option tests for `FILE_DIRECTORY_FILE` and `FILE_NON_DIRECTORY_FILE`, including regular file requested as directory, directory requested as file, symlink-to-file with non-directory create, root directory create, and nested directory tree creation through `NTCreateX`.
- Base-FID-relative open tests for valid base directories, deleted base FIDs, nonexistent base FIDs, and TID-rooted opens with and without DFS support.
- Share-mode tests that open the same file with combinations of write access, `FILE_SHARE_READ`, and `FILE_SHARE_WRITE`, verifying the reserved-byte synthetic lock yields `CM_ERROR_SHARING_VIOLATION` when expected and is released on close.
- Delete-on-close/write-open tests that verify `SMB_FID_NTOPEN`, `NTopen_dscp`, and `NTopen_pathp` are saved and later consumed by `smb_CloseFID()` for delete and change notification.
- Response-format tests for standard `NTCreateX`, non-extended `NT_TRANSACT_CREATE`, and extended `NT_TRANSACT_CREATE`, checking FID, action, times, attributes, size fields, directory flag, device state, zero oplock, zero GUID, and maximal-access fields.
- Notify-change tests that register watches, perform file create/delete/rename/write operations in the watched directory, verify one-shot completion, verify two-entry same-directory rename payloads, verify callback-break `STATUS_NOTIFY_ENUM_DIR`, and verify cancellation returns NT `STATUS_CANCELLED`.
- Multi-watch tests on the same directory and subtree flag to detect whether clearing scache watch flags after one completion suppresses later pending notifications.
- Query-security tests for owner/group/DACL masks, unsupported SACL or other masks, small `maxData`, small `maxParm`, deleted FID, and unknown FID. Expected outputs are the fixed descriptor, `CM_ERROR_BUFFERTOOSMALL`, `CM_ERROR_BUFFER_OVERFLOW`, `CM_ERROR_BAD_LEVEL`, `CM_ERROR_NOSUCHFILE`, and `CM_ERROR_BADFD`.
- Error-path leak tests using fault injection around `cm_CheckNTOpen()`, `cm_SetAttr()`, `cm_Create()`, `cm_MakeDir()`, `cm_Lock()`, and `cm_EvaluateSymLink()` to ensure FID, user, scache, path, and NT-open lock state are released exactly once.
- Operational log signals include `NTCreateX rejecting invalid name`, `NTTranCreate rejecting invalid readDirFlag and createDisp combination`, `Unknown SMB Fid`, `Sending Change Notification`, `SMB NT Transact ... not implemented`, `SMB NT CreateX opening fid`, `SMB NTTranCreate opening fid`, and `NTCancel unable to resolve fid`.
