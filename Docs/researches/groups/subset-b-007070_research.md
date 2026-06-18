# subset-b-007070 Research

Grouped source research for GlusterFS socket RPC transport and RPC/XDR support files. Each source file has a marker-delimited section for deterministic reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c` implements GlusterFS's socket-backed `rpc_transport_ops`. It owns TCP/UNIX socket listen/connect/accept, nonblocking event handling, outbound RPC record framing, inbound RPC record parsing, SSL/TLS setup and handshake, keepalive/nodelay/window options, disconnect cleanup, throttling, and the volume options exported by the socket transport. The source was read as a complete 4642-line file for this report.

## Important APIs, Types, and Functions

The public transport surface is the `tops` table, wiring `.listen`, `.connect`, `.disconnect`, `.submit_request`, `.submit_reply`, peer/local address getters, and `.throttle` to this implementation. Module lifecycle entry points are `init`, `reconfigure`, and `fini`, with `options[]` describing tunables such as `transport.socket.ssl-enabled`, certificate/key paths, `transport.listen-backlog`, `tcp-window-size`, `transport.tcp-user-timeout`, keepalive settings, `transport.socket.nodelay`, and `non-blocking-io`.

Core connection functions include `socket_init`, `socket_listen`, `socket_connect`, `socket_connect_finish`, `socket_disconnect`, `socket_server_event_handler`, `socket_event_handler`, and helpers for bind/nonblock/nodelay/keepalive/connect-finish. Outbound I/O is staged through `__socket_ioq_new`, `__socket_ioq_churn_entry`, `__socket_ioq_churn`, `socket_submit_outgoing_msg`, and `__socket_rwv`/`__socket_writev`. Inbound parsing is handled by `socket_proto_state_machine`, `__socket_read_frag`, `__socket_read_request`, `__socket_read_reply`, `__socket_read_vectored_request`, `__socket_read_vectored_reply`, `__socket_read_accepted_reply`, `__socket_read_accepted_successful_reply_v2`, and `__socket_read_simple_msg`.

SSL/TLS is concentrated in `init_openssl_mt`, `ssl_setup_connection_params`, `ssl_setup_connection_prefix`, `ssl_complete_connection`, `ssl_setup_connection_postfix`, `ssl_teardown_connection`, `ssl_do`, `ssl_handle_server_connection_attempt`, and `ssl_handle_client_connection_attempt`.

## Control Flow

Client connect resolves the remote address, creates a socket, applies socket options, optionally binds a local address, makes the fd nonblocking, starts `connect`, registers the fd with Gluster's event pool, and lets `socket_event_handler` finish the connection with `getsockopt(SO_ERROR)`. Server listen resolves the local address, creates and configures a socket, binds/listens, and registers a listener event handler. Accepted sockets are wrapped in new `rpc_transport_t` objects, initialized with inherited options, notified to RPC service through `RPC_TRANSPORT_ACCEPT`, then registered for normal socket events.

Event flow is nonblocking and stateful. `socket_event_handler` first completes plain or SSL handshakes if the fd is not logically connected. It then drains pending writes on `POLLOUT`, parses inbound RPC records on `POLLIN`, and treats negative return or poll errors as disconnects. Received messages are packaged as `rpc_transport_pollin_t`, then delivered asynchronously through `socket_event_poll_in_async` so the event loop can resume while upper layers process the message.

The inbound parser reads an ONC/RPC fragment header, allocates or extends an `iobuf`, reads the RPC message type, then dispatches to request or reply state machines. Request parsing can use an RPC service vector sizer to split program headers and payload into separate iovecs. Reply parsing maps XID to request metadata before deciding whether a Gluster read reply can use a vectored payload path. Multi-fragment records loop until the last-fragment bit is seen, then the final iovec set is handed to the transport layer.

## State and Persistence Behavior

All runtime state lives in `socket_private_t` attached to `rpc_transport_t`. It includes fd/index/generation, connection flags, SSL context/session state, outgoing queue, keepalive/window options, read-ahead cache state, inbound parser state, and an async notification counter/condition variable. The implementation has no file-backed persistence. It persists kernel sockets, OpenSSL objects, `iobuf`/`iobref` references, and queued outbound RPC messages only for the lifetime of the transport. Disconnect and `fini` release queued `ioq` entries, unregister/close event fds, free SSL contexts/cert path copies, and unref inbound buffers.

## Dependencies and Integration Points

This file integrates with Gluster's RPC transport framework (`rpc-transport.h`), event pool (`gf_event_register`, `gf_event_select_on`, `gf_event_handled`, `gf_event_unregister_close`), RPC service/client notification path (`rpc_transport_notify` events such as CONNECT, DISCONNECT, ACCEPT, MSG_RECEIVED, MAP_XID_REQUEST), `iobuf`/`iobref` memory management, Gluster dict/options parsing, address helpers from the socket transport support code, generated XDR headers, and OpenSSL. OS dependencies include sockets, `fcntl`, `shutdown`, `setsockopt`, TCP keepalive/TCP_USER_TIMEOUT, `accept`, `connect`, `listen`, `bind`, UNIX socket path cleanup, and IPv4/IPv6 address handling.

## Risks and Edge Cases

The highest-risk areas are partial-read state transitions, vectored read/write pointer mutation, and disconnect races between event threads and async notifications. SSL handshake is split across epoll events and must rearm read/write interest correctly for `SSL_ERROR_WANT_READ` and `SSL_ERROR_WANT_WRITE`. Fragment sizes are checked against a 1 GiB aggregate read guard and `RPC_MAX_FRAGMENT_SIZE` on write, but malformed peer inputs still stress allocation and state reset paths. The read-ahead cache borrows the active inbound iobuf memory, so pointer lifetime and state reset order are important. Accepted transport setup has multiple early-failure paths that must balance refs, event registration, socket close, and RPC service notification. Certificate option changes can break TLS setup, and the code deliberately ignores certificate purpose restrictions with `X509_PURPOSE_ANY` for shared client/server settings.

## Test Signals

Useful signals include RPC transport unit/integration tests for TCP and UNIX sockets, SSL and non-SSL connection setup, reconnect/disconnect races, keepalive/nodelay/window option coverage, malformed fragment/message type tests, large and multi-fragment record tests, Gluster FOP read reply vectored payload tests, NFS/GNFS read/write payload tests, event-thread-death notification tests, and leak/refcount checks around failed accept/connect/register paths. Build coverage should include OpenSSL 1.0.x and 1.1+ conditionals, Linux TCP_USER_TIMEOUT, IPv6, and `BUILD_GNFS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h -->
# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h` is the private state and protocol-state header for the GlusterFS socket RPC transport. It defines socket defaults, RPC fragment limits, inbound parser state enums, outbound queue entries, and the `socket_private_t` structure consumed by `socket.c`. The source was read as a complete 264-line file for this report.

## Important APIs, Types, and Functions

Important constants include `GF_DEFAULT_SOCKET_LISTEN_PORT`, `RPC_MAX_FRAGMENT_SIZE`, socket window bounds, keepalive defaults, and `GF_SOCKET_RA_MAX`. Parser enums define the record, fragment, simple-message, request-header, vectored-request, and vectored-reply states used by the nonblocking reader. `struct ioq` stores one outbound framed RPC message as an iovec list plus pending write cursor and optional `iobref`.

`struct gf_sock_incoming_frag` tracks the current fragment cursor, bytes read, pending vector, and request/reply parser substate. `struct gf_sock_incoming` tracks whole-record buffers, payload vectors, request metadata, read-ahead cache fields, fragment header, message type, and record state. `socket_private_t` is the owning transport-private state: outbound queue/lock, socket options, fd/event ids, SSL objects and paths, connection booleans, server/client role flags, and async notification synchronization.

## Control Flow

The header has no executable control flow, but its enums encode the control flow in `socket.c`: records progress from no state to fragment header to fragment body to complete; fragments progress from message type to request/reply body; request and reply bodies may pause at each read boundary and resume after another epoll event.

## State and Persistence Behavior

The structures define in-memory state only. `socket_private_t` persists for the lifetime of a transport, while `gf_sock_incoming` and `ioq` entries are repeatedly reset/freed as messages are received or sent. SSL certificate/key/CA path strings are dynamically copied in the implementation and freed during reset/fini.

## Dependencies and Integration Points

The header depends on OpenSSL headers, `rpc-transport.h`, Gluster list/iovec/iobuf types through included transport headers, and protocol types such as `rpc_request_info_t`, `msg_type_t`, and `mgmt_ssl_t`. It is tightly coupled to `socket.c` and intentionally not a public protocol API.

## Risks and Edge Cases

State enum changes must match switch statements in `socket.c`; missing reset transitions can leave stale parser state across records. `struct ioq` uses a union of `list_head` and explicit next/prev fields, so list layout assumptions must stay aligned. Padding fields suggest layout/alignment sensitivity. Changing `MAX_IOVEC` assumptions or parser substructure sizes affects outbound framing and inbound memory behavior.

## Test Signals

Compile coverage of socket transport is the primary signal. Runtime tests should exercise partial reads/writes across every parser enum state, queue churn with multiple pending messages, SSL and non-SSL connection lifecycles, and teardown while async notifications are in progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/Makefile.am -->
# sources/distributed-fs/glusterfs/rpc/xdr/Makefile.am

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/Makefile.am` is the top-level Automake file for the GlusterFS RPC XDR subtree. It delegates all build work to the `src` subdirectory. The source was read as a complete 1-line file for this report.

## Important APIs, Types, and Functions

The only directive is `SUBDIRS = src`, which tells Automake to recurse into `rpc/xdr/src`.

## Control Flow

There is no runtime control flow. Build control flows from the parent build into this directory and immediately into `src`.

## State and Persistence Behavior

No runtime state or persistent artifacts are owned directly here. Generated XDR sources/headers and the `libgfxdr` library are managed by the child `Makefile.am`.

## Dependencies and Integration Points

This file integrates the XDR subtree into the broader GlusterFS Automake recursion. Removing or changing `SUBDIRS` would disconnect the generated RPC/XDR library from the build.

## Risks and Edge Cases

The risk is simple but high impact: if recursion is broken, all RPC XDR generated sources and helper libraries disappear from the build.

## Test Signals

Automake/configure generation and a full build that enters `rpc/xdr/src` and produces `libgfxdr.la` are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am` builds GlusterFS's RPC XDR support library `libgfxdr.la`. It combines rpcgen-generated C/header files from `.x` protocol descriptions with handwritten helper sources such as `xdr-generic.c`, `xdr-custom.c`, and optional GNFS/NFSv3 wrappers. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

Important build variables are `NFS_XDRS`, `NFS_SRCS`, `NFS_HDRS`, `XDRGENFILES`, `XDRHEADERS`, `XDRSOURCES`, `libgfxdr_la_SOURCES`, `nodist_libgfxdr_la_SOURCES`, `libgfxdr_la_HEADERS`, and `nodist_libgfxdr_la_HEADERS`. It exports headers under `$(includedir)/glusterfs/rpc`, links against `libglusterfs.la`, applies `LIBGFXDR_LT_VERSION`, and restricts exported symbols through `libgfxdr.sym`.

## Control Flow

Automake builds generated headers and sources from `.x` files via explicit `rpcgen` rules. Header generation runs `rpcgen -h`, then uses `sed` to normalize include guards for hyphenated `.x` names. Source generation runs `rpcgen -c` only when the generated output is missing or stale. A `.PHONY` rule links `.x` files into the build directory for out-of-tree builds so rpcgen emits clean local include directives.

## State and Persistence Behavior

Generated `.c`, `.h`, and out-of-tree symlinked `.x` files are build artifacts. `CLEANFILES` removes generated sources/headers, and `clean-local` removes linked `.x` files in out-of-tree builds. The file itself has no runtime state.

## Dependencies and Integration Points

The build depends on rpcgen, sed, Automake/libtool, generated protocol descriptions (`glusterfs4-xdr.x`, `cli1-xdr.x`, `rpc-common-xdr.x`, `glusterd1-xdr.x`, `changelog-xdr.x`, `portmap-xdr.x`, and optional NFS `.x` files), `libglusterfs.la`, and include paths for `libglusterfs`, `rpc-lib`, and builddir XDR outputs. `BUILD_GNFS` controls whether NFSv3/NLM/ACL XDRs and helper sources are part of `libgfxdr`.

## Risks and Edge Cases

The custom rpcgen rules avoid noisy failures when make tries to regenerate existing files unnecessarily; changes can reintroduce flaky builds. Out-of-tree symlink handling is fragile because rpcgen include paths depend on current working directory. `BUILD_GNFS` must keep generated NFS headers and handwritten `msg-nfs3`/`xdr-nfs3` sources in sync. Header guard `sed` expressions are portability-sensitive.

## Test Signals

Signals include in-tree and out-of-tree builds, `make clean` followed by rebuild, builds with and without `BUILD_GNFS`, generated header include guard inspection, symbol export checks for `libgfxdr.la`, and platforms with different sed/rpcgen behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h` provides inline conversion helpers between GlusterFS in-memory structures and generated Gluster protocol/XDR structures. It covers open flag translation, `statvfs`, leases, flock, iatt/stat layouts, upcall payloads, metadata timestamps, and typed dict-to-XDR conversion. The source was read as a complete 963-line file for this report.

## Important APIs, Types, and Functions

Important helpers include `gf_flags_from_flags`, `gf_flags_to_flags`, `gf_statfs_to_statfs`, `gf_statfs_from_statfs`, `gf_proto_lease_to_lease`, `gf_proto_lease_from_lease`, `gf_proto_flock_to_flock`, `gf_proto_flock_from_flock`, `gf_stat_to_iatt`, `gf_stat_from_iatt`, `gfx_stat_to_iattx`, `gfx_stat_from_iattx`, `gfx_mdata_iatt_to_mdata_iatt`, `gfx_mdata_iatt_from_mdata_iatt`, `dict_to_xdr`, and `xdr_to_dict`.

Upcall conversion helpers include recall lease, cache invalidation, inode lock contention, and entry lock contention conversions. Flag macros (`GF_O_*`, `XLATE_BIT`, `UNXLATE_BIT`, access-mode macros) define wire-stable open flags independent of host OS values.

## Control Flow

Most helpers are straight field-copy conversions with early null checks. Dict serialization locks the source dict, allocates an array of `gfx_dict_pair`, iterates `members_list`, maps each known `GF_DATA_TYPE_*` to its XDR union field, computes the XDR variable-size payload using `xdr_sizeof`, then unlocks. Dict deserialization allocates a new dict, iterates received pairs, allocates owned values for strings/UUID/iatt/mdata/opaque pointer-like values, inserts them into the dict, frees rpcgen-allocated key/value buffers, and hands ownership of the completed dict to the caller.

## State and Persistence Behavior

The header owns no global storage. It creates transient heap allocations while converting dictionaries and may transfer ownership to `dict_t` via `dict_set_dynstr`, `dict_set_dynptr`, `dict_set_gfuuid`, `dict_set_iatt`, and `dict_set_mdata`. Upcall conversions may serialize or unserialize embedded xdata dictionaries through Gluster protocol macros. Wire encodings persist only in RPC buffers.

## Dependencies and Integration Points

It depends on `xdr-generic.h`, `xdr-custom.h`, generated `glusterfs4-xdr.h`, `glusterfs/iatt.h`, `protocol-common.h`, and `upcall-utils.h`. It is consumed by RPC clients/servers and translators that need to convert between local VFS-style structures and GlusterFS wire protocol objects.

## Risks and Edge Cases

This file is protocol-boundary code. Field order, missing flag translations, host-specific open flags, lock-owner length limits, empty-string-to-NULL normalization, and dict ownership rules are all high risk. `dict_to_xdr` skips unknown types and warns for pointer/old-string compatibility; callers must tolerate omitted keys. `xdr_to_dict` manually frees rpcgen-allocated buffers, so mismatched XDR allocation behavior or failed insertions can leak or double-free. Inline functions in a widely included header increase rebuild blast radius and can hide ABI drift until integration tests fail.

## Test Signals

Round-trip tests for flags, `iatt`, `statvfs`, flock, lease, upcall payloads, and typed dict entries are useful. Tests should include null dicts, empty dicts, unknown dict types, UUID/iatt/mdata entries, lock owners at boundary lengths, cache invalidation with invalid GFID strings, and compatibility between generated `glusterfs4-xdr` structures and local structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/glusterfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c` provides convenience serialization and deserialization wrappers for NFSv3, mount, NLMv4, and ACL RPC messages. It adapts typed generated XDR functions to Gluster's `struct iovec` message buffers. The source was read as a complete 481-line file for this report.

## Important APIs, Types, and Functions

The file exports functions named `xdr_to_*args` for decoding request arguments and `xdr_serialize_*res` or `xdr_serialize_*` for encoding responses and lists. Examples include `xdr_to_getattr3args`, `xdr_serialize_getattr3res`, `xdr_to_read3args`, `xdr_serialize_read3res`, `xdr_to_write3args_nocopy`, `xdr_serialize_write3res`, directory operations, fsstat/fsinfo/pathconf/commit wrappers, mount wrappers (`xdr_to_mountpath`, `xdr_serialize_mountres3`, `xdr_serialize_mountbody`, `xdr_serialize_exports`, `xdr_serialize_mountlist`), NLM wrappers, and ACL wrappers.

## Control Flow

Most functions are one-line adapters to `xdr_to_generic`, `xdr_to_generic_payload`, or `xdr_serialize_generic` with the correct generated `xdr_*` procedure. `xdr_to_mountpath` explicitly creates a decode XDR stream over the input iovec and decodes a `dirpath` into caller-provided output storage. `xdr_serialize_exports` explicitly creates an encode stream and serializes the recursive exports list.

## State and Persistence Behavior

The file owns no persistent state. Decode wrappers fill caller-owned typed structs, and encode wrappers write into caller-provided output buffers. Nocopy decode leaves payload bytes referenced through an output iovec instead of copying them into the decoded struct. Any allocations made by lower-level XDR routines follow SunRPC/rpcgen conventions and must be freed by callers using the matching cleanup paths.

## Dependencies and Integration Points

It depends on generated NFS headers (`xdr-nfs3.h`, `nlm4-xdr.h`, `acl3-xdr.h` via the header), `xdr-generic.h`, and `xdr-common.h`. It is built only when GNFS support is enabled and is consumed by the Gluster NFS server/mount/NLM/ACL RPC layers.

## Risks and Edge Cases

Wrapper correctness depends on pairing every typed argument/result with the exact generated XDR function. Buffer size validation is delegated to XDR routines; null iovec bases return `-1` in explicit helpers and generic helpers. Nocopy write/read paths require callers to respect that payload bytes are not stored in the decoded structure. Recursive export/mount list encoding can still be sensitive to deeply nested lists.

## Test Signals

Tests should encode/decode each NFSv3 procedure, mount exports/list responses, NLM lock/share/test/freeall paths, ACL get/set paths, null-buffer failures, short-buffer failures, and nocopy write payload extraction. Interoperability with an NFSv3 client is the strongest end-to-end signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h` declares the iovec-based NFSv3, mount, NLMv4, and ACL XDR wrapper API implemented by `msg-nfs3.c`. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

The header declares decode helpers for NFS args (`xdr_to_getattr3args`, `xdr_to_setattr3args`, `xdr_to_lookup3args`, `xdr_to_read3args`, `xdr_to_write3args`, `xdr_to_write3args_nocopy`, directory operation args, fsstat/fsinfo/pathconf/commit args), encode helpers for NFS results, mount helpers, NLM helpers, and ACL helpers. It includes generated `xdr-nfs3.h`, `nlm4-xdr.h`, and `acl3-xdr.h`.

## Control Flow

There is no executable control flow in the header. It defines the compile-time contract used by GNFS RPC handlers to convert raw RPC iovec buffers to typed request/response structures.

## State and Persistence Behavior

No state is owned here. Function contracts imply caller-owned input/output iovecs and typed structures.

## Dependencies and Integration Points

This header integrates generated NFS/NLM/ACL XDR types with Gluster's NFS server code and `libgfxdr`. It depends on system `iovec` and type definitions.

## Risks and Edge Cases

Declaration drift between this header and `msg-nfs3.c` will break builds or cause incorrect function calls. Nocopy variants need clear caller discipline because payload ownership differs from normal decode helpers. Conditional `BUILD_GNFS` build logic must keep this header installed only when matching generated headers exist.

## Test Signals

Compile coverage with `BUILD_GNFS`, link coverage for every declared symbol, and RPC handler tests that include this header and call decode/encode helpers are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/rpc-pragmas.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/rpc-pragmas.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/rpc-pragmas.h` centralizes compiler diagnostic suppressions needed by generated or generated-like RPC/XDR code. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

The file defines only an include guard and conditional pragmas. GCC 4+ suppresses `-Wunused-but-set-variable` and `-Wunused-variable` except on clang and NetBSD. Clang suppresses `-Wunused-variable` and `-Wunused-value`.

## Control Flow

There is no runtime control flow. Preprocessor conditionals choose compiler-specific diagnostic pragmas at compile time.

## State and Persistence Behavior

No state or persistence is involved.

## Dependencies and Integration Points

It is included by `xdr-custom.h` and related XDR code to keep builds clean when rpcgen-style code creates variables only used under some operation modes or platform typedefs.

## Risks and Edge Cases

The risk is hiding real unused-variable bugs in handwritten code that includes this header. Compiler/version conditionals also need maintenance as warning names and behaviors change. NetBSD is explicitly excluded from GCC pragmas, so platform-specific warning behavior may diverge.

## Test Signals

Builds with GCC, clang, and NetBSD toolchains are the main signal. Warning-clean builds for generated XDR files without globally weakening all project warnings verify the intended scope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/rpc-pragmas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c` implements non-recursive custom XDR routines for GlusterFS readdir and readdirp response lists. It avoids large stack usage from rpcgen's recursive linked-list encoders while preserving the existing wire format. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

Exports are `xdr_gfx_dirlist_custom`, `xdr_gfx_readdir_rsp_custom`, `xdr_gfx_dirplist_custom`, and `xdr_gfx_readdirp_rsp_custom`. The list-entry helpers serialize one `gfx_dirlist` or `gfx_dirplist` node without recursing into `nextentry`; the response helpers iteratively walk the linked list using `xdr_pointer`.

## Control Flow

Entry helpers encode/decode fixed entry fields and return `TRUE` only if every field succeeds. Response helpers first encode/decode `op_ret`, `op_errno`, and `xdata`, then set a pointer-to-pointer to the list head and loop over `xdr_pointer`. The loop returns `TRUE` when the decoded/encoded pointer is `NULL`; otherwise it advances to the current node's `nextentry` field.

## State and Persistence Behavior

The file owns no persistent state. During XDR decode, `xdr_pointer` can allocate list nodes according to the SunRPC XDR allocator rules. During encode, it walks caller-owned list nodes. It does not free list storage.

## Dependencies and Integration Points

It depends on generated `glusterfs4-xdr.h`, `rpc-pragmas.h`, and Gluster FOP definitions. Generated XDR code or protocol code can select these custom functions instead of recursive rpcgen output for large directory responses.

## Risks and Edge Cases

Wire compatibility depends on matching the generated field order exactly. The iterative loop must advance via `nextentry` after each non-null node; otherwise it would loop forever or corrupt decode output. Very large lists still consume memory and wire bandwidth, but no longer consume one C stack frame per entry. Decode ownership and freeing must match the generated structure's normal cleanup expectations.

## Test Signals

Round-trip encode/decode tests for empty, one-entry, and large readdir/readdirp lists are important. Stress tests with many directory entries should demonstrate bounded stack use. Compatibility tests should compare bytes against rpcgen output for small lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h` declares custom XDR routines that replace recursive rpcgen handling for selected GlusterFS directory response lists. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

The header declares `xdr_gfx_dirlist_custom`, `xdr_gfx_readdir_rsp_custom`, `xdr_gfx_dirplist_custom`, and `xdr_gfx_readdirp_rsp_custom`.

## Control Flow

There is no runtime flow in the header. Including code receives prototypes for custom encode/decode procedures that match the `xdrproc_t` style used by SunRPC XDR.

## State and Persistence Behavior

No state is owned here. The declared functions operate on caller-provided `XDR` streams and generated objects.

## Dependencies and Integration Points

It includes `<rpc/xdr.h>`, generated `glusterfs4-xdr.h`, and `rpc-pragmas.h`. It is included by `glusterfs3.h` and built into `libgfxdr`.

## Risks and Edge Cases

Prototype drift from the implementation or generated types breaks custom XDR substitution. Because this header includes warning-suppression pragmas, include placement can affect diagnostics in downstream files.

## Test Signals

Compile/link coverage of `xdr-custom.c` and any generated protocol code using these prototypes is the main signal, followed by readdir/readdirp round-trip tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c` implements generic iovec-to-XDR helpers used by the RPC/NFS wrapper layer. It serializes typed structures into caller-provided buffers, decodes buffers into typed structures, exposes remaining payload bytes for nocopy paths, and rounds payload lengths to XDR alignment when GNFS is enabled. The source was read as a complete 127-line file for this report.

## Important APIs, Types, and Functions

Exports are `xdr_serialize_generic`, `xdr_to_generic`, `xdr_to_generic_payload`, `xdr_length_round_up`, `xdr_bytes_round_up`, and `xdr_vector_round_up`. They depend on the `PROC` macro from the header to call `xdrproc_t` portably across Linux/BSD/macOS signature differences.

## Control Flow

Serialize and decode helpers validate buffer/data/procedure pointers, create an `XDR` memory stream with `xdrmem_create`, call the supplied XDR procedure, and return the encoded/decoded length or `-1`. The payload variant additionally returns the unconsumed portion of the XDR stream through `pendingpayload` under `BUILD_GNFS`. Round-up helpers compute 4-byte XDR padding and adjust a single iovec or the last vector in a vector list.

## State and Persistence Behavior

The file owns no persistent state. It only mutates caller-provided output buffers, decoded argument structures, and optional iovec lengths. `xdr_to_generic_payload` exposes pointers into the input buffer, so the input buffer must remain valid while the pending payload is used.

## Dependencies and Integration Points

It depends on SunRPC XDR APIs, `struct iovec`, and compatibility macros from `glusterfs/compat.h`. It is used by `msg-nfs3.c` and other RPC message wrappers that want uniform iovec handling.

## Risks and Edge Cases

Without `BUILD_GNFS`, payload and round-up helpers mostly return defaults/no-ops, so callers must be compiled consistently with GNFS expectations. Length macros depend on XDR internals (`x_private`, `x_base`, `x_handy`), which can be portability-sensitive. Nocopy payload pointers are only valid as long as the source iovec storage is valid. The hardcoded `1048576` buffer-size argument in `xdr_vector_round_up` is a policy assumption for padding safety.

## Test Signals

Round-trip tests using representative XDR procedures, null pointer failure tests, short output buffer tests, nocopy payload extraction tests, and XDR padding tests with lengths 0 through several modulo-4 cases are useful. Cross-platform compile tests validate `PROC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h` declares GlusterFS's generic XDR/iovec helper API and portability macros for invoking `xdrproc_t`. The source was read as a complete 76-line file for this report.

## Important APIs, Types, and Functions

The header defines XDR stream length macros, `XDR_BYTES_PER_UNIT`, the platform-specific `PROC` macro, and prototypes for `xdr_serialize_generic`, `xdr_to_generic`, `xdr_to_generic_payload`, `xdr_bytes_round_up`, `xdr_length_round_up`, and `xdr_vector_round_up`.

## Control Flow

There is no runtime flow here. The compile-time `PROC` macro chooses whether to call an XDR procedure as `proc(xdr, res)` on NetBSD or `proc(xdr, res, 0)` elsewhere to accommodate platform typedef differences.

## State and Persistence Behavior

No state is owned. The declared helpers operate on caller-owned buffers and structures.

## Dependencies and Integration Points

It depends on `sys/uio.h`, `rpc/types.h`, `rpc/xdr.h`, and `glusterfs/compat.h`. It is the common include for XDR wrapper files and generated-protocol adapters.

## Risks and Edge Cases

The macros inspect XDR implementation fields directly, which can break if the system XDR layout changes. The `PROC` portability shim must match each platform's `xdrproc_t` signature. Duplicate length macros also appear in `glusterfs3.h`, so changes should stay consistent.

## Test Signals

Cross-platform compile coverage on Linux, NetBSD, FreeBSD, and macOS is important. Wrapper tests that include this header and call generated XDR functions through `PROC` validate the signature abstraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c` is a handwritten rpcgen-style XDR implementation for NFSv3, mount, export, and related structures. It serializes/deserializes primitive aliases, file handles, attributes, weak-cache-consistency data, all core NFSv3 procedure arguments/results, mount responses/lists, exports, and cleanup helpers. The source was read as a complete 1907-line file for this report.

## Important APIs, Types, and Functions

Primitive wrappers include `xdr_uint64`, `xdr_int64`, `xdr_uint32`, `xdr_int32`, `xdr_filename3`, `xdr_nfspath3`, `xdr_fileid3`, `xdr_cookie3`, verifier helpers, UID/GID/size/offset/mode/count helpers, `xdr_nfsstat3`, and `xdr_ftype3`. Structural helpers include `xdr_specdata3`, `xdr_nfs_fh3`, `xdr_nfstime3`, `xdr_fattr3`, `xdr_post_op_attr`, `xdr_pre_op_attr`, `xdr_wcc_data`, `xdr_post_op_fh3`, `xdr_sattr3`, `xdr_diropargs3`, and `xdr_sattrguard3`.

Procedure coverage includes getattr, setattr, lookup, access, readlink, read, write, create, mkdir, symlink, mknod, remove, rmdir, rename, link, readdir, readdirp, fsstat, fsinfo, pathconf, and commit. Mount/export support includes `xdr_fhandle3`, `xdr_dirpath`, `xdr_name`, `xdr_mountstat3`, `xdr_mountres3`, `xdr_mountbody`, `xdr_mountlist`, `xdr_groups`, `xdr_exports`, and `xdr_exportnode`. Cleanup helpers are `xdr_free_exports_list`, `xdr_free_mountlist`, and `xdr_free_write3args_nocopy`.

## Control Flow

Each XDR function returns `FALSE` on the first failed field operation and `TRUE` after all fields are processed. Union-like results first serialize/deserialize status or discriminator fields, then switch on success/failure cases to choose the correct arm. Optional attributes and handles use boolean discriminators. Linked lists use recursive `xdr_pointer` for NFS directory, mount, group, and export lists. `xdr_pathconf3resok` has optimized inline encode/decode branches using `XDR_INLINE` for four booleans, with a field-by-field fallback. `xdr_write3args` intentionally decodes only the payload length and leaves remaining payload extraction to higher-level nocopy code.

## State and Persistence Behavior

No global state is owned. Decode operations can allocate strings, opaque byte arrays, file handles, and list nodes through XDR routines. Cleanup helpers free recursive or iterative mount/export list allocations and the nocopy write file-handle buffer. Encoded/decoded values persist in caller-owned structures and RPC buffers.

## Dependencies and Integration Points

It depends on `xdr-nfs3.h`, Gluster memory helpers, and `xdr-common.h`. `msg-nfs3.c` wraps these functions for iovec-based RPC handlers, and the GNFS server relies on the exact NFSv3 wire format implemented here.

## Risks and Edge Cases

This is wire-format code, so any field order or discriminator mistake breaks NFS interoperability. Several list encoders are recursive and can consume stack on deeply nested lists. Nocopy write handling is subtle because `data.data_len` is filled but `data.data_val` is not populated by `xdr_write3args`; callers must use the remaining payload iovec. Memory ownership follows SunRPC allocation conventions mixed with Gluster `GF_FREE`/`FREE`, so cleanup must match allocation source. The inline fast path in `xdr_pathconf3resok` must behave identically to fallback paths for encode/decode/free operations.

## Test Signals

NFSv3 protocol round-trip tests for every procedure, byte-level comparison with known-good rpcgen encodings, mount/export list tests, large readdir/readdirp responses, nocopy write payload tests, pathconf inline/fallback coverage, decode failure and cleanup leak tests, and interoperability tests with standard NFSv3 clients are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c -->
