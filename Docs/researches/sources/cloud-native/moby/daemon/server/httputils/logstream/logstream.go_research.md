# sources/cloud-native/moby/daemon/server/httputils/logstream/logstream.go

## Purpose
Writes container log messages as raw or multiplexed byte streams for traditional Docker log responses.

## Important APIs, Types, And Functions
`Write(ctx, w, msgs, config, mux)` streams logs. `rfc3339NanoFixed` defines fixed-width timestamps. `attrsByteSlice` formats sorted log attrs as query-escaped `key=value` pairs. `byKey` sorts attrs.

## Control Flow
The function writes status 200 and flushes immediately, sets stdout/stderr/system error writers, optionally wrapping them with stdcopy multiplex writers, then loops over messages until cancellation or channel close. Error messages are written to system error stream. Details and timestamps are prepended before routing by source.

## State And Persistence
Only response bytes are written. `attrsByteSlice` sorts the message's `Attrs` slice in place, mutating message metadata order.

## Dependencies And Integration Points
Used by container logs route for raw/multiplexed stream formats. Depends on stdcopy, daemon stdcopymux, backend log options, and ioutils flushing.

## Risks And Edge Cases
Response headers are committed before log processing, so later errors are in-band. Writer errors are ignored. Attribute sorting mutation is documented as acceptable because nothing else should use the attrs afterward.

## Test Signals
No direct listed tests. Log API tests should validate mux headers, timestamp format, detail attr encoding, stdout/stderr filtering, and in-band error text.
