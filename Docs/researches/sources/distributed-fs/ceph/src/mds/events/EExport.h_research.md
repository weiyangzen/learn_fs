# sources/distributed-fs/ceph/src/mds/events/EExport.h

Purpose: Declares the journal event for exporting a directory subtree to another MDS rank.

Important APIs/types: `EExport` stores an `EMetaBlob` for exported metadata, base `dirfrag_t`, boundary dirfrags, and target rank. It exposes `get_bounds`, `get_metablob`, encode/decode/dump/test instances, and replay.

Control flow: During export, the event records the subtree root and boundaries plus enough metadata for replay to reconstruct/export state. The print path describes base, target, and metablob.

State and persistence behavior: Persistent state includes base dirfrag, bounds, target, and serialized metablob. Replay depends on metablob content to reconstruct cache objects and subtree authority.

Dependencies and integration points: Uses `MDSRank`, `LogEvent`, `EMetaBlob`, `CDir`, and MDS migration/export logic.

Risks: Incorrect bounds can corrupt subtree authority after replay. Metablob completeness is essential for migrated metadata.

Test signals: Export/replay of subtrees with multiple bounds, dirty/importing dirs, and target rank failover.
