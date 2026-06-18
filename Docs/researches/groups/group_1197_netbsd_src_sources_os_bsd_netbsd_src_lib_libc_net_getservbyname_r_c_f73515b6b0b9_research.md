# Group Research: group_1197_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_net_getservbyname_r_c_f73515b6b0b9

Scope: `Docs/research_subset_a.md`, NetBSD source tree under `sources/os/bsd/netbsd-src/lib/libc`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname_r.c

Reentrant service lookup by service name and optional protocol. `getservbyname_r()` opens service state with `setservent_r()`, searches with `_servent_getbyname()`, and closes the backing store unless `_SV_STAYOPEN` is set.

The implementation supports both compiled CDB service data and plain `/etc/services` parsing. The CDB path builds a length-prefixed key from `name` and `proto`, validates returned record bounds, checks aliases/name entries, and delegates record decoding to `_servent_parsedb()`. The plain-file path iterates `_servent_getline()` / `_servent_parseline()`, matches the canonical service name or aliases, and then applies the protocol filter.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport.c

Thread-safe public wrapper for non-reentrant `getservbyport()`. It locks `_servent_mutex`, calls `getservbyport_r()` using the global `_servent_data.serv` and `_servent_data`, then unlocks and returns the shared `struct servent *`.

This file contains no parsing logic; all storage handling and lookup behavior are in `getservbyport_r.c` and `getservent_r.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport_r.c

Reentrant service lookup by network-order port and optional protocol. `getservbyport_r()` opens service state, calls `_servent_getbyport()`, and closes unless stay-open mode is active.

The CDB path converts the requested port with `be16toh()`, constructs a key containing zero name length, protocol length, encoded port, and protocol bytes, then validates the returned record before parsing it. The plain-file path iterates service records and compares `sp->s_port` directly against the caller’s port value, with an optional protocol string check.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservent.c

Non-reentrant service database API wrappers. It defines the global `_servent_data` and, under `_REENTRANT`, `_servent_mutex`.

`setservent()`, `endservent()`, and `getservent()` serialize access to the global service state and call their `_r` equivalents. Returned records live in the shared global state, so callers needing independent storage use the reentrant functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservent_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservent_r.c

Core reentrant implementation for the services database. `_servent_open()` prefers `_PATH_SERVICES_CDB` via `cdbr_open()` and falls back to `_PATH_SERVICES` opened as a close-on-exec plain file; it also resets cached line, alias, and CDB buffer storage when opening fresh.

Plain-file parsing uses `fparseln()` and splits service lines into name, port/protocol, and aliases, growing the alias vector as needed. CDB iteration uses `cdbr_get()` and `_servent_parsedb()`, which decodes binary records into `struct servent`, copies data into `sd->cdb_buf` when not staying open, and grows alias storage with `reallocarr()`.

`setservent_r()` opens and marks stay-open state, `endservent_r()` closes and frees all dynamic buffers, and `getservent_r()` selects either CDB iteration or plain-file parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservent_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/hesiod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/hesiod.c

Thread-safe Hesiod resolver implementation built around resolver-state APIs such as `res_nmkquery()` and `res_nsend()`. `hesiod_init()` allocates a context, reads `/etc/hesiod.conf` or compiled defaults, and honors `HESIOD_CONFIG` / `HES_DOMAIN` only when not running set-id.

`hesiod_to_bind()` converts a Hesiod name/type pair into a DNS name, handling `name@rhs` forms and `rhs-extension` lookups. `hesiod_resolve()` performs TXT lookups against the configured class order, while `get_txt_records()` constructs DNS queries, validates answer boundaries, filters TXT answers by class/type, and returns a NULL-terminated string vector.

The bottom of the file implements the older `hes_*` compatibility interface using one static context and translated Hesiod error codes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/hesiod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/hostent.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/hostent.h

Internal header for NetBSD host database reentrant helpers. It declares non-standard `sethostent_r()`, `gethostent_r()`, `endhostent_r()`, `gethostbyname*_r()`, and `gethostbyaddr_r()` interfaces used inside libc to provide thread-safe host lookups.

It also exposes internal test hooks for `/etc/hosts`, DNS, and optional NIS host lookups, plus buffer-packing macros `HENT_ARRAY`, `HENT_COPY`, and `HENT_SCOPY`. `MAXALIASES` and `MAXADDRS` are fixed at 35.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/hostent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_indextoname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_indextoname.c

Implementation of `if_indextoname()`. It calls `getifaddrs()`, scans AF_LINK addresses for a matching `sdl_index`, copies the interface name into the caller-provided buffer with `strlcpy()`, and frees the address list.

If no interface matches, it returns `NULL` and sets `errno` to `ENXIO`; `getifaddrs()` failures preserve their own `errno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_indextoname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_nameindex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_nameindex.c

Implementation of `if_nameindex()` and `if_freenameindex()`. It gathers interfaces with `getifaddrs()`, counts AF_LINK entries and total name storage, then performs one allocation containing the `struct if_nameindex` array plus all copied interface names.

The result is terminated with `{ 0, NULL }`. `if_freenameindex()` frees the single allocation returned by `if_nameindex()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_nameindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_nametoindex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_nametoindex.c

Implementation of `if_nametoindex()`. It first tries a close-on-exec AF_INET datagram socket and `SIOCGIFINDEX` ioctl for the supplied name.

If that path fails, it falls back to `getifaddrs()` and scans AF_LINK entries by name. If no interface matches, it returns `0` and sets `errno` to `ENXIO`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/if_nametoindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/inet6_scopeid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/inet6_scopeid.c

KAME-compatibility helpers for embedded IPv6 scope IDs. When compiled with `__KAME__`, `inet6_getscopeid()` extracts bytes 2-3 from link-local, multicast link-local, or site-local addresses into `sin6_scope_id` and clears those address bytes.

`inet6_putscopeid()` performs the inverse operation: it writes the scope ID back into bytes 2-3 in network order and clears `sin6_scope_id`. Without `__KAME__`, both functions compile to no-ops.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/inet6_scopeid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/ip6opt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/ip6opt.c

IPv6 Hop-by-Hop and Destination option construction/parsing helpers for both RFC2292 and RFC3542 APIs. The older `inet6_option_*` functions operate on ancillary `cmsghdr` objects, insert Pad1/PadN options, maintain `ip6e_len`, and iterate or search options with strict length checks through `ip6optlen()`.

The newer `inet6_opt_*` functions operate directly on extension-header buffers. They validate 8-byte header sizing, option type/length/alignment constraints, skip padding while iterating, and use byte-copy helpers for unaligned option data values.

`inet6_insert_padopt()` centralizes Pad1 versus PadN encoding for padding lengths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/ip6opt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/iso_addr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/iso_addr.c

Converters for legacy ISO network addresses. `iso_addr()` parses hexadecimal digits with delimiters into a static `struct iso_addr` containing up to 20 address bytes, using a small state machine for one- and two-nibble bytes.

`iso_ntoa()` converts an ISO address back to dotted lowercase hexadecimal text in a static 64-byte buffer. Both APIs return static storage and are therefore not reentrant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/iso_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/linkaddr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/linkaddr.c

Link-layer address text conversion helpers. `link_addr()` parses an optional interface-name prefix followed by delimited hexadecimal bytes into a caller-provided `sockaddr_dl`, setting `AF_LINK`, `sdl_nlen`, `sdl_alen`, and possibly extending `sdl_len`.

`link_ntoa()` formats a `sockaddr_dl` into static storage, preserving the optional interface-name prefix and rendering address bytes as dot-separated lowercase hex. It bounds output through the `ADDC` macro and forces the last byte of the static buffer to NUL before formatting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/linkaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nsdispatch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nsdispatch.c

NetBSD libc name-service switch dispatcher. It maintains global database-to-source maps and loaded NSS modules, with default source lists for `files`, `compat`, and `nis` variants.

`_nsconfigure()` watches `_PATH_NS_CONF`, parses it with the lexer/parser, rebuilds the map/module arrays, and sorts them for binary search. Threaded builds use a read/write lock plus a per-thread recursion list so recursive `nsdispatch()` calls do not attempt configuration reloads while holding a read lock.

`nsdispatch()` selects the configured source list or caller defaults, resolves a callback from the caller’s dispatch table or dynamic `nss_*.so` modules, passes variadic arguments to the method, and stops based on the source’s status flags unless force-all behavior is requested.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nsdispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nslexer.l -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nslexer.l

Flex lexer for `nsswitch.conf`. It skips blanks, comments, and escaped newlines, returns `NL`, status tokens (`SUCCESS`, `UNAVAIL`, `NOTFOUND`, `TRYAGAIN`), action tokens (`RETURN`, `CONTINUE`), and lowercased source/database strings.

String token allocation failures are logged to syslog and converted into a newline token. `_nsyyerror()` logs parse errors with file name, line number, message, and current token text.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nslexer.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nsparser.y -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/nsparser.y

Yacc grammar for `nsswitch.conf`. It parses database entries of the form `database: source [criteria] ...`, constructs `ns_dbt` records, and stores them through `_nsdbtput()`.

Each source defaults to returning on `NS_SUCCESS`; criteria toggle return/continue bits for success, unavailable, not found, and try-again statuses. `_nsaddsrctomap()` rejects mixing `compat` with other sources, rejects duplicate sources, and logs source-addition failures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/nsparser.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/protoent.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/protoent.h

Internal header for protocol database reentrant state. `struct protoent_data` stores the backing `FILE *`, current `struct protoent`, alias vector, stay-open flag, current line buffer, and a dummy compatibility pointer.

It declares the global `_protoent_data`, optional `_protoent_mutex`, and reentrant protocol lookup functions: `getprotoent_r()`, `getprotobyname_r()`, `getprotobynumber_r()`, `setprotoent_r()`, and `endprotoent_r()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/protoent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/rcmd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/rcmd.c

Implementation of classic BSD remote-command and remote-user trust helpers. `rcmd()` / `rcmd_af()` resolve the target, canonicalize the host name when possible, and either use a local `RCMD_CMD`/rsh execution path for the shell service or the reserved-port network protocol through `resrcmd()`.

`resrcmd()` obtains reserved local ports, connects with retry/backoff on refusal, optionally creates the stderr side channel, validates the peer’s reserved stderr port, sends local user, remote user, and command strings, then waits for the server’s one-byte status. `rshrcmd()` instead forks, sets up socketpairs, drops to the local user, and execs either a local shell for same-user localhost or an rsh command with `-4`/`-6` as appropriate.

The file also implements `rresvport*()` reserved-port binding and `ruserok()` / `iruserok*()` trust checks. `.rhosts` handling temporarily switches effective uid/gid to the local user, requires regular owner-safe files, supports `+`, `-`, and netgroup syntax, and validates hostnames through forward/reverse address matching.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/rcmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/recv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/recv.c

Small compatibility wrapper for `recv()`. It implements `recv(s, buf, len, flags)` as `recvfrom(s, buf, len, flags, NULL, NULL)`.

There is no independent syscall logic or buffering in this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/recv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/rthdr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/rthdr.c

IPv6 routing-header helper APIs for legacy RFC2292 and RFC3542 interfaces. The RFC2292 functions allocate ancillary-data space, initialize type-0 routing headers, append loose route addresses, report segment counts, return addresses, and report loose-hop flags.

The RFC3542 functions operate directly on routing-header buffers: `inet6_rth_space()`, `inet6_rth_init()`, `inet6_rth_add()`, `inet6_rth_reverse()`, `inet6_rth_segments()`, and `inet6_rth_getaddr()`. Only `IPV6_RTHDR_TYPE_0` is supported, with validation of length parity, segment count, and index bounds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/rthdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sctp_sys_calls.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sctp_sys_calls.c

Userland SCTP convenience wrappers around ioctls, socket options, `sendmsg()`, and `recvmsg()`. It implements address conversion for IPv4-mapped IPv6, multi-address connect/bind helpers, association ID lookup, peer/local address list retrieval and freeing, send/receive helpers, `sctp_recvv()`, `sctp_sendv()`, and `sctp_peeloff()`.

The send wrappers build SCTP control messages such as `SCTP_SNDRCV`, `SCTP_SNDINFO`, `SCTP_PRINFO`, `SCTP_AUTHINFO`, and destination-address ancillary data. The receive wrappers scan returned control messages for SCTP metadata and copy the requested receive info shape when the caller supplied enough storage.

The address-list functions return pointers into allocated `struct sctp_getaddresses` buffers and the matching free functions subtract the hidden header offset before freeing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sctp_sys_calls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/send.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/send.c

Small compatibility wrapper for `send()`. It implements `send(s, msg, len, flags)` as `sendto(s, msg, len, flags, NULL, 0)` and exports the weak alias for libc namespace handling.

There is no independent socket-send implementation here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/servent.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/servent.h

Internal header for service database state and helpers. `struct servent_data` stores plain-file and CDB handles, current service record, alias vector, flags, CDB iterator index, CDB copy buffer, and current parsed line.

It defines service-state flags `_SV_STAYOPEN`, `_SV_CDB`, `_SV_PLAINFILE`, and `_SV_FIRST`, declares the global `_servent_data` and optional mutex, and exposes reentrant public helpers plus internal open/close/parse routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/servent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sethostent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sethostent.c

Host database control and dispatch implementation. It provides `sethostent()`, `endhostent()`, and related reentrant helpers that coordinate resolver state, `/etc/hosts` file state, and name-service-switch dispatch for host lookups.

The implementation is part of the libc host lookup stack declared by `hostent.h`, connecting public host APIs to backend sources such as files, DNS, and optional NIS through `nsdispatch()`. State is serialized for the non-reentrant public interfaces and kept in caller-supplied buffers for the `_r` variants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sethostent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sockatmark.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sockatmark.c

Implementation of `sockatmark()`. It asserts the socket descriptor is not `-1`, issues `ioctl(s, SIOCATMARK, &val)`, and returns either `-1` on ioctl failure or the returned at-mark value.

This is a thin libc wrapper around the socket ioctl.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/sockatmark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/vars6.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/vars6.c

Definitions of standard constant IPv6 addresses exported by libc. It defines `in6addr_any`, `in6addr_loopback`, `in6addr_nodelocal_allnodes`, `in6addr_linklocal_allnodes`, and `in6addr_linklocal_allrouters` from the corresponding initializer macros.

Weak aliases expose the namespace-prefixed variants where supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/vars6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/Makefile.inc

Build include for libc native language support catalog routines. It adds the `nls` directory to `.PATH`, builds `catclose.c`, `catgets.c`, and `catopen.c`, and installs their manual pages.

`catopen.c` receives an extra include path for libc citrus headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catclose.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catclose.c

Implementation of `_catclose()`. It rejects `(nl_catd)-1` with `EBADF`; for non-null descriptors it unmaps the mapped catalog data using the stored size and frees the descriptor object.

A null catalog descriptor is accepted and returns success without doing work.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catclose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catgets.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catgets.c

Implementation of `_catgets()`. It validates the catalog descriptor, then binary-searches the mapped catalog set table for `set_id` and the message table for `msg_id`.

Catalog numeric fields are read in network byte order with `ntohl()`. On success it returns a pointer into the mapped message text; on missing set/message it sets `errno = ENOMSG` and returns the caller’s fallback string.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catgets.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catopen.c

Implementation of `catopen()` and `catopen_l()`. Absolute or relative catalog names are loaded directly; bare names are expanded through `NLSPATH` unless set-id, otherwise the built-in default path is used.

Locale selection uses `LC_MESSAGES` from the supplied locale for `NL_CAT_LOCALE`, otherwise `LANG`, with slash-containing or missing locale names falling back to `C`. It resolves aliases through `/usr/share/nls/nls.alias`, expands `%L` and `%N` path substitutions, and tries each path element.

`load_msgcat()` opens the catalog close-on-exec, mmaps it read-only, checks `_NLS_MAGIC`, and returns an allocated descriptor storing the map and size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nls/catopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/Makefile.inc

Build include for POSIX.1e and NFSv4 ACL libc support. It adds `posix1e` and `sys/kern` to `.PATH`, defines `_ACL_PRIVATE`, and builds ACL object manipulation, parsing, text conversion, validation, kernel syscall wrappers, and NFSv4 support files.

It also installs ACL, extended attribute, and POSIX.1e manual pages with many MLINK aliases for public API variants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_branding.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_branding.c

Internal ACL brand tracking for unknown, POSIX.1e, and NFSv4 ACL semantics. It derives an ACL pointer from an entry pointer via alignment masking, reads/sets `ats_brand`, and checks whether an ACL or entry may be branded as a requested semantic.

Branding controls type validation: NFSv4-branded ACLs accept `ACL_TYPE_NFS4`, POSIX-branded ACLs accept access/default types, and unknown ACLs remain permissive. `acl_get_brand_np()` exposes the current brand after validating arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_branding.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_calc_mask.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_calc_mask.c

Implementation of `acl_calc_mask()` for POSIX.1e ACLs. It validates the pointer, brands the ACL as POSIX, duplicates it, computes the union of permissions from `ACL_USER`, `ACL_GROUP`, and `ACL_GROUP_OBJ` entries, and writes that value into an existing `ACL_MASK` entry or appends a new one.

The resulting ACL is validated with `acl_valid()` before replacing the caller’s ACL contents. Capacity failures and invalid inputs set `errno` and clean up the duplicate.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_calc_mask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_compat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_compat.c

Symbol-compatibility wrappers for applications built before NFSv4 ACL permission expansion. The old exported symbols forward to current `acl_get_perm_np()`, `acl_add_perm()`, and `acl_delete_perm()`.

`__sym_compat()` binds those wrappers to the `FBSD_1.0` symbol versions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_copy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_copy.c

Implements `acl_copy_entry()`. It rejects null or identical source/destination entries, ensures the destination can take the source entry’s ACL brand, brands it accordingly, and copies tag, id, permissions, entry type, and flags.

`acl_copy_ext()` and `acl_copy_int()` are present but unimplemented, returning `ENOSYS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete.c

Thin deletion wrappers for file, link, and fd ACL removal. `acl_delete_def_file()` and `acl_delete_def_link_np()` delete default ACLs, while `acl_delete_file_np()`, `acl_delete_link_np()`, and `acl_delete_fd_np()` normalize old ACL type values with `_acl_type_unold()` and call the corresponding internal syscall wrapper.

No ACL parsing or validation is performed in this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete_entry.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete_entry.c

Entry deletion helpers for ACL objects. `acl_delete_entry()` validates ACL and entry brands, copies the target entry, removes every matching entry, shifts later entries down, clears the unused slot, and resets the cursor.

Matching is brand-sensitive: NFSv4 entries compare tag and entry type, plus id for user/group entries; POSIX-style entries compare tag and id. `acl_delete_entry_np()` deletes a specific offset with similar shifting and cursor reset.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_delete_entry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_entry.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_entry.c

ACL entry creation and iteration. `acl_create_entry()` appends a blank undefined entry if capacity allows, initializes tag/id/permissions/type/flags, and resets the ACL cursor.

`acl_create_entry_np()` inserts at a requested offset by shifting existing entries upward. `acl_get_entry()` supports `ACL_FIRST_ENTRY` and `ACL_NEXT_ENTRY`, returning `1` for an entry, `0` at end, and `-1` for invalid requests.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_entry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_flag.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_flag.c

NFSv4 ACL flag-set operations. The helper `_flag_is_invalid()` rejects flags outside `ACL_FLAGS_BITS`.

`acl_add_flag_np()`, `acl_clear_flags_np()`, `acl_delete_flag_np()`, and `acl_get_flag_np()` mutate or query raw flag sets. `acl_get_flagset_np()` and `acl_set_flagset_np()` operate on an ACL entry’s `ae_flags` and require that the entry may be NFSv4-branded; setting the flagset brands the entry as NFSv4.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_flag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_free.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_free.c

Implementation of `acl_free()`. It calls `free()` when the supplied pointer is non-null and always returns success.

The local assignment `obj_p = NULL` has no caller-visible effect.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_free.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text.c

Text-to-ACL parser for POSIX.1e and NFSv4 forms. `acl_from_text()` duplicates the input, initializes an ACL, strips comments, splits entries by comma/newline, auto-detects NFSv4 versus POSIX by counting separators, brands the ACL, and dispatches each entry to the appropriate parser.

The POSIX parser expects `tag:qualifier:permission`, maps user/group/mask/other tags, resolves user/group names or numeric ids through `_acl_name_to_id()`, converts permissions with `_posix1e_acl_string_to_perm()`, and appends entries with `_posix1e_acl_add_entry()`.

Validation with `acl_valid()` is present but disabled, so successful parsing can return ACLs without final validity checking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text_nfs4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text_nfs4.c

NFSv4 ACL text-entry parser used by `acl_from_text()`. It parses tags such as `owner@`, `group@`, `everyone@`, `user`, and `group`, optional qualifiers, access masks, optional flags, entry types (`allow`, `deny`, `audit`, `alarm`), and optional appended numeric ids for unresolved names.

The parser creates an entry first, fills it through public ACL setters, and deletes the entry on malformed or truncated input. Name resolution uses `_acl_name_to_id()`, and unresolved user/group names require an appended id field.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text_nfs4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_get.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_get.c

ACL retrieval and accessor functions. `acl_get_file()`, `acl_get_link_np()`, and `acl_get_fd_np()` allocate an ACL with `ACL_MAX_ENTRIES`, normalize old type values, call internal kernel wrappers, set maximum count, and brand the ACL from the requested type. `acl_get_fd()` selects NFSv4 or access ACLs based on `fpathconf(fd, _PC_ACL_NFS4)`.

The accessors return permission-set pointers, allocate and return user/group qualifiers, read tag types, and read NFSv4 entry types after brand compatibility checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_id_to_name.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_id_to_name.c

Internal id-to-name helper for ACL text output. `_posix1e_acl_id_to_name()` maps `ACL_USER` ids through `getpwuid()` and `ACL_GROUP` ids through `getgrgid()`, unless `ACL_TEXT_NUMERIC_IDS` requests numeric output.

Missing names fall back to decimal ids. The source comments note that the function is not thread-safe because it relies on stateful password/group database APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_id_to_name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_init.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_init.c

ACL allocation and duplication. `acl_init()` rejects negative counts and counts above `ACL_MAX_ENTRIES`, allocates aligned `struct acl_t_struct` storage with `posix_memalign()`, zeroes it, sets the brand to unknown, and sets kernel ACL max count.

`acl_dup()` allocates a fresh ACL, copies the structure, and resets both source and destination iteration cursors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_perm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_perm.c

Permission-set operations for POSIX.1e and NFSv4 ACL bits. `_perm_is_invalid()` accepts only a single permission bit that belongs to the union of POSIX.1e and NFSv4 permission masks.

`acl_add_perm()`, `acl_clear_perms()`, `acl_delete_perm()`, and `acl_get_perm_np()` validate arguments, mutate/query the bitset, and set `EINVAL` for invalid permission values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_perm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_set.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_set.c

ACL setter and mutator functions. File, link, and fd setters normalize ACL type values, reject ACL/type brand mismatches, sort POSIX.1e ACLs before submission, reset the iterator cursor, and call the internal kernel set wrappers. `acl_set_fd()` selects NFSv4 versus access ACL based on `fpathconf()`.

Entry mutators set permission sets, qualifiers, tag types, and NFSv4 entry types. Permission setting brands entries as NFSv4 when NFSv4-only permission bits are used; tag and entry-type setters enforce brand compatibility and reject unknown values with `EINVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_set.c -->