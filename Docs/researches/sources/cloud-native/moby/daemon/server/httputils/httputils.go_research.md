# sources/cloud-native/moby/daemon/server/httputils/httputils.go

## Purpose
Defines core HTTP utilities for Docker API handlers: API function signature, hijacking, stream closing, JSON content validation/decoding/encoding, form parsing, API version context access, and content-type matching.

## Important APIs, Types, And Functions
`APIVersionKey`, `APIFunc`, `HijackConnection`, `CloseStreams`, `CheckForJSON`, `ReadJSON`, `WriteJSON`, `ParseForm`, `VersionFromContext`, and `matchesContentType` are the main APIs.

## Control Flow
`CheckForJSON` allows missing content type only when there is no body. `ReadJSON` validates content type, treats nil/empty body as no-op, decodes one JSON document, closes the body, maps invalid JSON to invalid-parameter errors, and rejects extra JSON documents/content using `dec.More`. `ParseForm` ignores MIME-only parse errors for compatibility. `CloseStreams` prefers `CloseWrite` when available.

## State And Persistence
`ReadJSON` consumes and closes request bodies. `ParseForm` populates request form fields. `WriteJSON` writes response headers and body. No persistent daemon state is touched.

## Dependencies And Integration Points
Used by most API routers. Depends on daemon errdefs, Go HTTP/JSON/mime packages, and stream interfaces.

## Risks And Edge Cases
`VersionFromContext` panics if the context value under `APIVersionKey` is not a string. `ReadJSON`'s use of `dec.More` detects extra tokens in common object cases but is a subtle JSON decoder API choice. Hijack assumes the writer implements `http.Hijacker`.

## Test Signals
`httputils_test.go` covers content type matching and JSON body decoding for nil, empty, valid, whitespace, extra content, and invalid JSON cases.
