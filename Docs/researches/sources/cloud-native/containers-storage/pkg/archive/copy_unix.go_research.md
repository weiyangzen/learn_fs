<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_unix.go

Purpose: Unix path normalization shim for archive copy code.

Important APIs/types/functions: `normalizePath`.

Control flow: returns the input path unchanged because Unix paths already use the process-native separator conventions expected by `filepath`.

State/persistence: none.

Dependencies/integration: called throughout `copy.go` before path cleaning, splitting, symlink resolution, and copy decisions. The Windows counterpart adapts paths for Windows semantics.

Risks/test signal: behavior is intentionally minimal; correctness is validated indirectly by the Unix copy matrix tests in `copy_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix.go -->
