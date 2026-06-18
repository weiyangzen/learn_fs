# sources/control-plane/ceph-csi/internal/kms/kms_util_test.go

## Purpose
`kms_util_test.go` tests the integer config conversion helper used by KMS providers.

## Important APIs, Types, And Functions
`TestSetConfigInt` defines table cases for valid, invalid, and missing values and calls `setConfigInt`.

## Control Flow And Test Behavior
Subtests run in parallel. The valid case supplies `1.0` and expects success. Error cases check `errors.Is` against `errConfigOptionInvalid` or `errConfigOptionMissing`.

## Dependencies And Integration Points
The test depends on KMS config error sentinels from `vault.go` and `testify/require`.

## Risks And Edge Cases
All cases share the same `option` variable pointer, and subtests run in parallel, which can race. The assertions for error cases check that the option is not equal to zero rather than checking it remained at its prior value.

## Test Signals
The test covers the common JSON-number path and two error categories. It does not cover fractional truncation, negative values, overflow, or parallel safety.
