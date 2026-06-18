# sources/cloud-native/nydus-snapshotter/pkg/resolve/resolver.go

## Purpose
Provides a higher-level resolver that turns an image reference and digest into an authenticated HTTP reader for the resolved blob.

## Important APIs, Types, And Functions
`Resolver`, `NewResolver`, `Resolver.Resolve`, and `newRetryHTTPClient`.

## Control Flow
`Resolve` parses a Docker reference, reconstructs a go-containerregistry reference from domain/path, builds a keychain from labels, asks a shared transport resolver for a URL and authenticated round tripper, creates a retryable GET request, executes it, requires HTTP 200, and returns the response body.

## State And Persistence
`Resolver` holds a transport resolve pool. No files are written; callers own closing the returned body.

## Dependencies And Integration Points
Uses repository auth labels through `pkg/auth`, transport resolution through `pkg/utils/transport`, go-containerregistry reference/keychain concepts, distribution reference parsing, and hashicorp retryable HTTP.

## Risks And Edge Cases
Only HTTP 200 is accepted, so partial-content/range responses are not expected here. Non-OK responses return without draining/closing the body in this function. Digest is passed to transport resolver but not independently verified while streaming.

## Test Signals
No direct tests in this subset. Stargz resolver tests cover a related transport resolver pattern with range reads.
