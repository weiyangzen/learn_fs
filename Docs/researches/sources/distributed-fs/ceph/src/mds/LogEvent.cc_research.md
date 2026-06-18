# sources/distributed-fs/ceph/src/mds/LogEvent.cc

## Purpose

`LogEvent.cc` implements runtime decoding and type-name mapping for MDS journal events. It is the central factory that turns a serialized event type in an MDS journal buffer into the correct `LogEvent` subclass for replay, inspection, and tooling.

## Important APIs, Types, and Functions

`LogEvent::decode_event(bufferlist::const_iterator)` reads the leading event type and supports both classic encoding and the newer versioned wrapper marked by `EVENT_NEW_ENCODING`. For versioned events it decodes a wrapper version, then the real event type, then delegates to the typed factory.

`LogEvent::decode_event(bufferlist::const_iterator&, EventType)` is the typed factory. It creates concrete subclasses for subtree maps, exports/imports, fragments, reset journal, session events, metadata updates, peer updates, open events, committed/purged markers, table client/server events, no-op, segment boundaries, and log-id events. `EVENT_SESSIONS_OLD` creates an `ESessions` instance and marks old encoding.

`get_type_str` maps numeric event ids back to stable names for logging and printing. `types` and `str_to_type` map strings to event ids for command/tool paths that refer to event names.

## Control Flow and Data Flow

Decode starts by reading an `EventType` from the buffer. If the value is `EVENT_NEW_ENCODING`, the method enters a `DECODE_START` block, reads the actual type, builds and decodes that event, and exits with `DECODE_FINISH`. Otherwise it treats the first type as the legacy event type and decodes directly. The typed factory logs the remaining byte count, constructs the subclass, calls `le->decode(p)`, asserts the iterator is at the end, and returns the unique pointer.

Errors in wrapper or event-body decoding are caught as `buffer::error`; the code logs at level 0 and returns `nullptr`. Unknown event types also return `nullptr`.

## State and Persistence Behavior

This file does not persist state itself. Its correctness determines whether persisted MDS journal records can be decoded during replay. The string/type map and switch statements are part of the durable journal compatibility surface: event id changes or missing cases can break recovery of existing logs.

The factory preserves special compatibility behavior for old session-map event encoding and for `EVENT_SUBTREEMAP_TEST`, which reuses `ESubtreeMap` but overrides the event type.

## Dependencies and Integration Points

The file includes every known concrete event header used by the switch, `MDSRank` for replay interfaces, and Ceph buffer/debug/config headers. It is used by `MDLog` replay and by journal inspection paths that need a polymorphic `LogEvent`. It integrates with each subclass's `encode`, `decode`, `update_segment`, `replay`, `dump`, and optional `get_metablob` behavior.

## Risks and Edge Cases

Adding a new event type requires updating `LogEvent.h` constants, this factory switch, `get_type_str`, and the `types` map. `str_to_type` uses `std::map::at`, so unknown strings throw rather than returning the comment's historical `-1`; callers must be prepared for that behavior. The `ceph_assert(p.end())` requires event decoders to consume exactly the supplied payload, making partial or trailing data a hard failure in debug/asserting builds.

The wrapper decode catch logs "type maybe" because the real type may not have decoded correctly. Returning `nullptr` must be handled by replay callers as corrupt or unsupported journal data.

## Test Signals

Tests should round-trip every event subclass through `encode_with_header` and `decode_event`, including legacy/classic encoding where still supported. Recovery tests should include old `EVENT_SESSIONS_OLD` logs, unknown event ids, truncated buffers, buffers with trailing bytes, and string mapping for every named event. Segment-boundary events should be decoded in integration tests that start new log segments.
