# Research: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server.h

Purpose:
This header defines the shared protocol/server translator data structures and public functions used by lifecycle, handshake, helpers, and FOP dispatch code.

Important APIs, types, and functions:
- `server_conf_t` is translator private state: RPC service, inode LRU limit, gid/auth settings, config paths, transport list, child status, event threads, mutexes, inode-table lock, and gid cache.
- `server_resolve_type_t` and `server_resolve_t` describe resolver semantics and one resolver target.
- `server_resume_fn_t` and `resolve_and_resume()` define the resolver-to-FOP continuation contract.
- `server_state_t` is the per-RPC carrier for locs, resolves, fds, payload/rsp vectors, iobrefs, offsets, modes, names, xattrs, flock/lease/lock-list, xdata, and subdir-mount client state.
- `server_ctx_t` stores per-client fdtable state.
- Public functions include `server_submit_reply()`, xattr command checkers, `forget_inode_if_no_dentry()`, `server_graph_janitor_threads()`, `server_ctx_get()`, and `server_cleanup()`.

Control flow and integration:
Actors populate `server_state_t`, call `resolve_and_resume()`, and resume functions wind into child FOPs. Callback code later calls `server_submit_reply()`, which frees the state. `server_conf_t` is stored in `xlator_t->private`, and client fdtable contexts are obtained with `server_ctx_get()`.

State and persistence behavior:
All state is in-memory. `server_conf_t` is long-lived per translator, `server_state_t` is per RPC, and `server_ctx_t` persists per client across fd-based operations.

Dependencies:
The header includes pthreads, RPC service definitions, protocol common definitions, server memory types, Gluster protocol types, client/gid-cache APIs, and authentication. It exposes global RPC program declarations.

Risks and edge cases:
`server_state_t` is broad and cleanup-sensitive. New fields must be audited against `free_state()`. Two-resolve operations must correctly populate both `resolve` and `resolve2`. `fd_out` for `copy_file_range` is a special case beyond the usual single-fd model.

Test signals:
Compile coverage should catch signature drift. Runtime tests should verify cleanup of all state fields, especially dict/xdata, locs, fds, iobrefs, leases/flocks/locklists, and two-resolve operations.
