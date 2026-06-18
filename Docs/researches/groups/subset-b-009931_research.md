# Research: subset-b-009931

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket.c -->
# sources/user-network-fs/samba/source4/lib/socket/socket.c

## Purpose

`socket.c` is the common source4 socket facade. It allocates and owns `struct socket_context`, validates state transitions, dispatches calls through `struct socket_ops`, converts between Samba `socket_address` and `tsocket_address`, and selects IPv4, IPv6, or Unix-domain backends by family name.

## Important APIs, Types, and Functions

The file exports `socket_create_with_ops()`, `socket_create()`, `socket_connect()`, `socket_connect_complete()`, `socket_listen()`, `socket_accept()`, `socket_recv()`, `socket_recvfrom()`, `socket_send()`, `socket_sendto()`, `socket_pending()`, `socket_set_option()`, address getters/converters, `socket_get_fd()`, `socket_dup()`, `socket_address_from_strings()`, `socket_address_from_sockaddr()`, `socket_address_from_sockaddr_storage()`, `socket_address_set_port()`, `socket_address_copy()`, `socket_getops_byname()`, and `socket_set_flags()`. The private `socket_destructor()` closes backend sockets unless `SOCKET_FLAG_NOCLOSE` is set.

## Control Flow

Creation allocates a talloc-owned context, initializes neutral state, calls backend `fn_init`, enables randomized short I/O when `SOCKET_TESTNONBLOCK` is set for streams, makes datagram sockets nonblocking immediately, and installs the destructor. Public operations check null pointers, socket type, and `enum socket_state` before calling the backend vtable. Accept returns a backend-created child context and then installs the common destructor. Send and receive optionally simulate partial nonblocking I/O, including a special encrypted path that preserves resend consistency by splitting in deterministic halves.

## State and Persistence Behavior

State is in `struct socket_context`: type, current state, flags, fd, private backend data, ops, backend name, and address family. The facade does not persist external data, but it owns file descriptor lifetime through talloc. Address constructors allocate independent talloc-owned copies of textual addresses or `sockaddr` blobs.

## Dependencies and Integration Points

This layer depends on talloc, NTSTATUS mapping, Unix networking headers, Samba `set_blocking()`, `print_sockaddr()`, `set_sockaddr_port()`, and libtsocket conversion helpers. It integrates with `socket_ip.c`, `socket_unix.c`, async connect helpers in `connect.c`/`connect_multi.c`, packet framing in `lib/stream`, and callers such as SMB client transports.

## Risks and Edge Cases

The facade trusts backend callbacks and only partially normalizes accepted contexts. `socket_address_from_sockaddr()` does not reject unknown address families before returning an object with an unset family. `socket_dup()` closes the old fd after `dup()` but does not preserve close-on-exec. Random partial I/O can expose callers that assume full writes or reads. The encrypted partial-send behavior is intentionally different and must remain aligned with TLS/SASL resend requirements.

## Test Signals

The local socket torture suite exercises UDP/TCP send, receive, accept, and address reporting. Additional useful signals are IPv6 and Unix-domain coverage, `SOCKET_TESTNONBLOCK=1` runs, fd ownership tests for `SOCKET_FLAG_NOCLOSE`, and conversion round trips through `tsocket_address`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket.h -->
# sources/user-network-fs/samba/source4/lib/socket/socket.h

## Purpose

`socket.h` declares the source4 socket abstraction shared by socket backends, async connect helpers, packet streams, and callers. It defines the public data model for socket types, socket addresses, backend vtables, state values, flags, and exported helper APIs.

## Important APIs, Types, and Functions

Core types are `enum socket_type`, `struct socket_address`, `struct socket_ops`, `enum socket_state`, and `struct socket_context`. Flags include `SOCKET_FLAG_PEEK`, `SOCKET_FLAG_TESTNONBLOCK`, `SOCKET_FLAG_ENCRYPT`, and `SOCKET_FLAG_NOCLOSE`. The header declares synchronous operations, address conversion/copy functions, access checking, async connect APIs, multi-address connect APIs with optional establishment hooks, `set_socket_options()`, `socket_set_flags()`, `socket_tevent_fd_close_fn()`, and the external `testnonblock`.

## Control Flow

The header has no runtime flow. Its contracts define which state transitions implementations must support: undefined to client connected, server listen to accepted server connected, and starttls/error states used by higher layers. `struct socket_ops` is the vtable dispatch point used by `socket.c`.

## State and Persistence Behavior

The state contract is explicit in `struct socket_context`; ownership is talloc-centered, with fd cleanup controlled by flags and backend close functions. `struct socket_address` may represent either a textual family/address/port tuple or an already-materialized `sockaddr` and length.

## Dependencies and Integration Points

The header forward-declares tevent, resolve, composite, and tsocket types while relying on Samba base types such as `NTSTATUS`, `DATA_BLOB`, and `TALLOC_CTX` from including translation units. It is included by socket backends, stream packet code, TLS declarations, SMB client socket code, and tests.

## Risks and Edge Cases

The public structs expose implementation details, so ABI and source compatibility are fragile. Callers can mutate state, flags, and fd directly. `SOCKET_FLAG_ENCRYPT` has subtle interaction with test nonblocking behavior, and address objects with both textual and `sockaddr` fields require callers to understand precedence.

## Test Signals

Compile coverage across socket, stream, TLS, and libcli users is the main header signal. Behavioral tests should verify that all backends implement every required vtable operation for both stream and datagram where advertised.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket_ip.c -->
# sources/user-network-fs/samba/source4/lib/socket/socket_ip.c

## Purpose

`socket_ip.c` implements IPv4 and IPv6 `socket_ops` backends for source4 sockets. It wraps POSIX `socket`, `bind`, `connect`, `listen`, `accept`, `recv`, `send`, `recvfrom`, `sendto`, address reporting, options, and pending-byte queries behind NTSTATUS-returning Samba APIs.

## Important APIs, Types, and Functions

Exports are `socket_ipv4_ops()` and, when IPv6 is available, `socket_ipv6_ops()`. Important helpers include `ipv4_init()`, `ipv4_connect()`, `ipv4_listen()`, `ipv4_accept()`, `ipv4_recvfrom()`, `ipv4_sendto()`, peer/local address getters, shared `ip_connect_complete()`, `ip_recv()`, `ip_send()`, `ip_pending()`, `ip_close()`, and IPv6 equivalents such as `interpret_addr6()`, `fix_scope_id()`, `ipv6_tcp_connect()`, `ipv6_listen()`, and `ipv6_tcp_accept()`.

## Control Flow

Initialization maps Samba stream/datagram types to `SOCK_STREAM` or `SOCK_DGRAM`, creates an AF_INET or AF_INET6 fd, marks close-on-exec, and records backend name/family. Connect optionally binds a local address, resolves textual numeric addresses, calls `connect()`, then validates completion through `SO_ERROR` and switches to nonblocking mode. Listen sets `SO_REUSEADDR`, binds, calls `listen()` for stream sockets, and marks the context as `SOCKET_STATE_SERVER_LISTEN`. Accept creates a nonblocking child fd and copies core context fields. Datagram receive/send build `socket_address` metadata from source/destination socket addresses.

## State and Persistence Behavior

The backend stores only fd, backend name, and family in `socket_context`; per-call address objects are talloc-owned by the caller context. Listening and connected states are set in the common context. IPv6 listen forces `IPV6_V6ONLY` before bind.

## Dependencies and Integration Points

The file depends on POSIX networking, Samba address utilities `interpret_addr2()`, `is_ipaddress_v6()`, `set_socket_options()`, close-on-exec helpers, and NTSTATUS errno mapping. It is selected by `socket_getops_byname("ip"|"ipv4"|"ipv6")` and used by socket tests, stream transports, and SMB connection paths.

## Risks and Edge Cases

Textual address parsing accepts only numeric-style addresses through Samba helpers; unresolved hostnames are not resolved here. IPv4 treats an all-zero parsed server address as bad/unreachable, which also means `0.0.0.0` is not valid as a remote target. IPv6 link-local scope parsing depends on `%ifname`. `gethostbyaddr()` is used for peer names and can block or fail. Accepted contexts omit `family` initialization in the copied fields, which can matter to code reading it directly.

## Test Signals

Current local tests cover IPv4 UDP and TCP loopback. Stronger coverage should include IPv6 loopback, link-local scoped addresses, datagram source address reporting, `FIONREAD` pending behavior, nonblocking connect completion failures, and `IPV6_V6ONLY` binding interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket_ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket_unix.c -->
# sources/user-network-fs/samba/source4/lib/socket/socket_unix.c

## Purpose

`socket_unix.c` implements the Unix-domain socket backend for the source4 socket abstraction. It supports stream and datagram Unix sockets, path-based connect/listen/sendto, accept, byte I/O, pending-byte queries, and generic local address reporting.

## Important APIs, Types, and Functions

The exported selector is `socket_unixdom_ops()`. Backend functions include `unixdom_init()`, `unixdom_connect()`, `unixdom_connect_complete()`, `unixdom_listen()`, `unixdom_accept()`, `unixdom_recv()`, `unixdom_send()`, `unixdom_sendto()`, `unixdom_pending()`, peer/local address getters, and `unixdom_close()`.

## Control Flow

Initialization creates a `PF_UNIX` socket matching the requested type. Connect validates path length, builds `sockaddr_un`, connects, checks `SO_ERROR`, makes the fd nonblocking, and marks the client connected. Listen unlinks an existing path, binds, optionally listens for streams, makes the fd nonblocking, marks server listen, and stores the path in `private_data`. Accept creates a nonblocking child context. Datagram `sendto()` may retry once with a larger `SO_SNDBUF` after `EMSGSIZE`.

## State and Persistence Behavior

The backend stores the listen path as talloc-owned `private_data` but does not unlink it in `unixdom_close()`. Fd lifetime is otherwise managed by the common talloc destructor. Peer and local address getters return `LOCAL/unixdom` as a synthetic address with `port=0`.

## Dependencies and Integration Points

It depends on Unix socket APIs, Samba close-on-exec and errno-to-NTSTATUS mapping, and the common `socket_context` vtable. It is built as the internal `socket_unix` module and selected by family `"unix"`.

## Risks and Edge Cases

`unixdom_listen()` has a suspicious `my_address->sockaddr` branch that binds an uninitialized local `my_addr` instead of the supplied sockaddr. Stale socket path cleanup only happens before bind, not on close. Path length checks use `strlen()+1 > sizeof(sun_path)` but abstract namespace sockets are not represented. Datagram buffer growth retries only on `EMSGSIZE`.

## Test Signals

Useful tests should cover stream connect/listen/accept, datagram sendto, long path rejection, cleanup of preexisting socket paths, supplied `sockaddr_un` inputs, and close behavior around stale filesystem socket nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/socket_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/testsuite.c -->
# sources/user-network-fs/samba/source4/lib/socket/testsuite.c

## Purpose

`testsuite.c` provides local torture tests for the source4 socket abstraction. It validates basic UDP datagram behavior and TCP stream behavior over the `"ip"` backend on the best loopback interface address.

## Important APIs, Types, and Functions

`test_udp()` creates two datagram sockets, binds one, sends random data both directions with `socket_sendto()`/`socket_recvfrom()`, and checks addresses, ports, sizes, and bytes. `test_tcp()` creates a listener/client pair, connects with `socket_connect_ev()`, accepts, sends random bytes, receives them, and validates peer address and payload. `torture_local_socket()` registers the `udp` and `tcp` tests.

## Control Flow

Both tests load interface data from loadparm, choose a loopback address through `iface_list_best_ip()`, create sockets, bind/listen on port zero, discover the assigned local address, and exercise one round-trip or one client-to-server transfer. Failures are reported through torture assertions.

## State and Persistence Behavior

The tests allocate all sockets and blobs under the torture context, relying on talloc cleanup. They bind ephemeral local ports only and do not persist files or network configuration.

## Dependencies and Integration Points

The file integrates with Samba torture local suites, tevent, loadparm, interface discovery, random buffer generation, and the async connect helper from the socket subsystem.

## Risks and Edge Cases

Coverage is intentionally basic. It does not test Unix-domain sockets, IPv6, error paths, partial nonblocking mode, socket options, fd duplication, address conversion helpers, or TLS/encrypted socket behavior. Loopback selection depends on local interface configuration.

## Test Signals

Passing `torture_local_socket` confirms basic IPv4-style UDP/TCP behavior. Regressions in bind, ephemeral port discovery, send/recv byte accounting, or async TCP connect should show up here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/testsuite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/wscript_build -->
# sources/user-network-fs/samba/source4/lib/socket/wscript_build

## Purpose

This waf build script defines the source4 socket-related build units: interface discovery, IPv4 backend, Unix-domain backend, and the common `samba_socket` subsystem.

## Important APIs, Types, and Functions

It declares `netif` as a private library from `interface.c`, `socket_ip` and `socket_unix` as internal modules in subsystem `samba_socket`, and `samba_socket` as a subsystem built from `socket.c`, `access.c`, `connect_multi.c`, and `connect.c`.

## Control Flow

At configure/build time, waf evaluates these declarations to compile backend modules and link dependencies. Runtime backend selection still happens through `socket_getops_byname()`.

## State and Persistence Behavior

No runtime state is stored here. The script determines build graph persistence in generated waf metadata.

## Dependencies and Integration Points

`netif` depends on `samba-util`, `interfaces`, and `samba-hostconfig`. `socket_ip` depends on `samba-errors`; `socket_unix` depends on `talloc`; `samba_socket` has public deps `talloc` and `LIBTSOCKET` and private deps including `cli_composite`, `LIBCLI_RESOLVE`, `socket_ip`, `socket_unix`, and `access`.

## Risks and Edge Cases

Because `socket_ip` and `socket_unix` are internal modules but also direct dependencies of `samba_socket`, build graph changes can affect backend availability. IPv6 is conditional in C code, not expressed as a separate build target here.

## Test Signals

Successful waf configuration/compilation of `samba_socket`, plus local socket torture tests, are the main signals. Dependency changes should be validated by clean builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/packet.c -->
# sources/user-network-fs/samba/source4/lib/stream/packet.c

## Purpose

`packet.c` implements a helper layer that turns a byte stream socket into framed request callbacks and queued packet sends. It handles partial reads, multiple frames in one read, event-boundary scheduling, serialized callbacks, temporary receive disablement, and write queue callbacks.

## Important APIs, Types, and Functions

The central type is private `struct packet_context`. Exported setup functions include `packet_init()`, callback/error/private setters, socket/event/fd setters, `packet_set_serialise()`, `packet_set_initial_read()`, `packet_set_nofree()`, and `packet_set_unreliable_select()`. Runtime APIs are `packet_recv()`, `packet_recv_disable()`, `packet_recv_enable()`, `packet_queue_run()`, `packet_send_callback()`, `packet_send()`, and full-request helpers `packet_full_request_nbt()` and `packet_full_request_u32()`.

## Control Flow

`packet_recv()` is called when the fd is readable. It guards against reentrant processing, honors receive disablement, computes bytes to read from known packet size, initial-read hint, or `socket_pending()`, expands the partial buffer, reads through `socket_recv()`, and asks `full_request()` whether a complete frame is present. Complete frames are passed to `callback()`. Extra buffered frames are either processed immediately or scheduled on a zero-time tevent timer to preserve event boundaries. `packet_queue_run()` drains queued sends until the socket would block or the queue empties.

## State and Persistence Behavior

The packet context persists partial input bytes, current packet size, send queue elements, callback pointers, and flags. Its destructor refuses to free while callbacks are busy and defers actual free until processing unwinds. Send blobs are either stolen into queue elements or referenced when `nofree` is set.

## Dependencies and Integration Points

It depends on dlinklist helpers, tevent fd/timer APIs, `socket_context`, `DATA_BLOB`, and SMB length helpers from `libcli/raw/smb.h`. It is used by higher-level stream protocols that need framed messages over source4 sockets.

## Risks and Edge Cases

Correctness depends on `full_request()` returning consistent sizes. The code contains explicit overflow and pointer-wrap checks, but a buggy callback can still report invalid packet sizes. Default error handling frees `private_data`, which is a strong ownership convention. `unreliable_select` loops can read buffered TLS data without fd readiness but must avoid spinning. `packet_recv_enable()` scheduling depends on `packet_size >= num_read`, which is subtle for partial buffered packets.

## Test Signals

Useful tests should cover NBT and u32 framing, multiple frames in one read, partial frames, callback errors, send callbacks, `nofree` ownership, serialized reentrancy, receive disable/enable, and TLS-like unreliable select behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/packet.h -->
# sources/user-network-fs/samba/source4/lib/stream/packet.h

## Purpose

`packet.h` declares the framed packet stream API implemented by `packet.c`. It exposes an opaque `packet_context`, callback types, configuration setters, receive and send entry points, and standard frame-size detectors.

## Important APIs, Types, and Functions

Callback types are `packet_full_request_fn_t`, `packet_callback_fn_t`, `packet_send_callback_fn_t`, and `packet_error_handler_fn_t`. Public APIs include `packet_init()`, setter functions for callbacks/private/socket/event/fd/flags, `packet_recv()`, `packet_recv_disable()`, `packet_recv_enable()`, `packet_set_unreliable_select()`, `packet_send()`, `packet_send_callback()`, `packet_queue_run()`, `packet_full_request_nbt()`, and `packet_full_request_u32()`.

## Control Flow

The header itself has no runtime flow. Callers wire a context by setting socket, frame detector, receive callback, optional error handler, tevent fd/event context, then invoke `packet_recv()` from read readiness and `packet_queue_run()` from write readiness.

## State and Persistence Behavior

`packet_context` is opaque; callers manage it by talloc lifetime and setter functions. The API implies persistent buffering and queued-send state across readiness callbacks.

## Dependencies and Integration Points

The header forward-declares tevent and socket types and depends on Samba `NTSTATUS`, `DATA_BLOB`, and `TALLOC_CTX` through the includer. It bridges stream transports and socket backends.

## Risks and Edge Cases

The default error-handler ownership convention is not visible from the header, so callers may be surprised that private data can be freed. Callers must keep sent blob memory valid unless allowing `packet_send()` to steal it or enabling `nofree` with talloc-referenced data.

## Test Signals

Compile tests catch callback signature drift. Runtime tests should use custom frame detectors to validate callback ordering, error propagation, and queue behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/wscript_build -->
# sources/user-network-fs/samba/source4/lib/stream/wscript_build

## Purpose

This waf script defines the `LIBPACKET` subsystem that builds the packet framing helper.

## Important APIs, Types, and Functions

It declares `bld.SAMBA_SUBSYSTEM('LIBPACKET', source='packet.c', deps='LIBTLS')`.

## Control Flow

At build time, waf compiles `packet.c` into `LIBPACKET` and ensures `LIBTLS` is available before linking consumers.

## State and Persistence Behavior

No runtime state is present. The declaration affects generated build metadata.

## Dependencies and Integration Points

The explicit `LIBTLS` dependency reflects packet users that may operate over TLS-wrapped stream behavior, especially unreliable select handling.

## Risks and Edge Cases

If `packet.c` is used without direct TLS symbols, this dependency can still pull TLS-related build requirements into consumers. Build graph changes should confirm this remains intentional.

## Test Signals

Clean waf builds of `LIBPACKET` and consumers are the relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/stream/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tls.h -->
# sources/user-network-fs/samba/source4/lib/tls/tls.h

## Purpose

`tls.h` declares Samba source4 TLS support: certificate autogeneration, TLS parameter construction, asynchronous TLS stream wrapping, synchronous TLS I/O, certificate verification modes, channel bindings, QUIC handshakes, and ngtcp2-backed QUIC stream connection.

## Important APIs, Types, and Functions

The main public types are opaque `struct tstream_tls_params` and `struct tstream_tls_sync`, plus `enum tls_verify_peer_state`. APIs include `tls_cert_generate()`, `tls_verify_peer_string()`, client/server parameter constructors and loadparm wrappers, `tstream_tls_params_quic_prepare()`, enabled/verify/peer-name accessors, `tstream_tls_channel_bindings()`, async `tstream_tls_connect_send/recv()` and `tstream_tls_accept_send/recv()`, sync read/write/pending/setup/channel-binding functions, `tstream_tls_quic_handshake_send/recv()`, blocking `tstream_tls_quic_handshake()`, and `tstream_tls_ngtcp2_connect_send/recv()`.

## Control Flow

The header defines the public setup sequence: create TLS params from explicit values or loadparm, optionally prepare QUIC, wrap an existing `tstream_context` asynchronously as client/server or set up sync callbacks, then use returned streams through generic tstream operations.

## State and Persistence Behavior

TLS parameters hold certificate credentials, DH params, priority strings, verification policy, peer name, and QUIC enablement internally. Channel bindings become available only after a successful handshake.

## Dependencies and Integration Points

It includes `lib/socket/socket.h`, forward-declares loadparm and tstream types, and exposes APIs consumed by LDAP/SMB transports and QUIC paths. Implementations depend on GnuTLS, tevent, tsocket, loadparm, optional kernel QUIC, and optional ngtcp2.

## Risks and Edge Cases

Verification mode semantics are security-sensitive. `TLS_VERIFY_PEER_CA_AND_NAME` and stricter require a usable peer name. QUIC preparation is conditional and may disable itself for IP peer names. Callers must not assume channel bindings exist before handshake success.

## Test Signals

Compile coverage with and without optional QUIC/ngtcp2 libraries is important. Runtime tests should cover every verify-peer mode, missing CA/CRL/peer-name failures, client/server stream handshakes, sync setup, and QUIC feature gating.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tls_tstream.c -->
# sources/user-network-fs/samba/source4/lib/tls/tls_tstream.c

## Purpose

`tls_tstream.c` implements TLS and QUIC transport wrappers for Samba tstreams. It builds GnuTLS client/server parameters, verifies peers, exposes TLS channel bindings, wraps existing tstreams with asynchronous encrypted read/write/disconnect operations, supports synchronous callback-based TLS, optionally drives kernel QUIC handshakes, and optionally implements an ngtcp2 client stream over an existing connected UDP socket.

## Important APIs, Types, and Functions

Public functions include `tls_verify_peer_string()`, TLS parameter constructors/accessors, `tstream_tls_channel_bindings()`, `_tstream_tls_connect_send()`, `tstream_tls_connect_recv()`, `_tstream_tls_accept_send()`, `tstream_tls_accept_recv()`, sync TLS APIs, `tstream_tls_quic_handshake_send/recv()`, `tstream_tls_quic_handshake()`, `_tstream_tls_ngtcp2_connect_send()`, and `tstream_tls_ngtcp2_connect_recv()`. Key internal state types are `struct tstream_tls`, `struct tstream_tls_params_internal`, `struct tstream_tls_sync`, and, under `HAVE_LIBNGTCP2`, `struct tstream_ngtcp2` plus queued buffer structures.

## Control Flow

TLS parameter construction loads trust roots, CRLs, priority strings, peer names, server cert/key files, and DH parameters. `tstream_tls_prepare_gnutls()` initializes a GnuTLS session, applies priorities and credentials, sets SNI when appropriate, and configures server certificate requests. Async connect/accept create a `tstream_context`, install GnuTLS pull/push callbacks that delegate to the plain stream, and drive `gnutls_handshake()` through tevent retries. Read/write copy iovecs into fixed buffers and call `gnutls_record_recv()`/`gnutls_record_send()` until complete or blocked. Disconnect uses `gnutls_bye()`. Sync setup performs a blocking-style handshake through caller-supplied send/recv callbacks. QUIC paths either use kernel `quic_handshake_*` steps or ngtcp2 callbacks and timers to drive handshake, datagram I/O, stream read/write queues, monitoring, and disconnect.

## State and Persistence Behavior

TLS stream state persists the plain stream, current error, GnuTLS session, server/client role, verification policy, peer name, channel bindings, current tevent context, pending push/pull subrequests, and active management/read/write/disconnect requests. TLS params hold long-lived credentials referenced by sessions. ngtcp2 state persists connection IDs, path addresses, buffers for pushed/pending/read data, timers, keepalive settings, and request pointers. No external database is modified, but server parameter setup may trigger certificate autogeneration through `tlscert.c`.

## Dependencies and Integration Points

The implementation depends on GnuTLS, Samba GnuTLS helpers, tevent, tsocket internals, tdgram, loadparm, file utilities, time utilities, optional `<netinet/quic.h>`, optional ngtcp2 and `ngtcp2_crypto_gnutls`, and Samba debug/NTSTATUS helpers. It integrates with generic tstream users and TLS configuration from `loadparm_context`.

## Risks and Edge Cases

This file is concurrency- and state-machine-heavy. Errors are latched in `tlss->error`/`si->error` and can complete outstanding requests later. The async GnuTLS pull/push callbacks must map `EAGAIN` exactly or handshakes/read/write can stall. Verification policy around IP peer names, missing CRLs, and strict mode is security-sensitive. Server key permissions are enforced because of CVE-2013-4476. QUIC support is compile-time conditional, so callers must handle `NT_STATUS_INVALID_PARAMETER_MIX`. ngtcp2 cleanup tries to flush close frames without blocking and has many request ownership paths.

## Test Signals

High-value tests include client and server TLS handshakes with valid, expired, revoked, wrong-name, IP-name, missing-CA, and missing-CRL certificates; channel-binding validation; simultaneous read/write during handshake and shutdown; sync callback I/O with EINTR/EAGAIN; loadparm-driven configuration; kernel QUIC handshake success/failure when available; and ngtcp2 stream read/write/disconnect under packet loss, blocked congestion window, timeout, and peer reset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tls_tstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tlscert.c -->
# sources/user-network-fs/samba/source4/lib/tls/tlscert.c

## Purpose

`tlscert.c` autogenerates a temporary self-signed CA certificate, host certificate, and private key for Samba TLS use when configured TLS files do not already exist.

## Important APIs, Types, and Functions

The public function is `tls_cert_generate()`. It uses GnuTLS X.509 certificate/private-key objects, constants for organization/unit/common names, a 700-day lifetime, and `RSA_BITS`, which selects 3072 bits in FIPS mode and 4096 bits otherwise.

## Control Flow

The function first refuses to run if any of key, cert, or CA files already exists. It generates host and CA private keys, creates a CA certificate with CA/key-cert-sign usage, creates a host certificate with DNS subject alt names for the primary and additional hostnames, signs the host certificate with both itself and the CA key path, exports host cert, CA cert, and private key as PEM, and saves the private key with mode `0600`. A macro funnels GnuTLS failures to a common failure label.

## State and Persistence Behavior

This file persists new PEM files to the configured paths. It does not overwrite partial existing TLS material. Generated certificates use current time for activation/serial and expire after the fixed lifetime.

## Dependencies and Integration Points

It depends on GnuTLS X.509 APIs and Samba file helpers `file_exist()`, `file_save()`, and `file_save_mode()`. Server TLS parameter setup in `tls_tstream.c` calls this when the CA file is absent.

## Risks and Edge Cases

The all-or-nothing guard skips generation if only one of the three files exists, which can leave incomplete TLS configuration for callers to diagnose later. The failure path logs but does not clean up files already written before a later failure. The generated CA and host certificate are temporary self-signed material, so strict external trust still requires proper CA deployment.

## Test Signals

Tests should cover clean autogeneration, existing-file skip behavior, additional SANs, FIPS/non-FIPS key sizes, private-key file mode, unwritable parent directories, and server parameter setup consuming the generated files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/tlscert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/wscript_build -->
# sources/user-network-fs/samba/source4/lib/tls/wscript_build

## Purpose

This waf script defines the `LIBTLS` subsystem for source4 TLS, certificate generation, TLS tstream wrapping, and optional QUIC-related integration.

## Important APIs, Types, and Functions

It builds `tlscert.c` and `tls_tstream.c` into `LIBTLS` and declares public dependencies: `talloc`, `gnutls`, `GNUTLS_HELPERS`, `samba-hostconfig`, `LIBTSOCKET`, `tevent`, `tevent-util`, `quic`, `libngtcp2`, and `libngtcp2_crypto_gnutls`.

## Control Flow

At build time, waf uses this dependency graph to expose TLS symbols to consumers. Conditional C compilation still controls whether kernel QUIC and ngtcp2 code is active.

## State and Persistence Behavior

No runtime state exists in the build script. It persists only in build metadata.

## Dependencies and Integration Points

The dependency list makes TLS a central integration point between GnuTLS, Samba host configuration, tsocket/tstream infrastructure, tevent, and optional QUIC libraries.

## Risks and Edge Cases

Optional library availability must match the feature macros used in `tls_tstream.c`. Dependency churn can affect many consumers because `LIBTLS` is pulled by `LIBPACKET` and transport code.

## Test Signals

Clean builds with default options and feature-enabled QUIC/ngtcp2 builds are the main signals. Link tests should confirm consumers resolve TLS and optional QUIC symbols correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/tls/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/cliconnect.c -->
# sources/user-network-fs/samba/source4/libcli/cliconnect.c

## Purpose

`cliconnect.c` provides convenience wrappers for SMB1 client connection setup and teardown. It connects a socket, negotiates protocol, performs session setup, tree-connects to a share, builds a full `smbcli_state`, disconnects a tree, initializes state, and parses UNC names.

## Important APIs, Types, and Functions

Exports include `smbcli_socket_connect()`, `smbcli_negprot()`, `smbcli_session_setup()`, `smbcli_tconX()`, `smbcli_full_connection()`, `smbcli_tdis()`, `smbcli_state_init()`, and `smbcli_parse_unc()`. The helper `terminate_path_at_separator()` splits mutable UNC components.

## Control Flow

The classic sequence is socket connect through `smbcli_sock_connect()`, transport initialization and `smb_raw_negotiate()`, session allocation and `smb_composite_sesssetup()`, then tree allocation and `smb_raw_tcon()`. `smbcli_full_connection()` delegates to `smbcli_tree_full_connection()` and wraps the returned tree/session/transport in a `smbcli_state`. `smbcli_tconX()` chooses password encoding based on negotiated security mode and enables session-key protection when extended signatures are returned.

## State and Persistence Behavior

`smbcli_state` owns or references socket, transport, session, and tree objects under talloc. Successful negotiation consumes `cli->sock` into `cli->transport`. Tree connect persists the TID and session VUID in client state. No server-side data is modified except normal authentication/session/share connection state.

## Dependencies and Integration Points

The file depends on `libcli/libcli.h`, raw SMB1 client APIs, authentication helpers, SMB composite session setup, resolve/loadparm/tevent contexts, and smbXcli session signing helpers.

## Risks and Edge Cases

`smbcli_tconX()` can leak `mem_ctx` on an early invalid short challenge return. Share-level password handling is legacy-sensitive. `smbcli_parse_unc()` mutates allocated copies and only accepts `//` or `\\` prefixes with both server and share. The wrapper returns booleans in some places and NTSTATUS in others, requiring callers to retrieve detailed errors from lower layers.

## Test Signals

Connection tests should cover user-level and share-level security, encrypted share passwords, extended signatures, failed negotiate/session/tree-connect paths, full connection cleanup, and UNC parsing for slash and backslash separators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/cliconnect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clideltree.c -->
# sources/user-network-fs/samba/source4/libcli/clideltree.c

## Purpose

`clideltree.c` implements recursive deletion of a remote SMB path using the `smbcli_*` convenience APIs. It deletes files, descends into directories, clears read-only attributes when needed, and returns a count of deleted entries or `-1` on failure.

## Important APIs, Types, and Functions

The public function is `smbcli_deltree()`. Internal `struct delete_state` tracks the tree, total deletions, and any failure. Callback `delete_fn()` is passed to `smbcli_list()` for recursive directory traversal.

## Control Flow

`smbcli_deltree()` first tries to unlink the target as a file and treats missing paths as success with zero deletions. If deletion is denied, it clears attributes and retries. For directories it builds `path\\*`, deletes matching files via `smbcli_unlink_wcard()`, lists directories including hidden/system entries, recursively calls `delete_fn()`, then removes the directory, again clearing attributes on `NT_STATUS_CANNOT_DELETE`.

## State and Persistence Behavior

The function mutates the remote SMB share by deleting files/directories and changing read-only attributes to normal. Local state is transient C heap strings plus the stack `delete_state`.

## Dependencies and Integration Points

It depends on directory attribute macros, `smbcli_unlink()`, `smbcli_unlink_wcard()`, `smbcli_list()`, `smbcli_setatr()`, `smbcli_rmdir()`, and `smbcli_errstr()`/`smbcli_nt_error()` for error handling.

## Risks and Edge Cases

Path construction uses `strdup()`/`asprintf()` and manual trimming. Some allocation failures in callbacks simply return without setting `failed`, so deletions can be silently skipped. Concurrent directory changes can cause list/delete races. Clearing read-only attributes changes remote metadata even if later deletion fails.

## Test Signals

Tests should cover nonexistent targets, single files, read-only files/directories, hidden/system entries, nested trees, allocation/error injection if possible, and server races where entries disappear during traversal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clideltree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clifile.c -->
# sources/user-network-fs/samba/source4/libcli/clifile.c

## Purpose

`clifile.c` provides synchronous convenience wrappers for SMB1 file and directory operations. It maps POSIX-like helper calls and Samba test helpers onto raw SMB open, close, rename, delete, attribute, lock, truncate, path, disk, and temporary-file requests.

## Important APIs, Types, and Functions

Exports include Unix extension helpers `smbcli_unix_symlink()`, `smbcli_unix_hardlink()`, `smbcli_unix_chmod()`, `smbcli_unix_chown()`, file operations `smbcli_rename()`, `smbcli_unlink()`, `smbcli_unlink_wcard()`, `smbcli_mkdir()`, `smbcli_rmdir()`, `smbcli_nt_delete_on_close()`, `smbcli_nt_create_full()`, `smbcli_open()`, `smbcli_close()`, locks/unlocks with 32-bit and 64-bit offsets, `smbcli_getattrE()`, `smbcli_getatr()`, `smbcli_setatr()`, `smbcli_fsetatr()`, `smbcli_ftruncate()`, `smbcli_chkpath()`, `smbcli_dskattr()`, and `smbcli_ctemp()`.

## Control Flow

Most functions fill a raw SMB union at a specific information level and call the matching `smb_raw_*` function. `smbcli_open()` converts POSIX flags into SMBopenX open functions and access modes. Wildcard unlink lists matching entries and deletes each resolved name. 64-bit lock helpers fall back to 32-bit locks when the negotiated transport lacks `CAP_LARGE_FILES`. Query helpers copy selected output fields to optional caller pointers.

## State and Persistence Behavior

These functions mutate remote files/directories, locks, attributes, timestamps, delete-on-close flags, and file sizes. They maintain little local state beyond temporary talloc contexts and return fnums from successful opens. Wildcard delete tracks the first failed name for debugging but does not return it to callers.

## Dependencies and Integration Points

The file depends on raw SMB1 unions/functions from `libcli/raw`, `struct smbcli_tree`, negotiated transport capabilities, Unix permission conversion, and `smbcli_list()` for wildcard deletion.

## Risks and Edge Cases

Some wrappers return `-1` instead of NTSTATUS, losing details. `smbcli_unlink_wcard()` initializes `state->status` to zero through talloc, which corresponds to OK, and only preserves the first delete failure. `smbcli_chkpath()` uses `strdup()` without null checks. `smbcli_open()` only sets explicit read/write bits and leaves read-only as default access mode. Large `off_t` values can be truncated on fallback 32-bit lock paths.

## Test Signals

Coverage should include every wrapper against a test share: Unix extensions, wildcard delete, create dispositions, sharing modes, delete-on-close, lock conflict behavior, large-file locks with and without capability, timestamp/attribute round trips, truncation, disk attribute queries, and temporary file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clifile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clilist.c -->
# sources/user-network-fs/samba/source4/libcli/clilist.c

## Purpose

`clilist.c` implements SMB1 directory listing convenience functions. It supports modern TRANS2 find-first/find-next searches and old LANMAN search calls, normalizing returned entries into `struct clilist_file_info` and invoking a caller callback for each result.

## Important APIs, Types, and Functions

Public APIs are `smbcli_list_new()`, `smbcli_list_old()`, and `smbcli_list()`. Internal helpers are `interpret_long_filename()`, `smbcli_list_new_callback()`, `interpret_short_filename()`, and `smbcli_list_old_callback()`. `struct search_private` holds accumulated entries, counts, selected data level, last name, and old-style resume id.

## Control Flow

`smbcli_list()` selects old search for `PROTOCOL_LANMAN1` or older, otherwise new TRANS2 search. New search chooses `BOTH_DIRECTORY_INFO` when NT SMBs are available or `STANDARD` otherwise, loops first/next calls until end-of-search or zero results, accumulates entries, then calls the user callback once per accumulated entry. Old search follows the same pattern using `RAW_SEARCH_SEARCH` and resume ids.

## State and Persistence Behavior

Listing is read-only from the share perspective but may keep server-side search handles until close-if-end behavior or end of search. Locally it accumulates all entries in a talloc array before invoking callbacks, so memory use scales with result count.

## Dependencies and Integration Points

The file depends on raw search APIs, negotiated protocol/capabilities, NT time conversion, and the `clilist_file_info` contract used by delete and wildcard helpers.

## Risks and Edge Cases

Accumulating the entire result set can be expensive for large directories. In `smbcli_list_new()`, an error during a subsequent find-next returns `-1` without freeing `state.mem_ctx`. Callback invocation is deferred until after enumeration, so callers cannot stop early. Resume by last name can be fragile with changing directories.

## Test Signals

Tests should cover old and new protocol paths, large directories, Unicode/short-name entries, hidden/system attributes, changing directories during enumeration, no-match results, and callback-visible ordering/counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clilist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/climessage.c -->
# sources/user-network-fs/samba/source4/libcli/climessage.c

## Purpose

`climessage.c` implements legacy SMB messenger commands for starting, sending, and ending a message sequence to a host/user through an SMB tree connection.

## Important APIs, Types, and Functions

The public functions are `smbcli_message_start()`, `smbcli_message_text()`, and `smbcli_message_end()`. They manually build `SMBsendstrt`, `SMBsendtxt`, and `SMBsendend` requests with `smbcli_request_setup()`.

## Control Flow

Start appends username and host strings, sends and receives the request, checks tree error state, and returns the message group id from the response. Text sends the group id plus raw message bytes. End sends the group id to close the message sequence. Each path destroys the request on completion or failure.

## State and Persistence Behavior

Remote state is the server-side message group/session between start and end. Local state is only the returned integer group id. No persistent files are touched.

## Dependencies and Integration Points

It depends on low-level SMB request construction, string/byte append helpers, request send/receive, `smbcli_is_error()`, and SMB command constants.

## Risks and Edge Cases

This is legacy protocol functionality and may be unsupported by modern servers. The text function accepts a mutable `char *` even though it only sends bytes. Errors are collapsed to boolean false, so callers need tree error state for details.

## Test Signals

Tests require a server that supports messenger commands. Useful checks cover start/text/end success, invalid group ids, unsupported server responses, zero-length text, and non-ASCII message bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/climessage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clireadwrite.c -->
# sources/user-network-fs/samba/source4/libcli/clireadwrite.c

## Purpose

`clireadwrite.c` provides synchronous SMB1 file read/write convenience wrappers. It reads with SMBreadX, writes with SMBwriteX, and offers an older SMBwrite path that does not bypass zero-byte writes.

## Important APIs, Types, and Functions

Public APIs are `smbcli_read()`, `smbcli_write()`, and `smbcli_smbwrite()`. They fill `union smb_read` or `union smb_write` and call `smb_raw_read()`/`smb_raw_write()`.

## Control Flow

`smbcli_read()` computes a read block size from negotiated `max_xmit`, caps it at 64 KiB, loops until requested bytes are read or the server returns a short read, and advances offset and output buffer. `smbcli_write()` similarly chunks writes using writeX and advances by bytes actually written until complete. `smbcli_smbwrite()` uses the legacy write command, including for zero-length requests, and loops until all bytes are written or the server writes zero.

## State and Persistence Behavior

Reads do not mutate remote file data. Writes mutate remote file content at supplied offsets. No local persistent state is held beyond loop counters and raw request unions.

## Dependencies and Integration Points

The file depends on raw SMB read/write helpers, negotiated transport `max_xmit`, `MIN_SMB_SIZE`, and valid tree/fnum state created by connection/open wrappers.

## Risks and Edge Cases

Errors return `-1`, losing NTSTATUS detail. Block-size calculations assume negotiated `max_xmit` is larger than protocol overhead; negative or tiny values can lead to problematic sizes. `smbcli_write()` sets `parms.writex.in.data = buf`, then advances `buf` each iteration, so the pointer remains current but can be easy to misread. Offset types depend on `off_t` width.

## Test Signals

Tests should cover zero-length reads/writes, EOF short reads, large transfers spanning many chunks, small `max_xmit`, write modes for named pipes/cache behavior, and large offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clireadwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clitrans2.c -->
# sources/user-network-fs/samba/source4/libcli/clitrans2.c

## Purpose

`clitrans2.c` provides convenience wrappers for SMB TRANS2 file and path information queries. It fetches standard path info, all-info path/file metadata, file names by fnum, and alternate 8.3 names.

## Important APIs, Types, and Functions

Exports are `smbcli_qpathinfo()`, `smbcli_qpathinfo2()`, `smbcli_qfilename()`, `smbcli_qfileinfo()`, and `smbcli_qpathinfo_alt_name()`. They use `union smb_fileinfo` with levels `RAW_FILEINFO_STANDARD`, `RAW_FILEINFO_ALL_INFO`, `RAW_FILEINFO_NAME_INFO`, and `RAW_FILEINFO_ALT_NAME_INFO`.

## Control Flow

Each function creates a short-lived talloc context, fills the appropriate input path or fnum, calls `smb_raw_pathinfo()` or `smb_raw_fileinfo()`, frees the context, and copies selected outputs to optional caller pointers. Time values from all-info levels are converted from NT time to Unix time. Name-returning helpers duplicate strings for the caller.

## State and Persistence Behavior

The operations are read-only against the remote share. Locally they allocate temporary talloc memory and return heap-allocated strings from `strdup()` for name outputs.

## Dependencies and Integration Points

The file depends on raw path/file info APIs, NT time conversion, `struct smbcli_tree`, and caller conventions from `libcli.h`.

## Risks and Edge Cases

The `ino` output parameter in `smbcli_qpathinfo2()` is ignored, while `smbcli_qfileinfo()` sets it to zero. String outputs use `strdup()` and must be freed by callers; allocation failure is not checked before returning OK. `smbcli_qpathinfo_alt_name()` returns `smbcli_nt_error(tree)` on raw failure rather than the local status, which can differ.

## Test Signals

Tests should cover all query levels against files and directories, optional null output parameters, alternate-name absence/presence, Unicode names, allocation failure if injectable, and consistency between path and fnum all-info results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/clitrans2.c -->
