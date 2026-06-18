
# sources/distributed-fs/ceph-client/net/sched/em_nbyte.c

## Purpose

`em_nbyte.c` implements an ematch that compares an arbitrary byte pattern at a configured layer and offset inside the skb. It is a simple fixed-pattern matcher for short packet fields that are not necessarily 32-bit aligned.

## Important APIs, Types, and Functions

`struct nbyte_data` wraps `struct tcf_em_nbyte` and a flexible pattern. `em_nbyte_change()` validates payload size and copies the header plus pattern. `em_nbyte_match()` resolves the configured base layer with `tcf_get_base_ptr()`, adds the offset, validates the requested length with `tcf_valid_offset()`, and compares bytes with `memcmp()`. `em_nbyte_ops` registers `TCF_EM_NBYTE`.

## Control Flow

Configuration rejects payloads shorter than the header or shorter than header plus declared pattern length. Matching fails closed on missing layer base or out-of-bounds range; otherwise exact byte equality returns true.

## State and Persistence Behavior

All state is copied into `m->data` and freed by the ematch core because this module has no custom destroy callback. No global state is kept besides registration.

## Dependencies and Integration Points

It depends on ematch core default data management, packet base helpers, skb bounds checking, and netlink payload layout from `tc_em_nbyte.h`.

## Risks and Edge Cases

The declared length controls both allocation and match bounds. Large lengths are bounded only by the netlink attribute size and memory allocation. Matching is exact; masks or partial wildcards require other ematches.

## Test Signals

Test valid pattern matches at network/transport layers, truncated packets, invalid layer, zero-length or malformed config, dump through ematch core, and inversion/boolean composition in ematch trees.
