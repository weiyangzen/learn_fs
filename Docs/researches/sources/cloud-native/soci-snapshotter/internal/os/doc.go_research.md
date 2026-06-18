# sources/cloud-native/soci-snapshotter/internal/os/doc.go

Purpose: package documentation for internal OS utility functions.

Important APIs/types/functions: declares package `os` with import path `github.com/awslabs/soci-snapshotter/internal/os`.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies/integration points: documents helpers such as executable path sanitation used by configurable decompression setup.

Risks: package name shadows the standard library `os` in imports, so callers generally alias it as `intos` or similar.

Test signals: behavior is covered by `filepath_test.go`.
