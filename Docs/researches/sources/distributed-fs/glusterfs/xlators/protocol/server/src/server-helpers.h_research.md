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
