# sources/distributed-fs/openafs/src/WINNT/afsd/smb.h

## Purpose

`smb.h` is the primary public contract for the OpenAFS Windows `afsd` SMB1 server layer. It defines the on-wire SMB header layout, protocol constants, per-connection/session/tree/file-handle state records, directory-search and byte-range-lock bookkeeping, and the exported helper APIs used by `smb.c`, `smb3.c`, `smb_ioctl.c`, and `smb_rpc.c`.

The file is not just a declarations bucket: it encodes ownership and locking expectations for the SMB server. `smb_vc_t`, `smb_user_t`, `smb_tid_t`, and `smb_fid_t` form the reference-counted object graph for virtual circuits, authenticated sessions, tree connects, and open file descriptors. Packet helpers and dispatch types define how incoming NetBIOS/SMB messages are decoded, routed, chained, suspended, resumed, and sent back.

## Important APIs, Types, And Constants

- `smb_t`: packed SMB1 wire header. It preserves byte-level protocol layout with `id`, `com`, DOS/NT error fields, `flg2`, `tid`, `pid`, `uid`, `mid`, `wct`, and variable data. The macros `KNOWS_LONG_NAMES`, `WANTS_DFS_PATHNAMES`, and `WANTS_UNICODE` inspect this header directly.
- Protocol flags and levels: `SMB_FLAGS*`, `SMB_FLAGS2_*`, information-level constants, transaction named-pipe opcodes, file attributes, locking flags, file types, and device-state constants are consumed by core SMB handlers and Tran2/NT handlers in `smb.c` and `smb3.c`.
- `smb_packet_t`: in-memory packet wrapper around `SMB_PACKETSIZE` bytes. It stores the current request pointer (`wctp`), current chained command (`inCom`), chained request count (`inCount`), inherited AndX FID (`fid`), associated `smb_vc_t`, NetBIOS control block, decoded string storage, resume code, and flags such as `SMB_PACKETFLAG_NOSEND` and `SMB_PACKETFLAG_SUSPENDED`.
- `smb_ncb_t`: free-list wrapper around a Windows NetBIOS `NCB`.
- `smb_vc_t`: virtual circuit. Tracks connection identity (`vcID`, `lsn`, `lana`, `session`), negotiated protocol/auth flags, child TIDs/UIDs/FIDs, SMB counters, remote name, NTLM challenge key, and extended-security context. `SMB_VCFLAG_*` records negotiated dialect, NT status support, Unicode support, remote/dead/cleanup state, and extended-auth progress.
- `smb_user_t` and `smb_username_t`: per-session UID and shared username/machine identity. `smb_username_t` owns the `cm_user_t` token context and logoff/AFS integrated-logon preservation flags.
- `smb_tid_t`: tree-connect record. Stores share-derived pathname, tree user, IPC marker, and VC backlink.
- `smb_fid_t`: open file descriptor. Holds the server FID, scache/user references, current offset, IOCTL/RPC handles, NT-open parent/path state, raw-write event, directory-delete state, sharing/open-mode flags, and named-pipe flags.
- `smb_dirSearch_t`: persistent directory enumeration cookie with LRU queue linkage, scache, attributes, tree/relative path, mask, and bulk-stat flags.
- `smb_dirListPatch_t`: deferred patch entry for directory listings, including dot-file and IOCTL markers.
- `smb_waitingLock_t` and `smb_waitingLockRequest_t`: async byte-range lock state. A suspended SMB packet can be resumed when all locks complete, fail, timeout, or are cancelled.
- `smb_proc_t` and `smb_dispatch_t`: dispatch-table ABI for SMB commands. `SMB_DISPATCHFLAG_CHAINED` describes AndX commands and `SMB_DISPATCHFLAG_NORESPONSE` marks handlers that send or suppress responses themselves.
- Exported lifecycle APIs: `smb_FindVC`, `smb_HoldVC`, `smb_ReleaseVC`, `smb_CleanupDeadVC`, `smb_FindTID`, `smb_ReleaseTID`, `smb_FindUID`, `smb_ReleaseUID`, `smb_FindFID`, `smb_CloseFID`, `smb_ReleaseFID`, and directory-search find/new/delete/release helpers.
- Exported packet APIs: `smb_CopyPacket`, `smb_FreePacket`, `smb_GetSMBData`, parameter get/set helpers, string parse/unparse helpers, `smb_GetResponsePacket`, `smb_SendPacket`, `smb_FormatResponsePacket`, and error mappers.
- Auth/global state: `smb_authType`, `SMB_AUTH_*`, LSA handles/package IDs, server domain/OS/LanManager strings, server GUID, Unicode setting, monitor flag, and NTLM challenge request/response structures.

## Control Flow

Incoming traffic is handled by the SMB server code in `smb.c`. A NetBIOS receive path obtains or creates an `smb_vc_t`, wraps the bytes in `smb_packet_t`, creates a response packet, and calls `smb_DispatchPacket`. The dispatcher initializes `inp->inCom`, `inp->wctp`, `inp->inCount`, and `inp->ncb_length`, formats the response with `smb_FormatResponsePacket`, and then loops over the current SMB command until `inCom == 0xff`.

For each command, `smb_DispatchPacket` indexes `smb_dispatchTable[SMB_NOPCODES]`, whose entries use the `smb_dispatch_t` ABI from this header. Unknown opcodes are initialized to `smb_SendCoreBadOp`; known entries include core file operations, negotiate, session setup, tree connect, AndX read/write/open/lock, transaction/transaction2, NT create, NT transact, cancel, and rename. Chained commands get a default AndX response header; no-response handlers such as raw read, echo, transaction, transaction2, and cancel avoid normal send behavior.

Negotiation (`smb_ReceiveNegotiate`) sets `SMB_VCFLAG_USECORE`, `SMB_VCFLAG_USEV3`, or `SMB_VCFLAG_USENT` and advertises capabilities such as NT status, large files, raw mode, DFS, extended security, and Unicode. Session setup (`smb_ReceiveV3SessionSetupX`) authenticates using none/NTLM/extended auth, creates or reuses `smb_username_t` and `smb_user_t`, sets status and Unicode flags from client capabilities, and returns the assigned UID. Tree connect creates an `smb_tid_t`, resolves the share path, optionally marks IPC, and returns the TID. Open/create paths allocate `smb_fid_t`; read/write/lock/close paths resolve FIDs back to `cm_scache_t` and `cm_user_t`.

Tran2 and NT paths extend this contract through `smb3.h`, included at the end of `smb.h`. `smb_tran2Packet_t` stores multi-packet transaction assembly and response state while still using `smb_vc_t`, `smb_packet_t`, string helpers, error mapping, and dispatch semantics declared here.

## State And Persistence Behavior

The SMB layer keeps long-lived in-memory state rather than persistent on-disk state.

- Virtual circuits live on global VC lists, have magic validation, and own child TID/UID/FID lists. `smb_FindVC(..., SMB_FLAG_CREATE, ...)` allocates a VC, initializes counters, stores NetBIOS connection identity, and obtains an NTLM challenge when needed.
- Reference counts are protected primarily by `smb_rctLock`; comments in the header call out that tree connection fields and reference counts are locked there. Per-object mutexes protect non-tree fields and mutable flags.
- Dead VCs are marked with `SMB_VCFLAG_ALREADYDEAD`. `smb_CleanupDeadVC` moves them from the active list to a dead list, closes outstanding FIDs, releases TIDs and UIDs, and lets the final reference free the VC. Cleanup state is guarded by `SMB_VCFLAG_CLEAN_IN_PROGRESS`.
- `smb_username_t` can intentionally survive with zero references for AFS integrated logon or logoff token transfer. `SMB_USERNAMEFLAG_AFSLOGON`, `SMB_USERNAMEFLAG_LOGOFF`, `last_logoff_t`, `smb_LogoffTokenTransfer`, and `smb_LogoffTransferTimeout` let the daemon preserve tokens briefly across SMB session churn.
- FIDs own scache/user references, IOCTL state, RPC state, raw-write events, and NT-open paths. Deletion is two-stage: close logic marks `deleteOk`, and `smb_ReleaseFID` removes the FID, clears `CM_SCACHEFLAG_SMB_FID`, releases resources, closes events, and releases the parent VC only when the refcount reaches zero.
- Directory searches are cookie-based, LRU-managed, and held in global memory. Old core protocol searches use small cookies; SMB3/Tran2 searches can use 16-bit cookies. GC deletes unused search objects when cookie space wraps.
- Waiting locks persist suspended packet state in `smb_allWaitingLocks`. The waiting-lock daemon retries CM locks, resumes the original packet via `SMB_PACKETFLAG_SUSPENDED`, and frees packets, VC, scache, NCB, and lock request state after dispatch resumes.

## Dependencies

This header depends on Windows and OpenAFS client internals:

- Windows APIs and types: `_WIN32_WINNT`, `ntsecapi.h`, `NCB`, `HANDLE`, `GUID`, `LSA_STRING`, `MSV1_0_*`, `SID`, `FILETIME`, `LARGE_INTEGER`, and NetBIOS/LSA authentication behavior.
- OpenAFS/cache manager types: `cm_user_t`, `cm_scache_t`, `cm_req_t`, `cm_attr_t`, `cm_space_t`, `cm_fid_t`, `cm_dirEntry_t`, `cm_file_lock_t`, and cache-manager vnode operations via `cm_vnodeops.h`.
- OpenAFS OSI primitives: `osi_mutex_t`, `osi_rwlock_t`, `osi_queue_t`, `osi_hyper_t`, `osi_log_t`, event handles, thread/event helpers, and lock hierarchy rules.
- Local SMB modules: `smb3.h`, `smb_ioctl.h`, `smb_iocons.h`, and `smb_rpc.h` are included after the base types so those modules can build on `smb_vc_t`, `smb_packet_t`, and `smb_fid_t`.
- Character conversion/NLS: `cm_nls.h`, `clientchar_t`, Unicode/UTF-8 conversion helpers, and the compile-time `SMB_UNICODE` behavior used by parse/unparse routines.

## Integration Points

- `smb.c` owns the base implementation: global locks and lists, packet/NCB free lists, VC/TID/UID/FID lifecycle, packet parameter helpers, string helpers, response formatting, send/error mapping, daemon cleanup, waiting-lock daemon, dispatch loop, core SMB handlers, and dispatch-table initialization.
- `smb3.c` implements SMB3/NT/Tran2 command handlers declared here or in the included `smb3.h`: session setup, tree connect, transaction assembly, named-pipe commands, RAP calls, query/set info, directory enumeration, AndX open/read/write/lock, NT create, NT transact, notify change, cancel, and rename.
- `smb_ioctl.c` uses `SMB_FID_IOCTL`, `smb_ioctl_t`, packet helpers, and UID/user lookup to implement OpenAFS control-file IOCTLs over SMB reads/writes.
- `smb_rpc.c` uses `SMB_FID_RPC` and named-pipe flags to multiplex MS RPC endpoint behavior over SMB named pipes.
- Cache-manager integration is through `cm_user_t`, `cm_scache_t`, vnode operations, lock operations, request initialization (`smb_InitReq` sets `CM_REQ_SOURCE_SMB`), and SMB-to-CM error translation.
- Windows configuration and identity integration includes registry-backed share/DFS policy lookup, LSA/NTLM or extended authentication, SID normalization, LocalSystem detection, and NetBIOS listener control.

## Risks And Edge Cases

- Wire-format safety is fragile. `smb_t` is packed and many helpers compute byte offsets manually from `wct`, BCC, and raw packet pointers. Bad bounds checks can become crashes or malformed responses; several parameter getters panic on out-of-range access.
- `SMB_PACKETSIZE` is fixed at 32768 while raw mode and SMB negotiation advertise larger limits. Handlers that copy variable data must respect packet buffer limits and client-reported sizes.
- Refcount and lock-order correctness are critical. Comments warn that `smb_ReleaseFID` must not run with a `cm_scache_t` rwlock held; VC cleanup intentionally drops and reacquires locks. Regressions here can deadlock, leak, double-free, or free objects still linked from global lists.
- Authentication state spans VC flags, LSA handles, `secCtx`, username records, SID strings, and token transfer windows. Session setup failures must avoid creating or reusing the wrong UID/token association.
- Unicode behavior depends on both compile-time `SMB_UNICODE` and runtime negotiation flags. `WANTS_UNICODE(inp)` alone is not sufficient; VC `SMB_VCFLAG_USEUNICODE` also matters for response formatting and Tran2 parsing.
- AndX chaining relies on packet fields such as `inCom`, `inCount`, `fid`, and response `wctp`. Errors in a handler can corrupt later chained operations or fail to inherit an OpenAndX FID via `smb_ChainFID`.
- Long-running byte-range locks suspend packets and keep VC/scache/packet references alive. Cancellation, timeout, VC death, and retry completion must all release the same resources exactly once.
- Directory-search cookie exhaustion and LRU GC are old-protocol sensitive. Core searches are limited to 8-bit cookies, while V3 searches use wider cookies; cleanup behavior differs by protocol mode.
- File flags encode Windows compatibility quirks (`SMB_FID_LOOKSLIKECOPY`, delete-on-close, share modes, executable flush behavior, named-pipe modes). Simplifying these flags risks breaking legacy Windows redirector behavior.

## Test Signals

- Protocol negotiation tests should verify dialect selection, capability bits, NT status versus core error mapping, Unicode negotiation, extended-security advertisement, and raw-mode behavior.
- Session and token tests should cover anonymous/blank UID 0, NTLM and extended-auth success/failure, SID-backed usernames, repeated session setup for the same user, AFSLOGON token preservation, logoff transfer timeout cleanup, and LocalSystem detection.
- Tree-connect tests should cover normal shares, `*.` aliasing to `all`, bad share names, IPC$, DFS advertisement, CSC policy bits, and per-TID path lookup.
- FID lifecycle tests should open/read/write/close files, exercise IOCTL and RPC FIDs, delete-on-close, NT-open parent/path state, share-mode locks, raw writes, VC-death cleanup, and refcount assertions.
- Packet and dispatch tests should include malformed short packets, bad parameter indexes, unknown opcodes, AndX command chains, no-response handlers, suspended lock resumes, and error responses in both DOS/class and NTSTATUS modes.
- Directory enumeration tests should cover core and Tran2 search cookies, LRU movement, cookie wrap/GC, hidden dot-file filtering, bulk-stat flag cleanup, find-close behavior, and search-after-delete cases.
- String conversion tests should cover ASCII blocks, ANSI paths, Unicode word alignment, nul-terminated and counted strings, empty strings, long names near `SMB_STRINGBUFSIZE`, and output-size accounting.
- Concurrency tests should stress multiple VCs, UID/TID/FID churn, simultaneous close and scache lookup, waiting locks, daemon cleanup, NetBIOS send failures, listener restart/stop, and shutdown.
