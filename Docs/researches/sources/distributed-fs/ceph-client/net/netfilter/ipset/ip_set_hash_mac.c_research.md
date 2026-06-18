# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_mac.c

## Purpose

`ip_set_hash_mac.c` implements the `hash:mac` ipset type. It stores one Ethernet MAC address per element and supports packet-path matching on source or destination Ethernet addresses plus userspace netlink management.

## Important APIs, types, and functions

`struct hash_mac4_elem` stores `ETH_ALEN` bytes in a union padded to two `__be32` words because generic hash code assumes zero-valued IP-like storage cannot represent a valid element. `hash_mac4_data_equal()` compares addresses with `ether_addr_equal()`, and `hash_mac4_data_list()` emits `IPSET_ATTR_ETHER`. `hash_mac4_kadt()` validates that the skb is on an Ethernet device with a usable MAC header, copies source or destination Ethernet address based on `IPSET_DIM_ONE_SRC`, rejects the all-zero address, and dispatches the generated ADT operation. `hash_mac4_uadt()` validates a six-byte netlink `ETHER` attribute, parses extensions, rejects the all-zero address, and calls the generated ADT function.

## Control flow

The module defines only one generated variant, with `NFPROTO_UNSPEC`, `IP_SET_PROTO_UNDEF`, and `IP_SET_EMIT_CREATE`; address family is irrelevant because matching happens at layer two. Create and ADT policies support generic hash options, timeouts, counters, comments, and skbinfo. Module init/fini register and unregister the type with an RCU barrier before unregister on unload.

## State and persistence behavior

Stored state is the generic hash table plus optional per-element extensions. The file keeps no file-local mutable state. Timeout, resize, bucket size, and init value behavior are inherited from the generated hash implementation.

## Dependencies and integration points

The file depends on Ethernet device/header helpers, ipset core, and the generic hash generator. It integrates with packet rules that can access `skb_mac_header`, and with userspace `ipset` commands through `IPSET_ATTR_ETHER`.

## Risks

Packet-path matching fails for non-Ethernet devices, skbs without a MAC header, short MAC headers, or zero MAC addresses. There is no IPv4/IPv6 split, so tests should not expect address-family filtering. Any caller using this on bridged or tunneled paths must ensure the skb still carries the intended Ethernet header.

## Test signals

Tests should create `hash:mac` sets, add/list/delete MAC addresses, reject zero and wrong-length addresses, match source and destination MACs from Ethernet skbs, verify non-Ethernet skb rejection, and exercise timeout/counter/comment/skbinfo extension behavior.
