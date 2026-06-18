# subset-b-007069 Research

Grouped source research for GlusterFS RPC service dispatch, RPC XDR helpers, and socket transport naming/build metadata. Each section preserves the original source path for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-common.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-common.h

## Purpose

`xdr-common.h` provides shared XDR/RPC constants, compatibility macros, dump-program identifiers, and helper macros for measuring encoded/decoded XDR stream positions. The file was read as a complete 115-line header.

## Important APIs, Types, and Functions

It defines `enum gf_dump_procnum`, `GLUSTER_DUMP_PROGRAM`, `GLUSTER_DUMP_VERSION`, `GF_MAX_AUTH_BYTES`, `GF_AUTH_GLUSTERFS_MAX_GROUPS`, `GF_AUTH_GLUSTERFS_MAX_LKOWNER`, and platform compatibility aliases for XDR integer function names. It also exposes `xdr_decoded_remaining_addr`, `xdr_decoded_remaining_len`, `xdr_encoded_length`, and `xdr_decoded_length` macros.

## Control Flow

There is no runtime control flow. Consumers create an `XDR` stream, call an XDR encode/decode function, then use these macros to locate the remaining payload or determine how many bytes were encoded.

## State and Persistence Behavior

No state is owned here. The macros inspect mutable fields inside a caller-owned `XDR` object, especially `x_private`, `x_handy`, and `x_base`.

## Dependencies and Integration Points

It includes RPC auth/types headers and `sys/uio.h`, with NetBSD, Linux, Darwin, and Solaris compatibility sections. It is used by server and client XDR helpers (`xdr-rpc.c`, `xdr-rpcclnt.c`) and by the built-in dump RPC program in `rpcsvc.c`.

## Risks and Edge Cases

The auth-size macros encode the on-wire limit assumptions for GlusterFS auth v2/v3; incorrect lock-owner or group lengths can exceed `MAX_AUTH_BYTES`. The XDR position macros depend on libc/TIRPC `XDR` internals, so portability changes in XDR implementation layout are risky. Platform alias macros must stay consistent with the RPC library selected by configure.

## Test Signals

Tests should decode a call/reply with trailing payload and verify remaining address/length; encode a reply and verify encoded length; and exercise auth-size boundary calculations for AUTH_GLUSTERFS_v2 and v3 with group and lock-owner lengths near the limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.c -->
# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.c

## Purpose

`xdr-rpc.c` implements server-side SunRPC XDR helpers: decode inbound RPC calls, construct empty/denied/accepted replies, encode replies, and decode AUTH_UNIX credential payloads. The file was read as a complete 198-line source.

## Important APIs, Types, and Functions

The exported functions are `xdr_to_rpc_call`, `rpc_fill_empty_reply`, `rpc_fill_denied_reply`, `rpc_fill_accepted_reply`, `rpc_reply_to_xdr`, and `xdr_to_auth_unix_cred`. `true_func` is a small XDR callback used as a successful reply result placeholder.

## Control Flow

`xdr_to_rpc_call` validates buffers, clears `struct rpc_msg`, points credential and verifier opaque-auth storage at caller-provided buffers or a local fallback, decodes with `xdr_callmsg`, and returns the remaining program payload as an iovec. Reply builders mutate a caller-owned `struct rpc_msg`: empty replies set xid/direction, denied replies fill mismatch/auth fields, accepted replies fill verifier and program-version mismatch or success result fields. `rpc_reply_to_xdr` encodes with `xdr_replymsg` and returns an iovec spanning the encoded bytes. `xdr_to_auth_unix_cred` prepares `authunix_parms` storage and decodes with `xdr_authunix_parms`.

## State and Persistence Behavior

All state is caller-provided and transient. The functions do not allocate persistent storage; credentials are decoded into caller-owned buffers and reply XDR is written into caller-owned memory.

## Dependencies and Integration Points

It uses libc/TIRPC RPC/XDR APIs, `xdr-common.h` stream-position macros, `xdr-rpc.h` declarations, and Gluster validation/logging helpers. It is used by `rpcsvc_request_create` and reply construction in `rpcsvc.c`, and by auth code that decodes AUTH_UNIX data.

## Risks and Edge Cases

If callers omit `credbytes` or `verfbytes`, both opaque auth bases can point at the same local fallback buffer during decode, which is only safe because decoded values are consumed before function return and callers that need persistence pass request-owned storage. Decode failures produce warning logs and `-1`, leaving callers responsible for sending correct RPC errors. Accepted-success replies use a placeholder `true_func` because the SunRPC interface expects a result encoder even when the program payload is sent separately.

## Test Signals

Tests should cover valid call decode with payload remainder, malformed call decode, denied replies for `RPC_MISMATCH` and `AUTH_ERROR`, accepted replies for `PROG_MISMATCH` and `SUCCESS`, reply encoding length, and AUTH_UNIX credential decoding with platform-specific gid pointer types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.h

## Purpose

`xdr-rpc.h` declares the server-side RPC XDR helper API and Gluster-specific RPC auth flavor numbers. It also provides macros for reading fields from `struct rpc_msg` calls and printf-format helpers for RPC identifiers. The file was read as a complete 93-line header.

## Important APIs, Types, and Functions

It defines `gf_rpc_authtype_t` with `AUTH_GLUSTERFS`, `AUTH_GLUSTERFS_v2`, and `AUTH_GLUSTERFS_v3`. It declares `xdr_to_rpc_call`, `rpc_fill_empty_reply`, `rpc_fill_denied_reply`, `rpc_fill_accepted_reply`, `rpc_reply_to_xdr`, and `xdr_to_auth_unix_cred`. Accessor macros include `rpc_call_xid`, `rpc_call_direction`, `rpc_call_rpcvers`, `rpc_call_program`, `rpc_call_progver`, `rpc_call_progproc`, and credential/verifier flavor/length helpers.

## Control Flow

There is no executable flow in the header. It defines how server code decodes inbound calls, builds replies, and reads RPC identifiers without spreading SunRPC union-field details throughout the codebase.

## State and Persistence Behavior

No state is owned here. The macros read caller-owned `struct rpc_msg` instances, and declared functions operate on caller-owned buffers and iovecs.

## Dependencies and Integration Points

The header includes platform-specific RPC headers, `arpa/inet.h`, `rpc/xdr.h`, and `sys/uio.h`. It is consumed by `rpcsvc.c`, `xdr-rpc.c`, auth code, and logging paths that need format-width compatibility for RPC ids on Darwin or systems without `<rpc/rpc.h>`.

## Risks and Edge Cases

The macros depend on SunRPC/TIRPC `struct rpc_msg` union layout. The auth flavor values use RFC5531 unused ranges; changing them would break wire compatibility. Format macros differ by platform, so incorrect use can produce warnings or bad log output for xid/program fields.

## Test Signals

Compile coverage across Linux, Darwin, Solaris, and no-`rpc/rpc.h` configurations is the main signal. Wire tests should verify GlusterFS auth flavor numbers and field accessor macros against decoded RPC calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.c -->
# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.c

## Purpose

`xdr-rpcclnt.c` implements client-side SunRPC XDR helpers: decode inbound RPC replies, encode outbound RPC calls, and serialize AUTH_UNIX credentials for requests. The file was read as a complete 104-line source.

## Important APIs, Types, and Functions

The exported functions are `xdr_to_rpc_reply`, `rpc_request_to_xdr`, and `auth_unix_cred_to_xdr`.

## Control Flow

`xdr_to_rpc_reply` validates input, clears `struct rpc_msg`, initializes accepted-reply verifier/result defaults, decodes with `xdr_replymsg`, and returns remaining program payload as an iovec. `rpc_request_to_xdr` validates the request and destination, encodes with `xdr_callmsg`, and returns the encoded byte range. `auth_unix_cred_to_xdr` is intended to convert `authunix_parms` into an iovec backed by caller-provided storage.

## State and Persistence Behavior

All state is transient and caller-owned. The helpers use stack `XDR` streams and write into caller-provided `struct rpc_msg`, iovec, or byte buffers.

## Dependencies and Integration Points

It uses RPC/XDR headers, `xdr-common.h` length/remainder macros, and Gluster validation/logging helpers. It is used by client/callback request paths and by `rpcsvc_callback_submit` through `rpc_request_to_xdr`.

## Risks and Edge Cases

`xdr_to_rpc_reply` accepts a `verfbytes` parameter but does not assign it to the decoded verifier storage, so verifier data persistence should be checked by callers. `auth_unix_cred_to_xdr` creates the XDR stream with `XDR_DECODE` despite its name and later reads `xdr_encoded_length`; this appears suspicious and should be verified with a credential serialization test. Reply decode depends on the result placeholder `xdr_void`, with application payload decoded separately from the remaining iovec.

## Test Signals

Tests should encode a call and decode it server-side, decode accepted and denied replies with trailing payload, verify reply accessor macros from `xdr-rpcclnt.h`, and specifically test `auth_unix_cred_to_xdr` against `xdr_authunix_parms` expected bytes to catch encode/decode direction errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.h

## Purpose

`xdr-rpcclnt.h` declares the client-side RPC XDR helper API and convenience macros for reading decoded RPC replies. The file was read as a complete 36-line header.

## Important APIs, Types, and Functions

It declares `xdr_to_rpc_reply`, `rpc_request_to_xdr`, and `auth_unix_cred_to_xdr`. Macros include `rpc_reply_xid`, `rpc_reply_status`, `rpc_accepted_reply_status`, and `rpc_reply_verf_flavour`.

## Control Flow

There is no executable flow. Client-side code builds `struct rpc_msg` calls, serializes them through `rpc_request_to_xdr`, decodes replies through `xdr_to_rpc_reply`, then uses the macros to inspect reply status and verifier flavor.

## State and Persistence Behavior

No state is owned by the header. It defines accessors over caller-owned `struct rpc_msg` values and declares functions using caller-owned buffers.

## Dependencies and Integration Points

It includes `arpa/inet.h`, `rpc/xdr.h`, `sys/uio.h`, `rpc/rpc_msg.h`, and `rpc/auth_unix.h`. The header is consumed by RPC client code and by server callback code in `rpcsvc.c`.

## Risks and Edge Cases

The macros depend on SunRPC `struct rpc_msg` layout and only cover accepted-reply verifier fields, so denied replies require direct struct handling. Any mismatch between this header and `xdr-rpcclnt.c` function behavior can affect client request serialization and callback RPCs.

## Test Signals

Compile coverage with the selected RPC/TIRPC library and round-trip tests for request encode/reply decode are the most useful signals. Denied reply tests should ensure callers do not use accepted-reply macros blindly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/Makefile.am -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/Makefile.am

## Purpose

This Automake file routes the RPC transport build into the `socket` subdirectory. It was read as a complete one-line file.

## Important APIs, Types, and Functions

The only build directive is `SUBDIRS = socket`.

## Control Flow

There is no runtime control flow. During `make`, Automake descends into `rpc/rpc-transport/socket` to build transport modules.

## State and Persistence Behavior

No runtime state or persistence is represented. Build state is the generated Makefile dependency graph.

## Dependencies and Integration Points

This is the top-level RPC transport build hook and integrates with the socket transport subtree.

## Risks and Edge Cases

Adding another transport requires updating this file or it will not be built. A missing or empty subdirectory build would silently limit available RPC transports to those listed here.

## Test Signals

Autotools `make`/`make distcheck` coverage should verify that the socket subdirectory is entered and packaged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/Makefile.am -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/Makefile.am

## Purpose

This Automake file routes the socket RPC transport build into the `src` subdirectory. It was read as a complete one-line file.

## Important APIs, Types, and Functions

The only build directive is `SUBDIRS = src`.

## Control Flow

There is no runtime control flow. Automake descends into `rpc/rpc-transport/socket/src` to compile the socket transport module.

## State and Persistence Behavior

No runtime state or persistence is represented.

## Dependencies and Integration Points

It connects the parent RPC transport build to the actual socket transport sources and module definition.

## Risks and Edge Cases

If source files or generated headers move out of `src`, this file would need to be adjusted or the module build would omit them.

## Test Signals

Autotools configure/build tests should verify descent into `src` and inclusion in distribution artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/Makefile.am -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/Makefile.am

## Purpose

This Automake file builds the socket RPC transport plugin as `socket.la`, installs it under GlusterFS's `rpc-transport` module directory, and lists private headers and dependencies. It was read as a complete 22-line file.

## Important APIs, Types, and Functions

It declares `noinst_HEADERS = socket.h name.h socket-mem-types.h`, `rpctransport_LTLIBRARIES = socket.la`, `rpctransportdir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/rpc-transport`, `socket_la_SOURCES = socket.c name.c`, `socket_la_LDFLAGS = -module -avoid-version`, and `socket_la_LIBADD` dependencies on libglusterfs, libgfxdr, libgfrpc, and `-lssl`.

## Control Flow

There is no runtime flow. Build flow compiles `socket.c` and `name.c`, links them into a libtool module, and installs the module in the versioned GlusterFS RPC transport plugin directory.

## State and Persistence Behavior

No runtime state is owned. The file controls build outputs and cleanable editor backups via `CLEANFILES = *~`.

## Dependencies and Integration Points

Include paths point at `libglusterfs/src`, `rpc/rpc-lib/src`, and both source/build `rpc/xdr/src` directories. The module links against Gluster core, generated XDR support, RPC library support, and OpenSSL.

## Risks and Edge Cases

Forgetting a new source/header here can produce runtime plugin load failures or incomplete distribution tarballs. The hard `-lssl` dependency means SSL availability and linker ordering matter for socket transport builds.

## Test Signals

`make`, module installation checks, and plugin-load smoke tests should verify that `socket.la` builds, installs in `$(PACKAGE_VERSION)/rpc-transport`, and resolves symbols from libglusterfs/libgfxdr/libgfrpc/OpenSSL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.c -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.c

## Purpose

`name.c` resolves, binds, and formats local/remote socket addresses for the GlusterFS socket RPC transport. It handles IPv4, IPv6, SDP-over-INET compatibility, and Unix-domain sockets for both client and server paths. The file was read as a complete 887-line source.

## Important APIs, Types, and Functions

Public entry points are `client_bind`, `socket_client_get_remote_sockaddr`, `socket_server_get_local_sockaddr`, and `get_transport_identifiers`. Important internal helpers include `_assign_port`, `af_inet_bind_to_port_lt_ceiling`, `af_unix_client_bind`, `client_fill_address_family`, `gf_resolve_ip6`, `af_inet_client_get_remote_sockaddr`, `af_unix_client_get_remote_sockaddr`, `af_unix_server_get_local_sockaddr`, `af_inet_server_get_local_sockaddr`, `server_fill_address_family`, and `fill_inet6_inet_identifiers`.

## Control Flow

Client remote resolution starts in `socket_client_get_remote_sockaddr`: it determines address family from `transport.address-family`, `remote-host`, or `transport.socket.connect-path`, then either resolves inet addresses with `af_inet_client_get_remote_sockaddr` or copies a Unix connect path. Inet resolution reads `remote-host` and optional `remote-port`, infers AF_INET/AF_INET6 for literal addresses, then calls `gf_resolve_ip6`, which caches `getaddrinfo` results and returns one address per call while rotating through the result list. `client_bind` then binds a socket locally, trying privileged or insecure port ceilings for inet sockets and optional `transport.socket.bind-path` for Unix sockets.

Server address setup starts in `socket_server_get_local_sockaddr`: it determines family using `server_fill_address_family`, then either builds a Unix listen path from `transport.socket.listen-path` or an inet listener from `transport.socket.listen-port` and optional `transport.socket.bind-address`. Inet server setup defaults to any-address for AF_INET/AF_INET6 when no bind address is given, otherwise uses `getaddrinfo` with `AI_PASSIVE`, preferring IPv6 results when available. `get_transport_identifiers` formats local and peer addresses into stable `host:service` strings, with IPv4-mapped IPv6 addresses normalized to IPv4 for readability.

## State and Persistence Behavior

The file stores no global state. It mutates caller-owned transport fields: `this->dnscache` holds cached `struct addrinfo` results, `this->myinfo` and `this->peerinfo` receive sockaddr lengths and textual identifiers, and bind behavior depends on `this->options` and `this->bind_insecure`. Unix socket path state is copied into caller-provided sockaddr buffers. DNS cache memory is allocated through Gluster allocation helpers and freed/replaced when exhausted or on errors.

## Dependencies and Integration Points

It depends on POSIX sockets, `getaddrinfo`, `getnameinfo`, `inet_pton`, Gluster dict/data helpers, reserved-port tracking (`gf_process_reserved_ports`, `BIT_VALUE`, `BIT_CLEAR`), logging/message IDs, socket-private types from `socket.h`, and transport types from `rpc-transport.h`. It is used by the socket transport implementation when connecting, listening, binding, and labeling connections.

## Risks and Edge Cases

Privileged bind loops can be expensive and must correctly skip Gluster-reserved ports; when all secure ports are exhausted the code falls back to an insecure ceiling to avoid brick-port collisions. Several Unix path checks use the 108-byte `sun_path` limit; off-by-one mistakes can truncate or reject paths. DNS resolution is blocking and the file has a TODO for nonblocking DNS. `gf_resolve_ip6` frees and recreates the cache after cycling through results, so callers should expect different destination addresses across reconnects. IPv4-mapped IPv6 normalization relies on direct `s6_addr32`/`s6_addr16` access with Solaris conditionals. Identifier formatting uses `sprintf` into caller-owned buffers, so buffer sizing must be guaranteed by transport structs.

## Test Signals

Tests should cover address-family inference for remote-host versus Unix connect-path, invalid/missing options, literal IPv4/IPv6 hosts, DNS rotation across multiple `addrinfo` results, client secure and insecure bind fallback, reserved-port skipping, Unix path length boundaries, server any-address defaults, bind-address resolution, IPv4-mapped IPv6 identifier formatting, SDP family restoration, and error logging for unsupported address families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.h

## Purpose

`name.h` declares the socket transport address helper interface implemented by `name.c`. The file was read as a complete 33-line header.

## Important APIs, Types, and Functions

It declares `client_bind`, `socket_client_get_remote_sockaddr`, `socket_server_get_local_sockaddr`, and `get_transport_identifiers`.

## Control Flow

There is no executable control flow. Socket transport code includes this header to bind client sockets, compute remote and local sockaddr values, and populate printable identifiers after connect/accept.

## State and Persistence Behavior

No state is owned by the header. Declared functions mutate caller-owned `rpc_transport_t`, `sockaddr`, `socklen_t`, and `sa_family_t` storage.

## Dependencies and Integration Points

It includes `glusterfs/compat.h` and relies on `rpc_transport_t` being visible through the including translation unit's transport headers. The declarations integrate `name.c` with `socket.c` and the RPC transport module build.

## Risks and Edge Cases

Because prototypes use generic `struct sockaddr *`, callers must pass buffers large enough for IPv6 and Unix-domain addresses. Missing direct inclusion of the transport type means include order can matter unless `compat.h` or prior includes provide the needed declarations.

## Test Signals

Compile coverage of `socket.c` including this header and runtime tests for each declared function through the socket transport are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket-mem-types.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket-mem-types.h

## Purpose

`socket-mem-types.h` defines socket transport-specific memory accounting type identifiers for Gluster's allocator/debugging infrastructure. The file was read as a complete 22-line header.

## Important APIs, Types, and Functions

It defines `gf_sock_mem_types_t` with `gf_sock_connect_error_state_t`, `gf_sock_mt_lock_array`, and `gf_sock_mt_end`, starting after `gf_common_mt_end`.

## Control Flow

There is no runtime control flow. The enum values are used as allocation type tags by socket transport code.

## State and Persistence Behavior

No state is owned. The enum contributes to in-memory accounting and diagnostics rather than persistent data.

## Dependencies and Integration Points

It includes `glusterfs/mem-types.h` and integrates socket transport allocations with the common Gluster memory-type namespace.

## Risks and Edge Cases

The enum must not collide with common memory types or future socket-specific additions. New socket allocations should use values before `gf_sock_mt_end` so statedumps and leak reports remain meaningful.

## Test Signals

Compile coverage and memory-accounting/statedump checks should confirm socket allocation tags resolve to valid type names and do not overlap common tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket-mem-types.h -->
