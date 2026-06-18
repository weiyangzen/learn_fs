# Group Research: group_1391_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__622f7c4aa261

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.h

`config_file.h` is Unbound's central configuration schema and public configuration API. It declares `struct config_file`, which stores daemon-wide resolver settings for listener ports, address families, UDP/TCP behavior, TLS, DNS-over-HTTPS, DNS-over-QUIC, DNSCrypt, socket buffers, outgoing port pools, caches, infra-cache timing, iterator policy, DNSSEC validation, local zones, response-IP policy, RPZ, views, remote control, dnstap, cachedb, ipset, EDNS options, cookies, logging, and iterator scrub limits.

The main structure is intentionally broad because many subsystems consume parsed configuration directly. Transport fields cover standard DNS, TCP reuse and keepalive, TLS service/upstream settings, HTTP/2 buffer limits and endpoint, QUIC size/port, proxy-protocol ports, automatic interface handling, outgoing interfaces, port permit/avoid policy, DSCP, transparent/freebind sockets, and TCP connection limits. Resolver-resource fields cover message, rrset, key, negative, infra, rate-limit, DNSCrypt, and cachedb cache sizes and slab counts, with helper APIs for auto-selecting slab values and parsing memory-size strings.

Policy and data configuration are modeled as linked lists and small list structs. `config_stub` represents stub and forward zones with hosts, addresses, priming/fallback, TCP/TLS upstream, and no-cache flags. `config_auth` represents auth-zone and RPZ-backed auth-zone configuration, including masters, URLs, allow-notify, zonefile, downstream/upstream use, fallback, RPZ tag/action/log/CNAME settings, and ZONEMD checks. `config_view` stores per-view local-zone data, nodefault and optional ipset lists, response-IP policy, and fallback-to-global behavior. Generic `config_strlist`, `config_str2list`, `config_str3list`, and `config_strbytelist` carry repeated string or tag-bitlist directives.

The header exports lifecycle and access functions: create default configs for daemon or library use, read config files, delete and apply configs, look up configured UID/GID, set and get options by name, collate option values, and print options through callbacks. It also exposes insertion, search, deletion, and parsing helpers for list-based configuration, stub lookup, tag definition/parsing/intersection, local-zone parsing, outgoing port parsing/condensing, filename conversion around chroot/chdir, PTR reverse record synthesis, and option-specific validation helpers such as TLS protocol validation.

Parser integration is declared through `struct config_parser_state`, the global `cfg_parser`, lexer/parser entry points renamed to `ub_c_*`, error-reporting helpers, and the `ub_c_in`/`ub_c_out` lexer streams. Additional utility APIs report whether interfaces listen on HTTPS/TLS/DNSCrypt/QUIC/PROXYv2 ports, whether HTTPS or QUIC is enabled, file mtime state, and memory used by strings. The header is the contract tying the yacc parser, config file implementation, daemon setup, worker modules, views, RPZ, auth zones, networking, and validation modules together.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/config_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.h

`configparser.h` is the generated yacc token header for Unbound configuration parsing. It assigns numeric token IDs for lexical categories such as spaces, newlines, comments, colons, zone strings, and string arguments, then enumerates every recognized configuration keyword token from `VAR_SERVER` through `VAR_LOG_THREAD_ID`.

The token list mirrors the directives implemented in `configparser.y` and the fields declared in `config_file.h`. It includes server options for networking, caches, DNSSEC, local zones, views, tagging, response-IP, rate limiting, DNS64/NAT64, TLS/DoH/DoQ, cookies, dnstap, DNSCrypt, cachedb/Redis, ipset, auth-zones, RPZ, dynamic libraries, iterator scrub options, and logging. Because this file is generated from the grammar, its numeric values are part of the compile-time interface between the lexer and parser rather than hand-authored business logic.

The semantic value type is a single-member `YYSTYPE` union carrying `char* str`; every meaningful parser argument is passed from the lexer as an allocated string and then consumed or freed by grammar actions. The header also declares the global `yylval` used by the lexer to hand values to the parser. In this OpenBSD libunbound copy, `configyyrename.h` maps these yacc names to `ub_c_*` names to avoid symbol collisions with other lex/yacc parsers in the same program.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.y

`configparser.y` is the yacc grammar that turns Unbound configuration files into mutations on `struct config_file`. It includes the parser symbol renaming header, the config schema, network helpers, and sldns string-to-wire utilities, then declares one string-valued semantic type and a large token set matching all supported configuration directives.

The grammar is organized around top-level clauses: `server:`, `stub-zone:`, `forward-zone:`, `view:`, `auth-zone:`, `rpz:`, `remote-control:`, `dnstap:`, `python:`, `dynlib:`, `dnscrypt:`, `cachedb:`, and `ipset:`. Starting a compound clause allocates or selects the appropriate config object and marks parsing as being inside a top-level block. Clause endings validate required names for stub, forward, and view blocks. `force_toplevel` resets parser state for include-style or API-driven parsing.

Most `server:` productions parse one directive and write one field or list entry. Numeric directives are parsed with `atoi()` plus explicit checks for zero-allowed options, power-of-two slab counts, port ranges, maximum EDNS size, HTTP/QUIC buffer sizes, RTT/timeouts, and bounds such as DSCP 0..63 or ECS prefix lengths. Boolean directives consistently accept only `yes` or `no`. String directives replace owned strings after freeing old values, while repeated directives insert into linked lists. Memory-size directives delegate to `cfg_parse_memsize`, port allow/avoid directives delegate to `cfg_mark_ports`, tags use `config_add_tag` and `config_parse_taglist`, and local-data-ptr directives call `cfg_ptr_reverse`.

The parser handles transport and protocol options for IPv4/IPv6/NAT64, UDP/TCP, TCP reuse and keepalive, upstream TCP/TLS, TLS certificates/ciphers/protocols/SNI/session-ticket keys, DoH endpoint normalization, QUIC feature warnings when ngtcp2 is missing, DNSCrypt provider keys/certs/nonces/shared-secret caches, PROXYv2 ports, EDNS client strings, cookies and cookie-secret hex parsing, and socket options such as SO_RCVBUF/SO_SNDBUF/SO_REUSEPORT/IP_TRANSPARENT/IP_FREEBIND/IP_DSCP. It also captures logging controls, daemon/chroot/user/directory changes, root hints, trust anchors, DNSSEC validation settings, serve-expired/EDE behavior, QNAME minimisation, iterator scrub limits, and anti-abuse rate/wait/global quota controls.

Local policy parsing covers local-zone types, local data, local-zone overrides, view assignment, interface and ACL actions, tag data/action maps, response-IP actions and data, private addresses/domains, caps-for-id whitelist, DNS64/NAT64 policy, and access-control entries. The same local-zone type validation appears for global and per-view local zones, with special handling for `nodefault` and optional `ipset` zones. ACL and response-IP actions are checked by helper functions at the end of the file.

Stub, forward, auth-zone, RPZ, and view clauses populate their current head object in the config lists. Stubs and forwards support name, host, address, first/prime/no-cache, and TCP/TLS upstream flags. Auth zones support name, zonefile, masters, URLs, allow-notify, downstream/upstream serving, fallback, and ZONEMD controls. RPZ clauses are backed by `config_auth` objects marked `isrpz`, with defaults disabling downstream/upstream serving, and add RPZ tags, override action validation, CNAME override, logging name, and NXDOMAIN RA signaling. Views carry per-view local zones/data, response-IP policy, and the `view-first` fallback flag.

Optional modules are guarded by compile-time macros. CLIENT_SUBNET, IPsecmod, cachedb/Redis, DNSCrypt, and ipset directives either populate fields when enabled or free the argument while ignoring the directive when the feature is absent. Deprecated or removed options such as DLV anchors, infra lame settings, low-rtt, and client-subnet opcode are accepted but logged or ignored, preserving compatibility with older config files.

The file ends with `validate_respip_action()` and `validate_acl_action()`, which centralize allowed action names for response-IP and access-control directives. Overall, `configparser.y` is a direct, side-effecting parser: syntax recognition, semantic validation, allocation ownership, feature gating, and compatibility handling are all embedded in grammar actions that build the runtime `config_file`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configparser.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configyyrename.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configyyrename.h

`configyyrename.h` renames yacc and lex global symbols for the configuration parser so they do not collide with other generated parsers linked into the same binary. It maps generic names such as `yyparse`, `yylex`, `yyerror`, `yylval`, parser tables, parser stack variables, lexer buffer functions, allocation hooks, lexer streams, and debug/line/text accessors to `ub_c_*` names.

The header is included before parser/lexer generated code and effectively makes the config parser's ABI names unique to Unbound's config subsystem. It covers both yacc-side symbols (`yychar`, `yynerrs`, `yytable`, `yycheck`, stack pointers, etc.) and flex-side symbols (`yy_create_buffer`, `yy_switch_to_buffer`, `yy_scan_string`, `yyget_lineno`, `yylex_destroy`, `yyalloc`, and related APIs). The result is that callers use declarations such as `ub_c_parse`, `ub_c_lex`, `ub_c_in`, and `ub_c_error` from `config_file.h` while the generated source can still be written in normal yacc/flex terms.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/configyyrename.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/Makefile.inc

`util/data/Makefile.inc` is the OpenBSD make include for the bundled libunbound data utilities used by `unwind`. It adds `${.CURDIR}/libunbound/util/data` to `.PATH` and appends the data-layer source files to `SRCS`.

The selected files are `dname.c`, `msgencode.c`, `msgparse.c`, `msgreply.c`, and `packed_rrset.c`. This make fragment therefore pulls in domain-name handling, DNS message parsing/encoding, reply structures, and packed RRset support for the local libunbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.c

`dname.c` implements Unbound's low-level domain-name routines for DNS wire-format names. It handles uncompressed query names, compressed packet names, case-insensitive comparison and hashing, decompression/copying, printable debug output, label counting, subdomain checks, wildcard checks, canonical ordering, and shared-topdomain discovery.

Parsing helpers distinguish query names from packet names. `query_dname_len()` reads an uncompressed name from an `sldns_buffer`, rejects compression pointers, length overruns, and names beyond `LDNS_MAX_DOMAINLEN`, and leaves the buffer after the name. `dname_valid()` validates an already resident uncompressed name against an allocation length. `pkt_dname_len()` handles DNS packet compression pointers, follows them with `MAX_COMPRESS_PTRS` loop protection, validates pointer bounds and label lengths, accumulates the decompressed length, and restores the buffer position to the first byte after the compressed name.

Case normalization and comparison functions preserve wire data where needed. `query_dname_tolower()` lowercases an uncompressed name in place. `pkt_dname_tolower()` lowercases a packet name while following compression pointers and stopping on bounds or pointer-loop problems. `query_dname_compare()` and `dname_pkt_compare()` compare labels case-insensitively, with the packet form resolving compression pointers from the containing buffer. Hashing is similarly label-oriented: `dname_query_hash()` and `dname_pkt_hash()` lowercase each label into a temporary buffer and feed it to `hashlittle`, producing the same hash whether the packet name was compressed or not.

Copying and rendering utilities include `dname_pkt_copy()`, which decompresses a valid packet name into an uncompressed output buffer and terminates early on excessive pointers, bad labels, or excessive total length; `dname_buffer_write()`, which writes an uncompressed name into a packet buffer with space checks; `dname_print()`, which prints a compressed or uncompressed name to a stream with diagnostic placeholders for bad compression or extended labels; and `dname_str()`, which emits a safe printable string, replacing non-alnum/non-`-`/`_`/`*` characters with `?` and using sentinel characters for overlong or malformed names.

Label and hierarchy helpers provide the operations used by zone trees and DNSSEC logic. `dname_count_labels()` and `dname_count_size_labels()` count labels including the root and optionally return total length. `dname_lab_cmp()` compares names label-by-label from the shared right-hand side and reports how many topdomain labels matched, using case-insensitive label comparison. `dname_lab_startswith()` tests whether a label begins with a lowercase prefix and returns the remaining label pointer. `dname_has_label()` scans for a case-insensitive label match. `dname_strict_subdomain()`, `dname_strict_subdomain_c()`, and `dname_subdomain_c()` identify strict or inclusive subdomain relationships using label comparisons. `dname_remove_label()`, `dname_remove_label_limit_len()`, and `dname_remove_labels()` walk a name upward toward its parent while adjusting the caller's pointer and length.

DNSSEC-specific helpers include `dname_signame_label_count()`, which implements the RRSIG Labels count by excluding root and an initial wildcard label, `dname_is_wild()`, which recognizes `*.` names, and canonical comparison functions. `dname_canon_lab_cmp()` uses RFC 4034-style canonical label ordering where shorter labels sort first after equal lowercased prefixes, `dname_canonical_compare()` counts labels and applies that comparison, and `dname_get_shared_topdomain()` returns a pointer into the first name at the shared suffix found by label comparison.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.h

`dname.h` declares the DNS domain-name utility interface implemented by `dname.c`. It documents that routines operate on DNS wire-format domain names, either uncompressed in memory or compressed inside an `sldns_buffer`, and defines `MAX_COMPRESS_PTRS` as the compression-pointer loop limit.

The parsing and validation API includes `query_dname_len()` for uncompressed query names, `dname_valid()` for resident uncompressed names, and `pkt_dname_len()` for compressed packet names with pointer checking. Case and comparison APIs include `query_dname_tolower()`, `pkt_dname_tolower()`, `query_dname_compare()`, and `dname_pkt_compare()`. Hashing and copying APIs include `dname_query_hash()`, `dname_pkt_hash()`, `dname_pkt_copy()`, and `dname_buffer_write()`.

The header also exposes label and hierarchy utilities: label counting with optional size reporting, label-wise comparison with matching-suffix count, prefix and label-presence checks, strict and inclusive subdomain tests, root detection, removal of one or more leading labels, and conversion to debug printable forms through `dname_print()` and `dname_str()`. DNSSEC and zone-order helpers include RRSIG label counting, wildcard-name detection, canonical RFC 4034-style label comparison, whole-name canonical comparison, and shared-topdomain lookup.

Callers are expected to pass valid uncompressed names to most non-packet routines and provide the packet buffer when compression pointers may need to be resolved. The API is shared by message parsing/encoding, packed RRset handling, local-zone and auth-zone ordering, DNSSEC validation, and resolver cache/key comparisons.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/dname.h -->