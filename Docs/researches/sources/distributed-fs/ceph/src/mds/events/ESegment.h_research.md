# sources/distributed-fs/ceph/src/mds/events/ESegment.h

Purpose: Declares a normal journal segment-boundary event carrying a log segment sequence.

Important APIs/types: `ESegment` inherits `LogEvent` and `SegmentBoundary`, stores sequence via the base class, and implements print, encode/decode/dump/replay/test instances.

Control flow: Used by mdlog to mark segment boundaries during write and replay.

State and persistence behavior: Persistent state is segment sequence metadata only.

Dependencies and integration points: Depends on `LogEvent`, `SegmentBoundary`, and `LogSegment::seq_t`.

Risks: Segment sequence mismatch can affect log trimming and replay ordering.

Test signals: Encode/decode of boundary seq and replay segment transition.
