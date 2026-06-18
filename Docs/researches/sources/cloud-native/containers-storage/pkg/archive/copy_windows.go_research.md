<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_windows.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_windows.go

Purpose: Windows path normalization shim for archive copy code.

Important APIs/types/functions: `normalizePath`.

Control flow: converts slash separators to Windows separators via `filepath.FromSlash`.

State/persistence: none.

Dependencies/integration: used by `copy.go` before path cleaning, destination symlink resolution, split logic, and archive copy decisions.

Risks/test signal: Windows path handling differs for volumes, long paths, and trailing separators; this shim only normalizes separators. Coverage comes from Windows archive/copy tests outside this subset and compile-time integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_windows.go -->
