# sources/distributed-fs/ceph-client/net/sched/act_tunnel_key.c

## Purpose

`act_tunnel_key.c` implements tc tunnel metadata actions. It can release tunnel metadata from an skb or attach transmit metadata describing IPv4/IPv6 tunnel endpoints, key id, destination port, checksum/DF flags, TOS/TTL, and Geneve/VXLAN/ERSPAN options.

## Important APIs, types, and functions

`tunnel_key_act()` drops or sets `skb_dst` with metadata dsts. `tunnel_key_init()` parses `TCA_TUNNEL_KEY_*`, validates set/release modes, allocates `metadata_dst` using `__ip_tun_set_dst()` or `__ipv6_tun_set_dst()`, initializes optional dst cache, parses encapsulation options, and installs `tcf_tunnel_key_params` under RCU. Option helpers include `tunnel_key_copy_geneve_opt()`, `tunnel_key_copy_vxlan_opt()`, `tunnel_key_copy_erspan_opt()`, `tunnel_key_copy_opts()`, and `tunnel_key_opts_set()`. Dump helpers serialize addresses and options. `tcf_tunnel_key_offload_act_setup()` maps set/release to tunnel encap/decap flow actions.

## Control flow

For `SET`, init handles optional key id, checksum default-on with `NO_CSUM` override, optional no-frag, dst port, tunnel options length validation, TOS/TTL, and exactly one IPv4 or IPv6 source/destination pair. It then stores options and marks the tunnel info as TX metadata. Runtime for release calls `skb_dst_drop()`. Runtime for set drops the existing dst and installs a clone of the prepared metadata dst.

## State and persistence

Each action persists an RCU params block containing the tcft action, control action, and optional metadata dst. Metadata dsts own dst-cache and tunnel-info option memory; cleanup releases the dst before freeing params. Per-net storage is the normal tc action IDR.

## Dependencies and integration points

It integrates tc actions with tunnel metadata used by tunnel netdevices and flower offload, plus Geneve, VXLAN, ERSPAN, IPv4/IPv6 tunnel info, dst cache, and flow offload.

## Risks and edge cases

The parser must reject mixed or duplicate option types, empty options, oversize Geneve options, invalid ERSPAN version-specific fields, and missing address pairs. Metadata dst lifetime is subtle on error paths and replace paths. `CONFIG_INET` gates option setting. Existing skb dst is always dropped before release or set.

## Test signals

Cover release, IPv4 set, IPv6 set, key id, no-csum, no-frag, dst port, TOS/TTL, Geneve/VXLAN/ERSPAN options, invalid mixed options, dump round trips, dst-cache cleanup, and offload tunnel info copying.
