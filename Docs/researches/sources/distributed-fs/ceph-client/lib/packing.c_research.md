# sources/distributed-fs/ceph-client/lib/packing.c

## Purpose
Implements generic bitfield packing and unpacking between CPU-readable `u64` or C structures and packed byte buffers with hardware-specific layout quirks.

## APIs, Control Flow, and State
Exports `pack()`, `unpack()`, deprecated `packing()`, and field-array helpers for `packed_field_u8`/`u16`. `calculate_box_addr()` maps a logical byte of a big-number view to a physical buffer byte while honoring `QUIRK_LSW32_IS_FIRST` and `QUIRK_LITTLE_ENDIAN`; `QUIRK_MSB_ON_THE_RIGHT` reverses bits within bytes. `__pack()` and `__unpack()` iterate logical bytes from high to low significance, compute per-byte masks, project bits between packed buffer and unpacked value, and update only the target field. Public entry points validate bit order and width limits before modifying output. Field helpers read/write structure members by offset and size and call the raw pack/unpack routines for each declared field.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/packing.h`, bitops, `GENMASK`, `bitrev8`, and kernel module exports. Risks include overlapping field definitions, unsupported member sizes falling into the 64-bit default path, value truncation after warning, invalid width arguments, and layout quirk combinations being misunderstood by callers. Test signals are the KUnit packing suite, driver descriptor round trips, fuzzing of start/end bit ranges, and field-array pack/unpack equivalence tests.
