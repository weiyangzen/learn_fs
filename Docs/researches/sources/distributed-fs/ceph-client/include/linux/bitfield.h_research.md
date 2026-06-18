# sources/distributed-fs/ceph-client/include/linux/bitfield.h

## Purpose
Provides type-safe bitfield extraction, preparation, replacement, and endian-aware helpers for shifted contiguous masks in registers and protocol fields.

## Important APIs, types, and functions
- `FIELD_MAX()`, `FIELD_FIT()`, `FIELD_PREP()`, `FIELD_PREP_CONST()`, `FIELD_GET()`, and `FIELD_MODIFY()` operate on compile-time constant masks with build-time validation.
- Internal checks validate nonzero masks, contiguous masks, value fit, and register type width.
- `field_multiplier()`, `field_mask()`, `field_max()`, and generated `u8/u16/u32/u64`, `le16/le32/le64`, and `be16/be32/be64` helpers support runtime field masks and endian conversions.
- `field_prep()` and `field_get()` allow non-constant masks while using checked constant paths when possible.

## Control flow and state
The macros compute the shift from the low set bit, validate mask shape and width, then mask/shift values into or out of registers. Endian helpers convert to/from CPU order around the same mask arithmetic. Compile-time errors are intentionally produced for invalid constant use.

## State and persistence behavior
No runtime state. The macros transform caller-owned register or protocol values. `FIELD_MODIFY()` mutates the pointed-to value in place.

## Dependencies and integration points
Depends on build bug helpers, compiler support, type checking, and byteorder conversion APIs. Heavily integrated with register definition headers, device drivers, networking, storage, and firmware parsing.

## Risks
Masks must be shifted and contiguous. Passing too-small register types or values that do not fit triggers compile errors for constants; runtime masks have less checking. Side effects in macro arguments should be avoided despite local temporaries in some helpers.

## Test signals
Compile-time negative tests for zero/non-contiguous masks, value overflow, and type width. Runtime tests for field prep/get/replace across u8/u16/u32/u64 and little/big endian fields, including non-constant masks.
