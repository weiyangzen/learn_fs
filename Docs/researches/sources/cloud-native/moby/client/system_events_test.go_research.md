# sources/cloud-native/moby/client/system_events_test.go

## Purpose
Tests event-stream option errors, daemon error propagation, request construction, and streaming decode behavior.

## APIs, Types, And Functions
The tests are `TestEventsErrorInOptions`, `TestEventsErrorFromServer`, and `TestEvents`. They use `Client.Events`, `EventsListOptions`, filters, `events.Message`, JSON encoding, and channel assertions.

## Control Flow, State, And Integration
Tests force timestamp parse errors before HTTP, mock server errors from `/events`, and emit JSON event messages for the streaming path. They read from returned message and error channels to verify startup and decode behavior.

## Risks And Test Signals
Signals include early option validation, method/path correctness, filter/timestamp query output, and stream channel semantics. Context cancellation and alternate event content types remain important integration risks.
