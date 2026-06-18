# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.c

## Purpose

`client.c` is the protocol/client xlator implementation for GlusterFS. It is the client-side bridge between the xlator FOP surface and the versioned RPC client programs negotiated during handshake. Most exported FOP callbacks are thin adapters: they validate that `this->private` and `conf->fops` exist, populate a `clnt_args_t`, invoke the appropriate `conf->fops->proctable[GF_FOP_*].fn`, and unwind with `ENOTCONN` or `EINVAL` if the request cannot be submitted.

## Important APIs, types, and functions

The main public xlator hooks are `init`, `fini`, `notify`, `reconfigure`, `mem_acct_init`, the `fops` table, `cbks`, `dumpops`, and `xlator_api`. `client_submit_request()` is the central RPC send helper. It XDR-serializes a request into an iobuf, merges request payload iobrefs, optionally rewrites supplemental groups when `send-gids` is disabled, and calls `rpc_clnt_submit()`. On local failure it synthesizes an RPC failure and invokes the callback.

`client_rpc_notify()` handles RPC connection events: `RPC_CLNT_CONNECT` starts `client_handshake()`, `RPC_CLNT_DISCONNECT` marks saved fds bad, emits child-down notifications, updates reconnect flags, and resets remote port state, while `RPC_CLNT_DESTROY` completes `fini` waiters. `client_notify_dispatch()` and `client_notify_dispatch_uniq()` serialize graph notification delivery through `ctx->notify_lock` and suppress duplicate child events. `client_filter_o_direct()` strips `O_DIRECT` when configured. `client_setxattr()` has special control paths for `CLIENT_CMD_CONNECT` and, for `replace-brick`, `CLIENT_CMD_DISCONNECT`.

The FOP callbacks cover lookup/stat/path operations, fd operations, xattrs, locks, dir reads, fallocate/discard/zerofill, compound, lease, active lock migration, `icreate`, `namelink`, `put`, and `copy_file_range`. The xlator options define transport, remote host/subvolume/port, timeouts, `filter-O_DIRECT`, `send-gids`, `event-threads`, `testing.old-protocol`, and `strict-locks`.

## Control flow

Initialization rejects children, warns on dangling parents, allocates `clnt_conf_t`, initializes locks/conditions and `saved_fds`, applies options through `build_client_config()`, creates the local mem pool, and calls `client_init_rpc()`. RPC initialization creates `rpc_clnt_new()`, registers `client_rpc_notify`, binds handshake/dump programs, and registers callback programs. Parent-up starts the RPC client; parent-down marks `parent_down`, disables RPC, and may mark the graph unused when all protocol/client children are down.

Every normal FOP follows the same path: caller enters the xlator FOP, the function builds `clnt_args_t`, a version-specific RPC stub sends via `client_submit_request()`, and the callback unwinds later. If no RPC proctable exists, the local callback unwinds immediately. Handshake and getspec are special because they use protocol-level handshake procedures while being exposed through xlator FOP slots.

## State and persistence behavior

Persistent runtime state lives in `clnt_conf_t`: RPC handle, selected programs, connection flags, saved fd list, event-thread count, reconnect state, option booleans, lock recovery lock, setvolume count, and fini condition state. Saved fd contexts are protected by `fd_lock`; disconnect sets all `remote_fd` values to `-1` so later fd operations know reopen is needed or invalid. `fini()` waits until the RPC destroy callback broadcasts `fini_complete_cond`, then destroys locks and frees the conf.

## Dependencies and integration points

This file depends on `rpc-clnt`, XDR helpers, iobuf/iobref, inode/fd/lock helpers, xlator defaults, graph notification synchronization, statedump, event thread reconfiguration, and versioned protocol client programs declared elsewhere. It integrates with server handshake through `clnt_handshake_prog`, with callback handling through `gluster_cbk_prog`, and with replace-brick through the special xattr command keys.

## Risks and test signals

High-risk areas are disconnect notification ordering, graph cleanup after child-down, fd reopen after reconnect, lock recovery under `strict-locks`, and option reconfiguration that changes remote host or subvolume. `client_submit_request()` must preserve callback unwinding on all local allocation/XDR failures. The `client_setxattr()` disconnect control path appears inverted: it treats nonzero `client_destroy_rpc()` as success, so replace-brick disconnect behavior deserves a focused regression check. Useful tests include mount/connect/disconnect loops, parent-down graph cleanup, fd reopen with held POSIX locks, `filter-O_DIRECT` open/read/write cases, `send-gids` on/off behavior, event-thread reconfiguration, getspec, and replace-brick connect/disconnect xattr commands.
