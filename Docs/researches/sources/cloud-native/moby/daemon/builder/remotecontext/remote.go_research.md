# sources/cloud-native/moby/daemon/builder/remotecontext/remote.go

## Purpose
Downloads remote Docker build contexts and validates response content type before exposing a readable body. It also classifies HTTP errors into Docker `errdefs`.

## Important APIs, Types, And Functions
Defines `maxPreambleLength`, `acceptableRemoteMIME`, lazy `mimeRe`, `downloadRemote`, `GetWithStatusError`, `inspectResponse`, and `selectAcceptableMIME`.

## Control Flow
`downloadRemote` calls `GetWithStatusError`, then `inspectResponse`, and wraps the reconstructed body with a closer that closes the original response. `GetWithStatusError` maps DNS misses and HTTP 400/401/403/404/default failures to specific `errdefs`. `inspectResponse` reads up to 100 bytes, rejects empty bodies, replays the preamble with `io.MultiReader`, sniffs missing/octet-stream content, and accepts only tar/compressed/text/plain/octet-stream MIME matches.

## State And Persistence
No persistent state. It consumes bytes from network responses but reconstructs the reader so callers see the full body.

## Dependencies And Integration Points
Uses `http.Get`, `lazyregexp`, `ioutils.NewReadCloserWrapper`, `detectContentType`, and Docker error classification. It feeds higher-level build-context selection between Dockerfile text and archive streams.

## Risks And Test Signals
Accepting regex substrings can tolerate parameters but also depends on MIME spelling. DNS error classification is specific to non-timeout `net.DNSError`. Tests cover MIME acceptance, body preservation, empty responses, downloads via `httptest`, and status error bodies.
