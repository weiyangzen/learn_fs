# sources/distributed-fs/ceph-client/include/linux/hw_bitfield.h

## Purpose
Adds helper macros for hardware registers whose upper 16 bits are a write-enable mask for lower 16-bit fields.

## APIs, Control Flow, and State
`FIELD_PREP_WM16(mask, val)` performs normal bitfield preparation for the low half and ORs `mask << 16` into the result. It uses `__BF_FIELD_CHECK()` to catch invalid masks or values. `FIELD_PREP_WM16_CONST()` provides constant-expression support by combining `FIELD_PREP_CONST()` with a build-time check that the mask fits in 16 bits. There is no runtime state or control flow beyond macro expansion.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/bitfield.h`, build bug helpers, and `U16_MAX`. It integrates with register programming code for mask-write hardware blocks. Risks are passing masks outside the lower half, assuming side effects in macro arguments are safe, or using the non-const macro in initializers. Test signals are compile-time assertion failures for bad masks/values and driver register write tests confirming upper-half write-enable bits are emitted.
