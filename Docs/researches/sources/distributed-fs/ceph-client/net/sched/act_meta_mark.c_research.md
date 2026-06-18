# sources/distributed-fs/ceph-client/net/sched/act_meta_mark.c

## Purpose

`act_meta_mark.c` registers the IFE metadata handler for `skb->mark`. It lets the `ife` tc action carry a packet mark across an Inter-FE encapsulation and restore it on decode.

## Important APIs, types, and functions

The file is built around one `struct tcf_meta_ops`, `ife_skbmark_ops`, with `metaid = IFE_META_SKBMARK`, `metatype = NLA_U32`, and user-facing name `skbmark`. `skbmark_encode()` reads `skb->mark` and delegates wire formatting to `ife_encode_meta_u32()`. `skbmark_decode()` reads a network-order 32-bit value and writes `skb->mark`. `skbmark_check()` delegates optional presence/value checks to `ife_check_meta_u32()`. Module init and exit call `register_ife_op()` and `unregister_ife_op()`.

## Control flow

When an IFE action is configured to export this metadata, the core IFE code invokes `check_presence`, then `encode`, and later `decode` on a receiving endpoint. The module itself has no packet scheduling decision; it is a metadata codec plugged into the IFE action registry.

## State and persistence

Persistent state is only the registered `tcf_meta_ops` module object. Per-packet state is the `skb->mark` value and the temporary encoded metadata payload supplied by the IFE core. There is no per-net IDR, RCU parameter block, or durable configuration in this file.

## Dependencies and integration points

It depends on `net/tc_act/tc_ife.h` helpers for allocation, validation, encode/decode support, and module aliasing through `MODULE_ALIAS_IFE_META("skbmark")`. Integration is with the tc `ife` action and consumers that classify, route, firewall, or policy-route based on `skb->mark`.

## Risks and edge cases

The decode path assumes the IFE core has validated the metadata length and alignment before handing `data` to the codec. Endianness is the primary correctness detail: encoded values are interpreted in network order with `ntohl()`. Regressions can silently alter downstream policy decisions because `skb->mark` is widely reused by netfilter, routing, and tc classifiers.

## Test signals

Useful coverage is `tc action ife encode type skbmark` paired with decode on another interface, checking that `skb->mark` survives encapsulation. Negative tests should cover invalid metadata length through the IFE core, module autoload via the `skbmark` alias, and filter behavior that proves the restored mark is visible to later tc or netfilter rules.
