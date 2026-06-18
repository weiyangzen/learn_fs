# subset-b-009702 research

This grouped report covers the requested NFS-Ganesha worker, 9P protocol, NFS/MOUNT protocol, and build manifest files. Each section is source-path aligned and delimited for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_worker_thread.c -->
## sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_worker_thread.c

Purpose: this file is the central ONC RPC dispatch lane for NFS-Ganesha. It defines `nfs_function_desc_t` descriptor tables for NFSv3, NFSv4, MOUNT, NLM, RQUOTA, and NFSACL procedures and uses those descriptors to select XDR decode/encode functions, service functions, cleanup functions, and dispatch behavior flags.

Important APIs and control flow: `nfs_rpc_valid_NFS`, `nfs_rpc_valid_MNT`, `nfs_rpc_valid_NLM`, `nfs_rpc_valid_RQUOTA`, `nfs_rpc_valid_NFSACL`, and `nfs_rpc_valid_NFS_RDMA` validate program/version/procedure and call `nfs_rpc_process_request`. The request pipeline authenticates with `svc_auth_authenticate`, decodes via descriptor XDR hooks, initializes `op_ctx`, resolves clients/exports, starts duplicate-request cache handling, enforces export access/security/transport/privileged-port/read-write policy, calls the protocol service function, sends replies through `complete_request`, and releases args/context through `free_args`. Async and duplicate paths are handled by `nfs_rpc_complete_async_request`, `drc_resume`, and `process_dupreq`.

State and integration: persistent runtime state is external: duplicate request cache entries, export/client references, per-thread `op_ctx`, request stats, tracepoints, metrics, and transport lifecycle. The file integrates tightly with ntirpc `SVCXPRT`, GSS/RPCSEC auth, HAProxy address validation, FSAL export permissions, server stats, LTTng tracepoints, and NFS metrics.

Risks and test signals: this is high-blast-radius dispatcher code. Bugs in cleanup can leave stale `op_ctx`, leaked client/export refs, duplicate-request cache corruption, or dropped replies. Important tests are duplicate replay/suspend/resume, GSS no-dispatch handling, RDMA policy rejection, export permission matrix, read-only/metadata-only behavior, and per-program invalid version/procedure errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_worker_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_attach.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_attach.c

Purpose: implements `_9p_attach`, binding a client fid to an export root or requested attach path/tag for 9P2000.L.

APIs and flow: it parses tag, fid, afid, username/aname, and numeric uid, validates fid bounds, resolves the export by tag, pseudo path, or real path, installs it in `op_ctx`, enforces `EXPORT_OPTION_9P` and privileged-port policy, allocates a `_9p_fid`, resolves user credentials by uid or name, looks up the root object, allocates embedded `STATE_TYPE_9P_FID` state, initializes qid fields, and replies with `RATTACH`.

State/dependencies: creates connection-persistent fid state in `req9p->pconn->fids[]`, holds export/object references, records credential/group data, and relies on `export_mgr`, `nfs_exports`, FSAL lookup/root APIs, and `_9p_proto_tools` credential helpers.

Risks/tests: error cleanup must release partially initialized op context, fids, exports, credentials, and object handles. Test attach by tag/path/pseudo, invalid fid, missing export, non-9P export, unprivileged client ports, uid/name credential failure, and root lookup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_auth.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_auth.c

Purpose: handles `TAUTH` parsing for 9P but deliberately does not implement authentication fids.

APIs and flow: `_9p_auth` decodes tag, afid, uname, aname, and numeric user field, logs the request, validates that `afid` is within `_9P_FID_PER_CONN`, then returns `EOPNOTSUPP` via `_9p_rerror`.

State/dependencies: it does not create fid state or touch FSAL. It depends only on 9P wire helpers and the common error response path.

Risks/tests: clients must be prepared to continue with unauthenticated `TATTACH` credential handling. Test signals are correct `ERANGE` for out-of-range afid and `EOPNOTSUPP` for otherwise valid requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_clunk.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_clunk.c

Purpose: implements `_9p_clunk`, releasing a fid and any associated open state or pending xattr write.

APIs and flow: the handler parses tag/fid, validates the fid table entry, initializes op context from the fid, calls `_9p_tools_clunk`, clears the connection fid slot, and replies with `RCLUNK` or `RERROR`.

State/dependencies: `_9p_tools_clunk` owns most persistence effects: closing open regular files, releasing active parent refs, committing deferred xattr content, releasing group/export/credential/object refs, and freeing the fid. Dependencies are `_9p_proto_tools`, FSAL close/xattr APIs, and op context.

Risks/tests: clunk is the finalizer for many 9P resources, so regressions leak fids or lose deferred xattrs. Test invalid fid, open file close, xattr size mismatch, xattr set failure, and repeated clunk/connection cleanup interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_clunk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush.c

Purpose: implements `TFLUSH`, coordinating cancellation ordering for earlier 9P requests on the same connection.

APIs and flow: `_9p_flush` parses tag and oldtag, calls `_9p_FlushFlushHook` with the connection and current request sequence, and always returns `RFLUSH` after the hook has synchronized with the target request if found.

State/dependencies: it depends on the flush hook subsystem in `9p_flush_hook.c`, especially per-connection flush buckets and request sequence numbers. It does not touch FSAL or fid state directly.

Risks/tests: correctness depends on not replying before an older matching request has finished. Test flush for missing oldtag, active oldtag, newer same tag, and concurrent request completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush_hook.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush_hook.c

Purpose: provides the synchronization machinery behind 9P `TFLUSH`.

APIs and flow: `_9p_AddFlushHook` inserts a request hook into a tag-hash bucket; `_9p_FlushFlushHook` finds an older hook with the target tag, attaches a stack-local condition object, removes the hook, waits for request completion, then returns to let `RFLUSH` be sent; `_9p_DiscardFlushHook` removes the hook or signals the waiting flusher once the request reply path has completed.

State/dependencies: state lives in `struct _9p_conn` flush buckets guarded by pthread mutexes and glists. The flush condition is transient but shared between the flushing thread and request-completion thread while the bucket lock coordinates lifetime.

Risks/tests: concurrency risks include missed signals, stack condition lifetime, hook deletion races, and tag modulo bucket correctness. Stress tests should cover simultaneous flushes, request completion during wait setup, and same tag with sequence ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush_hook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_fsync.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_fsync.c

Purpose: implements 9P `TFSYNC` by committing cached file data through FSAL.

APIs and flow: `_9p_fsync` decodes tag/fid, validates the fid, initializes op context, calls `fsal_commit(pfid->pentry, 0, 0)` to commit the whole file, maps FSAL errors through `_9p_tools_errno`, and returns `RFSYNC`.

State/dependencies: it does not mutate fid structure except through any FSAL-side persistence. It depends on valid fid object handles and FSAL commit semantics where count zero means whole file.

Risks/tests: test unopened vs open regular files, directory/object fsync behavior according to FSAL, FSAL retry/error mapping, and invalid fid handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getattr.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getattr.c

Purpose: implements `TGETATTR`, translating FSAL attributes into 9P2000.L stat fields.

APIs and flow: `_9p_getattr` parses fid and request mask, gets `ATTRS_NFS3` attributes through `obj_ops->getattrs`, computes the returned valid mask and selected fields, maps FSAL object type to POSIX mode bits, fills qid, ownership, size, block, and timestamp fields, and returns `RGETATTR`.

State/dependencies: read-only operation over fid/object/export state. It depends on FSAL attr preparation/release and uses export filesystem id for `rdev`, while birth time, generation, and data version are stubbed as zero.

Risks/tests: test per-bit mask behavior, type-to-mode mapping, timestamp precision, attr release on error, and unsupported/stubbed attributes expected by Linux 9p clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getlock.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getlock.c

Purpose: parses `TGETLOCK` but currently acts as a placeholder.

APIs and flow: `_9p_getlock` decodes fid, lock type, range, proc id, and client id, validates fid bounds, then echoes the request lock fields in `RGETLOCK` without consulting state or FSAL locks.

State/dependencies: no persistent lock state is read or updated, and the actual fid lookup is commented out. It depends only on wire helpers and common error formatting.

Risks/tests: this is behaviorally incomplete for clients expecting fcntl-style conflict discovery. Tests should document the echo behavior and cover invalid fid; functional lock conflict tests should fail or be marked unsupported until implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_interpreter.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_interpreter.c

Purpose: dispatches 9P messages from decoded connection buffers to individual handlers.

APIs and flow: `_9pfuncdesc` maps 9P opcodes to handlers and names. `_9p_process_buffer` reads message length/type, bounds checks opcode, sets max reply length to negotiated `msize`, calls the service handler, records 9P stats, and releases op context. `_9p_tcp_process_request` wraps processing and sends replies with `tcp_conn_send`, which serializes socket writes and records transport stats. `_9p_not_2000L` returns `ENOTSUP` for unsupported legacy 9P2000 operations.

State/dependencies: uses per-request `_9p_request_data`, per-connection `msize`, socket lock, flush hook cleanup, server stats, and common op context lifecycle.

Risks/tests: opcode table holes, incorrect max reply sizing, socket short writes, and forgotten op context release are core risks. Test all known opcodes, unsupported opcodes, small msize, concurrent TCP replies, and stats accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_interpreter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lcreate.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lcreate.c

Purpose: implements 9P2000.L file create-and-open.

APIs and flow: `_9p_lcreate` validates a directory fid, checks write export permissions, copies the child name, translates Linux open flags to FSAL flags/share access, prepares mode/group/optional truncate attributes, selects `FSAL_EXCLUSIVE_9P` for exclusive creates, calls `fsal_open2`, releases attrs, replaces the fid's object with the new file, sets qid, marks `opens = 1`, holds an active parent reference, and returns qid/iounit.

State/dependencies: mutates the existing fid from directory to opened file, owns FSAL state and parent refs, and depends on FSAL open/create semantics.

Risks/tests: failure after parent ref/object replacement would be dangerous, so the code orders irreversible updates after successful FSAL calls. Test guarded/exclusive/truncate flags, long names, read-only exports, parent reference balancing, and close-on-clunk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lcreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_link.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_link.c

Purpose: implements hard-link creation.

APIs and flow: `_9p_link` parses directory fid, target fid, and link name; validates both fids; initializes op context from the destination directory; enforces write access and same-export constraints; copies the link name; calls `fsal_link(target, dir, name)`; and returns `RLINK`.

State/dependencies: no fid mutation occurs, but filesystem namespace state changes through FSAL. It depends on export ids to reject cross-export links and on FSAL link semantics for permissions and link counts.

Risks/tests: test cross-export `EXDEV`, long names, read-only exports, invalid target/dfid, link to directories if FSAL forbids it, and post-link attribute/cache consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lock.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lock.c

Purpose: implements 9P byte-range locking over Ganesha state management.

APIs and flow: `_9p_lock` parses fid, lock type, flags, byte range, proc id, and client id. It resolves the client id through `getaddrinfo`, obtains a 9P state owner with `get_9p_owner`, handles read/write locks under grace and object state lock, verifies open mode with `status2`, calls `state_lock`, maps conflicts to `_9P_LOCK_BLOCKED`, and unlocks through `state_unlock`.

State/dependencies: uses fid embedded `state_t`, Ganesha state owner/lock tables, NFS grace tracking, and FSAL open status. The `flags` field is logged but blocking behavior is effectively nonblocking.

Risks/tests: array indexing in debug strings assumes valid lock type before switch, DNS/client-id parsing can fail, and blocking lock semantics are incomplete. Test lock type validation, grace behavior, wrong open modes, conflicts, unlock ranges, and client owner reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lopen.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lopen.c

Purpose: opens an existing fid using 9P2000.L open flags.

APIs and flow: `_9p_lopen` validates fid, translates flags to FSAL open flags and share access, initializes op context, optionally adds truncation, calls `fsal_reopen2` for regular files, increments `pfid->opens`, holds an active parent reference, and returns qid/iounit.

State/dependencies: mutates fid open count and embedded FSAL state. Non-regular objects return success without FSAL open, relying on object type semantics elsewhere.

Risks/tests: open count/ref balancing with repeated opens and clunk is important. Test read/write/truncate modes, regular vs directory/special files, FSAL reopen failure, stats with later read/write, and parent ref release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mkdir.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mkdir.c

Purpose: implements `TMKDIR`.

APIs and flow: `_9p_mkdir` validates parent fid, initializes op context, enforces write access, copies the name, prepares mode attributes, calls `fsal_create` with `DIRECTORY`, releases attrs, drops the returned object reference, builds a directory qid from fileid, and returns `RMKDIR`.

State/dependencies: changes namespace through FSAL but does not allocate a new fid. The gid request field is parsed and logged but not applied.

Risks/tests: test mode application, ignored gid behavior, long names, read-only exports, parent not directory, existing names, and returned qid validity after the object ref is released.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mknod.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mknod.c

Purpose: implements special-file creation for `TMKNOD`.

APIs and flow: `_9p_mknod` validates parent fid/write access/name, maps mode bits to FSAL object type, prepares rawdev and mode attributes, calls `fsal_create`, releases attrs and the returned object ref, then returns a qid.

State/dependencies: changes namespace through FSAL. The gid is parsed but ignored. The qid path is initialized from a local `fileid` variable that remains zero rather than the created object's fileid, which is a notable correctness risk.

Risks/tests: test block/char/fifo/socket creation, invalid mode, rawdev fields, ignored gid, qid path correctness, long names, read-only exports, and FSAL support for special files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_proto_tools.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_proto_tools.c

Purpose: shared 9P support routines for credentials, op context setup, FSAL error/open-flag translation, fid finalization, and connection cleanup.

APIs and flow: `_9p_init_opctx` installs fid export and credentials into `op_ctx`; `_9p_release_opctx` releases them. `_9p_tools_get_req_context_by_uid` and `_9p_tools_get_req_context_by_name` map users through `uid2grp`/`uname2grp`. `_9p_tools_errno` maps FSAL status to errno. `_9p_openflags2FSAL` and `_9p_tools_clunk` handle flag translation and fid close/free behavior. `_9p_cleanup_fids` walks all connection fids during teardown.

State/dependencies: owns `_9p_user_cred` refcounts, fid embedded state cleanup, xattr finalization, group-data refs, export refs, object refs, and active open parent refs. Dependencies include idmapper, uid2grp, export manager, FSAL convert, and common memory helpers.

Risks/tests: this file is the resource-lifetime hub. Test fid cleanup under partial attach, xattr write commit/mismatch, multiple opens, credential refcounts, export switching assertions, and connection teardown with many fids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_proto_tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read.c

Purpose: implements file and xattr reads.

APIs and flow: `_9p_read` validates fid and negotiated `msize`, initializes op context, starts building `RREAD`, and either copies from cached xattr content or prepares a one-iovec `fsal_io_arg` and calls `fsal_read`. It records I/O stats when a client object is available and returns actual byte count.

State/dependencies: reads from fid object state or xattr cache. Uses request cond/mutex in `async_process_data`, FSAL read completion, client manager, and server stats.

Risks/tests: test `msize` enforcement, xattr offset bounds/read-only mode, partial reads, EOF, FSAL async/sync return behavior, stats byte accounting, and reading without prior open if client permits it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read_conf.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read_conf.c

Purpose: declares configurable 9P protocol parameters.

APIs and flow: defines global `_9p_param`, `_9p_params` config items for worker count, TCP/RDMA ports, msize, backlog, and RDMA pool sizes, plus `_9p_param_blk` for the `_9P` config stanza with DBus interface metadata and `noop_conf_commit`.

State/dependencies: persists configuration into `_9p_param` during config parsing. Depends on `config_parsing.h`, `gsh_config.h`, and constants in `9p.h`.

Risks/tests: test min/max validation, default values, singleton block enforcement, DBus/config reload behavior, and that negotiated msize defaults align with runtime buffer sizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readdir.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readdir.c

Purpose: implements directory enumeration for 9P.

APIs and flow: `_9p_readdir` validates fid/msize/count, initializes op context, emits synthetic `.` and `..` entries for offsets 0/1, converts cookies, then calls `fsal_readdir` with `_9p_readdir_callback`. The callback maps FSAL object types to 9P qid type and VFS `d_type`, stops before the reply buffer limit, and encodes directory entries.

State/dependencies: read-only over directory object state, but uses FSAL lookup-parent refs and readdir cookies. Reply size accounting is local to `_9p_cb_data`.

Risks/tests: test small count handling, dot/dotdot offsets, cookie continuation, buffer-full truncation, unknown object types, parent lookup failure, and consistency of returned dcount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readlink.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readlink.c

Purpose: implements symlink target retrieval.

APIs and flow: `_9p_readlink` validates fid, initializes op context, calls `fsal_readlink`, encodes the returned UTF-8 string in `RREADLINK`, frees the FSAL-allocated string, and maps FSAL errors to errno.

State/dependencies: read-only over object state and depends on FSAL readlink allocation semantics.

Risks/tests: test invalid fid, non-symlink FSAL errors, long link targets vs msize, memory free on success, and no leak on error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_remove.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_remove.c

Purpose: implements legacy `TREMOVE`, removing the object named by a fid and clunking that fid.

APIs and flow: `_9p_remove` validates fid, initializes op context, checks write access, calls `fsal_remove(pfid->ppentry, pfid->name)`, closes open regular files if needed, frees the fid through a local macro that clears `pentry` and the connection slot, and replies `RREMOVE`.

State/dependencies: mutates namespace, closes file state, and releases fid resources. It relies on `ppentry` and `name` having been set by walk/create flows.

Risks/tests: test removing open files, directories vs files, missing parent/name, close failure after remove, read-only exports, invalid fid, and double-release safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rename.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rename.c

Purpose: implements fid-based rename.

APIs and flow: `_9p_rename` validates source fid and destination directory fid, initializes context from the source, checks write access and same-export constraints, copies the new name, calls `fsal_rename(pfid->ppentry, pfid->name, pdfid->pentry, newname)`, and returns `RRENAME`.

State/dependencies: changes namespace while keeping fid object handles unchanged. Depends on valid parent/name metadata from earlier walk and FSAL rename semantics.

Risks/tests: test cross-export `EXDEV`, stale `pfid->name`, renaming open files, overwrite behavior, long names, read-only exports, and cache consistency after rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_renameat.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_renameat.c

Purpose: implements directory/name based `TRENAMEAT`.

APIs and flow: `_9p_renameat` validates old and new directory fids, initializes context from the old directory, enforces same-export and write-access checks, copies old/new names, calls `fsal_rename(old_dir, oldname, new_dir, newname)`, and replies `RRENAMEAT`.

State/dependencies: namespace mutation through FSAL without fid mutation. It depends on valid directory fids and export ids.

Risks/tests: test source/destination in same directory and different directories, cross-export failure, long old/new names, overwrite cases, read-only exports, invalid fids, and directory rename constraints.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_renameat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rerror.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rerror.c

Purpose: common 9P error response encoder.

APIs and flow: `_9p_rerror` builds `RERROR`, writes the request tag and errno value, finalizes/checks reply length, maps the original request opcode to a function name for logging, and returns success to the transport layer so the error reply is sent.

State/dependencies: no persistent state beyond reply buffer mutation. It depends on `_9pfuncdesc` for log names and 9P wire macros.

Risks/tests: if `msgtag` is invalid or unavailable, error replies can carry the wrong tag. Test all handlers' error paths, unsupported opcodes, bounds behavior, and errno/log message mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_setattr.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_setattr.c

Purpose: implements 9P attribute updates.

APIs and flow: `_9p_setattr` parses valid mask and attribute payload, validates fid/write access, optionally gets current time for non-explicit time updates, populates `fsal_attrlist` for mode/owner/group/size/atime/mtime/ctime, calls `fsal_setattr(pfid->pentry, false, pfid->state, &fsalattr)`, releases attrs, and replies `RSETATTR`.

State/dependencies: mutates object metadata through FSAL and may use fid open state. Depends on write export permission and FSAL attr masks.

Risks/tests: test all mask combinations, explicit vs server-current timestamps, truncation through size, owner/group permission/squash behavior, read-only exports, invalid fid, and unsupported ctime updates by FSAL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_setattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_statfs.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_statfs.c

Purpose: implements filesystem statistics for 9P.

APIs and flow: `_9p_statfs` validates fid, initializes op context, gets object attrs, calls `fsal_statfs`, maps dynamic byte/file counts and rawdev major into the 9P `RSTATFS` payload, and returns constant magic/type, block size, and name length values.

State/dependencies: read-only over object/export state. It depends on FSAL attr/statfs APIs and attr release discipline.

Risks/tests: block size is hard-coded to one while byte counts come from FSAL, so client interpretation should be tested. Cover invalid fid, statfs failure, attr failure, large count encoding, and msize bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_symlink.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_symlink.c

Purpose: implements symbolic link creation.

APIs and flow: `_9p_symlink` parses parent fid, name, link target, and gid, validates fid/write access/name, allocates a NUL-terminated target string, prepares mode 0777 attrs, calls `fsal_create(... SYMBOLIC_LINK ...)`, releases attrs and target buffer, drops the returned object ref, builds a symlink qid, and replies `RSYMLINK`.

State/dependencies: namespace mutation through FSAL; gid is parsed but not used. Depends on FSAL symlink create behavior and memory allocation helpers.

Risks/tests: test long names and link targets, read-only exports, ignored gid expectations, FSAL failure with non-null object, qid path correctness after put_ref, and target NUL termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_unlinkat.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_unlinkat.c

Purpose: implements name-based unlink relative to a directory fid.

APIs and flow: `_9p_unlinkat` parses directory fid, name, and unused flags, validates fid, initializes context, checks write access, copies the name, calls `fsal_remove(pdfid->pentry, name)`, and returns `RUNLINKAT`.

State/dependencies: namespace mutation through FSAL, no fid cleanup. Flags are currently ignored.

Risks/tests: test file vs directory removal semantics, ignored flags such as remove-directory intent, long names, read-only exports, invalid directory fid, FSAL error mapping, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_unlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_version.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_version.c

Purpose: negotiates 9P protocol version and message size.

APIs and flow: `_9p_version` parses tag, requested msize, and version string; accepts strings matching `9P2000.L`; clamps requested msize to the connection maximum or lowers connection msize; rejects values under 512; and returns `RVERSION` with the accepted values.

State/dependencies: mutates `req9p->pconn->msize`, which later handlers use for reply and I/O bounds. Depends on string comparison and wire helpers.

Risks/tests: test exact and longer/shorter version strings, too-small msize, client-requested shrink, server-side cap, and all later handlers respecting negotiated msize.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_walk.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_walk.c

Purpose: implements fid cloning and path walking.

APIs and flow: `_9p_walk` validates source/new fids, initializes context, allocates a new fid, either clones the source fid for zero components or iteratively `fsal_lookup`s path components, tracks parent/name for later rename/remove, sets qid type/path, allocates embedded 9P state, stores the new fid in the connection table, increments group/user/export/object/parent refs, and returns qids.

State/dependencies: creates persistent fid state and FSAL object references. Depends on `uid2grp`, FSAL lookup, export refs, and `alloc_state`.

Risks/tests: multi-component replies currently return the final qid for every component. Clone path copies the full fid before allocating new state, so refcount and pointer ownership require careful testing. Cover partial lookup failure cleanup, newfid collision, long names, multi-component qids, and clunk ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_walk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_write.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_write.c

Purpose: implements file and deferred-xattr writes.

APIs and flow: `_9p_write` parses fid, offset, count, and data pointer; validates fid and negotiated `msize`; initializes op context; checks write access; writes into cached xattr content when `pfid->xattr` is active, otherwise prepares a one-iovec `fsal_io_arg` and calls `fsal_write`; records I/O stats; and returns `RWRITE` with actual bytes written.

State/dependencies: mutates file contents or fid xattr buffer. Xattr content is committed later on clunk. Depends on FSAL write, server stats, and write export permissions.

Risks/tests: xattr path increments offset by requested size rather than actual clipped size and has TODO gap detection. Test partial writes, offset gaps, msize limits, read-only exports, FSAL errors, xattr finalization, and stable-write expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrcreate.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrcreate.c

Purpose: prepares a fid for extended-attribute creation/replacement/removal.

APIs and flow: `_9p_xattrcreate` validates fid, max xattr size, write access, and name length. Size zero maps to `remove_extattr_by_name`. Nonzero size allocates a fid xattr buffer, records expected size/name/write mode, optionally skips initial creation for POSIX ACL or overlong copied name, otherwise calls `setextattr_value` with create/replace semantics and retry-on-exists behavior for flag zero.

State/dependencies: stores deferred xattr content in `pfid->xattr`; actual final value is written during clunk after client writes the payload. Depends on FSAL xattr APIs and POSIX xattr flags.

Risks/tests: test create/replace/exclusive flags, size limit, remove path, POSIX ACL special case, write then clunk, size mismatch, and cleanup on FSAL create failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrcreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrwalk.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrwalk.c

Purpose: creates a read-only xattr fid either for listing attributes or reading one attribute.

APIs and flow: `_9p_xattrwalk` validates source and attr fids, copies the source fid minus state pointer, initializes op context, allocates xattr buffer, and either lists attributes into a NUL-separated buffer or reads a named xattr, retrying with a larger allocation on `ERANGE`. It stores the attr fid in the connection table, increments object/group/export/credential/parent refs, and returns the xattr size.

State/dependencies: creates persistent attrfid state with read-only cached xattr content. Depends on FSAL list/get xattr operations, fixed list array of 100 entries, and `_9P_XATTR_MAX_SIZE`.

Risks/tests: test list overflow, more than 100 xattrs, large xattr reallocation, `ENOATTR` mapping, attrfid collision, ref balancing on errors, and reading from the attrfid through `_9p_read`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrwalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/CMakeLists.txt

Purpose: builds the 9P protocol implementation as an object library.

APIs and flow: `9p_STAT_SRCS` enumerates all 9P interpreter, helper, config, protocol operation, xattr, I/O, and error source files. `add_library(9p OBJECT ...)` creates the object target, `add_sanitizers(9p)` applies sanitizer settings, and compile flags force `-fPIC`. When `USE_LTTNG` is enabled it depends on generated trace headers and includes generated file properties.

State/dependencies: build-time dependency surface for every 9P source in this subset; included only by parent CMake when `USE_9P` is set.

Risks/tests: missing a new handler here causes link/dispatch failures even if opcode table is updated. Test configure/build with `USE_9P` on/off, sanitizer builds, and LTTng-enabled builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/9P/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/CMakeLists.txt

Purpose: top-level protocol subdirectory selector.

APIs and flow: always adds `NFS` and `XDR`, conditionally adds `NLM`, `RQUOTA`, `NFSACL`, and `9P` based on CMake options such as `USE_NLM`, `USE_RQUOTA`, `USE_NFSACL3`, and `USE_9P`.

State/dependencies: build configuration controls which protocol object libraries are available to the final server. No runtime state.

Risks/tests: option mismatches can leave descriptor tables compiled for protocols whose implementation objects are absent, or vice versa. Test all supported protocol option combinations, especially `USE_9P` and `USE_NFS3` interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/CMakeLists.txt

Purpose: builds the core NFS protocol object libraries.

APIs and flow: `nfsproto_STAT_SRCS` always includes NFSv4 compound/op handlers and common protocol helpers. When `USE_NFS3` is enabled it appends MOUNT procedures and NFSv3 handlers such as access, commit, create, fsinfo, read/write, readdir, link, rename, and setattr. It creates `nfsproto` and `nfs4callbacks` object libraries with sanitizer and `-fPIC` settings, plus optional LTTng generated-header dependency.

State/dependencies: build-time source manifest backing descriptor tables in `nfs_worker_thread.c`. No runtime persistence.

Risks/tests: missing handlers under `USE_NFS3` break descriptor references. Test builds with and without NFSv3, NFSv4 callbacks, sanitizer settings, and LTTng enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/maketest.conf -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/maketest.conf

Purpose: defines a mount protocol test harness rule.

APIs and flow: `Test mount_protocol` runs architecture-specific `test_mntproto`, expects stdout markers for `test_mnt_Null : OK` and `test_mnt_Export : OK`, and defines failure classifications for missing markers, generic `ERROR`, and nonzero exit status.

State/dependencies: external test runner configuration only; depends on command path conventions and stdout strings emitted by the mount protocol test binary.

Risks/tests: brittle string matching can miss changed test output or overmatch unrelated `ERROR`. Use it as a signal that MOUNT null/export basics still work, not as coverage for `mnt_Mnt` access and auth-flavor behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/maketest.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Dump.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Dump.c

Purpose: implements MOUNT protocol `DUMP`.

APIs and flow: `mnt_Dump` logs the request and returns a null mount list because Ganesha does not maintain/support the historical mount list. `mnt_Dump_Free` is a no-op.

State/dependencies: no persistent mount list state is read or written. It depends only on NFS/MOUNT result structures and logging.

Risks/tests: clients expecting mount-list introspection always see empty data. Test XDR encoding of null list and compatibility with MOUNT v1/v3 descriptor tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Export.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Export.c

Purpose: implements MOUNT `EXPORT`, returning exports visible to the caller.

APIs and flow: `mnt_Export` iterates all exports with `foreach_gsh_export`. `proc_export` sets each export in `op_ctx`, runs `export_check_access`, filters out inaccessible or non-NFSv3 exports, builds an `exportnode`, copies client group strings from export-specific clients or global export options under locks, selects pseudo or full path, and links nodes into the result list. `mnt_Export_Free` frees nested group nodes and path refstrings.

State/dependencies: reads export manager state, export permissions, client lists, and op context. Allocates response-owned linked lists.

Risks/tests: lock/ref ordering and cleanup are key. Test export visibility by client, pseudo vs path mode, empty client list fallback, memory cleanup, and concurrent export updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Mnt.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Mnt.c

Purpose: implements MOUNT v3 `MNT`, returning an NFSv3 file handle and supported authentication flavors for an export path/tag.

APIs and flow: `mnt_Mnt` rejects unsupported MOUNT versions, normalizes a trailing slash, resolves the export by tag/pseudo/path, installs it in `op_ctx`, checks NFSv3 and access permissions, resolves the requested object through export root or `fsal_lookup_path`, converts it to an NFSv3 handle with `nfs3_FSALToFhandle`, builds auth flavor list from export security options, and returns status. `mnt3_Mnt_Free` releases allocated auth flavor array and file handle storage on success.

State/dependencies: reads export/client/security state and returns heap-owned XDR fields. Depends on FSAL lookup/root and file-handle conversion.

Risks/tests: test tag/path/pseudo resolution, access denial, auth flavor ordering, handle allocation/freeing, unsupported v1 mount, null path drop, and client UDP/TCP differences noted in comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Mnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Null.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Null.c

Purpose: implements MOUNT `NULL` health/no-op procedure.

APIs and flow: `mnt_Null` logs and returns `MNT3_OK`; `mnt_Null_Free` is a no-op.

State/dependencies: no state or FSAL dependencies.

Risks/tests: minimal. Test that descriptor XDR void in/out paths dispatch and reply successfully for MOUNT v1/v3.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Umnt.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Umnt.c

Purpose: implements MOUNT `UMNT`.

APIs and flow: `mnt_Umnt` logs the path argument and returns success without removing any mount-list entry because Ganesha does not maintain a mount list. Free function is a no-op.

State/dependencies: no persistent mount state exists here.

Risks/tests: clients expecting server-side mount list updates receive success but no state change. Test null/normal path logging and XDR void response behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_Umnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_UmntAll.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_UmntAll.c

Purpose: implements MOUNT `UMNTALL`.

APIs and flow: `mnt_UmntAll` logs and returns `NFS_REQ_OK`; `mnt_UmntAll_Free` is a no-op. It does not walk or clear any mount list.

State/dependencies: no persistent mount list state.

Risks/tests: behavior is intentionally a no-op. Test descriptor dispatch and successful void reply for MOUNT versions that include this procedure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/mnt_UmntAll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_access.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_access.c

Purpose: implements NFSv3 `ACCESS`.

APIs and flow: `nfs3_access` converts the file handle to an FSAL/cache object with `nfs3_FhandleToCache`, calls `nfs_access_op` with the requested access mask, builds post-op attributes on success or access-denied, maps nonretryable errors to NFSv3 status, drops retryable errors, and releases the object ref. Free function is a no-op.

State/dependencies: read-only over object metadata and export permissions resolved by the dispatcher. Depends on NFSv3 handle conversion, FSAL access checks, and post-op attr helpers.

Risks/tests: test allowed/denied masks, stale/bad handles, retryable FSAL errors, attr-follow flags on failure, and squashed credential effects inherited from dispatcher.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_commit.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_commit.c

Purpose: implements NFSv3 `COMMIT`.

APIs and flow: `nfs3_commit` converts the file handle, calls `fsal_commit` with offset/count, drops retryable errors, maps nonretryable errors with weak cache consistency data, and on success returns WCC data plus `NFS3_write_verifier`. Free function is a no-op.

State/dependencies: flushes persistent storage through FSAL and reports verifier state. Depends on dispatcher write permissions, FSAL commit, WCC helpers, and global write verifier.

Risks/tests: test whole/partial commit ranges, FSAL retryable failures, verifier stability across server restart rules, WCC before/after data, and stale handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_create.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_create.c

Purpose: implements NFSv3 regular file `CREATE`.

APIs and flow: `nfs3_create` prepares result and attr structures, converts parent handle, captures pre-op parent attrs, verifies parent is a directory, checks inode quota, validates the filename, converts create attributes for guarded/unchecked modes, supplies default mode 0600 when absent, maps NFS create mode to FSAL mode, applies verifier for exclusive create, squashes requested owner/group if needed, calls stateless `fsal_open2` with read/write, builds a post-op file handle and attrs, sets WCC data, closes/releases the created object, and releases parent refs. `nfs3_create_free` frees the allocated handle on success.

State/dependencies: mutates namespace and uses FSAL create/open, quota, attr conversion, handle conversion, and WCC helpers.

Risks/tests: test guarded/exclusive/unchecked behavior, verifier semantics, quota denial, bad names, default mode, owner squash, handle allocation/freeing, retryable errors, and parent WCC consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsinfo.c -->
## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsinfo.c

Purpose: implements NFSv3 `FSINFO`.

APIs and flow: `nfs3_fsinfo` converts the root handle, calls `fsal_statfs` for time delta, fills read/write/readdir preferences from export atomics, gets max file size from FSAL export ops, sets static property flags for links/symlinks/homogeneous/cansettime, attaches post-op attrs, and returns `NFS3_OK`.

State/dependencies: read-only over export configuration and FSAL filesystem info. Depends on atomics in `gsh_export`, FSAL statfs/maxfilesize, and post-op attr helpers.

Risks/tests: there is a likely typo on statfs failure assigning `res_fsstat3.status` instead of `res_fsinfo3.status`. Test FSAL statfs failure, export preference values, maxfilesize propagation, property flags, stale handles, and post-op attrs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsinfo.c -->
