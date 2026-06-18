## sources/cloud-native/containers-storage/pkg/fileutils/exists_windows.go

Purpose: Windows implementation of existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: wraps `os.Stat` for follow behavior and `os.Lstat` for no-follow behavior.

State and persistence: read-only.

Dependencies and integration points: keeps fileutils API portable.

Risks: Windows symlink semantics and permission requirements differ from Unix; no fast faccess equivalent is used.

Test signals: shared tests apply when symlink support is available.
