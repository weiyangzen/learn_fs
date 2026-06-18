# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/errors/errors.go

## Purpose
Defines a structured error type for unexpected HTTP statuses from registry API requests.

## Important APIs, Types, And Functions
`ErrUnexpectedStatus` and `NewUnexpectedStatusErr(resp *http.Response)` are the full API.

## Control Flow
`NewUnexpectedStatusErr` reads up to 64KB from the response body, captures status text/code, request method, and request URL, and returns an `ErrUnexpectedStatus`. `Error` formats the method, URL, and status.

## State And Persistence
No state. The response body is consumed when creating the error.

## Dependencies And Integration Points
Used by resolver, fetcher, pusher, and authorizer fallback logic. Authorizer inspects this concrete type to handle OAuth POST fallback statuses.

## Risks And Edge Cases
Because the body is read and stored, callers must not expect to reuse the response body after creating the error. Body capture is capped, avoiding unbounded memory use but truncating very large server messages.

## Test Signals
Fetcher and pusher tests indirectly verify error conversion and body inclusion in logs/messages.
