# sources/distributed-fs/ceph-client/net/ethtool/bitset.c

## Purpose
This file implements ethtool netlink bitset encoding, decoding, sizing, and update helpers. It supports both compact bitmap attributes and verbose per-bit nested attributes, and bridges the kernel's `unsigned long` bitmap representation with ethtool's `u32` netlink wire format.

## Important APIs, Types, And Functions
Public helpers include `ethnl_bitset_is_compact()`, `ethnl_bitset32_size()`, `ethnl_put_bitset32()`, `ethnl_update_bitset32()`, `ethnl_parse_bitset()`, `ethnl_bitset_size()`, `ethnl_put_bitset()`, and `ethnl_update_bitset()`. Internal helpers handle interval clearing, nonzero checks, value/mask updates, name-to-index lookup, verbose bit parsing, equality checks, and compact sanity validation.

## Control Flow
Output sizing and emission first account for the outer bitset nest and the `SIZE` attribute. Compact mode serializes raw `VALUE` and optional `MASK` arrays, trimming unused high bits in the last word. Verbose mode emits one nested bit per selected bit, optionally including index, name, and value flag. Parsing distinguishes verbose input from compact input. Compact updates validate size and array lengths, reject unsupported high-bit modifications, then apply value/mask bits. Verbose updates parse each named or indexed bit and either patch selected bits or replace the whole bitmap when `NOMASK` is present.

## State, Persistence, And Dependencies
The functions mutate caller-provided bitmaps and set caller-provided modification flags. There is no persistent state. Dependencies are generic netlink attribute parsing, `bitmap` helpers, `ETH_GSTRING_LEN` name arrays, endian-sensitive bitmap layout, and `netlink_ext_ack` diagnostics.

## Integration Points
Most ethtool netlink feature handlers use these helpers for link modes, device features, Wake-on-LAN modes, debug message classes, FEC modes, and other named capability sets. The header `bitset.h` exposes the API to sibling request files.

## Risks
The main risk is wire-format compatibility: compact `u32` arrays must behave identically on little-endian, 32-bit, and 64-bit big-endian systems. Verbose parsing must reject inconsistent index/name pairs and out-of-range indices. `NOMASK` semantics differ from masked updates, so missing clear behavior can accidentally preserve stale bits. Size estimation must match emission or netlink replies can fail with `-EMSGSIZE`.

## Test Signals
Tests should exercise compact and verbose input/output, named and indexed bits, `NOMASK` replacement, masked updates, out-of-range high bits, mismatched names, empty bitsets, non-multiple-of-32 sizes, and big-endian conversion wrappers.
