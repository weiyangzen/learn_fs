# Group Research: group_381_freebsd_src_sources_os_bsd_freebsd_src_sbin_pfctl_parse_y_sources_os_3c8867186d3e

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/parse.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/parse.y

## Purpose
Yacc grammar and support implementation for parsing FreeBSD `pfctl` configuration files. It translates `pf.conf` syntax into in-memory `pfctl` rules, anchors, tables, ALTQ queue definitions, Ethernet rules, NAT/rdr/binat translation rules, state/source limiters, and global PF options before handoff to the pfctl load paths.

## Main Elements
- Parser prologue defines parser-global state: active `struct pfctl *pf`, current rule-order state, default block/fail policies, default ICMP return values, macro table, include-file stack, ALTQ queue staging list, state-default list, and reusable option accumulator structs.
- Grammar entry `ruleset` accepts includes, options, state/source limiter declarations, Ethernet rules, scrub rules, NAT/binat/rdr rules, filter rules, anchors, ALTQ/queue definitions, variables, antispoof rules, and tables.
- `option` handles `set` directives: reassembly, optimization, ruleset optimization, timeouts, limits, loginterface, hostid, block/fail policy, require-order, fingerprints, state-policy/defaults, debug level, skip interfaces, keepcounters, and syncookies.
- Rule grammars build `struct pfctl_rule` or `struct pfctl_eth_rule` for `pass`, `match`, `block`, `scrub`, `antispoof`, `nat`, `rdr`, `binat`, `nat-to`, `rdr-to`, `binat-to`, `af-to`, `route-to`, `reply-to`, and `dup-to`.
- Support routines include consistency checks, table processing, label macro expansion, combinatorial rule expansion, pool application, binat-to companion rule generation, skip-interface application, lexer/token lookup, include-file management, macro management, and parser entry `parse_config()`.

## Dependencies And Integration
Uses `pfctl_parser.h`, `pfctl.h`, `<net/pfvar.h>`, ALTQ headers, libc name-service helpers, sysctl, MD5, and pfctl helper functions such as `pfctl_append_rule()`, `pfctl_define_table()`, `pfctl_add_altq()`, `pfctl_set_*()`, `host()`, `ifa_lookup()`, and `gen_dynnode()`.

## Risk Notes
This is a high-blast-radius parser: grammar changes can silently alter pf.conf compatibility, rule ordering, or generated kernel rule semantics. Parser-global accumulator structs, inline anchor/table movement, and address-family inference around NAT/rdr/binat are especially subtle.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pf_print_state.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pf_print_state.c

## Purpose
Formats PF runtime state entries for `pfctl` output. It converts kernel/userland state structures into readable addresses, ports, protocol state names, counters, flags, routing metadata, and the rule that created the state.

## Main Elements
- `print_addr()` prints PF address wrappers, including dynamic interface addresses, tables, ranges, masks, `any`, `no-route`, and `urpf-failed`.
- `print_state()` prints one `struct pfctl_state`, including direction-sensitive endpoints, NAT/address-family translation display, protocol state names, age/expiry, packet/byte counters, rule/anchor IDs, flags, routing target, rtable, original interface, and verbose creator rule.
- `unmask()` computes prefix length from a PF mask.

## Dependencies And Integration
Includes PF, TCP, SCTP, networking, resolver, and parser headers. Uses helpers such as `pfctl_proto2name()`, `print_rule()`, PF address macros, state flag constants, and PF state-name arrays.

## Risk Notes
Output depends on exact PF state structure layout and flag definitions. Direction and address-family translation logic is easy to regress because it rewrites which key index is displayed as source or destination.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pf_print_state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pf_ruleset.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pf_ruleset.c

## Purpose
Manages pfctl's in-memory normal and Ethernet anchor/ruleset hierarchy while parsing and assembling rules. It creates, finds, links, initializes, and removes rulesets and attaches anchor references to rules.

## Main Elements
- Defines global parser-side anchor state and RB-tree operations for normal anchors.
- `pf_get_ruleset_number()` maps PF actions to scrub, filter, NAT, binat, or rdr ruleset indexes.
- `pf_find_ruleset()` and `pf_find_or_create_ruleset()` find or build normal anchor paths.
- `pf_remove_if_empty_ruleset()` removes unreferenced normal anchors with no child anchors, tables, open table operations, or queued rules.
- Ethernet support includes `pf_init_eth_ruleset()`, recursive anchor lookup, `pf_find_or_create_eth_ruleset()`, and `pfctl_eth_anchor_setup()`.
- `pfctl_anchor_setup()` resolves absolute/relative normal anchor names, handles `../` traversal and `/*` wildcards, creates target rulesets, and increments reference counts.

## Dependencies And Integration
Uses PF and pfctl parser structures from `pfctl.h`, `pfctl_parser.h`, `<net/pfvar.h>`, and FreeBSD queue/tree macros. Called heavily by `parse.y` for anchor rules and inline anchor blocks.

## Risk Notes
Anchor tree integrity depends on synchronized RB-tree insertion/removal. `pf_remove_if_empty_eth_ruleset()` currently returns immediately, so Ethernet empty-anchor cleanup logic below it is unreachable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pf_ruleset.c -->