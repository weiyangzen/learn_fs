
# sources/distributed-fs/ceph-client/net/sched/em_u32.c

## Purpose

`em_u32.c` implements a small ematch based on the `cls_u32` 32-bit key format. It tests one `struct tc_u32_key` against packet data, using the skb network header or an ematch packet-info pointer as the base.

## Important APIs, Types, and Functions

`em_u32_match()` is the only runtime function. It computes the pointer from `skb_network_header()` or `info->ptr`, adds `(info->nexthdr & key->offmask)` when packet info is supplied, then adds `key->off`, validates four bytes, and applies the classic `((word ^ val) & mask) == 0` predicate. `em_u32_ops` declares fixed `datalen = sizeof(struct tc_u32_key)` and registers `TCF_EM_U32`.

## Control Flow

There is no custom change callback; the ematch core validates and copies fixed-size key data. Runtime matching fails closed on invalid offset and returns the mask comparison result otherwise.

## State and Persistence Behavior

All persistent state is the copied `tc_u32_key` in `m->data`. The module has no dynamic per-instance allocations and no global state besides registration.

## Dependencies and Integration Points

It depends on the ematch core, `tc_u32_key` layout from packet classifier headers, skb network-header helpers, optional `tcf_pkt_info`, and skb offset validation.

## Risks and Edge Cases

The code dereferences a `__be32 *` directly after validation, so alignment assumptions follow architecture/network-header behavior. `info->nexthdr & offmask` makes behavior dependent on callers that populate packet info. Endianness follows the u32 key values supplied by userspace.

## Test Signals

Test network-header base matches, packet-info base matches, offmask behavior, truncated skbs, exact and masked values, and ematch inversion/boolean composition.
