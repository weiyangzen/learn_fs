<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath.go -->
# sources/cloud-native/moby/pkg/longpath/longpath.go

Purpose: handles Windows long path prefixing while remaining harmless on other platforms. Important APIs are `AddPrefix` and `MkdirTemp`. Control flow adds `\\?\` for Windows paths that are not already prefixed, handles UNC paths with the correct long UNC form, and delegates temp-directory creation after prefixing. State is filesystem path strings and created temp directories. Dependencies are `os`, `runtime`, and string manipulation. Risks include subtle Windows path forms, already-prefixed paths, and UNC normalization. Test signal is in `longpath_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath.go -->
