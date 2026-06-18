# sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter.go

## Purpose
Formats daemon progress, status, error, and aux messages as Docker JSON stream records with CRLF framing.

## Important APIs, Types, And Functions
`FormatStatus` builds `jsonstream.Message{ID, Status}`. `FormatError` wraps ordinary errors or existing `jsonstream.Error` values and uses `compat.Wrap` to include both `error` and `errorDetail`. `jsonProgressFormatter.formatProgress` serializes progress and optional aux JSON. `NewJSONProgressOutput` returns a `progress.Output`. `progressOutput.WriteProgress` serializes updates under a mutex and optionally emits a final blank status. `AuxFormatter.Emit` writes aux messages and checks short writes.

## Control Flow
Progress messages with `Message` become status lines; otherwise fields are copied to `jsonstream.Progress` and serialized with action, id, and aux. Every successful message is terminated with `\r\n`.

## State And Persistence
State is limited to the output writer and a mutex protecting interleaved writes. No durable state is stored.

## Dependencies And Integration Points
Used by pull/build/push style daemon APIs that stream JSON to clients. Depends on `api/types/jsonstream`, daemon `progress`, and compatibility wrapping for legacy fields.

## Risks And Test Signals
Aux marshal failures in progress formatting return nil formatted bytes, which may become empty writes. Client compatibility depends on exact field names and CRLF framing. Tests cover status, error, JSON error, progress aux decoding, output construction, and aux emission.
