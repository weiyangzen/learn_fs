# Group Research: group_1196_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_nameser_ns_name_c_sou_191d24580768

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_name.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_name.c

Read completely: 1153 lines.

Implements DNS counted-name conversion, compression, decompression, comparison, and label mapping helpers for libc/resolver. Public entry points include `ns_name_ntop`, `ns_name_pton`, `ns_name_pton2`, `ns_name_ntol`, `ns_name_unpack`, `ns_name_unpack2`, `ns_name_pack`, `ns_name_uncompress`, `ns_name_compress`, `ns_name_rollback`, `ns_name_skip`, `ns_name_length`, `ns_name_eq`, `ns_name_owned`, `ns_name_map`, and `ns_name_labels`.

Presentation names are escaped per DNS rules, wire names enforce label and total-name limits, unpacking follows compression pointers with loop detection, and packing searches prior suffixes through caller-owned `dnptrs`. Legacy EDNS0 bitstring labels are still supported through `DNS_LABELTYPE_BITSTRING`.

Security/reliability notes: most malformed input paths set `errno` to `EMSGSIZE`, `EINVAL`, `ENOENT`, or `EISDIR`. The pointer and size checks are central; changes near compression, `labellen`, or bitstring encode/decode need malformed DNS packet tests.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_netint.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_netint.c

Read completely: 65 lines.

Provides function-symbol wrappers for resolver byte-order operations: `ns_get16`, `ns_get32`, `ns_put16`, and `ns_put32`. Each delegates to the corresponding nameser macro.

Security/reliability notes: no bounds checks are performed; callers must ensure the buffer has the required 2 or 4 bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_netint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_parse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_parse.c

Read completely: 285 lines.

Parses DNS messages into `ns_msg`, `ns_rr`, and `ns_rr2` views. It defines `_ns_flagdata`, `ns_msg_getflag`, `ns_skiprr`, `ns_initparse`, `ns_parserr`, and `ns_parserr2`.

`ns_initparse` validates the packet structure by walking all sections. `ns_parserr` expands owner names to presentation format; `ns_parserr2` unpacks them to uncompressed wire format. Question records omit TTL/RDATA parsing, while other sections parse TTL, RDLENGTH, and RDATA pointers.

Security/reliability notes: malformed/truncated packets return `EMSGSIZE`; invalid section or RR indexes return `ENODEV`. Parsed RDATA points into the original message buffer, so callers must keep that buffer alive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_print.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_print.c

Read completely: 1287 lines.

Formats DNS resource records into zone-file-style text. Public entry points are `ns_sprintrr` and `ns_sprintrrf`, with helpers for origin pruning, character strings, names, lengths, strings, and tab alignment.

It handles common address/name records, structured records such as `SOA`, `MX`, `SRV`, `NAPTR`, DNSSEC-related records including `DNSKEY`, `RRSIG`, `DS`, `NSEC`, `NSEC3`, and legacy/special records such as `A6`, `OPT`, `TKEY`, `TSIG`, and `CERT`. Unknown or malformed records fall back to hex-style output.

Security/reliability notes: output writes are bounded through helper routines and report `ENOSPC`. RR-specific parsing is manual; new record formatting should add explicit `rdata`/`edata` checks before every field read.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_samedomain.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_samedomain.c

Read completely: 216 lines.

Implements textual DNS-domain relationship helpers. Under `_LIBRESOLV`, it provides `ns_samedomain` and `ns_subdomain`; under `_LIBC`, it provides `ns_makecanon` and `ns_samename`.

The code trims unescaped trailing dots, compares whole-label suffixes, treats an empty ancestor as root, canonicalizes names to one trailing dot, and compares canonical names case-insensitively.

Security/reliability notes: `ns_makecanon` checks output size and returns `EMSGSIZE` on overflow. Correct escaped-dot handling is the main edge case.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_samedomain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_ttl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_ttl.c

Read completely: 167 lines.

Formats DNS TTL values with `ns_format_ttl`, producing compact week/day/hour/minute/second strings. Outside `_LIBC`, also parses TTL strings with `ns_parse_ttl`.

Security/reliability notes: formatting checks destination space and returns `-1` on overflow. The non-libc parser validates units and syntax but accumulates into `u_long`, so overflow behavior should be considered if reused.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_ttl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htonl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htonl.c

Read completely: 16 lines.

Lint-only stub for `htonl(uint32_t)`. It undefines macro forms and returns `0`.

Security/reliability notes: not runtime conversion logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htonl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htons.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htons.c

Read completely: 16 lines.

Lint-only stub for `htons(uint16_t)`. It undefines macro forms and returns `0`.

Security/reliability notes: not runtime conversion logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_htons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohl.c

Read completely: 16 lines.

Lint-only stub for `ntohl(uint32_t)`. It undefines macro forms and returns `0`.

Security/reliability notes: not runtime conversion logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohs.c

Read completely: 16 lines.

Lint-only stub for `ntohs(uint16_t)`. It undefines macro forms and returns `0`.

Security/reliability notes: not runtime conversion logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Lint_ntohs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Makefile.inc

Read completely: 155 lines.

Defines libc networking source composition, generated lexer/parser rules, machine-dependent byte-order source inclusion, man pages, and manual-page links.

It includes resolver/base64/ethers/host/network/protocol/service lookups, `getaddrinfo`, `getnameinfo`, interface helpers, SCTP calls, and optional Hesiod/IPv6 pieces. Architecture-specific `htonl`, `htons`, `ntohl`, and `ntohs` are included through `${ARCHDIR}/net/Makefile.inc`.

Security/reliability notes: no runtime behavior, but build flags such as `USE_INET6` and `MKHESIOD` alter exported libc networking coverage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/base64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/base64.c

Read completely: 350 lines.

Implements resolver base64 conversion through `b64_ntop` and `b64_pton`.

Encoding writes padded base64 text from binary data, checks destination capacity, and NUL-terminates. Decoding uses a state machine, accepts whitespace, validates padding, and rejects non-zero unused trailing bits.

Security/reliability notes: short output buffers and invalid input return `-1`. The decoder’s unused-bit validation helps enforce canonical base64.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/ethers.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/ethers.c

Read completely: 221 lines.

Implements Sun-style `/etc/ethers` helpers: `ether_ntoa`, `ether_aton`, `ether_ntohost`, `ether_hostton`, and `ether_line`, with libc weak aliases.

`ether_ntoa` formats Ethernet addresses, `ether_aton` parses colon-separated hex bytes, `ether_line` parses one database line, and host/address lookup functions scan `_PATH_ETHERS` with optional YP support.

Security/reliability notes: `ether_ntoa` and `ether_aton` use static storage and are not thread-safe. Parsing casts `%x` values to `u_char`, so byte values above `0xff` are not strict errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/ethers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getaddrinfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getaddrinfo.c

Read completely: 2889 lines.

Implements `getaddrinfo`, `freeaddrinfo`, `allocaddrinfo`, and `gai_strerror`, including files/DNS/NIS backends and result ordering. It supports IPv4, optional IPv6, numeric hosts, scoped IPv6 literals, hosts-file lookup, DNS A/AAAA/SRV lookup, service resolution, `AI_ADDRCONFIG`, `AI_CANONNAME`, `AI_PASSIVE`, `AI_NUMERICHOST`, `AI_NUMERICSERV`, and NetBSD `AI_SRV`.

The top-level flow validates hints, resolves service constraints, handles NULL/numeric names first, dispatches FQDN lookups through `nsdispatch`, and reorders non-passive nonnumeric results. DNS paths build `res_target` chains, parse answers in `getanswer`, handle CNAMEs, and sort SRV targets by priority/weight.

Security/reliability notes: allocation ownership is clear: `allocaddrinfo` stores sockaddr inline and `freeaddrinfo` frees each node and canon name. DNS parsing is pointer-heavy and must preserve `eom` and RDLENGTH checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getaddrinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/gethnamaddr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/gethnamaddr.c

Read completely: 1364 lines.

Implements traditional host database APIs and reentrant variants: `gethostbyname_r`, `gethostbyname2_r`, `gethostbyaddr_r`, `gethostent_r`, and non-reentrant wrappers. It also provides DNS and optional YP backend callbacks.

`getanswer` parses DNS A, AAAA, PTR, and CNAME responses into caller buffers, validates names, stores aliases/address lists, sorts IPv4 addresses by resolver sortlist, supports multiple PTR aliases, and maps IPv4 to IPv4-mapped IPv6 under `RES_USE_INET6`. Hosts-file parsing uses `fparseln`.

Security/reliability notes: reentrant APIs avoid static result buffers; non-reentrant wrappers use shared static state. DNS and hosts-file buffer packing is subtle and should be tested with malformed packets and long alias lists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/gethnamaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getifaddrs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getifaddrs.c

Read completely: 306 lines.

Implements `getifaddrs` and `freeifaddrs`. It retrieves interface data through `sysctl` over `NET_RT_IFLIST`, sizes the required linked-list, sockaddr, name, and `if_data` storage, then fills one combined allocation.

It handles `RTM_IFINFO` and `RTM_NEWADDR`, including link-layer addresses, netmasks, broadcast addresses, interface flags, address flags, and aligned interface data.

Security/reliability notes: route-message iteration trusts kernel-provided lengths. `freeifaddrs` frees the single allocation; nested pointers must not be freed separately.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getifaddrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnameinfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnameinfo.c

Read completely: 639 lines.

Implements `getnameinfo` for IPv4/IPv6, AppleTalk, link-layer, and local-domain sockaddr families. It supports numeric and reverse-name host output, service lookup, `NI_NUMERICHOST`, `NI_NAMEREQD`, `NI_NUMERICSERV`, `NI_DGRAM`, IPv6 scope IDs, and link-layer formatting.

INET handling validates sockaddr length, resolves services through `getservbyport_r` unless numeric output is requested, avoids reverse DNS for unsuitable address classes, and falls back to numeric text when allowed.

Security/reliability notes: short buffers return `EAI_MEMORY` or `EAI_OVERFLOW` depending on path. Non-INET formatters assume the caller supplied host storage when requesting host output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnameinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnetent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnetent.c

Read completely: 166 lines.

Implements sequential network database access: `setnetent`, `endnetent`, and `getnetent`.

It opens `_PATH_NETWORKS`, skips comments and malformed lines, parses network name, network number via `inet_network`, and up to 34 aliases into static storage. `setnetent` and `endnetent` also call host database open/close routines for legacy behavior.

Security/reliability notes: uses static storage and a process-global file pointer, so it is not reentrant or thread-safe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnetent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnetnamadr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnetnamadr.c

Read completely: 651 lines.

Implements `getnetbyaddr` and `getnetbyname` with files, DNS, and optional YP backends through `nsdispatch`.

Files lookup scans `getnetent`. DNS lookup queries PTR records, including RFC1101-style network names under `in-addr.arpa`; `parse_reversed_addr` validates and converts `d.c.b.a.IN-ADDR.ARPA` names back to network numbers. YP support uses `networks.byaddr` and `networks.byname`.

Security/reliability notes: results use static `struct netent`, alias arrays, and buffers. DNS answer parsing manually advances through compressed names and RDATA, so bounds checks around `dn_expand`, `GETSHORT`, and packet end pointers are critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getnetnamadr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getpeereid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getpeereid.c

Read completely: 68 lines.

Implements `getpeereid` for local-domain sockets. It verifies the socket family with `getsockname`, rejects non-`AF_LOCAL` sockets with `EOPNOTSUPP`, then reads peer credentials via `getsockopt(SOL_LOCAL, LOCAL_PEEREID)`.

Security/reliability notes: `euid` and `egid` are optional output pointers. Errors from `getsockname` and `getsockopt` pass through directly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getpeereid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname.c

Read completely: 56 lines.

Thread-serialized non-reentrant wrapper for `getprotobyname_r`. It locks `_protoent_mutex`, searches using shared `_protoent_data`, unlocks, and returns the shared result.

Security/reliability notes: the mutex protects libc’s shared protocol database state, but the returned pointer refers to shared storage overwritten by later protocol lookups.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname_r.c

Read completely: 77 lines.

Implements `getprotobyname_r`. It opens or rewinds the protocols database, iterates entries from `getprotoent_r`, and matches the canonical protocol name or aliases.

Security/reliability notes: asserts `name != NULL`. If `stayopen` is false, it closes the protocol file after the search. Result storage is owned by the supplied `protoent_data`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber.c

Read completely: 57 lines.

Thread-serialized non-reentrant wrapper for `getprotobynumber_r`. It locks `_protoent_mutex`, uses shared `_protoent_data`, unlocks, and returns the shared result.

Security/reliability notes: returned storage is shared and may be overwritten by later protocol database calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber_r.c

Read completely: 66 lines.

Implements `getprotobynumber_r`. It opens or rewinds the protocols database, iterates entries through `getprotoent_r`, and returns the first entry whose `p_proto` matches the requested protocol number.

Security/reliability notes: if `stayopen` is false, it closes the file after lookup. It relies on `getprotoent_r` for parsing and allocation failure handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent.c

Read completely: 80 lines.

Provides non-reentrant protocol database APIs: `setprotoent`, `endprotoent`, and `getprotoent`. It defines the shared `_protoent_data` and, when reentrant support is enabled, `_protoent_mutex`.

Each public function locks the shared mutex and delegates to the corresponding `_r` implementation.

Security/reliability notes: serialization protects shared state, but returned protocol entries are still backed by shared storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent_r.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent_r.c

Read completely: 152 lines.

Implements reentrant protocol database iteration: `setprotoent_r`, `endprotoent_r`, and `getprotoent_r`.

It reads `_PATH_PROTOCOLS` with `fparseln`, skips malformed entries, parses protocol name, number, and aliases, and grows the alias array with `reallocarr`. `endprotoent_r` closes the file and frees line and alias storage.

Security/reliability notes: allocation failures clean up via `endprotoent_r` while preserving `errno`. Alias storage is dynamically resized, avoiding the fixed alias cap used by older database parsers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname.c

Read completely: 56 lines.

Thread-serialized non-reentrant wrapper for `getservbyname_r`. It locks `_servent_mutex`, searches using shared `_servent_data`, unlocks, and returns the shared service entry.

Security/reliability notes: returned storage is shared and may be overwritten by later service database calls. Protocol filtering is delegated to `getservbyname_r`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname.c -->