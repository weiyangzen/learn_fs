# sources/distributed-fs/ceph/src/mds/events/EImportStart.h

Purpose: Declares the event that begins importing a subtree from another MDS rank.

Important APIs/types: `EImportStart` stores base dirfrag, boundary vector, source rank, `EMetaBlob`, encoded client map, and client map version. It overrides `get_metablob`, `update_segment`, and replay.

Control flow: On import start, the event records incoming subtree metadata and any client/session map needed to force-open sessions for imported caps. Replay rebuilds imported metadata and session context before later finish events.

State and persistence behavior: Durable payload includes subtree metadata, boundaries, source rank, client map buffer, and cmap version. Segment updates account for metablob contents.

Dependencies and integration points: Uses `MDLog`, `MDSRank`, `EMetaBlob`, `LogEvent`, and import migration code.

Risks: Client map version and encoded client insts must align with sessionmap replay. Boundary omissions can produce incorrect authority maps.

Test signals: Import replay with client caps, multiple boundary fragments, and interrupted import followed by finish/failure.
