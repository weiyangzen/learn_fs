# sources/distributed-fs/ceph-client/net/sched/act_mpls.c

## Purpose

`act_mpls.c` implements tc MPLS manipulation actions: pop, push, MAC push, modify label stack entry fields, and decrement TTL. It also exposes supported actions to flow offload.

## Important APIs, types, and functions

`tcf_mpls_act()` is the packet path. `tcf_mpls_init()` parses `TCA_MPLS_*` netlink attributes, validates action-specific combinations, creates an RCU `tcf_mpls_params`, and installs control action state. `tcf_mpls_get_lse()` composes a new label stack entry from optional label, TTL, traffic class, and BOS fields. `valid_label()` enforces MPLS label bounds and rejects implicit-null. `tcf_mpls_dump()` serializes the current params. `tcf_mpls_offload_act_setup()` maps push/pop/modify to `FLOW_ACTION_MPLS_*` and rejects `dec_ttl` and `mac_push` offload.

## Control flow

Initialization validates different rules per action: pop requires an 802.3 protocol and rejects label/TTL/TC/BOS; push/mac_push require a label and an MPLS ethertype if protocol is supplied; push defaults TTL from `net->mpls.default_ttl` or 255; modify rejects protocol; dec_ttl rejects all field attributes. Runtime temporarily pushes the MAC header for ingress, then calls `skb_mpls_pop()`, `skb_mpls_push()`, `skb_mpls_update_lse()`, or `skb_mpls_dec_ttl()`. Ingress packets are pulled back before returning the configured action.

## State and persistence

The action stores one RCU-replaced `tcf_mpls_params` block with mode, label, ttl, tc, bos, protocol, and control action. Per-net state is standard tc action IDR storage. The module itself has no external durable state, but push default TTL can depend on namespace MPLS settings.

## Dependencies and integration points

It depends on MPLS skb helpers, VLAN helper behavior for `MAC_PUSH` with accelerated VLAN tags, tc action APIs, optional `CONFIG_MPLS`, and flow offload. `MODULE_SOFTDEP("post: mpls_gso")` highlights integration with MPLS segmentation support.

## Risks and edge cases

Header position at ingress, VLAN-tag materialization before `MAC_PUSH`, default TTL selection, BOS auto-setting when pushing onto non-MPLS packets, and unsupported offload modes are the sensitive areas. Packet mutation failures drop with `TC_ACT_SHOT`; callers need to distinguish configured action from mutation failure.

## Test signals

Exercise pop, push, mac_push, modify, and dec_ttl on Ethernet and ingress paths; validate invalid label/protocol combinations; verify default TTL behavior with and without namespace MPLS TTL; inspect tc dumps; and verify offload conversion accepts only push/pop/modify.
