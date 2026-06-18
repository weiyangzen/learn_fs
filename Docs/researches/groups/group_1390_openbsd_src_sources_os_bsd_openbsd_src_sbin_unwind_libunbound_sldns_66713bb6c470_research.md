# Group Research: group_1390_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_sldns_66713bb6c470

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.c

`wire2str.c` implements sldns/libunbound DNS wire-format to presentation-format conversion. It defines lookup tables for DNSSEC algorithms, DS hashes, CERT algorithms, rcodes, opcodes, wire parse errors, EDNS flags/options, EDNS EDE codes, TSIG errors, and SVCB parameter keys.

The public allocation-returning helpers (`sldns_wire2str_pkt`, `sldns_wire2str_rr`, `sldns_wire2str_dname`, `sldns_wire2str_type`, `sldns_wire2str_class`, `sldns_wire2str_rcode`) are two-pass wrappers around buffer/scanner APIs: first compute required length, then allocate and print.

Packet scanning prints dig-style sections: header, question, answer, authority, additional, message size, and trailing garbage if present. RR scanning recognizes OPT records as EDNS, parses owner names with compression loop protection, prints TTL/class/type, reads rdatalen, then tries descriptor-driven pretty RDATA parsing before falling back to RFC3597-style `\# <len> <hex>` output. Malformed/partial data is usually rendered as an error plus available hex rather than aborting.

RDATA conversion is routed by `sldns_wire2str_rdf_scan()` across DNS field types: names, integers, periods, TSIG times, A/AAAA, character strings, APL, base32/base64/hex, NSEC bitmaps, NSEC3 salt/owner, CERT/algorithm fields, LOC, WKS/service bitmaps, NSAP, ATMA, IPSECKEY, HIP, ILNP64, EUI48/EUI64, unquoted/tag/long strings, SVCB parameters, and TSIG errors.

The file contains specialized SVCB/HTTPS SvcParam formatting for `mandatory`, `alpn`, `no-default-alpn`, `port`, `ipv4hint`, `ech`, `ipv6hint`, and default quoted values. It validates length constraints and returns failure to trigger unknown-format fallback when wire data is inconsistent.

EDNS handling prints OPT metadata, DO/CO flags, extended rcode, UDP size, and option comments. Supported option printers include LLQ, UL, NSID, DAU, DHU, N3U, client subnet, keepalive, padding, and EDE. Unknown options are hex-rendered.

Default RR comments are added for DNSKEY key tag/role/key size, RRSIG key tag, and NSEC3 opt-out. The implementation is careful about bounded output buffers, null termination through `sldns_str_print`, compressed-name loop limits, and preserving partial diagnostic output for corrupt DNS packets.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.h

`wire2str.h` declares the sldns wire-to-text conversion interface used by libunbound. It exposes lookup-table globals for algorithms, hashes, CERT algorithms, rcodes, opcodes, EDNS flags/options/EDE codes, wire parse errors, and TSIG errors.

The API is organized in three layers. First are malloc-returning convenience functions for packets, RRs, dnames, type/class names, and rcodes. Second are buffer functions that return the needed character count and silently truncate if the caller buffer is too small. Third are scanner functions that consume `uint8_t**`/length input and advance output `char**`/length pointers as each wire element is parsed.

The header documents scanner behavior in detail: outputs are null-terminated when buffers are supplied, return values are character counts excluding the terminating NUL, input/output pointers are advanced, malformed input may produce shorter diagnostic output, and domain-name scanners optionally use a packet buffer plus compression-loop state.

Declared conversion coverage includes packet headers, full RRs, question RRs, unknown RR/RDATA RFC3597 output, RR comments, types/classes/TTLs, SVCB parameters, all supported RDF field kinds, and EDNS option-specific printers. This header is the contract matched by `wire2str.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/wire2str.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/Makefile.inc

`Makefile.inc` adds libunbound utility sources to the OpenBSD `unwind` build. It sets `.PATH` to `libunbound/util` and appends allocator, config parser/lexer, EDNS, locks, event, module, networking, proxy protocol, randomness, tree, regional allocation, RTT, siphash, TCP limit, timing, tube, event plugin, logging, and winsock event sources.

Because this subtree already has another `log.c` naming context, it builds `util_log.c` by symlinking `${.CURDIR}/libunbound/util/log.c` and registers that generated symlink in `CLEANFILES`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.c

`alloc.c` implements libunbound’s per-thread allocation cache for two hot allocation classes: packed RRset keys (`alloc_special_type`) and reusable `regional` query-state arenas. A top-level allocator has a lock and serves as a shared super-cache; thread-local allocators can keep small local quarantines to reduce malloc/free and lock contention.

Special RRset allocation initializes embedded locks and key pointers, assigns per-thread 64-bit IDs, and recycles freed objects through local or super caches. IDs reserve high bits for the thread number and detect wraparound; on exhaustion, the configured cleanup callback is invoked to clear caches holding stale RRset IDs.

Regional allocation keeps up to ten custom 16 KiB regional arenas per allocator. Released arenas are reset with `regional_free_all()` and cached unless the per-allocator limit has been reached.

With `UNBOUND_ALLOC_STATS`, the file wraps malloc/calloc/free/realloc/strdup with accounting headers, a magic marker, and optional log-at-call-site wrappers. With `UNBOUND_ALLOC_LITE`, it adds front/back guard bytes, detects overwrite on free/realloc, fills allocated/freed memory with debug patterns, and wraps selected sldns/OpenSSL allocation-returning APIs so they use the lite allocator.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.h

`alloc.h` declares the allocation cache API and data structures. `alloc_special_type` is an alias for `struct ub_packed_rrset_key`; helper macros clean its ID and store freelist links in `entry.overflow_next`.

`struct alloc_cache` contains the optional super allocator pointer, a lock for top-level allocators, the special-object quarantine list/count, thread-number and ID range state, an ID-overflow cleanup callback, and cached regional arena state.

The public API initializes/clears caches, clears special objects, obtains/releases special RRset objects, allocates fresh IDs, reports memory/statistics, obtains/releases regional arenas, and installs the ID cleanup callback.

When `UNBOUND_ALLOC_LITE` is enabled, the header remaps `malloc`, `calloc`, `free`, `realloc`, `strdup`, selected sldns string conversion functions, `sldns_pkt2wire`, and `i2d_DSA_SIG` to checked wrappers implemented in `alloc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.c

`as112.c` defines the static AS112/local-use reverse-zone list exported as `as112_zones`. The array contains RFC1918 reverse zones, shared-address-space `100.64.0.0/10` reverse zones, link-local/test/broadcast IPv4 reverse zones, IPv6 unspecified/link-local/ULA-related reverse zones, and related local-use reverse delegations.

The array is NULL-terminated and contains no logic. Consumers use it as a built-in list of zones that should normally be answered locally or blocked from leaking to the public DNS hierarchy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.h

`as112.h` declares `extern const char** as112_zones` and documents its purpose: a NULL-terminated list of text-format AS112/local-use domain names that Unbound should normally avoid sending toward the public internet.

It has only include guards and the exported declaration; all data lives in `as112.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/as112.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.c

`config_file.c` owns libunbound configuration construction, parsing, mutation, querying, cleanup, and runtime application. `config_create()` allocates `struct config_file` and fills extensive defaults for transport, logging, caches, RTT/infra behavior, DNSSEC validation, local zones/data, remote control, rate limits, DNSCrypt/DNSTAP/cachedb/IPsec modules when compiled, cookies, padding, scrub limits, and quotas. `config_create_forlib()` derives smaller library defaults.

`config_set_option()` is the imperative option setter used by lib callers. It normalizes option names to colon form, validates integers/yes-no/power-of-two/memory sizes, updates strings/lists, and applies selected side effects immediately: log timestamp formatting, cache TTL globals, RTT globals, serve-expired globals, infra rate-limit globals, AUTR holddown behavior, TLS protocol validation, NSID parsing, port permit/avoid policy, local-zone parsing, and outgoing-interface array growth. Unsupported parser-only sections return failure.

`config_get_option()` mirrors a broad set of options through callback-based printing macros. `config_get_option_list()` and `config_get_option_collate()` collect those callback results into list or newline-joined string form. It supports scalar, string, list, pair/triple list, interface array, memory-size, and tag-list output.

`config_read()` handles direct config files and optional glob expansion for includes. It opens files, initializes the global parser state, invokes the generated parser, reports accumulated parse errors with filename/line context, disables DNSCrypt port when DNSCrypt is off, and computes automatic slab values based on thread count.

The destructor layer frees all nested config allocations: string lists, pair/triple lists, auth/stub/view objects, arrays, tag byte lists, module-specific fields, cache/rate-limit lists, control interfaces, trust anchors, local data/zones, and file paths. This is important because `config_create()` may fail mid-construction and calls `config_delete()` on the partial object.

Utility routines cover outgoing port initialization from `iana_ports.inc`, permit/avoid range parsing, port condensation to dense arrays, optional Linux ephemeral-port-range policy, parser error callbacks, string-list insertion/appending/find helpers, UTC date parsing, memory-size parsing, tag definition and bitset parsing/printing/intersection, NSID parsing from `ascii_` or hex forms, applying config values to global runtime variables, username lookup, and chroot/chdir-aware filename construction.

Local DNS helpers parse `local-zone` values, convert `local-data-ptr` IP/name input into reverse PTR records, determine whether remote-control interfaces are filesystem sockets or addresses, test whether an interface/port is TLS, proxy-protocol, HTTPS, DNSCrypt, or QUIC, scan automatic interface port lists, validate/derive allowed TLS protocol versions, and return file mtimes with nanosecond support when the platform exposes it.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.c -->