<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/packing.h -->
# sources/distributed-fs/ceph-client/include/linux/packing.h

## Purpose
This header declares generic bitfield pack/unpack helpers for hardware protocols/register layouts whose bit numbering, byte order, or word ordering differs from native C layout. It also supplies compile-time validation for table-driven field mappings.

## Important APIs, types, and functions
`GEN_PACKED_FIELD_STRUCT()` defines `struct packed_field_u8` and `struct packed_field_u16`. `PACKED_FIELD()` maps a packed bit range to an unpacked structure field. Validation macros include `CHECK_PACKED_FIELD()`, overlap/order checks, size checks, generated `CHECK_PACKED_FIELDS_1..50`, and `CHECK_PACKED_FIELDS()`. Quirks are `QUIRK_MSB_ON_THE_RIGHT`, `QUIRK_LITTLE_ENDIAN`, and `QUIRK_LSW32_IS_FIRST`. APIs include `packing()`, `pack()`, `unpack()`, `pack_fields_u8/u16()`, `unpack_fields_u8/u16()`, and generic `pack_fields()`/`unpack_fields()`.

## Control flow
Single-field callers use `pack()`/`unpack()` or the lower-level `packing()` with an operation enum. Table-driven callers declare packed-field arrays, then `pack_fields()` or `unpack_fields()` first performs compile-time validation of field order, overlap, storage size, and packed-buffer bounds, then dispatches by `_Generic()` to the u8 or u16 implementation.

## State and persistence
The header stores no state. Field mapping arrays are static caller data, and packed buffers are caller-owned hardware/protocol byte arrays.

## Dependencies and integration points
It depends on array size, bitops, build-bug assertions, min/max, offsets, and integer types. It integrates with network switch/PHY/register drivers and any subsystem needing endian/bit-order-quirked serialization.

## Risks and test signals
Risks include incorrect bit numbering, field overlap, unsupported field storage sizes, field arrays larger than 50 without regenerating macros, pbuf length not compile-time constant for generic helpers, quirk misselection, and silent truncation if unpacked field sizes are wrong. Test pack/unpack round trips across all quirks, ascending and descending field tables, compile-time failures for overlap/out-of-range fields, u8/u16 table dispatch, and hardware register golden vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/packing.h -->
