# Group Research: group_1383_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_itera_2f5af6e82b67

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.c

`iter_hints.c` implements Unbound iterator root/stub hint storage. It owns creation/destruction of `struct iter_hints`, a locked `name_tree` keyed by zone name and class, with `struct iter_hints_stub` values that wrap a `delegpt` plus the stub priming mode.

Configuration loading is handled by `hints_apply_cfg()`: it clears the existing tree under a write lock, reads configured root-hints files, reads configured stub zones, and falls back to compiled-in root server hints when no IN root hint exists. Compiled-in hints cover the root server IPv4/IPv6 addresses according to `cfg->do_ip4` and `cfg->do_ip6`.

Root-hints parsing uses `sldns_fp2wire_rr_buf()` and accepts NS/A/AAAA records, creating a delegation point with parent-side NS state. Stub parsing handles stub zone names, `stub-host` names, direct stub addresses, TLS auth names when supported, `stub-first`/prime behavior, `no_cache`, `ssl_upstream`, and `tcp_upstream`.

Lookup/update APIs include `hints_find()`, `hints_find_root()`, `hints_lookup_stub()`, `hints_next_root()`, `hints_add_stub()`, `hints_delete_stub()`, `hints_swap_tree()`, and `hints_get_mem()`. Several lookup functions intentionally leave the read lock held on successful returns unless `nolock` is set, matching the header’s caller-unlock contract.

Notable behavior: duplicate hint insertion logs and ignores the second hint while returning success; external add/delete rebuilds parent pointers with `name_tree_init_parents()`. The file is tightly coupled to iterator delegation-point management, config parsing, dname utilities, and root/stub resolution policy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.h

`iter_hints.h` declares the iterator hint subsystem API. `struct iter_hints` contains an RW lock and a `name_tree` of hint entries sorted by class and DNS name so closest-enclosing ancestor lookups work for root and stub hints.

`struct iter_hints_stub` stores the tree node, owned `delegpt`, and `noprime` flag. The public API covers create/delete, config application, root and closest hint lookup, stub priming lookup, memory accounting, externally adding/removing stubs, root-class iteration, and tree swapping.

The header documents the locking contract carefully: callers may pass `nolock` when they already hold the lock, while successful non-`nolock` lookups may require the caller to release the read lock.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.c

`iter_priv.c` implements iterator filtering for configured private addresses and private domains. `priv_create()` allocates a regional allocator plus an address tree for blocked netblocks and a name tree for domains allowed to contain those private addresses.

`priv_apply_cfg()` clears the regional allocator, reloads `private-address` entries with `netblockstrtoaddr()`, reloads `private-domain` names with `sldns_str2wire_dname()`, and initializes parent pointers for efficient lookup. Duplicate address/domain entries are ignored with verbose logging.

The main enforcement path is `priv_rrset_bad()`. Public-name A and AAAA RRsets are scanned for configured private addresses; bad individual RRs are removed when possible via `msgparse_rrset_remove_rr()`, and the whole RRset is removed when all RRs are gone. Owner names under configured private domains are exempt.

The file also handles SVCB/HTTPS privacy filtering by parsing `ipv4hint` and `ipv6hint` svcparams from the RDATA. Hints containing private addresses are treated the same as A/AAAA private-address leakage. Malformed SVCB/HTTPS data is generally tolerated unless a private address can be found inside the remaining bytes.

This subsystem is used by iterator scrubbing to prevent public DNS answers from returning RFC1918/private or otherwise configured internal addresses unless the name is explicitly whitelisted as private.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.h

`iter_priv.h` declares the iterator private-address filtering state and API. `struct iter_priv` owns a regional allocator, an address tree for blocked address spans, and a name tree for private-domain exceptions.

The exported functions create/delete the structure, apply config, test and sanitize RRsets, and report memory use. `priv_rrset_bad()` is the key runtime entry point: it may mutate a parsed RRset by removing individual bad RRs and returns whether the entire RRset should be dropped.

The header is intentionally narrow and hides the address/name lookup helpers inside `iter_priv.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.c

`iter_resptype.c` classifies DNS responses for the iterator. `response_type_from_cache()` handles cached messages and only distinguishes terminal answers from CNAME-continuation responses, assuming cached throwaway/lame/referral cases are not delivered through this path.

`response_type_from_server()` classifies wire responses as answer, referral, CNAME, throwaway, lame, or recursion-lame. It drops TC responses, treats most non-NOERROR/NXDOMAIN rcodes as throwaway, follows relevant CNAMEs, detects ANY/NS answer-section referrals, and uses authority-section SOA/NS relationships against the queried delegation point to distinguish NODATA, referrals, and lameness.

Recursive-lame detection is based on RA without AA when the iterator did not send RD. Empty NOERROR/NODATA messages are retried a limited number of times through `empty_nodata_found` before being accepted as answers.

The file is central to iterator state transitions after receiving a server response, especially deciding whether to cache, chase a CNAME, follow a referral, mark a server lame, or try another target.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.h

`iter_resptype.h` defines `enum response_type` for iterator response interpretation: untyped, answer, referral, CNAME, throwaway, lame, and recursion-lame.

It declares the two classifiers: `response_type_from_cache()` for cached messages and `response_type_from_server()` for wire responses. The server classifier takes the sent-RD state, request, active delegation point, and empty-NODATA retry counter.

This header is the contract between response parsing/scrubbing and the iterator control flow that decides the next resolution step.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.c

`iter_scrub.c` cleans parsed DNS replies before the iterator classifies and caches them. The public entry point `scrub_message()` verifies the QR bit and echoed question, clears AD/Z bits, then runs normalization followed by sanitization.

Normalization removes irrelevant answer data, enforces ordered CNAME chains, synthesizes CNAMEs from valid DNAME answers, limits excessive CNAME/DNAME chains, shortens oversized NS and RRSIG lists according to config, and marks justified A/AAAA additional-section glue. Authority-section CNAME/DNAME/A/AAAA records are stripped, unknown authority/additional types can be stripped under hardening, and promiscuous NS sets are removed in several answer/NODATA/NXDOMAIN cases.

Sanitization then removes extraneous answer RRsets, deletes out-of-zone data as potential poison, applies private-address filtering through `priv_rrset_bad()`, checks A/AAAA RR lengths and records EDE info for bad lengths, rejects overreaching NSEC records whose next-domain target leaves the server zone, and optionally stores certain potential poison or unverified glue into cache when hardening settings allow it.

Additional-section policy is conservative: A/AAAA glue is kept only if normalization marked it as directly referenced by relevant NS/MX/SRV-like data; if a referencing RRset is later removed, additional glue is removed as suspect. Hardened unverified-glue mode stores non-strict-subdomain glue separately with `PACKED_RRSET_UNVERIFIED_GLUE` and removes it from the response.

Special cases include transforming an authority-section DS RRset into the answer section for DS queries, retaining enough upward NS data to allow lame classification, and applying DNAME/CNAME TTL policy consistently when synthesizing a CNAME.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.h

`iter_scrub.h` declares the DNS message scrubbing entry point `scrub_message()`. The function takes the original packet buffer, parsed message, original query, active delegation/zone name, regional allocator, module environment, query state for EDE error information, and iterator environment.

The API promises to mutate the parsed message by removing useless or malicious data while leaving the packet buffer unchanged. It returns false when the message is unusable.

This header exposes only the high-level scrubber; all normalization, glue marking, DNAME/CNAME synthesis, and poison filtering helpers remain private to `iter_scrub.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.c

`iter_utils.c` is the iterator’s shared utility implementation. It parses target-fetch policy, builds caps-for-ID whitelist trees, applies NAT64 config, wires do-not-query/private-address state, and copies core iterator config into `iter_env`.

Server selection is a major part of the file. `iter_filter_unsuitable()` rejects bogus, do-not-query, unsupported address-family, lame, or unresponsive targets; applies NAT64 synthesis for IPv4 targets when enabled; reads infra-cache RTT/lame state; and assigns penalty-weighted selection RTTs for parent-side lame, DNSSEC-lame, recursion-lame, and blacklisted servers. `iter_filter_order()` groups fast-enough targets, honors fast-server sampling and IPv4/IPv6 preference settings, and `iter_server_selection()` randomly chooses among the best candidates while tracking retry attempts.

The file also provides DNS message allocation/copy/store helpers, random probability selection for NS ordering, dependency-cycle detection for target address lookups, delegation-usefulness checks, and DNSSEC heuristics based on trust anchors, DS records, key-cache entries, and RRSIG presence.

Cache support includes storing parent-side NS/glue and negative parent-side entries, looking them back up to help last-resort resolution, and finding the next configured root class across hints and forwards atomically. Reply comparison for fallback sorts authority/additional rrsets canonically while preserving answer order.

Scrubbing-related helpers remove irrelevant DS records from referrals, strip NXDOMAIN answer sections for subdomain use, limit NSEC/NSEC3 TTLs to SOA TTL per RFC9077, and make replies minimal by removing authority/additional sections. Retry helpers decrement or merge address attempt counters across delegation-point refreshes.

Other notable APIs include `iter_stub_fwd_no_cache()` for finding closest stub/forward `no_cache` policy and returning the governing delegation name, plus `iterator_set_ip46_support()` for disabling iterator IPv4/IPv6 support based on available outbound interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.h

`iter_utils.h` declares the broad helper surface used by the Unbound iterator module. It includes constants limiting cache lookups for nameserver address fetching and parent-side glue fetching.

The API covers config application, target server selection, DNS message allocation/copy/cache storage, NS random probability, dependency-cycle marking, delegation usefulness checks, DNSSEC expectation and message-origin heuristics, reply equality, caps-for-ID fallback cleanup, parent-side cache storage/lookup, root-class iteration across hints/forwards, DS/NXDOMAIN scrubbing, retry accounting, stub/forward no-cache lookup, runtime IP-family support, fetch-policy parsing, caps whitelist management, NAT64 config, NSEC TTL limiting, and minimal-response conversion.

Because this header is included by iterator control code and related modules, changes to it affect selection, caching, DNSSEC decision-making, hardening behavior, and fallback mechanics across the resolver.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.h -->