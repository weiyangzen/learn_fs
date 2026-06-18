# sources/distributed-fs/ceph/src/mds/events/EPeerUpdate.h

Purpose: Declares peer-update journal events for multi-MDS link, rename, and rmdir prepare/commit/rollback flows, including rollback payload formats.

Important APIs/types: Rollback structs include `link_rollback`, `rmdir_rollback`, and `rename_rollback` with nested `drec`. `EPeerUpdate` stores operation type, request id, leader rank, phase op, original op, commit `EMetaBlob`, and encoded rollback data.

Control flow: Peer participants journal prepare, commit, or rollback. The commit metablob records the metadata update; rollback buffer contains enough old state for replay to manually undo if the distributed operation did not commit.

State and persistence behavior: Persistent payload includes both forward and rollback metadata because old dirty metadata may become trim-safe before final outcome. Replay applies either commit or rollback semantics by phase and original operation.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `metareqid_t`, snap bufferlists, dirfrag/dentry records, and distributed `Server` peer link/rename/rmdir handlers.

Risks: Rollback records are operation-specific and must include snapbl/ctime/mtime/rctime details to restore visible metadata. Missing rollback data can break recovery after leader failure.

Test signals: Distributed link/rename/rmdir failover during prepare, commit replay, rollback replay, dencoder for all rollback structs, and log trimming with previously dirty metadata.
