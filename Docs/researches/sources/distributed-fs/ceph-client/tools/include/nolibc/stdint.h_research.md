# sources/distributed-fs/ceph-client/tools/include/nolibc/stdint.h

## Purpose
Defines fixed-width integer, pointer-width, least/fast-width, and limit macros for nolibc.

## APIs, Types, and Functions
Typedefs `uint8_t/int8_t`, `uint16_t/int16_t`, `uint32_t/int32_t`, `uint64_t/int64_t`, `size_t`, `ssize_t`, `uintptr_t`, `intptr_t`, `ptrdiff_t`, least/fast aliases, and max-width aliases. It also defines integer limit macros such as `INT8_MIN`, `UINT64_MAX`, `SIZE_MAX`, and related constants.

## Control Flow, State, and Persistence
There is no runtime behavior. The header establishes compile-time integer ABI used by every other nolibc header.

## Dependencies and Integration
Depends on compiler predefined `__SIZE_TYPE__` and conventional Linux userspace integer sizes. It integrates with `std.h`, binary parsers, syscall wrappers, and formatting code.

## Risks and Test Signals
Risks are unsupported targets with nonstandard integer widths, incomplete C standard macro coverage, and mismatch between `ssize_t` and kernel ABI on unusual platforms. Test signals are static assertions for sizes and limits, 32/64-bit builds, and compiling code that uses each typedef family.
