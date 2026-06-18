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
