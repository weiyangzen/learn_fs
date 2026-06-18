# Group Research: group_1200_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_rpc_getnetconfig_c_so_9eecfff57a6c

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetconfig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetconfig.c

Read completely: 691 lines.

Implements the `/etc/netconfig` access API: `setnetconfig()`, `getnetconfig()`, `endnetconfig()`, `getnetconfigent()`, `freenetconfigent()`, `nc_sperror()`, and `nc_perror()`. It keeps a global parsed-entry cache (`netconfig_info`) shared by active sessions, with per-session cursors and a reference count so repeated scans can reuse parsed `struct netconfig` records.

Parsing is done in-place on a line buffer: `parse_ncp()` tokenizes netid, semantics, flags, protocol family, protocol, device, and comma-separated lookup libraries. The resulting `struct netconfig` string pointers mostly point into the stored line buffer, while `nc_lookups` is separately allocated as an array of pointers into that same buffer. `getnetconfigent()` either duplicates cached entries via `dup_ncp()` or opens and scans `NETCONFIG` independently.

Thread support is partial: only `nc_error` is made thread-specific under `_REENTRANT`; the global file handle and parsed-entry cache are not protected here. Reliability notes: malformed records set `NC_BADFILE`; missing database sets `NC_NONETCONFIG`; many allocation failures just return `NULL`. Lookup-list `realloc()` is not checked before assignment in `parse_ncp()`, so allocation failure there can lose the original pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetpath.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetpath.c

Read completely: 286 lines.

Implements `setnetpath()`, `getnetpath()`, `endnetpath()`, and the shared `_get_next_token()` helper for RPC NETPATH iteration. If `NETPATH` is unset, a netpath session falls back to `setnetconfig()`/`getnetconfig()` and returns only `NC_VISIBLE` transports. If `NETPATH` is set, it copies the environment string, splits it on `:`, and resolves each netid with `getnetconfigent()`.

The session tracks netconfig entries allocated by `getnetconfigent()` so `endnetpath()` can free them. Invalid netids are silently skipped, matching the historical API behavior. `_get_next_token()` mutates the input string, supports escaped separators and backslashes, and is also used by `getnetconfig.c` for comma-separated lookup lists.

Reliability notes: `_get_next_token()` uses overlapping `strcpy()` for in-place compaction, which the source itself marks with `XXX`. The `ncp_list` append path stores only a head pointer and assigns `head->next` for later entries, so more than two returned NETPATH entries can overwrite the earlier second link and leak/lose cleanup tracking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getnetpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcent.c

Read completely: 224 lines.

Implements the legacy `/etc/rpc` database API: `setrpcent()`, `getrpcent()`, `endrpcent()`, `getrpcbyname()`, and `getrpcbynumber()`. A single static `rpcdata` object holds the open file, stay-open flag, current `struct rpcent`, alias pointer array, and line buffer.

`interpret()` copies the input line into the shared buffer, skips comments and malformed lines by recursively calling `getrpcent()`, parses the service name, numeric RPC program number via `atoi()`, and up to 34 aliases. `getrpcbyname()` checks both canonical names and aliases; `getrpcbynumber()` scans sequentially.

This is process-global and not thread-specific. Returned `struct rpcent` data points into static storage overwritten by the next lookup. Parsing is permissive and historical: bad/comment lines are skipped rather than surfaced as explicit errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcport.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcport.c

Read completely: 85 lines.

Implements `getrpcport()`, the old IPv4-only helper that resolves a hostname with `gethostbyname()`, builds a `sockaddr_in`, and calls `pmap_getport()` for the requested program, version, and protocol.

It returns `0` on host lookup failure or no registered port. The implementation mutates `hp->h_length` if it exceeds the destination address length, which is an old-style convenience but surprising because the `hostent` storage is owned by resolver code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/mt_misc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/mt_misc.c

Read completely: 136 lines.

Defines the global mutexes and rwlocks used across the RPC/libnsl implementation when `_REENTRANT` is enabled. Locks cover service registration, service fd sets, rpcbind address cache, auth caches, raw transports, client fd state, simple-registration lists, socket compatibility creation, and public-key serialization.

Also defines the public/global `rpc_createerr` object and `__rpc_createerr()`. In threaded mode, `__rpc_createerr()` returns a thread-specific `struct rpc_createerr`, lazily allocated via a thread key; in single-threaded mode or allocation failure it falls back to the global object.

This file is infrastructure rather than protocol logic. It is important because many other files assume these lock symbols exist and because `rpc_createerr` has both legacy global and thread-local behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/mt_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_clnt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_clnt.c

Read completely: 127 lines.

Implements legacy portmapper registration wrappers `pmap_set()` and `pmap_unset()` on top of rpcbind. `pmap_set()` accepts only UDP or TCP, obtains the matching IPv4 netconfig via `__rpc_getconfip()`, converts a port into a universal address of the form `0.0.0.0.hi.lo`, converts that to a transport address with `uaddr2taddr()`, and calls `rpcb_set()`.

`pmap_unset()` attempts to remove the mapping for both UDP and TCP rpcbind netconfigs and returns success if either unset succeeds, preserving backward-compatible semantics.

The file is compatibility glue; modern address registration is delegated to rpcbind APIs and netconfig conversion helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_clnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getmaps.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getmaps.c

Read completely: 107 lines.

Implements `pmap_getmaps()`, which contacts the remote portmapper over TCP at `PMAPPORT`, calls `PMAPPROC_DUMP`, and decodes the returned `struct pmaplist` with `xdr_pmaplist()`.

It uses a 60-second timeout, creates a temporary TCP client with `clnttcp_create()`, prints client errors with `clnt_perror()`, destroys the client, and restores the input address port to zero before returning.

This is a legacy v2 portmapper query path. Returned map list ownership follows XDR allocation conventions and must be freed by callers with the matching XDR free path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getmaps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getport.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getport.c

Read completely: 132 lines.

Implements `pmap_getport()`, the legacy portmapper lookup for an IPv4 address, program, version, and protocol. It builds a `struct pmap`, sets the target address port to `PMAPPORT`, and calls `PMAPPROC_GETPORT`.

The initial client transport follows the requested protocol (`clnttcp_create()` for TCP, `clntudp_bufcreate()` otherwise). If the returned port is zero, it retries using the opposite transport. On RPC failure it sets `rpc_createerr.cf_stat = RPC_PMAPFAILURE`; on zero port it sets `RPC_PROGNOTREGISTERED`.

This provides old pmap behavior while using shared client constructors and global `rpc_createerr` state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot.c

Read completely: 76 lines.

Implements `xdr_pmap()`, the XDR serializer for a v2 portmapper mapping: program, version, protocol, and port, all as unsigned long fields.

It is a minimal protocol helper used by pmap client calls and pmap list serialization. It validates non-null arguments with `_DIAGASSERT` and returns `FALSE` if any field fails to encode/decode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot2.c

Read completely: 151 lines.

Implements `xdr_pmaplist()` and `xdr_pmaplist_ptr()` for linked lists of portmapper entries. The XDR representation is a recursive pointer union encoded as a boolean “more elements” flag followed by a `struct pmap`; this implementation unwinds that recursion into a loop and uses `xdr_reference()` per node.

The free path stores the next pointer before freeing the current node so iteration remains valid. `xdr_pmaplist_ptr()` is a compatibility wrapper with a different declared pointer shape.

This is core v2 portmapper list XDR used by `pmap_getmaps()` and legacy pmap dump handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_rmt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_rmt.c

Read completely: 177 lines.

Implements the legacy portmapper remote-call service. `pmap_rmtcall()` sends a UDP call to `PMAPPROC_CALLIT`, allowing lookup and invocation of a service procedure through the portmapper in one round trip.

`xdr_rmtcall_args()` is encode-only: it serializes program/version/procedure, reserves a length field, encodes caller-supplied arguments, computes the encoded length via XDR positions, then rewrites the length field. `xdr_rmtcallres()` is decode-only: it decodes the returned port and result length, then dispatches to the caller-supplied result XDR function.

This file is protocol glue for historical broadcast/remote-call flows; it assumes seekable XDR streams for the length rewrite.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_rmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_callmsg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_callmsg.c

Read completely: 212 lines.

Implements `xdr_callmsg()`, the XDR encoder/decoder for RPC call messages. It has optimized inline paths for encoding and decoding fixed fields plus credential/verifier auth blobs, and a fallback path using normal XDR primitives.

The function enforces `CALL` direction and `RPC_MSG_VERSION`, rejects auth bodies larger than `MAX_AUTH_BYTES`, and allocates `oa_base` with `mem_alloc()` on decode when the caller did not provide storage. It handles both credential and verifier opaque auth sections.

This is a critical wire-format routine used by service transports such as datagram and raw RPC. Correct caller initialization of `oa_base` matters: service dispatch uses stack credential storage, while generic decode can allocate.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_callmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_commondata.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_commondata.c

Read completely: 56 lines.

Defines shared exported RPC data: `_null_auth`, and under `_LIBC`, compatibility globals `svc_fdset` and `svc_maxfd`.

The `svc_fdset` object is a fixed 256-fd compatibility view (`__fd_set_256`) maintained by `svc_fdset.c` when the global fdset changes. This file intentionally contains common data only, not logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_commondata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_dtablesize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_dtablesize.c

Read completely: 61 lines.

Implements `_rpc_dtablesize()`, a small helper that caches `sysconf(_SC_OPEN_MAX)` in a static integer and returns it on later calls.

This avoids repeated syscalls for legacy RPC code that needs the process descriptor table size. There is no locking; benign races can only recompute the cached value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_dtablesize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_generic.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_generic.c

Read completely: 904 lines.

Provides generic RPC transport, netconfig, socket-info, and universal-address helpers. It maps nettype strings such as `netpath`, `visible`, `circuit_v`, `datagram_n`, `tcp`, and `udp` to internal classes, implements `__rpc_setconf()`/`__rpc_getconf()`/`__rpc_endconf()`, and filters `getnetconfig()` or `getnetpath()` results by visibility, semantics, protocol family, and protocol.

Important helpers include `__rpc_dtbsize()`, `__rpc_get_t_size()`, `__rpc_get_a_size()`, `__rpc_getconfip()`, `rpc_nullproc()`, `__rpcgettp()`, `__rpc_fd2sockinfo()`, `__rpc_nconf2sockinfo()`, `__rpc_nconf2fd()`, `__rpc_sockinfo2netid()`, `__rpc_seman2socktype()`, `__rpc_socktype2seman()`, `__rpc_sockisbound()`, and `__rpc_setnodelay()`.

`taddr2uaddr()`/`uaddr2taddr()` and their address-family helpers convert between transport `netbuf` addresses and RPC universal-address strings for IPv4, optional IPv6, and local sockets. IPv4/IPv6 universal addresses encode the port as two trailing decimal octets. IPv6 scope fixup copies link/site-local scope IDs from the rpcbind service address where possible.

Thread behavior: `__rpc_getconfip()` caches the discovered tcp/udp netids in static storage for single-threaded use and thread-specific storage when threaded. Reliability notes: universal address port parsing uses `atoi()` without strict numeric validation; AF_LOCAL conversion truncates to `sun_path` size by `strncpy()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_internal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_internal.h

Read completely: 85 lines.

Private libc RPC header declaring internal-only helpers and shared globals. It exposes private XDR-record functions, service transport unregister/idle-cleanup hooks, transport/address conversion helpers, rpcbind lookup helpers, socket/netconfig conversion helpers, `rpc_nullproc()`, `__rpc_sockisbound()`, `__rpc_getxid()`, and `_get_next_token()`.

It also declares service globals (`__svc_xports`, `__svc_maxrec`, `__svc_flags`, `__rpc_lowvers`) and, under `_REENTRANT`, all lock objects defined in `mt_misc.c`.

This is the coordination header for the RPC implementation internals; it is explicitly not an exported public interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_prot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_prot.c

Read completely: 349 lines.

Implements core RPC protocol XDR and reply-to-error mapping. XDR helpers include `xdr_opaque_auth()`, `xdr_des_block()`, `xdr_accepted_reply()`, `xdr_rejected_reply()`, `xdr_replymsg()`, and `xdr_callhdr()`.

`xdr_accepted_reply()` handles `SUCCESS` by dispatching to the result XDR callback and encodes version bounds for `PROG_MISMATCH`. `xdr_rejected_reply()` handles RPC-version mismatch and auth errors. `_seterr_reply()` maps decoded reply statuses into `struct rpc_err`, including version ranges and auth failure reasons.

This file is shared by client and server code. It is protocol-level, not transport-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_soc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_soc.c

Read completely: 430 lines.

Provides old socket-based RPC compatibility APIs when compiled with `PORTMAP`. Client constructors `clntudp_bufcreate()`, `clntudp_create()`, and `clnttcp_create()` are built on a shared `clnt_com_create()` that resolves tcp/udp netconfig, optionally creates a socket, looks up a port with `pmap_getport()`, binds a reserved local port, and calls `clnt_tli_create()`.

Server constructors `svctcp_create()`, `svcudp_bufcreate()`, `svcudp_create()`, `svcfd_create()`, and `svcraw_create()` adapt old interfaces to `svc_tli_create()`, `svc_fd_create()`, and `svc_raw_create()`. `get_myaddress()` returns loopback `PMAPPORT`. `callrpc()` and `registerrpc()` forward to `rpc_call()` and `rpc_reg()`.

`clnt_broadcast()` adapts the old sockaddr-in callback signature to `rpc_broadcast()` using thread-specific or global callback storage. The whole file is compatibility glue for TCP/UDP-only pre-netconfig RPC.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_soc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_clnt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_clnt.c

Read completely: 1271 lines.

Implements the client interface to rpcbind: `rpcb_set()`, `rpcb_unset()`, `rpcb_getaddr()`, `rpcb_getmaps()`, `rpcb_rmtcall()`, `rpcb_gettime()`, `rpcb_taddr2uaddr()`, `rpcb_uaddr2taddr()`, private `__rpcb_findaddr()`, and `__rpc_control()`.

The file maintains a small six-entry rpcbind address cache keyed by `(host, netid)`, protected by `rpcbaddr_cache_lock`. `getclnthandle()` checks the cache, deletes stale entries on failed client creation, resolves `sunrpc` with `getaddrinfo()`, creates an RPCB v4 client, and caches successful transport addresses plus optional universal address strings.

Local rpcbind access prefers the Unix-domain socket `_PATH_RPCBINDSOCK`; if that fails it discovers a loopback TCP transport from netconfig and connects to `127.0.0.1` or `::1`, caching the selected netconfig permanently.

`__rpcb_findaddr()` contains the main version-negotiation algorithm. With `PORTMAP`, IPv4 TCP/UDP first try portmapper v2. Then rpcbind v4/v3 are tried, using `RPCBPROC_GETADDRLIST` for connection-oriented transports via a datagram transport when possible, and falling back to `RPCBPROC_GETADDR`. It converts universal addresses to `netbuf`s and applies IPv6 scope fixup.

Registration sends owner as effective uid text. Remote calls use `RPCBPROC_CALLIT` across v4 then v3 and optionally return the responding address. Error paths set `rpc_createerr` with statuses such as `RPC_UNKNOWNPROTO`, `RPC_UNKNOWNHOST`, `RPC_PROGNOTREGISTERED`, `RPC_N2AXLATEFAILURE`, `RPC_PMAPFAILURE`, or `RPC_RPCBFAILURE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_clnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_prot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_prot.c

Read completely: 361 lines.

Implements XDR routines for rpcbind v3/v4 data structures: `xdr_rpcb()`, `xdr_rpcblist_ptr()`, `xdr_rpcblist()`, `xdr_rpcb_entry()`, `xdr_rpcb_entry_list_ptr()`, `xdr_rpcb_rmtcallargs()`, `xdr_rpcb_rmtcallres()`, and `xdr_netbuf()`.

Like the pmap list code, rpcbind map and entry-list serializers unwind pointer-recursive XDR lists into loops, with special handling for `XDR_FREE`. `xdr_rpcb_rmtcallargs()` writes the argument length after encoding by saving/restoring XDR stream positions. `xdr_netbuf()` bounds `maxlen` by `RPC_MAXDATASIZE` before serializing bytes.

This file is the main rpcbind wire-format implementation used by rpcbind clients, dumps, remote calls, and address conversion RPCs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_st_xdr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_st_xdr.c

Read completely: 279 lines.

Generated-from-RPCL XDR support for rpcbind statistics. It serializes address lookup stat lists, remote-call stat lists, per-procedure counters, per-version stats, and arrays of stats by rpcbind version.

Functions include `xdr_rpcbs_addrlist()`, `xdr_rpcbs_rmtcalllist()`, `xdr_rpcbs_proc()`, `xdr_rpcbs_addrlist_ptr()`, `xdr_rpcbs_rmtcalllist_ptr()`, `xdr_rpcb_stat()`, and `xdr_rpcb_stat_byvers()`. The remote-call list has inline encode/decode fast paths for its fixed numeric fields, then serializes `netid` and the next pointer.

This file is only for the rpcbind stats facility, not normal address lookup. Strings are bounded by `RPC_MAXDATASIZE`; linked lists use `xdr_pointer()` recursion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_st_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc.c

Read completely: 815 lines.

Implements the core server-side RPC dispatcher and service registry. Transport registration uses `xprt_register()`/`xprt_unregister()` with a dynamically grown `__svc_xports` array; index `-1` is reserved for raw transports. Registered fds are mirrored into `svc_fdset.c` state.

Service registration uses a global `svc_callout` list keyed by program, version, and optionally netid. `svc_reg()` records dispatch functions and registers with local rpcbind via `rpcb_set()` when a netconfig is supplied. `svc_unreg()` removes all matching callouts and unsets rpcbind mappings. `PORTMAP` builds also include legacy `svc_register()`/`svc_unregister()` using pmap.

The reply helpers construct accepted/denied RPC replies for success, no-procedure, decode error, system error, auth error, weak auth, no-program, and version mismatch. `svc_getreq_common()` receives messages from the selected transport, authenticates via `_authenticate()`, locates the matching service callout, dispatches, or returns program/version errors. It also handles batched requests and destroys dead transports.

`rpc_control()` currently supports setting/getting `RPC_SVC_CONNMAXREC`. Reliability notes: dispatch walks `svc_head` without holding `svc_lock` in `svc_getreq_common()`, relying on broader RPC usage assumptions; `svc_unreg()` frees `sc_netid` with an incorrect size expression, though `mem_free` may ignore size depending on allocator configuration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth.c

Read completely: 220 lines.

Implements the server authentication dispatcher. `_authenticate()` copies raw credentials into the request, resets the response verifier to null auth, dispatches built-in flavors `AUTH_NULL`, `AUTH_SYS`, and `AUTH_SHORT`, and then checks a mutex-protected list of dynamically registered custom auth handlers.

`_svcauth_null()` always returns `AUTH_OK`. `svc_auth_reg()` lets services register additional credential flavors; built-in flavors return “already registered”, duplicate custom flavors are rejected, and successful registrations are permanent for the process.

This file owns auth flavor dispatch, while actual AUTH_SYS decoding is in `svc_auth_unix.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth_unix.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth_unix.c

Read completely: 148 lines.

Implements server-side AUTH_UNIX/AUTH_SYS credential decoding. `_svcauth_unix()` decodes the credential body into the request’s cooked credential area, setting up an `authunix_parms` structure, fixed machine-name buffer, and fixed group array.

It uses an inline XDR fast path when possible, validating machine-name length against `MAX_MACHINE_NAME`, group count against `NGRPS`, and minimum encoded length against the credential length. On success it sets a null response verifier and returns `AUTH_OK`; malformed credentials return `AUTH_BADCRED`.

`_svcauth_short()` is intentionally gutted and always returns `AUTH_REJECTEDCRED`; shorthand Unix auth is not supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth_unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.c

Read completely: 626 lines.

Implements connectionless/datagram server transports. `svc_dg_create()` derives socket info from the fd, chooses send/receive sizes, allocates an `SVCXPRT`, datagram-private state, an aligned RPC buffer, an XDR memory stream, local address storage, and registers the transport.

Transport ops implement receive, reply, argument decode/free, destroy, status, and no-op control. `svc_dg_recv()` reads with `recvfrom()`, stores the remote address, decodes an RPC call with `xdr_callmsg()`, and checks the duplicate-request cache. `svc_dg_reply()` encodes `xdr_replymsg()`, sends with `sendto()`, and stores the reply in cache when enabled.

The duplicate-request cache (`svc_dg_enablecache()`, `cache_get()`, `cache_set()`) is a FIFO hash table keyed by xid, program, version, procedure, and remote address. Duplicate requests get the cached reply resent without redispatch. Cache state is protected by `dupreq_lock`.

Reliability notes: cache replacement reuses cached reply buffers but allocates a fresh copy of the remote address each set; replacement paths should be reviewed for old address-buffer ownership. `xp_rtaddr.len` is also used as allocation size for freeing, while `maxlen` is used in destroy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.h

Read completely: 51 lines.

Private header for datagram service transport state. It defines `struct svc_dg_data`, stored in `SVCXPRT.xp_p2`, containing the IO buffer size, current xid, XDR stream, verifier body storage, and optional duplicate-request cache pointer.

It also defines `__rpcb_get_dg_xidp(x)` so rpcbind-related code can access the datagram xid field. Comments state this header exists only so rpcbind code can include the datagram-private layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.c

Read completely: 494 lines.

Implements dynamic service fd-set and pollfd management. Internally `struct svc_fdset` tracks a resizable `fd_set`, current max fd, fd capacity, a resizable `pollfd` array, allocated poll capacity, and used poll slots. The global single-threaded instance can be replaced by per-thread instances when `svc_fdset_init(SVC_FDSET_MT)` is used.

Public helpers include `svc_fdset_init()`, `svc_fdset_zero()`, `svc_fdset_set()`, `svc_fdset_isset()`, `svc_fdset_clr()`, `svc_fdset_copy()`, `svc_fdset_get()`, `svc_fdset_getmax()`, `svc_fdset_getsize()`, `svc_pollfd_copy()`, `svc_pollfd_get()`, `svc_pollfd_getmax()`, and `svc_pollfd_getsize()`.

The fdset resizes in `FD_SETSIZE` chunks and can represent fds beyond the traditional fixed `FD_SETSIZE`. Poll arrays use `fd = -1` holes and shrink `fdused` when trailing slots become empty. Under `_LIBC`, `svc_fdset_sanitize()` updates legacy exported globals `svc_fdset` and `svc_maxfd`.

Reliability notes: per-thread initialization copies the global struct shallowly, so transition timing matters; callers protect access with `svc_fd_lock` in higher-level service code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.h

Read completely: 25 lines.

Small private header for service fd-set compatibility. In `RUMP_RPC` builds it remaps selected syscalls (`close`, `fcntl`, `read`, `write`, `pollts`, `select`) to rump syscall wrappers.

Under `_LIBC`, it defines `__fd_set_256`, the fixed-size compatibility fdset type used by `rpc_commondata.c` for the exported legacy `svc_fdset`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_generic.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_generic.c

Read completely: 326 lines.

Implements high-level server creation APIs `svc_create()`, `svc_tp_create()`, and `svc_tli_create()`. `svc_create()` iterates transports selected by `__rpc_setconf(nettype)`, reuses existing transports for the same netid from a static `xprtlist`, and registers each program/version with `svc_reg()`.

`svc_tp_create()` creates one transport with `svc_tli_create()`, unsets any old rpcbind mapping, and registers with rpcbind. `svc_tli_create()` opens a socket from netconfig when needed, detects socket info for provided fds, binds to a reserved or anonymous address when unbound, listens for non-datagram transports, then delegates to `svc_fd_create()`/`svc_vc_create()` for streams or `svc_dg_create()` for datagrams.

The created transport gets `xp_type`, `xp_netid`, and `xp_tp` filled from socket/netconfig data. This is the main bridge between netconfig transport selection and concrete service transport implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_raw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_raw.c

Read completely: 259 lines.

Implements the in-process “raw” RPC server transport used for testing/timing without kernel networking. A singleton `svc_raw_private` holds a shared raw buffer, embedded `SVCXPRT`, XDR memory stream, and verifier body. The buffer is shared with raw client code via global `__rpc_rawcombuf`.

`svc_raw_create()` initializes the singleton, sets `xp_fd = -1`, installs raw transport ops, creates an XDR decode stream over the shared buffer, and registers the transport. Receive/reply/getargs/freeargs operate on the shared memory XDR stream; destroy is a no-op.

All singleton access is serialized by `svcraw_lock`. This transport is intentionally process-local and not a real network service.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_raw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_run.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_run.c

Read completely: 214 lines.

Implements the server event loop and exit hook. `svc_run()` chooses between a `select()` loop and a `poll()` loop based on `__svc_flags & SVC_FDSET_POLL`.

Both loops copy the current service fd state under `svc_fd_lock`, wait up to 30 seconds, dispatch ready fds via `svc_getreqset2()` or `svc_getreq_poll()`, and call `__svc_clean_idle(NULL, 30, FALSE)` on timeout. They tolerate repeated `EINTR` and limited `EBADF` retries outside rump builds.

`svc_exit()` causes the loop to drain by clearing the service fdset under write lock. The loops then fail to get work and return through their cleanup paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_simple.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_simple.c

Read completely: 319 lines.

Implements `rpc_reg()`, the simplified server registration front end used by `registerrpc()`-style code. It creates or reuses one service transport per netid for the requested nettype, allocates a shared XDR argument buffer per netid, registers a universal dispatcher with `svc_reg()`, and records each `(program, version, procedure, netid)` in `proglst`.

The universal dispatcher handles `NULLPROC` with an empty reply, finds the matching registration for the incoming program/version/procedure/netid, zeroes the shared input buffer, decodes arguments, calls the registered function, sends the encoded reply, and frees decoded arguments.

This interface is intentionally simple but constrained: one shared argument buffer per netid limits usable argument size to the transport receive size and serialization is guarded by `proglst_lock`, so registered procedure callbacks run while that lock is held.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_simple.c -->