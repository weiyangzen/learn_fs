# sources/distributed-fs/ceph-client/include/linux/bcd.h

## Purpose
Provides binary-coded decimal conversion helpers for kernel code that reads or writes BCD-encoded hardware or firmware fields.

## Important APIs, types, and functions
- `bcd2bin(x)` and `bin2bcd(x)` choose compile-time constant conversions when possible and otherwise call `_bcd2bin()` or `_bin2bcd()`.
- `bcd_is_valid(x)` validates that both nibbles are decimal digits.
- `const_bcd2bin()`, `const_bin2bcd()`, and `const_bcd_is_valid()` implement simple constant expressions.

## Control flow and state
No runtime state. The macros use `__builtin_constant_p` to select constant arithmetic for constant inputs, reducing call overhead and enabling initializer use.

## State and persistence behavior
No persistence. Callers usually translate persistent RTC, firmware, or device-register fields into normal integers and back.

## Dependencies and integration points
Depends on compiler attributes. Integrated by RTC, firmware, NVRAM, and device drivers with BCD registers.

## Risks
`bin2bcd()` assumes values are in a representable two-digit range unless the caller enforces bounds. `bcd_is_valid()` is separate and must be used before trusting external BCD input.

## Test signals
Test all valid `00..99` conversions, invalid nibbles, constant-expression use in initializers, and runtime conversion paths.
