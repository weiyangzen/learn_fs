# Group Research: group_1384_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_itera_5f1ad7fa6768

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.c

`iterator.c` implements Unbound's recursive iterative resolver module. It registers the `iterator` module function block and drives the resolver state machine from initial cache/config lookup through authoritative target selection, response classification, CNAME/DNAME chasing, referrals, priming, and final response construction.

The main state paths are `processInitRequest()`, `processInitRequest2()`, `processInitRequest3()`, `processQueryTargets()`, `processQueryResponse()`, `processPrimeResponse()`, `processCollectClass()`, `processDSNSFind()`, and `processFinished()`, orchestrated by `iter_handle()` and entered through `iter_operate()`. Per-query state is allocated in `iter_new()` and cleaned in `iter_clear()`.

Initial resolution checks local/RPZ/auth-zone data, positive and negative caches, no-cache stub/forward policy, forwarding zones, cached delegations, auth-zone delegations, stub priming, and root priming. It handles non-recursive referral returns, qclass `ANY` by spawning per-class subqueries, and DS-query edge cases by searching for the correct parent-side NS point.

Target handling builds and updates delegation points, fetches missing A/AAAA nameserver addresses with subqueries, enforces dependency depth and target/query quotas, performs parent-side glue fallback, NXNS-style fallback, root safety-belt fallback, and optional hardened referral-path checks. Server selection respects IPv4/IPv6/NAT64 availability, do-not-query/private policy via helpers, infra-cache state, blacklists, TCP/TLS upstream flags, ratelimits, retry counts, and target-fetch policy.

Response handling parses packets, extracts EDNS options, scrubs/sanitizes responses, classifies them as answer/referral/CNAME/lame/recursive-lame/throwaway, stores useful data in message/rrset/negative/parent-side caches, marks lame or DNSSEC-lame servers, follows CNAME/DNAME chains, validates referral shape, prefetches DNSKEYs, and finalizes answer flags. It also implements qname minimisation, 0x20/caps-for-ID fallback, DNSSEC expected-data checks, serve-expired DNSKEY minimization, and EDE/error-info propagation.

Important safety controls include maximum query restarts, dependency depth, referrals, upstream sends, target lookups, per-delegation target lookups, NXDOMAIN nameserver lookups, and global upstream-query quota. Memory ownership is mostly regional for per-query data, with shared `target_count`/`nxns_dp` reference-counted manually across subqueries.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.h

`iterator.h` declares the iterator module's public internal API, resolver limits, global iterator environment, per-query iterator state, qname-minimisation states, resolver states, and prepend-list structure.

`struct iter_env` stores process-wide iterator settings: IPv4/IPv6 availability, NAT64 prefix state, do-not-query and private-address/domain structures, caps-for-ID whitelist, dependency depth, target-fetch policy, ratelimit counter/lock, outbound retry count, send cap, and CNAME restart cap.

`struct iter_qstate` is the core per-query state record. It tracks the current/final iterator state, recursion depth, active response, answer/authority prepend lists, chased query name, outgoing query info, current delegation point, outstanding target/direct query counters, restart/referral/send counts, shared target counters, NXNS fallback marker, parent-side glue state, DS parent search state, DNSSEC expectation/lame flags, priming/refetch flags, qname minimisation state, auth-zone fallback flags, parse/scrub failure counters, and last failing upstream address.

The header exports the module hook functions: `iter_get_funcblock()`, `iter_init()`, `iter_deinit()`, `iter_operate()`, `iter_inform_super()`, `iter_clear()`, `iter_get_mem()`, plus state helpers. Changes here affect the iterator implementation and any module-stack code that creates, clears, or introspects iterator state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/Makefile.inc

This OpenBSD make include adds `${.CURDIR}/libunbound/libunbound` to `.PATH` and appends `context.c`, `libunbound.c`, and `libworker.c` to `SRCS`.

It is the local build glue that brings the libunbound context/API/worker implementation into the `unwind`-vendored libunbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.c

`context.c` implements internal libunbound context setup, outstanding-query bookkeeping, allocator-cache reuse, and pipe-message serialization/deserialization for background asynchronous resolution.

`context_finalize()` applies runtime configuration, initializes module startup/init, creates local zones, applies local/auth-zone/forward/hint/EDNS-string configuration, sizes message/rrset/infra caches, sets logging, and marks the context finalized. After this point many public configuration calls reject changes with `UB_AFTERFINAL`.

The query registry uses an rbtree keyed by integer query IDs. `context_new()` allocates `ctx_query`, assigns an unused ID, creates the user-facing `ub_result`, records callback metadata, and inserts the query. `context_query_delete()` frees query result/message storage. `find_id()` retries query-ID allocation up to `NUM_ID_TRIES`.

The serialization protocol supports `UB_LIBCMD_NEWQUERY`, `UB_LIBCMD_CANCEL`, `UB_LIBCMD_ANSWER`, and `UB_LIBCMD_QUIT`. Messages encode fixed-width command/query/type/class/error/security fields followed by query names, optional bogus-reason strings, and raw DNS answer packets. Deserializers validate minimum lengths and look up existing queries before attaching results or cancellations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.h

`context.h` defines libunbound's internal `ub_ctx` and `ctx_query` structures plus the private pipe command protocol used between API callers and background workers.

`struct ub_ctx` owns async query/result tubes and locks, configuration/finalization state, background process/thread identity, allocator-cache freelist, shared module environment, module stack, local zones, random seed state, optional event-base integration, outstanding-query rbtree, and async query count.

`struct ctx_query` represents one outstanding synchronous, asynchronous, or event-based lookup. It stores the query number, cancellation state, callback pointers, callback argument, raw answer packet, validation security status, handling worker, and allocated `ub_result`.

The header declares context finalization, query allocation/deletion/comparison, alloc-cache obtain/release, and serialization/deserialization helpers for new-query, answer, cancel, quit, and command probing. It couples libunbound's public API layer to the worker/tube protocol and module environment internals.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libunbound.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libunbound.c

`libunbound.c` implements the public libunbound API: context creation/deletion, configuration, synchronous resolution, asynchronous resolution, event-based resolution, cancellation, result freeing, error strings, local-zone/data mutation, and version reporting.

Context creation initializes logging, optional Winsock, allocator state, random seed state, locks, module environment, default library config, EDNS known-options/string state, auth zones, module stack, and query rbtree. `ub_ctx_create()` additionally creates query/result pipes; `ub_ctx_create_ub_event()` and `ub_ctx_create_event()` create contexts for caller-owned event loops.

Context deletion handles background worker shutdown, fork/thread edge cases, pipe cleanup, event worker cleanup, module deinit/destartup, cached allocators, local zones, locks, tubes, caches, config, forwards, hints, auth zones, random state, outstanding queries, logfile override state, and Winsock cleanup.

Configuration APIs mutate the pre-finalized config under `cfglock`: generic options, config files, trust anchors, trusted-keys files, debug level/output, async threading mode, forwarders, TLS forwarding, stub zones, `/etc/resolv.conf` import, and hosts-file import. Most return `UB_AFTERFINAL` once resolution has finalized the context.

Resolution paths are split across `ub_resolve()` for foreground synchronous work, `ub_resolve_async()` for pipe-driven background worker requests, and `ub_resolve_event()` for event-loop integration. Async results are read with `ub_process()` or `ub_wait()`, decoded by `process_answer_detail()`, converted into `ub_result`, and delivered with callbacks outside locks. `ub_cancel()` marks threaded/event queries cancelled or sends cancel messages to forked workers.

Local-zone APIs finalize the context if needed, then print zones, add/remove zones, and add/remove local RR data. `ub_resolve_free()` releases every allocation owned by a `ub_result`; `ub_strerror()` maps library error codes; `ub_version()` returns `PACKAGE_VERSION`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libunbound.c -->