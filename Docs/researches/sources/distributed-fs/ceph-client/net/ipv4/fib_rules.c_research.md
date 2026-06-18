# sources/distributed-fs/ceph-client/net/ipv4/fib_rules.c

## Purpose
`fib_rules.c` implements IPv4 policy routing rules for the generic FIB rules engine. It defines IPv4-specific rule selectors, validates and serializes rule netlink attributes, initializes default local/main/default rules, performs rule-driven lookup, and tracks whether custom rules require slower packet flow dissection.

## Important APIs, Types, and Functions
`struct fib4_rule` embeds `struct fib_rule` and adds IPv4 source/destination prefix lengths, masks and addresses, DSCP/TOS selector state, and optional route class ID. Exported helpers include `fib4_rule_default()`, `fib4_rules_dump()`, `fib4_rules_seq_read()`, and `__fib_lookup()`.

Rule callbacks in `fib4_rules_ops_template` are `fib4_rule_action()`, `fib4_rule_suppress()`, `fib4_rule_match()`, `fib4_rule_configure()`, `fib4_rule_delete()`, `fib4_rule_compare()`, `fib4_rule_fill()`, `fib4_rule_nlmsg_payload()`, and `fib4_rule_flush_cache()`. Namespace lifecycle is `fib4_rules_init()` and `fib4_rules_exit()`.

## Control Flow
`__fib_lookup()` updates the flow for l3mdev devices, calls `fib_rules_lookup()` with the IPv4 rules ops, copies class ID from the matching rule when enabled, and maps `-ESRCH` to `-ENETUNREACH`.

Rule matching checks source and destination masked prefixes, then DSCP/TOS semantics. Full DSCP selector rules compare the complete DSCP field with a mask; legacy TOS rules use masked legacy behavior. It then checks IP protocol and source/destination port ranges, which may require earlier flow dissection by callers.

Rule action handles table lookup and non-table actions. `FR_ACT_TO_TBL` selects the table from the rule and calls `fib_table_lookup()`. `FR_ACT_UNREACHABLE`, `FR_ACT_PROHIBIT`, and blackhole/unsupported actions return the route error directly. Suppression rejects otherwise matching results when the prefix length is too small or the nexthop device is in a suppressed interface group.

Configuration rejects IPv6 flowlabel attributes, validates TOS/DSCP, handles optional DSCP masks, forces `fib_unmerge()` so local/main table aliasing cannot hide custom rule behavior, allocates an empty table for unspecified table rules when needed, stores source/destination masks, increments class ID users, increments flow-dissect requirement counters for port/protocol selectors, and marks the namespace as having custom rules.

## State and Persistence Behavior
Rules are runtime per-net objects managed by the generic fib rules framework. IPv4-specific state is in each `fib4_rule` plus per-net `rules_ops`, `fib_has_custom_rules`, and `fib_rules_require_fldissect`. Optional class ID rules update `fib_num_tclassid_users`.

No state is durable. Adding or deleting rules flushes route cache through the rules ops and updates rule sequence via the generic framework. Default rules are recreated for each namespace during init.

## Dependencies and Integration Points
The file depends on the generic `fib_rules` framework, IPv4 FIB table lookup, l3mdev, DSCP helpers, nexthop/table state, route cache flush, and optional route class ID support. It integrates with `fib_frontend.c` for initialization and `fib_notifier.c` for rule dump/sequence reporting. `route.c`, `fib_frontend.c`, and netfilter use `fib4_rules_early_flow_dissect()` decisions through per-net counters set here.

## Risks and Edge Cases
DSCP/TOS compatibility is subtle: legacy TOS cannot express high-order DSCP bits, while new DSCP plus mask must be internally consistent and mutually exclusive with TOS. Incorrect validation can change policy routing behavior for existing users.

`fib_unmerge()` is required before custom rule changes; failure to split tables would cause rule-visible local/main lookup differences to be wrong. The flow-dissect counter must be incremented and decremented exactly for rules needing ports or protocol, or lookup callers will either miss selectors or pay unnecessary cost.

Suppression releases `fib_info` unless `FIB_LOOKUP_NOREF` is set. Refcount behavior must stay aligned with lookup flags. Rule delete marks `fib_has_custom_rules` true even after deletion, preserving conservative source-validation behavior.

## Test Signals
Test default rule creation, lookup through local/main/default tables, unreachable/prohibit/blackhole rule actions, source/destination prefix rules, legacy TOS versus DSCP/mask selectors, invalid flowlabel rejection, port/protocol rules and flow-dissect requirement counters, suppression by prefix length and interface group, class ID accounting, table auto-allocation, cache flush on rule change, and notifier sequence changes for rule mutations.
