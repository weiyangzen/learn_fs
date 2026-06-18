# sources/cloud-native/moby/daemon/server/httputils/json-seq.go

## Purpose
Creates JSON stream encoders for Docker API streaming responses, including RFC-style JSON text sequences.

## Important APIs, Types, And Functions
`EncoderFn` is the encoder function type. `NewJSONStreamEncoder(w, contentType)` selects encoding based on media type. `jsonSeq.Encode` prefixes records with ASCII record separator `0x1E` before JSON encoding.

## Control Flow
For `types.MediaTypeJSONSequence`, the helper returns a `jsonSeq` encoder. For NDJSON, JSON, JSON Lines, and unknown content types, it returns the standard `json.Encoder.Encode`.

## State And Persistence
Encoders write to the supplied `io.Writer`; no other state persists.

## Dependencies And Integration Points
Used by JSON log streaming. Depends on Docker API media type constants and Go JSON encoding.

## Risks And Edge Cases
Unknown content types silently fall back to newline-delimited JSON. JSON-seq relies on `json.Encoder` to add the line feed after each record.

## Test Signals
No direct tests listed; log stream tests or API content negotiation tests should validate wire format.
