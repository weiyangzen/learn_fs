# sources/cloud-native/buildkit/source/http/transport.go

## Purpose
Wraps an HTTP transport so URLs with host `buildkit-session` can be served from BuildKit client session uploads instead of the network.

## Important APIs, Types, And Functions
- `newTransport(rt, sm, g)` returns a `sessionHandler`.
- `sessionHandler.RoundTrip` delegates ordinary hosts to the wrapped transport and intercepts `buildkit-session` GET requests.

## Control Flow
For non-session hosts, `RoundTrip` calls `rt.RoundTrip`. For `buildkit-session`, it rejects non-GET methods, selects a session caller with `sm.Any`, creates an `upload.New` reader for the URL, pipes upload content into an `io.Pipe`, and returns a synthetic `200 OK` response with streaming body.

## State And Persistence
No persisted state. It streams data from the session and does not set cache metadata itself.

## Dependencies And Integration Points
Integrates HTTP source downloads with BuildKit session upload service and the source handler's session group.

## Risks And Edge Cases
Uses `context.TODO` for session selection and upload creation rather than the request context. Response lacks headers such as filename, length, etag, or last-modified, so normal HTTP metadata reuse is unavailable for session uploads.

## Test Signals
No dedicated tests in the assigned file set; it is indirectly used if HTTP sources address `buildkit-session`.
