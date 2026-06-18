# File Research: sources/block-storage/libblkid-rs/src/macros.rs

Purpose: Provides internal macros for C string conversion, errno handling, pointer handling, enum conversion, and flag-set construction.

Key macros:
- `str_ptr_to_owned!`
- `str_ptr_with_size_to_owned!`
- `errno!`
- `errno_ptr!`
- `option_ptr!`
- `errno_with_ret!`
- `consts_enum_conv!`
- `flags!`

Implementation notes:
- `errno!` treats `0` as success, negatives as `LibErr`, and positives as `PositiveReturnCode`.
- `errno_ptr!` maps null pointers to `LibErr(0)`.
- `consts_enum_conv!` creates enum-to-integer and integer-to-enum conversions.
- `flags!` stores flag members in a `HashSet`.

Notable risks:
- `flags!::TryFrom` iterates over every bit and tries to convert `(1 << i) & v`; unset bits become `0`, which usually causes `InvalidConv`.
- `str_ptr_with_size_to_owned!` requires a NUL-terminated byte slice of exactly `size`; it is fragile if libblkid reports sizes excluding the terminator.
- Generated enums implement `Into` rather than `From`, which is less idiomatic and prevents blanket conversion ergonomics.
