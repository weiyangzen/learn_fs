# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netlink.c

## Purpose
This file implements the nfnetlink userspace API for listing, creating, modifying, deleting, and receiving events for conntrack entries and expectations. It is the kernel side of ctnetlink: it serializes conntrack state into netlink attributes, parses userspace requests back into tuples and mutable fields, exposes per-CPU/global stats, bridges conntrack metadata into nfqueue glue when enabled, and registers per-netns event notifiers.

## Important APIs, Types, And Functions
The main callback tables are `ctnl_cb[]` for `NFNL_SUBSYS_CTNETLINK` and `ctnl_exp_cb[]` for `NFNL_SUBSYS_CTNETLINK_EXP`. The module registers `ctnl_subsys`, `ctnl_exp_subsys`, and `ctnetlink_net_ops`. Serialization is centered on `ctnetlink_fill_info()`, tuple dump helpers, extension dump helpers for accounting/timestamps/helper/labels/seqadj/synproxy, and expectation dump helpers such as `ctnetlink_exp_fill_info()`.

Parsing uses netlink policies `ct_nla_policy`, `tuple_nla_policy`, `proto_nla_policy`, `help_nla_policy`, `exp_nla_policy`, and optional NAT/seqadj/synproxy policies. Request handlers include `ctnetlink_get_conntrack()`, `ctnetlink_new_conntrack()`, `ctnetlink_del_conntrack()`, stats handlers, `ctnetlink_get_expect()`, `ctnetlink_new_expect()`, and `ctnetlink_del_expect()`. Event delivery uses `ctnetlink_conntrack_event()` and `ctnetlink_expect_event()`.

## Control Flow
Dumping a conntrack walks the hash table under bucket locks in `ctnetlink_dump_table()`, skips expired/nonmatching/non-original-direction entries, applies optional family/zone/mark/status/tuple filters, and emits netlink messages through `ctnetlink_fill_info()`. Single-entry get/delete parses an original or reply tuple plus zone and uses `nf_conntrack_find_get()`. Delete without a tuple flushes entries through `nf_ct_iterate_cleanup_net()` with the same filter machinery.

Creating a conntrack requires original and reply tuples, matching L4 protocol, and `CTA_TIMEOUT`. `ctnetlink_create_conntrack()` allocates the entry, optionally attaches helper/NAT/acct/timestamp/ecache/labels/seqadj/synproxy extensions, sets confirmed status and timeout, applies status/protoinfo/seqadj/synproxy/mark, optionally links a master conntrack, inserts into the hash, and reports events. Existing entries are modified by `ctnetlink_change_conntrack()`, which intentionally disallows NAT and master changes after creation.

Expectation control mirrors conntrack control. `ctnetlink_new_expect()` parses tuple, mask, master, zone, class, flags, optional NAT, helper assignment, and optional expectfn. It requires a helper-bearing master because expectations are helper-scoped. Dumps can list all expectations or only those attached to a master conntrack. Deletes can remove one expectation by tuple/id, all expectations for a helper name, or all expectations.

## State And Persistence
No disk state is used. Persistent runtime state is the conntrack table, expectation table, per-net event notifier registration, per-CPU stats, timers, labels, timestamps, helper extensions, and optional NAT/seqadj/synproxy extensions. Netlink dump cursors persist only in `netlink_callback` args/context during a multipart dump.

## Dependencies And Integration Points
This file is deeply integrated with conntrack core, expectations, helpers, L4 protocol plugins, accounting, zones, timestamps, labels, synproxy, NAT, security secctx, nfnetlink, module autoloading, per-netns registration, and optional `CONFIG_NETFILTER_NETLINK_GLUE_CT` for nfqueue metadata build/parse/expect attach/seq-adjust hooks.

## Risks
The risk profile is high because this is a privileged mutation API over shared conntrack state. Attribute validation must reject incomplete tuples, unsupported zones, impossible masks, invalid status masks, missing protocol numbers for protocol-specific filters, invalid label masks, and invalid expectation classes. Dump code must handle hash resize, expired entries, and skb space exhaustion without skipping or looping forever. Creation order matters: extensions must be attached before confirmation/insertion, helper and NAT autoload paths must handle `-EAGAIN`, and master references must be dropped on insertion failure. Event allocation failures are reported as netlink buffer pressure rather than crashing.

## Test Signals
Tests should cover multipart dump resume with filters, filtered flush, tuple get/delete by original and reply directions, zones and tuple zones, mark/status masks, create/update/delete conntracks, required timeout enforcement, helper attach and helper-private netlink data, NAT setup autoload failures, label attach with mask length validation, sequence-adjust and synproxy updates, event delivery for new/update/destroy/related, dying-list dump, stats dumps, expectation create/update/delete/dump with id checks, helper-name expectation flush, and nfqueue glue build/parse when enabled.
