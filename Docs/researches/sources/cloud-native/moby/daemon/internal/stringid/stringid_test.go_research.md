# sources/cloud-native/moby/daemon/internal/stringid/stringid_test.go

## Purpose
Tests ID generation length, truncation behavior, digest-prefix handling, and numeric-only prefix detection.

## Important APIs, Types, And Functions
`TestGenerateRandomID` checks that `GenerateRandomID` returns `fullLen` characters. `TestTruncateID` covers empty strings, invalid short IDs, full IDs, `sha256:` digest strings, and very long strings. `TestAllNum` verifies mixed, alphabetic, and numeric-only inputs.

## Control Flow
All tests are table-driven except the random ID length check. Subtests name each truncation and numeric case.

## State And Persistence
No external state. Randomness is consumed from `crypto/rand`.

## Dependencies And Integration Points
Standard testing only. The tests support daemon assumptions that short IDs are display prefixes and that generated IDs are 64 hex characters.

## Risks And Test Signals
The random generation test does not assert non-numeric truncated prefixes even though production guarantees it. Collision behavior is out of scope. The important signal is backward-compatible truncation of digest strings by stripping the algorithm before shortening.
