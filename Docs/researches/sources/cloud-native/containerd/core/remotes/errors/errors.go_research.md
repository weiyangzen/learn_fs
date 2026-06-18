<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/errors/errors.go -->
# sources/cloud-native/containerd/core/remotes/errors/errors.go

## Purpose
Defines a serializable `ErrUnexpectedStatus` error for remote HTTP responses with unexpected status codes.

## Important APIs, Types, And Functions
- `ErrUnexpectedStatus` stores status string, status code, up to 64 KiB of response body, request URL, and request method.
- `Error()` formats a concise message including request method, URL, and status.
- `NewUnexpectedStatusErr(resp)` reads a bounded body and builds the error.
- `init` registers the error type with `typeurl` for wire serialization.

## Control Flow
When a response is unexpected, callers pass the response to `NewUnexpectedStatusErr`. The function drains at most 64 KiB from `resp.Body`, copies request metadata if available, and returns the structured error.

## State And Persistence
No mutable runtime state besides typeurl registration during init. Error values may be serialized by containerd APIs.

## Dependencies And Integration Points
Used by Docker remotes unexpected response helpers and tested through resolver/fetcher error paths. Integrates with `github.com/containerd/typeurl/v2`.

## Risks And Edge Cases
Calling `NewUnexpectedStatusErr` consumes response body content up to the limit. The captured request URL may include query data unless callers sanitize before exposing/logging; Docker request logging separately redacts URLs.

## Test Signals
No direct listed test, but resolver tests assert errors can be unwrapped as `remoteerrors.ErrUnexpectedStatus` and contain expected status codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/errors/errors.go -->
