# sources/control-plane/csi-driver-smb/pkg/os/smb/smb_test.go

## Purpose
Windows unit test for HostProcess SMB duplicate mount detection.

## Important APIs, Types, and Functions
Tests `CheckForDuplicateSMBMounts` with a non-existing directory.

## Control Flow
Calls the function and compares expected false result plus expected Windows open error string.

## State and Persistence
No created state.

## Dependencies
Uses testing and fmt; expected error text is Windows-specific.

## Integration Points
Protects one failure path used by HostProcess unmount logic.

## Risks and Edge Cases
Coverage is very narrow and error-string matching can vary by OS/localization.

## Test Signals
Passing test confirms missing duplicate scan root returns an error.
