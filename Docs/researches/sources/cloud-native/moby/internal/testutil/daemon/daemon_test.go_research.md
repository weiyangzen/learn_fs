# sources/cloud-native/moby/internal/testutil/daemon/daemon_test.go

## Purpose
Regression tests for sanitizing test names into safe filesystem paths.

## Important APIs, Types, And Functions
- `TestSanitizeTestName` runs subtests whose names contain quotes, spaces, dots, dashes, underscores, slashes, and path traversal-like text, then compares `sanitizedTestName(t)` with expected paths.

## Control Flow
Each table row runs as a subtest, calls `sanitizedTestName`, converts expected slash separators through `filepath.FromSlash`, and reports mismatch with `t.Errorf`.

## State And Persistence
No persistent state; it only uses subtest names.

## Dependencies And Integration Points
Tests `sanitizePathComponent`/`sanitizedTestName`, which are used by daemon constructor paths and artifact tooling safety.

## Risks And Edge Cases
The table captures important path edge cases such as `../foo`, bare quotes, and leading dashes. It does not test non-ASCII names.

## Test Signals
Passing means daemon test directories will not contain shell-hostile quotes or path traversal components derived from test names.
