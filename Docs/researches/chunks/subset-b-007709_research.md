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
