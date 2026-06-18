# sources/cloud-native/containers-storage/pkg/system/lstat_unix_test.go

Purpose: tests Unix `Lstat` success and failure behavior.

Important APIs, types, and functions: `TestLstat`.

Control flow: uses `prepareFiles` from other system tests, calls `Lstat` on an existing file and a missing path, and checks non-nil stat on success and nil stat plus error on failure.

State and persistence: creates temporary filesystem entries through shared helpers.

Dependencies and integration points: depends on `testing`; selected on Linux or FreeBSD. It validates `lstat_unix.go` and platform stat conversion.

Risks and edge cases: does not inspect fields of `StatT`; only checks presence/absence.

Test signals: confirms basic error contract for existing versus non-existing paths.
