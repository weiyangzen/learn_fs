# Group Research: group_1386_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_servi_5ec2b7007dda

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All five listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.c

## Purpose
Implements Unbound's infrastructure cache for OpenBSD `unwind`: authoritative-server RTT tracking, EDNS capability/lame-server state, delegation-point rate limiting, client-IP rate limiting, and per-client wait limits.

## Main Responsibilities
- Create, resize, and destroy `struct infra_cache` and its slabhash-backed tables.
- Track per `(server address, zone)` health with TTL, RTT/RTO, probe delay, EDNS support, DNSSEC lameness, recursion lameness, type-specific lameness, and timeout counters.
- Implement delegation-point ratelimits with exact and below-domain overrides.
- Implement client-IP ratelimits and client-IP mesh wait limits, with separate defaults/trees for DNS Cookie clients.
- Provide memory accounting and hash/delete/compare callbacks for slabhash entries.

## Key Data Flow
- `infra_create()` builds `hosts`, `domain_rates`, `client_ip_rates`, `domain_limits`, and wait-limit trees from `struct config_file`.
- `infra_host()` looks up or creates an infra host entry before sending to an upstream server. Expired entries are reinitialized while preserving severe timeout/probe state when useful.
- `infra_rtt_update()` updates RTT state after success or timeout, increments A/AAAA/other timeout counters on loss, and clears counters on success.
- `infra_get_lame_rtt()` exposes lameness and RTT to server selection, including single-probe behavior for hosts near or above `PROBE_MAXRTO`.
- `infra_ratelimit_inc()/dec()/exceeded()` charge or release delegation-point query counts in a two-second `RATE_WINDOW`.
- `infra_ip_ratelimit_inc()` charges per-client address QPS, ignoring source port via `hash_addr(..., use_port=0)`.
- `infra_wait_limit_allowed/inc/dec()` uses the same client-IP rate table's `mesh_wait` field to limit outstanding replies.

## Important Functions
- `still_useful_timeout()`: returns a timeout below `USEFUL_SERVER_TOP_TIMEOUT` but above the RTT band, keeping bad servers probeable without fully selecting them.
- `infra_compfunc()`, `hash_infra()`: key infra entries by full socket address including port plus zone dname.
- `setup_domain_limits()`: parses configured ratelimit domains into a `name_tree`.
- `setup_wait_limits()`: initializes address-tree wait limits and adds loopback defaults with limit `-1`.
- `infra_find_ratelimit()`: resolves exact domain limit, nearest parent `below` limit, or global `infra_dp_ratelimit`.
- `infra_rate_max()`: returns current-second rate or window max when backoff is enabled.
- `check_ip_ratelimit()`: logs the first crossing of a client-IP limit with parsed query details when possible.

## Concurrency and Lifetime
Slabhash lookups return locked entries. Mutating operations request write locks; read operations unlock before returning. New entries are inserted after allocation and lock initialization. Domain-limit and wait-limit trees are rebuilt during `infra_adjust()` when cache sizing is unchanged; slabhashes are recreated when configured sizes/slabs differ.

## Edge Cases and Risks
- Infra host expiration intentionally preserves severe timeout/probe state to avoid immediately trusting an unresponsive server.
- Client-IP rate limiting only checks `infra_ip_ratelimit` as the top-level enabled flag, so cookie-specific limiting depends on ordinary IP limiting being enabled.
- `infra_adjust()` reapplies domain limits but does not rebuild wait-limit trees unless the whole cache is recreated.
- Allocation failures in rate-entry creation are mostly treated as non-fatal and may allow traffic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.h

## Purpose
Declares the infrastructure cache API and data structures used by Unbound services for upstream-server health, EDNS/lameness knowledge, domain/client ratelimits, and wait limits.

## Key Types
- `struct infra_key`: slabhash key for a server address plus zone name.
- `struct infra_data`: cached server metadata: TTL, probe delay, RTT estimator, EDNS version/known flag, DNSSEC/recursion/type lameness, and A/AAAA/other timeout counters.
- `struct infra_cache`: top-level owner for host cache, domain rate table, domain limit tree, client-IP rate table, and wait-limit netblock trees.
- `struct domain_limit_data`: name-tree node with exact and below-domain QPS limits.
- `struct rate_key` / `struct rate_data`: delegation-point QPS key and two-second counter window.
- `struct ip_rate_key`: client address key for IP ratelimit and wait-count tracking.
- `struct wait_limit_netblock_info`: address-tree node with configured outstanding-wait limit.

## Constants and Globals
- `TIMEOUT_COUNT_MAX`: allows limited type-specific probes before marking a server unusable for that qtype class.
- `PROBE_MAXRTO`: external probe threshold for high RTO values.
- `RATE_WINDOW`: two-second rate tracking window.
- `infra_dp_ratelimit`, `infra_ip_ratelimit`, `infra_ip_ratelimit_cookie`: process-global configured ratelimits.

## API Surface
- Lifecycle/configuration: `infra_create()`, `infra_delete()`, `infra_adjust()`.
- Host health: `infra_host()`, `infra_lookup_nottl()`, `infra_rtt_update()`, `infra_update_tcp_works()`, `infra_get_host_rto()`.
- Capability/lameness: `infra_set_lame()`, `infra_edns_update()`, `infra_get_lame_rtt()`.
- Domain ratelimit: `infra_ratelimit_inc()`, `infra_ratelimit_dec()`, `infra_ratelimit_exceeded()`, `infra_find_ratelimit()`, `infra_rate_max()`.
- Client-IP ratelimit and wait limits: `infra_ip_ratelimit_inc()`, `infra_wait_limit_allowed()`, `infra_wait_limit_inc()`, `infra_wait_limit_dec()`.
- Tree setup/free helpers exported for tests or config reload code.
- Slabhash callback functions for infra, domain-rate, and IP-rate tables.

## Design Notes
The header exposes enough internals for unit tests and other resolver modules to inspect timing, lameness, and ratelimit behavior. It also documents lock expectations: `infra_lookup_nottl()` can return read- or write-locked entries, and array/cache users must unlock entries they obtain.

## Dependencies
Depends on Unbound utility infrastructure: `lruhash`, `dnstree`, `rtt`, `netevent`, and message reply/query structures. It is tightly coupled to resolver server selection, mesh wait accounting, and configuration parsing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.c

## Purpose
Implements the RRset cache wrapper around Unbound's slabhash, including insertion/update policy, TTL checks, LRU touch behavior, security-status propagation, wildcard insertion, and selective cache removal.

## Main Responsibilities
- Create/delete/adjust `struct rrset_cache`.
- Safely touch LRU state without holding other RRset locks.
- Merge newly parsed RRsets with cached RRsets according to TTL, trust, security status, data equality, and special NS behavior.
- Lookup RRsets with expiration checks, including a short grace for upstream TTL=0 DNAME synthesis.
- Lock/unlock sorted arrays of RRset references used by message-cache entries.
- Update/check security status when validation improves cached or in-flight RRsets.
- Remove or detect expired parent RRsets above a query name.

## Important Functions
- `rrset_cache_create()`: creates a slabhash using packed-RRset size/compare/delete callbacks and installs `rrset_markdel()`.
- `rrset_cache_touch()`: locks the target slab then entry, verifies id/hash, and touches LRU. Comments explicitly warn callers not to hold any RRset lock.
- `need_to_update_rrset()`: central update policy. Prefers unexpired, secure, non-bogus, and higher-trust data; constrains NS TTL extension to reduce ghost-domain persistence.
- `rrset_cache_update()`: looks up existing data, possibly returns cached superior reference, inserts replacement, and changes IDs for changed NSEC/NSEC3/DNAME data so message-cache proofs are invalidated.
- `rrset_cache_update_wildcard()`: copies an RRset and rewrites owner name to `*.<closest-encloser>`.
- `rrset_cache_lookup()`: builds a stack key, looks up slabhash, and rejects expired data except TTL=0 upstream DNAMEs within `DNAME_TTL0_GRACE_SECONDS`.
- `rrset_array_lock()/unlock()/unlock_touch()`: lock reference arrays once per duplicate key and optionally touch LRU after releasing locks.
- `rrset_update_sec_status()` / `rrset_check_sec_status()`: copy better validation/trust state between a provided RRset and cache entry if rdata still matches.
- `rrset_cache_remove_above()` and `rrset_cache_expired_above()`: walk parent labels to evict or inspect parent RRsets.

## Concurrency and Lifetime
The implementation relies on slabhash and per-entry locks. Inserted RRsets become immutable without holding their entry lock. The cache update path has an acknowledged gap between unlocking an existing entry and inserting replacement data; comments treat races as acceptable cache behavior.

## Edge Cases and Risks
- TTL=0 DNAME grace is intentionally non-RFC caching behavior for immediate synthesis load reduction.
- `rrset_array_unlock_touch()` may skip LRU touches on regional allocation failure but still releases locks.
- NS updates deliberately avoid extending TTL past the cached entry in several cases, preventing stale delegation persistence.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.h

## Purpose
Declares the RRset cache API used by Unbound's resolver and message-cache layers.

## Key Type
- `struct rrset_cache`: a thin wrapper whose first member is `struct slabhash table`, allowing slabhash lifecycle functions to manage the allocated object.

## API Surface
- Lifecycle: `rrset_cache_create()`, `rrset_cache_delete()`, `rrset_cache_adjust()`.
- LRU/cache updates: `rrset_cache_touch()`, `rrset_cache_update()`, `rrset_cache_update_wildcard()`.
- Lookup: `rrset_cache_lookup()` returns a locked packed RRset or `NULL`.
- Reference-array locking: `rrset_array_lock()`, `rrset_array_unlock()`, `rrset_array_unlock_touch()`.
- Validation status: `rrset_update_sec_status()`, `rrset_check_sec_status()`.
- Parent cleanup/inspection: `rrset_cache_remove_above()`, `rrset_cache_expired_above()`.
- Direct removal and deletion marking: `rrset_cache_remove()`, `rrset_markdel()`.

## Contract Notes
Callers must unlock returned RRsets. `rrset_cache_touch()` must not be called while holding any RRset lock because it takes locks in the opposite direction from normal slabhash lookup. Reference arrays are expected to be sorted, but duplicate references are explicitly handled.

## Dependencies
Uses packed RRset structures, slabhash/lruhash storage, regional scratch allocation, and config/alloc-cache helpers from Unbound.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.c

## Purpose
Implements Unbound's listener setup and runtime request handling for DNS transports in OpenBSD `unwind`: UDP, TCP, local sockets, TLS/DoT, HTTP/2 DoH, DNSCrypt hooks, PROXYv2 flags, UDP ancillary packet info, socket timestamping, and DNS-over-QUIC when compiled with ngtcp2.

## Main Responsibilities
- Create UDP/TCP/local listening sockets with platform-specific options.
- Build `listen_port` lists from config interfaces, wildcard/default addresses, automatic interfaces, and per-interface port overrides.
- Convert open ports into `comm_point` event handlers.
- Track stream-response memory, HTTP/2 query buffers, and HTTP/2 response buffers with locks.
- Manage pipelined TCP query state and queued responses.
- Parse and service HTTP/2 DoH streams with nghttp2 callbacks.
- Manage DoQ connection tables, connection IDs, timers, streams, packet I/O, TLS/QUIC setup, and memory accounting.

## Socket Setup
- `create_udp_sock()` handles systemd activation, `SO_REUSEADDR`, `SO_REUSEPORT`/`SO_REUSEPORT_LB`, transparent/freebind options, receive/send buffers, DSCP, IPv6-only behavior, IPv6 minimum MTU/PMTU controls, IPv4 PMTU behavior, bind, and nonblocking mode.
- `create_tcp_accept_sock()` creates/listens TCP sockets with reuse, transparent/freebind, MSS, `TCP_NODELAY`, DSCP, IPv6-only behavior, TCP Fast Open, and nonblocking mode.
- `create_local_accept_sock()` creates AF_LOCAL stream sockets, unlinks stale paths, binds, listens, and supports systemd activation where available.
- `set_recvpktinfo()` enables destination-address ancillary data for wildcard/automatic UDP and DoQ sockets.
- `set_recvtimestamp()` enables packet timestamps for socket-queue timeout behavior.

## Port and Listener Construction
- `ports_create_if()` classifies an interface/port as ordinary DNS, TLS, HTTPS/DoH, DNSCrypt, PROXYv2, or DoQ. It rejects unsupported combinations such as PROXYv2 with DNSCrypt/DoH/DoQ and blocks DoQ on port 53.
- `listening_ports_open()` applies config flags for IPv4/IPv6, UDP/TCP, automatic interfaces, extra automatic ports, and explicit interface arrays.
- `resolve_interface_names()` expands interface names to concrete IPv4/IPv6 addresses with scope IDs when `getifaddrs()` is available.
- `listen_create()` converts each `listen_port` into an event `comm_point`, assigns the appropriate SSL context, DNSCrypt buffer, DoQ table, callback, and transport type.

## TCP Stream Handling
- `tcp_req_info_create/delete/clear()` own per-connection pipelined TCP state.
- Open mesh requests are tracked in `tcp_req_open_item`; finished replies are queued in `tcp_req_done_item`.
- `tcp_req_info_handle_readdone()` invokes the worker callback, handles immediate replies, mesh-deferred replies, and connection drops.
- `tcp_req_info_send_reply()` either writes immediately or queues a copied response subject to `stream_wait_max`.
- `tcp_req_info_handle_writedone()` resumes reading or sends the next queued reply.
- A read-half close drops the connection, matching the RFC 7766 behavior noted in comments.

## HTTP/2 DoH Handling
When built with nghttp2, the file registers callbacks for begin-headers, headers, data chunks, frame completion, stream close, recv, and send.
- GET queries are decoded from `?dns=` using base64url, with fallback for non-url base64.
- POST queries are buffered from DATA frames, honoring content-length when present.
- Invalid endpoint/content-type/method/size yields HTTP status responses.
- DNS responses are copied from the shared comm buffer into per-stream response buffers, bounded by `http2_response_buffer_max`.
- Query buffers are globally bounded by `http2_query_buffer_max`.

## DNS-over-QUIC Handling
When built with ngtcp2, this file contains a substantial DoQ implementation:
- `doq_table_create/delete()` own connection, connection-ID, timer, write-list, static-secret, and memory accounting state.
- `doq_conn_create/setup/delete()` create server-side ngtcp2 connections, TLS state, connection IDs, transport parameters, and locks.
- Connection IDs are indexed separately in `conid_tree` so packets with rotated CIDs can find the right connection.
- Timers use an rbtree keyed by timeval, with set-lists for multiple timers at the same instant.
- Streams parse the two-byte DNS-over-TCP-style length prefix, buffer input, call the resolver callback, queue output, and keep output allocated for QUIC retransmission until acknowledged.
- ngtcp2 callbacks handle stream open/data/close/reset/ack, connection ID creation/removal, handshake completion, crypto logging, and random generation.
- `quic_sslctx_create()` builds a TLS 1.3 server context, loads key/certificate/optional client-verify PEM, configures ALPN `doq`, early data, and ngtcp2 crypto provider glue.
- DoQ memory use is bounded through `doq_table_quic_size_available/add/subtract/get()` against `cfg->quic_size`.

## Memory and Concurrency
The file uses global locks for stream wait and HTTP/2 buffer counters, per-DoQ-table read/write locks for connection and CID trees, per-connection locks, and a size lock for DoQ memory accounting. Listener deletion closes commpoints and frees shared buffers; port-list deletion closes sockets and frees stored socket addresses.

## Edge Cases and Risks
- Many features are compile-time optional; fallback stubs warn or return failure for missing nghttp2/ngtcp2/platform support.
- Socket behavior is highly platform-dependent, with many conditional branches for Linux, BSD, Windows, systemd, and OpenSSL variants.
- DoQ code is large and stateful: connection-ID ownership, timer movement between tree/list forms, and retained retransmission buffers are key invariants.
- Buffer accounting must remain balanced on all error paths; the implementation has explicit subtract/free paths for HTTP/2 and DoQ buffers.
- This file is networking/resolver infrastructure rather than filesystem code, but it is in subset A because the complete OpenBSD source tree is in scope.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.c -->