# sources/cloud-native/containers-storage/pkg/archive/archive_windows.go

## Purpose
This Windows platform file adapts archive paths and metadata to Windows filesystem semantics.

## Important Functions
`fixVolumePathPrefix` adds long-path prefixes through `longpath.AddPrefix`. `getWalkRoot` joins source and include paths normally. `CanonicalTarNameForPath` rejects relative paths containing forward slashes and converts Windows separators to POSIX tar slashes. `chmodTarEntry` adds execute bits and clamps permission bits to `0755` while preserving non-permission mode bits. Special-device functions are no-ops because Windows lacks Unix device/inode concepts here. `getFileUIDGID` returns zero IDs. `handleLLink` uses `os.Link`.

## Control Flow and State
The file mostly transforms paths and tar header modes. Extraction of block/char/fifo and chmod are no-ops. Persistent effects are ordinary file creation and hardlinks through generic extraction.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `fmt`, `os`, `filepath`, `strings`, `idtools`, and `longpath`. The functions are invoked from `archive.go` through platform-neutral helper names.

## Risks and Edge Cases
Rejecting forward slashes protects assumptions that Windows input paths use backslashes, but can surprise callers passing POSIX-like relative paths. Permission normalization is lossy by design. No-op device handling means archives containing Unix special files cannot be faithfully restored on Windows.

## Test Signals
`archive_windows_test.go` validates canonical path conversion and directory suffix behavior. One invalid-destination copy test is skipped as currently failing, which marks an unresolved Windows behavior gap.
