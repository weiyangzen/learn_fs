# sources/cloud-native/moby/daemon/internal/containerfs/rm_windows.go

## Purpose
Provides the Windows implementation of container filesystem removal.

## APIs, Control Flow, and Integration
`EnsureRemoveAll(path string)` is a direct alias to `os.RemoveAll`. Unlike the Unix implementation, it performs no mount recursion, busy retry, or race-specific handling.

## State, Dependencies, and Risks
State and effects are exactly `os.RemoveAll`. The risk is behavioral divergence from Unix: missing-path handling and transient filesystem races depend entirely on Go's Windows removal behavior. Shared non-Darwin tests cover missing path/file/dir removal, but Windows-specific busy or locked-file behavior is not tested here.
