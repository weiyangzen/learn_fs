# sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.c

## Purpose

`tracepoint.c` provides low-level helpers for validating tracepoint event directories and `system:event` strings.

## Important APIs, Types, and Functions

`tp_event_has_id()` checks whether a tracepoint event directory has an `id` file. `is_valid_tracepoint()` converts `system:event` to `system/event/id`, resolves it under tracefs events, and checks file availability.

## Control Flow and State

Validation allocates a path buffer, replaces colon with slash, appends `/id`, calls `get_events_file()`, then checks the resulting file and frees both buffers. There is no persistent state.

## Dependencies and Integration Points

It depends on tracefs path helpers and `fncache` file availability. It backs tracepoint iteration macros in the header and CLI validation of tracepoint event names.

## Risks and Test Signals

Risks include malformed strings without colons, allocation failure, tracefs unavailability, and event directories racing away. Tests should validate known good and bad tracepoints and paths with missing `id` files.
