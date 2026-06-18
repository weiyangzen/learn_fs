# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_host_process_windows.go

## Purpose
Windows HostProcess mounter implementation that bypasses CSI proxy clients and uses local filesystem/SMB wrappers.

## Important APIs, Types, and Functions
Defines `winMounter`, `NewWinMounter`, `SMBMount`, `SMBUnmount`, `Mount`, `Unmount`, `Rmdir`, `IsLikelyNotMountPoint`, `MakeDir`, `ExistsPath`, and mount.Interface stubs.

## Control Flow
`SMBMount` validates options, ensures parent directory, normalizes UNC path, checks/removes invalid existing global mapping, creates mapping with credentials, and creates a symlink from target to remote path. `SMBUnmount` reads the target link, checks duplicate mounts, removes global mapping if safe, then removes the target.

## State and Persistence
Creates Windows symlinks and SMB global mappings. Uses driver global mount path to find duplicate mounts.

## Dependencies
Depends on `pkg/os/filesystem`, `pkg/os/smb`, os symlinks, klog, and mount-utils interfaces.

## Integration Points
Selected by `NewSafeMounter(enableWindowsHostProcess=true, ...)` and connected to HostProcess manifests/options.

## Risks and Edge Cases
Duplicate detection scans a fixed kubelet path. Mapping removal errors are logged but unmount still removes target in some cases. Symlink creation fails if target already exists.

## Test Signals
No direct tests in this file; exercised indirectly by Windows node lifecycle and OS wrapper tests.
