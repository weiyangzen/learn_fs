# sources/control-plane/ceph-csi/internal/kms/kms_util.go

## Purpose
`kms_util.go` provides a shared config conversion helper for integer options.

## Important APIs, Types, And Functions
`setConfigInt(option *int, config map[string]any, key string)` reads `key`, requires the JSON-decoded value to be `float64`, converts it to `int`, and stores it in `option`.

## Control Flow And State
Missing keys return an `errConfigOptionMissing`-wrapped error and leave the option unchanged. Non-`float64` values return `errConfigOptionInvalid`. Valid values update the pointed-to integer.

## State And Persistence Behavior
The function has no persistent state. It mutates only the caller-provided option pointer.

## Dependencies And Integration Points
The helper depends on error sentinels from `vault.go`. KMIP timeout parsing uses this helper because JSON config numbers decode to `float64`.

## Risks And Edge Cases
The conversion truncates fractional values without validation. It requires `float64`, so manually built configs using `int` fail even though the logical value is numeric. It does not check range before callers cast to narrower types.

## Test Signals
`kms_util_test.go` covers valid float64, invalid string, and missing key behavior. It does not cover fractional values, negative numbers, overflow, or nil option pointers.
