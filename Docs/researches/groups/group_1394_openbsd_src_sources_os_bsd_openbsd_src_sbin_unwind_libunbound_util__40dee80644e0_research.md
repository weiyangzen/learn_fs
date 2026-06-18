# Group Research: group_1394_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__40dee80644e0

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.c

Implements Unbound's event-driven networking layer over `ub_event`: per-thread event bases, UDP and TCP communication points, outgoing TCP/HTTP clients, local/raw descriptors, timers, signals, optional TLS, optional HTTP/2, optional DNS-over-QUIC, optional DNSTAP, optional DNSCrypt, and PROXYv2 address propagation.

Core event-base routines allocate `comm_base` and its private `internal_base`, dispatch or exit the loop, expose cached time pointers, and install slow-accept callbacks. Slow accept is triggered when `accept()` hits descriptor exhaustion; the base stops accept listeners, rate-limits logging, and schedules a timeout to resume accepting.

UDP support includes plain `recvfrom`/`sendto` and ancillary `recvmsg`/`sendmsg` variants. Send paths handle transient nonblocking failures, `ENOBUFS`/`ENOMEM` pressure, short sends, and verbosity-sensitive error squelching for unreachable, broadcast, IPv4-mapped, any-address, and permission errors. Ancillary UDP preserves destination/interface packet info so replies can use the same local address, and optionally records kernel receive timestamps.

PROXYv2 support is integrated into UDP packet handling and TCP stream startup. `consume_pp2_header()` validates the PROXYv2 header, extracts proxied IPv4 or IPv6 source address/port into `comm_reply.client_addr`, sets `is_proxied`, ignores LOCAL/UNSPEC headers, and rejects unsupported family/protocol combinations. UDP removes the header from the packet buffer; TCP consumes it as a stream preface before DNS length framing begins.

When compiled with ngtcp2, the file implements the DNS-over-QUIC server socket event path. It receives UDP datagrams with local address/ifindex/ECN metadata, decodes QUIC version/CIDs, sends version negotiation, performs stateless retry and token validation, creates and indexes `doq_conn` objects, handles read/write callbacks, blocked UDP sends, write-list fairness, timer ownership across workers, idle/closing/draining cleanup, stream replies, and reply drops. Connection lookup is keyed by address, local address, ifindex, and destination CID, with a secondary CID table lookup for migration-like cases.

TCP support preallocates handler comm points under an accept listener. Accepted handlers inherit parent settings, apply connection limits, optionally wrap with SSL, shrink idle timeouts under high handler usage, and return to the parent's free list on close. Read/write routines implement DNS-over-TCP two-byte length framing, partial IO accounting, optional simultaneous write-and-read mode, retry loops for "more read/write" flags, nonblocking connect completion checks, TCP Fast Open fallback, and platform-specific Winsock behavior.

TLS handling drives nonblocking OpenSSL handshakes and record IO. It toggles event interest for WANT_READ/WANT_WRITE, suppresses noisy common handshake failures at lower verbosity, logs certificate verification state when peer verification is required, and negotiates HTTP/2 by ALPN for HTTP comm points.

HTTP support covers outgoing and accepted HTTP handlers. HTTP/1.1 parsing processes status lines, `Content-Length`, `Transfer-Encoding: chunked`, chunk sizes, trailers, buffered fragments, final `NETEVENT_DONE`, and callback delivery for streamed response bodies. HTTP/2 support creates nghttp2 server sessions and stream lists, caps consecutive recv callbacks, sends SETTINGS for max streams, wires nghttp2 recv/send callbacks to SSL or sockets, closes stream mesh replies safely, and switches event interest based on nghttp2 want-read/want-write state.

Lifecycle functions create UDP, UDP-ancillary, DoQ, TCP listener, TCP handler, HTTP handler, outgoing TCP, outgoing HTTP, local, and raw comm points. Teardown removes events before closing descriptors, updates TCP connection-limit state, deletes HTTP/2 sessions and DoQ sockets, frees buffers and timeout state, and avoids closing descriptors marked `do_not_close`. Reply paths dispatch UDP replies immediately, enqueue TCP/HTTP/DoQ replies for later write events, log DNSTAP client responses when enabled, and drop/close transports according to type.

Timer and signal utilities wrap `ub_event` timeout and signal events behind `comm_timer` and `comm_signal`, with explicit create, set, disable, delete, bind, callback, and memory accounting helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.h

Declares the public and test-visible interface for the event networking layer implemented by `netevent.c`. The header documents the communication model: per-thread `comm_base`, UDP sockets, TCP accept sockets with preallocated handlers, TCP/HTTP/local/raw handlers, timers, signals, and temporary `comm_reply` structures passed to callbacks.

Defines callback error/status codes: `NETEVENT_NOERROR`, `NETEVENT_CLOSED`, `NETEVENT_TIMEOUT`, `NETEVENT_CAPSFAIL`, `NETEVENT_DONE`, and `NETEVENT_PKT_WRITTEN`. It also defines slow-accept timing/log throttling constants and a DoQ CID storage limit.

`struct comm_reply` carries the reply comm point, remote peer address, optional ancillary source-interface data, DNSCrypt state, maximum UDP size, PROXYv2-derived client address state, and, when DoQ is enabled, the DoQ ifindex, destination CID, stream ID, and source port needed to route replies back to the correct QUIC stream.

`struct comm_point` is the central transport state object. It stores event internals, socket metadata, fd, timeout, buffer ownership, TCP read/write counters, parent/free-list relationships, SSL handshake state, HTTP/1.1 parser state, HTTP/2 session and stream limits, optional DoQ socket state, DNSTAP environment, comm point type, PROXYv2 preface state, connection-close behavior flags, simultaneous read/write buffers, retry flags for draining more TCP work, TCP timeout/keepalive/connect-limit fields, optional TCP request multiplexing, optional TCP Fast Open state, optional DNSCrypt buffers, callback function, and callback argument.

The header exposes constructors for UDP, UDP with ancillary data, DoQ, TCP listeners, outgoing TCP, outgoing HTTP, local AF_UNIX descriptors, and raw descriptors. It exposes lifecycle and event-control helpers for close/delete, send/drop reply, direct UDP send, stop/start listening, change read/write interest, adjusted TCP timeouts, and memory accounting.

Timer and signal APIs expose lightweight event wrappers: create, set, disable, delete, query, bind, and callback entry points. Several internal callback functions are deliberately declared for checks and tests, including UDP, ancillary UDP, DoQ, TCP accept, TCP handler, HTTP handler, local/raw handlers, timer, signal, and slow-accept callbacks.

The HTTP/2 declarations define per-connection `http2_session`, `http_status`, and per-stream `http2_stream` state. Streams track method, content validation, content length, response status, endpoint validity, oversized-query status, independent query/response buffers, and mesh state cleanup hooks. nghttp2 callbacks and stream list helpers are declared under `HAVE_NGHTTP2`.

The DoQ declarations define compact IPv4/IPv6 socket address storage, `doq_server_socket` state, packet address metadata, packet initialization, packet sending, and timer callback entry points. The server socket stores shared connection table access, random state, address-validation settings, server CID length, idle timeout, static secret, QUIC SSL context, packet buffers, blocked packet retry state, timer marker, cached time pointers, and config.

Platform and feature-specific declarations include Winsock BIO callback wiring, TCP-connect errno logging policy, and SSL handshake log-squelch checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.c

Implements minimal PROXY protocol v2 helpers used by `netevent.c`. It stores caller-supplied endian-writing callbacks in a global `proxy_protocol_data` via `pp_init()`, so header generation can use the project's normal wire-format writers.

`pp_lookup_error()` maps parse error enum values to short static messages used in network error logs. The lookup table covers no error, undersized input, signature/version mismatch, unknown command, and unknown family/protocol.

`pp2_write_to_buf()` writes a PROXYv2 header for an IPv4 or IPv6 source address. It checks source presence and output capacity, emits the fixed signature, version/PROXY command, family/protocol based on stream versus datagram, address block length, source address, zero destination address, source port, and destination port field. It returns the total header size on success or `0` for unsupported families or insufficient space. AF_UNIX is not emitted.

`pp2_read_header()` validates an existing PROXYv2 header without interpreting all address data. It checks minimum header size, signature, version, full declared length availability, supported LOCAL/PROXY command, and supported UNSPEC, IPv4, IPv6, or UNIX family/protocol combinations. It returns `PP_PARSE_NOERROR` on success or a specific parse error code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.h

Defines the PROXY protocol v2 constants, wire layout, parse errors, and helper prototypes. The file explicitly supports only PROXYv2 and notes that TLVs are not currently supported.

Constants cover the 16-byte minimum header size, 12-byte v2 signature, and protocol version value. Enums define v2 commands (`LOCAL`, `PROXY`), address families (`UNSPEC`, `INET`, `INET6`, `UNIX`), transport protocols (`UNSPEC`, `STREAM`, `DGRAM`), and the accepted family/protocol byte combinations.

`struct pp2_header` models the fixed PROXYv2 header plus a union of address payloads: IPv4 address/port pair with 12-byte payload, IPv6 address/port pair with 36-byte payload, and AF_UNIX source/destination paths with 216-byte payload.

`enum pp_parse_errors` defines the parse result contract returned by `pp2_read_header()`: success, insufficient size, wrong v2 header, unknown command, or unknown family/protocol.

The declared API initializes endian writers (`pp_init()`), returns parse error text (`pp_lookup_error()`), writes a PROXYv2 header for IPv4/IPv6 source addresses (`pp2_write_to_buf()`), and validates a PROXYv2 header from a buffer (`pp2_read_header()`).
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/proxy_protocol.h -->