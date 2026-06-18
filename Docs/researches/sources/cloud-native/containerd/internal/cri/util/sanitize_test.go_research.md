# sources/cloud-native/containerd/internal/cri/util/sanitize_test.go

## Purpose
Tests URL-query redaction behavior for `SanitizeError`.

## Important APIs, Types, And Functions
Test cases create `url.Error` values with sensitive query strings, wrapped errors, non-URL errors, nil errors, and no-query URLs.

## Control Flow
The tests call `SanitizeError`, inspect concrete wrapper type for direct URL errors, compare rendered messages, and verify `errors.As` and `errors.Unwrap` still expose the original URL error.

## State And Persistence
Only in-memory error objects are used.

## Dependencies And Integration Points
Uses `errors`, `fmt`, `net/url`, `testing`, `testify/assert`, and `testify/require`.

## Risks
Tests do not cover malformed URLs, userinfo credentials, repeated query values, fragments, or multiple URL errors in one chain.

## Test Signals
Strong coverage for the intended signed-URL query redaction path and error-chain preservation.
