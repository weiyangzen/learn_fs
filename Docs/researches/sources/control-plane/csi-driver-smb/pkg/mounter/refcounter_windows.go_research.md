# sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows.go

## Purpose
Windows-only reference counter for SMB global mappings.

## Important APIs, Types, and Functions
Defines `basePath`, `mutexes`, `lock`, `getRootMappingPath`, `incementVolumeIDReferencesCount`, `decrementVolumeIDReferencesCount`, `getVolumeIDReferencesCount`, and `getMd5`.

## Control Flow
Normalizes UNC paths to server/share mapping keys, serializes operations per mapping key, writes one MD5-named reference file per volume ID, removes it on decrement, and counts files to decide when no references remain.

## State and Persistence
Persists reference files under `c:\csi\smbmounts\<server>\<share>`. In-memory mutexes serialize per-process access only.

## Dependencies
Uses os, filepath, strings, sync.Map, md5, and Windows path conventions.

## Integration Points
Used by Windows CSI proxy v1 mounter when `RemoveSMBMappingDuringUnmount` is enabled from the v1.9 manifest flag.

## Risks and Edge Cases
Function names contain misspellings but are internal. Reference files can become stale after process crash. `os.MkdirAll(path, os.ModeDir)` lacks normal permission bits. MD5 is for naming only.

## Test Signals
`refcounter_windows_test.go` covers locking, root path parsing, increment/decrement, idempotent increments, and duplicate decrement errors.
