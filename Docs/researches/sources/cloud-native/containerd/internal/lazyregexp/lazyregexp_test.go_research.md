# sources/cloud-native/containerd/internal/lazyregexp/lazyregexp_test.go

## Purpose
Tests lazy regexp compilation behavior in the test environment.

## Important APIs, Types, And Functions
`TestCompileOnce` has invalid and valid subtests using `New` and `MatchString`.

## Control Flow
The invalid case expects a panic from `New("[")` because tests compile early. The valid case checks a simple match.

## State And Persistence
Only in-memory regexp state.

## Dependencies And Integration Points
Uses Go testing.

## Risks
Does not prove production lazy behavior where invalid regex panics on first use rather than construction. Does not test concurrent first use.

## Test Signals
Confirms the test-mode early compile guard works.
