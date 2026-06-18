# Research: subset-b-009718

Grouped research for NFS-Ganesha NFSv4.1/NLM/NSM protocol headers and OS portability headers. Each section preserves the source path in its title and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfsv41.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfsv41.h

## Purpose
This generated-but-locally-edited RPC/XDR header is the central wire contract for NFSv4.x in Ganesha. Despite the filename, it covers common NFSv4 primitives, NFSv4.0 operations, NFSv4.1 sessions/backchannel/pNFS operations, selected NFSv4.2 operations, and local NFSv4.3 extended-attribute operations. It defines the data structures used by COMPOUND decoding/encoding, callback COMPOUNDs, pNFS file/flex-file layout payloads, and the service/client stubs for NFS program 100003 and callback program 0x40000000.

## Important APIs, Types, And Functions
The header exports constants for object/filehandle sizes, verifier/session id sizes, attribute bit numbers, ACL masks, filehandle volatility flags, open-share/delegation flags, session flags, sequence status flags, pNFS layout flags, and operation counts such as `NFS_V41_NB_OPERATION`. Core scalar aliases include `changeid4`, `clientid4`, `count4`, `length4`, `offset4`, `sessionid4`, `slotid4`, `stateid4`, `bitmap4`, `utf8string`, `nfs_fh4`, and `fattr4`. Major enum families are `nfsstat4`, `nfs_ftype4`, `layouttype4`, `layoutiomode4`, `nfs_lock_type4`, `open_claim_type4`, `open_delegation_type4`, `state_protect_how4`, `nfs_opnum4`, and `nfs_cb_opnum4`.

The per-operation structures model request/result unions for file access, open/close, locking, directory traversal, read/write/commit, attribute operations, client id setup, session setup, pNFS device/layout operations, server-side copy/offload, sparse I/O helpers, xattrs, layout error/stat reporting, and callbacks. `nfs_argop4` and `nfs_resop4` are the main discriminated unions for foreground COMPOUND requests/responses. `CB_COMPOUND4args`/`CB_COMPOUND4res`, `nfs_cb_argop4`, and `nfs_cb_resop4` serve the backchannel callback side. RPC entry prototypes include `nfsproc4_null_4`, `nfsproc4_compound_4`, `cb_null_1`, and `cb_compound_1`, with `_svc` variants for server dispatch.

Most functions are `static inline` XDR helpers. They encode/decode primitives, arrays, discriminated unions, operation arguments/results, COMPOUND arrays, callback arrays, pNFS file layout payloads, and flex-file payloads. Notable local helpers include `utf8string_dup`, `xdr_utf8string_decode`, `inline_xdr_utf8string`, `xdr_bitmap4`, `xdr_dirlist4_encode`, `xdr_nfs_argop4`, `xdr_nfs_resop4`, `xdr_nfs_cb_argop4`, `xdr_nfs_cb_resop4`, and `copy_into_utf8string`.

## Control Flow
The control path is almost entirely XDR-driven. Primitive helpers return false on the first failed field. Union helpers first decode a discriminant, then switch on status, boolean presence, enum value, operation number, delegation type, layout return type, or security flavor before touching the corresponding union member. Result helpers only encode success payloads for `NFS4_OK` and selected error payloads such as denied locks, client-id-in-use address data, too-small device info counts, and layout-try-later hints.

`xdr_nfs_argop4` is the most important decoding dispatcher. It decodes the operation number, calls the matching argument helper, and records request lookahead flags in `xdrs->x_public` when available. It increments read/write counters and marks operations such as OPEN, CREATE, CLOSE, LOOKUP, READDIR, REMOVE, RENAME, SETATTR, SETCLIENTID, and LAYOUTCOMMIT. Unknown foreground opcodes are normalized to `NFS4_OP_ILLEGAL` rather than treated as RPC decode failures. Callback op dispatch is stricter: unknown callback opcodes return false.

## State And Persistence
This header itself owns no durable state. It mutates in-memory XDR objects, allocated buffers, request lookahead fields attached to an `XDR`, and `uio` release behavior during directory encoding. `xdr_utf8string_decode` may allocate `gsh_malloc(size + 1)` and NUL-terminate decoded strings. `copy_into_utf8string` always allocates and NUL-terminates a copy. `xdr_bitmap4` intentionally stores only up to `BITMAP4_MAPLEN` words, skips any extra decoded words, and then clamps `bitmap4_len` to the retained map size. Persistence is represented by protocol state carried elsewhere: client ids, stateids, sequence ids, sessions, delegations, locks, pNFS layouts, device ids, and verifier values.

## Dependencies And Integration Points
The file depends on the Ganesha RPC/XDR layer (`gsh_rpc.h` transitively), inline XDR helpers, memory helpers (`gsh_malloc`/`gsh_free`), logging (`LogDebug` with `COMPONENT_TIRPC`), `nfs_request_lookahead`, `io_data`, `uio` buffer helpers, and optional GSSAPI fields behind `_HAVE_GSSAPI`. NFS server dispatch, compound execution, callback client code, state management, pNFS layout/device code, attribute encoding, and xattr handlers all depend on this ABI matching the wire protocol and implementation tables.

## Risks And Test Signals
Risks concentrate around generated-contract drift, union discriminants, allocation ownership, and size caps. `xdr_bitmap4` silently truncates oversized bitmaps to three words, so new attribute bits beyond that range require scrutiny. `xdr_utf8string_decode` rejects `size >= maxsize`, meaning the maximum is exclusive, and callers must know whether protocol limits expect inclusive behavior. Some NFSv4.2 offload op argument/result helpers are declared but foreground dispatch leaves several cases as no-argument placeholders, which must match the server's advertised operation support. `READ_PLUS` currently enforces a single content segment and only accepts data/hole content. `xdr_data_contents` appears suspicious because the `NFS4_CONTENT_DATA` branch serializes the `hole` fields rather than the `data` union member. Directory encode paths release `uio` on failure, so ownership must be clear. Callback device notification decoding uses bitmap map word values as a type selector, making malformed masks a focused fuzz target.

Strong test signals include protocol compile tests for all operation numbers, COMPOUND decode/encode round trips, XDR_FREE passes for structures with local allocation choices, fuzz tests for oversized arrays/strings/bitmaps and bad union discriminants, NFSv4.1 session and replay-cache tests, pNFS device/layout get/return/commit tests, flex-file layout encode/decode tests, xattr operation tests, callback COMPOUND tests, and focused regression tests for `READ_PLUS`, `WRITE_SAME`, `LAYOUTERROR`, and request lookahead flag population.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfsv41.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm4.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nlm4.h

## Purpose
This rpcgen header defines the Network Lock Manager version 4 protocol surface used by Ganesha for NFSv3-style advisory locking and share reservations. It provides the XDR data model, RPC procedure numbers, client/server stub prototypes, and XDR function declarations for program 100021 version 4.

## Important APIs, Types, And Functions
Important constants include string/object size caps (`LM_MAXSTRLEN`, `MAXNETOBJ_SZ`, `SM_PRIV_SZ`), `NLMPROG`, `NLM4_VERS`, `NLMPROC4_*`, and `NLM_V4_NB_OPERATION`. `nlm4_stats` captures granted, denied, grace-period, deadlock, read-only filesystem, stale filehandle, file-too-large, and generic failure states. Core protocol structures are `nlm4_res`, `nlm4_testres`, `nlm4_holder`, `nlm4_lock`, lock/test/cancel/unlock argument structs, share mode/access enums, `nlm4_shareargs`, `nlm4_shareres`, `nlm4_free_allargs`, and `nlm4_sm_notifyargs`.

The header declares sync RPC entry points such as `nlmproc4_test_4`, `nlmproc4_lock_4`, `nlmproc4_cancel_4`, `nlmproc4_unlock_4`, and service-side `_svc` variants. It also declares async message/result procedures (`*_MSG`, `*_RES`), `NLMPROC4_SM_NOTIFY`, share/unshare, no-monitor lock, free-all, `nlmprog_4_freeresult`, and XDR functions for every exported structure.

## Control Flow
NLM control flow is encoded as independent RPC procedures. Synchronous calls return `nlm4_res`, `nlm4_testres`, or `nlm4_shareres`; asynchronous calls send a void request and later deliver a result through matching `*_RES` procedures keyed by cookies. Test replies use a discriminated union: when status indicates denial, `nlm4_holder` describes the blocking lock. Share procedures carry an extra sequence value in results. `SM_NOTIFY` bridges status monitor restart notifications into the lock manager.

## State And Persistence
The header defines wire state rather than owning storage. Cookies correlate async requests and results. `nlm4_lock` carries caller name, filehandle, owner handle, svid, offset, and length. Reclaim/state fields link locks to NSM restart state. Actual persistent lock/share/client ownership lives in SAL/state-management code outside this generated header.

## Dependencies And Integration Points
It depends on `gsh_rpc.h` for RPC/XDR types including `CLIENT`, `SVCXPRT`, `XDR`, `netobj`, and `struct svc_req`. It integrates with NLM service dispatch, NLM client callbacks, NSM monitor notifications, SAL lock owner/client tracking, and utility code in `nlm_util.h`/`nlm_async.h`.

## Risks And Test Signals
Risks include ABI drift from rpcgen output, duplicate typedefs for fixed-width integer names, cookie/owner byte ownership, and status mapping mismatches between NLM and internal state codes. Async procedures need timeout and duplicate-response coverage. Test signals include XDR round trips for every argument/result struct, lock/test/unlock/cancel integration tests, share/unshare tests, reclaim-after-grace tests, SM_NOTIFY restart simulations, and interop with Linux `lockd` clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm_async.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nlm_async.h

## Purpose
This header declares the asynchronous NLM response path. It coordinates sending NLMv4 async callbacks/results and waking waiters that are blocked waiting for a response key.

## Important APIs, Types, And Functions
It exports `nlm_async_resp_mutex` and `nlm_async_resp_cond` for response synchronization. `nlm_async_callback_init()` initializes the async callback machinery. `nlm_send_async_res_nlm4()` and `nlm_send_async_res_nlm4test()` send async responses for normal NLM results and TEST results through a `state_async_func_t` callback. `nlm_send_async()` is the generic client-side send routine taking an NLM procedure number, host/client state, argument pointer, and wait key. `nlm_signal_async_resp()` signals completion for a key.

## Control Flow
Callers initialize once, then use `nlm_send_async()` or the typed result wrappers to issue RPC messages to a `state_nlm_client_t`. The key argument is the rendezvous identity for a waiter; when a corresponding async result is observed, `nlm_signal_async_resp()` wakes waiters via the exported mutex/condition pair.

## State And Persistence
State is transient process memory: the global mutex, condition variable, host/client structures, callback function references, result storage in `nfs_res_t`, and wait keys. No persistent data is written by this layer, but its completion signals influence lock wait progress and blocked-lock grant behavior.

## Dependencies And Integration Points
The header depends on pthreads and `sal_data.h` for `state_nlm_client_t`, `state_async_func_t`, and `nfs_res_t`. It integrates with generated NLM RPC procedures from `nlm4.h`, blocked-lock handling, and NLM utility/state code that registers owners and lock entries.

## Risks And Test Signals
Risks include lost wakeups, key lifetime bugs, holding `nlm_async_resp_mutex` across slow RPC paths, mismatched callback function signatures, and double signaling. Test signals include async lock-grant callbacks, timeout/cancel paths, multi-client concurrent waits, callback init idempotence, and fault-injection of unreachable NLM peers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm_async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm_util.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nlm_util.h

## Purpose
This header declares the NLM utility layer that translates wire-level NLM lock/share requests into Ganesha FSAL/SAL state objects and back into NLM status/conflict replies.

## Important APIs, Types, And Functions
Utility helpers include `lock_result_str()`, `copy_netobj()`, `netobj_free()`, and `netobj_to_string()`. `nlm_process_parameters()` is the central lock request normalizer: it consumes an RPC request, exclusivity flag, `nlm4_lock`, and NSM state, then fills a `fsal_lock_param_t`, target FSAL object, NSM client, NLM client, owner, optional blocked-lock callback data, and internal `state_t`. `nlm_process_share_parms()` performs analogous translation for share reservations. `nlm_process_conflict()` fills an `nlm4_holder` from an internal conflicting owner and lock range. `nlm_convert_state_error()` maps internal state-layer failures to `nlm4_stats`. `nlm_granted_callback()` is the state-layer hook used when a blocked lock can be granted.

## Control Flow
NLM service handlers call the process helpers before invoking the state manager. The helpers parse filehandles and owner handles, resolve exports/objects, acquire or create NSM/NLM client references and owner references, translate byte-range semantics, and optionally prepare callback data. After a state operation, handlers map internal statuses through `nlm_convert_state_error()` and report conflicts through `nlm_process_conflict()`.

## State And Persistence
This header does not store state directly, but its APIs manage references to SAL state objects. The returned NSM client, NLM client, state owner, blocked data, and state handle represent live server state and must be released according to the implementation's ownership contract. Netobj helpers allocate/copy/free byte buffers.

## Dependencies And Integration Points
It includes `gsh_list.h`, generated `nlm4.h`, and `sal_data.h`. It integrates NLM RPC handlers with FSAL object lookup, export state, SAL locking, blocked-lock callbacks, NSM monitoring, and generated NLM wire structures.

## Risks And Test Signals
Risks include reference leaks on partial failures, stale filehandle handling, incorrect owner identity composition, byte-range overflow for offset/length conversion, mismatched `care_t` behavior, and translating internal statuses to overly broad NLM failures. Test signals include lock/share requests for valid and stale handles, owner reuse, no-owner `care` cases, blocked-lock grant callbacks, conflict formatting, reclaim/grace handling, and netobj copy/free leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nlm_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nsm.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nsm.h

## Purpose
This rpcgen header defines the Network Status Monitor protocol pieces used by Ganesha's NLM implementation to monitor client restarts and receive reboot notifications.

## Important APIs, Types, And Functions
Constants identify status monitor program/version/procedures: `SM_PROG`, `SM_VERS`, `SM_MON`, `SM_UNMON`, `SM_UNMON_ALL`, and `SM_NOTIFY`. Wire types include `res`, `sm_stat_res`, `sm_stat`, `my_id`, `mon_id`, `mon`, and `notify`. Ganesha-facing helpers are `nsm_monitor()`, `nsm_unmonitor()`, `nsm_unmonitor_all()`, and `nsm_notify()`. XDR declarations cover every wire type.

## Control Flow
The NLM layer asks NSM to monitor a host when lock state is established, unmonitor hosts when state is removed, unmonitor all during shutdown/reset, and process notify events carrying host and state values after a peer restarts. The `mon` structure combines monitored peer identity with callback identity and a private 16-byte token.

## State And Persistence
The header owns no runtime storage. It defines monitor identities and notification payloads. Actual monitor tables, host references, and restart-state persistence are implemented outside the header, tied to `state_nsm_client_t`.

## Dependencies And Integration Points
It includes `config.h`, `gsh_rpc.h`, and `sal_data.h`. It integrates NSM RPC/XDR data with SAL client state and the NLM reclaim/free-all paths that react to client restart notifications.

## Risks And Test Signals
Risks include host-name canonicalization mismatches, stale monitor records, private-token mismatch, and notification replay/order issues. Test signals include XDR round trips, monitor/unmonitor lifecycle tests, simulated `SM_NOTIFY` after client restart, unmonitor-all shutdown coverage, and NLM lock reclaim behavior during grace periods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/acl.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/acl.h

## Purpose
This is the OS-neutral include point for non-standard POSIX ACL APIs. It hides platform-specific ACL headers behind one `os/acl.h` path.

## Important APIs, Types, And Functions
The header includes `config.h` and, when `LINUX` is defined, includes `<os/linux/acl.h>`. It declares no functions or types itself.

## Control Flow
All behavior is compile-time conditional inclusion. Linux builds receive the Linux ACL shim; non-Linux builds currently receive only the guard and config include.

## State And Persistence
There is no runtime state or persistence. The file controls preprocessor visibility of platform ACL declarations.

## Dependencies And Integration Points
It depends on build configuration macros from `config.h`. FSAL and permission code can include this common path without directly selecting Linux ACL headers.

## Risks And Test Signals
Risks include silent absence of ACL declarations on platforms that need their own shim and accidental build macro mismatch. Test signals are compile tests for Linux and non-Linux configurations, plus ACL feature tests in FSAL modules that include `os/acl.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/darwin/sys_resource.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/darwin/sys_resource.h

## Purpose
This Darwin portability header declares a platform wrapper for retrieving the open-file resource limit.

## Important APIs, Types, And Functions
It includes `<sys/resource.h>` and declares `int get_open_file_limit(struct rlimit *rlim);`.

## Control Flow
Callers pass an `rlimit` pointer to the wrapper. The implementation outside this header is expected to perform the Darwin-appropriate `RLIMIT_NOFILE` query and return a normal system-call style status.

## State And Persistence
No state is stored in the header. The function writes into caller-provided `struct rlimit` memory and reads process/kernel resource-limit state.

## Dependencies And Integration Points
It integrates generic resource-limit code with Darwin-specific implementation. It is paired with FreeBSD's macro version and likely a Linux equivalent so common code can call `get_open_file_limit()`.

## Risks And Test Signals
Risks are implementation/header mismatch, null `rlim` handling, and platform differences in maximum file descriptor limits. Test signals include Darwin compile tests and runtime checks comparing the wrapper result to `getrlimit(RLIMIT_NOFILE, ...)`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/darwin/sys_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/extended_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/extended_types.h

## Purpose
This FreeBSD extended-types shim centralizes platform type includes for code that expects OS-specific type completion.

## Important APIs, Types, And Functions
It includes `<sys/types.h>` and declares no new aliases, structs, or functions.

## Control Flow
The header is compile-time only. Including it makes standard FreeBSD system types available through a Ganesha OS abstraction path.

## State And Persistence
There is no runtime state or persistent behavior.

## Dependencies And Integration Points
It depends on FreeBSD system headers and integrates with code that includes `os/<platform>/extended_types.h` for platform-specific type availability.

## Risks And Test Signals
Risks are minimal but include missing future FreeBSD-specific aliases if generic code starts requiring them. Test signals are FreeBSD compile coverage for FSAL and utility files that include extended types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/extended_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/fsal_handle_syscalls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/fsal_handle_syscalls.h

## Purpose
This FreeBSD FSAL handle syscall shim adapts Ganesha's VFS file-handle operations to FreeBSD's `fhlink`/`fhreadlink` and handle layout.

## Important APIs, Types, And Functions
It includes `fsal_convert.h`, `<sys/mount.h>`, and `syscalls.h`. It defines fallback constants for Linux-ish flags that FreeBSD may lack (`O_PATH`, `O_DIRECTORY`, `O_NOACCESS`, `AT_EMPTY_PATH`) and `HANDLE_DUMMY`. `struct v_fid` and `struct v_fhandle` model the FreeBSD handle data layout containing flags, filesystem id, and file id bytes. `v_to_fhandle(hdl)` converts a Ganesha handle data pointer to the `struct fhandle *` expected by FreeBSD calls. Inline wrappers are `vfs_stat_by_handle()`, `vfs_link_by_handle()`, and `vfs_readlink_by_handle()`.

## Control Flow
`vfs_stat_by_handle()` ignores missing FreeBSD `AT_EMPTY_PATH` semantics and calls `fstat()` on the mount file descriptor. `vfs_link_by_handle()` and `vfs_readlink_by_handle()` convert `fh->handle_data` to a native handle pointer and call `fhlink()` or `fhreadlink()`.

## State And Persistence
The header stores no state. The wrappers operate on descriptors, destination directories, names, buffers, and serialized handle bytes supplied by callers. Link creation can persist filesystem namespace changes through `fhlink()`.

## Dependencies And Integration Points
It integrates FreeBSD VFS FSAL code with common Ganesha handle abstractions (`vfs_file_handle_t`) and system calls declared in `syscalls.h`. It bridges source code written around Linux-style open/stat/link-by-handle APIs to FreeBSD primitives.

## Risks And Test Signals
Risks include handle layout/offset assumptions in `v_to_fhandle`, unused `srcfd`/`sname` parameters hiding semantic differences, fallback flag values changing behavior relative to Linux, and `fstat(mountfd)` not being equivalent to stat-by-handle for all callers. Test signals include FreeBSD compile tests, round trips for file handles from real mounts, hard-link-by-handle tests, symlink readlink-by-handle tests, and namespace/permission failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/fsal_handle_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/memstream.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/memstream.h

## Purpose
This FreeBSD compatibility header provides the API declaration and state structure for `open_memstream()` on platforms where the GNU-style function is not natively exposed.

## Important APIs, Types, And Functions
It includes standard C headers and defines `struct memstream` with `char **cp`, `size_t *lenp`, and `size_t offset`. It declares `FILE *open_memstream(char **cp, size_t *lenp);`.

## Control Flow
The header has no inline implementation. Callers request a writable `FILE *` backed by dynamically managed memory; the implementation is responsible for updating the caller's buffer pointer and length pointer as data is written/flushed/closed.

## State And Persistence
State lives in the returned stream and internal `struct memstream` bookkeeping. Data persists in heap memory returned to the caller via `cp`/`lenp`; the caller is responsible for eventual free according to the implementation contract.

## Dependencies And Integration Points
It integrates code using GNU `open_memstream()` with FreeBSD builds. It depends on libc `FILE`, allocation, errno, string, and size types.

## Risks And Test Signals
Risks include incomplete compatibility with GNU flush/close semantics, allocation failure handling, offset/length synchronization, and caller ownership confusion. Test signals include write/flush/close behavior, zero-length streams, repeated writes, large writes, error injection, and ASAN/leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/memstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/mntent.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/mntent.h

## Purpose
This FreeBSD compatibility header supplies a Linux-style `mntent` interface for code that scans mounted filesystems.

## Important APIs, Types, And Functions
It defines `MOUNTED` as `"dummy"` and `MNTTYPE_NFS` as `"nfs"`. `struct mntent` contains filesystem name, mount directory, type, options, dump frequency, and pass number. `setmntent(x, y)` is a dummy macro returning a non-null `FILE *` sentinel, `endmntent(x)` is a no-op macro, and real declarations are provided for `getmntent(FILE *fp)` and `hasmntopt(const struct mntent *mnt, const char *option)` using `__P`.

## Control Flow
Common mount-scanning code can call `setmntent`, repeatedly call `getmntent`, check options with `hasmntopt`, and call `endmntent`. On FreeBSD the open/close phases are stubbed; the implementation of `getmntent` must translate native mount data into `struct mntent` records.

## State And Persistence
No state is stored in the header. Runtime state belongs to the implementation of `getmntent` and returned static or allocated `mntent` fields. It reads system mount state but does not persist changes.

## Dependencies And Integration Points
It depends on `<stdio.h>` and old-style prototype macro support from the platform headers. It integrates Linux-oriented mount parsing code with FreeBSD mount enumeration.

## Risks And Test Signals
Risks include dummy `FILE *` values surprising code that expects a real stream, lifetime of returned strings, option parsing differences, and hard-coded `"dummy"` for `MOUNTED`. Test signals include FreeBSD mount enumeration, NFS mount type detection, option lookup tests, repeated iteration, and callers that pass the sentinel to no APIs other than this shim.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/mntent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/quota.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/quota.h

## Purpose
This FreeBSD quota shim normalizes quota syscall naming and quota-block structure field names for Ganesha code shared with Linux.

## Important APIs, Types, And Functions
It includes `<ufs/ufs/quota.h>`. `QUOTACTL(cmd, path, id, addr)` maps generic call sites to FreeBSD `quotactl(path, cmd, id, (void *)addr)`. `struct dqblk_os` mirrors the quota fields expected by Ganesha, using `dqb_curspace` rather than FreeBSD's differently named member. On newer FreeBSD compiler versions it undefines `dqblk`, then maps `dqblk` to `dqblk_os`.

## Control Flow
Shared quota code calls `QUOTACTL` and refers to `struct dqblk` fields. This header rewrites those compile-time names so FreeBSD builds call the native syscall with the correct argument order and use the compatibility quota structure.

## State And Persistence
The header has no state. Runtime quota state is read or written through `quotactl` depending on the command. `dqblk_os` instances are caller-owned buffers representing quota limits, usage, and grace times.

## Dependencies And Integration Points
It integrates FSAL quota/reporting code with FreeBSD UFS quota definitions. It also depends on FreeBSD-specific `__FreeBSD_cc_version` behavior for the `dqblk` macro adjustment.

## Risks And Test Signals
Risks include structure layout mismatch with kernel expectations, command argument-order mistakes, macro replacement leaking into unrelated includes, and version-guard drift. Test signals include FreeBSD quota compile tests, `QUOTACTL` get/set smoke tests against a quota-enabled filesystem, field-value round trips for block/inode usage, and builds across supported FreeBSD versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/sys_resource.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/sys_resource.h

## Purpose
This FreeBSD resource-limit shim provides the common `get_open_file_limit()` name used by portable Ganesha code.

## Important APIs, Types, And Functions
It includes `<sys/resource.h>` and defines `get_open_file_limit(rlim)` as `getrlimit(RLIMIT_NOFILE, (rlim))`.

## Control Flow
Callers invoke the common wrapper-like macro with a `struct rlimit *`; the macro directly evaluates to the system `getrlimit` call for open-file limits.

## State And Persistence
No state is stored. The macro reads process resource-limit state and writes into caller-provided memory.

## Dependencies And Integration Points
It integrates generic resource-limit initialization code with FreeBSD's standard `getrlimit` API and mirrors the Darwin header's declared wrapper name.

## Risks And Test Signals
Risks include macro side effects if the argument expression has side effects and lack of function-address compatibility compared with platforms that declare a real function. Test signals include FreeBSD compile tests, runtime comparison with direct `getrlimit(RLIMIT_NOFILE, ...)`, and call sites that do not attempt to take the wrapper's address.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/sys_resource.h -->
