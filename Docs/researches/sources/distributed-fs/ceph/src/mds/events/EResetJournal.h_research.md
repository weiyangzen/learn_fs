# sources/distributed-fs/ceph/src/mds/events/EResetJournal.h

Purpose: Declares a major segment-boundary event that resets the MDS journal.

Important APIs/types: `EResetJournal` inherits `LogEvent` and `SegmentBoundary`, returns true from `is_major_segment_boundary`, and implements encode/decode/dump/test/replay.

Control flow: Replay treats this as a reset boundary rather than a metadata mutation.

State and persistence behavior: Persistent payload is boundary/reset metadata handled by implementation.

Dependencies and integration points: Uses `LogEvent` and `SegmentBoundary`; integrated with `MDLog` journal reset handling.

Risks: Reset events must be recognized as major boundaries to prevent replay from crossing invalid journal history.

Test signals: Journal reset replay, segment-boundary detection, and dencoder compatibility.
