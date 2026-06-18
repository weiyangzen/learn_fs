# subset-b-007129 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.h

## Purpose

`client.h` defines the protocol/client xlator's shared state, request argument containers, fd context, payload wrapper, helper macros, and exported helper prototypes used by `client.c` and the version-specific client RPC implementation files.

## Important APIs, types, and functions

The core type is `clnt_conf_t`, which owns the RPC client, option values, RPC timeout config, saved fd list, locks, negotiated RPC program pointers, connection and notification flags, reconnect counters, and lifecycle condition variables. `clnt_fd_ctx_t` tracks a local fd's remote fd number, directory/released flags, open flags, lock context, gfid, reopen callback, and reopen attempts. `clnt_local_t` is per-call local state with locs, fd references, iobref, lock owner/cmd data, lock recovery list, and reopen attempt flags. `clnt_args_t` is the broad argument carrier used by FOP adapters and versioned RPC stubs; it can represent loc, fd, fd_out, iovec payload, xattrs, iatts, locks, names, offsets, modes, flags, xdata, and active lock migration lists. `client_payload_t` wraps iobrefs and request/response iovec payload arrays for `client_submit_request()`.

The important macros are `CLIENT_GET_REMOTE_FD`, which centralizes remote-fd lookup and EBADFD handling, `CLIENT_STACK_UNWIND`, which unwinds and wipes `clnt_local_t`, and `CLIENT_POST_FOP`, which maps common compound responses into callback argument storage. The header declares fd context helpers, local cleanup, request submission, fd reopen/recovery helpers, dirent and locklist serialization helpers, notification dispatchers, and lock command translation functions.

## Control flow

The header encodes the contract between generic FOP dispatch and version-specific protocol code. Generic FOPs fill `clnt_args_t`; RPC implementations use remote fd helpers, allocate `clnt_local_t`, submit requests, and unwind using the macros. Reconnect flow is represented by saved fd contexts, `client_is_reopen_needed()`, `client_attempt_reopen()`, and lock recovery helpers.

## State and persistence behavior

The state is in-memory only and tied to a live xlator instance. `saved_fds` preserves fd metadata across disconnect/reconnect attempts, including lock contexts. `setvol_count`, `reopen_fd_count`, `last_sent_event`, and logging booleans are process-lifetime counters/flags. There is no durable persistence; correctness depends on reconstructing state from fd contexts, locks, and handshake after connection loss.

## Dependencies and integration points

The header depends on GlusterFS RPC client interfaces, list primitives, defaults, dict/xlator/fd/lock types through included headers, and generated protocol/XDR types referenced by cleanup/serialization prototypes. Versioned protocol client files include this header to share state and helper contracts with `client.c`.

## Risks and test signals

Because `clnt_args_t` is a wide loosely typed carrier, mismatching fields to FOPs is easy and can produce protocol bugs that compile cleanly. `CLIENT_STACK_UNWIND` requires frame-local ownership discipline. Saved fd and lock recovery state is protected by a spinlock in some paths and lock contexts in others, so reconnect tests should cover concurrent fd operations, release/releasedir, lock migration, `copy_file_range` dual-fd paths, and anonymous-fd fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/Makefile.am

## Purpose

This top-level automake fragment for `xlators/protocol/server` declares only `SUBDIRS = src`, delegating all build content to the `src` directory.

## Important APIs, types, and functions

There are no C APIs or functions in this file. Its only build API is the recursive automake directory declaration.

## Control flow

During an automake build, entering this directory recurses into `src`, where the server xlator shared object, sources, headers, compiler flags, and install locations are defined.

## State and persistence behavior

No runtime state or persistence exists here. Build state is limited to automake's recursive traversal.

## Dependencies and integration points

This file integrates with the parent automake tree and the child `src/Makefile.am`. Removing or changing `SUBDIRS` would disconnect the protocol/server implementation from recursive builds.

## Risks and test signals

The main risk is accidental omission of the `src` subtree from builds. Test signal is simple: `make` from the parent should enter `xlators/protocol/server/src` and produce/install `server.la` when server support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/Makefile.am

## Purpose

This automake file builds the protocol/server xlator module. It declares `server.la` conditionally under `WITH_SERVER`, lists source and installed header files, and wires library and include dependencies needed for the server-side RPC protocol implementation.

## Important APIs, types, and functions

The module sources are `server.c`, `server-resolve.c`, `server-helpers.c`, `server-handshake.c`, `authenticate.c`, `server-common.c`, and `server-rpc-fops_v2.c`. Installed headers are `server.h`, `server-helpers.h`, `server-mem-types.h`, `authenticate.h`, `server-messages.h`, and `server-common.h`. Link inputs are libglusterfs, gfrpc, gfxdr, and `LIB_DL`, the last of which is required by dynamic authentication module loading in `authenticate.c`.

## Control flow

When `WITH_SERVER` is true, automake builds `server.la` as a module using `-module` and GlusterFS's default xlator LDFLAGS. Compile flags define `CONFDIR`, `LIBDIR` for authentication modules, and `DATADIR`, and add include paths for libglusterfs, socket transport, protocol lib, rpc-lib, XDR build/source trees, and glusterfsd.

## State and persistence behavior

There is no runtime state here, but the compile-time `LIBDIR` constant determines where `authenticate.c` looks for auth modules at runtime. The install paths place the xlator under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/protocol` and headers under `$(includedir)/glusterfs/server`.

## Dependencies and integration points

The file connects protocol/server to GlusterFS's core library, RPC stack, generated XDR code, dynamic loader, and socket transport. It is also the source of truth for which server implementation files are compiled into the module.

## Risks and test signals

Risks include missing `LIB_DL`, stale source/header lists, incorrect generated-XDR include paths, and mismatched `LIBDIR` causing authentication modules to fail at runtime. Build tests should check `WITH_SERVER` on/off, `make dist`, installation layout, and a runtime authentication module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.c

## Purpose

`authenticate.c` implements protocol/server authentication module lifecycle and evaluation. It dynamically loads configured auth modules from `LIBDIR`, records their `gf_auth` functions and optional volume option definitions, validates their options, runs all modules against a client handshake, and unloads modules during cleanup.

## Important APIs, types, and functions

`gf_auth_init(xlator_t *xl, dict_t *auth_modules)` iterates an auth-module dictionary through `init()`, then validates each module's options with `_gf_auth_option_validate()`. `init()` maps legacy `auth.ip` to `addr`, builds `LIBDIR/<key>.so`, opens it with `dlopen()`, resolves `gf_auth`, optionally resolves `options`, stores an `auth_handle_t` in the dictionary, and records errors through the caller-supplied integer. `gf_authenticate()` evaluates loaded modules using `gf_auth_one_method()`. It returns accept if at least one module accepts and none reject, rejects immediately on `AUTH_REJECT`, and rejects if every module returns `AUTH_DONT_CARE`. `gf_auth_fini()` closes loaded module handles.

## Control flow

During server initialization, configured auth keys are converted to loaded module handles. During `SETVOLUME`, server handshake passes client input params and volume config params to `gf_authenticate()`. Each module gets the same input/config dictionaries. A rejecting module terminates the loop; accepting modules set the result only if no earlier reject occurred; uninterested modules leave the result unchanged. If no module accepts, the connection is refused.

## State and persistence behavior

Loaded module state is stored in the `auth_modules` dict as dynamically allocated `auth_handle_t` values. The dynamic library handles stay open until `gf_auth_fini()`. Option validation state is also appended to the xlator's `volume_options` list, with duplicate `given_opt` pointers avoided by scanning the list.

## Dependencies and integration points

This file depends on `dlopen`, `dlsym`, `dlclose`, dict iteration, xlator option validation, GlusterFS allocation helpers, and message IDs from `server-messages.h`. It integrates directly with `server-handshake.c`, which calls `auth_set_username_passwd()` first and then `gf_authenticate()`.

## Risks and test signals

Authentication is sensitive to module path correctness, dictionary key names, and module return semantics. A malformed module without `gf_auth` causes init failure. If every module is uninterested, clients are rejected, which is secure but can surprise misconfigured volumes. Tests should cover legacy `auth.ip`, missing modules, missing `gf_auth`, option validation failure, accept/reject/dont-care combinations, `ssl-name` handling via params, and cleanup after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.h

## Purpose

`authenticate.h` declares the protocol/server authentication interface and the runtime handle used for dynamically loaded auth modules.

## Important APIs, types, and functions

`auth_result_t` has three possible outcomes: `AUTH_ACCEPT`, `AUTH_REJECT`, and `AUTH_DONT_CARE`. `auth_fn_t` is the module function signature, taking client input params and server config params. `auth_handle_t` stores the dynamic library handle, resolved `authenticate` function, and optional `given_opt` volume option array. The exported functions are `gf_auth_init()`, `gf_auth_fini()`, and `gf_authenticate()`.

## Control flow

The header defines the contract modules must satisfy: an auth shared object must expose `gf_auth` with the `auth_fn_t` signature and may expose `options` for validation. Server initialization loads modules and handshake calls the authenticate function set.

## State and persistence behavior

The only state shape declared here is `auth_handle_t`; actual ownership is in the auth modules dictionary managed by `authenticate.c`.

## Dependencies and integration points

The header includes dict, compat, list, xlator, stdio, and fnmatch related headers. It is consumed by `authenticate.c` and `server-handshake.c`.

## Risks and test signals

The ABI between auth modules and server is string/symbol based, so symbol names and function signatures must remain stable. Tests should compile a minimal auth module, validate `options`, and run `gf_authenticate()` against all three return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.c

## Purpose

`server-common.c` contains response post-processing helpers for the version 4 server protocol path. These functions translate backend callback results into generated `gfx_*` RPC response structures and keep server-side inode/fd tables synchronized with successful namespace and fd operations.

## Important APIs, types, and functions

The helpers include simple translators such as `server4_post_readlink()`, `server4_post_statfs()`, `server4_post_readv()`, `server4_post_seek()`, `server4_post_lease()`, and `server4_post_rchecksum()`. Metadata helpers `server4_post_common_iatt()`, `server4_post_common_2iatt()`, `server4_post_common_3iatt()`, and `server4_post_common_3iatt_noinode()` serialize iatts and optionally link inodes. Directory helpers delegate to `serialize_rsp_dirent_v2()` and `serialize_rsp_direntp_v2()`. Namespace-mutating helpers update the inode table: `server4_post_entry_remove()` unlinks and forgets, `server4_post_rename()` handles destination replacement and `inode_rename()`, `server4_post_lookup()` links looked-up inodes and handles namespace marker xdata, and `server4_post_link()` links hardlinks. `server4_post_open()` and `server4_post_create()` bind fds and allocate server-side fd numbers in the per-client `server_ctx_t` fdtable.

## Control flow

Version-specific FOP callbacks call these helpers after successful backend operations and before `server_submit_reply()`. The helpers perform protocol conversion with `gfx_stat_from_iattx()`, `gf_statfs_from_statfs()`, `gf_proto_flock_from_flock()`, and related conversion routines. Open/create helpers obtain `server_ctx_get(frame->root->client, this)` and allocate remote fd numbers using `gf_fd_unused_get()`.

## State and persistence behavior

The file mutates in-memory inode and fd state. Successful create/link/lookup/rename/remove operations update the server inode table so later client GFID/name resolution can be cache-assisted. Open/create bind and reference fds, then store them in a per-client fdtable. Subdirectory mounts rewrite the apparent root gfid/inode number to the conventional root gfid for responses to the client.

## Dependencies and integration points

This file depends on generated `glusterfs3`/`glusterfs4` XDR types, inode/fd table APIs, `server_ctx_get()`, dirent serialization helpers, and server state from `server.h`. It is integrated by `server-rpc-fops_v2.c` callback paths.

## Risks and test signals

The riskiest behavior is inode table correctness after rename, create, link, lookup, and remove, especially destination replacement and subdir-mount root rewriting. Fd reference and fdtable allocation must stay balanced with release/cleanup paths. Tests should cover create/open remote fd allocation, rename over existing entries, directory unlink forget behavior, subdir mounts reporting root gfid as `000...001`, readdir/readdirp serialization cleanup, and lock type conversion in `server4_post_lk()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.h

## Purpose

`server-common.h` declares the version 4 response post-processing helpers implemented in `server-common.c`.

## Important APIs, types, and functions

The declarations cover response fill helpers for readlink, statfs, locks, directory reads, checksums, rename, open, read, create, common iatt response shapes, entry removal, lookup, link, lease, and no-inode variants. These functions operate on generated `gfx_*` response structs, `server_state_t`, `call_frame_t`, `xlator_t`, inode/fd objects, iatts, statvfs, dirent lists, flock/lease structures, and xdata dictionaries.

## Control flow

Server RPC FOP callback implementations include this header and call the relevant `server4_post_*()` helper just before serializing a response. The header separates protocol response shaping from the large generated FOP request/response logic.

## State and persistence behavior

The header declares functions that may mutate inode links and fdtable state, but it owns no state itself.

## Dependencies and integration points

It includes `server.h`, `glusterfs3.h`, compatibility errno support, and server message IDs, with optional GNFS XDR support under `BUILD_GNFS`. It integrates `server-common.c` with versioned server RPC FOP files.

## Risks and test signals

The public helper signatures must remain synchronized with generated XDR types and callback code. Compile failures are the first signal for signature drift. Runtime tests should exercise every helper indirectly through the corresponding FOP response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-handshake.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-handshake.c

## Purpose

`server-handshake.c` implements protocol/server handshake RPC procedures: getspec, setvolume, ping, and lock-version negotiation. The central responsibility is `SETVOLUME`, which binds a transport to a GlusterFS client object, validates the requested subvolume, authenticates the client, initializes inode tables, and performs the first lookup required before FOP processing can begin.

## Important APIs, types, and functions

`server_getspec()` optionally serves a volfile from `conf->volfile_dir`, rejects `../` in volid, reads `<volid>.vol`, and replies with `gf_getspec_rsp`. `server_setvolume()` decodes `gf_setvolume_req`, unserializes client parameters, validates `remote-subvolume`, finds the target xlator, checks graph cleanup and parent-up state, checks child-up status, validates process UUID and volume ID, creates or retrieves the `client_t`, sets login credentials and SSL name in params, checks FOP/MGMT versions, stores opversion, authenticates with `gf_authenticate()`, stores client options, binds `client->bound_xl`, creates an inode table if needed, sends server process UUID, dummy lock version, and transport pointer, then performs `server_first_lookup()`. `server_first_lookup()` does root lookup and, for subdir mounts, walks each path component through `do_path_lookup()` and stores `subdir_gfid`/`subdir_inode`. `server_ping()` replies success. `server_set_lk_version()` echoes the requested lock version. `gluster_handshake_prog` registers the actors.

## Control flow

A client connects at the RPC layer, then calls `SETVOLUME`. The server copies base options, locates the target brick xlator, rejects requests while the graph is not ready or cleanup is starting, populates a reply dict with child/volume/process metadata, authenticates, and only then allows the transport's `xl_private` to point at the client. On success, first lookup validates backend reachability and subdir-mount existence. The response is serialized into `gf_setvolume_rsp` and sent through `server_first_lookup_done()`.

## State and persistence behavior

Handshake mutates transport state (`req->trans->xl_private`, `clnt_options`), client state (`client_name`, `bound_xl`, `opversion`, subdir fields), peerinfo max op version in `conf->xprt_list`, and bound xlator inode table allocation. State is process-memory only but forms the active session identity for all future FOPs.

## Dependencies and integration points

This file depends on generated handshake XDR, dict serialization, auth modules, `auth_set_username_passwd()`, client table APIs, syncop lookup, inode APIs, graph locks, events, and server reply submission. It integrates with protocol/client `client_handshake()` and with all FOP handling because FOPs require a bound/authenticated client.

## Risks and test signals

High-risk areas include error-path cleanup, setting `xl_private` only for valid clients, subdir mount path walking, volume-ID mismatch, graph cleanup races, and authentication config copying. `gf_compare_client_version()` is currently a stub returning success, so version mismatch protection is incomplete. Tests should cover malformed XDR, missing `remote-subvolume`, missing child-up, wrong volume ID, auth reject, auth accept, missing auth modules, cleanup-starting races, subdir mount success/failure, getspec path traversal rejection, and lock-version/ping compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-handshake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.c

## Purpose

`server-helpers.c` provides shared server-side utility logic for request frame creation, credential/group handling, connection cleanup, tracing, response serialization cleanup, command xattr handling, per-client context allocation, login credential extraction, inode creation, and active-lock migration serialization.

## Important APIs, types, and functions

`get_frame_from_request()` turns an `rpcsvc_request_t` into a `call_frame_t` with `server_state_t`, client ref, uid/gid/pid, lock owner, groups, transport identifier, flags, ctime, and local request pointer. It applies root/all squashing depending on client trust and special PIDs. `server_connection_cleanup()` and `do_fd_cleanup()` collect server-side fds from the per-client fdtable and wind flush calls during disconnect/cleanup; `server_connection_cleanup_flush_cbk()` unrefs fds, decrements client fd counts, may detach transports, releases the client, and destroys the frame. `free_state()` releases all refs and heap members from `server_state_t`.

`gid_resolve()` optionally resolves supplemental groups server-side using `gid_cache`, `getpwuid_r()`, and `gf_getgrouplist()`, while `server_decode_groups()` copies aux gids sent by the client. `server_build_config()` parses `inode-lru-limit`, `trace`, and `config-directory`. Trace helpers print caller, loc, resolve, params, request, and reply. Serialization helpers include `serialize_rsp_dirent_v2()`, `serialize_rsp_direntp_v2()`, their cleanup functions, `serialize_rsp_locklist_v2()`, `getactivelkinfo_rsp_cleanup_v2()`, and `unserialize_req_locklist_v2()`. `gf_server_check_getxattr_cmd()` logs mount-point lists for special getxattr keys; `gf_server_check_setxattr_cmd()` logs aggregate IO stats for special setxattr keys. `server_ctx_get()` lazily allocates per-client server context and fdtable. `auth_set_username_passwd()` validates login username/password options and stores accepted credentials on the client.

## Control flow

For each incoming FOP, the server uses `get_frame_from_request()`, then FOP-specific code decodes arguments and may resolve loc/fd state before winding to the bound xlator. On disconnect, cleanup paths gather all open fds and send flushes to the bound xlator to release POSIX locks and fd resources. During tracing, request/reply logging is conditional on `conf->trace`.

## State and persistence behavior

The file owns no global state but mutates per-client context, fdtable refs, client refs, group arrays on call stacks, gid cache entries, transport refs, `server_state_t`, and client auth fields. All state is in-memory and tied to the server process and active client sessions.

## Dependencies and integration points

It depends on passwd/group system calls, gid cache, GlusterFS frame/stack APIs, fdtable APIs, dict/XDR conversion, inode/fd helpers, RPC transport refs, server config, and auth/login volume options. It is used by handshake, FOP dispatch, response helpers, cleanup, and resolution paths.

## Risks and test signals

Important risks include group resolution failures changing access behavior, root-squash exceptions, fd cleanup races during transport detach, ref leaks in cleanup callbacks, trace formatting with partially resolved state, and login option matching. `server_build_config()` has security-sensitive path validation for `config-directory`. Tests should cover server-managed gids enabled/disabled, trusted versus untrusted client squashing, NFS PID handling, disconnect with open fds, cleanup detach, special xattr command logging, auth.login allow/password combinations, active-lock list serialization cleanup, and readdir/readdirp cleanup under allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.h

## Purpose

`server-helpers.h` exposes shared helper contracts for protocol/server request state, cleanup, tracing, config, authentication helper logic, context access, inode creation, and XDR list serialization.

## Important APIs, types, and functions

`CALL_STATE(frame)` casts `frame->root->state` to `server_state_t *`. Exported functions include `free_state()`, `server_print_request()`, `get_frame_from_request()`, `server_connection_cleanup()`, `server_build_config()`, readdir cleanup helpers, `auth_set_username_passwd()`, `server_ctx_get()`, `server_process_event_upcall()`, `server_inode_new()`, active-lock serialization/cleanup helpers, locklist unserialization, and dirent serialization helpers.

## Control flow

FOP request handlers use this header to allocate and access call state, resolve per-client fd tables, print trace logs, and serialize complex response payloads. Cleanup code uses the exported connection cleanup function to flush fds on disconnect.

## State and persistence behavior

The header declares state access but owns none. The main state convention is that `frame->root->state` is a `server_state_t` allocated by the server helper path and must be released by `free_state()`.

## Dependencies and integration points

It includes GlusterFS defaults and depends on types from `server.h` and generated protocol headers included before or through related headers. It is a central include for server FOP and handshake code.

## Risks and test signals

Any mismatch in `CALL_STATE` assumptions can corrupt request handling. Compile tests catch signature drift; runtime tests should verify each exported cleanup/serialization function through the FOP paths that allocate those payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-mem-types.h

## Purpose

`server-mem-types.h` reserves protocol/server-specific memory accounting type IDs.

## Important APIs, types, and functions

The enum `gf_server_mem_types_` starts at `gf_common_mt_end + 1` and defines accounting buckets for `server_conf_t`, `server_state_t`, dirent responses, setvolume responses, lock migration records, child status records, and the terminating `gf_server_mt_end`.

## Control flow

Server allocations pass these enum values to GlusterFS allocation macros such as `GF_CALLOC()` and `GF_MALLOC()` so memory usage can be categorized.

## State and persistence behavior

There is no runtime state in this header. It affects memory accounting labels for process-lifetime allocations.

## Dependencies and integration points

It includes `<glusterfs/mem-types.h>` and must stay numerically after common memory types. It is used by server source files that allocate typed memory.

## Risks and test signals

The main risk is enum collision or failing to update the end marker when adding buckets. Memory-accounting initialization and statedump/mem-leak diagnostics are the relevant test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-messages.h -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-messages.h

## Purpose

`server-messages.h` declares the protocol/server component's stable GLFS message IDs and message string constants used by logging across server, handshake, helper, auth, resolution, and FOP code.

## Important APIs, types, and functions

The `GLFS_MSGID(PS, ...)` block enumerates all protocol/server message identifiers, including authentication errors, GFID resolution failures, memory/fd errors, uid/gid mapping errors, config issues, connection and cleanup messages, per-FOP trace messages, serialization failures, RPC setup/reconfigure messages, child status, active lock operations, and login/password errors. The `PS_MSG_*_STR` defines provide human-readable strings for many of those IDs.

## Control flow

Source files include this header and pass IDs to `gf_msg()`, `gf_smsg()`, or related logging macros. Message IDs are intentionally append-only to avoid reusing numeric identifiers in logs and tooling.

## State and persistence behavior

No runtime state exists here. The persisted contract is the stable mapping of message ID names to generated numeric IDs through `glfs-message-id.h`.

## Dependencies and integration points

The header depends on `<glusterfs/glfs-message-id.h>`. It integrates with all protocol/server logging and with external log parsers or diagnostics that rely on stable message IDs.

## Risks and test signals

The header explicitly warns never to remove IDs. Risks include renumbering, deleting, or reusing IDs, misspelled constants becoming public API, and string constants drifting from actual log behavior. Build tests catch missing symbols; log-format tests and operational diagnostics catch semantic drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-resolve.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-resolve.c

## Purpose

`server-resolve.c` resolves client-supplied protocol references into server-side `loc_t` and `fd_t` objects before FOPs are resumed. It supports resolution by fd number, anonymous fd/GFID, inode GFID, and parent GFID plus basename, with cache-only fast paths and backend lookup fallback.

## Important APIs, types, and functions

The public entry point is `resolve_and_resume(call_frame_t *frame, server_resume_fn_t fn)`, which stores the resume callback and starts resolving `state->resolve` and `state->resolve2`. `server_resolve_all()` sequences first and second resolve slots, then calls `server_resolve_done()` to print traces and invoke the resume function. `server_resolve()` dispatches by `fd_no`, `pargfid`, or `gfid`. `resolve_entry_simple()`, `resolve_inode_simple()`, and `resolve_anonfd_simple()` try inode/fd cache resolution. `resolve_gfid()` and `resolve_name()` perform backend lookups through `STACK_WIND()` when cache state is missing or stale. Their callbacks link inodes into the table, remove stale dentries on `RESOLVE_NOT`, wipe temporary locs, and continue resolution. `server_resolve_fd()` maps remote fd numbers through the per-client `server_ctx_t` fdtable and has special handling for `GF_ANON_FD_NO`.

## Control flow

FOP decoders populate `server_state_t` resolve descriptors. `resolve_and_resume()` starts with `state->resolve`, resolves it synchronously if the cache is decisive or asynchronously via backend lookup if needed, then repeats for `state->resolve2`. Once both are complete, the original FOP resume function runs against `frame->root->client->bound_xl`. `copy_file_range` uses the same fd resolver twice, relying on whether `state->fd` is already populated to place the second fd in `state->fd_out`.

## State and persistence behavior

Resolution mutates `state->loc`, `state->loc2`, `state->fd`, `state->fd_out`, temporary `resolve_loc` objects, and the bound xlator inode table. Successful lookup paths link and lookup inodes so future operations can resolve from cache. Anonymous fd resolution creates temporary anonymous fds from inodes. No durable persistence is involved.

## Dependencies and integration points

The file depends on inode table APIs, loc construction/wiping, backend lookup FOPs, dict copy/ref, server fdtable context, and server state definitions. It is used by server FOP request handlers before winding requests to lower xlators.

## Risks and test signals

Risks include stale inode cache behavior, parent type validation, basename path traversal via `/`, asynchronous lookup lifetime, anonymous fd creation, and dual-fd ambiguity for `copy_file_range`. The code correctly rejects basenames containing `/` and uses backend lookup for stale or indecisive cache states. Tests should cover GFID-only resolve, parent+basename resolve, missing parent ESTALE fallback, `RESOLVE_NOT` stale dentry removal, invalid basename rejection, normal fd lookup, bad fd EBADF, anonymous fd read/write with flags, subdir mount interactions through inode table state, and two-fd `copy_file_range` resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-resolve.c -->
