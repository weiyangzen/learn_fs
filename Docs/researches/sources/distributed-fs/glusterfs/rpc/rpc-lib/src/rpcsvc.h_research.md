# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.h

## Purpose

`rpcsvc.h` is the public contract for GlusterFS server-side RPC services. It defines request, listener, program, actor, auth, callback-program, and queue structures plus the functions used by RPC programs to register actors, create listeners, authenticate calls, submit replies, and emit callbacks. The file was read as a complete 618-line header.

## Important APIs, Types, and Functions

Important types are `rpcsvc_request_t`, `rpcsvc_listener_t`, `rpcsvc_actor_t`, `rpcsvc_program_t`, `rpcsvc_request_queue_t`, `rpcsvc_cbk_program_t`, `rpcsvc_auth_ops_t`, `rpcsvc_auth_t`, and `rpcsvc_auth_list`. Main exported APIs include `rpcsvc_init`, `rpcsvc_destroy`, `rpcsvc_program_register`, `rpcsvc_program_unregister`, `rpcsvc_create_listeners`, `rpcsvc_register_notify`, `rpcsvc_unregister_notify`, `rpcsvc_submit_message`, `rpcsvc_submit_generic`, `rpcsvc_error_reply`, `rpcsvc_request_submit`, `rpcsvc_callback_submit`, `rpcsvc_program_actor`, `rpcsvc_get_program_vector_sizer`, auth initialization/check APIs, portmap/rpcbind APIs, and runtime option setters. Key macros expose request fields and implement `RPC_AUTH_ROOT_SQUASH` and `RPC_AUTH_ALL_SQUASH`.

## Control Flow

The header describes the control contract: transports deliver RPC messages into the service, the service resolves a `rpcsvc_program_t`, indexes its actor table by procnum, then calls the actor with a populated `rpcsvc_request_t`. Actors return `RPCSVC_ACTOR_SUCCESS`, `RPCSVC_ACTOR_ERROR`, or `RPCSVC_ACTOR_IGNORE` and normally submit replies through the declared submit functions. Programs may opt into own-thread queues or synctask dispatch.

## State and Persistence Behavior

`rpcsvc_request_t` carries per-call state: transport reference, service pointer, program/proc identifiers, uid/gid/pid, lock owner, xid, aux groups, payload iovecs, iobref, auth credentials/verifiers, DRC reply pointer, queue linkage, RPC/auth error status, client time, latency start time, and dispatch flags. `rpcsvc_program_t` carries long-lived program registration data, actor table, private pointer, latencies, notify callback, auth minimum, queue/thread state, port, and liveness flags. This header declares in-memory state only; persistence is limited to externally managed RPC program effects.

## Dependencies and Integration Points

It depends on Gluster event, dict, client, compat, transport, XDR RPC, and common RPC service types. The contract integrates with `rpcsvc.c`, `rpcsvc-auth.c`, `rpc-drc`, transport implementations, and higher-level protocol/server xlators that define actor tables and private program state.

## Risks and Edge Cases

The accessor macros expose internal layout directly, so structure changes have broad compile-time impact. Some macros reference members not present in the visible `rpcsvc_request_t` definition in this version (`recordiob`, `vecstate`, and unconditional `private` when GNFS is not built), so stale macro use can fail compile or expose configuration-dependent behavior. The root/all squash macros mutate uid/gid and auxgid arrays in place and only rewrite auxgid entries equal to zero. Actor tables must keep `numactors`, `procnum`, and array indexes consistent or dispatch can reject valid procedures.

## Test Signals

Compile tests across GNFS/non-GNFS and platform variants are important because many declarations are conditional. Actor registration tests should validate proc bounds, `unprivileged` behavior, own-thread flags, and vector sizer lookup. Auth tests should cover root/all squash with small and large auxgid arrays and confirm AUTH_UNIX auxgid extraction behavior.
