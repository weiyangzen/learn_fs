# sources/distributed-fs/ceph/src/mds/events/ESubtreeMap.h

Purpose: Declares a major segment-boundary event that records the MDS subtree authority map.

Important APIs/types: `ESubtreeMap` stores an `EMetaBlob`, `subtrees` map from root dirfrag to bounds, `ambiguous_subtrees`, and `expire_pos`. It exposes `get_metablob`, replay, dump, dencoder test generation, and `is_major_segment_boundary`.

Control flow: Written to checkpoint subtree authority and cache metadata; replay restores subtree map and ambiguous subtrees at a major boundary.

State and persistence behavior: Persistent payload includes metablob metadata plus subtree maps and expiration position. It is both metadata payload and journal boundary.

Dependencies and integration points: Uses `LogEvent`, `SegmentBoundary`, `EMetaBlob`, `MDCache` subtree authority, and mdlog trimming/replay.

Risks: Stale or incomplete subtree maps can assign authority incorrectly after failover. `expire_pos` must align with journal expiry.

Test signals: Replay of subtree checkpoints with ambiguous subtrees, metablob restoration, and major-boundary handling.
