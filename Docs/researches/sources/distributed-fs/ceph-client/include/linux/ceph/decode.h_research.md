# sources/distributed-fs/ceph-client/include/linux/ceph/decode.h

## Purpose

`decode.h` provides low-level little-endian encode/decode primitives and bounds-checking helpers for Ceph wire buffers. It also handles encoded strings, timespec conversion, entity address encoding, and versioned encoding blocks.

## Important APIs, Types, and Functions

Important helpers include `ceph_decode_64/32/16/8`, `ceph_decode_copy`, `ceph_has_room`, `ceph_decode_*_safe`, skip macros for primitive/string/set/map forms, `ceph_extract_encoded_string()`, `ceph_decode_timespec64()`, `ceph_encode_timespec64()`, banner address helpers, `ceph_decode_entity_addr()`, `ceph_decode_entity_addrvec()`, `ceph_encode_entity_addr()`, `ceph_encode_*`, `ceph_encode_filepath()`, `ceph_encode_string()`, `ceph_start_encoding()`, and `ceph_start_decoding()`.

## Control Flow

Encode/decode flow is pointer-cursor based: functions read or write at `*p` and advance it. Safe macros check `end` and branch to caller-supplied error labels. Versioned decode reads current version, compatible version, and length before allowing unsafe field reads within the validated block.

## State and Persistence Behavior

No state is stored here. The helpers define how persistent and network Ceph records are serialized. Allocated strings from `ceph_extract_encoded_string()` become caller-owned heap state.

## Dependencies and Integration Points

It depends on unaligned access helpers, `ERR_PTR`, slab allocation, time types, and `ceph/types.h`. It is used by monitor map, OSD map, messenger address, and protocol decoder implementations.

## Risks and Edge Cases

Unsafe decode helpers do not check bounds. `ceph_encode_filepath()` and `ceph_encode_string()` use `BUG_ON` on overflow, making caller length calculation critical. Timespec encoding truncates seconds to 32 bits with a documented year-2106 overflow. String allocation must account for `len + 1` overflow risk in implementation assumptions.

## Test Signals

Fuzz truncated buffers, verify safe macros branch on short input, test version/compat rejection, round-trip entity addresses and strings, cover zero-length strings, and run endian/unaligned access tests.
