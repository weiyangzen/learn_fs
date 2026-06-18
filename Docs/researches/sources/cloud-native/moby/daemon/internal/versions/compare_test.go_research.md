# sources/cloud-native/moby/daemon/internal/versions/compare_test.go

## Purpose
Tests numeric dot-separated version comparison ordering.

## Important APIs, Types, And Functions
`assertVersion` wraps private `compare`. `TestCompareVersion` covers equal versions, trailing zero equivalence, longer/shorter comparisons, and multi-component ordering.

## Control Flow
The test calls `compare` with fixed pairs and expected -1, 0, or 1 results, failing immediately on mismatch.

## State And Persistence
No state.

## Dependencies And Integration Points
Standard testing only. It validates the assumptions behind public comparison helpers.

## Risks And Test Signals
No tests cover invalid components, prerelease strings, whitespace, or leading signs. The key compatibility signal is that `"1.0.0"` equals `"1"` while `"1.0.1"` is greater.
