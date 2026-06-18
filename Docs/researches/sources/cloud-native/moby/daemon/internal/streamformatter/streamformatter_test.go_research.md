# sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter_test.go

## Purpose
Verifies JSON stream formatter output for status, errors, progress, output initialization, and aux messages.

## Important APIs, Types, And Functions
Tests call `FormatStatus`, `FormatError`, `jsonProgressFormatter.formatProgress`, `jsonProgressFormatter.formatStatus`, `NewJSONProgressOutput`, and `AuxFormatter.Emit`. `cmpJSONMessageOpt` ignores the derived deprecated `ProgressMessage` field when comparing decoded messages.

## Control Flow
Tests compare exact JSON strings for status/errors and decode progress JSON into `jsonstream.Message` to compare structured fields, including raw aux JSON.

## State And Persistence
All state is an in-memory `bytes.Buffer`. No external files or daemon state are involved.

## Dependencies And Integration Points
Uses `google/go-cmp`, `gotest.tools`, and `jsonstream` types. These tests protect client-facing JSON wire compatibility.

## Risks And Test Signals
Exact string checks are sensitive to JSON field ordering, but Go's marshal order for struct fields is stable. Tests do not cover concurrent `WriteProgress` locking or short-write behavior. Strong signal is preserved CRLF framing and legacy `error` plus `errorDetail` fields.
