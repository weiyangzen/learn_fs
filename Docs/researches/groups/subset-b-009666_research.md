# Grouped research: subset-b-009666

This grouped report covers libtirpc RPC protocol, rpcbind/portmap client, service transport, and server authentication files under `sources/user-network-fs/libtirpc/src`. Each file section preserves the source path in the title and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_rmt.c -->
# sources/user-network-fs/libtirpc/src/pmap_rmt.c

Purpose: legacy portmapper remote-call support for IPv4 `PMAPPROC_CALLIT`. The file lets callers ask a remote portmapper to locate a program/version and invoke one procedure in a single UDP RPC call.

Important APIs and functions: `pmap_rmtcall()` builds a UDP client to `PMAPPORT`, fills `struct rmtcallargs` and `struct rmtcallres`, invokes `CLNT_CALL(... PMAPPROC_CALLIT ...)`, returns the contacted service port through `port_ptr`, and resets `addr->sin_port` to zero. `xdr_rmtcall_args()` serializes program/version/procedure plus an opaque argument blob whose length is backpatched after calling the caller-supplied argument XDR routine. `xdr_rmtcallres()` decodes the returned port and then dispatches to the caller-supplied result XDR routine.

Control flow: the public call temporarily mutates the passed `sockaddr_in` to point at the portmapper, creates a UDP client with a fixed three-second retry timeout, performs one RPC call using the user-provided timeout, destroys the client, and restores the input address port field. The XDR argument encoder records the stream position before the length field, emits placeholder length, serializes arguments, computes the byte span, seeks back to overwrite the length, then restores the final position.

State and persistence: no durable state is stored. The only side effect is transient mutation of `addr->sin_port`; assertions require non-null `addr` and `port_ptr`.

Dependencies and integration points: depends on classic SunRPC headers, `clntudp_create`, `CLNT_CALL`, `xdr_reference`, and portmapper protocol constants from `rpc/pmap_prot.h`. It integrates with compatibility callers that still use portmapper rather than rpcbind.

Risks: IPv4/UDP only, legacy portmapper only, and no broadcast implementation in this file despite historical comments. Length backpatching assumes an XDR stream that supports `XDR_GETPOS` and `XDR_SETPOS`. Callers must pass valid XDR procedures and writable result storage.

Test signals: exercise successful `PMAPPROC_CALLIT` against a portmapper-compatible test service, service-not-registered failure, encode/decode with non-empty and empty argument/result payloads, preservation of `addr->sin_port` after failure, and XDR streams that reject seek/backpatch operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_rmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_callmsg.c -->
# sources/user-network-fs/libtirpc/src/rpc_callmsg.c

Purpose: XDR serializer/deserializer for RPC call messages. It handles the call header plus credential and verifier opaque-auth fields.

Important APIs and functions: `xdr_callmsg(XDR *xdrs, struct rpc_msg *cmsg)` is the sole exported function. It supports optimized inline encode/decode paths and a generic fallback using `xdr_u_int32_t`, `xdr_enum`, and `xdr_opaque_auth`.

Control flow: encode validates `oa_length <= MAX_AUTH_BYTES`, attempts a single `XDR_INLINE` allocation for the fixed header plus rounded credential and verifier lengths, writes xid/direction/rpc version/program/version/procedure, and copies opaque bodies. Decode first tries to inline the fixed header, validates `CALL` direction and `RPC_MSG_VERSION`, allocates credential/verifier buffers with `mem_alloc` when `oa_base` is null, then reads opaque bodies either inline or via `xdr_opaque`. If optimized paths are unavailable, the generic XDR chain performs the same field ordering and validation.

State and persistence: the function can allocate `cb_cred.oa_base` and `cb_verf.oa_base` during decode; ownership follows the normal XDR/auth message lifecycle. It does not store global state.

Dependencies and integration points: used by server transports such as `svc_dg.c` and `svc_raw.c` to parse incoming calls, and by client transports elsewhere in libtirpc. It depends on IXDR macros, `MAX_AUTH_BYTES`, and the `struct rpc_msg` layout from public RPC headers.

Risks: callers must initialize `oa_base` to either null or valid writable buffers before decoding. Inline paths rely on correct rounded-length arithmetic. Overlong authentication data is rejected, but malformed streams may still leave partially allocated fields for the caller/XDR cleanup path to free.

Test signals: cover encode/decode round trips for AUTH_NONE, AUTH_SYS-sized credentials, maximum-size opaque auth, over-limit rejection, wrong direction/version rejection, preallocated versus null auth buffers, and fallback behavior with an XDR implementation where `XDR_INLINE` returns null.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_callmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_com.h -->
# sources/user-network-fs/libtirpc/src/rpc_com.h

Purpose: private libtirpc common-interface header shared by client, server, rpcbind, and transport code. It wraps public `rpc/rpc_com.h` while declaring internal helpers that are not installed as public APIs.

Important APIs and types: declares `__rpc_set_netbuf`, `__rpcb_findaddr_timed`, `__rpc_control`, `__svc_clean_idle`, `__xdrrec_setnonblock`, `__xdrrec_getrec`, `__xprt_unregister_unlocked`, `__xprt_set_raddr`, and exported `__svc_maxrec`. It also defines fallback `SOL_IPV6`/`SOL_IP` aliases and `SUN_LEN_A()` for Linux abstract Unix sockets.

Control flow: no runtime logic except macro expansion. `SUN_LEN_A(ptr)` computes a `sockaddr_un` length for abstract Unix socket names by including the leading NUL path byte and the string that follows it.

State and persistence: declares, but does not define, shared service state (`__svc_maxrec`) and internal cross-module entry points.

Dependencies and integration points: included by `rpc_generic.c`, `rpcb_clnt.c`, `svc.c`, `svc_dg.c`, `rpcb_prot.c`, and other libtirpc internals. It connects address translation, rpcbind lookup, record-stream internals, and service transport registration.

Risks: this is a private ABI surface inside the library; signature drift here can break many source files. `SUN_LEN_A` assumes abstract-socket layout and uses `strlen(ptr->sun_path + 1)`, so callers must provide NUL-terminated abstract names.

Test signals: compile-time coverage across IPv4, IPv6, and Unix socket builds; runtime local rpcbind abstract-socket connection paths; record-stream nonblocking tests; and service unregister behavior using `__xprt_unregister_unlocked`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_commondata.c -->
# sources/user-network-fs/libtirpc/src/rpc_commondata.c

Purpose: defines public/global RPC data objects that must have one library-wide storage instance.

Important APIs and state: defines `_null_auth`, `svc_fdset`, `svc_maxfd`, `svc_pollfd`, and `svc_max_pollfd`. These are consumed by service registration, polling, and authentication code.

Control flow: no functions are present. Initialization relies on C static initialization: `_null_auth` is zeroed, `svc_fdset` is zeroed, `svc_maxfd` starts at `-1`, and poll globals start null/zero.

State and persistence: all data is process-global. `svc_fdset`, `svc_maxfd`, `svc_pollfd`, and `svc_max_pollfd` persist for the lifetime of the process or until service code such as `svc_exit()` frees/clears the poll array.

Dependencies and integration points: `svc.c` mutates these globals under `svc_fd_lock`; `svc_run.c` reads `svc_pollfd`; authentication code uses `_null_auth` to initialize reply verifiers. Applications that include legacy RPC globals may also observe `svc_fdset` and `svc_maxfd`.

Risks: process-global mutable service state means multiple independent RPC server subsystems in one process share polling and registration state. Correct locking is external to this file.

Test signals: start and stop multiple transports, verify `svc_fdset`/`svc_pollfd` reflect registrations and unregistrations, call `svc_exit()`, and ensure `_null_auth` remains the zero-flavor verifier used by authentication initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_commondata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_dtablesize.c -->
# sources/user-network-fs/libtirpc/src/rpc_dtablesize.c

Purpose: supplies `_rpc_dtablesize()`, a cached descriptor-table size for select-based service loops.

Important APIs and functions: `_rpc_dtablesize()` calls `sysconf(_SC_OPEN_MAX)` once, clamps the value to `FD_SETSIZE`, caches it in a static `size`, and returns it thereafter.

Control flow: first call populates the static cache; later calls return it directly. If `sysconf` returns a value larger than `FD_SETSIZE`, the function returns `FD_SETSIZE` because `fd_set` cannot represent higher descriptors.

State and persistence: one process-local static integer persists after first use. It is not refreshed if resource limits change later.

Dependencies and integration points: used by `svc.c` to size `__svc_xports` and scan fd sets. It includes public RPC compatibility headers.

Risks: `sysconf(_SC_OPEN_MAX)` failure is not explicitly handled; a negative return could be cached and later used incorrectly. The cache can become stale after `setrlimit`.

Test signals: run under normal and low/high `RLIMIT_NOFILE` settings, validate clamping to `FD_SETSIZE`, and exercise service registration after changing limits to document static-cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_dtablesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_generic.c -->
# sources/user-network-fs/libtirpc/src/rpc_generic.c

Purpose: shared RPC transport utility layer. It maps netconfig entries to sockets and addresses, iterates nettype selectors, converts between transport addresses and universal addresses, computes buffer sizes, and provides small compatibility helpers.

Important APIs and functions: `__rpc_dtbsize()` caches `RLIMIT_NOFILE`; `__rpc_get_t_size()` and `__rpc_get_a_size()` choose transport/address buffer sizes; `__rpc_getconfip()` finds cached IPv4 tcp/udp netconfig entries in thread-specific storage; `__rpc_setconf()`, `__rpc_getconf()`, and `__rpc_endconf()` implement nettype iteration. `rpc_nullproc()` pings NULLPROC. `__rpcgettp()`, `__rpc_fd2sockinfo()`, `__rpc_nconf2sockinfo()`, `__rpc_nconf2fd_flags()`, `__rpc_nconf2fd()`, and `__rpc_sockinfo2netid()` bridge descriptors, netconfig, and socket metadata. `taddr2uaddr()`, `uaddr2taddr()`, `__rpc_taddr2uaddr_af()`, and `__rpc_uaddr2taddr_af()` handle universal address encoding. `__rpc_fixup_addr()` preserves IPv6 scope IDs. `__rpc_sockisbound()` tests whether a descriptor has a usable bound address. `__rpc_set_netbuf()` reallocates/copies a `netbuf`.

Control flow: nettype strings are mapped to internal enum values, then `__rpc_getconf()` filters `getnetpath()` or `getnetconfig()` results by visibility, semantics, protocol family, and protocol. Socket creation derives family/type/protocol from netconfig and sets IPv6-only on IPv6 sockets. Universal address conversion formats IPv4/IPv6 as address plus two decimal port octets and local sockets as path/abstract names; decoding reverses this into allocated `netbuf` and sockaddr objects.

State and persistence: caches descriptor-table size in `__rpc_dtbsize`; caches tcp/udp netids in thread-specific keys; returned netconfig entries and address buffers are heap allocations requiring caller cleanup. `__rpc_set_netbuf()` owns/replaces the destination netbuf buffer via `mem_alloc`/`mem_free`.

Dependencies and integration points: depends on netconfig/netpath, sockets, `inet_ntop`/`inet_pton`, pthread/TSD compatibility wrappers, and `rpc_com.h`. It is foundational for `rpcb_clnt.c`, `svc_generic.c`, `svc_dg.c`, and `rpc_soc.c`.

Risks: universal-address parsing uses `atoi` for port octets without strict range validation. AF_LOCAL conversion truncates long paths through `strncpy`. Thread-specific netid caching depends on global key initialization locks. `__rpc_nconf2fd_flags()` silently ignores IPv6-only `setsockopt` failure.

Test signals: nettype iteration for `netpath`, visible, tcp, udp, circuit, and datagram filters; IPv4/IPv6/local universal address round trips; invalid universal addresses; descriptor-to-netid mapping; IPv6 link-local scope fixups; bound/unbound sockets; and memory cleanup of netbuf replacements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_gss_utils.c -->
# sources/user-network-fs/libtirpc/src/rpc_gss_utils.c

Purpose: RPCSEC_GSS utility API for mechanism/QOP discovery and thread-specific error reporting.

Important APIs and functions: `rpc_gss_get_error()`, `rpc_gss_set_error()`, and `rpc_gss_clear_error()` manage `rpc_gss_error_t` values. `rpc_gss_get_mechanisms()`, `rpc_gss_get_mech_info()`, `rpc_gss_get_versions()`, `rpc_gss_is_installed()`, `rpc_gss_mech_to_oid()`, `rpc_gss_oid_to_mech()`, `rpc_gss_qop_to_num()`, and `rpc_gss_num_to_qop()` expose static Kerberos v5 mechanism/QOP mappings. Internal helpers search mechanism and QOP tables and compare OIDs.

Control flow: `__rpc_gss_error()` lazily creates a thread-specific key, allocates one error object per thread, and falls back to a static error object if key creation or allocation fails. Mechanism APIs validate null arguments, search static tables, set `EINVAL` or `ENOENT` on failure, and clear errors on success.

State and persistence: thread-specific error objects persist until thread exit through TSD destructors. Mechanism/QOP tables are static read-only data. Supported mechanisms are limited to Kerberos v5 and its principal-name OID, with default QOP only.

Dependencies and integration points: depends on `<rpc/auth_gss.h>`, `<rpc/rpcsec_gss.h>`, and GSS/Kerberos OID definitions. `svc_auth_gss.c` calls `rpc_gss_oid_to_mech()` and `rpc_gss_num_to_qop()` to populate credentials and QOP strings.

Risks: the static table emulates Solaris files and can become incomplete if the underlying GSS implementation supports more mechanisms or QOPs. Fallback to a shared static error object means error reporting is less thread-isolated under allocation/key failures.

Test signals: mechanism name/OID round trips, null-argument error reporting, unknown mechanism/QOP failures, per-thread independent error values, and GSS builds with both MIT/Heimdal headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_gss_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_prot.c -->
# sources/user-network-fs/libtirpc/src/rpc_prot.c

Purpose: common RPC protocol XDR and reply-to-error mapping helpers shared by clients and servers.

Important APIs and functions: `xdr_opaque_auth()`, `xdr_des_block()`, `xdr_accepted_reply()`, `xdr_rejected_reply()`, `xdr_replymsg()`, `xdr_callhdr()`, and `_seterr_reply()`. Static `accepted()` and `rejected()` translate protocol accept/reject statuses into `enum clnt_stat` values in `struct rpc_err`.

Control flow: reply XDR uses a discriminator table to decode/encode `MSG_ACCEPTED` versus `MSG_DENIED`. Accepted replies serialize verifier and accept status, then either call the embedded result XDR procedure for `SUCCESS`, encode low/high versions for `PROG_MISMATCH`, or accept terminal error statuses with no payload. Rejected replies encode RPC version ranges or authentication reasons. `_seterr_reply()` handles the success fast path and fills version or auth details when appropriate.

State and persistence: no mutable file-local state. It references global `_null_auth` declared elsewhere but only as an external symbol.

Dependencies and integration points: used by transport reply code such as `svc_dg_reply()` and raw/connection transports, and by client code to interpret server replies. Depends on public RPC structs and XDR.

Risks: `xdr_callhdr()` only supports `XDR_ENCODE`; callers using decode/free get `FALSE`. Unknown accept/reject discriminants collapse to generic failure. Result XDR callbacks must be valid for `SUCCESS` replies.

Test signals: encode/decode reply messages for success, program mismatch, auth error, RPC mismatch, garbage args, and unknown statuses; verify `_seterr_reply()` populates `re_vers` and `re_why`; and validate `xdr_callhdr()` emits the expected static call header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_soc.c -->
# sources/user-network-fs/libtirpc/src/rpc_soc.c

Purpose: legacy socket-style RPC compatibility layer compiled under `PORTMAP`. It maps old IPv4 TCP/UDP and Unix-domain APIs onto TIRPC client/server creation and rpcbind/portmap helpers.

Important APIs and functions: client helpers include `clntudp_bufcreate()`, `__libc_clntudp_bufcreate()`, `clntudp_create()`, `clnttcp_create()`, `clntraw_create()`, `clntunix_create()`, and AUTH_DES compatibility constructors. Server helpers include `svctcp_create()`, `svcudp_bufcreate()`, `svcudp_create()`, `svcfd_create()`, `svcraw_create()`, `svcunix_create()`, and `svcunixfd_create()`. Utility wrappers include `get_myaddress()`, `callrpc()`, `registerrpc()`, and `clnt_broadcast()`.

Control flow: `clnt_com_create()` obtains an IPv4 netconfig for tcp/udp, creates or uses a descriptor, optionally asks portmapper for a service port, binds a reserved port, and delegates to `clnt_tli_create`; ownership of auto-created descriptors is transferred to the client through `CLSET_FD_CLOSE`. `svc_com_create()` creates a descriptor if needed and delegates to `svc_tli_create`. Broadcast wraps modern `rpc_broadcast()` with a thread-specific legacy callback adapter. Unix-domain creation copies/binds/connects `sockaddr_un` addresses, including abstract socket support.

State and persistence: relies on external `rpcsoc_lock`, TSD key `clnt_broadcast_key`, and netconfig caches from `rpc_generic.c`. It mutates caller-provided socket variables and remote address port fields.

Dependencies and integration points: integrates old SunRPC APIs with `clnt_tli_create`, `svc_tli_create`, `rpc_call`, `rpc_reg`, `rpc_broadcast`, `pmap_getport`, and optional AUTH_DES support. IPv6 variants are present but disabled under `INET6_NOT_USED`.

Risks: most paths are IPv4-only despite TIRPC support. Some AUTH_DES constructors are stubs when `AUTHDES_SUPPORT` is absent. `svcunix_create()` ignores its incoming `sock` argument and creates a new descriptor. Legacy callback storage in thread-specific data means nested broadcasts need care.

Test signals: legacy UDP/TCP client creation with explicit and `RPC_ANYSOCK` descriptors, portmapper lookup fallback, descriptor close-on-destroy behavior, service creation and rpcbind/portmap registration, broadcast callback address conversion, Unix abstract and pathname socket clients/servers, and builds with and without `AUTHDES_SUPPORT`/`PORTMAP`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_clnt.c -->
# sources/user-network-fs/libtirpc/src/rpcb_clnt.c

Purpose: client interface to the rpcbind service, including mapping registration, address lookup, remote call, time lookup, address conversion fallbacks, and an rpcbind-address cache.

Important APIs and functions: public/internal APIs include `__rpc_control()`, `rpcb_set()`, `rpcb_unset()`, `__rpcb_findaddr_timed()`, `rpcb_getaddr()`, `rpcb_getmaps()`, `rpcb_rmtcall()`, `rpcb_gettime()`, `rpcb_taddr2uaddr()`, and `rpcb_uaddr2taddr()`. Key helpers include address-cache routines, `getclnthandle()`, `getpmaphandle()`, `local_rpcb()`, and, under `PORTMAP`, `__try_protocol_version_2()`.

Control flow: rpcbind client creation checks the host/netid cache, deep-copies cache entries under a mutex, tries `clnt_tli_create`, and deletes failed cached addresses. Without a usable cache, it resolves the rpcbind service via local Unix sockets for loopback transports or `getaddrinfo(host, "sunrpc")` for remote hosts, then stores successful target addresses. Registration/unregistration always uses local rpcbind. Address lookup creates or reuses a client, tries rpcbind v4 then v3 for `RPCBPROC_GETADDR`, translates universal addresses to transport addresses, fixes IPv6 scope IDs, and optionally falls back to portmapper v2 for IPv4 TCP/UDP. `rpcb_rmtcall()` tries rpcbind v4/v3 `RPCBPROC_CALLIT`, translates the returned universal address, and copies it into caller-provided storage when requested.

State and persistence: stores a six-entry process-global LRU-ish `address_cache` list guarded by `rpcbaddr_cache_lock`. `local_rpcb()` caches a selected loopback `netconfig` and loopback hostname under `loopnconf_lock`. Timeouts are global (`tottimeout`, `rpcbrmttime`) and can be changed through `__rpc_control`; `__rpc_lowvers` is also controlled there.

Dependencies and integration points: relies on `rpc_generic.c` address conversion, local rpcbind Unix socket paths, GSS-independent RPC client calls, netconfig, `rpcb_prot.c` XDR, optional portmapper compatibility, and debug logging. Service registration from `svc.c` and service creation from `svc_generic.c` call `rpcb_set`/`rpcb_unset`.

Risks: global cache and timeout changes affect all threads. Cache deletion compares raw netbuf bytes and may evict any matching address regardless of host/netid. `local_rpcb()` never frees the cached netconfig. Fallback order changes under `RPCB_V2FIRST`. Some error paths depend on `rpc_createerr` global state.

Test signals: local abstract and pathname rpcbind sockets, remote `getaddrinfo` resolution, cache hit/miss/delete behavior under concurrent lookups, v4-to-v3 fallback, portmap v2 fallback for IPv4, `RPCB_V2FIRST`, `rpcb_set`/`rpcb_unset` owner strings, address-too-small failure in `rpcb_getaddr`, rmtcall result address copying, and timeout control through `__rpc_control`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_clnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_prot.c -->
# sources/user-network-fs/libtirpc/src/rpcb_prot.c

Purpose: XDR routines for rpcbind protocol data structures and rpcbind remote-call payloads.

Important APIs and functions: `xdr_rpcb()`, `xdr_rpcblist_ptr()`, `xdr_rpcblist()`, `xdr_rpcb_entry()`, `xdr_rpcb_entry_list_ptr()`, `xdr_rpcb_rmtcallargs()`, `xdr_rpcb_rmtcallres()`, and `xdr_netbuf()`.

Control flow: simple structures serialize fixed integers and bounded strings. Linked-list functions avoid recursive `xdr_pointer` traversal by looping over presence booleans and serializing nodes through `xdr_reference`; free mode saves the next pointer before freeing the current node. Remote-call argument XDR writes program/version/procedure, backpatches the argument length after invoking the provided argument XDR callback, and restores the stream position. Remote-call result XDR reads the universal address, result length, then calls the provided result decoder.

State and persistence: no global state. Decode/free operations allocate or free strings, linked-list nodes, netbuf buffers, and callback-owned payloads through XDR helpers.

Dependencies and integration points: used by `rpcb_clnt.c` for rpcbind requests and by rpcbind-compatible services. Depends on `RPC_MAXDATASIZE` bounds and callback XDR procedures.

Risks: `xdr_rpcb_rmtcallargs()` is intended for encode direction and assumes positional XDR support. `xdr_netbuf()` serializes `maxlen` first and rejects values above `RPC_MAXDATASIZE`; malformed data can still allocate up to that limit. Non-recursive freeing code is subtle and should not be casually refactored.

Test signals: rpcbind map encode/decode/free, long string rejection, multi-node list decode/free without recursion, remote-call argument length backpatch accuracy, result callback invocation, and netbuf maxlen/len boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c -->
# sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c

Purpose: XDR support for rpcbind statistics structures generated from `rpcb_prot.x` and used by the rpcbind stats facility.

Important APIs and functions: `xdr_rpcbs_addrlist()`, `xdr_rpcbs_rmtcalllist()`, `xdr_rpcbs_proc()`, `xdr_rpcbs_addrlist_ptr()`, `xdr_rpcbs_rmtcalllist_ptr()`, `xdr_rpcb_stat()`, and `xdr_rpcb_stat_byvers()`.

Control flow: address and remote-call list nodes serialize program/version/procedure counters, success/failure/indirect counts, netid strings, and recursive next pointers. `xdr_rpcbs_rmtcalllist()` has optimized inline encode/decode paths for six fixed fields and a generic fallback. Stat arrays are handled through `xdr_vector`.

State and persistence: no static mutable state. XDR decode/free owns linked-list allocations through `xdr_pointer`.

Dependencies and integration points: depends on rpcbind stats typedefs and `RPCBSTAT_HIGHPROC`/`RPCBVERS_STAT` dimensions. It is consumed by rpcbind monitoring clients and servers rather than normal RPC call paths.

Risks: list serialization is recursive through `xdr_pointer`, so extremely long stats lists could recurse deeply. Inline decode assumes matching integer field order. Strings are bounded by `RPC_MAXDATASIZE` but can still allocate large buffers.

Test signals: encode/decode/free of empty and multi-node addr/rmtcall lists, vector dimensions for every rpcbind version, inline and non-inline XDR paths, and counter preservation for success/failure/indirect values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcdname.c -->
# sources/user-network-fs/libtirpc/src/rpcdname.c

Purpose: returns the system default NIS/RPC domain name through a small caching wrapper.

Important APIs and functions: internal `get_default_domain()` calls `getdomainname()` into a stack buffer and stores a heap copy in static `default_domain`. `__rpc_get_default_domain(char **domain)` exposes the cached string and returns `0` on success or `-1` on failure.

Control flow: first successful call reads the domain, rejects empty strings, allocates and copies it, then returns the cached pointer. Later calls return the cached pointer without another syscall.

State and persistence: `default_domain` is process-global, heap allocated, and never freed. The returned pointer is shared and should not be modified or freed by callers.

Dependencies and integration points: used by NIS/RPC name code that needs a default domain and expects ypclnt-style success/failure status.

Risks: no locking protects first-time initialization, so concurrent first calls can race and leak or publish one of multiple allocations. The 256-byte temporary buffer truncation behavior depends on `getdomainname`.

Test signals: empty domain failure, successful cached domain reuse, concurrent first-call stress, and callers treating returned memory as read-only shared storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcdname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rtime.c -->
# sources/user-network-fs/libtirpc/src/rtime.c

Purpose: implements the legacy `rtime()` client for the RFC 868 time service over IPv4 TCP or UDP, converting seconds since 1900 to Unix epoch seconds.

Important APIs and functions: `rtime(struct sockaddr_in *addrp, struct timeval *timep, struct timeval *timeout)` performs the query. `do_close()` closes a socket while preserving `errno`.

Control flow: a null timeout selects TCP; a non-null timeout selects UDP. The function opens an IPv4 socket, sets the target family and service port from `getservbyname("time", "tcp")`, sends a UDP probe and polls for a response or connects/reads over TCP, validates that exactly four bytes were received, converts from network byte order, subtracts the 1900-to-1970 offset, and writes `timep`.

State and persistence: no global state. It mutates `addrp->sin_family` and `addrp->sin_port` and writes `timep`.

Dependencies and integration points: uses sockets, `poll`, `/etc/services` service lookup, and IPv4 sockaddr structures. It is a standalone legacy utility rather than RPC protocol logic.

Risks: IPv4-only, depends on the deprecated time service, and calculates UDP timeout milliseconds with potential integer overflow for very large timeouts. The UDP request sends an uninitialized `thetime` buffer, which is conventional for the service but still awkward for analysis tools.

Test signals: TCP and UDP time service fixtures, timeout maps to `ETIMEDOUT`, short-read maps to `EIO`, `getservbyname` failure, EINTR during poll, and epoch conversion for known RFC 868 timestamps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc.c -->
# sources/user-network-fs/libtirpc/src/svc.c

Purpose: core server-side RPC dispatch and transport registry. It tracks active transports, service program registrations, error replies, request authentication, and dispatch to application handlers.

Important APIs and functions: transport registry functions `xprt_register()`, `xprt_unregister()`, `__xprt_unregister_unlocked()`, and `svc_open_fds()` maintain `__svc_xports`, `svc_fdset`, and `svc_pollfd`. Service registration APIs `svc_reg()` and `svc_unreg()` manage rpcbind-backed callouts; `svc_register()`/`svc_unregister()` provide portmap compatibility under `PORTMAP`. Reply helpers include `svc_sendreply()`, `svcerr_noproc()`, `svcerr_decode()`, `svcerr_systemerr()`, `svcerr_auth()`, `svcerr_weakauth()`, `svcerr_noprog()`, and `svcerr_progvers()`. Input paths are `svc_getreq()`, `svc_getreqset()`, `svc_getreq_common()`, and `svc_getreq_poll()`. `rpc_control()` gets/sets `__svc_maxrec`.

Control flow: registration inserts `SVCXPRT` pointers by fd into `__svc_xports`, updates `fd_set` state for select, and appends/reuses poll slots for poll-based loops. `svc_reg()` determines a netid from transport/netconfig/fd, stores a callout keyed by program/version/netid, optionally registers with local rpcbind, and stores the netid on the transport. `svc_getreq_common()` receives one or more batched requests from a transport, authenticates with `_gss_authenticate`, skips dispatch for GSS handshake/control requests when requested, finds matching program/version callouts, invokes the dispatch routine, or emits program/version errors.

State and persistence: process-global `__svc_xports`, `svc_head`, `svc_fdset`, `svc_pollfd`, `svc_maxfd`, `svc_max_pollfd`, and `__svc_maxrec`. Registry state is protected by `svc_fd_lock` and `svc_lock`. Per-request credentials are stack-backed in `cred_area`.

Dependencies and integration points: uses transport ops through `SVC_RECV`, `SVC_REPLY`, `SVC_STAT`, and `SVC_DESTROY`; authentication from `svc_auth.c`; rpcbind/portmap registration; and common data from `rpc_commondata.c`.

Risks: callout traversal in `svc_getreq_common()` is not visibly under `svc_lock`, so concurrent registration/unregistration must be considered carefully. `svc_unreg()` frees `sc_netid` with an incorrect size expression, though `mem_free` may ignore the size. Descriptor values >= `_rpc_dtablesize()` are not registered in `__svc_xports`.

Test signals: registering multiple transports and netids for one program/version, duplicate dispatch rejection, rpcbind registration/unregistration, dispatch success, missing procedure/program/version replies, GSS no-dispatch handshakes, transport death during recursive dispatch, poll `POLLNVAL` cleanup, and `rpc_control` validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth.c -->
# sources/user-network-fs/libtirpc/src/svc_auth.c

Purpose: server-side authentication dispatcher. It maps incoming credential flavors to built-in or registered authentication handlers.

Important APIs and functions: `_gss_authenticate()` is the main dispatcher and supports `AUTH_NONE`, `AUTH_SYS`, `AUTH_SHORT`, optional `AUTH_DES`, optional `RPCSEC_GSS`, and custom flavors. `_authenticate()` is a compatibility wrapper. `svc_auth_reg()` registers custom handlers in a linked list.

Control flow: authentication initialization copies raw credentials to the request, resets the transport `SVCAUTH` ops to `svc_auth_none`, clears private auth state, resets the reply verifier to `_null_auth`, and dispatches by credential flavor. Unknown flavors are looked up under `authsvc_lock`. Custom registration rejects already built-in flavors, prevents duplicate custom entries, and prepends new handler nodes.

State and persistence: static linked list `Auths` persists for process lifetime and has no unregister path. Transport auth state is reset per request before flavor-specific handling.

Dependencies and integration points: called from `svc_getreq_common()` before service dispatch. Integrates with `svc_auth_none.c`, `svc_auth_unix.c`, `svc_auth_des.c`, and `svc_auth_gss.c`.

Risks: registered custom handlers are never freed. `AUTH_NULL` and `AUTH_NONE` naming differences are handled through constants, but custom flavor validation must match platform definitions. Built-in GSS can set `no_dispatch`, which callers must honor.

Test signals: all built-in flavor branches, GSS handshake no-dispatch behavior, custom handler registration and duplicate detection, unknown flavor rejection, and transport verifier reset between mixed-auth requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_des.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_des.c

Purpose: server-side AUTH_DES authenticator with conversation-key cache, timestamp replay protection, nickname support, and DES-to-Unix credential mapping.

Important APIs and functions: `_svcauth_des()` authenticates AUTH_DES credentials. Cache helpers `cache_init()`, `cache_victim()`, `cache_ref()`, `cache_spot()`, and `invalidate()` manage a 64-entry LRU cache. `authdes_getucred()` maps an authenticated network name to Unix uid/gid/groups and caches the result.

Control flow: full-name credentials parse the client netname, encrypted conversation key, and window; nickname credentials index an existing cache entry. The authenticator decrypts the timestamp using CBC for full credentials or ECB for nickname credentials, validates microseconds, replay ordering, and expiration window, builds an encrypted reply verifier using timestamp minus one second, then commits session data to the cache. Full-name credentials resolve a public key and decrypt the session key; nickname credentials hydrate full-name fields from the cache entry. Unix credential lookup calls `netname2user()` on cache miss.

State and persistence: process-global `authdes_cache`, `authdes_lru`, and `svcauthdes_stats` persist after lazy initialization. Each cache entry stores a session key, client name, window, last timestamp, and optional local credential cache. There is no explicit locking around this global cache in this file.

Dependencies and integration points: used from `svc_auth.c` when `AUTHDES_SUPPORT` is enabled. Depends on DES crypt routines, public-key lookup/decryption, netname-to-user mapping, RPC auth/des structs, and debug logging.

Risks: legacy DES cryptography is weak by modern standards. Global cache access appears unsynchronized. Direct IXDR parsing assumes valid opaque lengths supplied by the RPC message. Replay checks depend on system time and timestamp monotonicity. Some credential fields are stored in fixed-width short fields in local credential cache.

Test signals: full-name authentication with valid public key/session key, nickname reuse, replayed timestamp rejection, expired timestamp rejection, invalid microseconds, bad nickname, window verifier mismatch, DES encrypt/decrypt failure paths, LRU victim replacement, and `authdes_getucred()` success/unknown/cache-hit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_gss.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_gss.c

Purpose: server-side RPCSEC_GSS implementation. It accepts GSS security contexts, validates signed RPC headers, enforces sequence-window replay checks, wraps/unwraps protected data, exposes credentials, and supports service callbacks.

Important APIs and functions: setup APIs include `svcauth_gss_set_svc_name()` and `rpc_gss_set_svc_name()`. Main authentication is `_svcauth_gss()`. Context helpers include `svcauth_gss_import_name()`, `svcauth_gss_acquire_cred()`, `svcauth_gss_release_cred()`, `svcauth_gss_accept_sec_context()`, `svcauth_gss_validate()`, `svcauth_gss_nextverf()`, `svcauth_gss_callback()`, cache helpers, and `destroy_gd()`. Transport auth ops are `svcauth_gss_wrap()`, `svcauth_gss_unwrap()`, and `svcauth_gss_destroy()`. Public credential helpers include `svcauth_gss_get_principal()`, `rpc_gss_svc_max_data_length()`, `rpc_gss_getcred()`, `rpc_gss_set_callback()`, and `rpc_gss_get_principal_name()`.

Control flow: `_svcauth_gss()` gets or creates a per-transport `svc_rpc_gss_data` cache entry, refreshes its five-minute expiry, installs GSS auth ops on the transport, decodes `rpc_gss_cred`, validates version/service, and checks sequence numbers once established. INIT and CONTINUE_INIT are allowed only for NULLPROC, lazily import/acquire service credentials, call `gss_accept_sec_context`, return `rpc_gss_init_res` directly with `no_dispatch = TRUE`, and mark the context established on completion. DATA validates the verifier over a reconstructed RPC call header, creates a reply verifier for the sequence number, runs a registered program/version callback once, enforces locked service/QOP constraints, and updates effective service/QOP. DESTROY validates, replies, releases global creds, destroys the transport auth context, and resets to no-auth ops.

State and persistence: global service name, GSS name, credential handle, requested credential lifetime, and OID set persist process-wide. `svcauth_gss_cache` is a linked list of per-transport contexts guarded by `svcauth_gss_cache_lock`; cold entries expire after five minutes. `_svcauth_callbacks` persists registered callbacks under `svcauth_cb_lock` and is never freed. Each context stores GSS handles, raw/cooked credentials, sequence window state, delegated creds, callback cookie, and client name buffers.

Dependencies and integration points: called from `svc_auth.c`; wraps/unwraps transport argument/result XDR through `SVCAUTH_WRAP` and `SVCAUTH_UNWRAP` used by transports such as `svc_dg.c`; uses `rpc_gss_utils.c` for mechanism/QOP names; depends on platform GSSAPI and password/group lookup for cooked Unix credentials.

Risks: context cache is keyed only by `SVCXPRT *`, noted in-code as limited for interleaved credentials. The sequence mask uses `1 << offset` and a small advertised window, so window size assumptions matter. Global credential release on one DESTROY can affect other contexts. Default service principal falls back to `"nfs"` if not configured. Callback registrations and service name memory persist for process lifetime.

Test signals: GSS INIT/CONTINUE handshakes, DATA with valid and invalid verifier MICs, replay and out-of-window sequence numbers, service/QOP lock enforcement, integrity/privacy wrap and unwrap, DESTROY cleanup, callback accept/reject paths, expired cache entry cleanup, credential extraction through `rpc_gss_getcred`, max data length for none/integrity/privacy, and principal-name export failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_none.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_none.c

Purpose: no-auth server authenticator for AUTH_NONE/AUTH_NULL style requests.

Important APIs and functions: defines `svc_auth_none_ops`, global `svc_auth_none`, `_svcauth_none()`, `svcauth_none_wrap()`, and `svcauth_none_destroy()`.

Control flow: `_svcauth_none()` always returns `AUTH_OK`. Wrap and unwrap operations are the same function and simply call the provided XDR function on the supplied pointer without integrity or privacy transformation. Destroy is a no-op that returns true.

State and persistence: global `svc_auth_none` has ops and null private state. No per-request state is allocated.

Dependencies and integration points: `svc_auth.c` installs these ops as the default transport auth ops before every authentication attempt and dispatches to `_svcauth_none()` for `AUTH_NONE`.

Risks: no authentication, authorization, integrity, or privacy is provided. Callers must rely on higher-level access controls when accepting AUTH_NONE.

Test signals: AUTH_NONE request dispatch succeeds, wrap/unwrap invokes arbitrary XDR functions exactly once, destroy is harmless, and mixed requests reset transport auth ops back to no-auth before flavor-specific handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_unix.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_unix.c

Purpose: server-side AUTH_SYS/AUTH_UNIX credential decoder and AUTH_SHORT rejection.

Important APIs and functions: `_svcauth_unix()` decodes long-form Unix credentials into `struct authunix_parms` stored in `rqst->rq_clntcred`. `_svcauth_short()` rejects shorthand credentials with `AUTH_REJECTEDCRED`.

Control flow: `_svcauth_unix()` builds an XDR memory decoder over the raw credential, points output fields into the caller-provided credential area, and first tries an inline parse of timestamp, machine name, uid, gid, group count, and group list. It bounds machine name to `MAX_MACHINE_NAME`, group count to `NGRPS`, and validates the encoded credential length. If inline data is unavailable, it falls back to `xdr_authunix_parms`. It copies a non-empty incoming verifier into the transport reply verifier or emits AUTH_NULL otherwise.

State and persistence: no global state. Parsed credential storage is request-scoped and lives in the stack-backed area prepared by `svc_getreq_common()`.

Dependencies and integration points: called from `svc_auth.c` for `AUTH_SYS`; service dispatchers can read `rqst->rq_clntcred` as `authunix_parms`. Uses XDR and IXDR macros.

Risks: inline parser depends on sufficient raw credential length; it validates minimum size after reading fields, so malformed short buffers need fuzz coverage. AUTH_SYS is unauthenticated identity assertion and should not be treated as strong security. The debug `printf` on bad length writes to stdout.

Test signals: valid AUTH_SYS with zero and multiple groups, max machine name, overlong machine name, overlarge group count, short/truncated credential, fallback XDR path, verifier propagation, and AUTH_SHORT rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_dg.c -->
# sources/user-network-fs/libtirpc/src/svc_dg.c

Purpose: connectionless/datagram server transport implementation with optional duplicate request cache for at-most-once reply behavior.

Important APIs and functions: `svc_dg_create()` creates/registers a datagram `SVCXPRT`; transport ops include `svc_dg_recv()`, `svc_dg_reply()`, `svc_dg_getargs()`, `svc_dg_freeargs()`, `svc_dg_destroy()`, `svc_dg_stat()`, and `svc_dg_control()`. Cache APIs include `svc_dg_enablecache()`, `cache_get()`, and `cache_set()`. Packet-info helpers are `svc_dg_enable_pktinfo()` and `svc_dg_valid_pktinfo()`.

Control flow: creation derives socket metadata, computes send/receive buffer size, allocates `SVCXPRT`, extension, private `svc_dg_data`, and an aligned XDR buffer, records local address via `getsockname`, enables packet-info cmsgs for IPv4/IPv6, installs ops, and registers the transport. Receive uses `recvmsg`, saves remote address, preserves valid IP_PKTINFO/IPV6_PKTINFO control data for the reply, decodes an RPC call with `xdr_callmsg`, and returns cached replies immediately for duplicate requests. Reply encodes an RPC reply header, temporarily moves success result encoding through `SVCAUTH_WRAP`, sends with the preserved destination control message, and saves the reply in cache on success. Argument decode uses `SVCAUTH_UNWRAP`.

State and persistence: per-transport private state stores XDR stream, I/O buffer, current xid, verifier storage, cmsg buffer, and optional cache. The cache has a hash table plus FIFO victim array and entries keyed by xid/prog/vers/proc/client address; `dupreq_lock` guards cache access.

Dependencies and integration points: used by `svc_generic.c` and legacy `svcudp_create`. Integrates with `svc.c` registration/dispatch, `xdr_callmsg`, `xdr_replymsg`, auth wrap/unwrap, socket `recvmsg`/`sendmsg`, and `rpc_generic.c` address helpers.

Risks: cache entries allocate copied remote addresses but victim replacement reuses nodes without visibly freeing old `cache_addr.buf`, creating leak risk. Packet-info validation only accepts a single cmsg and clears interface index before reply. `svc_dg_control()` is a stub. Datagram transport is sensitive to buffer sizing and message truncation.

Test signals: datagram request/reply round trip, duplicate xid replay returns cached reply without dispatch, cache eviction, auth wrap/unwrap with GSS, IPv4 and IPv6 packet-info replies to aliased addresses, malformed/truncated RPC calls, EINTR retry in receive, destruction cleanup, and cache enable called twice.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_dg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_generic.c -->
# sources/user-network-fs/libtirpc/src/svc_generic.c

Purpose: high-level service creation over arbitrary netconfig/nettype transports. It opens/binds/listens descriptors and delegates to stream or datagram transport implementations.

Important APIs and functions: `svc_create()` creates or reuses transports across all netconfigs selected by a nettype. `svc_tp_create()` creates one transport for one `netconfig` and registers a program/version. `svc_tli_create()` is the generic descriptor/netconfig transport constructor.

Control flow: `svc_create()` iterates selected netconfigs, reuses existing transports by `xp_netid` from a static list, unregisters stale mappings, registers the new program/version, or creates a new transport via `svc_tp_create()` and stores it in the reuse list. `svc_tli_create()` opens a socket when fd is `RPC_ANYFD`, or derives socket info from the supplied fd; binds to a dynamic port when unbound and no bind address is supplied; otherwise binds to requested address and listens; then chooses `svc_fd_create` for accepted stream sockets, `svc_vc_create` for listening stream sockets, or `svc_dg_create` for datagram sockets.

State and persistence: `svc_create()` keeps a static process-global list of created transports protected by `xprtlist_lock`. Created transports persist until application destruction or process exit. `svc_tli_create()` fills `xp_type`, `xp_netid`, and `xp_tp`.

Dependencies and integration points: depends on `__rpc_setconf`/`__rpc_getconf`, `__rpc_nconf2fd`, `__rpc_fd2sockinfo`, `__rpc_sockisbound`, `__binddynport`, `svc_vc_create`, `svc_fd_create`, `svc_dg_create`, and rpcbind registration via `svc_reg`.

Risks: the static transport reuse list has no removal path, so destroyed transports can leave stale pointers if applications destroy them independently. `listen()` is called even for dynamically bound sockets before final transport-type switch. Error paths must carefully avoid closing caller-owned descriptors.

Test signals: create services over `netpath`, `tcp`, `udp`, and visible nettypes; reuse a transport for multiple program versions; accepted stream fd detection; dynamic bind success/failure; caller-owned fd cleanup behavior; rpcbind unregister/register ordering; and service destruction after failed registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_raw.c -->
# sources/user-network-fs/libtirpc/src/svc_raw.c

Purpose: in-process raw server transport for testing and timing RPC without kernel networking.

Important APIs and functions: `svc_raw_create()` creates/reuses the singleton raw `SVCXPRT`. Transport ops are `svc_raw_recv()`, `svc_raw_reply()`, `svc_raw_getargs()`, `svc_raw_freeargs()`, `svc_raw_destroy()`, `svc_raw_stat()`, and `svc_raw_control()`. Global `__rpc_rawcombuf` is the shared client/server buffer.

Control flow: first creation allocates singleton private state, extension storage, and the shared buffer if needed; later calls reuse it. The server fd is set to `FD_SETSIZE`, ops are installed, verifier storage is assigned, an XDR memory stream is created over the shared buffer, and the transport is registered. Receive decodes a call message from offset zero; reply encodes a reply message back to offset zero; getargs/freeargs call the supplied XDR procedure on the same memory stream.

State and persistence: singleton `svc_raw_private` and `__rpc_rawcombuf` persist for process lifetime. `svcraw_lock` protects singleton access, but the raw transport remains a shared non-reentrant testing mechanism.

Dependencies and integration points: pairs with raw client transport code through the shared buffer and uses the normal `svc.c` transport registry/dispatch.

Risks: not a real network transport and not suitable for concurrent independent sessions. `svc_raw_destroy()` does nothing, so registration/state can persist. The fake fd value can interact awkwardly with descriptor-table assumptions.

Test signals: raw client/server NULLPROC and argument round trips, repeated `svc_raw_create()` reuse, concurrent call behavior documentation, freeargs path, and cleanup expectations around no-op destroy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_run.c -->
# sources/user-network-fs/libtirpc/src/svc_run.c

Purpose: default RPC server event loop built on `poll()`, plus an exit helper.

Important APIs and functions: `svc_run()` loops forever while service poll descriptors exist and dispatches readiness through `svc_getreq_poll()`. `svc_exit()` frees global poll state to make `svc_run()` leave its loop.

Control flow: `svc_run()` snapshots `svc_max_pollfd`, resizes a private pollfd array when the global size changes, copies global `svc_pollfd` entries, blocks in `poll(..., -1)`, ignores `EINTR`, warns and exits on other poll failures, and dispatches ready fds. If no poll descriptors exist, it breaks. `svc_exit()` takes `svc_fd_lock`, frees `svc_pollfd`, nulls it, and zeroes `svc_max_pollfd`.

State and persistence: reads global `svc_pollfd`/`svc_max_pollfd`; `svc_exit()` mutates and frees them. The local poll array is allocated and freed inside `svc_run()`.

Dependencies and integration points: used by applications that rely on the classic blocking server loop after registering transports in `svc.c`. Dispatches into `svc_getreq_poll()`.

Risks: `svc_run()` snapshots globals without holding `svc_fd_lock` while copying, so concurrent registration/unregistration can race with the copy. `svc_exit()` is coarse: it removes the global poll array rather than marking a loop-specific stop flag.

Test signals: loop dispatch with one and multiple transports, EINTR continuation, poll failure warning, descriptor array growth/shrink, `svc_exit()` causing loop termination from another thread, and no-transport immediate return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_simple.c -->
# sources/user-network-fs/libtirpc/src/svc_simple.c

Purpose: simplified `rpc_reg()` front end that lets applications register procedure callbacks without building full dispatch functions.

Important APIs and functions: `rpc_reg()` registers one program/version/procedure on transports selected by a nettype. Static `universal()` is the shared dispatch routine for all simplified registrations.

Control flow: `rpc_reg()` rejects `NULLPROC`, selects `netpath` by default, iterates matching netconfigs, reuses an existing transport/xdr buffer by netid or creates one with `svc_tli_create`, computes receive size, allocates a per-netid decode buffer and netid string, avoids duplicate rpcbind unsets when the program/version/netid is already registered, registers `universal()` through `svc_reg`, and prepends a `proglst` entry. `universal()` handles NULLPROC by replying void, otherwise finds the exact program/version/procedure/netid entry, zeroes the shared XDR buffer, decodes arguments, calls the user callback, sends the encoded result, and frees decoded args.

State and persistence: static `proglst` linked list persists process-wide and is protected by `proglst_lock`. Each netid can share one transport and one argument buffer among simplified registrations.

Dependencies and integration points: built on `__rpc_setconf`, `svc_tli_create`, `svc_reg`, `svc_getargs`, `svc_sendreply`, and `svc_freeargs`. Legacy `registerrpc()` in `rpc_soc.c` delegates here for UDP.

Risks: `universal()` holds `proglst_lock` while decoding, invoking user code, replying, and freeing args, so callbacks that call registration APIs can deadlock and unrelated simplified procedures are serialized. It calls `memset(xdrbuf, 0, sizeof(pl->p_recvsz))`, which clears only the size of the integer field rather than the receive buffer, leaving stale argument bytes risk. Shared per-netid argument buffers are not safe for concurrent dispatch.

Test signals: registering multiple procedures on one transport, NULLPROC response, duplicate program/version/netid handling, decode failure path, void and non-void result behavior, callback returning null for non-void, concurrent requests on same netid, and regression for full-buffer zeroing/stale arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_simple.c -->
