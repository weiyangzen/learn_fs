# sources/cloud-native/moby/daemon/server/httputils/logstream/json_logstream.go

## Purpose
Writes container log messages as a JSON stream, supporting stdout/stderr filtering, optional details, partial-log metadata, timestamps, and in-band errors.

## Important APIs, Types, And Functions
`WriteJSON` streams `backend.LogMessage` values to an HTTP response. `jsonLogWriter`, `newJSONLogWriter`, `jsonLogMessage`, and `(*jsonLogWriter).write` handle record conversion and encoding.

## Control Flow
`WriteJSON` sends status 200 immediately, wraps the response in a write flusher, picks a JSON stream encoder based on response content type, then loops until context cancellation or channel close. Messages with `Err` are always written with an error field; stdout/stderr messages are filtered by `ContainerLogsOptions`. Writer details include attrs only when requested.

## State And Persistence
Writes streaming response bytes and flushes headers; no daemon state is changed. Once the header is written, later errors are encoded in-band rather than returned as HTTP errors.

## Dependencies And Integration Points
Used by container logs route when JSON format is requested. Depends on backend log types, `httputils.NewJSONStreamEncoder`, and ioutils write flushing.

## Risks And Edge Cases
`write` ignores encoder errors, so client disconnects may not surface here. `Line` is converted to string and assumes text-oriented JSON output. Headers are committed before the backend channel is drained.

## Test Signals
No direct listed tests. Container logs API tests should validate media type negotiation, filtering, detail attrs, metadata, and error records.
