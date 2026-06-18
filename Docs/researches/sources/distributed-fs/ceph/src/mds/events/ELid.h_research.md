# sources/distributed-fs/ceph/src/mds/events/ELid.h

Purpose: Declares a major segment-boundary journal event carrying a log segment id.

Important APIs/types: `ELid` inherits both `LogEvent` and `SegmentBoundary`, stores `seq` through the base boundary, and implements encode/decode/dump/replay/test instances. `is_major_segment_boundary()` returns true.

Control flow: The event marks a durable boundary during journal processing and replay; print emits `ELid(seq)`.

State and persistence behavior: Persistent state is segment sequence from `SegmentBoundary`. It is boundary metadata, not filesystem metadata.

Dependencies and integration points: Depends on `LogEvent`, `SegmentBoundary`, and `LogSegment` sequence types.

Risks: The explicit constructor initializes `LogEvent(EVENT_SEGMENT)` rather than `EVENT_LID`, which is noteworthy because the default constructor uses `EVENT_LID`; tests should confirm intentional compatibility.

Test signals: Dencoder and replay tests around segment boundary classification and event type.
