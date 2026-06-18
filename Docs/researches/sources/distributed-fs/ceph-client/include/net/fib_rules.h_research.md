# sources/distributed-fs/ceph-client/include/net/fib_rules.h

Read `sources/distributed-fs/ceph-client/include/net/fib_rules.h` completely for this pass (225 lines, 6137 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/fib_rules.h_research.md`.

Purpose: declares the generic policy routing rule framework used by IPv4/IPv6 and other families to match flows against ordered rules and dispatch lookups to routing tables.

Important APIs/types/functions: `struct fib_rule` stores match keys and action state: iif/oif indexes/names, mark/mask, flags, table/action/l3mdev/proto/ip_proto, goto target/ctarget, tunnel ID, netns, refcount, priority, suppressors, UID range, sport/dport ranges and masks, L3 master flags, and RCU node. `struct fib_lookup_arg` carries family lookup callbacks/results/rule/table/flags. `struct fib_rules_ops` is the family operation table for action, suppress, match, configure, delete, compare, fill, nlmsg payload, flush cache, rules list, owner, netns, and sequence. Helpers cover refcounting, table extraction with L3 master support, netlink table attr extraction, port range set/inrange/match/valid/compare/is-range, and field-dissect requirement detection. APIs include register/unregister, `fib_rules_lookup()`, default rule add, match-all test, dump/seq read, newrule/delrule netlink handlers, and indirect-call declarations for IPv4/IPv6 actions/matches/suppressors.

Control flow: families register `fib_rules_ops` per netns. Netlink rule add/delete creates or removes ordered `fib_rule` objects and flushes route cache. Lookup iterates rules in priority order, matching flow keys and optional dissected ports, performing actions/gotos/table lookups through family callbacks, and applying suppressors. Notifier integration reports rule changes.

State and persistence: rule lists, unresolved goto counts, sequence counters, and per-rule refs are runtime netns state. Rules are configured by userspace and persist until netns teardown or deletion, but are not stored by this header.

Dependencies and integration points: depends on fib_rules UAPI, netdevice, flow keys/dissection, rtnetlink, fib_notifier, refcount/RCU, indirect call wrappers, IPv4/IPv6 rule implementations, VRF/L3 master support, and route cache flushing.

Risks: port range matching combines masks and ranges; invalid zero/0xffff ranges must be rejected. Flow dissection is required only for non-loopback rules with ip_proto or ports; missing dissection can skip intended matches. Goto rules and unresolved targets can create loops or stale ctargets if not managed. Refcount/RCU teardown must be exact. L3 master table selection differs by config.

Test signals: add/delete/dump rules with priorities, tables, marks, iif/oif, UID range, tunnel ID, ip_proto, sport/dport ranges and masks; goto target resolution; suppress prefix/interface rules; L3 master/VRF behavior; route cache flush; notifier events; IPv4/IPv6 indirect action/match paths; invalid netlink attrs and extack messages; concurrent lookup/delete RCU tests.
