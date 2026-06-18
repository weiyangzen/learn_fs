# Group Research: group_1392_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__e400d455cdbb

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.c

## Role

`msgencode.c` encodes Unbound DNS query and reply data structures back into DNS wire-format packets. It handles DNS name compression, RRset section insertion, TTL adjustment, truncation behavior, EDNS OPT attachment, EDE size trimming, minimal responses, local-alias insertion, and error response construction.

Although this file is under the OpenBSD `unwind` vendored `libunbound` tree in subset A, its domain is DNS resolver message serialization rather than filesystem logic.

## Main Implementation

The file builds an in-message compression tree with `compress_tree_node`. `compress_tree_search()`, `compress_tree_lookup()`, `compress_tree_store()`, `write_compressed_dname()`, `compress_owner()`, `compress_any_dname()`, and `compress_rdata()` maintain compression targets and emit compressed owner names or RDATA names. Compression is capped by `MAX_COMPRESSION_PER_MESSAGE` to bound CPU cost and avoids pointer chains for compatibility.

`packed_rrset_encode()` writes a `ub_packed_rrset_key` plus `packed_rrset_data` as one or more DNS RRs, optionally including data RRs and/or RRSIGs. It filters DNSSEC records when DNSSEC is not requested, applies fixed/upstream-zero/absolute/expired TTL rules, round-robins data RRs, and recompresses compressible RDATA types by consulting `sldns_rr_descriptor`.

`insert_section()` serializes answer, authority, and additional sections. It trims a failing RRset back to its section start when packet space runs out. Additional-section handling emits ordinary RRs first and RRSIGs afterward when DNSSEC is enabled.

`reply_info_encode()` writes the DNS header and question, then serializes local aliases, answer, authority, and additional sections. It handles whole-RRset truncation, TC-bit setting for answer/authority truncation, and minimal-response suppression for clear positive or negative answers.

## EDNS and Error Encoding

`calc_edns_field_size()`, `calc_edns_option_size()`, and `calc_ede_option_size()` estimate OPT-record space from outgoing EDNS option lists. `ede_trim_text()` removes EDE extra text, and can unlink `LDNS_EDE_OTHER` options when the text would no longer be useful.

`attach_edns_record_max_msg_sz()` appends an OPT RR, writes outgoing callback/module EDNS options, reserves padding when requested, and respects an explicit maximum packet size. `reply_info_answer_encode()` chooses reply flags, reserves EDNS space before encoding the base response, and retries EDNS attachment with full EDEs, trimmed EDE text, or EDE removal.

`qinfo_query_encode()` emits a basic outbound query packet. `extended_error_encode()` and `error_encode()` build QR/RA error replies, preserve RD/CD, include the question when available, and attach EDNS when it fits so extended RCODEs can be conveyed.

## Research Notes

Correctness depends on buffer-position discipline and count patching after section writes. Truncation is intentionally RRset-granular except additional-section omission, and EDNS/EDE handling is opportunistic so a response can still be sent when optional metadata does not fit.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.h

## Role

`msgencode.h` declares the public message-encoding API for converting `query_info`, `reply_info`, and `edns_data` structures into DNS wire-format buffers.

## API Surface

The main reply entry points are `reply_info_answer_encode()` and `reply_info_encode()`. The first is the higher-level answer encoder that derives response flags from query flags, cache/auth state, DNSSEC state, and EDNS metadata. The second regenerates a DNS packet from stored reply data and handles whole-RRset truncation and optional minimal-response suppression.

`qinfo_query_encode()` serializes a query from `query_info`. `calc_edns_field_size()`, `calc_edns_option_size()`, `calc_ede_option_size()`, and `attach_edns_record()` expose EDNS OPT sizing and appending helpers. `error_encode()` and `extended_error_encode()` build DNS error packets with optional question and EDNS data.

## Dependencies and Contracts

The header forward-declares `sldns_buffer`, `query_info`, `reply_info`, `regional`, and `edns_data`, keeping callers decoupled from the concrete parser and reply storage internals. Callers provide a scratch `regional` allocator for compression state and must supply packet-size limits such as 512, EDNS UDP size, or TCP-sized buffers.

## Research Notes

The contract distinguishes allocation failure from truncation: public functions usually return failure for memory/server errors while successful truncation still returns a valid packet. Extended errors above classic 4-bit RCODE space require EDNS attachment to be visible on the wire.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgencode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.c

## Role

`msgparse.c` parses DNS wire-format packets into temporary `msg_parse`, `rrset_parse`, and `rr_parse` structures. It validates packet bounds, groups RRs into RRsets, associates RRSIGs with their covered RRsets, extracts EDNS OPT metadata, and provides helpers for skipping or removing parsed RRs.

## Message and RRset Parsing

`parse_packet()` reads the DNS header, enforces at most one question, parses the query section, then parses answer, authority, and additional sections. It tolerates a missing additional OPT in one lenient case and ignores trailing spurious packet bytes.

`parse_section()` walks RRs in a section. For each RR it parses the owner name, type, class, and TTL/RDATA framing, then calls `find_rrset()` and `add_rr_to_rrset()`. The parser hashes by owner name/type/class/flags into a 32-bucket parse table, while also optimizing for sequential RRs with the same owner.

`calc_size()` computes decompressed in-memory RDATA size, expanding domain names in RDATA for types whose `sldns_rr_descriptor` marks embedded names. `skip_ttl_rdata()`, `skip_pkt_rr()`, and `skip_pkt_rrs()` safely advance over uninterested records.

## RRSIG and Section Handling

The file has detailed RRSIG grouping logic. `pkt_rrsig_covered()` reads the covered type from RRSIG RDATA. `rrset_has_sigover()`, `moveover_rrsigs()`, and `change_rrsig_rrset()` allow signatures that appear before or after their data RRset to be attached to the final dataset.

`find_rrset()` also handles NSEC-apex and negative-SOA flag differences, compares compressed names with `smart_compare()`, and handles special qtype `RRSIG` or `ANY` cases so signatures are not incorrectly split or duplicated.

If the same RRset appears in multiple sections, `add_rr_to_rrset()` drops later less-trustworthy parts rather than merging section trust levels, following the RFC 2181 RRset placement rule.

## EDNS Parsing

`parse_extract_edns_from_response_msg()` scans parsed additional RRsets for OPT, removes the selected OPT RRset from the parsed message, initializes `edns_data`, and copies incoming EDNS options into a region list.

`parse_edns_from_query_pkt()` is a direct query-path EDNS parser. It validates query-section assumptions, rejects answer/authority complications unless skipped successfully, enforces at most one additional OPT, reads EDNS version/bits/UDP size, and delegates option handling to `parse_edns_options_from_query()`.

`parse_edns_options_from_query()` handles NSID, TCP keepalive, padding, and COOKIE options. Cookie parsing validates client/server cookie lengths, remote address binding, active or configured cookie secrets, renewal/expired/future status, and creates outgoing COOKIE options where needed. It also records all parsed incoming options in `opt_list_in`.

## Research Notes

The parser stores pointers into the packet buffer until later copy/decompression. Any caller must keep the buffer alive through `parse_create_msg()` or equivalent conversion. Security-sensitive behavior centers on bounds checks, RRSIG grouping, EDNS option length handling, and DNS COOKIE validation state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.h

## Role

`msgparse.h` defines the temporary DNS packet parsing structures, EDNS data structures, TTL policy globals/macros, compression-pointer helpers, and parser APIs used by `msgparse.c`, `msgreply.c`, and `msgencode.c`.

## Core Structures

`struct msg_parse` stores DNS header fields, section counts, query metadata, a fixed-size parse hashtable, and an ordered list of parsed RRsets.

`struct rrset_parse` represents one parsed RRset during packet parsing. It records hash, section, compressed owner-name pointer, decompressed owner length, type/class, flags, ordinary RR list, RRSIG list, and cumulative uncompressed RDATA size.

`struct rr_parse` represents one RR inside an RRset. Its `ttl_data` points at the TTL field in the packet, unless `outside_packet` marks generated data, and `size` records uncompressed RDATA storage size including the rdlength field.

`struct edns_data` stores OPT metadata: extended RCODE, EDNS version, Z/DO bits, UDP size, incoming options, outgoing options, outgoing in-place callback options, padding block size, and cookie state bits. `struct edns_option` is the linked-list representation for individual EDNS options.

## Constants and Macros

The header defines `PARSE_TABLE_SIZE`, `NORR_TTL`, compression-pointer macros `LABEL_IS_PTR`, `PTR_OFFSET`, `PTR_CREATE`, `PTR_MAX_OFFSET`, and `EDNS_RCODE_BADVERS`.

Global TTL policy variables include max/min TTLs, negative TTL bounds, serve-expired settings, serve-original-TTL behavior, and expired-reply TTL. Macros `PREFETCH_TTL_CALC`, `EXPIRED_REPLY_TTL_CALC`, `UPDATE_TTL_FROM_RRSET`, and `TTL_IS_EXPIRED` centralize TTL arithmetic and expiration tests.

## Public API

The header declares packet parsing (`parse_packet()`), EDNS extraction from parsed responses and query packets, RR skipping, RRset hashing and lookup, parse hashtable removal, EDNS option logging, and parsed-RR removal.

## Research Notes

The header documents the parser’s RRSIG reassociation model in detail. The structures intentionally point back into packet memory, so they are scratch objects rather than durable cache objects. Hash calculations must remain identical to `packed_rrset.c` for parser-to-cache consistency.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.c

## Role

`msgreply.c` converts parsed DNS packets into durable query/reply cache structures, manages reply TTLs and copying, supplies query/reply cache hash callbacks, logs replies, handles EDNS option lists, and dispatches in-place module callbacks.

## Parsing to Durable Reply Data

`parse_create_qinfo()` copies query names out of the packet. `construct_reply_info_base()` allocates a `reply_info` with packed trailing arrays for RRset references and RRset pointers. `reply_info_alloc_rrset_keys()` obtains per-RRset key objects from either a region or special allocator.

`parse_copy_decompress_rrset()` copies a parsed RRset into a `ub_packed_rrset_key`, decompressing owner names and RDATA. `parse_create_rrset()`, `parse_rr_copy()`, and `rdata_copy()` allocate and populate contiguous `packed_rrset_data`, apply TTL caps/floors, handle negative-SOA TTL rules, preserve upstream zero-TTL status, and decompress embedded RDATA names.

`parse_create_msg()` combines query creation, reply allocation, RRset-key allocation, and RR copy/decompression. `reply_info_parse()` is the top-level response parser: it parses the packet, extracts EDNS, creates cacheable data, and returns DNS RCODE-style errors.

## TTL, Cache, and Query Helpers

The file defines global TTL policy defaults such as `MAX_TTL`, `MIN_TTL`, `MAX_NEG_TTL`, `SERVE_EXPIRED_TTL`, and `SERVE_ORIGINAL_TTL`.

`reply_info_set_ttls()` converts relative TTLs to absolute cache times, while `reply_info_absolute_ttls()` forces all reply/RR TTLs to a given absolute value. `reply_info_can_answer_expired()` and `reply_info_could_use_expired()` decide whether expired cache entries can still answer or remain useful.

`query_info_parse()`, `query_info_compare()`, `query_info_hash()`, `query_info_entrysetup()`, `query_info_clear()`, `msgreply_sizefunc()`, `query_entry_delete()`, and `reply_info_delete()` implement query cache key parsing, ordering, hashing, ownership transfer, memory accounting, and cleanup.

`reply_info_copy()` and `repinfo_copy_rrsets()` deep-copy replies and RRsets, including DNSSEC bogus EDE reason strings. `make_new_reply_info()` builds a reduced answer-only reply using shallow-copied RRsets.

## Reply Inspection and Logging

`reply_find_final_cname_target()`, `reply_find_answer_rrset()`, `reply_find_rrset_section_an()`, `reply_find_rrset_section_ns()`, and `reply_find_rrset()` search answer or full reply data, following CNAME chains where appropriate.

`reply_check_cname_chain()` verifies cached CNAME/DNAME chain consistency. `reply_all_rrsets_secure()` checks whether all RRsets have secure validation status. `log_dns_msg()`, `log_reply_info()`, and `log_query_info()` provide wire-format or structured query/reply logging.

## EDNS Options and In-place Callbacks

`edns_opt_list_append()`, `edns_opt_list_append_ede()`, `edns_opt_list_append_keepalive()`, `edns_opt_list_remove()`, copy helpers, comparison helpers, free helpers, and `edns_opt_list_find()` manage region-allocated or malloc-allocated EDNS option lists.

`inplace_cb_reply_call_generic()` and the specific reply/cache/local/servfail wrappers call registered module callbacks after validating callback function pointers through `fptr_ok()`/`fptr_whitelist_*`. Query, EDNS-back-parsed, and query-response callback paths are similarly dispatched.

`local_alias_shallow_copy_qname()` exposes the current single-CNAME local alias assumption by returning the target name from the alias RR’s RDATA.

## Research Notes

This file bridges untrusted packet parsing and long-lived cache storage. Important invariants include decompressed RDATA storage, consistent TTL conversion, ownership transfer of query names into cache entries, RRset trust assignment by section and AA bit, and callback whitelist checks before indirect calls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.h

## Role

`msgreply.h` declares Unbound’s stored DNS query and reply data model plus helper APIs for parsing, copying, TTL handling, lookup, logging, EDNS option lists, and in-place callback dispatch.

## Data Model

`struct query_info` stores the cache-significant question: qname, qname length, qtype, qclass, and optional `local_alias`. The local alias comments document that the current implementation supports a single CNAME-style alias but callers must treat lifetime carefully.

`struct rrset_ref` stores a cached RRset key pointer and its id for lock-ordered validation.

`struct reply_info` stores response flags, authoritative bit, qdcount, reply TTLs, prefetch TTL, serve-expired TTLs, DNSSEC security status, cached EDE bogus reason, section RRset counts, an ordered RRset pointer array, and a trailing `rrset_ref` array used for locking/cache validation.

`struct msgreply_entry` combines a `query_info` cache key with an `lruhash_entry`.

## Public API

The header declares constructors and parsing functions: `construct_reply_info_base()`, `query_info_parse()`, `reply_info_parse()`, `parse_create_msg()`, `parse_reply_in_temp_region()`, `parse_copy_decompress_rrset()`, and `reply_info_alloc_rrset_keys()`.

Cache and lifetime helpers include `reply_info_sortref()`, TTL setters, parse deletion, query comparison/hash/clear, message size accounting, entry setup, reply copying, expired-answer checks, and reduced reply creation.

Search and validation helpers include CNAME target lookup, CNAME-chain checking, all-secure checking, and RRset lookup in answer, authority, or all sections.

Logging helpers expose packet-style and structured query/reply logging. EDNS helpers append, remove, find, copy, compare, and free option lists, including EDE and keepalive convenience functions.

Callback APIs cover reply, cache reply, local reply, SERVFAIL reply, outbound query, EDNS-back-parsed, and query-response callback lists. `local_alias_shallow_copy_qname()` exposes the current alias extraction helper.

## Research Notes

The header’s comments are important for ownership and concurrency: `query_info` names may point into buffers or be allocated; `reply_info` has packed trailing arrays; `rrset_ref` ordering matters for lock acquisition; and local alias data may point to configuration or ephemeral regional memory.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/msgreply.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.c

## Role

`packed_rrset.c` implements memory management, hashing, comparison, copying, TTL adjustment, target extraction, logging, and lookup helpers for Unbound’s packed RRset representation.

## Key Behavior

`ub_packed_rrset_parsedelete()`, `ub_rrset_key_delete()`, and `rrset_data_delete()` clean up RRset key/data objects and return special keys to the allocator. `ub_rrset_sizefunc()` and `packed_rrset_sizeof()` report memory usage for cache accounting.

`ub_rrset_compare()` orders RRset keys by type, owner-name length/name, class, and flags. `rrset_key_hash()` hashes owner name, host-order type, network-order class, and flags; comments require it to match parser hashing in `msgparse.c`. `rrsetdata_equal()` compares raw RDATA/RRSIG contents while ignoring trust and TTL metadata.

`packed_rrset_ptr_fixup()` repairs internal array pointers after copying a contiguous `packed_rrset_data` blob. `packed_rrset_ttl_add()` adds an absolute-time offset to RRset and per-RR TTLs.

`get_cname_target()` extracts a CNAME or DNAME target from the first RR’s RDATA after validating rdlength and dname format. `ub_packed_rrset_ttl()` returns the RRset TTL.

## Copying and Diagnostics

`packed_rrset_copy_region()` copies an RRset into a regional allocator and optionally converts absolute TTLs back to relative TTLs, including serve-expired calculations and the NS special case for ghost-attack mitigation. `packed_rrset_copy_alloc()` malloc/special-allocates a copy and converts relative TTLs to absolute by adding `now`.

`rrset_trust_to_string()` and `sec_status_to_string()` stringify trust/security enums. `packed_rr_to_string()` reconstructs a single RR wire image and formats it with `sldns_wire2str_rr_buf()`. `log_rrset_key()` and `log_packed_rrset()` log keys and all RR/RRSIG data.

`packed_rrset_find_rr()` searches ordinary data RRs by raw RDATA bytes and length.

## Research Notes

The packed data layout relies on contiguous allocation followed by pointer fixup after `memdup` or regional copy. Hash compatibility with `msgparse.c` is a cross-file invariant, and TTL conversion differs depending on whether the copy is for cache storage or response assembly.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.h

## Role

`packed_rrset.h` defines Unbound’s cacheable RRset key/data structures, RRset flags, trust/security enums, and utility APIs for packed RRset lifecycle and inspection.

## Structures and Flags

`rrset_id_type` is a 64-bit unique RRset id. Flags distinguish NSEC-at-apex, parent-side glue, negative-SOA copies, fixed TTL data, RPZ synthetic data, unverified glue, and upstream zero-TTL RRsets. `RR_COUNT_MAX` bounds RR/RRset counts for overflow protection.

`struct packed_rrset_key` contains owner dname, dname length, flags, network-order type, and network-order class. `struct ub_packed_rrset_key` wraps that key with an `lruhash_entry` and id for cache use.

`enum rrset_trust` ranks data trust from none through additional/authority/answer variants, glue, primary/zone-transfer data, DNSSEC validated data, and ultimate trust. `enum sec_status` records validation state from unchecked through bogus, indeterminate, insecure, sentinel fail, and secure.

`struct packed_rrset_data` stores TTL metadata, RR/RRSIG counts, trust/security state, and arrays for RDATA length, per-RR TTL, and RDATA pointers. Its memory layout is designed for one contiguous cache allocation: base struct, arrays, then uncompressed wire-format RDATA blobs.

## API Surface

The header declares parse cleanup, memory sizing, TTL access, cache compare/delete callbacks, data equality, hash calculation, pointer fixup, TTL add, CNAME/DNAME target extraction, enum stringification, logging, RR-to-string conversion, regional and allocator copies, and raw RDATA lookup.

## Research Notes

The key/data split supports cache replacement and locking. Callers must know that RDATA begins with a network-order rdlength field, RRSIGs are stored after ordinary RRs, and copied contiguous blobs require `packed_rrset_ptr_fixup()` before use.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/data/packed_rrset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.c

## Role

`edns.c` implements base EDNS utility support outside the packet parser/encoder: configured EDNS client-string lookup data and RFC9018 DNS COOKIE creation, validation, and secret rotation.

## EDNS Client Strings

`edns_strings_create()` and `edns_strings_delete()` allocate and free an `edns_strings` container with a regional allocator. `edns_strings_apply_cfg()` rebuilds the address-prefix tree from configuration entries, parsing netblocks and inserting configured strings with `edns_strings_client_insert()`.

`edns_string_addr_lookup()` looks up the best address-tree match for a client address. `edns_strings_get_mem()` reports memory use. `edns_strings_swap_tree()` swaps a live structure with prepared data, allowing config reload-style replacement.

## DNS COOKIE Handling

`edns_cookie_server_hash()` computes the RFC9018 server-cookie SipHash over client cookie, version/reserved/timestamp, and client IP. `edns_cookie_server_write()` writes version 1 cookie metadata, timestamp, and the 8-byte server hash into a 24-byte cookie output.

`edns_cookie_server_validate()` accepts only 24-byte version-1 server cookies with a 16-byte secret, checks timestamp freshness using RFC1982 serial arithmetic, rejects expired/future/invalid hashes, and returns renewal status for valid cookies older than 30 minutes.

## Cookie Secret Management

`cookie_secrets_create()` allocates a locked secret history structure and marks protected fields. `cookie_secrets_delete()` destroys the lock, zeroes secrets with `explicit_bzero()`, and frees memory.

`cookie_secret_file_read()` reads up to `UNBOUND_COOKIE_HISTORY_SIZE` hex-encoded 16-byte secrets from a configured file, treats one file-open error case as non-fatal, and rejects malformed lines. `cookie_secrets_apply_cfg()` wraps this for config application.

`cookie_secrets_server_validate()` validates a cookie against active and staging secrets under lock, returning renewal for staging-secret matches. `add_cookie_secret()`, `activate_cookie_secret()`, and `drop_cookie_secret()` manage active/staging secret lifecycle and zero temporary or removed secret material.

## Research Notes

This file contains security-sensitive time and secret handling. Important invariants are the 16-byte secret size, 24-byte interoperable cookie format, IPv4 versus IPv6 hash input length, lock coverage around shared secrets, and zeroing secrets after use or removal.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.h

## Role

`edns.h` declares EDNS client-string storage and DNS COOKIE secret/hash APIs used by the parser, config, and resolver runtime.

## Data Structures

`struct edns_strings` contains an address-prefix `rbtree_type`, the EDNS client-string option code, and a regional allocator. `struct edns_string_addr` embeds `addr_tree_node` first for tree use and stores the configured string plus length.

`UNBOUND_COOKIE_HISTORY_SIZE` is `2`, and `UNBOUND_COOKIE_SECRET_SIZE` is `16`. `struct cookie_secret` stores one secret, while `struct cookie_secrets` wraps the active/staging secret array with a basic lock and count.

`enum edns_cookie_val_status` reports cookie validation states: client-only, future, expired, invalid, valid, and valid-needs-renewal.

## Public API

The header declares EDNS string creation/deletion, config application, address lookup, memory accounting, and tree swapping.

The DNS COOKIE API includes server-cookie hash generation, cookie writing, single-secret validation, cookie-secret allocation/deletion, config/file loading, multi-secret validation, adding a staging secret, activating a staging secret, and dropping a staging secret.

## Research Notes

The comments document RFC9018 input layout for cookie hashing and writing. Callers of secret mutation functions are expected to hold the lock, while validation functions perform their own locking around the shared secret list.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.c

## Role

`fptr_wlist.c` implements function-pointer whitelist checks for Unbound. Each exported `fptr_whitelist_*` function verifies that an indirect callback pointer equals one of the known legitimate functions for that callback category.

## Whitelist Categories

The file covers communication callbacks, raw communication callbacks, timers, signals, accept start/stop hooks, libevent-style event callbacks, pending UDP/TCP callbacks, serviced-query callbacks, rbtree comparators, lruhash size/compare/delete/mark-delete callbacks, module environment callbacks, module lifecycle callbacks, alloc cleanup, tube listeners, mesh callbacks, print/collation callbacks, in-place reply/query/EDNS/query-response callbacks, and serve-expired lookup callbacks.

The allowed functions span core Unbound modules and optional build features: worker/libworker, outside network, mesh, iterator, validator, DNS64, response-IP, auth zones, local zones, infra/rrset/key/rate caches, remote control, Windows service hooks, Python module, dynamic library module, cachedb, ipsecmod, ECS/subnet, ipset, dnstap, and DNS-over-QUIC support where enabled.

## Security and Build Configuration

Most whitelist functions are straightforward pointer equality chains. Optional module callbacks are guarded by compile-time feature macros such as `WITH_PYTHONMODULE`, `WITH_DYNLIBMODULE`, `USE_CACHEDB`, `USE_IPSECMOD`, `CLIENT_SUBNET`, `USE_IPSET`, `USE_DNSTAP`, `HAVE_NGTCP2`, and `UB_ON_WINDOWS`.

For exported-all-symbols or disabled-feature cases, unused parameters are explicitly cast to void. The file intentionally violates normal modular boundaries because its purpose is to centralize every allowed indirect-call target.

## Research Notes

This is a control-flow hardening file. Any new callback target introduced elsewhere in the resolver must be added to the correct whitelist or `fptr_ok()` checks will reject it. Conversely, overly broad additions here weaken the indirect-call integrity model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.c -->