# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_xlat.c

Purpose: implements IPv6 Identifier-Locator Addressing translation for one network namespace. It stores locator-match mappings in an rhashtable, registers an IPv6 prerouting netfilter hook lazily on first mapping, and rewrites destination locators with `ila_update_ipv6_locator()` when a packet matches.

Important APIs, types, and functions: `struct ila_xlat_params` combines `struct ila_params` with an input ifindex discriminator; `struct ila_map` is the rhashtable object plus per-key RCU chain. `ila_xlat_nl_cmd_add_mapping()`, `ila_xlat_nl_cmd_del_mapping()`, `ila_xlat_nl_cmd_get_mapping()`, `ila_xlat_nl_cmd_flush()`, and dump start/done/dump implement generic-netlink control. `ila_xlat_init_net()`, `ila_xlat_pre_exit_net()`, and `ila_xlat_exit_net()` own per-net hash table, hook, and bucket-lock lifetime.

Control flow: netlink add parses locator, locator_match, checksum mode, identifier type, and ifindex; registers the prerouting hook if needed; allocates an `ila_map`; inserts it as either a new rhashtable head or an ordered per-key chain entry. Lookup uses `locator_match` as hash key and then filters by ifindex wildcard semantics. Packet flow enters `ila_nf_input()`, calls `ila_xlat_addr()`, looks up the destination locator under RCU, and rewrites in place if a mapping exists.

State and persistence: state is per-netns and memory-resident only. Mutations are serialized by per-bucket spinlocks plus a global mutex for hook registration. Readers are RCU-protected. Deletions use `kfree_rcu()`, and namespace teardown unregisters hooks before destroying the table and lock array.

Dependencies and integration points: depends on `ila.h`, rhashtable, generic netlink, netns generic storage, netfilter IPv6 prerouting, and ILA checksum/update helpers. It integrates with the ILA generic-netlink family defined elsewhere.

Risks: mapping ordering currently only scores ifindex specificity, so future wildcard dimensions must update `ila_order()` and comparison together. Flush walks and removes rhashtable entries while each per-locator lock is taken; iterator restart handling is important. Lazy hook registration means first add can fail due to netfilter registration errors. Packet rewrite assumes a pulled, valid IPv6 header.

Test signals: add/get/dump/delete/flush mappings through generic netlink; verify per-ifindex wildcard precedence; inject IPv6 packets with matching and non-matching locators; test namespace teardown with mappings present; run with RCU/debug lockdep to catch chain mutation issues.
