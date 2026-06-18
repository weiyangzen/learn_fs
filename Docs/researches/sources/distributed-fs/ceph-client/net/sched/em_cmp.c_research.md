
# sources/distributed-fs/ceph-client/net/sched/em_cmp.c

## Purpose

`em_cmp.c` implements the basic comparison ematch. It compares an 8-, 16-, or 32-bit value at a configured packet layer and offset against a configured operand using equality, less-than, or greater-than semantics.

## Important APIs, Types, and Functions

The module consumes `struct tcf_em_cmp` as fixed-size ematch data. `em_cmp_match()` obtains a base pointer with `tcf_get_base_ptr()`, validates the offset/width with `tcf_valid_offset()`, reads unaligned big-endian data, optionally transforms endian order when `TCF_EM_CMP_TRANS` is set, applies a mask, and evaluates the operand. `em_cmp_ops` registers `TCF_EM_CMP`.

## Control Flow

There is no custom change callback; the ematch core copies the fixed data after checking `datalen`. Match returns false on missing base pointer, invalid offset, unsupported alignment, or unsupported operand. Valid reads dispatch by alignment and then compare.

## State and Persistence Behavior

All state is the copied `tcf_em_cmp` payload held by the ematch core. The module has no per-net or global runtime state beyond registration.

## Dependencies and Integration Points

It depends on ematch core data handling, packet-layer base helpers, skb bounds checking, and unaligned access helpers. It is used inside ematch trees by classifiers that support `TCA_EMATCH_TREE`.

## Risks and Edge Cases

Endian transformation is opt-in and only meaningful for 16/32-bit reads. Offset validation must remain paired with the chosen alignment or malformed skbs could be read out of bounds. Unsupported alignment/operator values fail closed.

## Test Signals

Test all alignments, EQ/LT/GT operands, masks, transform flag, invalid layer/offset, packet truncation, and inverted/combined ematch-tree behavior.
