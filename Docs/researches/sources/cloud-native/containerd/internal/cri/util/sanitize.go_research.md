# sources/cloud-native/containerd/internal/cri/util/sanitize.go

## Purpose
Redacts URL query parameters from errors, mainly to avoid leaking signed URL tokens or credentials in CRI/containerd error messages.

## Important APIs, Types, And Functions
`SanitizeError` detects `*url.Error` through `errors.As`, sanitizes its URL, and returns a `sanitizedError` wrapper when redaction changes the URL. `sanitizeURL` parses URLs and replaces every query value with `[REDACTED]`. `sanitizedError` implements `Error` and `Unwrap`.

## Control Flow
Non-URL or nil errors pass through unchanged. URL errors without query parameters also pass through. Wrapped URL errors preserve their original chain while changing the rendered message by replacing occurrences of the original URL.

## State And Persistence
No persistent state. The wrapper keeps the original error and sanitized URL.

## Dependencies And Integration Points
Uses `errors`, `net/url`, and `strings`. It integrates with logging and error-return paths where `errors.As` compatibility must be preserved.

## Risks
Malformed URLs are returned unchanged. Redacted marker values are URL-encoded as `%5BREDACTED%5D`, which is safe but may surprise string comparisons. Only query values are redacted; credentials in userinfo or paths are not.

## Test Signals
`sanitize_test.go` covers direct and wrapped URL errors, nil/non-URL passthrough, no-query passthrough, and unwrap behavior.
