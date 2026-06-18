# sources/cloud-native/moby/integration/system/event_test.go

## Purpose
Tests daemon events for exec lifecycle, nonblocking event API behavior, and avoiding duplicate volume create events when a volume is later mounted by a container.

## Important APIs, Types, And Functions
- `TestEventsExecDie` subscribes to `exec_die` events for a container and checks event fields after `ExecStart`.
- `TestEventsNonBlocking` performs raw `GET /events` and asserts it returns quickly.
- `TestEventsVolumeCreate` captures daemon time, creates a volume, queries filtered events with `Since`/`Until`, then creates a container with that volume and checks only one create event exists.

## Control Flow
Tests use setup context and the environment API client. Event tests subscribe or query, perform daemon actions, and select/poll with timeouts. `getEvents` drains event streams until EOF or timeout.

## State And Persistence
Creates containers, exec instances, volumes, and event log entries in the daemon. Context cancellation bounds event streams.

## Dependencies And Integration Points
Uses events API, exec API, volume API, container mount helpers, raw request helpers, daemon time helpers, and Moby event filter types.

## Risks And Edge Cases
Windows skips indicate event timing/behavior uncertainty there. Event tests are race-prone if event subscription starts too late or daemon time boundaries are too tight. The nonblocking test uses a three-second grace period.

## Test Signals
Passing signals include an `exec_die` container event with matching container ID, exec ID, and exit code `0`; immediate `/events` response with HTTP 200; and exactly one volume create event despite subsequent container attachment.
