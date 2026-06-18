# sources/control-plane/rook/pkg/util/display/bytes.go

## Purpose
`bytes.go` formats byte counts for display and converts between bytes and megabytes.

## Important APIs, Types, and Functions
Constants define binary units from `KiB` through `EiB`. `BytesToString()` chooses the largest unit threshold and formats two decimals for units larger than bytes. `BToMb()` rounds bytes to MiB. `MbTob()` multiplies MiB by 1024 squared.

## Control Flow, State, and Persistence
The functions are pure. `BToMb()` uses floating-point division and `math.Round()`.

## Dependencies and Integration Points
It depends on `fmt` and `math`. It integrates with CLI/status display paths that need human-readable storage sizes.

## Risks
`BToMb()` rounds rather than floors, which may surprise capacity calculations if used beyond display. `BytesToString()` reports binary units but `BToMb()` names the unit `Mb`, which can be ambiguous. Very large values are capped by uint64 and formatted as EiB.

## Test Signals
`bytes_test.go` checks one value per unit, zero, max uint64, and 50 MiB round-trip conversions.
