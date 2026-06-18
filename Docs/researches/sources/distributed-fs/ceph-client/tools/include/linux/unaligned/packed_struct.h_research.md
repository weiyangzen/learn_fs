# sources/distributed-fs/ceph-client/tools/include/linux/unaligned/packed_struct.h

## Purpose
Provides the low-level CPU-endian unaligned access backend used by `linux/unaligned.h`, using packed wrapper structs to express potentially unaligned typed memory.

## APIs, Types, and Functions
Defines packed wrappers `struct __una_u16`, `struct __una_u32`, and `struct __una_u64`, plus `__get_unaligned_cpu16/32/64()` and `__put_unaligned_cpu16/32/64()` inline helpers.

## Control Flow, State, and Persistence
Each getter casts the address to a packed wrapper pointer and returns the member; each setter assigns through the packed wrapper. There is no retained state and no branchy control flow. The behavior relies on compiler support for packed member access lowering to safe byte-wise or unaligned-capable loads/stores.

## Dependencies and Integration
Depends on kernel-style `u16/u32/u64` aliases and the `__packed` attribute from `linux/compiler.h`. It is intentionally private to the unaligned helper layer and not a general structure-serialization API.

## Risks and Test Signals
Risks are compiler or architecture behavior around packed unaligned access, strict-aliasing surprises if used outside its intended wrapper pattern, and caller buffer size mistakes. Test signals are generated assembly inspection on strict-alignment architectures, round-trip tests for 16/32/64-bit values at misaligned addresses, and sanitizer-backed parser tests.
