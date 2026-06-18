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
