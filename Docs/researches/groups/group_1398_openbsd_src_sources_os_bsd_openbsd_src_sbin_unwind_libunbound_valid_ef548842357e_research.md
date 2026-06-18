# Group Research: group_1398_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_valid_ef548842357e

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.h

`val_utils.h` declares the shared helper API for unwind's embedded libunbound DNSSEC validator. It defines `enum val_classification`, which is the validator's response-shape taxonomy: positive answers, CNAME/DNAME chains, NODATA, NXDOMAIN, CNAME-with-no-final-answer, referrals, ANY answers, and unknown/untyped cases.

The header exposes the major validation utilities used by `validator.c`: response classification, signer discovery, RRset signature validation, DNSKEY validation through DS or trust anchors, DS usability checks, wildcard detection, CNAME chasing, chased-reply extraction, authority RRset removal, nonsecure RRset cleanup, and marking unchecked RRsets indeterminate or insecure.

It also declares chain-of-trust support helpers: `val_find_DS()` can synthesize a DS denial message from caches, `val_blacklist()` carries forward bad upstream/origin avoidance, `val_has_signed_nsecs()` verifies that negative proofs are present, and `val_favorite_ds_algo()` chooses a supported DS algorithm.

Important coupling: this header bridges the validator core to packed RRsets, reply/query structures, trust anchors, key entries, regional allocation, rrset cache, NSEC/NSEC3 proof helpers, and EDE bogus reason reporting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.c

`validator.c` implements the libunbound DNSSEC validator module used by `unwind`. It owns validator initialization, trust-anchor/key-cache/negative-cache setup, per-query validation state, chain-of-trust walking, DS/DNSKEY subquery handling, answer proof validation, retry/blacklist behavior, and final cache insertion.

The main state machine is `VAL_INIT_STATE -> VAL_FINDKEY_STATE -> VAL_VALIDATE_STATE -> VAL_FINISHED_STATE`, driven by `val_operate()` and `val_handle()`. `processInit()` classifies the response, finds the signer and nearest trust anchor or cached key, primes trust anchors when necessary, and handles insecure/null/bad key entries. `processFindKey()` walks down the DNS tree by issuing DS and DNSKEY subqueries or by using cached DS denial data. `processValidate()` verifies RRset signatures and dispatches to response-type proof validators. `processFinished()` aggregates security status, handles CNAME/referral continuation, stores negative proofs, retries bogus answers with blacklisting, applies bogus TTL/permissive mode/root-key-sentinel behavior, and caches the final result.

Response-type validators cover positive answers, NODATA, NXDOMAIN, referrals, ANY, CNAME/DNAME, and CNAME chains ending without an answer. They require validated answer/authority RRsets first, then prove wildcard applicability or denial with NSEC/NSEC3 as appropriate. DNAME-generated unsigned CNAMEs are accepted only when their target matches RFC 6672 derivation; wildcarded DNAMEs are rejected for ordinary CNAME validation.

Chain-of-trust handling is concentrated in `primeResponseToKE()`, `ds_response_to_ke()`, `process_ds_response()`, `process_dnskey_response()`, and `process_prime_response()`. DS answers must validate and contain usable algorithms; DS NODATA/NXDOMAIN must be proven with signed NSEC/NSEC3; DNSKEY answers must match DS material unless the chain reaches a null/insecure point. Bogus DS/DNSKEY paths can blacklist origins and retry until `val_max_restart` is exhausted.

Resource-control details are significant. `validate_msg_signatures()` limits synchronous RRSIG verification with `MAX_VALIDATE_AT_ONCE`, and NSEC3 proof paths can suspend and resume through `validate_suspend_setup_timer()` with a maximum suspend count. This keeps expensive DNSSEC work from monopolizing the event loop.

Security-relevant behavior includes EDE reason preservation, strict signer/name relationship checks, special handling for stripped DNSSEC depending on `harden_dnssec_stripped`, optional `serve_expired` fallback for previously valid cached answers, additional-section cleanup, RPZ-applied answers marked insecure, and root-key-sentinel result adjustment. The module function block exported by `val_get_funcblock()` registers this file as the `"validator"` module.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.h

`validator.h` declares the public interface and state structures for the embedded libunbound DNSSEC validator module. It defines TTL constants for null and bogus key entries plus root-key-sentinel label constants.

`struct val_env` is global validator state: key cache, aggressive negative cache, validation date/skew settings, restart limit, bogus TTL, NSEC3 iteration limits, and a protected bogus-RRset counter. `struct val_qstate` is per-query state: original/chased messages, restart and blacklist state, chased qname, trust-anchor and DS state, current key entry, response classification/signer data, trust-anchor priming flag, signature-suspension cursor, NSEC3 cache table, suspended DS message, and resume timer.

The exported API provides module lifecycle and operation hooks (`val_init()`, `val_deinit()`, `val_operate()`, `val_inform_super()`, `val_clear()`, `val_get_mem()`), state string conversion, suspend timer callback, NSEC3 iteration config parsing, and validator environment config application. It is the header consumed by the resolver and module framework to embed the validator.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/log.c

`log.c` implements unwind's local logging wrapper. `uw_log_init()` records debug/verbose mode, initializes the process name, opens syslog when not debugging, and calls `tzset()`.

The normal logging path is `logit()`/`vlog()`: in debug mode messages are printed to stderr with a trailing newline, otherwise they go to syslog. `uw_log_warn()` preserves `errno`, appends `strerror(errno)` to the caller's message, and falls back cleanly if `asprintf()` fails. `log_warnx()`, `uw_log_info()`, and `log_debug()` provide error-free, info, and verbosity-gated debug wrappers.

Fatal paths use `vfatalc()` to format `"fatal in <proc>"` messages with or without an errno code, then `fatal()` and `fatalx()` exit with status 1. Global state is limited to debug/verbose flags and the current process name.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/log.h

`log.h` declares unwind's logging API and maps the generic names `log_init`, `log_warn`, and `log_info` to unwind-prefixed implementations to avoid conflicts with libunbound's logging symbols.

It exposes debug/verbose getters and setters, process-name initialization, warn/info/debug/logit/vlog functions, and `__dead` fatal exits. The variadic functions carry printf-format attributes, making compile-time format checking available to callers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/parse.y

`parse.y` is the yacc grammar and lexer for `unwind.conf`. It parses includes, macros, resolver preference order, forwarders, DoT authentication names, block-list configuration, and forced resolver rules.

The grammar builds a `struct uw_conf` with defaults of DoT, oDoT forwarder, plain forwarder, recursor, oDoT autoconf, autoconf, and stub/ASR. `preference` entries are checked for uniqueness and enable their resolver types. `forwarder` entries require numeric IP addresses, validate ports, default to port 853 for DoT and 53 otherwise, and only allow `authentication name` with DoT. `block list` can be configured once, optionally with logging. `force [accept bogus] <resolver> { domains... }` normalizes domains to trailing dots, stores them in an RB tree, and enables the forced resolver type.

The lexer supports quoted strings, comments, line continuations, numeric tokens, keywords, and `$macro` expansion with START/DONE markers to prevent recursive expansion during insertion. Included files are managed as a stack with per-file line/error accounting. `parse_config()` accepts a missing default config as a valid empty config, frees nonpersistent macros after parsing, and discards the config on accumulated errors.

Safety details: `check_file_secrecy()` rejects secret files not owned by root/current user or writable by group/world-readable or writable by others; `host_ip()` uses `AI_NUMERICHOST`, so configured forwarders do not trigger name resolution; token buffers and destination fields are bounds-checked with explicit errors.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/printconf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/printconf.c

`printconf.c` serializes an in-memory `struct uw_conf` back into unwind configuration syntax. `print_config()` prints resolver preference order, plain and DoT forwarders, block-list settings, and force rules.

Plain forwarders omit `port 53`; DoT forwarders omit `port 853`, print an authentication name when present, and append `DoT`. Force rules are grouped by resolver type and emitted separately for normal and `accept bogus` entries by scanning the force RB tree for each resolver type.

This file is presentation-only: it does not validate or mutate configuration, but it depends on `uw_resolver_type_str`, forwarder TAILQs, and the force tree layout from `unwind.h`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/printconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/resolver.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/resolver.c

`resolver.c` implements unwind's resolver subprocess. It runs after privilege drop and pledge/unveil, owns the libevent loop, receives queries and controls over imsg, maintains resolver instances for configured resolver types, dispatches queries across preferred resolvers, tracks latency/state, refreshes trust anchors, manages autoconf forwarders, detects DNS64, and reports status/memory telemetry.

Resolver instances are `struct uw_resolver`: each has either a libunbound context or ASR context, state (`DEAD`, `UNKNOWN`, `RESOLVING`, `VALIDATING`), check/free events, reference count, median latency, and histograms. `new_resolver()` creates only enabled and materially configured resolver types; validating libunbound resolvers require trust anchors. `create_resolver()` configures libunbound options, trust anchors, address-family availability, debug/syslog behavior, forwarders, TLS bundles, TLS mode, and transparent local zones for forwarding modes.

Query flow starts in `resolver_dispatch_frontend()` on `IMSG_QUERY`, then `setup_query()` creates a `running_query`, applies any `force` rule, sorts resolver preferences by state and latency, and calls `try_next_resolver()`. Multiple resolvers may be tried with timers based on median latency and a skew allowance for the preferred resolver. `resolve()` dispatches to either ASR or `ub_resolve_event()`. `resolve_done()` validates packet size, imports libunbound results, updates histograms, doubts fresh-network NXDOMAIN/BOGUS answers in favor of ASR when possible, marks bogus validating answers unless a force rule accepts bogus, chunks large answers across `IMSG_ANSWER`, and falls back to the next resolver or SERVFAIL.

Health checking uses `check_resolver()` to query root NS through a fresh resolver and `check_resolver_done()` to classify the resolver as validating, merely resolving, or dead. DNS64 presence downgrades autoconf validating resolvers to resolving because DNS64 breaks DNSSEC. Dead or time-bogus resolvers are rechecked with exponential backoff up to about 17 minutes.

Configuration and runtime updates arrive from main/frontend imsg handlers. Reconfiguration merges new config and restarts affected resolver types; network changes reset recent histograms and schedule rechecks; address-family changes restart libunbound resolvers; autoconf DNS proposals replace generated forwarder lists; trust-anchor updates restart validating resolvers. Reference counting defers freeing resolver contexts until callbacks have unwound to avoid use-after-free in libunbound event callbacks.

Operational support includes status/autoconf/memory replies, unified-cache setup under `UNIFIED_CACHE`, decaying latest latency histograms, force-domain lookup by longest suffix, generated ASR resolv.conf text, root trust-anchor refresh via DNSKEY lookup, and DNS64 prefix discovery from `ipv4only.arpa.` per RFC 7050/RFC 6052.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/resolver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/resolver.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/resolver.h

`resolver.h` declares control-facing resolver state and telemetry structures. `enum uw_resolver_state` orders states as dead, unknown, resolving, and validating, with string names used for status display.

The latency histogram bucket limits range from sub-10ms through 1000ms and an `INT64_MAX` catchall. `struct ctl_resolver_info` carries resolver state, type, median latency, lifetime histogram, and decayed recent histogram. `struct ctl_forwarder_info` reports autoconf forwarder IP, interface index, and source. `struct ctl_mem_info` reports cache usage and maximums for message, rrset, key, and negative caches.

The header exports the resolver process entry point and imsg compose helpers for sending messages to main and frontend processes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/resolver.h -->