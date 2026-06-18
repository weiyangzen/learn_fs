## sources/cloud-native/containers-storage/pkg/chunked/internal/path/path_test.go

Purpose: unit tests for chunked internal path normalization and digest-based regular-file path generation.

Important APIs/types/functions: `TestCleanAbsPath` and `TestRegularFilePathForValidatedDigest`.

Control flow: table-driven tests feed empty, relative, absolute, repeated slash, `.` and `..` paths into `CleanAbsPath`. Digest tests parse a valid SHA256 and a SHA512 and assert path generation or error.

State and persistence: no persistent state; all tests are pure.

Dependencies and integration points: validates helpers used by fd-safe filesystem operations and flat output mapping in `storage_linux.go`.

Risks: tests do not check malformed digest strings directly because parsing is done before calling the helper; they also do not validate OS-specific path separator differences.

Test signals: strong signal for traversal normalization; local execution was blocked because `go` is unavailable.
