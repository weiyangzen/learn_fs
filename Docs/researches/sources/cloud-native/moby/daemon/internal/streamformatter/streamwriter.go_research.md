# sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter.go

## Purpose
Provides stdout and stderr writers that transform raw byte chunks into JSON stream messages for Docker API clients.

## Important APIs, Types, And Functions
`streamWriter` wraps an `io.Writer` and a `lineFormat` function. `Write` formats the input into a `jsonstream.Message{Stream: ...}`, writes the formatted bytes, returns `io.ErrShortWrite` on partial formatted writes, and reports the original input length on success. `NewStdoutWriter` passes content through; `NewStderrWriter` wraps content in red ANSI color escape sequences.

## Control Flow
Each write becomes one JSON message terminated by CRLF. There is no line splitting; the caller's byte chunk is the stream payload.

## State And Persistence
No persistent state. The only mutable state belongs to the wrapped writer.

## Dependencies And Integration Points
Used by daemon code that needs to expose stdout/stderr as JSON stream messages, especially non-multiplexed HTTP responses. Relies on `jsonstream.Message` and `FormatError`.

## Risks And Test Signals
Short writes return the formatted byte count rather than input bytes, which differs from the success path. Stderr coloring is embedded in JSON and assumes terminal-compatible clients. Tests verify exact stdout/stderr JSON.
