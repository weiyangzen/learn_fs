# Research: subset-b-007128

Grouped research for GlusterFS protocol/client v2 common, handshake, helper, message, memory, and fop RPC files. Each section is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.c

## Purpose

`client-common.c` is the protocol/client v2 marshalling layer. It translates Gluster in-memory arguments (`loc_t`, `fd_t`, `dict_t`, `iatt`, `gf_flock`, `gf_lease`) into `gfx_*` XDR request structures before RPC submission, and translates `gfx_*` XDR responses back into callback-facing C structures and dictionaries. It is shared by `client-rpc-fops_v2.c` request and callback handlers.

## Important APIs, types, and functions

- `client_cmd_to_gf_cmd()` maps POSIX fcntl commands, including reserve-lock and fd-lock variants, to `GF_LK_*` protocol commands.
- `client_post_common_iatt()`, `client_post_common_2iatt()`, `client_post_common_3iatt()`, and `client_post_common_dict()` decode common response shapes and xdata dictionaries.
- `client_post_readv_v2()`, `client_post_create_v2()`, `client_post_lease_v2()`, `client_post_lk_v2()`, `client_post_readdir_v2()`, `client_post_readdirp_v2()`, and `client_post_rename_v2()` handle fop-specific response payloads.
- `client_pre_*_v2()` functions populate request structures for nearly every v2 fop: namespace ops, fd ops, xattr ops, locks, readdir, allocation/discard/zerofill, lease, put, seek, rchecksum, and copy-file-range.
- `CLIENT_GET_REMOTE_FD()` is used through `client_get_remote_fd()` for fd-based requests and selects either a real remote fd, anonymous fd fallback, or EBADFD failure.
- `set_fd_reopen_status()` writes `"fd-reopen-status"` into xdata and relaxes reopen restrictions when `conf->strict_locks` is disabled.

## Control flow

The request builders follow two patterns. Path-based builders validate `loc` and inode/parent availability, choose a gfid from inode when present or from `loc` fallback fields, assert non-null gfids, copy basename/linkname/flags/mode/offset fields, then serialize xdata with `dict_to_xdr()`. Fd-based builders call `CLIENT_GET_REMOTE_FD()` with either `DEFAULT_REMOTE_FD` or `FALLBACK_TO_ANON_FD`, copy the fd inode gfid, fill operation parameters, and serialize xdata.

The response helpers decode only when the server operation succeeded where data is meaningful. Stat-bearing responses copy `gfx_stat` fields with `gfx_stat_to_iattx()`. Dictionary responses call `xdr_to_dict()` for the main dict and xdata. Readdir responses delegate list materialization to helper functions in `client-helpers.c`. Readv binds the RPC response iobref and payload vector to callback output when `op_ret > 0`.

## State and persistence behavior

This file does not own durable state. It reads client configuration through `this->private` only for fd lookup and strict-lock reopen-status policy. It writes transient XDR buffers inside request structs, which callers must free after `client_submit_request()`. Its persistent effect is indirect: by embedding remote fd numbers, gfids, flags, lock data, and xdata in requests, it defines the on-wire state transitions seen by the server.

## Dependencies and integration points

The file depends on Gluster core structures and helpers from `client.h`, `glusterfs3.h`, dict XDR helpers, fd-context lookup through `CLIENT_GET_REMOTE_FD`, gfid utilities, protocol stat/flock/lease conversion helpers, and message IDs from `client-messages.h`. `client-rpc-fops_v2.c` calls these functions before submitting RPCs and after decoding callbacks.

## Risks and edge cases

- Many builders return negative errno values such as `-ESTALE`, `-EINVAL`, or `-EBADF`; callers must convert them correctly when unwinding.
- Null gfid assertions are common and can turn partially initialized `loc_t` or fd/inode state into request failure.
- Fd fallback to anonymous fd is intentionally selective and depends on lock state and strict-lock policy, so widening fallback can break lock correctness.
- `client_pre_writev_v2()` contains a conditional test-only path using `ret` under `GF_TESTING_IO_XDATA`; that configuration depends on external declarations/macros compiling cleanly.
- Several request structs keep borrowed string pointers (`loc->name`, xattr names, volume names); callers must not outlive the original frame data before serialization completes.
- `set_fd_reopen_status()` assumes non-null `xdata`; callers using it must allocate xdata on local error paths.

## Test signals

Good tests cover gfid source precedence for inode vs loc fallback, null-gfid rejection, each fd fallback mode under strict/non-strict locks, lock command/type conversion, xdata round trips, dict decode failure handling, readdir/readdirp decode, copy-file-range dual-fd handling, and `fd-reopen-status` behavior for write-lock vs read/unlock cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.h

## Purpose

`client-common.h` declares the protocol/client v2 marshalling and unmarshalling API. It is the contract between high-level client fop handlers in `client-rpc-fops_v2.c`, fd/reopen helpers, and the generated `gfx_*` XDR protocol types.

## Important APIs, types, and functions

- Common response decoders are declared for dictionary, one-iatt, two-iatt, three-iatt, and common response shapes.
- Request builders are declared for path-based fops (`stat`, `lookup`, `mknod`, `mkdir`, `rename`, `link`, xattrs, locks, lease, put) and fd-based fops (`readv`, `writev`, `flush`, `fsync`, `fstat`, `ftruncate`, fd locks, readdir, allocation, seek, copy-file-range).
- Post-decoders are declared for readv, create, lease, lk, readdir, readdirp, and rename.
- `set_fd_reopen_status()` is exported so lock callbacks and error paths can report whether an fd can be reopened after anonymous-fd fallback.

## Control flow

The header itself has no runtime control flow. Its shape shows the intended two-stage fop pipeline: a `client_pre_*_v2()` function prepares an XDR request, `client_submit_request()` sends it, and a callback decodes with either a common post helper or an fop-specific `client_post_*_v2()` function before `CLIENT_STACK_UNWIND()`.

## State and persistence behavior

The header defines no storage. Ownership conventions are implicit in the signatures: request builders fill caller-owned `gfx_*_req` structs and may allocate XDR dictionary buffers inside them; response decoders allocate or fill caller-owned output structures and pass dictionary references back through `dict_t **`.

## Dependencies and integration points

It includes `<glusterfs/dict.h>`, `glusterfs3.h`, and `client.h`, binding this API to Gluster dicts, protocol XDR structures, fop frame-local state, fd contexts, and `enum gf_fd_reopen_status`. It is included by `client-rpc-fops_v2.c`, `client-helpers.c`, and other client protocol files needing the v2 conversion API.

## Risks and edge cases

- The API surface is broad and manually kept in sync with `client-common.c`; prototype drift would be caught only by compilation.
- Several functions take mutable request structs plus borrowed pointers, so callers must respect the allocate-submit-free lifecycle.
- The distinction between `dict_t *xdata` and `dict_t **xdata` in request builders matters: writev/copy-file-range can mutate or allocate xdata in test paths, while most builders only serialize an existing dict.
- The header names these as "version 4" functions while symbols use `_v2`, reflecting Gluster protocol naming history that can confuse maintainers.

## Test signals

Build coverage with all fop handlers enabled is the primary interface test. Runtime tests should verify each declared pre/post helper is exercised through its corresponding actor in `clnt4_0_fop_actors`, with sanitizers or leak checks around XDR dictionary allocation/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-handshake.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-handshake.c

## Purpose

`client-handshake.c` implements connection negotiation for the protocol/client xlator. It discovers server-supported programs, optionally queries the portmapper for the brick port, sends `SETVOLUME`, records connection identity/version data, notifies parents of child status, and coordinates saved-fd reopening after reconnect.

## Important APIs, types, and functions

- `client_handshake()` starts negotiation by submitting a dump/version request through `conf->dump`.
- `client_dump_version_cbk()` decodes `gf_dump_rsp`, checks for portmap support, selects `clnt4_0_fop_prog`, then calls `client_setvolume()`.
- `select_server_supported_programs()` chooses the v2/4.x fop program and sets RPC auth to `AUTH_GLUSTERFS_v3`.
- `client_query_portmap()` and `client_query_portmap_cbk()` request a brick port from glusterd/portmap and reconfigure `conf->rpc`.
- `client_setvolume()` serializes the xlator options dict with fop/mgmt versions, process uuid, process name, client version, volume id, volfile metadata, subdir mount, lock version, and opversion.
- `client_setvolume_cbk()` handles authentication/volume errors, validates volume id, records `conf->child_up`, marks `conf->connected`, and calls `client_post_handshake()`.
- `client_post_handshake()`, `client_child_up_reopen_done()`, `client_reopen_done()`, and `client_attempt_reopen()` manage fd reopen gating and delayed `CHILD_UP` notification.
- `protocol_client_reopenfile_v2()` and `protocol_client_reopendir_v2()` resend open/opendir for saved fds.
- `clnt_handshake_prog`, `clnt_dump_prog`, and `clnt_pmap_prog` register RPC program metadata and procedure names.

## Control flow

The normal connection path is `client_handshake()` -> `client_dump_version_cbk()` -> `select_server_supported_programs()` -> `client_setvolume()` -> `client_setvolume_cbk()` -> `client_post_handshake()`. If the server advertises portmap, the dump callback sends `PORTBYBRICK`; the portmap callback reconfigures the RPC remote port, sets quick-reconnect flags, disconnects the current transport, and lets reconnect continue against the brick port.

After successful `SETVOLUME`, `client_post_handshake()` scans `conf->saved_fds` under `conf->fd_lock`. Fds with `remote_fd == -1` and no strict-lock-blocking lock context are moved to a temporary reopen list and assigned `client_child_up_reopen_done`. Parent `CHILD_UP` is delayed until all reopen callbacks decrement `conf->reopen_fd_count` to zero. If no eligible fd needs reopening, parents are notified immediately.

Single-fd lazy reopen is separate: fd-based fops can detect anonymous-fd fallback and later call `client_attempt_reopen()`. That function rate-limits by `CLIENT_REOPEN_MAX_ATTEMPTS`, marks the fdctx as in-progress by swapping `reopen_done`, removes it from `saved_fds`, and dispatches reopen.

## State and persistence behavior

State is held in `clnt_conf_t`: selected RPC programs, connection flags, `client_id`, `child_up`, `connected`, `quick_reconnect`, `skip_notify`, `portmap_err_logged`, `disconnect_err_logged`, `setvol_count`, `reopen_fd_count`, `saved_fds`, and the global volume id in `ctx->volume_id`. Fd reopen state is held in each `clnt_fd_ctx_t`: `remote_fd`, `reopen_done`, `released`, `reopen_attempts`, `is_dir`, `flags`, and `gfid`. The process uuid sent in `SETVOLUME` deliberately includes context id, graph id, pid, host, translator name, and reconnect counter so server-side resources are not reused across reconnects.

## Dependencies and integration points

This file depends on the RPC client, XDR types from `rpc-common-xdr.h`, `xdr-rpc.h`, `portmap-xdr.h`, protocol fop program from `client-rpc-fops_v2.c`, fd context helpers from `client-helpers.c`, event dispatch in `client.c`, dict serialization, graph/context options, and message IDs from `client-messages.h`. It integrates with parent translators through `GF_EVENT_CHILD_UP`, `GF_EVENT_CHILD_CONNECTING`, `GF_EVENT_AUTH_FAILED`, and `GF_EVENT_VOLFILE_MODIFIED`.

## Risks and edge cases

- `client_attempt_reopen()` reopens only when `reopen_attempts == CLIENT_REOPEN_MAX_ATTEMPTS`, incrementing otherwise; this is a deliberate delay/throttle but easy to misread as an off-by-one.
- Strict locks suppress fd reopen for fds with lock state, causing later fd operations to fail rather than silently use a reopened fd without recovered locks.
- If reopen submission fails, the code calls `fdctx->reopen_done()` with the prior remote fd value; child-up delay accounting still depends on the callback path completing.
- `client_setvolume_cbk()` treats auth failures and early subdir-mount ENOENT specially so mount startup can fail while background reconnect semantics continue for other errors.
- Volume-id mismatch is fatal for regular volumes but skipped for snapd, so tests must distinguish snapshot and non-snapshot remotes.
- Portmap callback always disconnects after reconfiguration; correctness depends on reconnect code honoring `quick_reconnect` and `skip_notify`.

## Test signals

Useful tests include server program selection, old-protocol behavior, portmap reconfiguration for TCP and RDMA brick names, SETVOLUME dict contents, auth failure and subdir-mount failure notification, volume-id mismatch, child_up false deferral, reconnect with zero saved fds, reconnect with multiple saved files/dirs, release racing with reopen, strict-lock reopen suppression, and lazy reopen after anonymous-fd fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-handshake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-helpers.c

## Purpose

`client-helpers.c` provides shared runtime helpers for the protocol/client xlator: fd-context lookup/set/delete, local frame cleanup, readdir/readdirp response materialization and cleanup, remote-fd selection, anonymous-fd reopen detection, active-lock migration serialization, and release-on-fd-context-destroy.

## Important APIs, types, and functions

- `client_fd_lk_list_empty()` safely checks whether an fd lock list is empty, optionally with try-lock semantics.
- `this_fd_get_ctx()`, `this_fd_del_ctx()`, and `this_fd_set_ctx()` wrap fd context APIs and log duplicate or failed context updates.
- `client_local_wipe()` releases the resources in `clnt_local_t`: locs, fd, iobref, name, and the pool object.
- `unserialize_rsp_dirent_v2()` and `unserialize_rsp_direntp_v2()` convert `gfx_dirlist`/`gfx_dirplist` replies into `gf_dirent_t` lists.
- `clnt_readdir_rsp_cleanup_v2()` and `clnt_readdirp_rsp_cleanup_v2()` free libc-allocated XDR list nodes and names.
- `client_get_remote_fd()` returns the usable remote fd for an fd-based request, respecting reopen-in-progress, anonymous fds, strict locks, and fallback flags.
- `client_is_reopen_needed()` and `client_fd_fop_prepare_local()` record whether a successful fd fop should trigger lazy reopen afterward.
- `clnt_unserialize_rsp_locklist_v2()`, `serialize_req_locklist_v2()`, `clnt_getactivelk_rsp_cleanup_v2()`, and `clnt_setactivelk_req_cleanup_v2()` handle lock migration lists.
- `client_fdctx_destroy()` and `send_release4_0_over_wire()` release remote fd state and submit `RELEASE` or `RELEASEDIR` when the parent is up.

## Control flow

Fd operations call `client_get_remote_fd()` under `conf->fd_lock`. If no fdctx exists and the fd is anonymous, it returns `GF_ANON_FD_NO`; if a fdctx exists but reopen is in progress, it returns `-1`; otherwise it returns `fdctx->remote_fd`. If the caller allows `FALLBACK_TO_ANON_FD`, remote fd `-1` is replaced with anonymous fd only when no locks are involved.

Readdir callbacks decode XDR list chains into Gluster dirents, transform offsets with `gf_itransform()` and `conf->client_id`, attach stats/dicts/inodes for readdirp, unwind to upper translators, then clean both the Gluster dirent list and RPC-allocated XDR chain.

Fd context destruction removes lock context references, checks `conf->parent_down`, creates a frame when release can be sent, submits the release request through the v2 fop program, and finally marks `remote_fd = -1` and frees the fdctx.

## State and persistence behavior

This file manipulates in-memory client state only. Fd contexts are attached to `fd_t` objects and linked in `conf->saved_fds` elsewhere; this file reads and deletes them, clears `lk_ctx`, and frees them. `client_local_wipe()` is the central ownership cleanup path used after `CLIENT_STACK_UNWIND`. Readdir offsets are transformed using the translator's client id but not persisted here. Active lock migration lists are heap-allocated request/response structures passed through callbacks.

## Dependencies and integration points

Dependencies include fd/inode/table APIs, Gluster list and dict utilities, XDR allocation conventions, iobuf/iobref references, fd lock contexts, `client-common.h` request/response types, `client-messages.h` IDs, `client_submit_request()`, and callback symbols from `client-rpc-fops_v2.c`. The helpers are invoked by request builders in `client-common.c`, fop actors/callbacks in `client-rpc-fops_v2.c`, and reconnect logic in `client-handshake.c`.

## Risks and edge cases

- `client_get_remote_fd()` must be called with `conf->fd_lock` only inside the function; callers must not inspect fdctx outside protected state unless they own the context.
- Anonymous fallback is unsafe when locks exist, so the lock-involved check is central to strict-lock correctness.
- `serialize_req_locklist_v2()` mutates `tmp->flock.l_type` while converting to protocol constants; callers should not expect the original POSIX lock type to remain unchanged.
- Readdirp creates new inodes when `inode_find()` misses; tests must account for inode table side effects.
- `client_fdctx_destroy()` skips release when `parent_down` is set, relying on server disconnect cleanup rather than explicit release.
- XDR list cleanup uses `free()` for rpc/libc allocations and `GF_FREE()` for Gluster allocations; mixing these would be a memory-management bug.

## Test signals

Tests should cover duplicate fdctx set logging, remote-fd lookup for normal/missing/reopening/anonymous fds, strict-lock fallback denial for write-like fops, local cleanup leak checks, readdir offset transformation, readdirp dict/inode creation, locklist serialize/unserialize including client_uid allocation failures, and release/releasedir behavior with parent up vs parent down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-mem-types.h

## Purpose

`client-mem-types.h` defines memory-accounting type IDs for allocations owned by the protocol/client xlator. These IDs let Gluster's memory accounting and statedump tooling attribute client configuration, request buffers, fd contexts, and lock migration request nodes to the client component.

## Important APIs, types, and functions

- `enum gf_client_mem_types_` starts at `gf_common_mt_end + 1` to avoid overlap with common allocation IDs.
- `gf_client_mt_clnt_conf_t` accounts `clnt_conf_t` allocations.
- `gf_client_mt_clnt_req_buf_t` accounts client request buffers.
- `gf_client_mt_clnt_fdctx_t` accounts `clnt_fd_ctx_t` allocations used for saved remote fd state.
- `gf_client_mt_clnt_lock_request_t` accounts serialized active-lock migration request list nodes.
- `gf_client_mt_end` marks the end of this component's memory type range.

## Control flow

The header has no runtime control flow. Its enum values are consumed by `GF_CALLOC`, `GF_MALLOC`, and related memory-accounted allocation calls in client implementation files.

## State and persistence behavior

There is no runtime state here. The enum values are stable process-local identifiers used by memory accounting; changing or reordering them affects diagnostics rather than on-disk data.

## Dependencies and integration points

The file includes `<glusterfs/mem-types.h>` for `gf_common_mt_end`. `client.h`, `client-rpc-fops_v2.c`, and helper code use these IDs when allocating fd contexts and lock request structures. Gluster memory accounting and statedump infrastructure consume the resulting allocation categories.

## Risks and edge cases

- New client allocation classes should be appended before `gf_client_mt_end`; inserting or reusing values can confuse memory diagnostics.
- If code allocates client-owned objects with common or wrong memory types, leak reports become less useful.
- The enum is tiny, so missing IDs may encourage overloading existing categories.

## Test signals

Compile coverage verifies enum visibility. Memory-accounting or statedump tests should show `clnt_fd_ctx_t` allocations under `gf_client_mt_clnt_fdctx_t` and active lock request nodes under `gf_client_mt_clnt_lock_request_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-messages.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-messages.h

## Purpose

`client-messages.h` centralizes log message IDs and common message strings for the protocol/client translator. It provides stable `PC_MSG_*` identifiers for structured logging across fop RPCs, fd/reopen handling, handshake, portmap, cache invalidation, leases, lock recovery, and lifecycle errors.

## Important APIs, types, and functions

- `GLFS_MSGID(PC, ...)` declares the client component message IDs. The comments require new IDs to be appended and never removed to avoid ID reuse.
- Message IDs cover timer events, fd context errors, XDR failures, remote operation failures, handshake/version/portmap failures, reconnect events, volume-id mismatch, auth failures, cache invalidation, lease failures, lock contention, reopen, memory allocation, and bad fds.
- `PC_MSG_*_STR` macros provide reusable human-readable text for many IDs, such as XDR decoding failure, failed fop send, child-up delay, SETVOLUME failure, port number errors, remote subvolume errors, strict client protocol violations, and unknown lock types.

## Control flow

The header has no executable flow. It shapes runtime logging by supplying IDs and string constants to `gf_smsg()`, `gf_msg()`, `gf_msg_debug()`, and related logging calls throughout the client xlator.

## State and persistence behavior

The message ID list is a compatibility surface for logs and tooling. It is not persisted as application state, but stable numeric IDs are important for log analysis, alerting, and documentation. The header explicitly forbids removing IDs even if unused.

## Dependencies and integration points

It includes `<glusterfs/glfs-message-id.h>` for `GLFS_MSGID`. The client implementation files include this header and pass IDs to Gluster logging. Downstream integrations include log parsers, support diagnostics, statedump analysis, and any tests that assert specific message IDs.

## Risks and edge cases

- Removing or reordering IDs can silently reuse numeric IDs for unrelated messages.
- Several string macros contain typos or legacy phrasing (`isze`, `Defering`, `reister`), but changing them may affect tests or operational log matching.
- Message macros do not enforce that callers provide the right contextual key/value pairs.
- Duplicated concepts exist across IDs and strings, so new logging should choose the closest existing ID before appending another one.

## Test signals

Build coverage catches missing IDs. Logging tests should verify representative failure paths emit the expected `PC_MSG_*` IDs: XDR decode failure, fop send failure, bad fd, SETVOLUME failure, auth failure, volume-id mismatch, portmap failure, child-up delay, and fd reopen failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-rpc-fops_v2.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-rpc-fops_v2.c

## Purpose

`client-rpc-fops_v2.c` is the GlusterFS protocol/client v2 fop implementation. It maps translator fop calls to `gfx_*` RPC requests, submits them through the selected fop program, decodes RPC callbacks, unwinds upper-stack callbacks, and maintains fd context state for open, create, opendir, release, reconnect, and anonymous-fd fallback behavior.

## Important APIs, types, and functions

- `client_is_setlk()` and `_copy_gfid_from_inode_holders()` support lock/reopen and fdctx setup.
- `client_add_fd_to_saved_fds()` creates `clnt_fd_ctx_t`, stores gfid/flags/remote fd/lock context, attaches it to `fd_t`, and links it into `conf->saved_fds`.
- `client4_0_*_cbk()` callbacks decode RPC results, translate response payloads with `client_post_*_v2()` helpers, log failures, and call `CLIENT_STACK_UNWIND()`.
- `client4_0_*()` actor functions build requests with `client_pre_*_v2()` helpers, allocate `clnt_local_t` when callbacks need context, attach payload/iobuf state for read/write/readdir/lookup-with-content, call `client_submit_request()`, and free serialized XDR buffers.
- `client4_0_release()` and `client4_0_releasedir()` remove fd contexts and either destroy them immediately or mark them released while reopen is in progress.
- Lock-migration fops `client4_0_getactivelk()` and `client4_0_setactivelk()` exchange active lock lists for migration/heal.
- Internal/less common fops include `namelink`, `icreate`, `put`, `copy_file_range`, `lease`, `seek`, `ipc`, `zerofill`, `discard`, `fallocate`, and `rchecksum`.
- `clnt4_0_fop_names`, `clnt4_0_fop_actors`, and `clnt4_0_fop_prog` register procedure names, actor dispatch, program number, protocol version, and procedure count.

## Control flow

For most fops, the actor validates `frame`, `this`, and `data`, extracts `clnt_args_t`, prepares a `gfx_*_req` via `client_pre_*_v2()`, submits it with `client_submit_request(this, &req, frame, conf->fops, GFS3_OP_*, callback, payload, xdrproc)`, frees XDR dict buffers, and returns. On local preparation failure it immediately unwinds with `CLIENT_STACK_UNWIND()` using the local errno.

Callbacks follow a mirrored pattern: if `req->rpc_status == -1`, synthesize `ENOTCONN`; otherwise decode the response with `xdr_to_generic()`. Successful responses are converted into `iatt`, dict, fd, lease, lock, dirent, iobuf, or locklist outputs. The callback logs selected errors with `PC_MSG_REMOTE_OP_FAILED` or more specific message IDs, unwinds the stack, and releases decoded dictionaries or RPC-allocated buffers.

Open/create/opendir callbacks are special: on success they call `client_add_fd_to_saved_fds()` so the remote fd can be reused and reopened after reconnect. Release/releasedir are also special: they remove the fdctx from the fd, and if no reopen is active they call `client_fdctx_destroy()` to send a release over the wire.

Fd-based data ops use `client_fd_fop_prepare_local()` after request preparation. If the request used anonymous fd fallback because a saved fd was stale and lock-safe, successful callbacks call `client_attempt_reopen()` to lazily restore a real remote fd.

## State and persistence behavior

The file owns several important in-memory state transitions. `client_add_fd_to_saved_fds()` allocates fd contexts with `gf_client_mt_clnt_fdctx_t`, refs the fd lock context, links into `conf->saved_fds`, and attaches the context to `fd_t`. Request actors store transient state in `clnt_local_t`: locs for logging/unwind, fd refs, output fd for copy-file-range, payload iobrefs, lock owner, command, xattr name, and reopen flags. The fop tables are static program registration state used by RPC dispatch.

No on-disk persistence occurs here. Persistence-like behavior is remote/server state: remote fd numbers, locks, file data changes, xattrs, directory entries, leases, and active lock lists are created or changed by submitted RPCs.

## Dependencies and integration points

The file depends on `client.h` for `clnt_conf_t`, `clnt_local_t`, macros, fdctx helpers, and `client_submit_request()`, on `client-common.h` for v2 pre/post marshalling, on generated `glusterfs3.h`/`gfx_*` XDR structures, on iobuf/iobref payload APIs, dict APIs, inode/loc/fd APIs, lock owner and flock conversion helpers, and message IDs from `client-messages.h`. It is selected during handshake through `clnt4_0_fop_prog` and invoked by the translator fop dispatch layer.

## Risks and edge cases

- Request actors free serialized dict buffers after submission; any submit path that does not synchronously copy encoded data would create use-after-free risk, so this relies on `client_submit_request()`/RPC semantics.
- Many callbacks continue after decode failures with synthetic errors; missing cleanup of partially decoded libc-allocated fields can leak if new response types are added.
- `client4_0_readdir()` sets `local->cmd = remote_fd` before `remote_fd` is populated, so its error log can report `-1` rather than the actual fd.
- `client4_0_getactivelk_cbk()` declares `lock_migration_info_t locklist` and initializes it only after successful decode; if `rpc_status` or decode fails, the unwind receives an uninitialized stack object pointer.
- `client4_0_put()` does not free serialized `req.xattr`/`req.xdata` buffers in the success path visible here, unlike most other actors; this deserves leak-focused review against the exact XDR helper behavior.
- Lock reopen status is subtle: `lk` callbacks may add `"fd-reopen-status"` based on returned lock type, and local EBADF paths may synthesize `FD_BAD`.
- Saved fd release races with reopen are handled by `fdctx->released`, but future edits must preserve the lock ordering around `conf->fd_lock`.
- Some errors are intentionally logged at debug or suppressed for common cases (`ENOENT`, `ESTALE`, `ENOTSUP`, `EAGAIN`), so tests should not assert uniform warning logs.

## Test signals

High-value tests include every actor's local validation unwind, XDR decode failure callbacks, rpc-status `ENOTCONN`, open/create/opendir fdctx creation, release during and outside reopen, readv iobuf sizing and oversized read rejection, readdir/readdirp large-response iobuf path, lookup gfid mismatch setting `"gfid-changed"`, xattr op_ret normalization to zero, fd anonymous fallback followed by lazy reopen for read/write/fxattrop/finodelk/copy-file-range, strict-lock `lk` reopen-status behavior, get/set active lock list migration, and program table coverage for all supported `GF_FOP_*` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-rpc-fops_v2.c -->
