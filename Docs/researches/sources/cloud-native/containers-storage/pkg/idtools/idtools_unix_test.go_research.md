## sources/cloud-native/containers-storage/pkg/idtools/idtools_unix_test.go

Purpose: Unix tests for mkdir-and-chown helpers and subid parser comment/blank-line handling.

Important APIs/types/functions: `TestMkdirAllAs`, `TestMkdirAllAndChownNew`, `TestMkdirAs`, `TestParseSubidFileWithNewlinesAndComments`, plus helpers `buildTree`, `readTree`, and `compareTrees`.

Control flow: builds temporary directory trees with specified ownership, calls public mkdir helpers, reads ownership recursively with `unix.Stat`, and compares expected maps. The parser test writes a synthetic subuid file with comments/blank lines and verifies only the requested range is returned.

State and persistence: creates temp trees and performs real `os.Chown`, which may require privileges or be affected by user namespace mappings.

Dependencies and integration points: validates `mkdirAs` behavior used by storage directory creation.

Risks: ownership tests can be environment-sensitive in rootless or restricted CI. No tests for group/user lookup fallback.

Test signals: strong for ownership semantics; local execution unavailable because `go` is missing.
