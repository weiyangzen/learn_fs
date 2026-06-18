# sources/cloud-native/containers-storage/pkg/longpath/longpath_test.go

Purpose: tests Windows long-path prefix conversion.

Important APIs, types, and functions: `TestStandardLongPath` and `TestUNCLongPath`.

Control flow: each test calls `AddPrefix` with a representative drive-letter or UNC path and compares with the expected long-path form using case-insensitive comparison.

State and persistence: no state or persistence; only string transformations are checked.

Dependencies and integration points: depends on `strings` and `testing`. It verifies behavior consumed by Windows filesystem helpers such as `ioutils.TempDir`.

Risks and edge cases: tests do not cover already-prefixed paths, relative paths, malformed UNC paths, or empty strings.

Test signals: confirms the two main supported Windows path shapes are mapped correctly.
