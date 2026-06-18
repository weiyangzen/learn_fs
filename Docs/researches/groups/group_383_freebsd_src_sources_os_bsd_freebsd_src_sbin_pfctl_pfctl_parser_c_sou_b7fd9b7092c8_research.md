# Group Research: group_383_freebsd_src_sources_os_bsd_freebsd_src_sbin_pfctl_pfctl_parser_c_sou_b7fd9b7092c8

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.c

## Purpose
Core helper implementation for `pfctl` parsing, display, address expansion, interface lookup, and PF transaction buffer handling.

## Main Elements
- Defines ICMP/ICMPv6 type and code name tables and PF timeout name mappings.
- Pretty-printers for rules, ethernet rules, pools, status, source nodes, tables, state/source limiters, ports, uid/gid clauses, flags, labels, NAT/RDR/binat pools, scrub options, queue/tag options, route options, divert options, and expired rules.
- Host and interface expansion: `host()`, `host_ip()`, `host_if()`, `host_dns()`, `ifa_load()`, `ifa_lookup()`, group lookup, dynamic nodes, netmask handling, and address-list conversion.
- Interface-group cache using `hsearch_r()` initialized by constructor.
- PF table address append helpers and transaction helpers: `append_addr()`, `append_addr_host()`, `pfctl_add_trans()`, `pfctl_get_ticket()`, `pfctl_trans()`.

## Dependencies And Integration
Uses kernel PF structures from `<net/pfvar.h>`, interface ioctls, `getifaddrs()`, `getaddrinfo()`, libpfctl-facing structs, and declarations from `pfctl_parser.h`/`pfctl.h`. Other pfctl modules rely on this file for printable rule output and parser-time host/table expansion.

## Risk Notes
The code mixes user-visible formatting with kernel ABI fields. Address-family handling, interface-group lookup, netmask truncation, and list expansion are high-risk areas because parser output must match kernel expectations and regression `.ok` files exactly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.h

## Purpose
Shared public header for pfctl parser, optimizer, table, ALTQ, address, rule, and display helpers.

## Main Elements
- Defines option bits such as `PF_OPT_VERBOSE`, `PF_OPT_NOACTION`, `PF_OPT_NUMERIC`, `PF_OPT_NODNS`, and parser/load category flags.
- Declares `struct pfctl`, including device/libpfctl handles, anchor stacks, table transaction state, ethernet anchor state, limit trees, and `set` option state.
- Defines parser node structures for interfaces, hosts, MACs, OS fingerprints, queue bandwidth/service curves, table initializers, optimizer tables, and optimizer rule containers.
- Declares rule append, ALTQ, pool, limit, config, table, fingerprint, interface, host, and print helper APIs.
- Provides FreeBSD compatibility aliases mapping `SIMPLEQ_*` to `STAILQ_*`.

## Dependencies And Integration
Included across pfctl sources and test builds. It bridges parser-generated structures, libpfctl handles, PF kernel ABI structures, ALTQ queue structures, and radix/table buffer APIs.

## Risk Notes
This header is a broad coupling point. Struct layout and macro changes can break parser, optimizer, table loading, and display code simultaneously.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_qstats.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_qstats.c

## Purpose
Implements `pfctl` ALTQ queue statistics display and live rate sampling.

## Main Elements
- Maintains an in-memory tree of `pf_altq_node` entries with child queues and `queue_stats`.
- `pfctl_show_altq()` loads current ALTQ stats, prints queues, and optionally repeats every five seconds for verbose live output.
- `pfctl_update_qstats()` fetches queues and scheduler-specific stats through `DIOCGETALTQS`, `DIOCGETALTQ`, and `DIOCGETQSTATS`.
- Scheduler-specific printers cover CBQ, CoDel, PRIQ, HFSC, and FAIRQ counters.
- `update_avg()` computes smoothed packet/byte deltas for measured rates.

## Dependencies And Integration
Uses PF ioctls, ALTQ scheduler stat structures, and shared pfctl formatting helpers such as `print_altq()` and `rate2str()`.

## Risk Notes
Scheduler-specific union interpretation must match kernel-provided versions. Live average calculation depends on monotonic counter increases and fixed `STAT_INTERVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_qstats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_radix.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_radix.c

## Purpose
Implements PF table/radix compatibility wrappers, interface query wrappers, and generic pfr buffer management.

## Main Elements
- Generates RB tree support for `pfr_ktablehead`.
- Wraps libpfctl and ioctl table operations: add/delete/get tables, add/delete/set/get/test addresses, clear stats, inactive define.
- Reports oversized PF request errors using `net.pf.request_maxcount`.
- Exposes `pfi_get_ifaces()` for interface stats retrieval.
- Defines `pfr_buffer` element sizes and buffer add/next/grow/clear routines.
- Loads address tokens from files/stdin with comment and whitespace handling.

## Dependencies And Integration
Uses global `dev` and `pfh`, PF table ioctls, libpfctl table functions, and `append_addr()` from parser helpers.

## Risk Notes
The shared buffer code underpins table parsing and loading. Incorrect element type, growth, or token parsing would corrupt table operations or misread table files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_radix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_table.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_table.c

## Purpose
Implements pfctl table and interface commands: list, create, delete, flush, add, replace, expire, reset, show, test, zero, and interface display.

## Main Elements
- `pfctl_table()` dispatches table commands and manages `pfr_buffer` instances for addresses, stats, and tables.
- Creates persistent tables when needed and warns on duplicate table names in other anchors.
- Loads addresses from argv or files and prints feedback markers for add/delete/replace/test/zero operations.
- Prints table stats, address stats, DNS-resolved address output, and interface stats.
- `pfctl_define_table()` handles parse-time table definitions and inactive table loading.

## Dependencies And Integration
Uses wrappers from `pfctl_radix.c`, libpfctl table APIs, shared parser address expansion, `usage()`, and PF table/interface ABI structures.

## Risk Notes
`PF_OPT_NOACTION`, dummy action, recursion, and feedback flags alter behavior. Table commands are stateful kernel mutations, so error and cleanup paths matter.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_table.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/Makefile

## Purpose
Builds pfctl regression tests.

## Main Elements
- Declares C ATF test `pfctl_test` and shell ATF test `macro`.
- Adds `files` subdirectory for test input/output data.
- Links `pfctl_test` with `libsbuf`.
- Makes `pfctl_test.o` depend on `pfctl_test_list.inc`.

## Dependencies And Integration
Included by FreeBSD test build infrastructure via `bsd.test.mk`.

## Risk Notes
The generated test set depends on the included list file; missing dependency updates can leave stale test cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/Makefile

## Purpose
Installs pfctl regression input, expected-output, include, and failure files.

## Main Elements
- Sets `TESTSDIR` and `BINDIR` under `${TESTSBASE}/sbin/pfctl/files`.
- Uses globbed `FILES!=` expansion for `pf????.in`, `.include`, `.ok`, and `.fail`.
- Includes `bsd.progs.mk`.

## Dependencies And Integration
Provides data files consumed by `pfctl_test.c`.

## Risk Notes
Glob expansion is tied to `${.CURDIR}` and four-digit naming; irregular filenames will not install.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0001.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0001.in

## Purpose
Regression input for basic `pass` rules with labels.

## Main Elements
Covers `pass in all`, explicit `from any to any`, no-state, TCP source/destination port operators, negated destination, IGMP `allow-opts`, address-list expansion, and label macro interpolation.

## Risk Notes
Validates printed normalization for labels and port/address operators.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0001.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0002.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0002.in

## Purpose
Regression input for mixed block/pass policy rules.

## Main Elements
Exercises logged block rules, return-rst, return-icmp, quick blocks, private/broadcast/no-route sources, ICMP echo rules, UDP/TCP stateful pass rules, and service-name port parsing.

## Risk Notes
Covers canonicalization of log/quick/return combinations and service names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0002.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0003.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0003.in

## Purpose
Regression input for TCP flag handling.

## Main Elements
Includes block/pass rules with explicit flag masks, empty flag side, `flags any`, no-state, keep-state, and protocol-list expansion.

## Risk Notes
Validates `parse_flags()` and output of `flags` defaults.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0003.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0004.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0004.in

## Purpose
Regression input for block rule expansion.

## Main Elements
Covers protocol lists, source/destination CIDR lists, negated source, named ports, port ranges, relational port operators, and multi-dimensional rule expansion.

## Risk Notes
Stress-tests list expansion and port operator normalization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0004.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0005.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0005.in

## Purpose
Regression input for variables used in port/address lists.

## Main Elements
Defines string variables for ports and networks, then uses them inside UDP block rule source and destination port lists.

## Risk Notes
Checks variable substitution in mixed literal/service/hex port lists.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0005.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0006.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0006.in

## Purpose
Regression input for variable names.

## Main Elements
Defines simple macros `a`, `c`, and `a_b_c`.

## Risk Notes
Checks macro parser accepts underscores and adjacent names without accidental expansion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0006.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0007.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0007.in

## Purpose
Regression input for block/pass rules with state variants.

## Main Elements
Similar to `pf0002.in`, adding `modulate state` and `synproxy state` combinations for TCP/UDP/ICMP protocol lists and service-name ports.

## Risk Notes
Validates state-mode formatting and protocol-list expansion under stateful rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0007.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0008.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0008.in

## Purpose
Regression input for negated address list macro expansion.

## Main Elements
Defines `extern` as an address list containing negation and uses it in a logged block rule.

## Risk Notes
Checks negation survives macro/list expansion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0008.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0009.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0009.in

## Purpose
Regression input for interface-list macros.

## Main Elements
Defines an interface list and uses it in `block in on`.

## Risk Notes
Validates expansion of interface macros in `on` clauses.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0009.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0010.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0010.in

## Purpose
Regression input for return action variants.

## Main Elements
Covers IPv4/IPv6 ICMP pass/block, TCP `return-rst` with and without TTL, ICMP/ICMPv6 numeric and named return codes, and mixed-family `return-icmp` code pairs.

## Risk Notes
Exercises ICMP code lookup tables and formatting across address families.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0010.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0011.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0011.in

## Purpose
Regression input for ICMP and ICMPv6 type/code parsing.

## Main Elements
Tests numeric ICMP/ICMPv6 types and codes for pass/block rules plus named code combinations such as `unreach needfrag` and `timex reassemb`.

## Risk Notes
Validates type/code tables and protocol aliases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0011.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0012.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0012.in

## Purpose
Regression input for subnet masks and negated hosts.

## Main Elements
Uses loopback IPv4 addresses with different prefix lengths, negated `localhost`, and negated `lo0` interface expansions.

## Risk Notes
Checks address masking and DNS/interface expansion in normalized output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0012.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0013.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0013.in

## Purpose
Regression input for `pass quick`; route-related examples are preserved as comments.

## Main Elements
Contains active quick pass rules for `enc0` with any, `inet`, and `inet6` address families, plus commented route-to/dup-to/reply-to cases.

## Risk Notes
Ensures comments do not affect parser output and basic quick pass normalization remains stable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0013.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0014.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0014.in

## Purpose
Regression input for IPv6 link-local scoped addresses.

## Main Elements
Tests `fe80::1%lo0` in source and destination positions, with and without explicit `on lo0`.

## Risk Notes
Validates IPv6 scope-id parsing and printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0014.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0016.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0016.in

## Purpose
Regression input for NAT/RDR/binat ordering and no-state pass output.

## Main Elements
Includes match rules for `nat-to`, `rdr-to`, `binat-to`, followed by a pass rule with `no state`.

## Risk Notes
Historically tied to rule-order processing expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0016.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0018.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0018.in

## Purpose
Regression input for NAT address-list expansion.

## Main Elements
Defines source and destination lists; tests protocol-specific `nat-to`, interface targets, parenthesized dynamic interfaces, negated destinations, static-port, and interface-list `on`.

## Risk Notes
Validates NAT pool and list expansion behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0018.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0019.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0019.in

## Purpose
Regression input for RDR list processing.

## Main Elements
Defines interface and network macros, then tests a direct RDR rule and list-expanded RDR rule with destination port translation.

## Risk Notes
Checks macro/list expansion in redirect rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0019.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0020.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0020.in

## Purpose
Regression input for NAT/RDR list expansion.

## Main Elements
Uses macros for interfaces, source networks, and destination networks in both `nat-to` and `rdr-to` match rules.

## Risk Notes
Tests Cartesian expansion across NAT/RDR clauses.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0020.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0022.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0022.in

## Purpose
Regression input for global `set` options.

## Main Elements
Tests optimization, grouped and single timeout settings, limits, loginterface changes, and hostid.

## Risk Notes
Covers parser state for global option commands.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0022.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0023.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0023.in

## Purpose
Regression input for negated interface matching.

## Main Elements
Contains `block in on ! lo0 all`.

## Risk Notes
Checks `ifnot` parsing and output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0023.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0024.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0024.in

## Purpose
Regression input for variable concatenation.

## Main Elements
Defines variables from other variables and quoted strings, then uses a concatenated macro in a TCP port list.

## Risk Notes
Validates macro concatenation order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0024.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0025.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0025.in

## Purpose
Regression input for antispoof expansion.

## Main Elements
Tests `antispoof` for `lo0` and `(lo0)`, with `log quick` and `inet`.

## Risk Notes
Exercises parser-generated antispoof rules and dynamic interface notation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0025.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0026.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0026.in

## Purpose
Regression input for negated dynamic interface addresses.

## Main Elements
Blocks inbound/outbound traffic on `lo0` using `! (lo0)` in source and destination positions.

## Risk Notes
Validates dynamic address negation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0026.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0028.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0028.in

## Purpose
Regression input for log and quick keyword ordering.

## Main Elements
Tests `log (all) quick`, `quick log`, plain `log`, and variants on `lo0`.

## Risk Notes
Ensures parser accepts equivalent keyword orderings.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0028.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0030.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0030.in

## Purpose
Regression input for line continuation.

## Main Elements
Builds a block rule across multiple escaped lines.

## Risk Notes
Checks lexer continuation handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0030.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0031.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0031.in

## Purpose
Regression input for block-policy and explicit block actions.

## Main Elements
Sets block policy to drop and tests `block return`, `block drop`, and bare block for all/inet/inet6.

## Risk Notes
Validates interaction between global block policy and explicit rule action output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0031.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0032.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0032.in

## Purpose
Regression input for abbreviated IPv4 network parsing.

## Main Elements
Tests `10/8`, `10.1/8`, and host addresses with `/25`, `/24`, `/16`, `/8`.

## Risk Notes
Covers `inet_net_pton()` style parsing and mask normalization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0032.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0034.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0034.in

## Purpose
Regression input for mixed address families and probabilities.

## Main Elements
Tests address-list expansion containing IPv4 and IPv6 targets plus numeric and percent probability syntax.

## Risk Notes
Validates AF splitting and probability formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0034.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0035.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0035.in

## Purpose
Regression input for TOS matching.

## Main Elements
Defines interface macro and uses two TCP pass rules with different IPv4 TOS values.

## Risk Notes
Checks TOS parsing and hex output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0035.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0038.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0038.in

## Purpose
Regression input for user/group rule options.

## Main Elements
Pass rules matching user `bin`, group `bin`, and combined group/user constraints.

## Risk Notes
Validates uid/gid parser ordering and output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0038.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0039.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0039.in

## Purpose
Regression input for option ordering.

## Main Elements
Uses macro-built rule bodies and option fragments to test arbitrary ordering of user, group, flags, ICMP spec, TOS, keep state, fragment, allow-opts, labels, and priority.

## Risk Notes
Ensures parser canonicalizes options regardless of input order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0039.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0040.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0040.in

## Purpose
Regression input for minimal block/pass forms.

## Main Elements
Covers bare `block`, `pass`, direction-specific forms, `all`, interface, address, protocol, flags, UDP keep-state, and port matching.

## Risk Notes
Checks defaults and implicit expansions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0040.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0041.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0041.in

## Purpose
Regression input for anchor syntax.

## Main Elements
Tests named anchors, anchors with rule filters, address families, protocols, ports, user/group filters, and ICMP type.

## Risk Notes
Validates anchor-call formatting and filter option parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0041.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0047.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0047.in

## Purpose
Regression input for label macro expansion.

## Main Elements
Exhaustively tests `$if`, `$srcaddr`, `$dstaddr`, `$srcport`, `$dstport`, `$proto`, and `$nr` in labels across IPv4, IPv6, negated addresses, dynamic interfaces, port operators, and numeric protocols.

## Risk Notes
High coverage for rule-label interpolation and list expansion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0047.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0048.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0048.in

## Purpose
Regression input for tables.

## Main Elements
Defines tables with flags, negated entries, IPv4/IPv6 addresses, interface entries, files, and const flag; uses tables in NAT/RDR and pass rules with negated table references.

## Risk Notes
Covers table parser whitespace, flags, and rule references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0048.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0049.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0049.in

## Purpose
Regression input for interface `:network` and `:broadcast` modifiers.

## Main Elements
Uses `lo0:network` in inbound/outbound IPv4/IPv6 pass rules; broadcast case is commented out.

## Risk Notes
Validates interface modifier expansion and comment handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0049.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0050.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0050.in

## Purpose
Regression input for repeated macro assignment.

## Main Elements
Defines `extif` twice and uses final value in a block rule.

## Risk Notes
Checks macro redefinition semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0050.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0052.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0052.in

## Purpose
Regression input for optimization keyword parsing.

## Main Elements
Sets optimization modes `normal`, `satellite`, `high-latency`, `conservative`, and `aggressive`.

## Risk Notes
Guards against future keyword conflicts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0052.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0053.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0053.in

## Purpose
Regression input for labels with interface macro expansion.

## Main Elements
Two TCP pass rules with source address lists and labels containing `$nr`, `$if`, `$proto`, `$srcaddr`, `$srcport`, `$dstaddr`, and `$dstport`.

## Risk Notes
Checks label expansion with and without explicit interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0053.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0055.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0055.in

## Purpose
Regression input for many global `set` options.

## Main Elements
Covers timeout groups and singles, limits, loginterface, hostid, optimization, and block policy.

## Risk Notes
Validates repeated global option application and output order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0055.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0056.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0056.in

## Purpose
Regression input for per-rule state options.

## Main Elements
Tests TCP pass rules with `keep state` timeout override, max state limit, no-sync, and timeout override.

## Risk Notes
Checks rule option parenthesis formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0056.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0057.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0057.in

## Purpose
Regression input for variable redefinition.

## Main Elements
Defines `a`, redefines `b`, and uses `$a` in a pass rule.

## Risk Notes
Ensures unused redefinitions do not affect unrelated expansions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0057.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0060.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0060.in

## Purpose
Regression input for multicast netmask handling.

## Main Elements
Pass rules from multicast IPv4 addresses with `/32`, `/16`, `/26`, and host-only forms.

## Risk Notes
Checks mask normalization for multicast ranges.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0060.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0061.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0061.in

## Purpose
Regression input for dynamic address with netmask.

## Main Elements
Uses `pass inet to (lo0)/24`.

## Risk Notes
Checks dynamic interface mask parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0061.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0065.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0065.in

## Purpose
Regression input for antispoof labels.

## Main Elements
Antispoof rules for `lo0` with labels and `log quick`.

## Risk Notes
Checks labels on parser-generated antispoof rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0065.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0067.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0067.in

## Purpose
Regression input for tags.

## Main Elements
Pass rule setting tag `regress` and a second rule matching `tagged regress`.

## Risk Notes
Validates tag and tagged output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0067.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0069.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0069.in

## Purpose
Regression input for tag with NAT match rule.

## Main Elements
Match rule with `tag regress nat-to lo0` and pass rule matching the tag.

## Risk Notes
Checks tag propagation syntax on match/NAT rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0069.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0070.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0070.in

## Purpose
Regression input for tag matching after NAT.

## Main Elements
NAT match rule followed by block rule matching `tagged regress`.

## Risk Notes
Ensures tagged clause parses independently of actual prior tag creation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0070.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0071.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0071.in

## Purpose
Regression input for tag matching after RDR.

## Main Elements
RDR match rule followed by block rule matching `tagged regress`.

## Risk Notes
Covers tagged syntax with redirect rules nearby.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0071.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0072.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0072.in

## Purpose
Regression input for binat tagging.

## Main Elements
A binat match rule with `tag regress` and a block rule matching `tagged regress`.

## Risk Notes
Checks tag parsing on binat rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0072.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0074.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0074.in

## Purpose
Regression input for synproxy state.

## Main Elements
Single TCP pass rule with `synproxy state`.

## Risk Notes
Validates minimal synproxy formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0074.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0075.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0075.in

## Purpose
Regression input for block quick with tags.

## Main Elements
Sets tag `ssh` on a TCP block rule and blocks quickly on `! tagged ssh`.

## Risk Notes
Covers negated tagged syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0075.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0077.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0077.in

## Purpose
Regression input for dynamic address netmask edge case.

## Main Elements
Comments describe a prior parser/printing bug; active rule is `pass inet from (lo0)/8`.

## Risk Notes
Guards against interface-name truncation or malformed dynamic-address output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0077.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0078.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0078.in

## Purpose
Regression input for table reference in label expansion.

## Main Elements
Pass rule from fixed IPv4 source to `<regress>` with label `$srcaddr:$dstaddr`.

## Risk Notes
Checks label expansion when destination is a table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0078.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0079.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0079.in

## Purpose
Regression input for `no-route` in label expansion.

## Main Elements
Pass rule from fixed IPv4 source to `no-route` with label macros.

## Risk Notes
Checks special address keyword handling in labels.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0079.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0081.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0081.in

## Purpose
Regression input for optimizer skip-step behavior with dynamic addresses, tables, and no-route.

## Main Elements
Defines IPv4/IPv6 literal lists and table lists, then creates repeated pass rules from `(lo0)`, `<foo>`, and `no-route`.

## Risk Notes
Targets optimizer behavior and mixed address/table list expansion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0081.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0082.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0082.in

## Purpose
Regression input for optimizer skip-step behavior.

## Main Elements
Pass rules from dynamic interfaces, negated dynamic interfaces, tables, negated tables, `inet`/`inet6`, and `no-route`.

## Risk Notes
Checks optimizer interaction with special source types.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0082.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0084.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0084.in

## Purpose
Regression input for source tracking and sticky-address pools.

## Main Elements
Tests NAT/RDR pools with round-robin, sticky-address, random, and pass rules with `source-track`, max source nodes/states, and connection limits.

## Risk Notes
Covers pool option and state option formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0084.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0085.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0085.in

## Purpose
Regression input for tag macro expansion.

## Main Elements
Pass rules over a source address list using `$srcaddr` in `tag` and `tagged`.

## Risk Notes
Checks tag/tagged macro interpolation across expanded sources.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0085.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0087.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0087.in

## Purpose
Regression input for optimization rule reordering.

## Main Elements
Many pass rules across interfaces, directions, protocols, addresses, ports, and state modes intended for `pfctl -o` rule reordering tests.

## Risk Notes
Used to detect optimizer ordering regressions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0087.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0088.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0088.in

## Purpose
Regression input for optimization duplicate-rule handling.

## Main Elements
Contains duplicate and near-duplicate pass/block rules differing by AF, direction, quick, interface, state mode, and ports.

## Risk Notes
Checks optimizer deduplication preserves distinct semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0088.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0089.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0089.in

## Purpose
Regression input for TCP connection tracking limits.

## Main Elements
Defines table `<bad>`, blocks globally and quickly from it, and adds TCP pass rules with `max-src-conn`, `max-src-conn-rate`, overload table, flush, and flush global.

## Risk Notes
Validates state option parsing and overload output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0089.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0090.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0090.in

## Purpose
Regression input for log option variants.

## Main Elements
Tests `log (user)`, `log (all)`, `log (to pflog7)`, and combined log option ordering.

## Risk Notes
Covers log option list parsing and output order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0090.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0091.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0091.in

## Purpose
Regression input for nested anchors.

## Main Elements
Creates an anchor on an interface, nested named anchors with filters, and rules inside nested scopes.

## Risk Notes
Validates inline anchor nesting and inherited filters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0091.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0092.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0092.in

## Purpose
Regression input for comments and deeply nested anchors.

## Main Elements
Uses comments around anchor blocks, repeated nested anchor scopes, and an anchor with an interface filter.

## Risk Notes
Checks lexer comment handling inside nested braces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0092.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0094.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0094.in

## Purpose
Regression input for address ranges.

## Main Elements
Tests IPv4 and IPv6 source/destination address range syntax, including full IPv4 and IPv6 ranges.

## Risk Notes
Validates address range expansion and AF handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0094.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0095.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0095.in

## Purpose
Regression input for include handling.

## Main Elements
Includes `./pf0095.include` and adds a TCP block rule.

## Risk Notes
Depends on tests changing directory to the `files` directory so relative include paths resolve.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0095.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0096.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0096.in

## Purpose
Regression input for macro expansion inside numeric port lists.

## Main Elements
Defines `myports` and `moreports`, then uses the expanded macro as TCP destination ports.

## Risk Notes
Checks concatenated macro values can be parsed as numeric ports.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0096.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0097.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0097.in

## Purpose
Regression input for `divert-to`.

## Main Elements
Tests TCP `divert-to` rules with IPv4 localhost and ports; one `divert-reply` example is commented; includes a proto 103 FIXME case.

## Risk Notes
FreeBSD-specific divert formatting differs from OpenBSD paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0097.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0098.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0098.in

## Purpose
Regression input for rule-order processing.

## Main Elements
Contains a pass rule followed by an IPv6 NAT match rule; comment notes order should pass without require-order.

## Risk Notes
Guards against overly strict rule-order enforcement.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0098.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0100.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0100.in

## Purpose
Regression input for anchors with multiple path components.

## Main Elements
Tests absolute and relative anchors, wildcard anchors, nested named anchors, unnamed inline anchors, and labels inside anchor scopes.

## Risk Notes
Validates anchor path normalization and nested path resolution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0100.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0101.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0101.in

## Purpose
Regression input for priority setting.

## Main Elements
Tests single priority, two-priority tuple, and list-expanded UDP pass rule with priority.

## Risk Notes
Checks `set prio` parsing and printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0101.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0102.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0102.in

## Purpose
Regression input for mixed address-family list expansion.

## Main Elements
Pass rules from mixed IPv4/IPv6 lists to `(self)` with and without `/40`.

## Risk Notes
Validates AF-specific expansion for dynamic destinations and masks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0102.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0104.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0104.in

## Purpose
Regression input for divert-to localhost resolution.

## Main Elements
Tests `divert-to localhost`, explicit IPv4 localhost, explicit IPv6 localhost, and address-family-constrained variants.

## Risk Notes
Assumes `localhost` resolves to `127.0.0.1` first, as noted in the file.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf0104.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1001.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1001.in

## Purpose
FreeBSD regression input for IPv6 binat.

## Main Elements
Two `binat` rules translating between `fc00::/64` and `fc00:0:0:1::/64`.

## Risk Notes
Checks IPv6 binat normalization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1001.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1002.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1002.in

## Purpose
FreeBSD regression input for SCTP timeout settings.

## Main Elements
Sets interval and SCTP timeout values for first, opening, established, closing, and closed states.

## Risk Notes
Guards SCTP timeout keyword support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1002.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1003.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1003.in

## Purpose
FreeBSD regression input for ALTQ.

## Main Elements
Defines CBQ ALTQ on `em0`, queue `qmain`, and a pass rule using the queue.

## Risk Notes
Checks ALTQ parser integration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1003.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1004.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1004.in

## Purpose
FreeBSD regression input for ALTQ with CoDel.

## Main Elements
Defines CBQ default CoDel queue hierarchy with `q1`/`q2` and pass/block rules assigning queues.

## Risk Notes
Covers CoDel queue option output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1004.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1005.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1005.in

## Purpose
FreeBSD regression input for PR 231323 route/NAT behavior.

## Main Elements
RDR rule and route-to pass rules for IPv4 and IPv6 localhost.

## Risk Notes
Checks route-to formatting with address-family constraints.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1005.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1006.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1006.in

## Purpose
FreeBSD regression input for FAIRQ parser crash coverage.

## Main Elements
Defines fairq ALTQ and a default fairq queue.

## Risk Notes
Guards against crashes on minimal fairq configuration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1006.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1007.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1007.in

## Purpose
FreeBSD regression input for basic ethernet rule.

## Main Elements
Ethernet block rule on `igb0` to a negated MAC address.

## Risk Notes
Checks ethernet-rule printer and MAC negation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1007.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1008.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1008.in

## Purpose
FreeBSD regression input for ethernet mask length.

## Main Elements
Ethernet block rule to a MAC address with `/24` mask length.

## Risk Notes
Validates MAC prefix formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1008.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1009.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1009.in

## Purpose
FreeBSD regression input for ethernet explicit mask.

## Main Elements
Ethernet block rule to a MAC address with ampersand mask.

## Risk Notes
Validates non-prefix MAC mask formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1009.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1010.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1010.in

## Purpose
FreeBSD regression input for POM_STICKYADDRESS behavior.

## Main Elements
ICMP rule with type list and route-to rule with `sticky-address`.

## Risk Notes
Checks route pool option formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1010.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1011.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1011.in

## Purpose
FreeBSD regression input for disabling scrub fragment reassembly.

## Main Elements
Single `scrub fragment no reassemble` rule.

## Risk Notes
Checks scrub fragment flag output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1011.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1012.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1012.in

## Purpose
FreeBSD regression input for default scrub fragment reassembly.

## Main Elements
Single `scrub` rule.

## Risk Notes
Checks scrub default output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1012.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1013.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1013.in

## Purpose
FreeBSD regression input for ethernet ridentifier.

## Main Elements
Ethernet block rule with `ridentifier 12345678`.

## Risk Notes
Checks ethernet rule identifier printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1013.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1014.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1014.in

## Purpose
FreeBSD regression input for ethernet label.

## Main Elements
Ethernet block rule with one label.

## Risk Notes
Checks ethernet label output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1014.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1015.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1015.in

## Purpose
FreeBSD regression input for multiple ethernet labels.

## Main Elements
Ethernet block rule with two labels.

## Risk Notes
Checks repeated ethernet label parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1015.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1016.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1016.in

## Purpose
FreeBSD regression input for ethernet label plus ridentifier.

## Main Elements
Ethernet block rule with label and `ridentifier`.

## Risk Notes
Checks option ordering for ethernet rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1016.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1017.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1017.in

## Purpose
FreeBSD regression input for ethernet multiple labels plus ridentifier.

## Main Elements
Ethernet block rule with two labels and `ridentifier`.

## Risk Notes
Covers repeated labels combined with identifiers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1017.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1018.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1018.in

## Purpose
FreeBSD regression input for dynamic address mask.

## Main Elements
Pass rule from mixed IPv4/IPv6 literals to `(pppoe0)`.

## Risk Notes
Checks mixed AF expansion with dynamic destination.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1018.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1019.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1019.in

## Purpose
FreeBSD regression input for pflow option.

## Main Elements
Pass rule with `keep state (pflow)`.

## Risk Notes
Validates pflow state option formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1019.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1020.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1020.in

## Purpose
FreeBSD regression input for table-file comments.

## Main Elements
Defines table `<tabl1>` from `./pf1020.include` and blocks from it.

## Risk Notes
Checks include/table-file parsing for hash and semicolon comment handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1020.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1021.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1021.in

## Purpose
FreeBSD regression input for endpoint-independent NAT.

## Main Elements
NAT rule using dynamic interface target and `endpoint-independent`.

## Risk Notes
Checks pool option output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1021.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1022.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1022.in

## Purpose
FreeBSD regression input for `received-on`.

## Main Elements
Pass-out rule with fixed source/destination and `received-on fxp0`.

## Risk Notes
Checks receive-interface filter formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1022.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1023.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1023.in

## Purpose
FreeBSD regression input for `match log(matches)`.

## Main Elements
Two match rules using `log(matches)`, followed by a pass rule.

## Risk Notes
Validates log matches flag parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1023.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1024.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1024.in

## Purpose
FreeBSD regression input for NAT64 `af-to`.

## Main Elements
Pass rule `inet af-to inet6` from an IPv6 translation source.

## Risk Notes
Checks address-family translation syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1024.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1025.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1025.in

## Purpose
FreeBSD regression input for NAT64 with implicit address family.

## Main Elements
Pass rule from IPv4 network with `af-to inet6` source.

## Risk Notes
Checks inferred AF behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1025.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1026.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1026.in

## Purpose
FreeBSD regression input for NAT64 with route-to.

## Main Elements
Pass rule on `epair2b` with IPv4 route-to gateway, IPv6 destination prefix, and `af-to inet from (epair0a)`.

## Risk Notes
Checks AF translation with route pools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1026.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1027.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1027.in

## Purpose
FreeBSD regression input for NAT64 with reply-to.

## Main Elements
Pass rule on `epair2b` with IPv6 reply-to gateway and `af-to inet`.

## Risk Notes
Checks reply-to with translation rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1027.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1028.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1028.in

## Purpose
FreeBSD regression input for RDR pool default port behavior.

## Main Elements
RDR rule without explicit redirected port.

## Risk Notes
Ensures no port means keep original port for RDR output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1028.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1029.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1029.in

## Purpose
FreeBSD regression input for RDR single port.

## Main Elements
RDR rule redirecting to port `1002`.

## Risk Notes
Checks single RDR port display.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1029.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1030.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1030.in

## Purpose
FreeBSD regression input for RDR default port range display.

## Main Elements
RDR rule with explicit default range `50001:65535`.

## Risk Notes
Checks default RDR range behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1030.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1031.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1031.in

## Purpose
FreeBSD regression input for RDR port range to single port.

## Main Elements
RDR rule matching port range `1004:2004` redirected to port `1004`.

## Risk Notes
Checks port range/single target normalization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1031.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1032.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1032.in

## Purpose
FreeBSD regression input for RDR port range to target range.

## Main Elements
RDR rule matching `1005:2005` redirected to `3004:*`.

## Risk Notes
Checks wildcard upper port handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1032.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1033.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1033.in

## Purpose
FreeBSD negative regression input for RDR static-port.

## Main Elements
RDR rule attempts to use `static-port`.

## Risk Notes
Expected failure: static-port is not valid on RDR rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1033.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1034.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1034.in

## Purpose
FreeBSD negative regression input for RDR MAP-E portset.

## Main Elements
RDR rule attempts `map-e-portset 6/8/0x34`.

## Risk Notes
Expected failure: MAP-E portset is not valid on RDR rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1034.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1035.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1035.in

## Purpose
FreeBSD regression input for NAT default port behavior.

## Main Elements
NAT rule without explicit port range.

## Risk Notes
Checks default NAT proxy port semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1035.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1036.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1036.in

## Purpose
FreeBSD regression input for explicit default NAT port range.

## Main Elements
NAT rule with port `50001:65535`.

## Risk Notes
Default NAT range should not be redundantly shown.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1036.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1037.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1037.in

## Purpose
FreeBSD regression input for NAT single port.

## Main Elements
NAT rule with translated port `1003`.

## Risk Notes
Checks NAT port display.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1037.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1038.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1038.in

## Purpose
FreeBSD regression input for NAT port range.

## Main Elements
NAT rule with port range `1004:2004`.

## Risk Notes
Checks translated NAT range display.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1038.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1039.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1039.in

## Purpose
FreeBSD regression input for NAT static-port.

## Main Elements
NAT rule with `static-port`.

## Risk Notes
Checks static-port formatting on NAT.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1039.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1040.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1040.in

## Purpose
FreeBSD negative regression input for NAT static-port with port numbers.

## Main Elements
NAT rule combines explicit port `1006` with `static-port`.

## Risk Notes
Expected failure: static-port conflicts with explicit port translation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1040.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1041.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1041.in

## Purpose
FreeBSD regression input for NAT MAP-E portset.

## Main Elements
NAT rule with `map-e-portset 6/8/0x34`.

## Risk Notes
Checks decimal display of MAP-E fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1041.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1042.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1042.in

## Purpose
FreeBSD negative regression input for MAP-E with static-port.

## Main Elements
NAT rule combines `static-port` and `map-e-portset`.

## Risk Notes
Expected failure: MAP-E portset cannot be used with static-port.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1042.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1043.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1043.in

## Purpose
FreeBSD negative regression input for MAP-E with explicit port.

## Main Elements
NAT rule combines port `1007` and `map-e-portset`.

## Risk Notes
Expected failure: MAP-E portset cannot be used with explicit port numbers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1043.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1044.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1044.in

## Purpose
FreeBSD regression input for sticky-address on table pools.

## Main Elements
NAT rule to `<targets>` with `sticky-address`.

## Risk Notes
Checks automatic round-robin behavior plus sticky-address.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1044.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1045.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1045.in

## Purpose
FreeBSD regression input for bitmask pool on prefix.

## Main Elements
NAT rule to `203.0.113.0/24 bitmask`.

## Risk Notes
Checks allowed bitmask pool target.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1045.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1046.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1046.in

## Purpose
FreeBSD negative regression input for bitmask pool on table.

## Main Elements
NAT rule to `<targets> bitmask`.

## Risk Notes
Expected failure: bitmask is invalid for table targets.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1046.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1047.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1047.in

## Purpose
FreeBSD negative regression input for bitmask pool on dynamic interface.

## Main Elements
NAT rule to `(vtnet1) bitmask`.

## Risk Notes
Expected failure: bitmask is invalid for bracketed interface targets.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1047.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1048.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1048.in

## Purpose
FreeBSD regression input for random pool on prefix.

## Main Elements
NAT rule to `203.0.113.0/24 random`.

## Risk Notes
Checks allowed random pool target.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1048.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1049.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1049.in

## Purpose
FreeBSD regression input for single-host pool list.

## Main Elements
NAT rule to one-host brace list.

## Risk Notes
Checks round-robin is not automatically set for a single host.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1049.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1050.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1050.in

## Purpose
FreeBSD regression input for table pool round-robin.

## Main Elements
NAT rule to `<targets>`.

## Risk Notes
Checks automatic round-robin for tables.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1050.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1051.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1051.in

## Purpose
FreeBSD regression input for multi-target pool round-robin.

## Main Elements
NAT rule to two literal addresses in a brace list.

## Risk Notes
Checks automatic round-robin for multiple targets.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1051.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1052.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1052.in

## Purpose
FreeBSD regression input for mixed host/table pools.

## Main Elements
NAT rule to a brace list containing a literal host and `<targets>`.

## Risk Notes
Checks mixed pool target handling and automatic round-robin.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1052.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1053.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1053.in

## Purpose
FreeBSD regression input for prefix pool default type.

## Main Elements
NAT rule to `203.0.113.0/24` without explicit pool type.

## Risk Notes
Checks round-robin is not automatically set for prefixes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1053.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1054.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1054.in

## Purpose
FreeBSD regression input for explicit round-robin on prefix.

## Main Elements
Comment notes likely bug; active NAT rule uses prefix target with `round-robin`.

## Risk Notes
Documents and tests current behavior for round-robin prefix pools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1054.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1055.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1055.in

## Purpose
FreeBSD regression input for source-hash pool.

## Main Elements
NAT rule to prefix with 128-bit source-hash key.

## Risk Notes
Checks source-hash key parsing and printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1055.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1056.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1056.in

## Purpose
FreeBSD regression input for `af-to` from and to addresses.

## Main Elements
IPv6 pass rule translating to IPv4 with explicit translated source and destination.

## Risk Notes
Checks full `af-to inet from ... to ...` output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1056.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1057.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1057.in

## Purpose
FreeBSD interface-translation regression input for IPv4 target.

## Main Elements
NAT rule to unbracketed interface `vlan1057`.

## Risk Notes
Requires test-created interface; validates unbracketed interface address translation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1057.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1058.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1058.in

## Purpose
FreeBSD interface-translation regression input for IPv4 target plus host.

## Main Elements
NAT rule to brace list containing literal `203.0.113.1` and unbracketed `vlan1058`.

## Risk Notes
Requires test-created interface; checks translated interface plus round-robin.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1058.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1059.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1059.in

## Purpose
FreeBSD interface-translation regression input for bracketed IPv4 interface.

## Main Elements
NAT rule to `(vlan1059)`.

## Risk Notes
Requires test-created interface; checks bracketed interface is not eagerly translated.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1059.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1060.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1060.in

## Purpose
FreeBSD interface-translation regression input for bracketed IPv4 interface plus host.

## Main Elements
NAT rule to brace list containing prefix `203.0.113.0` and `(vlan1060)`.

## Risk Notes
Requires test-created interface; checks bracketed dynamic target in mixed pool.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1060.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1061.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1061.in

## Purpose
FreeBSD interface-translation regression input for IPv6 target.

## Main Elements
NAT rule from IPv6 source/destination to unbracketed `vlan1061:0`.

## Risk Notes
Requires test-created interface; checks IPv6 address translation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1061.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1062.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1062.in

## Purpose
FreeBSD interface-translation regression input for IPv6 target plus host.

## Main Elements
NAT rule to brace list with `2001:db8::3` and unbracketed `vlan1062:0`.

## Risk Notes
Requires test-created interface; checks mixed IPv6 pool round-robin.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1062.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1063.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1063.in

## Purpose
FreeBSD interface-translation regression input for bracketed IPv6 interface.

## Main Elements
NAT rule to `(vlan1063)`.

## Risk Notes
Requires test-created interface; checks bracketed IPv6 dynamic target behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1063.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1064.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1064.in

## Purpose
FreeBSD interface-translation regression input for bracketed IPv6 interface plus host.

## Main Elements
NAT rule to brace list containing `fe80::2` and `(vlan1064)`.

## Risk Notes
Requires test-created interface; checks mixed IPv6 dynamic pool handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1064.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1065.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1065.in

## Purpose
FreeBSD regression input for `no nat`.

## Main Elements
`no nat` TCP rule with IPv6 source/destination.

## Risk Notes
Checks negative NAT action formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1065.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1066.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1066.in

## Purpose
FreeBSD regression input for `no rdr`.

## Main Elements
`no rdr` TCP rule with IPv6 source/destination.

## Risk Notes
Checks negative RDR action formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1066.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1067.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1067.in

## Purpose
FreeBSD negative regression input for route-to on block rules.

## Main Elements
Block rule with `route-to`.

## Risk Notes
Expected failure: route-to is not allowed on block rules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1067.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1068.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1068.in

## Purpose
FreeBSD regression input for max packet rate.

## Main Elements
ICMP pass rule with `max-pkt-rate 100/10`.

## Risk Notes
Checks max packet rate parsing and output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1068.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1069.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1069.in

## Purpose
FreeBSD regression input for max packet size.

## Main Elements
ICMP pass rule with `max-pkt-size 128`.

## Risk Notes
Checks packet-size rule option formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1069.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1070.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1070.in

## Purpose
FreeBSD negative regression input for include line numbers.

## Main Elements
Contains `pass in` and includes `pf1070.include`.

## Risk Notes
Expected failure path validates include-origin line reporting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1070.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1071.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1071.in

## Purpose
FreeBSD regression input for mask length on dynamic loopback address.

## Main Elements
Pass rule from `(lo0)/24`.

## Risk Notes
Checks dynamic interface mask display.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1071.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1072.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1072.in

## Purpose
FreeBSD negative regression input for invalid port range.

## Main Elements
TCP pass rule with source port range `500:100`.

## Risk Notes
Expected failure: low port exceeds high port.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1072.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1073.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1073.in

## Purpose
FreeBSD regression input for route-to AF mismatch with IPv6 nexthop preference.

## Main Elements
IPv4 filter rule with IPv6 route-to gateway and `prefer-ipv6-nexthop`.

## Risk Notes
Checks allowed AF mismatch when preference flag is present.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1073.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1074.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1074.in

## Purpose
FreeBSD negative regression input for route-to AF mismatch without preference.

## Main Elements
IPv4 filter rule with IPv6 route-to gateway but no `prefer-ipv6-nexthop`.

## Risk Notes
Expected failure: route-to nexthop AF differs from filter AF.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1074.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1075.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1075.in

## Purpose
FreeBSD regression input for one-shot rules.

## Main Elements
Pass rule from `(lo0)/24 once`.

## Risk Notes
Checks `once` rule flag formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1075.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1076.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1076.in

## Purpose
FreeBSD regression input for state limiter.

## Main Elements
Defines state limiter `dns-server`, then references it from a TCP pass rule with `(no-match)` action.

## Risk Notes
Checks limiter definition and rule reference parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1076.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1077.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1077.in

## Purpose
FreeBSD regression input for source limiter.

## Main Elements
Defines source limiter `dns-server` with entries, limit, rate, and IPv4 mask; references it from a TCP pass rule.

## Risk Notes
Checks source limiter definition and rule reference output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1077.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1078.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1078.in

## Purpose
FreeBSD regression input for form-feed/new-page handling.

## Main Elements
Contains TCP and UDP pass rules separated by a form-feed character.

## Risk Notes
Checks lexer treats page breaks as whitespace.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1078.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1079.in -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1079.in

## Purpose
FreeBSD regression input for combined `rdr-to` and `nat-to`.

## Main Elements
Single pass rule with TCP port match, `rdr-to`, and `nat-to` with translated port.

## Risk Notes
Checks simultaneous redirection and NAT clause formatting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/pf1079.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/macro.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/macro.sh

## Purpose
Shell ATF test for pfctl macro definitions containing spaces.

## Main Elements
- Defines ATF test case `space`.
- Writes invalid macro assignment with quoted name containing a space and expects `pfctl -nvf` to fail.
- Writes valid macro assignment with unquoted name and quoted value containing spaces and expects success.
- Cleans up temporary `pf.conf`.

## Dependencies And Integration
Requires `pf` kernel module and uses `atf_check`.

## Risk Notes
Protects macro-name grammar and quoted-value handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/macro.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test.c

## Purpose
ATF C harness for pfctl parser/output regression tests.

## Main Elements
- Reads expected output files and command output into `sbuf`s.
- Runs `pfctl -o none -nvf` against each input file and compares to `.ok` output, or regex-matches `.fail` for expected failures.
- Runs selfpf tests by feeding expected normalized output back through pfctl.
- Provides helpers to create/destroy VLAN interfaces for interface translation tests inside vnet jails.
- Uses macros from `pfctl_test_list.inc` to instantiate and register many ATF test cases.

## Dependencies And Integration
Uses ATF C API, `posix_spawnp()`, `ifconfig`, `pfctl`, `pf` kernel module metadata, `sbuf`, and test data under `tests/files`.

## Risk Notes
The harness redirects child stdout/stderr through pipes and depends on exact output matching. Interface tests require jail/vnet support and cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test_list.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test_list.inc

## Purpose
Single source of truth for pfctl ATF test registration.

## Main Elements
- Lists OpenBSD-derived tests `0001` through `0104`.
- Lists FreeBSD-specific tests `1001` through `1079`.
- Marks expected-failure tests with `PFCTL_TEST_FAIL`.
- Marks interface/vnet-dependent tests with `PFCTL_TEST_IFACE`.
- Intentionally has no include guards because it is included multiple times with different macro definitions.

## Dependencies And Integration
Included by `pfctl_test.c` to generate ATF test case declarations, bodies, and registrations.

## Risk Notes
Adding or renaming test data requires updating this file consistently with corresponding `.in`, `.ok`, and optional `.fail` files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test_list.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfilctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfilctl/Makefile

## Purpose
Builds the `pfilctl` utility.

## Main Elements
Sets `PROG=pfilctl`, source `pfilctl.c`, and manual page `pfilctl.8`; includes `bsd.prog.mk`.

## Dependencies And Integration
Uses standard FreeBSD program build infrastructure.

## Risk Notes
No special libraries are declared; behavior is fully in `pfilctl.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfilctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfilctl/pfilctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfilctl/pfilctl.c

## Purpose
Command-line control utility for FreeBSD pfil heads and hooks.

## Main Elements
- Dispatches abbreviated commands: `heads`, `hooks`, `link`, and `unlink`.
- Opens `/dev/pfil`.
- `listheads()` queries `PFILIOC_LISTHEADS`, resizes buffers if counts grow, and prints intercept points with in/out hooks.
- `listhooks()` queries `PFILIOC_LISTHOOKS` and prints hook module/ruleset/type.
- `hook()` parses `-i`, `-o`, `-a`, module:ruleset, and head name, then issues `PFILIOC_LINK`.

## Dependencies And Integration
Uses `<net/pfil.h>` ioctl ABI and PFIL device path.

## Risk Notes
Link/unlink mutates packet-filter hook attachment. Command matching permits abbreviations but rejects ambiguous matches.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfilctl/pfilctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflogd/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pflogd/Makefile

## Purpose
Builds `pflogd` from contributed PF logging daemon sources.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/contrib/pf/pflogd`.
- Builds `pflogd.c`, `pidfile.c`, `privsep.c`, and `privsep_fdpass.c`.
- Includes libpcap config/header paths.
- Links against `pcap`.
- Sets `PACKAGE=pf` and `WARNS?=2`.

## Dependencies And Integration
Uses contributed PF pflogd source and in-tree libpcap configuration.

## Risk Notes
Build correctness depends on contrib path and libpcap include configuration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflogd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflowctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/pflowctl/Makefile

## Purpose
Builds the `pflowctl` utility.

## Main Elements
Includes `src.opts.mk`, sets `PACKAGE=pf`, `PROG=pflowctl`, `MAN=pflowctl.8`, and source `pflowctl.c`.

## Dependencies And Integration
Uses standard FreeBSD program build infrastructure.

## Risk Notes
No explicit `LIBADD` is declared here; netlink support is expected from base build context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflowctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflowctl/pflowctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pflowctl/pflowctl.c

## Purpose
Command-line control utility for PFLOW exporters through FreeBSD generic netlink.

## Main Elements
- Parses operations: list (`-l`), create (`-c`), delete (`-d id`), set (`-s id ...`), and verbose (`-v`).
- Converts `pflowN` or numeric IDs to integer IDs.
- Uses snl parsers for list, create, get, and nested sockaddr attributes.
- `list()` enumerates PFLOW instances and calls `get()` for each.
- `create()` creates a pflow instance and prints its name.
- `del()` deletes an instance by ID.
- `get()` prints version, observation domain, source/destination addresses, and optional socket status.
- `set()` accepts `src`, `dst`, `proto`, and `domain`, parses numeric IPv4/IPv6 endpoint strings, and sends netlink SET attributes.

## Dependencies And Integration
Uses `<net/pflow.h>` generic netlink family constants and FreeBSD `snl` netlink helpers.

## Risk Notes
Address parsing is numeric-only and supports bracketed IPv6 port syntax. Operations fail if `pflow.ko` is not loaded.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pflowctl/pflowctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/Makefile

## Purpose
Builds the setuid-root `ping`/`ping6` utility.

## Main Elements
- Sets `PACKAGE=runtime`, `PROG=ping`, `BINOWN=root`, and `BINMODE=4555`.
- Builds `main.c` always; adds IPv4 `ping.c utils.c` when `MK_INET_SUPPORT` is enabled.
- Adds IPv6 `ping6.c`, `ping6` link, and manual-page link when `MK_INET6_SUPPORT` is enabled.
- Links `m`, optional `casper`/`cap_dns`, and `ipsec`.
- Adds tests subdirectory when tests are enabled.

## Dependencies And Integration
Uses FreeBSD build options for INET, INET6, dynamic root, Casper, and IPsec.

## Risk Notes
Setuid and capability support are central to runtime security. Build options change protocol support and linked libraries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/main.c

## Purpose
Protocol dispatcher and shared summary/signal handling for `ping`.

## Main Elements
- Defines shared option, hostname, packet counters, signal flags, and timing accumulators.
- Dispatches to `ping6()` when invoked as `ping6`.
- Scans early options to force IPv4/IPv6 on `-4`, `-6`, or numeric `-S`.
- Resolves target with `getaddrinfo()` when both INET and INET6 are compiled, choosing IPv4 or IPv6 based on result and available kernel features.
- Resets getopt state before calling protocol-specific implementation.
- `onsignal()` records SIGINT/SIGALRM/SIGINFO and exits on second SIGINT when safe.
- `pr_summary()` prints packet loss and round-trip min/avg/max/stddev.
- `usage()` prints IPv4 and IPv6 usage forms according to compile-time options.

## Dependencies And Integration
Includes `ping.h` and `ping6.h` conditionally. Shared globals are declared in `main.h` and used by protocol implementations.

## Risk Notes
Dispatcher resolution loses IPv6 intermediate-hop nuance except for final error handling. Signal behavior must stay async-safe.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/main.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/main.h

## Purpose
Shared declarations and option strings for ping IPv4/IPv6 implementations.

## Main Elements
- Defines `PING4OPTS` and `PING6OPTS`, including conditional IPsec option characters.
- Declares shared option flag `F_HOSTNAME`.
- Declares global hostname, counters, signal flags, and timing accumulators.
- Declares `onsignal()`, `pr_summary()`, and `usage()`.

## Dependencies And Integration
Included by `main.c`, `ping.c`, and IPv6 implementation files.

## Risk Notes
Option strings must stay synchronized with actual parser switch cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/main.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping.c

## Purpose
IPv4 ICMP ping implementation: raw socket setup, option parsing, packet generation, receive loop, reply validation, and output.

## Main Elements
- Defines IPv4-specific option flags, duplicate tracking bitmap, sockets, packet buffers, ICMP types, payload sizes, counters, sweep settings, and Casper DNS channel.
- `ping()` opens raw ICMP send/receive sockets before dropping setuid privileges, parses IPv4 options, resolves source/target via Casper DNS, configures socket options, enters Capsicum/Casper capability mode, sends initial/preload packets, and runs the receive/transmit loop.
- Supports flood, interval, count, timeout, waittime, payload pattern, sweep sizes, TTL, TOS, VLAN PCP, multicast options, record route, IP_HDRINCL/DF, mask request, timestamp request, audible/dot/quiet modes, source bind, and IPsec policy.
- `pinger()` constructs ICMP packets, embeds monotonic timestamps, computes ICMP/IP checksums, sends packets, and updates counters.
- `pr_pack()` validates received IP/ICMP lengths, matches replies to process ID, computes RTT, tracks duplicates, validates returned data, handles ICMP errors with quoted-packet checks, prints IP options, and updates stats.
- `pr_icmph()`, `pr_iph()`, `pr_addr()`, and `pr_ntime()` format ICMP/IP diagnostics, addresses, and timestamps.
- `fill()` parses hexadecimal payload patterns.
- `capdns_setup()` opens and limits Casper DNS service.

## Dependencies And Integration
Uses raw IPv4 sockets, Capsicum/Casper, IPsec conditionals, `in_cksum()` from `utils.c`, and shared globals/functions from `main.h`.

## Risk Notes
Security-sensitive due to setuid-root raw socket creation and later capability reduction. Packet parsing uses defensive length checks to avoid malformed ICMP/IP data. Exact output is test-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping.h

## Purpose
Minimal IPv4 ping interface header.

## Main Elements
Declares `int ping(int argc, char *const *argv);`.

## Dependencies And Integration
Included by `main.c` when INET support is compiled.

## Risk Notes
Small ABI surface; signature must match `ping.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping.h -->