# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmark.c

## Purpose

`ip_set_hash_ipmark.c` implements the `hash:ip,mark` ipset type. It stores a packet IP address paired with the skb mark, with an optional create-time mark mask. The type is usable from both packet path lookups and netlink userspace add/delete/test operations, and it delegates generic hash-table creation, lookup, timeout, extension, resize, and listing mechanics to `ip_set_hash_gen.h`.

## Important APIs, types, and functions

The file defines `struct hash_ipmark4_elem` with `ip` and `mark`, and `struct hash_ipmark6_elem` with an IPv6 `union nf_inet_addr` and `mark`. `hash_ipmark{4,6}_data_equal()` compares stored keys; `hash_ipmark{4,6}_data_list()` serializes elements as `IPSET_ATTR_IP` plus `IPSET_ATTR_MARK`; and `hash_ipmark{4,6}_data_next()` records restart state for bounded IPv4 range expansion. The generated variants expose `hash_ipmark_create` through the `ip_set_type` record. Packet path functions `hash_ipmark{4,6}_kadt()` read `skb->mark`, apply `h->markmask`, read source or destination IP according to `IPSET_DIM_ONE_SRC`, and call the generated ADT function. Userspace functions `hash_ipmark{4,6}_uadt()` validate netlink attributes, parse extensions, apply the mark mask, and run add/delete/test operations.

## Control flow

Module initialization registers `hash_ipmark_type` with family `NFPROTO_UNSPEC`, dimension two, and features `IPSET_TYPE_IP | IPSET_TYPE_MARK`. The generic hash include creates IPv4 and IPv6 implementations based on `HTYPE`, `MTYPE`, `HOST_MASK`, and `IP_SET_HASH_WITH_MARKMASK`. Packet lookups are direct: construct an element from packet fields, mask the mark, then dispatch through `set->variant->adt[adt]`. Userspace IPv4 operations optionally expand `IPSET_ATTR_IP_TO` or `IPSET_ATTR_CIDR`; when the operation exceeds `IPSET_MAX_RANGE`, the current element is copied into `h->next` and `-ERANGE` signals retry. IPv6 deliberately rejects IP ranges and accepts only `/128` CIDR.

## State and persistence behavior

Persistent state lives in the generic hash set allocation: the table, element extensions, timeout metadata, bucket size, init value, resize policy, and the `next` cursor used across retried range additions. The module itself keeps no global mutable state beyond registration. Mark masking is create-time set state and is applied both to packet lookups and userspace entries, so stored keys match runtime packet interpretation.

## Dependencies and integration points

This file depends on the ipset core, `ip_set_hash.h`, `pfxlen.h`, netlink attribute helpers, skb IP address helpers, and the generic hash generator. It integrates with xtables/nftables match/set paths through `kadt`, with userspace `ipset` netlink commands through `uadt`, and with kernel module loading through `MODULE_ALIAS("ip_set_hash:ip,mark")`.

## Risks

The special invalid element check rejects only the all-zero IP plus all-zero masked mark case, so callers must understand that a zero mark can still be valid with a nonzero IP. IPv4 range expansion is bounded by `IPSET_MAX_RANGE`; large ranges depend on retry correctness and `h->next`. IPv6 range support is intentionally absent. Any mismatch between markmask creation policy and userspace expectations can make rules appear not to match because marks are normalized before storage and lookup.

## Test signals

Useful tests create IPv4 and IPv6 `hash:ip,mark` sets with and without `markmask`, add/test/delete exact entries, exercise IPv4 `IP_TO` and `CIDR` expansion including retry-sized ranges, verify `/128`-only IPv6 behavior, check zero IP/zero mark rejection, list elements and confirm netlink mark serialization, and run packet-path tests where `skb->mark` is masked before matching.
