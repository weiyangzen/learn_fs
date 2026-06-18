
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6.h

## Purpose

`ioam6.h` defines IPv6 IOAM option and trace header wire layouts, unavailable/default sentinel IDs, trace data size, and endian-sensitive trace-type bitfields. The complete 133-line file was read.

## Important APIs, Types, and Functions

Constants include unavailable/default IDs for 16/32/64-bit fields, `IOAM6_TYPE_PREALLOC`, and `IOAM6_TRACE_DATA_SIZE_MAX`. Structures are packed `ioam6_hdr` and `ioam6_trace_hdr`, with bitfield layouts for little- and big-endian builds and a flexible trace data array.

## Control Flow

No implementation flow exists. IPv6 IOAM insertion/parsing code reads or writes the option header, interprets namespace/type/nodelen/remlen/overflow fields, and appends trace data according to selected type bits.

## State and Persistence Behavior

No state is stored here. Per-namespace/default IDs and trace insertion policy live in IOAM kernel configuration and packet headers.

## Dependencies and Integration Points

It includes `asm/byteorder.h` and `linux/types.h`. It integrates with IPv6 Hop-by-Hop IOAM TLV handling, IOAM generic netlink namespace/schema config, and lightweight tunnel insertion.

## Risks and Edge Cases

Packed bitfields are endian-sensitive. Trace data is variable-length and bounded by 244 bytes. Risks include overflow flag handling, nodelen/remlen validation, reserved/unused bits, and alignment of packed network headers.

## Test Signals

IOAM packet tests should cover little/big endian bitfield expectations, preallocated trace insertion, overflow behavior, max trace data length, reserved-bit validation, and namespace/default ID encoding.
