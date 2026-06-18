# sources/distributed-fs/ceph-client/net/sched/act_meta_skbtcindex.c

## Purpose

`act_meta_skbtcindex.c` provides the IFE metadata codec for `skb->tc_index`. It preserves the legacy tc index/classification field across IFE encapsulation.

## Important APIs, types, and functions

`ife_skbtcindex_ops` registers `metaid = IFE_META_TCINDEX`, `metatype = NLA_U16`, name `tc_index`, and alias `tcindex`. `skbtcindex_encode()` reads `skb->tc_index` and encodes it with `ife_encode_meta_u16()`. `skbtcindex_decode()` stores an `ntohs()` decoded value back into `skb->tc_index`. `skbtcindex_check()` delegates presence checks to `ife_check_meta_u16()`.

## Control flow

The IFE action core selects this codec when configured for tc index metadata. Encode runs before the IFE frame is emitted; decode runs after metadata parsing on the receiving side and mutates the skb field for subsequent tc processing.

## State and persistence

The module owns only the registered `tcf_meta_ops`. The persistent packet metadata is carried externally in the IFE payload; after decode, state is just the 16-bit `skb->tc_index` value. No per-action parameters or per-net namespaces are allocated here.

## Dependencies and integration points

It uses the common IFE u16 helper set and participates in the tc action module registry. The restored value integrates with filters and legacy classifiers that still inspect `skb->tc_index`.

## Risks and edge cases

The encoder casts the field through a local `u32` while using u16 IFE helpers; correctness depends on the helper truncating/validating according to the u16 metadata type. As with the other metadata codecs, malformed payload length must be rejected by shared IFE validation before `decode` dereferences `data`.

## Test signals

Configure IFE metadata `tcindex`, send packets with a known `tc_index`, and confirm a receiver-side classifier sees the restored value. Include values near the 16-bit boundary, metadata omission cases, and module autoload by alias.
