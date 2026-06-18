# sources/control-plane/csi-driver-smb/pkg/os/smb/smb.go

## Purpose
Windows SMB global mapping wrapper for HostProcess mode.

## Important APIs, Types, and Functions
Functions include `IsSmbMapped`, `NewSmbGlobalMapping`, `RemoveSmbGlobalMapping`, `GetRemoteServerFromTarget`, and `CheckForDuplicateSMBMounts`.

## Control Flow
Uses PowerShell commands with environment variables for user input to check mapping status, create mappings with credentials and privacy, remove mappings, read symlink targets, and scan kubelet globalmount links for duplicate remote server usage.

## State and Persistence
Creates/removes Windows SMB global mappings and reads symlink state under the driver global mount directory.

## Dependencies
Depends on PowerShell SMB cmdlets, os symlinks, filepath, klog, and `util.RunPowershellCmd`.

## Integration Points
Used by HostProcess `winMounter` for SMB mapping lifecycle.

## Risks and Edge Cases
PowerShell/SMB cmdlet availability is required. Duplicate detection compares remote server strings case-sensitively. Directory scan failures abort duplicate detection.

## Test Signals
`smb_test.go` covers duplicate mount error behavior for a missing directory.
