# sources/distributed-fs/ipfs-kubo/test/cli/testutils/asserts.go

Purpose: provides a small assertion helper for tests that accept one of several possible error strings.

Important API: `AssertStringContainsOneOf(t *testing.T, str string, ss ...string)` loops over accepted substrings and returns as soon as one is present. If none match, it calls `t.Errorf` with the original string and accepted list.

Control flow: the helper is linear and non-fatal; the calling test continues after `t.Errorf` unless it has other fatal assertions. It imports only `strings` and `testing`.

State and persistence: no state or persistence.

Dependencies and integration points: used where external subsystems may produce semantically equivalent but textually different errors, for example resource-manager connection failures in rcmgr tests.

Risks and test signals: because the assertion is non-fatal, subsequent test code may run after failure. It also performs substring matching rather than structured error classification, so accepted message variants should remain narrow enough to avoid false positives.
