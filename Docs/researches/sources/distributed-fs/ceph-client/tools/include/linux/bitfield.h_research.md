# sources/distributed-fs/ceph-client/tools/include/linux/bitfield.h

## Purpose

This header supplies kernel-style bitfield extraction, preparation, validation, and typed endian-aware field helpers for tools code.

## APIs, State, and Dependencies

Core macros include `FIELD_MAX`, `FIELD_FIT`, `FIELD_PREP`, and `FIELD_GET`, backed by `__bf_shf` and `__BF_FIELD_CHECK`. The checks enforce constant nonzero masks, field fit for constant values, register type width, and contiguous power-of-two mask layout. The header also declares compile-time error helpers and builds typed operations for little-endian, big-endian, and native u8/u16/u32/u64 fields. It depends on build-bug, kernel, and byteorder headers. It has no runtime state.

## Risks and Test Signals

The macros deliberately fail compilation for bad masks or oversized constant values; nonconstant misuse may become runtime truncation. Tests should include compile-fail coverage for invalid masks, runtime extraction/prep for several field positions, and endian typed helper checks.
