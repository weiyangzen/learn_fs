# sources/distributed-fs/ceph/src/mds/SegmentBoundary.h

Purpose: defines a small base class marking metadata log events that create or represent log segment boundaries.

Important APIs and types: `SegmentBoundary` stores a `LogSegment::seq_t`, exposes `get_seq()` and `set_seq()`, and provides virtual `is_major_segment_boundary()` defaulting to false. It has a virtual destructor so log events can derive from it safely.

State and persistence: only the segment sequence number is stored. Persistence is provided by derived log event types and `MDLog`; this base class does not encode or write anything itself.

Dependencies and integration: depends on `LogSegment.h`. `MDLog` uses `dynamic_cast<SegmentBoundary*>` when starting new segments and trimming by boundary sequence.

Risks and test signals: because behavior is type-identified through inheritance/dynamic cast, derived log events must inherit correctly and set sequence numbers consistently. Tests should cover MDLog segment creation/trimming around boundary events and major-boundary overrides in derived classes.
