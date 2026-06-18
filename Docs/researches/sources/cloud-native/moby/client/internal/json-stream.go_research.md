# sources/cloud-native/moby/client/internal/json-stream.go

## Purpose
`json-stream.go` selects the correct decoder for Docker JSON stream media types and provides an RS-filtering reader for RFC 7464 JSON text sequences.

## Important APIs, Types, And Functions
Types: `DecoderFn`, `rsFilterReader`. Functions: `NewJSONStreamDecoder`, `NewRSFilterReader`, `Read`.

## Control Flow
`NewJSONStreamDecoder` wraps JSON sequence input with `NewRSFilterReader`; the reader repeatedly strips ASCII RS bytes, avoids returning `(0, nil)` after consuming separators, and preserves EOF semantics when filtered data remains.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `io`, `slices`, `github.com/moby/moby/api/types`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Filtering mutates the read buffer slice in place, so callers rely on standard `io.Reader` ownership rules. A bug here would break pull/push progress decoding for JSON sequence responses.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
