## sources/cloud-native/containers-storage/pkg/fsutils/fsutils_linux.go

Purpose: Linux filesystem feature detection for directory entry `d_type` support.

Important APIs/types/functions: `SupportsDType`, `locateDummyIfEmpty`, and `iterateReadDir`.

Control flow: if target directory is empty, creates a temporary dummy file so at least one dirent is visited. It reads raw dirents with `unix.ReadDirent`, stops early on `DT_UNKNOWN`, and reports whether all visited entries exposed known type values.

State and persistence: may create and remove a temporary dummy file in the checked directory.

Dependencies and integration points: used by storage drivers that need reliable d_type support. Depends on unsafe casting of raw dirent buffers.

Risks: requires write permission on empty directories; failure to create dummy file makes feature detection fail. Dirent parsing trusts `Reclen` values from the kernel.

Test signals: no selected tests for this file.
