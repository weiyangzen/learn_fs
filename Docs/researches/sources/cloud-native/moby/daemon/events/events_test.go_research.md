# sources/cloud-native/moby/daemon/events/events_test.go

Purpose: unit tests for the daemon events service in `daemon/events/events.go`.

Important APIs and control flow: `TestEventsLog` subscribes two listeners, logs one container event, and asserts subscriber count, buffered length, action, actor ID, and image attribute from both channels. `TestEventsLogTimeout` leaves a subscriber unread and verifies publishing returns within one second, proving pubsub timeout behavior prevents a blocked listener from stalling logging. `TestLogEvents` writes more than `eventsLimit`, checks that only the most recent 256 remain, subscribes, emits ten more events, and verifies buffered/live ordering. The three `loadBufferedEvents` tests parse CLI-like fixtures with `testutils.Scan` and assert since/until filtering and the historical behavior that no buffered events are returned when both times are zero.

State, dependencies, and risks: tests use real pubsub channels and timeouts, so timing assumptions matter but durations are conservative. Fixtures depend on timestamp parsing and event output scanning. Test signals are strong for buffer size/order and publication liveness, but topic filtering and metrics decrement edge cases are not directly covered here.
