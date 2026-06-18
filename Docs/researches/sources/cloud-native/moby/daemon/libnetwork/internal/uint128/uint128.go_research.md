# sources/cloud-native/moby/daemon/libnetwork/internal/uint128/uint128.go

## Purpose
Provides a minimal unsigned 128-bit arithmetic helper for IPv6 address math and subnet accounting without pulling in big integers.

## Important APIs, Types, And Functions
- `Uint128` stores high and low 64-bit words.
- `From16` converts a big-endian 16-byte address to `Uint128`; `Fill16` writes back.
- `From` constructs from two words.
- `Add`, `Sub`, `Lsh`, `Rsh`, `And`, and `Not` implement basic arithmetic/bit operations.
- `Uint64` returns the low word; `Uint64Sat` saturates to max uint64 if the high word is non-zero.

## Control Flow
Addition and subtraction use `math/bits` to propagate carries/borrows. Shifts split the operation across `hi` and `lo`, with special handling for counts greater than 64. Operations intentionally wrap like unsigned arithmetic.

## State And Persistence
The type is immutable by convention: methods return new values and do not mutate receivers. No persistent state exists.

## Dependencies And Integration Points
Used by `ipbits` for IPv6 address addition, subtraction, and bitfield extraction, and by default IPAM pool status to represent very large address counts before saturation.

## Risks
Shift behavior at exactly 64 uses expressions with `64-n`; in Go, shifting by zero is valid, but callers should treat this as a low-level helper with limited validation. `Uint64` silently drops high bits; callers needing capacity reporting should use `Uint64Sat`.

## Test Signals
There is no direct test file in this subset, but `ipbits_test.go` and default IPAM status paths exercise the helper indirectly for IPv6 arithmetic and saturation-sensitive subnet counts.
