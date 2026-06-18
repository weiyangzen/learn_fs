# sources/distributed-fs/ceph/src/mds/LogEvent.h

## Purpose

`LogEvent.h` defines the abstract base class and numeric type ids for CephFS MDS journal events. It establishes the serialization, replay, segment-update, printing, and metablob-inspection contract implemented by all concrete event classes under `src/mds/events`.

## Important APIs, Types, and Functions

The file defines stable event ids such as `EVENT_SUBTREEMAP`, `EVENT_EXPORT`, `EVENT_IMPORTSTART`, `EVENT_FRAGMENT`, `EVENT_SESSION`, `EVENT_UPDATE`, `EVENT_OPEN`, `EVENT_COMMITTED`, `EVENT_TABLECLIENT`, `EVENT_NOOP`, `EVENT_SEGMENT`, and `EVENT_LID`. `EVENT_NEW_ENCODING` marks the versioned wrapper used by `encode_with_header`.

`LogEvent` stores `_type`, `_start_off`, `stamp`, and a `LogSegmentRef`. The main virtual interface is `encode(bufferlist&, uint64_t features)`, `decode(bufferlist::const_iterator&)`, `dump(Formatter*)`, `print(std::ostream&)`, `update_segment()`, `replay(MDSRank*)`, and `get_metablob()`. `encode_with_header` writes the versioned wrapper plus the concrete event's payload. `decode_event` is the static factory implemented in `LogEvent.cc`.

The protected `get_segment()` gives subclasses access to the current log segment while `update_segment()` runs. `friend class MDLog` allows the log to set private segment/start metadata.

## Control Flow and Data Flow

During submit, `MDLog` assigns the current `LogSegmentRef` to the event, calls `update_segment`, stamps it, and serializes it with an event header. During replay or inspection, `decode_event` reads a buffer into a concrete subclass, after which callers can invoke `replay`, `dump`, `print`, or inspect a returned `EMetaBlob`.

Subclasses use `update_segment` to register dirty inodes, dentries, dirfrags, table versions, session touches, purges, or segment boundaries against the current log segment. That data later drives log trimming and expiry.

## State and Persistence Behavior

The event type ids and wire encoding are durable journal format. `_start_off` records where an event begins in the journal stream, `stamp` records event time, and `_segment` ties the in-memory event to the segment accounting object. The base `replay` aborts, so every replayable event must override it.

`encode_with_header` uses `ENCODE_START(1, 1)`, so future changes must preserve compatibility through Ceph's encoding versioning rules. `LogSegmentRef` is a shared pointer so event objects can safely refer to segment accounting while they are being submitted or processed.

## Dependencies and Integration Points

`LogEvent.h` depends on buffer forward declarations, `utime_t`, `LogSegmentRef`, and standard map/memory/ostream/string types. It integrates directly with `MDLog`, `LogSegment`, concrete `events/*` classes, `MDSRank` replay, journal dump tooling, and `EMetaBlob` metadata inspection.

## Risks and Edge Cases

Changing event ids, reusing ids, or failing to register a new event in the decode factory can make existing journals unreplayable. Subclasses that embed an `EMetaBlob` should override `get_metablob`; otherwise tooling and MDLog touched-inode tracking can miss metadata dependencies. Subclasses that need segment expiry accounting must override `update_segment`.

The base class is non-copyable and has a deleted default constructor, which prevents accidental type-less events but requires every subclass to explicitly pass an event id. `str_to_type` is declared as returning `EventType`, but the implementation throws for unknown strings.

## Test Signals

Compile tests should ensure every concrete event subclass implements encode/decode/dump and passes a valid event id. Journal replay tests should validate `replay` overrides for replayable event types. Encoding tests should inspect that `encode_with_header` emits `EVENT_NEW_ENCODING`, the wrapper version, and the concrete type. Segment-accounting tests should verify `update_segment` mutations are visible on the current `LogSegment`.
