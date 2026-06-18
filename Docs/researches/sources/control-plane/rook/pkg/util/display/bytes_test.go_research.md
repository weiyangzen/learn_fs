# sources/control-plane/rook/pkg/util/display/bytes_test.go

## Purpose
This file validates byte formatting and byte/MiB conversion helpers.

## Important APIs, Types, and Functions
`TestBytesToString()` asserts formatted strings for byte, KiB, MiB, GiB, TiB, PiB, EiB, zero, max uint64, `BToMb()`, and `MbTob()`.

## Control Flow, State, and Persistence
The test is pure and deterministic.

## Dependencies and Integration Points
It uses `math.MaxUint64` and testify. It protects user-facing size display.

## Risks
Boundary values just below each unit threshold are not covered. Rounding behavior in `BToMb()` is covered only for an exact 50 MiB value.

## Test Signals
Signals include two-decimal binary formatting and max uint64 rendering as `16.00 EiB`.
