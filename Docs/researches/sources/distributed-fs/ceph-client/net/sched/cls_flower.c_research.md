
# sources/distributed-fs/ceph-client/net/sched/cls_flower.c

## Purpose

`cls_flower.c` implements the `flower` traffic-control classifier. It matches packets by structured flow-dissector keys rather than fixed byte offsets, covering Ethernet addresses, VLAN/CVLAN, IPv4/IPv6, transport ports and ranges, ICMP, ARP, MPLS stacks, tunnel metadata and options, conntrack fields, packet hash, PPPoE, L2TPv3, IPsec SPI, CFM, and `tc` metadata such as `l2_miss`. It is a hot-path classifier used by `tc filter ... flower`, software classification, and hardware offload through `TC_SETUP_CLSFLOWER`.

## Important APIs, Types, and Functions

Core state is split among `struct cls_fl_head`, `struct fl_flow_mask`, `struct cls_fl_filter`, `struct fl_flow_key`, and `struct fl_flow_tmplt`. `cls_fl_head` owns the mask rhashtable, mask list, hardware-filter list, and handle IDR. Each mask owns a per-mask rhashtable keyed by the masked key bytes and a flow dissector tailored to only the requested fields. Each filter stores the raw key, masked key, actions/extensions, class result, offload flags, handle, hardware count, deleted bit, and refcount.

The main classifier path is `fl_classify()`. Management enters through `fl_init()`, `fl_change()`, `fl_delete()`, `fl_destroy()`, `fl_get()/fl_put()`, `fl_walk()`, `fl_dump()`, `fl_terse_dump()`, and `fl_delete_empty()` in `cls_fl_ops`. Key parsing is concentrated in `fl_set_key()` and helpers for MPLS, VLAN, PPPoE, flags, IP fields, tunnel options, conntrack, CFM, port ranges, and IPsec SPI. Mask creation and lookup are handled by `fl_mask_update_range()`, `fl_init_dissector()`, `fl_create_new_mask()`, `fl_check_assign_mask()`, `fl_ht_insert_unique()`, and `fl_mask_lookup()`. Offload integration uses `fl_hw_replace_filter()`, `fl_hw_destroy_filter()`, `fl_hw_update_stats()`, `fl_reoffload()`, `fl_hw_add()`, `fl_hw_del()`, and template hooks.

## Control Flow

Initialization allocates `cls_fl_head`, initializes the mask list/lock, hardware list, handle IDR, and rhashtable. Classification iterates the RCU-protected mask list. For each mask it clears only the masked key range, runs metadata, tunnel, conntrack, hash, and packet flow dissection into a stack key, computes a masked lookup key, and checks the per-mask rhashtable. Port-range masks take a slower list-assisted path to verify range bounds before the hash lookup. A hit copies the stored `tcf_result` and executes the filter extensions unless software matching is skipped.

`fl_change()` parses netlink options, allocates a temporary mask and new filter, reserves or reuses a handle, validates actions, binds a class, parses keys and masks, validates template compatibility, enables `tc_skb_ext` when needed, assigns or creates the shared mask, inserts a unique masked-key entry, pushes hardware offload if requested, and then publishes the rule under `tp->lock`. Replacement swaps the IDR entry and list node, removes the old rhashtable entry, marks the old filter deleted, destroys old hardware state, unbinds its class, and drops references. Error unwinding removes IDR entries, hardware state, rhashtable entries, masks, class bindings, and filter references in reverse order.

Deletion marks a filter deleted under `tp->lock`, removes it from the mask table, IDR, and list, possibly drops the now-empty mask, destroys hardware state, unbinds the class, and releases the filter. Destroy walks all masks and filters through the same deletion path, destroys the handle IDR, then queues sleepable rhashtable/head cleanup.

Dumping mirrors the parser: `fl_dump_key()` emits only fields with non-zero masks, including nested MPLS, tunnel options, conntrack, flags, and CFM. Full dumps update hardware stats before emitting extension stats; terse dumps emit only flags and terse extension data. Template operations parse a mask-only rule, create/destroy hardware hints, and reject filters whose masks exceed the template mask.

## State and Persistence Behavior

Filter state persists in the handle IDR, per-mask filter lists, and per-mask rhashtables. Masks are shared and refcounted; they are inserted in a global mask table so rules with identical masks reuse the same dissector and lookup table. Filter references are atomic because `flower` uses `TCF_PROTO_OPS_DOIT_UNLOCKED`; the code can race with concurrent get/delete/change paths and uses `tp->lock`, RCU lists, IDR lookups under RCU, and explicit `deleted` checks.

Hardware state is tracked through per-filter `flags`, `in_hw_count`, and `hw_list`. `fl_hw_add()` and `fl_hw_del()` maintain the offloaded-filter list from driver callbacks. A rule matching `l2_miss` enables the shared `tc_skb_ext` facility and disables it when the filter is finally freed. Masks and filters are freed through `rcu_work`, with action net references deciding whether final destruction must run later.

## Dependencies and Integration Points

The file depends on `net/pkt_cls.h`, `net/sch_generic.h`, `flow_dissector`, tunnel metadata helpers for Geneve/VXLAN/ERSPAN/GTP/PFCP, conntrack UAPI bits, `tcf_exts`, `tcf_block` offload callbacks, IDR, rhashtable, RCU, and netlink policy parsing. It integrates with `cls_api` through `struct tcf_proto_ops`, with drivers through `TC_SETUP_CLSFLOWER`, and with chain templates through `tmplt_create/destroy/reoffload/dump`.

## Risks and Edge Cases

The mask-sharing path is concurrency-sensitive: a temporary zero-ref mask is inserted to block duplicate mask creation, and callers must handle `-EAGAIN` when a concurrent delete races. Mask range calculation and masked-key hashing must stay consistent or lookups and dumps diverge. Tunnel option parsing requires key/mask lengths to stay aligned and only one option type per rule. Port-range matching combines a list scan with hash lookup and is easy to break by changing `mkey` updates. Conntrack matching is compile-time-feature gated; accepting unsupported fields would create silently unmatchable rules. Offload failure semantics depend on `skip_sw`/`skip_hw` flags, so changes can unexpectedly install software fallbacks or reject valid hardware-only filters.

This local source also contains apparent corruption markers such as duplicated assignments in `fl_range_port_src_cmp()`. Those are compile/test risks for this snapshot and should be distinguished from upstream logic when validating.

## Test Signals

Useful signals include `tc` flower add/replace/delete/dump tests for each key family, netlink extack checks for invalid flags, conntrack, MPLS, tunnel option, and port range combinations, concurrent add/delete stress, `skip_sw` and `skip_hw` offload tests against a driver or dummy callback, and dump round-trip checks. Kernel selftests under networking/tc and driver offload tests should catch many regressions; compile coverage needs conntrack zones/marks/labels, tunnel options, MPLS, and CFM enabled.
