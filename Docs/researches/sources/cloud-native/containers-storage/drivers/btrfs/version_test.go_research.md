# sources/cloud-native/containers-storage/drivers/btrfs/version_test.go

## Purpose
`version_test.go` checks that the Btrfs library version binding returns a meaningful positive value.

## Important APIs, Types, And Functions
`TestLibVersion` calls `btrfsLibVersion()` and reports an error when it is less than or equal to zero.

## Control Flow
The test runs only on Linux+cgo builds and validates the cgo header path at test time.

## State And Persistence
No persistent state is touched.

## Dependencies And Integration Points
It depends on the version helper in `version.go` and Btrfs headers.

## Risks
Older or unusual btrfs-progs headers that define no library version may make this test fail through the fallback `-1`.

## Test Signals
This is a narrow build-environment signal rather than a graphdriver behavior test.
