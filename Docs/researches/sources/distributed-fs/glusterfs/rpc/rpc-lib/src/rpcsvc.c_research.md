# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.c

## Purpose

`rpcsvc.c` implements the server side of GlusterFS's RPC service layer. It receives decoded transport messages, builds `rpcsvc_request_t` objects, authenticates calls, resolves registered program actors, dispatches work either inline, through synctasks, or through per-event-thread request queues, builds RPC replies, manages listeners and notifications, registers/unregisters programs with portmap/rpcbind, and exposes the built-in `GF-DUMP` RPC program. The file was read as a complete 3323-line source.

## Important APIs, Types, and Functions

Major request path entry points are `rpcsvc_notify`, `rpcsvc_handle_rpc_call`, `rpcsvc_request_create`, `rpcsvc_request_init`, `rpcsvc_program_actor`, `rpcsvc_submit_message`, `rpcsvc_submit_generic`, and `rpcsvc_error_reply`. Reply/callback helpers include `rpcsvc_fill_reply`, `rpcsvc_record_build_record`, `rpcsvc_record_build_header`, `rpcsvc_callback_submit`, `rpcsvc_request_submit`, `rpcsvc_callback_build_record`, and `rpcsvc_fill_callback`. Service lifecycle and registration are handled by `rpcsvc_init`, `rpcsvc_destroy`, `rpcsvc_program_register`, `rpcsvc_program_unregister`, `rpcsvc_create_listener`, `rpcsvc_create_listeners`, `rpcsvc_listener_destroy`, `rpcsvc_register_notify`, and `rpcsvc_unregister_notify`. Operational knobs include `rpcsvc_init_options`, `rpcsvc_reconfigure_options`, `rpcsvc_set_outstanding_rpc_limit`, `rpcsvc_set_throttle_on`, `rpcsvc_set_throttle_off`, `rpcsvc_get_throttle`, `rpcsvc_auth_check`, `rpcsvc_transport_privport_check`, and `rpcsvc_volume_allowed`.

## Control Flow

Transport events enter through `rpcsvc_notify`. Accepted transports notify registered service consumers, disconnect/cleanup events fan out to notification callbacks and listener cleanup, message events call `rpcsvc_handle_rpc_call`, and event-thread-death events enqueue internal requests to program-specific handler threads. `rpcsvc_handle_rpc_call` validates peer address family and privileged-port status, calls `rpcsvc_request_create`, checks accepted status, finds an actor via `rpcsvc_program_actor`, enforces `allow_insecure` and per-actor `unprivileged`, consults the duplicate request cache, then dispatches the actor. Dispatch is inline by default, via `synctask_new` for `synctask` programs, or via an own-thread queue keyed per event thread for `ownthread` programs.

Request creation decodes the SunRPC header with `xdr_to_rpc_call`, copies vectored payload references, initializes authentication metadata, validates RPC version 2, calls `rpcsvc_authenticate`, and starts per-transport outstanding-request accounting. Reply flow is the reverse: actors set request status/error and call `rpcsvc_submit_message` or `rpcsvc_submit_generic`; the generic submit updates latency, constructs an RPC reply header, optionally caches the completed reply in DRC, submits to the transport, unreferences buffers, and destroys the request.

## State and Persistence Behavior

The service state is in `rpcsvc_t`: lists of listeners, programs, auth schemes, notification wrappers, a request mem-pool, options, xlator/context pointers, duplicate-request-cache pointer, throttle flags, root/all squash settings, anonymous UID/GID, and portmap state. Program state is copied into heap-owned `rpcsvc_program_t` objects with latency arrays, request queues, queue status bitsets, and optional TLS keys. Request state lives only for a single RPC transaction and is returned to `svc->rxpool` after reply submission. There is no file persistence; durable effects are external, through registered RPC program actors and portmap/rpcbind registration.

## Dependencies and Integration Points

This file integrates with `rpc-transport` for listening, event delivery, throttling, and submit; `xdr-rpc`, `xdr-rpcclnt`, `xdr-generic`, and generated `rpc-common-xdr` for wire encoding; `rpcsvc-auth.c` for auth scheme initialization and authentication; `rpc-drc` for duplicate request handling; Gluster's `dict_t`, `iobuf`, `iobref`, mem-pool, statedump, syncop, logging, latency, and xlator context facilities; libc RPC portmap/rpcbind APIs under GNFS/IPV6 builds; and protocol constants from `protocol-common.h`. Public callers are Gluster RPC programs that register actor tables and then submit program replies through this layer.

## Risks and Edge Cases

The DRC path must keep request, cached reply, and transport lifetimes aligned; a duplicate in transit is destroyed without actor execution. `rpcsvc_program_unregister` marks own-thread programs dead but still calls `rpcsvc_program_destroy(prog)` at function exit, which is risky if request-handler threads can still dereference the copied program. Outstanding-request throttling intentionally exempts lock operations to avoid deadlocking unlock traffic, so load-control tests need to account for that exception. Error paths in request creation call `rpcsvc_error_reply` on partially initialized requests, making `trans`, `svc`, and status fields critical. `rpcsvc_handle_disconnect` copies notification wrappers before invoking callbacks to avoid list mutation under callbacks, but `notify_count` is not decremented in `rpcsvc_unregister_notify`, so allocation size may exceed active wrappers. Portmap/rpcbind operations are mostly no-ops outside GNFS, which can hide integration differences between builds.

## Test Signals

Useful tests include RPC decode/auth/actor-dispatch unit coverage for bad RPC version, missing program, missing version, bad procnum, auth reject, and unprivileged-port rejection; integration tests that register a small program and verify inline, synctask, and own-thread dispatch; DRC duplicate and in-transit replay tests; listener creation with multiple comma-separated transport types; portmap/rpcbind tests in GNFS/IPV6 builds; throttle limit tests around the rounded outstanding limit and lock-operation exemptions; and teardown tests that unregister programs while own-thread queues drain. Statedump tests should confirm per-procedure latency counters are emitted and reset.
