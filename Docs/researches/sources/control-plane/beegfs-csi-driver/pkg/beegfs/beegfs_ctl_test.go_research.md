<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go

## Purpose
Unit tests for BeeGFS CTL argument construction and error types.

## Important APIs, Types, And Functions
Tests `constructSetPatternForVolumeArgs`, `constructCreateDirForVolumeArgs`, and error constructors `newCtlNotExistError`, `newCtlExistError`, `newCtlConnAuthError`.

## Control Flow
Table-driven tests compare generated argument slices for v7/v8 cases and verify typed errors preserve expected Error strings and unwrap with `errors.As`.

## State And Persistence
No persistent state and no real CLI execution.

## Dependencies And Integration Points
Uses Go testing, reflect.DeepEqual, and github.com/pkg/errors wrapping.

## Risks And Edge Cases
Coverage is limited to pure helpers. It does not validate `execBeeGFSCmd` output parsing against real BeeGFS binaries.

## Test Signals
Strong signal for command argument stability, especially v7/v8 flag differences and special-permission truncation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go -->
