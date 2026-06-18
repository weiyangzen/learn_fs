# sources/cloud-native/buildkit/source/util/pathutil/pathutil_test.go

## Purpose
Tests filename sanitization behavior for HTTP/local source utility code.

## Important APIs, Types, And Functions
- `TestSafeFileName` uses table-driven cases with parallel subtests.

## Control Flow
The test builds common cases, appends OS-specific cases for Windows or non-Windows, then asserts `SafeFileName` output for each input.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses `runtime.GOOS`, `testing`, and `testify/require`.

## Risks And Edge Cases
The test intentionally documents OS-specific behavior for backslashes, so cross-platform changes to path handling will surface as test changes.

## Test Signals
Validates default `"download"` fallback and safe preservation of Unicode and spaces while rejecting empty, dot, dotdot, NUL, and control-character names.
