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
