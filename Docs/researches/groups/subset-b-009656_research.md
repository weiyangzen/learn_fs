# subset-b-009656 Research

Grouped source research for the libnfs NFSv4 high-level async API implementation and ONC RPC PDU handling. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/nfs_v4.c -->
# sources/user-network-fs/libnfs/lib/nfs_v4.c

## Purpose

`sources/user-network-fs/libnfs/lib/nfs_v4.c` implements the high-level asynchronous NFSv4 client operations for libnfs. It turns POSIX-like file API calls into NFSv4 COMPOUND requests, handles path normalization and symlink resolution, parses NFSv4 attributes into libnfs/stat structures, and maintains open, lock, directory, offset, and mount state. The source was read as a complete 5408-line file for this report.

## Important APIs, Types, and Functions

Core callback and request state is carried by `struct nfs4_cb_data`, which stores the `nfs_context`, callback, private data, resolved path, continuation callbacks, open owner, flags, path lookup filler, symlink lookup state, and read/write offset update data. `struct lookup_filler` lets path lookup append operation-specific NFSv4 ops after the common `PUTROOTFH` or `PUTFH`, `LOOKUP...`, and `GETATTR` prefix. `struct nfs4_blob` stores caller-owned or helper-owned variable buffers with optional destructors.

Public async entry points include `nfs4_mount_async`, `nfs4_chdir_async`, `nfs4_stat64_async`, `nfs4_fstat64_async`, `nfs4_open_async`, `nfs4_creat_async`, `nfs4_close_async`, `nfs4_pread_async_internal`, `nfs4_preadv_async_internal`, `nfs4_write_async`, `nfs4_pwrite_async_internal`, `nfs4_fsync_async`, `nfs4_truncate_async`, `nfs4_ftruncate_async`, `nfs4_lseek_async`, `nfs4_opendir_async`, `nfs4_readlink_async`, `nfs4_symlink_async`, `nfs4_link_async`, `nfs4_rename_async`, `nfs4_unlink_async`, `nfs4_rmdir_async`, `nfs4_mkdir2_async`, `nfs4_mknod_async`, `nfs4_getacl_async`, `nfs4_access_async`, `nfs4_access2_async`, `nfs4_chmod_async_internal`, `nfs4_fchmod_async`, `nfs4_chown_async_internal`, `nfs4_fchown_async`, `nfs4_utime_async`, `nfs4_utimes_async_internal`, `nfs4_lockf_async`, and `nfs4_fcntl_async`.

Important operation builders include `nfs4_op_putrootfh`, `nfs4_op_putfh`, `nfs4_op_lookup`, `nfs4_op_getattr`, `nfs4_op_getfh`, `nfs4_op_open_confirm`, `nfs4_op_close`, `nfs4_op_commit`, `nfs4_op_access`, `nfs4_op_create`, `nfs4_op_remove`, `nfs4_op_rename`, `nfs4_op_link`, `nfs4_op_read`, `nfs4_op_write`, `nfs4_op_readdir`, `nfs4_op_truncate`, `nfs4_op_chmod`, `nfs4_op_chown`, `nfs4_op_utimes`, `nfs4_op_lock`, `nfs4_op_locku`, and `nfs4_op_lockt`. Parsing helpers include `nfs_parse_attributes`, `nfs_parse_rwmax`, `nfs_parse_statvfs`, `nfs_parse_statvfs64`, `nfs_get_ugid`, and endian helpers `nfs_hton64`, `nfs_ntoh64`, and `nfs_pntoh64`.

## Control Flow

Most path-based operations allocate `nfs4_cb_data`, resolve the caller path with `nfs4_resolve_path`, optionally split the final component with `data_split_path`, configure `filler.func` and `filler.max_op`, then call `nfs4_lookup_path_async`. That common lookup path builds a COMPOUND request in `nfs4_allocate_op`, queues it through `rpc_nfs4_compound_task`, and routes the result through `nfs4_lookup_path_1_cb`. Successful lookup invokes the operation-specific continuation callback; `NFS4ERR_SYMLINK` or final symlink detection triggers a `READLINK` compound and retries with a rewritten path.

Mount flow is a multi-step chain: connect to port 2049 or configured port, send `SETCLIENTID`, send `SETCLIENTID_CONFIRM`, lookup the export and capture its root filehandle, fetch `FATTR4_MAXREAD` and `FATTR4_MAXWRITE`, then restore the runtime resiliency settings selected by mount options. This stores `server`, `export`, `clientid`, `setclientid_confirm`, root filehandle, and read/write max values in `nfs->nfsi`.

Open flow performs access check, `OPEN`, and `GETFH` as a compound after parent lookup. `nfs4_open_cb` verifies supported access, allocates `struct nfsfh`, copies the returned filehandle and stateid, initializes open seqid and flags such as sync, append, and readonly, and optionally performs `OPEN_CONFIRM`. `O_TRUNC` and `O_EXCL` install continuation callbacks that issue follow-up `SETATTR` requests for size or mode. A final-component symlink returned by `OPEN` is retried through `nfs4_open_readlink` unless `O_NOFOLLOW` is set.

Read and write flow uses direct filehandles rather than path lookup. `nfs4_pread_async_internal` and `nfs4_preadv_async_internal` send `PUTFH` plus `READ` using zero-copy aware RPC read helpers; callbacks update `nfsfh->offset` when requested. `nfs4_write_async` either writes at the current offset or, for append handles, first fetches current size through `GETATTR`, then writes at EOF. Non-sync writes mark `fh->is_dirty`, and `nfs4_close_async` includes `COMMIT` before `CLOSE` when dirty.

Directory flow opens with lookup plus `GETFH` and `READDIR`. `nfs4_parse_readdir` converts linked `entry4` results to libnfs `nfsdirent` entries, records cookies, and repeats `READDIR` via `nfs4_opendir_continue` until EOF. Link and rename are two-phase flows that capture one parent or source filehandle, then switch `data->path` and `filler.data` to complete `LINK` or `RENAME` with `SAVEFH` and `PUTFH`.

## State and Persistence Behavior

The file has no file-backed persistence, but it mutates durable client-session and handle state. `nfs->nfsi` stores server/export strings, current working directory, NFSv4 root filehandle, client id, verifier, read/write limits, open owner counter, and lock owner state. `struct nfsfh` instances retain NFS filehandles, stateids, open and lock seqids, current offset, append/sync/readonly flags, and dirty-write status across async calls.

Transient state is owned by `nfs4_cb_data` and released by `free_nfs4_cb_data`, including path strings, filler data, and up to four blobs. Some callbacks intentionally transfer ownership by nulling a blob before invoking the application callback, for example returning an opened `nfsfh`, `nfsdir`, or readlink target. With multithreading enabled, open/close/truncate paths serialize around `nfs4_open_call_mutex`, and open owner allocation uses `nfs4_open_counter_mutex`.

## Dependencies and Integration Points

Direct dependencies include generated NFSv4 ZDR types from `libnfs-raw-nfs4.h`, RPC task wrappers from `libnfs-raw.h`, public and private libnfs context definitions from `libnfs.h` and `libnfs-private.h`, linked-list helpers, platform compatibility headers, and system headers for stat, statvfs, utime, passwd lookup, major/minor device extraction, and networking. It integrates upward with the libnfs async API and downward with `rpc_nfs4_compound_task`, `rpc_nfs4_compound_task2`, `rpc_nfs4_read_task`, `rpc_nfs4_readv_task`, and `rpc_nfs4_write_task`.

The attribute masks `standard_attributes`, `statvfs_attributes`, `getacl_attributes`, and `rwmax_attributes` define the NFSv4 attribute ordering assumed by the local parsers. This makes the operation builders and parsers tightly coupled: changing masks or server result order assumptions requires updating the corresponding decode routines.

## Risks and Edge Cases

The path lookup and symlink retry logic mutates path buffers in place and depends on correct ownership transfers between `path`, `filler.data`, and blobs. Bugs here can cause leaks, double frees, incorrect final-component handling, or infinite symlink retries if normalization does not collapse the rewritten path as expected. `LOOKUP_FLAG_NO_FOLLOW` and `O_NOFOLLOW` are handled in separate stat/readlink and open paths, so regressions can diverge between `lstat`-style calls and `open`.

Attribute parsing is position-based against the requested bitmap and uses manual buffer cursor arithmetic. The `CHECK_GETATTR_BUF_SPACE` macro catches short buffers, but parser correctness still depends on exact NFSv4 attribute order and byte order. UID/GID strings are converted either numerically or through `getpwnam`; nonnumeric names without passwd support become 65534.

NFSv4 state sequencing is fragile. `nfs_increment_seqid` intentionally skips increment for selected protocol errors, while open, close, lock, unlock, and confirm callbacks update different stateids. Retry, reconnect, or callback ordering bugs can leave the server and client with different seqid expectations. Dirty writes rely on close or fsync issuing `COMMIT`; an application that never closes or syncs a handle after unstable writes can leave server-side persistence dependent on server behavior.

There are several small implementation hazards: some allocation failures return `0` rather than `-1` in `nfs4_mknod_async`; `nfs4_populate_symlink` has an unreachable `return 1`; statvfs ignores its `path` argument and always queries the mounted root filehandle; append writes race with other clients because EOF is fetched before write; directory entries are pushed to the head, so returned order is reverse of server traversal; and several callbacks pass stack-local result structs to the application callback, so callbacks must consume synchronously as expected by libnfs conventions.

## Test Signals

Useful coverage includes mount handshake tests against NFSv4 servers with and without `OPEN_CONFIRM`; path normalization and symlink tests for intermediate symlinks, final symlinks, `NO_FOLLOW`, `O_NOFOLLOW`, relative paths, root paths, and split final components; stat/fstat/statvfs tests validating all parsed fields and short-attribute error handling; open/create/truncate/exclusive-mode tests that inspect server-side mode, size, stateid, and seqid behavior; read/write tests for offset updates, append behavior, sync versus unstable write plus commit, zero-length reads/writes, and server max read/write limits; directory tests spanning multi-page `READDIR` and EOF; rename/link tests across directories; lock and fcntl tests for `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, lock owner reuse, unlock stateid updates, and conflict cases; and sanitizer or fault-injection runs around allocation failures and callback cancellation/timeouts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/nfs_v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/pdu.c -->
# sources/user-network-fs/libnfs/lib/pdu.c

## Purpose

`sources/user-network-fs/libnfs/lib/pdu.c` implements ONC RPC PDU lifecycle management for libnfs. It owns RPC queue primitives, PDU allocation and freeing, XID assignment and lookup, timeout stamping, send queueing over TCP, UDP, broadcast, server, TLS-start, and GSS-authenticated modes, reply decoding, server-side call dispatch, reply construction, cancellation, and top-level PDU processing. The source was read as a complete 1335-line file for this report.

## Important APIs, Types, and Functions

Queue utilities are `rpc_reset_queue`, `rpc_enqueue`, `rpc_return_to_outqueue`, `rpc_remove_pdu_from_queue`, and the mutex-wrapped `rpc_remove_pdu_from_queue_unlocked`. XID and lookup utilities are `rpc_hash_xid`, `rpc_set_next_xid`, `rpc_find_pdu`, and `rpc_cancel_pdu`.

Allocation and lifecycle APIs are `rpc_allocate_pdu2`, `rpc_allocate_pdu`, internal `rpc_allocate_reply_pdu`, and `rpc_free_pdu`. `rpc_allocate_pdu2` creates client call PDUs with a marshaling buffer, optional decode buffer area, iovec storage, record-marker slot, RPC header, auth credentials, optional AUTH_TLS flagging, and optional GSS credential/verifier state. `rpc_allocate_reply_pdu` builds server reply PDUs. `rpc_free_pdu` releases decoded ZDR payloads, GSS output buffers, ZDR state, iovectors, cursor buffers, and the PDU itself.

Send and receive APIs are `pdu_set_timeout`, `rpc_queue_pdu`, `rpc_process_pdu`, internal `rpc_process_reply`, and internal `rpc_process_call`. Server reply helpers are `rpc_send_reply`, `rpc_send_error_reply`, `rpc_copy_deferred_call`, and `rpc_free_deferred_call`.

## Control Flow

Client request flow starts with `rpc_allocate_pdu2`, which assigns an XID under `rpc_mutex` when multithreading is enabled, initializes the RPC call header, chooses auth flavor, creates the ZDR encoder, marshals the call message, and adds iovectors for the record marker and encoded header. Callers marshal procedure-specific payload after allocation, then `rpc_queue_pdu` finalizes GSS integrity or privacy wrapping if needed, computes the TCP record marker, stamps enqueue statistics and timeouts, and sends or queues based on transport.

For normal TCP clients, `rpc_queue_pdu` appends the PDU to `rpc->outqueue` and kicks `rpc_write_to_socket` if it is at the head. UDP, broadcast, server-context UDP, and AUTH_TLS NULL RPC paths send immediately or enqueue into `waitpdu` before direct `sendto` or `writev`. Transmitted UDP-like requests are tracked in a hash bucket keyed by XID so later replies can locate the PDU.

Reply flow enters `rpc_process_pdu`. Server contexts decode CALL messages through `rpc_process_call`; client contexts decode replies through `rpc_process_reply`. `rpc_process_reply` maps accepted RPC statuses to libnfs callback statuses, verifies TLS STARTTLS responses when expected, processes GSS verifier and privacy/integrity details, handles zero-copy read completion requirements, updates PDU statistics, and invokes the PDU callback with decoded data or an error string. For zero-copy reads, `pdu->in.base` can defer final completion until the remaining payload is read into caller buffers.

Server call flow decodes an RPC CALL into `_rpc_msg`, finds a registered endpoint by program and version, dispatches a matching procedure after decoding its arguments into endpoint-provided storage, or sends protocol-correct accepted error replies for program unavailable, version mismatch, procedure unavailable, or garbage arguments.

## State and Persistence Behavior

This file maintains in-memory RPC transport state only. Persistent fields include `rpc->xid`, `rpc->outqueue`, hashed `rpc->waitpdu` queues and `waitpdu_len`, `rpc->pdu`, transport mode flags, resiliency timeout fields, server endpoint registrations, authentication state, GSS sequence numbers/context, last successful response time, and statistics callbacks. Individual `rpc_pdu` objects persist across send, wait, retransmit, response decode, callback, and free; they store XID, callbacks, ZDR encoders/decoders, iovec cursors, retry flags, timeout timestamps, read cursors, authentication metadata, and stats.

`rpc_return_to_outqueue` supports retransmission by reinserting a previously transmitted PDU near the front of the output queue, incrementing retransmit statistics, resetting output progress, and resetting the input cursor. `pdu_set_timeout` writes absolute per-PDU timeout and major-timeout deadlines, respecting disabled timeout mode and coarser fallback clocks.

## Dependencies and Integration Points

Direct dependencies include `libnfs-zdr.h` for XDR-like encoding and decoding, public and private libnfs RPC structures, `slist.h`, socket headers, `sys/uio.h` for `writev`, platform compatibility headers, optional `krb5-wrapper.h`, optional TLS constants, and private cursor/iovector helpers such as `rpc_add_iovector`, `rpc_free_iovector`, `rpc_reset_cursor`, and `rpc_free_cursor`.

The file is a central integration point between higher-level NFS/MOUNT/NLM task builders and the socket service layer. Higher layers allocate PDUs, marshal procedure payloads, and receive callbacks. The socket layer drains `outqueue`, fills `rpc->pdu` and fragment buffers, and calls `rpc_process_pdu`. Server mode integrates with registered `rpc_endpoint` procedure tables.

## Risks and Edge Cases

Queue invariants are critical: queues are singly linked with explicit head and tail pointers, and incorrect removal or requeueing can lose PDUs, corrupt wait buckets, or break retransmission. `rpc_return_to_outqueue` intentionally avoids replacing a potentially half-sent head PDU, so changes to socket write progress must preserve this assumption.

Authentication and transport special cases add risk. GSS integrity and privacy rewrite encoded payloads late in `rpc_queue_pdu`; buffer sizing, sequence numbers, verifier validation, and zero-copy read handling must remain consistent. AUTH_TLS NULL RPCs are sent inline and expect a specific STARTTLS verifier; failures must stop the session rather than allowing queued RPCs onto an insecure transport. UDP broadcast keeps PDUs in wait queues differently from normal unicast, so removal conditions must be tested separately.

Memory ownership is split between the PDU allocation block, embedded decode buffer, dynamically allocated iovec arrays, ZDR-allocated decoded payloads, GSS buffers, and zero-copy input cursors. Error paths generally free the PDU immediately, so callers must not reuse a PDU after `rpc_queue_pdu` failure. In `rpc_allocate_pdu2`, failure after dynamic `out.iov` allocation jumps to `failed2` and frees the PDU without `rpc_free_iovector`, so this path relies on allocation layout assumptions and is worth leak testing.

Reply processing invokes callbacks with decoded storage owned by the PDU. Callbacks must finish using that storage before the PDU is freed by the surrounding RPC service lifecycle. Bad or malicious RPC replies can exercise decode errors, rejected messages, unknown accept statuses, GSS verifier failures, and size mismatches in zero-copy paths.

## Test Signals

Useful tests include queue unit tests for empty, singleton, head, middle, tail, missing removal, and requeue-after-head cases; deterministic XID hashing and cancellation tests; TCP send tests that verify record marker size, iovec accounting, and immediate write triggering for head PDUs; UDP, broadcast, and server-context send tests; timeout tests with disabled timeout, initial timeout, repeated timeout, major timeout, and fallback clock behavior; reply decode tests for success, rejected messages, all mapped accept errors, decode failure, and callback status/data; server dispatch tests for program unavailable, version mismatch, proc unavailable, garbage args, and successful procedure dispatch; GSS mode tests for krb5, krb5i, krb5p sequence/verifier/wrap behavior; AUTH_TLS NULL RPC tests for correct STARTTLS verifier and failure cases; zero-copy read tests for delayed completion and KRB5P copyout; and leak/fault-injection tests for every allocation and send failure path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/pdu.c -->
