# sources/cloud-native/moby/daemon/events_test.go

Purpose: daemon-level tests for event attribute handling and swarm event timestamp selection.

Important APIs and control flow: `TestLogContainerEventCopyLabels` subscribes to an event service, emits a container create event, and asserts container labels are not mutated with generated `image`/`name` fields while expected original labels are present. `TestLogContainerEventWithAttributes` passes explicit attributes and verifies container labels override colliding input keys while unrelated input attributes survive. `validateTestAttributes` reads one event with a 10 second timeout and checks expected key/value pairs. `TestEventTimestamp` table-tests create/update/remove/unknown/invalid swarm watch actions against `eventTimestamp`.

State, dependencies, and risks: tests construct minimal `Daemon`, `container.Container`, API config, and swarm metadata values. The label tests observe only selected keys and not the complete attribute map, so they do not assert generated `image` or trimmed `name`. Timestamp checks compare Unix seconds, not nanoseconds, and only assert non-zero for current-time fallbacks. These tests protect the main compatibility behavior around label copy semantics and event time source.
