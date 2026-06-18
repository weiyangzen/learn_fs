# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_windows.go

## Purpose
Primary Windows CSI proxy v1 mounter and safe mounter factory.

## Important APIs, Types, and Functions
Defines `CSIProxyMounter`, `csiProxyMounter`, `normalizeWindowsPath`, `SMBMount`, `SMBUnmount`, `Mount`, `Rmdir`, `IsLikelyNotMountPoint`, `MakeDir`, `ExistsPath`, `NewCSIProxyMounter`, and Windows `NewSafeMounter`.

## Control Flow
`SMBMount` validates credentials, ensures parent, resolves cluster DNS hostnames, normalizes/trims source, obtains root mapping path when cleanup is enabled, locks by mapping, calls CSI proxy `NewSmbGlobalMapping`, and writes a volume reference file. `SMBUnmount` reads the symlink target, decrements reference count, removes the global mapping when count reaches zero, then removes the target. Factory chooses HostProcess, CSI proxy v1, then v1beta fallback.

## State and Persistence
Maintains SMB global mappings, CSI proxy symlinks/directories, and optional reference files under `c:\csi\smbmounts`.

## Dependencies
Depends on CSI proxy filesystem/smb v1 clients, v1beta fallback, host-process mounter, mount-utils, utilexec, klog, os symlinks, DNS, and refcounter helpers.

## Integration Points
Used by driver startup on Windows; driven by deployment flags for HostProcess and mapping cleanup.

## Risks and Edge Cases
Reference file failure after mapping creation can leave mappings without tracked references. `os.Readlink(target)` assumes local process can read CSI proxy-created links. Locking is process-local only.

## Test Signals
Covered indirectly by Windows refcounter tests and node lifecycle tests; startup logs identify selected API version.
