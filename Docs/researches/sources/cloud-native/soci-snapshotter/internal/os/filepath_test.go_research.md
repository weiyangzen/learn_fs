# sources/cloud-native/soci-snapshotter/internal/os/filepath_test.go

Purpose: unit tests for executable path sanitation.

Important APIs/types/functions: `TestSanitizeExecutablePath` is table-driven and creates temporary files, directories, and symlinks to exercise sanitizer outcomes.

Control flow: each case builds a path under `t.TempDir`, calls `SanitizeExecutablePath`, checks errors using `errors.Is`, and compares returned path against expected resolved output.

State and persistence: creates temporary executable/non-executable files and symlinks with per-test cleanup through the testing package.

Dependencies/integration points: validates behavior that compression configuration relies on before executing custom decompression binaries.

Risks: test expectations depend on Unix permission semantics and symlink behavior. It does not cover relative paths or every rejected metacharacter individually.

Test signals: good coverage for success, symlink resolution, path-not-found, directory, permission, and injection-character rejection.
