# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-rule.yaml

Purpose: this raw rtnetlink schema documents FIB rule management, including rule creation, deletion, dumps, and IPv4/IPv6 rule notifications.

Important APIs, types, and functions: `fib-rule-hdr` is the fixed header with family, destination/source lengths, TOS, table, action, and flags. `fr-act` covers unspecified, table lookup, goto, nop, blackhole, unreachable, and prohibit actions. `fib-rule-port-range` and `fib-rule-uid-range` model selector ranges. `fib-rule-attrs` includes destination/source, input/output interface names, goto target, priority, fwmark/fwmask, flow, tunnel id, suppressors, table, l3mdev, UID range, protocol, IP protocol, sport/dport ranges, DSCP, flowlabel and masks.

Control flow: `newrule` value 32 adds a FIB rule with the full selector/action attribute set; `newrule-ntf` publishes creation notifications via `getrule`. `delrule` value 33 removes a matching rule and `delrule-ntf` announces deletion. `getrule` value 34 dumps rules and replies as value 32.

State and persistence: rules live in per-network-namespace FIB rule lists, ordered primarily by priority. They persist until deletion, namespace teardown, or owning protocol cleanup.

Dependencies and integration: depends on `linux/fib_rules.h`, rtnetlink raw protocol, policy routing, l3mdev, tunnel metadata selectors, and multicast groups `rtnlgrp-ipv4-rule` and `rtnlgrp-ipv6-rule`.

Risks: selector masks and ranges must match kernel support by address family; priority collisions and action semantics can affect routing globally inside a namespace. Test signals include netns add/delete/dump of rules with fwmark, UID range, port range, DSCP/flowlabel selectors, and multicast notification checks.
