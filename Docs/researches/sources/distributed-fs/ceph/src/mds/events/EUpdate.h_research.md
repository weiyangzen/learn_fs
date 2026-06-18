# sources/distributed-fs/ceph/src/mds/events/EUpdate.h

Purpose: Declares the general metadata update journal event used by most MDS namespace and inode mutations.

Important APIs/types: `EUpdate` stores an `EMetaBlob`, operation type string, encoded client map, client map version, request id, and `had_peers` flag. It exposes `get_metablob`, encode/decode/dump/test/update_segment/replay.

Control flow: Server mutation handlers populate the metablob, optional client map/request metadata, and submit the event to mdlog. Replay applies the metablob and uses request/client/peer metadata for idempotency and distributed operation recovery.

State and persistence behavior: Persistent state is the full metablob plus request/session context. Segment updates are delegated to metablob and event-specific fields.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `Server` mutation paths, `SessionMap`, `InoTable`, table clients, and peer request handling.

Risks: As the generic update event, missing metablob fields or wrong `had_peers`/reqid/cmapv can affect replay, duplicate suppression, and peer rollback. The type string is diagnostic but useful for debugging journal contents.

Test signals: Replay create/unlink/rename/setattr/xattr/snapshot updates, idempotent client request completion, peer-involved updates, and dencoder compatibility.
