# sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter_test.go

## Purpose
Tests `NewStdoutWriter` and `NewStderrWriter` JSON formatting and returned write sizes.

## Important APIs, Types, And Functions
`TestStreamWriterStdout` and `TestStreamWriterStderr` write `"content"` into a `bytes.Buffer`, assert no error, assert the returned size equals the original content length, and compare exact JSON output with `streamNewline`.

## Control Flow
Each test creates a writer, performs one write, then inspects the resulting buffer string.

## State And Persistence
State is only an in-memory buffer.

## Dependencies And Integration Points
Uses `gotest.tools` assertions. These tests protect the client-visible JSON stream format and stderr color escape sequence encoding.

## Risks And Test Signals
Short-write/error behavior is not covered. The exact JSON expectations make field names, escaping of ANSI sequences, and CRLF framing explicit compatibility signals.
