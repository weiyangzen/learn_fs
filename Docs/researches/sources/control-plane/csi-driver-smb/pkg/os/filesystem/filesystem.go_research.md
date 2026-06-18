# sources/control-plane/csi-driver-smb/pkg/os/filesystem/filesystem.go

## Purpose
Windows filesystem abstraction for HostProcess mounter operations.

## Important APIs, Types, and Functions
Functions include `ValidatePathWindows`, `PathExists`, `PathValid`, `Rmdir`, `IsMountPoint`, `IsSymlink`, plus helpers for invalid character, UNC, and absolute path checks.

## Control Flow
Validates Windows paths for length, absolute drive prefix, no UNC prefix, no invalid characters or `..`; checks existence with `os.Lstat`; validates remote paths through PowerShell `Test-Path`; removes paths with os remove calls; treats valid symlinks as mountpoints.

## State and Persistence
Mutates filesystem only through `Rmdir`; otherwise reads path state and executes PowerShell.

## Dependencies
Depends on os, regexp, strings, klog, and `util.RunPowershellCmd`.

## Integration Points
Used by HostProcess Windows mounter to create/check/remove local paths and verify SMB mapping targets.

## Risks and Edge Cases
Rejects UNC paths intentionally, so callers must normalize local paths first. `strings.Contains(path, "..")` can reject benign names. PowerShell output parsing is prefix-based.

## Test Signals
No mapped direct tests; exercised through HostProcess mounter and Windows integration.
