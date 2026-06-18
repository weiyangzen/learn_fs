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
