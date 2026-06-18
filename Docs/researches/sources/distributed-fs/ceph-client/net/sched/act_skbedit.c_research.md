# sources/distributed-fs/ceph-client/net/sched/act_skbedit.c

## Purpose

`act_skbedit.c` edits skb metadata rather than packet bytes. It can set priority, inherit DSCP into priority, choose queue mapping, set mark with a mask, and set packet type.

## Important APIs, types, and functions

`tcf_skbedit_init()` parses `TCA_SKBEDIT_*`, validates selected operations, creates an RCU `tcf_skbedit_params`, and installs control action state. `tcf_skbedit_act()` applies metadata edits. `tcf_skbedit_hash()` distributes queue mapping across a configured range using `skb_get_hash()`. `tcf_skbedit_dump()`, `tcf_skbedit_get_fill_size()`, and `tcf_skbedit_offload_act_setup()` support netlink dump sizing and hardware offload mapping.

## Control flow

Initialization builds a flags mask from supplied attributes and pure flags. Receive-side `queue_mapping` is allowed only for hardware-only use unless skip-sw is set. Hash-based queue ranges require both min and max queue mappings and valid ordering. Runtime updates stats, reads params under RCU, then applies priority, DS field inheritance for IPv4/IPv6, queue mapping with egress txqueue skip, masked mark update, and packet type update. If DS field headers cannot be pulled, the packet is dropped.

## State and persistence

Persistent action state is an RCU params block containing flags, priority, queue mapping/range, mark, mask, packet type, and action. The action also uses common tc stats and optional hardware stats updates.

## Dependencies and integration points

It depends on IP/IPv6 DS field helpers, skb hash and queue mapping APIs, netdevice tx queue limits, tc action infrastructure, and flow offload. It integrates with qdisc queue selection and later classifiers through skb metadata.

## Risks and edge cases

Queue mapping has direction-specific behavior and hardware-only constraints. DS field inheritance requires sufficient network header data and can drop malformed packets. Masked mark writes preserve bits outside the mask. Offload supports only one option shape at a time and rejects transmit queue mapping and inherit-DS-field modes.

## Test signals

Test priority set, IPv4/IPv6 DSCP inheritance, mark/mask writes, packet type validation, queue mapping range hashing, ingress skip-sw validation, dump round trips, and offload mapping/rejection paths.
