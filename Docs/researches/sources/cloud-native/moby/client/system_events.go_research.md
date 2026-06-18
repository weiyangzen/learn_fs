# sources/cloud-native/moby/client/system_events.go

## Purpose
Implements streaming daemon events with timestamp/filter query construction and content-type aware JSON stream decoding.

## APIs, Types, And Functions
`EventsListOptions` contains `Since`, `Until`, and `Filters`; `EventsResult` exposes message and error channels; `Client.Events` starts the stream. `buildEventsQueryParams` parses timestamps using `timestamp.GetTimestamp` and applies filters.

## Control Flow, State, And Integration
`Events` creates channels, starts a goroutine, builds query parameters, sets Accept headers for JSON lines, NDJSON, and JSON sequence, calls `GET /events`, and decodes messages until decoder error or context cancellation. The returned stream reflects live daemon event state and requires caller cancellation.

## Risks And Test Signals
Risks include goroutine leaks, blocked message consumers, incorrect timestamp reference times, content-type mismatch, and EOF/error channel semantics. Integration points are daemon event streaming and filter encoding shared by many Docker clients.
