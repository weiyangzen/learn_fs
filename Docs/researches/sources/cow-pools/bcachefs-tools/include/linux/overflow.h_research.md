# File Research: sources/cow-pools/bcachefs-tools/include/linux/overflow.h

This header provides overflow-safe arithmetic and size calculation helpers. It defines type min/max machinery, `check_add_overflow()`, `check_sub_overflow()`, `check_mul_overflow()`, wrapping add/sub/mul helpers, `check_shl_overflow()`, `overflows_type()`, and `castable_to_type()`.

It also defines saturating `size_mul()`, `size_add()`, `size_sub()`, and allocation-size macros `array_size()`, `array3_size()`, `flex_array_size()`, `struct_size()`, and `struct_size_t()`. On-stack flexible-array helpers `DEFINE_RAW_FLEX()` and `DEFINE_FLEX()` require compile-time constant counts.

The return values of overflow checks are marked must-check through an inline wrapper, reducing accidental ignored overflow detection.
