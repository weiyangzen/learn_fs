# sources/distributed-fs/ceph-client/net/sched/act_skbmod.c

## Purpose

`act_skbmod.c` modifies packet header data in common skb cases: destination MAC, source MAC, Ethernet type, MAC address swap, or ECN congestion marking.

## Important APIs, types, and functions

`tcf_skbmod_init()` parses `TCA_SKBMOD_*`, derives exactly one supported flag mode, creates an RCU `tcf_skbmod_params`, and installs it. `tcf_skbmod_act()` ensures the editable header area is writable, mutates Ethernet fields or calls `INET_ECN_set_ce()`, and returns the configured action. Dump and cleanup hooks serialize/free params.

## Control flow

Init accepts a combination of DMAC/SMAC/ETYPE, or overrides with `SKBMOD_F_SWAPMAC`, or overrides with `SKBMOD_F_ECN`. Runtime drops immediately if configured action is `TC_ACT_SHOT`. For ECN it accepts IPv4/IPv6 packets and includes network-header length in the writable range; for MAC edits it requires an Ethernet device. After `skb_ensure_writable()`, it performs the selected edits and returns the configured action.

## State and persistence

State is an RCU params block with flags, optional Ethernet addresses, optional ethertype, and control action. Old params are freed after an RCU grace period. No per-packet state is retained beyond changed skb contents.

## Dependencies and integration points

It depends on Ethernet header helpers, ECN helpers, skb writability, tc action registration, and per-net action IDR storage.

## Risks and edge cases

Flag precedence is important: swapmac and ECN replace any attribute-derived MAC/etype combination. MAC operations silently no-op on non-Ethernet devices, while writability failures drop. ECN only operates on IPv4/IPv6 packets; other protocols pass unchanged. There is no flow offload hook in this file.

## Test signals

Exercise each mode, combined DMAC/SMAC/ETYPE, swap precedence, ECN on IPv4/IPv6 and non-IP packets, non-Ethernet devices, non-linear skb writable failure, dump output, and replace semantics.
