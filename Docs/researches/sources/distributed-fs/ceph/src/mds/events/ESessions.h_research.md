# sources/distributed-fs/ceph/src/mds/events/ESessions.h

Purpose: Declares a batched session-open journal event for forcing multiple sessions open, usually during import/recovery.

Important APIs/types: `ESessions` stores client map version, old-encoding flag, `client_map`, and `client_metadata_map`. It supports old/new decode paths, encode/dump/test/update_segment/replay, and `mark_old_encoding`.

Control flow: Batch session events are replayed by opening all encoded sessions and marking sessionmap versions accordingly. Old-style encoding exists for compatibility.

State and persistence behavior: Persistent state is maps of client ids to entity insts and metadata plus cmap version. Replay interacts with sessionmap version projection.

Dependencies and integration points: Uses `LogEvent`, client metadata/entity types, `SessionMap::replay_open_sessions`, and import/force-open server paths.

Risks: Batch size and version math must match sessionmap replay; old/new encoding mismatch can corrupt client map decode.

Test signals: Old and new dencoder tests, replay with partially already-saved sessions, and metadata merge behavior.
