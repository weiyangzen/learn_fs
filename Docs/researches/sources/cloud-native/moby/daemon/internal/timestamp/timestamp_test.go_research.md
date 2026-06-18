# sources/cloud-native/moby/daemon/internal/timestamp/timestamp_test.go

## Purpose
Provides broad compatibility tests for timestamp parsing accepted by Docker log/event APIs.

## Important APIs, Types, And Functions
`TestParse` covers `timestamp.Parse` against a fixed reference time. `TestParseUnixTimestamp` covers the lower-level Unix timestamp parser. Assertions compare UTC RFC3339Nano strings or Unix seconds/nanoseconds.

## Control Flow
Table-driven cases include full and partial RFC3339 with/without zones, date-only inputs, Unix timestamps, fractional nanoseconds with padding/truncation, relative durations, invalid strings, whitespace, and empty values.

## State And Persistence
No state beyond fixed test data.

## Dependencies And Integration Points
Uses `gotest.tools` assertions and imports the package externally as `timestamp_test`, exercising the public API rather than internals.

## Risks And Test Signals
The suite assumes UTC reference zone, so local-zone parsing paths are only partially represented. Strong signals include rejecting whitespace-wrapped numeric timestamps, preserving fractional nanosecond rules, and treating negative durations as future offsets relative to the reference.
