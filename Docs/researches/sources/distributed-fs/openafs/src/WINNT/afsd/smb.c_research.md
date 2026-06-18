# Research: sources/distributed-fs/openafs/src/WINNT/afsd/smb.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007709`: lines 1-8404, `Docs/researches/chunks/subset-b-007709_research.md`
- `subset-b-007710`: lines 8405-11705, `Docs/researches/chunks/subset-b-007710_research.md`

## Chunk Research

### subset-b-007709: lines 1-8404

# sources/distributed-fs/openafs/src/WINNT/afsd/smb.c lines 1-8404

## Chunk Scope

This chunk covers the first 8,404 lines of the Windows OpenAFS SMB server implementation. It starts with global SMB/NetBIOS state, protocol utility routines, object lifetime management, packet parsing/formatting, error mapping, negotiation, daemon helpers, directory search, and the core SMB commands through the beginning of `smb_ReceiveCoreCreate`. The chunk boundary cuts inside `smb_ReceiveCoreCreate`: line 8404 has just set `created = 1` after a successful `cm_Create`; create notification and final FID response setup continue in the following chunk.

## Purpose

This portion of `smb.c` implements the SMB1-facing server layer that exposes the AFS cache manager as a Windows SMB share. It translates NetBIOS/SMB packet fields into cache-manager operations, manages per-client session state, maps AFS/cache errors to SMB/Win32/NT status codes, and handles core SMB commands such as negotiate, tree connect, search, open, create, delete, rename, read, write, raw read/write, close, flush, mkdir, rmdir, and attribute queries.

The code is not a standalone filesystem. It is the protocol adapter between Windows SMB clients and the OpenAFS Windows cache manager (`cm_*`, `buf_*`, `rx`, LSA/auth, DFS notification, RPC/ioctl helpers). Most command handlers follow the same shape: parse SMB parameters and variable data, resolve the authenticated user and tree path, translate an SMB path to an AFS cache object, perform cache-manager locking/synchronization, marshal SMB response parameters, and release all held references.

## Important State And Types

- Global protocol/service state includes `smbShutdownFlag`, `smb_ListenerState`, `smb_useV3`, `smb_UseUnicode`, `smb_authType`, `smb_maxMpxRequests`, `smb_maxVCPerServer`, `smb_NumServerThreads`, `smb_LANadapter`, `smb_sharename`, and `sessionGen`.
- Locks are split by responsibility: `smb_globalLock` protects packet/free-list and directory-search global structures; `smb_rctLock` protects reference-counted VC/TID/UID/FID/user-name lists; `smb_ListenerLock`/`smb_StartedLock` are declared for listener startup paths outside this chunk; per-object mutexes protect object-local fields.
- `smb_vc_t` virtual circuits track NetBIOS LSN/lana/session, negotiated dialect flags, encryption challenge, user/TID/FID lists, dead/already-dead state, and a reference count. Creation happens in `smb_FindVC`; teardown happens in `smb_CleanupDeadVC` and `smb_ReleaseVCInternal`.
- `smb_tid_t` tree IDs store share pathname, IPC flag, user pointer, and VC back-reference. They are created by tree connect and deleted by tree disconnect/dead-VC cleanup.
- `smb_user_t` and `smb_username_t` bridge SMB UIDs/session users to `cm_user_t` cache-manager users. `smb_username_t` entries are globally cached by user+machine and garbage-collected after logoff timeout rules.
- `smb_fid_t` file IDs hold an open `cm_scache_t`, user, open mode flags, raw-write event, ioctl/RPC state, NT-open metadata, delete-on-close metadata, and reference count.
- `smb_dirSearch_t` stores legacy `SMB_COM_SEARCH` continuation state: cookie, directory scache, masks, attributes, last offset, saved TID/relative paths, LRU links, and delete/refcount state.
- `smb_packet_t` wraps raw SMB packet bytes plus parsed word-count pointer, held VC, temporary string-space list, NCB pointer, chained-FID state, suspended/resume fields, and flags.
- `raw_write_cont_t` stores the second phase of `SMB_COM_WRITE_RAW`: result code, file offset, total count, raw buffer, write mode, and bytes already written.

## Core APIs And Functions

### Initialization And Basic Helpers

- `smb_InitReq` initializes `cm_req_t` and marks the request as SMB-originated with `CM_REQ_SOURCE_SMB`.
- `ncb_error_string` maps NetBIOS return codes to diagnostic strings used by send failure logging.
- `myCrt_Dispatch`, `myCrt_2Dispatch`, `myCrt_RapDispatch`, and `myCrt_NmpipeDispatch` provide symbolic names for SMB, transaction2, RAP, and named-pipe opcodes for tracing/debug UI.
- `smb_Attributes` maps `cm_scache_t` metadata to SMB attributes: directory/system/sparse-file/read-only decisions are based on AFS file type and Unix mode bits.
- `smb_SetInitialModeBitsForFile` and `smb_SetInitialModeBitsForDir` seed cache-manager create attributes from configured Unix mode defaults and SMB read-only attributes.
- `smb_IsDotFile`, `smb_IsLegalFilename`, `smb_Get8Dot3MaskFromPath`, `smb_Match8Dot3Mask`, and `smb_FindMask` implement Windows filename/mask behavior around dotfiles, illegal characters, 8.3 names, and wildcard matching.

### Time Handling

- `ExtractBits` and `ShowUnixTime` help trace DOS time/date conversions.
- `GetTimeZoneInfo` and `CompensateForSmbClientLastWriteTimeBugs` compensate for historical SMB client last-write-time DST and positive-offset timezone bugs.
- `smb_DosUTimeFromUnixTime` and `smb_UnixTimeFromDosUTime` translate between Unix `time_t` and SMB DOS-relative time using `smb_localZero`, which `smb_Daemon` periodically recomputes.

### Reference-Counted Session Objects

- `smb_MarkAllVCsDead` marks all VCs except an optional excluded one as dead and invokes cleanup outside the global list walk.
- `smb_FindVC` finds or creates a VC keyed by LSN/lana. On create it assigns VC/session IDs, initializes mutex/FID counters, stores NetBIOS session details, and obtains an NTLM challenge from LSA when needed.
- `smb_ReleaseVCInternal`, `smb_ReleaseVCNoLock`, `smb_ReleaseVC`, `smb_HoldVCNoLock`, and `smb_HoldVC` implement VC lifetime. A dead VC moves from `smb_allVCsp` to `smb_deadVCsp` and is freed only when its refcount reaches zero.
- `smb_CleanupDeadVC` removes a dead VC from the live list and closes/deletes all FIDs, TIDs, and UIDs it owns. It has explicit protection against reentrant cleanup via `SMB_VCFLAG_CLEAN_IN_PROGRESS`.
- `smb_FindTID`, `smb_HoldTIDNoLock`, and `smb_ReleaseTID` manage tree IDs and release associated `cm_user_t` and VC references on final deletion.
- `smb_FindUID`, `smb_ReleaseUID`, `smb_GetUserFromUID`, and `smb_GetUserFromVCP` manage per-VC SMB users and return held `cm_user_t` references for request execution.
- `smb_FindUserByName`, `smb_FindUserByNameThisSession`, `smb_ReleaseUsername`, and `smb_userIsLocalSystem` manage the global user-name cache and SID/local-system recognition.
- `smb_FindFID`, `smb_FindFIDByScache`, `smb_HoldFIDNoLock`, and `smb_ReleaseFID` manage open file IDs. `smb_ReleaseFID` is careful to drop scache/user references after releasing SMB locks and also cleans ioctl/RPC state.

### Share And Tree Resolution

- `smb_FindShare` resolves a share name to an AFS path. It handles the synthetic `all` share, `ioctl$`, volume-reference share names containing `%` or `#`, registry submounts under the OpenAFS Submounts key, variable substitution for `%USERNAME%`/`%COMPUTERNAME%`, root.afs partial matching, and cell-name fallback.
- `smb_FindShareProc` is the directory callback used to locate a share-like entry in `root.afs`, preferring exact matches but retaining partial matches for old RAP share-name truncation behavior.
- `smb_FindShareCSCPolicy` reads per-share Windows client-side caching policy from the registry.
- `smb_LookupTIDPath` obtains the path associated with an SMB TID and reports IPC TIDs as a special cache-manager error.

### Directory Search State

- `smb_FindDirSearchNoLock`, `smb_FindDirSearch`, `smb_NewDirSearch`, `smb_DeleteDirSearch`, `smb_ReleaseDirSearchNoLock`, `smb_ReleaseDirSearch`, and `smb_GCDirSearches` implement stateful legacy `SMB_COM_SEARCH` cookies with LRU ordering and protocol-specific cookie widths.
- Directory searches hold scache references and can mark bulk-stat progress on an scache. Deletion clears `CM_SCACHEFLAG_BULKSTATTING` and resets `bulkStatProgress`.

### Packet And String Marshalling

- `smb_GetPacket`, `smb_CopyPacket`, `smb_FreePacket`, `smb_GetNCB`, and `smb_FreeNCB` maintain packet/NCB free lists. Packets may hold a VC reference and a list of temporary decoded string buffers.
- `smb_GetSMBData`, `smb_SetSMBDataLength`, `smb_GetSMBParm*`, and `smb_SetSMBParm*` read/write SMB word parameters and byte counts. Out-of-range parameter reads log and panic.
- `smb_StripLastComponent` splits a path into parent and last component and special-cases `::$DATA` stream syntax so normal data stream opens are treated as the underlying file.
- `smb_ParseASCIIBlock`, `smb_ParseString`, `smb_ParseStringCb`, `smb_ParseStringCch`, `smb_ParseStringBuf`, and `smb_UnparseString` convert SMB byte strings to/from `clientchar_t`, honoring negotiated Unicode unless forced ASCII. Temporary strings are attached to packet-owned `cm_space_t`.
- `smb_ParseVblBlock` and `smb_ParseDataBlock` parse SMB variable/data blocks.
- `smb_FormatResponsePacket` initializes SMB response headers from a request, including flags, TID/PID/UID/MID echoing, NT long-name support, and Unicode flags.
- `smb_SendPacket` computes the response length, sends via NetBIOS `NCBSEND`, and marks/cleans a VC dead on send failure.

### Error Mapping

- `smb_MapNTError`, `smb_MapWin32Error`, and `smb_MapCoreError` translate OpenAFS/cache-manager/RX errors into NTSTATUS, Win32, or core SMB class/error pairs. The mappings encode Windows-client workarounds for timeout/retry handling, quotas, path-not-covered DFS behavior, Kerberos/auth errors, lock conflicts, buffer overflow, and unsupported operations.

## Command Control Flow In This Chunk

### Negotiation And Keepalive

- `smb_ReceiveNegotiate` parses client dialect strings, chooses NT LM 0.12, LM1.2X002, or core based on `smb_useV3`, sets VC dialect flags, and builds the dialect-specific response. NT negotiation advertises NT status, large files, NT find/SMBs, raw mode, optional DFS, optional Unicode, and optional extended security. NTLM responses include an LSA challenge and faux domain; extended-security responses include the server GUID and intentionally omit an initial security blob to work around Windows 7/Server 2008 R2 SMB1 behavior.
- `smb_CheckVCs` walks live VCs, sends SMB echo packets as keepalives, and skips already-dead VCs while maintaining references across dropped locks.
- `smb_Daemon` periodically recomputes `smb_localZero`, notifies freelance mount point changes when the local zero changes, runs VC checks, and garbage-collects logged-off global usernames after timeout.

### Waiting Locks

- `smb_WaitingLocksDaemon` monitors `smb_allWaitingLocks`, retries queued cache-manager locks with `cm_RetryLock`, handles timeout/cancel/error states, undoes partially granted locks on failure, removes completed requests from the global queue, and resumes packet processing through `smb_DispatchPacket` with `SMB_PACKETFLAG_SUSPENDED`.

### Tree And Disk Commands

- `smb_ReceiveCoreGetDiskAttributes` returns fixed legacy disk geometry/free-space values.
- `smb_ReceiveCoreTreeConnect` parses a UNC path, extracts the share name, allocates a new TID, resolves the share through `smb_FindShare`, associates the TID with a user/path, and returns the new TID and packet size.
- `smb_ReceiveCoreTreeDisconnect` marks the TID delete-ok and releases it.

### Directory Search

- `smb_ReceiveCoreSearchVolume` handles volume-label searches by returning a synthetic `AFS` volume label in the old 43-byte search result format.
- `smb_ApplyDirListPatches` is the second pass for search results. It bulk-stats directory entries when possible, falls back to individual status fetches if bulk stat fails, then patches attribute/time/size placeholders in the response. If the user lacks ACL visibility it fabricates conservative directory/file attributes and a sentinel date/size.
- `smb_ReceiveCoreSearchDir` implements legacy directory enumeration. It parses mask/status blocks, creates or resumes a `smb_dirSearch_t`, reads AFS directory buffers page by page, applies 8.3 mask matching and hidden-dotfile filtering, emits 43-byte search records, tracks continuation cookies, and runs patching to fill real metadata after it is safe to drop directory locks.

### Path And Attribute Commands

- `smb_ReceiveCoreCheckPath` resolves a path under the TID share, follows mount points, handles DFS links, fetches status, and returns success only if the target has directory attributes.
- `smb_ReceiveCoreSetFileAttributes` resolves a file, fetches status, rejects read-only volumes, converts DOS time to Unix time, toggles Unix write bits for SMB read-only changes, and calls `cm_SetAttr`.
- `smb_ReceiveCoreGetFileAttributes` resolves a file, includes a special `desktop.ini` avoidance path to reduce Explorer-triggered AFS root/mount lookups, handles DFS links, fetches status, and marshals SMB attributes, DOS mod time, and low 32-bit length.

### Open/Create/Delete/Rename/Link/Directory Mutation

- `smb_ReceiveCoreOpen` validates client string paths, special-cases the magic ioctl filename by creating an ioctl FID, resolves the target, checks sharing/open permissions, rejects non-files, allocates a new FID, records open mode/user/scache, marks `CM_SCACHEFLAG_SMB_FID`, returns FID/attributes/time/length, and calls `cm_Open`.
- `smb_UnlinkProc` and `smb_ReceiveCoreUnlink` implement delete with wildcard, case-fold, and generated 8.3 matching. Matching entries are collected first, then each original FS name is passed to `cm_Unlink`; delete notifications are emitted for watched directories.
- `smb_RenameProc` and `smb_Rename` implement old/new path resolution, same/different directory rename, case-sensitive then case-insensitive match fallback, target existence checks, DFS handling, `cm_Rename`, and change notifications for same-dir and cross-dir renames. `smb_ReceiveCoreRename` parses the two path blocks, validates the new path, and delegates to `smb_Rename`.
- `smb_Link` creates a hard link only within the same directory after resolving old/new directories, ensuring the source exists and target either does not exist or is already the same object. It calls `cm_Link` and emits add notifications.
- `smb_RmdirProc` and `smb_ReceiveCoreRemoveDir` remove directories with case-sensitive then case-insensitive matching and optional 8.3 tilde matching. It collects matching original FS names and calls `cm_RemoveDir`, emitting watched-directory notifications.
- `smb_ReceiveCoreMakeDir` resolves the parent, rejects root creation, checks target nonexistence, applies default directory mode bits and current mod time, calls `cm_MakeDir`, and emits add notifications.
- `smb_ReceiveCoreCreate` begins handling `SMB_COM_CREATE` and `SMB_COM_CREATE_NEW`: it parses attributes/time/path, validates the path and leaf filename, resolves the parent, rejects DFS links, looks up the target, either truncates an existing file for nonexclusive create or calls `cm_Create` with initial mode/time attributes. This chunk ends immediately after marking a successful create with `created = 1`; notification and FID creation/response happen after line 8404.

### Close, Flush, Read, And Write

- `smb_ReceiveCoreFlush` validates the FID and scache, ignores ioctl FIDs, closes deleted scaches, and calls `cm_FSync` for write-open FIDs when async store mode requires it.
- `smb_FullNameProc` and `smb_FullName` recover the full client/original FS name for delete-on-close, including 8.3 short-name resolution.
- `smb_CloseFID` is the core close path. It prevents double close with `deleteOk`, waits for asynchronous raw writers, optionally applies client mod time with SMB-client bug compensation, fsyncs write opens, unlocks all byte-range locks for the FID, performs delete-on-close for files/directories with notifications, clears creator state, releases NT-open metadata, clears `CM_SCACHEFLAG_SMB_FID`, and drops scache/path/user references.
- `smb_ReceiveCoreClose` parses FID and DOS time, resolves chained FIDs, gets the request user, delegates to `smb_CloseFID`, and releases references.
- `smb_ReadData` is shared by core read, ReadAndX, and raw read. It verifies read-open flags, holds the scache, fetches current length, clamps reads at EOF, loads cache buffers with `buf_Get`/`cm_GetBuffer`, copies bytes into the SMB output/raw buffer, and triggers prefetch for sequential access.
- `smb_WriteData` is shared by core write and raw write. It verifies write-open flags, fetches status with set/get status sync flags, extends scache length when needed, writes into cache buffers under buffer/scache locks, marks buffers dirty, handles quota/space flags, emits modify notifications for NT-open FIDs, optionally queues background stores by `smb_AsyncStore` window, or synchronously calls `cm_BufWrite`.
- `smb_ReceiveCoreRead` handles ioctl/RPC FID redirects, deleted scaches, byte-range lock checks, response data-block layout, and `smb_ReadData`.
- `smb_ReceiveCoreReadRaw` handles raw reads by checking optional 64-bit offsets, FID validity, byte-range locks, raw buffer availability, ioctl raw reads, and then sending the raw data directly through NetBIOS.
- `smb_ReceiveCoreWrite` handles ioctl/RPC FID redirects, deleted scaches, byte-range lock checks, zero-byte write truncation, mod-time updates unless an mtime operation already happened, repeated `smb_WriteData` calls until the request is consumed, and core write response fields.
- `smb_ReceiveCoreWriteRaw` writes any data included in the first packet, allocates a raw buffer for the remaining data, increments `raw_writers` for asynchronous raw writes to block premature close, and returns continuation state in `raw_write_cont_t`.
- `smb_CompleteWriteRaw` completes the raw second phase, writes from the raw buffer through `smb_WriteData`, sends `SMB_COM_WRITE_COMPLETE` for synchronous raw writes, decrements `raw_writers`/signals the raw write event for asynchronous writes, and returns the raw buffer to the free list.

## Dependencies And Integration Points

- Windows APIs: NetBIOS `NCB`/`Netbios`, events/handles, `GetTimeZoneInformation`, `SystemTimeToTzSpecificLocalTime`, `LookupAccountNameW`, `ConvertSidToStringSidW`, registry APIs, `StringCch*`, LSA authentication package calls, and Windows error/status constants.
- OpenAFS cache manager: `cm_NameI`, `cm_Lookup`, `cm_GetSCache`, `cm_RootSCachep`, `cm_SyncOp`, `cm_SyncOpDone`, `cm_GetBuffer`, `cm_SetAttr`, `cm_Create`, `cm_MakeDir`, `cm_RemoveDir`, `cm_Unlink`, `cm_Rename`, `cm_Link`, `cm_CheckOpen`, `cm_Open`, `cm_FSync`, `cm_BufWrite`, `cm_QueueBKGRequest`, `cm_TryBulkStatRPC`, `cm_FindACLCache`, `cm_FindFileType`, `cm_ApplyDir`, `cm_MatchMask`, string conversion helpers, user/scache hold/release helpers, lock-range checks/unlocks, and change notification hooks.
- Buffer package: `buf_Get`, `buf_Find`, `buf_Release`, `buf_SetDirty`.
- SMB adjunct modules: ioctl handling (`smb_SetupIoctlFid`, `smb_IoctlRead`, `smb_IoctlWrite`, `smb_IoctlReadRaw`), RPC handling (`smb_RPCRead`, `smb_RPCWrite`, `smb_CleanupRPCFid`), MSRPC service detection, DFS mapping notifications, and later dispatch/listener code outside this chunk.
- Registry integration controls submount resolution, `AllSubmount`, per-share CSC policy, and other service parameters.

## State And Persistence Behavior

- Session, tree, user, FID, directory-search, raw-buffer, packet, and NCB state live in process memory and are protected by SMB locks. They are not persisted across service restarts.
- Share/submount and client-side caching configuration are persistent Windows registry state.
- Open file state persists indirectly through cache-manager scaches, dirty buffers, background store queue entries, byte-range locks, and `CM_SCACHEFLAG_SMB_FID`.
- Write persistence depends on `smb_AsyncStore`: mode `0` writes buffers synchronously in `smb_WriteData`; mode `1` queues background stores per configured window; mode `2` suppresses some fsync behavior on close/flush.
- Close semantics are important for persistence: `smb_CloseFID` can set client mod time, flush dirty data, release locks, perform delete-on-close, clear creator state, and release the scache held by the FID.
- Directory search state is ephemeral but can affect scache bulk-stat flags; deletion clears bulk-stat state to avoid leaving a directory marked as in-progress.

## Risks And Edge Cases

- Lock ordering is delicate. Several paths intentionally drop `smb_rctLock`, `smb_globalLock`, scache locks, or FID mutexes before calling cache-manager operations. Regressions can deadlock or allow use-after-free.
- Many functions rely on manual reference counting. Error paths must release `cm_user_t`, `cm_scache_t`, FID/TID/UID/VC references, `cm_space_t`, raw buffers, and registry/string allocations exactly once.
- Some SMB parameter helpers panic on malformed packet parameter indexes. That is suitable for internal invariant violations but dangerous if a parser caller miscomputes bounds from client-controlled packets.
- Unicode/ANSI parsing must preserve alignment and packet bounds. Incorrect `chainpp`/length handling can corrupt subsequent variable-block parsing.
- Path handling mixes client strings, normalized strings, FS strings, generated 8.3 names, and special stream handling (`::$DATA`). Bugs here can create mismatched notification names or wrong object operations.
- The legacy `desktop.ini` hack intentionally hides some lookups to avoid expensive Explorer behavior; it can mask real files in narrow cases if cache state heuristics are wrong.
- Error mapping has client-specific behavior for timeouts/retries, quota, DFS, and symlinks. Seemingly cleaner mappings can cause Windows redirector disconnects or wrong UI behavior.
- Raw I/O depends on raw-buffer availability and `raw_writers` event accounting. Missed decrement/signaling can make close wait indefinitely; premature close can race outstanding raw writes.
- `smb_ReceiveCoreWriteRaw` computes continuation fields around `count`/`totalCount`; cross-checking with the later dispatch code is needed to verify second-phase byte counts.
- `smb_ReceiveCoreCreate` returns `CM_ERROR_BADNTFILENAME` for illegal leaf names after `dscp` is held in this chunk's visible code; the later cleanup path is outside the boundary, so merge review should inspect whether that early return leaks `dscp`/`userp`.
- This chunk ends mid-function, so whole-function reasoning for `smb_ReceiveCoreCreate` requires the next chunk.

## Test Signals

- SMB negotiate tests should cover core, LM1.2, NT LM 0.12, SMB2 dialect offered by clients, NTLM vs extended-security vs no-auth modes, Unicode on/off, DFS capability, and Windows 7 extended-security no-initial-blob behavior.
- Tree connect tests should cover `all`, disabled `AllSubmount`, `ioctl$`, registry submounts with `%USERNAME%`/`%COMPUTERNAME%`, volume-reference shares, root.afs exact/partial matching, and bad shares.
- Lifetime tests should exercise dead-VC cleanup with open FIDs/TIDs/UIDs, send failure cleanup, tree disconnect, UID/user-name logoff GC, and FID release after ioctl/RPC state allocation.
- Directory search tests should cover first search and resume cookies, 8.3 masks, `>` wildcard, hidden dotfile filtering, volume label search, long names with generated short names, bulk-stat success/failure fallback, and no-files responses.
- Attribute/path tests should cover DFS link responses, mountpoint/follow behavior, read-only volume rejection, readonly bit to Unix mode translation, desktop.ini avoidance, and DOS/Unix time conversion including DST compensation.
- File operation tests should cover open share modes, ioctl magic file opens, invalid Unicode/client strings, illegal Windows characters, exclusive/nonexclusive create, truncation, mkdir root rejection, delete/rename/rmdir wildcard and case-fold fallback, same-file hardlink idempotence, watched-directory notifications, and delete-on-close.
- I/O tests should cover lock conflicts on read/write/raw read/raw write, EOF-clamped reads, zero-byte write truncation, quota/out-of-space flags, async-store window crossing, sequential read prefetch, raw buffer exhaustion fallback, synchronous and asynchronous raw write completion, close waiting for raw writers, and flush behavior under all `smb_AsyncStore` modes.

### subset-b-007710: lines 8405-11705

# sources/distributed-fs/openafs/src/WINNT/afsd/smb.c lines 8405-11705

## Scope And Purpose

This chunk covers the late SMB1 server core in the Windows OpenAFS client daemon. It starts inside the tail of `smb_ReceiveCoreCreate()`, then includes `SMB_COM_SEEK`, the central SMB packet dispatcher, NetBIOS receive/listen worker threads, request timeout monitoring, listener restart logic, NetBIOS adapter initialization, SMB server initialization and shutdown, share-name construction, packet diagnostics, VC/FID/TID/user dump support, and a network-started query.

The code is the glue between SMB protocol packets and the OpenAFS cache manager (`cm_*`) on one side, and Windows NetBIOS, LSA authentication, registry, event, thread, and crash-dump facilities on the other. It owns the runtime server loop: creating NetBIOS names, accepting sessions, posting one receive per live session, waking server worker threads, dispatching SMB opcodes, handling raw-write serialization, and tearing down all sessions during shutdown.

The range also defines operational diagnostics. Long requests can enable tracing and trigger a minidump through `smb_ServerMonitor()`, `smb_DispatchPacket()` logs very slow SMB requests with user/tree/path/FID context, `smb_LogPacket()` can dump raw packet bytes when built with `LOG_PACKET`, and `smb_DumpVCP()` emits the live SMB identity/session/open-file/waiting-lock graph.

## Important APIs, Types, And Functions

Important SMB/cache-manager types in this range:

- `smb_vc_t`: virtual circuit/session state keyed by NetBIOS LSN and LANA. This range sets `session`, `rname`, remote-connection flags, error counters, and dead-session state.
- `smb_packet_t` and `smb_t`: SMB packet wrapper and on-wire SMB header. The dispatcher reads `com`, `tid`, `uid`, `pid`, `mid`, parameter words, byte counts, and chained `AndX` offsets through this structure.
- `smb_dispatch_t`: dispatch-table entry containing a request handler and flags such as `SMB_DISPATCHFLAG_CHAINED` and `SMB_DISPATCHFLAG_NORESPONSE`.
- `smb_fid_t`, `smb_tid_t`, `smb_user_t`, `smb_username_t`: per-VC open files, tree connects, SMB users, and username records dumped and partly released during shutdown.
- `cm_scache_t`, `cm_user_t`, `cm_req_t`: cache-manager vnode, authenticated user, and request context used by create/seek and shutdown reference release.
- `NCB`: Windows NetBIOS control block used for `NCBLISTEN`, `NCBRECV`, `NCBHANGUP`, `NCBADDNAME`, `NCBDELNAME`, `NCBRESET`, and `NCBENUM`.
- `monitored_task`: queue node used by the request monitor to remember server-thread task IDs, start times, and whether trace/dump timers have fired.
- `raw_write_cont_t`: continuation object used to serialize `SMB_COM_WRITE_RAW` so the raw data receive completes before a new session receive is posted.

Key functions in this range:

- `smb_ReceiveCoreCreate()` tail: on successful create/truncate, allocates an SMB FID, marks it read/write, attaches `scp` and `userp`, sets `CM_SCACHEFLAG_SMB_FID`, calls `cm_Open()`, and returns the FID to the client.
- `smb_ReceiveCoreSeek()`: validates an SMB FID, rejects IOCTL/deleted FIDs, obtains current file status, updates `fidp->offset` based on start/current/end whence, and returns the low 32 bits of the offset.
- `smb_DispatchPacket()`: central SMB opcode dispatch and chained-request executor. It formats responses, invokes handlers, maps OpenAFS errors to NT or core SMB status, advances `AndX` chains, and sends the response unless the handler is marked no-response or explicitly suppresses sending.
- `smb_ClientWaiter()`: waits on NetBIOS completion events and fans them into server-thread return events because NCB events are manual-reset.
- `smb_ServerWaiter()`: pairs live sessions with available NCB slots and posts exactly one asynchronous `NCBRECV` per live session.
- `smb_Server()`: worker-thread loop that consumes completed receives, finds the VC, handles NetBIOS errors/session death, dispatches SMB packets, serializes raw writes, notifies the monitor, and recycles NCB slots.
- `smb_ServerMonitor()`, `smb_NotifyRequestEvent()`, `smb_ShutdownMonitor()`: optional request timeout monitor. It tracks in-flight server-thread tasks, enables tracing at 60 seconds, and generates at most one minidump per 10 minutes after 120 seconds.
- `InitNCBslot()`: allocates an NCB slot, availability/completion events, shared return events for all worker threads, and a packet buffer with scratch space.
- `smb_Listener()`: blocking NetBIOS listen loop per LANA. It accepts sessions, creates/reuses VCs, allocates session/NCB slots, detects local vs remote callers, handles listener failures, and wakes the server waiter.
- `smb_configureBackConnectionHostNames()`: updates Windows LSA registry values so loopback SMB authentication to the OpenAFS NetBIOS name works, and manages the temporary `DisableLoopbackCheck` workaround marker under the OpenAFS client key.
- `smb_configureExtendedSMBSessionTimeouts()`: updates LanmanWorkstation registry values for `ReconnectableServers`, `ServersWithExtendedSessTimeout`, and `ExtendedSessTimeout` when supported by the Microsoft redirector.
- `smb_SetLanAdapterChangeDetected()`, `smb_LanAdapterChange()`: schedule and process adapter/name/gateway/LANA-list changes, stopping and restarting listeners when needed.
- `smb_NetbiosInit()`: obtains the OpenAFS NetBIOS name and gateway/LANA selection, resets adapters, registers the NetBIOS name, records invalid LANAs, and sets listener/network state.
- `smb_StartListeners()`, `smb_RestartListeners()`, `smb_StopListener()`, `smb_StopListeners()`: manage listener state, registry integration, volume-network status callbacks, listener threads, name unregistration, and adapter reset.
- `smb_Init()`: initializes locks, raw buffers, free lists, NetBIOS, event arrays, dispatch tables, transaction/RAP dispatch tables, SMB3 support, LSA authentication, server-domain name, listener/waiter/server/daemon threads, and optional monitor thread.
- `smb_Shutdown()`: marks shutdown, hangs up sessions, wakes worker/waiter/listener paths, waits for worker shutdown, deletes NetBIOS names, releases VC-held FID scache references and TID users/VC refs, and shuts down the monitor.
- `smb_GetSharename()`: returns an allocated UNC string of the form `\\<server>\ALL`.
- `smb_LogPacket()`: optional hex/ascii packet dump under `LOG_PACKET`.
- `smb_DumpVCP()`: dumps usernames, cell tickets, waiting locks, live VCs, dead VCs, users, TIDs, and FIDs to a Windows file handle.
- `smb_IsNetworkStarted()`: returns whether listeners are started and shutdown has not begun.

## Control Flow

The visible create path first resolves the result of create/truncate work from the previous chunk. If a non-exclusive create raced with an existing file, it falls back to lookup and zero-length `cm_SetAttr()`. It releases the parent scache, verifies the target is a file, creates a new SMB FID, holds the user, sets open-read/listdir and open-write flags, optionally records `SMB_FID_CREATED`, stores the target scache/user in the FID, marks the scache as having an SMB FID, returns the FID number in parameter word zero, opens the cache-manager object, releases transient refs, and deliberately leaves the scache held through `fidp->scp`.

`smb_ReceiveCoreSeek()` is a small stateful request. It resolves chained FID substitution, finds and validates the FID, closes the FID and returns `CM_ERROR_NOSUCHFILE` if the scache was deleted, then uses the VC/request user for a `cm_SyncOp()` requiring callback and status. The new offset is computed from the FID's current offset, the scache EOF, or zero depending on `whence`. The result is stored back in `fidp->offset` and returned as two 16-bit SMB parameter words. The function releases the FID, scache, and user on all normal exits after the cache-manager status step.

`smb_DispatchPacket()` is the primary protocol multiplexer. For a fresh packet, it seeds `inp->inCom`, `inp->wctp`, `inp->inCount`, and `inp->ncb_length`, rejects packets shorter than the SMB variable-data offset, increments `ongoingOps`, and formats the response header. Each loop iteration indexes `smb_dispatchTable[inp->inCom]`, initializes default output words for chained or non-chained replies, honors no-response handlers, and calls either the normal dispatch procedure or `smb_ReceiveCoreWriteRaw()` for opcode `0x1d`. It logs handler duration and, for requests over 45 seconds except Tran2, records user, TID path, opened path or request path, and AFS fid. If the request straddled `sessionGen`, it logs a session-startup warning. Bad opcodes map to `CM_ERROR_BADOP`, malformed SMBs are converted from `CM_ERROR_BADSMB` to `CM_ERROR_INVAL`, and `SMB_PACKETFLAG_NOSEND` exits without sending.

Error mapping in `smb_DispatchPacket()` depends on `SMB_VCFLAG_STATUS32`. NT-status VCs use `smb_MapNTError()` and set `SMB_FLAGS2_32BIT_STATUS`; legacy VCs use `smb_MapCoreError()`. Most errors clear the response word count and byte count, but partial writes, buffer-too-small, and in-progress GSS authentication preserve handler-provided payload where required. Successful chained requests advance by reading `AndXCommand` and `AndXOffset` from the prior input word area, then patching the prior response's `AndXOffset` to the next output record.

The NetBIOS receive architecture is split across three roles. `smb_Listener()` accepts sessions with blocking `NCBLISTEN`. `smb_ServerWaiter()` waits for a live session event, waits for an available NCB slot, links the slot to the session, and posts an asynchronous `NCBRECV`. `smb_ClientWaiter()` waits for the NetBIOS completion event and signals the shared `NCBreturns[0][idx]` event, which wakes any server worker because every worker's `NCBreturns[i][idx]` points at the same event handle for that slot.

`smb_Server()` is the worker consumer. It waits for any NCB return event, exits when slot zero is signaled during shutdown, validates the slot index, checks `ncb_retcode`, finds the VC for successful and some partial receives, and handles session-close errors by marking the VC already dead, marking `dead_sessions[session]`, and calling `smb_CleanupDeadVC()`. Repeated unusual receive errors increment `vcp->errorCount`; after more than three errors the session is closed, otherwise the worker sleeps briefly and reposts the session event. Successful packets set request start time, optionally enqueue a monitor start event, and dispatch under a structured exception wrapper when tracing support is enabled. Raw writes delay the session event until the second raw-data receive completes or times out; NT Transact is also serialized by dispatching before reposting the session event; other requests repost the session before dispatch. The NCB slot is returned to `NCBavails` afterward.

`smb_ServerMonitor()` is event-driven around a sorted in-progress queue. Start/end notifications are pushed to `smb_monitored_tasks` under `_monitor_mx` and wake `h_monitored_task_queue`. The monitor thread slurps queued notifications, inserts start records sorted by `start_time`, removes matching records on end notifications, purges old or dumped records, and sets a waitable timer for the head task's next trace or dump threshold. When the timer fires, the first event enables AFS/rx debug logging; the second can call `GenerateMiniDump(NULL)` if the global dump cooldown has elapsed.

Listener lifecycle starts in `smb_NetbiosInit()` and `smb_StartListeners()`. Initialization obtains the OpenAFS NetBIOS server name from `lana_GetUncServerNameEx()`, stores it in UTF-8 and client-character forms, enumerates or selects LANAs, resets each adapter, and registers the padded NetBIOS name with `NCBADDNAME`. Duplicate-name handling attempts one `NCBDELNAME` and retry. If no LANA accepts the name, the code records network stopped via `cm_VolStatus_Network_Stopped()`. Starting listeners configures registry workarounds/timeouts, marks `SMB_LISTENER_STARTED`, reports network started, and creates one `smb_Listener` thread per valid LANA.

`smb_Listener()` itself handles transient `NRC_BRIDGE` and `NRC_NOWILD` failures with limited retries. Persistent failures acquire `smb_StartedLock`, remove the failed LANA, stop its listener, and if no LANA remains, report network stopped and clear the LANA list. A successful listen creates or reuses a VC by LSN/LANA, increments `sessionGen` for new sessions, records remote caller name and `SMB_VCFLAG_REMOTECONN` when appropriate, allocates or reuses a session index, and either rejects the session with `CM_ERROR_ALLBUSY` or initializes `LSNs`, `lanas`, `SessionEvents`, and an additional NCB slot. New session and NCB slot allocation wakes sentinel index-zero events so waiters see the expanded arrays.

Adapter changes are asynchronous. `smb_SetLanAdapterChangeDetected()` records the flag under `smb_StartedLock` and, when not suspended, starts a delayed thread that calls `smb_LanAdapterChange()`. The change handler compares gateway state, NetBIOS name, selected adapter, and enumerated LANA list against current state. Any difference stops and restarts listeners while holding the started lock.

`smb_Init()` is the startup orchestrator. It initializes SMB-local time conversion baseline, freelance root timestamp state, logs and locks, raw buffers, NetBIOS/listener state, event arrays, per-worker NCB slots, and all dispatch tables. The core dispatch table maps classic SMB opcodes, SMB1 AndX calls, transaction calls, NT transact/create/cancel/rename, and unsupported printer/bulk operations. Tran2 and RAP dispatch tables are also populated. If SMB authentication is enabled, the code registers as an LSA logon process, locates the MSV1_0 package, asks MSV1_0 to try the logon cache first, and falls back to `SMB_AUTH_NONE` if registration or package lookup fails. It then starts listeners if NetBIOS initialization succeeded, starts waiter/server/daemon threads, and optionally starts the monitor.

Shutdown reverses the runtime path but does not fully free every global allocation. `smb_Shutdown()` sets `smbShutdownFlag`, sends `NCBHANGUP` for every non-dead session, wakes server workers and waiter sentinels, waits for each server thread's shutdown event with retry signaling, unregisters the NetBIOS name on every valid LANA, and walks live VCs under `smb_rctLock`. FID scache references are detached under each FID mutex with the global refcount lock temporarily dropped, `CM_SCACHEFLAG_SMB_FID` is cleared under the scache write lock, and TID-held VC/user refs are released. Finally it frees the temporary NCB and signals monitor shutdown if enabled.

## State And Persistence Behavior

Most state in this chunk is volatile service runtime state rather than AFS on-disk metadata. Persistent side effects are Windows registry edits used to make the SMB loopback server usable and less likely to time out:

- `smb_configureBackConnectionHostNames(TRUE)` may add `cm_NetbiosName` to `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0\BackConnectionHostNames`, set `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\DisableLoopbackCheck`, and create `HKLM\SOFTWARE\OpenAFS\Client\RemoveDisableLoopbackCheck` so a later disable path can remove the temporary workaround.
- `smb_configureBackConnectionHostNames(FALSE)` removes the OpenAFS NetBIOS name from `BackConnectionHostNames` and removes `DisableLoopbackCheck` only when the OpenAFS marker says this service instance/set-up path owns it.
- `smb_configureExtendedSMBSessionTimeouts(TRUE)` may add the OpenAFS NetBIOS name to `LanmanWorkstation\Parameters\ReconnectableServers` and `ServersWithExtendedSessTimeout`, and may set `ExtendedSessTimeout` to 300 seconds. The disable path removes the name from those multi-string values but leaves unrelated entries intact.

Runtime state includes listener state (`smb_ListenerState`), shutdown state (`smbShutdownFlag`), selected adapter (`smb_LANadapter`), `lana_list`, registered padded name (`smb_sharename`), dynamically allocated local name (`smb_localNamep`), session arrays (`LSNs`, `lanas`, `dead_sessions`, `SessionEvents`), NCB arrays (`NCBs`, `NCBavails`, `NCBevents`, `NCBreturns`, `NCBsessions`, `bufs`), worker shutdown events, raw-buffer free list, dispatch tables, and LSA authentication handles/package IDs. These are protected by a mixture of `smb_StartedLock`, `smb_globalLock`, `smb_ListenerLock`, `smb_rctLock`, FID mutexes, and monitor mutexes.

Session generation (`sessionGen`) is an important diagnostic consistency marker. It is incremented when a new VC session is accepted; dispatch compares the old and current generation to detect requests whose processing overlapped a session startup. `ongoingOps`, `smb_concurrentCalls`, and `smb_maxObsConcurrentCalls` are observational counters for active request processing.

FID/scache state is semi-persistent in the cache-manager lifetime. Create attaches a held `cm_scache_t` to a FID and sets `CM_SCACHEFLAG_SMB_FID`; shutdown and normal close paths must clear that flag and release the scache. Seek mutates only the SMB FID's current offset and does not update file content or metadata.

The monitor queues own heap-allocated `monitored_task` nodes and recycle them via `smb_free_monitored_tasks`. `smb_ServerMonitor()` frees in-progress, free, and pending queues on shutdown. Its `smb_last_dump_time` global throttles dump generation across tasks.

`smb_DumpVCP()` does not persist protocol state, but it serializes a diagnostic snapshot to a caller-supplied file handle. The output includes user/cell ticket state, waiting byte-range locks, live and dead VCs, users, TIDs, and FIDs with path fields and object pointers.

## Dependencies And Integration Points

OpenAFS cache-manager integration is direct:

- `cm_Lookup()`, `cm_SetAttr()`, `cm_Open()`, `cm_SyncOp()`, `cm_SyncOpDone()`, `cm_HoldSCache()`, `cm_ReleaseSCache()`, `cm_HoldUser()`, `cm_ReleaseUser()`, and `cm_ResetServerPriority()` bridge SMB requests and cache-manager vnode/user state.
- `cm_VolStatus_Network_Started()` and `cm_VolStatus_Network_Stopped()` publish SMB network availability using `cm_NetbiosName`.
- `cm_Utf8ToUtf16()` and `cm_Utf8ToClientString()` adapt NetBIOS names between Windows, OpenAFS, and client-character encodings.

SMB subsystem dependencies include the dispatch handlers defined elsewhere in `smb.c` and related files: core operations, V3/AndX operations, transaction/Tran2, NT transact/create/cancel/rename, RAP, SMB3 initialization, raw write completion, FID/UID/TID/VC lookup and release helpers, error mappers, response formatting, packet sending, string cleanup, and dead-VC cleanup.

Windows/NetBIOS dependencies are extensive: `Netbios()` and `NCB` commands implement listening, receive, adapter reset, name add/delete, session hangup, and adapter enumeration; Windows events and waitable timers coordinate all worker/waiter threads; registry APIs configure redirector and loopback behavior; LSA APIs provide SMB authentication integration; structured exception handling wraps server dispatch; and `GetComputerName*`, `GetSystemTimeAsFileTime()`, `GetTickCount()`, `Sleep()`, and `GenerateMiniDump()` support identity, timing, diagnostics, and watchdog behavior.

Threading integration uses OpenAFS thread wrappers: `thrd_Create()`, `thrd_CreateEvent()`, `thrd_WaitForMultipleObjects_Event()`, `thrd_WaitForSingleObject_Event()`, `thrd_SetEvent()`, `thrd_ResetEvent()`, `thrd_CloseHandle()`, and thread counters. Server worker threads call `rx_StartClientThread()` because SMB handlers may perform Rx client work against AFS servers.

Logging and observability go through `osi_Log*`, `afsi_log()`, Windows event-log `LogEvent()`, `afsd_ForceTrace()`, `buf_ForceTrace()`, `osi_LogEnable()`, and `rx_DebugOnOff()`. Long-dispatch logging also depends on `smb_FindUID()`, `smb_LookupTIDPath()`, and `smb_FindFID()` to enrich log records.

## Risks And Edge Cases

Index bounds checks in waiter/server code use `idx > sizeof(array) / sizeof(array[0])`; for zero-based arrays, `idx == length` is still invalid but passes these checks. If a wait result can ever produce the sentinel one-past index, this becomes an out-of-bounds access path. Similar patterns appear for `NCBevents`, `SessionEvents`, `NCBsessions`, and `NCBs`.

`smb_DispatchPacket()` indexes `smb_dispatchTable[inp->inCom]` before explicitly validating that `inCom` is within the table. The table appears sized for all byte opcodes, but any future widening of `inCom` or malformed chained offset handling could turn this into a memory safety issue. Chained request handling also trusts `AndXOffset` enough to set `inp->wctp = inp->data + offset`; malformed offsets rely on downstream handlers or exception handling rather than local bounds validation.

The slow-request logging path in `smb_DispatchPacket()` casts `smbp = (smb_t *) inp` instead of `inp->data`, unlike the rest of the function. If that is not intentional due to `smb_packet_t` layout, logged `mid`, `uid`, `tid`, and other fields could be wrong. This deserves audit because the same local variable name shadows the header pointer from the top of the function.

Raw write sequencing is delicate. The server intentionally delays reposting the session event for `SMB_COM_WRITE_RAW` until it has posted and waited for the raw-data `NCBRECV`. Reordering this path, changing timeout handling, or allowing multiple receives per session would break the protocol guarantee that the raw payload arrives before unrelated traffic on the same session.

The monitor notification API assumes the monitor handles are initialized before notifications are sent. `smb_Server()` only calls `smb_NotifyRequestEvent()` when `smb_monitorReqs` is set, but if monitor thread initialization fails or races, `SetEvent(h_monitored_task_queue)` could see a null handle. Startup currently asserts thread creation, but not event creation inside the monitor thread.

Registry multi-string editing is manual and duplicated. The `bNameFound` flag in `smb_configureExtendedSMBSessionTimeouts()` is reused across `ReconnectableServers` and `ServersWithExtendedSessTimeout`; if it remains true from the first value, the second value may not add `cm_NetbiosName` even when missing. Any fix should preserve disable-path behavior and independent allocation/free handling for the two values.

`smb_Listener()` has a likely typo in the `NRC_NAMERR` branch: while holding `smb_StartedLock`, it assigns `lana_list.lana[i] = LANA_INVALID`, but `i` is not the LANA-list index in that branch and may hold a stale value from prior loops. The persistent failure path below correctly searches the LANA list for the current `lana`.

Shutdown walks `smb_allVCsp` under `smb_rctLock` but temporarily releases the lock while clearing each FID's scache. That avoids lock-order issues but permits the VC/FID graph to change while the outer loop is in progress unless shutdown has fully quiesced all server activity. The preceding worker shutdown wait is therefore essential; regressions in worker wake/termination can expose use-after-free or leaked scache references here.

Many event arrays have sentinel slot zero semantics. `SessionEvents[0]`, `NCBavails[0]`, `NCBevents[0]`, and `NCBreturns[*][0]` are used to wake waiters when arrays grow or shutdown begins. Tests and refactors must preserve the convention that real sessions start at index one and that slot zero is not a normal receive completion.

LSA initialization degrades to `SMB_AUTH_NONE` if registration or MSV1_0 lookup fails. This is operationally resilient but security-sensitive: deployments expecting SMB authentication need logs or tests that make this fallback visible.

`smb_GetSharename()` hardcodes share name `ALL` and allocates with `malloc`; callers own the returned string. Any new caller must free it, and any future share-name configurability needs to revisit this fixed string.

`smb_DumpVCP()` assumes `unp->userp` and its `cellInfop` are valid while dumping usernames. It only takes `smb_rctLock` when requested, and username/cell state may have different lock ownership. Diagnostic callers should pass `lock=1` when possible and avoid invoking this concurrently with teardown unless that is already externally serialized.

## Test Signals

Useful tests for this range include:

- SMB core create/seek tests that create a file, verify returned FID state, seek from start/current/EOF, seek on deleted and IOCTL FIDs, and confirm scache/user references are released on error paths.
- Dispatcher tests for known, unknown, malformed, no-response, NT-status, legacy-core-status, partial-write, buffer-too-small, and GSS-continue results. Include chained `AndX` requests with valid offsets, terminal `0xff`, too-small word counts, and invalid offsets.
- Raw write integration tests that confirm only one receive is outstanding for a session, the raw-data receive is waited on before `SessionEvents[idx_session]` is set, and timeout/error paths still recycle the NCB slot.
- NetBIOS receive-loop tests using mocked `Netbios()` and event wrappers for successful receives, incomplete receives, client session close, repeated unusual errors, session slot reuse, all-busy rejection, and listener failures such as `NRC_BRIDGE`, `NRC_NOWILD`, `NRC_NAMERR`, and `NRC_DUPNAME`.
- Startup/shutdown tests that verify `smb_Init()` initializes dispatch tables and sentinel events, starts the expected threads, and `smb_Shutdown()` wakes all workers, hangs up live sessions, unregisters valid LANA names, clears `CM_SCACHEFLAG_SMB_FID`, releases TID user/VC refs, and signals monitor shutdown.
- Registry tests with isolated/mock registry APIs for enabling/disabling back-connection names and extended timeout server lists, including existing multi-string values, absent values, only-entry removal, unrelated entries, and independent presence/absence in the two LanmanWorkstation lists.
- Adapter-change tests that vary gateway flag, NetBIOS name, selected LANA, LANA-list length, and LANA-list contents, then assert listener stop/restart behavior and no restart when values are unchanged or power state is suspended.
- Request monitor tests that enqueue start/end events out of order, verify sorted insertion and removal, assert trace enabling after 60 seconds, dump generation after 120 seconds, dump cooldown enforcement, old-task purging, and clean queue freeing at shutdown.
- Diagnostics tests for `smb_DumpVCP()` with live/dead VCs, users, TIDs, FIDs, waiting locks, and username cell tickets, plus `smb_LogPacket()` formatting when `LOG_PACKET` is enabled.
- Concurrency and race tests around listener session allocation, `sessionGen` changes during long dispatch, server worker shutdown retries, and NCB/session array growth via slot-zero wakeups.

Operational signals worth monitoring are event-log warnings for bad/too-short/invalid SMBs, wrong-session long requests, unexpected session close, incomplete receives, bad VCP mappings, NetBIOS add/delete/reset/listen failures, LSA authentication fallback messages, long request `afsi_log()` records with AFS fid/path context, monitor-triggered trace/dump activation, and dump output from `smb_DumpVCP()`.
