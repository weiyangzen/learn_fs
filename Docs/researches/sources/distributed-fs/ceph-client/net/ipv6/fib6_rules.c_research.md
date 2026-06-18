# sources/distributed-fs/ceph-client/net/ipv6/fib6_rules.c

## Purpose
Implements IPv6 routing policy rules. It extends generic `fib_rules` with IPv6 source/destination prefix, DSCP/TOS, flowlabel, protocol, port-range, l3mdev, suppressor, and source-address-selection behavior, while optimizing the default local/main-table lookup case.

## Important APIs, Types, and Functions
`struct fib6_rule` embeds `struct fib_rule` and adds `rt6key` source/destination selectors plus flowlabel/DSCP masks. Exported or externally used functions include `fib6_lookup()`, `fib6_rule_lookup()`, `fib6_rule_default()`, `fib6_rules_dump()`, `fib6_rules_seq_read()`, `fib6_rules_init()`, and `fib6_rules_cleanup()`. Rule ops include `fib6_rule_match()`, `fib6_rule_action()`, `fib6_rule_suppress()`, `fib6_rule_configure()`, `fib6_rule_delete()`, `fib6_rule_compare()`, and `fib6_rule_fill()`.

## Control Flow
Lookup bypasses the generic rules engine when no custom rules exist, checking local then main tables. With custom rules, it updates l3mdev flow fields and calls `fib_rules_lookup()` using either table lookup or policy lookup callbacks. Rule matching tests destination/source prefixes, deferred source selection via `FIB_RULE_FIND_SADDR`, DSCP, flowlabel, protocol, and ports. Rule actions select a table, return special blackhole/prohibit/unreachable routes, or ask the selected table/policy lookup for a route, then apply source-prefix and suppressor checks. Netlink configure/compare/fill paths validate DSCP masks, flowlabel masks, table IDs, and prefix attributes.

## State and Persistence
State lives per namespace in `net->ipv6.fib6_rules_ops`, `fib6_has_custom_rules`, and `fib6_rules_require_fldissect`. Default local/main rules are installed at namespace init. Rule contents are runtime netlink state, not persistent by this file.

## Dependencies and Integration Points
Depends on generic FIB rules, IPv6 FIB tables/routes, DSCP helpers, netlink attributes, l3mdev, route cache generation IDs, and namespace lifecycle. Route lookups, nft fib modules, and notifier dumps depend on these APIs.

## Risks and Test Signals
Risks include incorrect no-custom fast path, source-address deferral loops, DSCP/TOS ambiguity, invalid flowlabel masks, refcount handling on suppressed routes, field-dissector requirement leaks, and namespace batch unregister races. Test signals include `ip -6 rule` add/delete/dump/lookup, DSCP mask validation, flowlabel matching, sport/dport rules, l3mdev VRF rules, suppress prefix/group behavior, unreachable/prohibit/blackhole actions, and source-prefix rules without preset source.
