# sources/cloud-native/moby/daemon/builder/remotecontext/mimetype.go

## Purpose
Centralizes MIME type detection for remote build-context preambles, normalizing Go's sniffed content type to the bare media type without parameters.

## Important APIs, Types, And Functions
Defines constants `mimeTypeTextPlain` and `mimeTypeOctetStream`, and unexported `detectContentType(c []byte) (string, error)`.

## Control Flow
`detectContentType` passes bytes to `http.DetectContentType`, then uses `mime.ParseMediaType` to strip parameters such as charset and return only the MIME token.

## State And Persistence
No mutable or persistent state.

## Dependencies And Integration Points
Called by `inspectResponse` in `remote.go` when the server omits `Content-Type` or reports `application/octet-stream`. It relies on Go's built-in sniffing behavior.

## Risks And Test Signals
Sniffing only sees the supplied preamble, so short or ambiguous content can be classified as octet-stream. `mimetype_test.go` verifies plain text normalization.
