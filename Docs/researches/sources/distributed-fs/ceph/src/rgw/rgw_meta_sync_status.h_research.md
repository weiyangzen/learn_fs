## sources/distributed-fs/ceph/src/rgw/rgw_meta_sync_status.h

Purpose: defines persisted metadata sync progress structures.

Important APIs/types: `rgw_meta_sync_info` records global sync state, shard count, period id, and realm epoch. `rgw_meta_sync_marker` records per-shard full/incremental state, markers, total entries, position, timestamp, and realm epoch. `rgw_meta_sync_status` combines sync info with a map of shard markers.

Control flow: sync code encodes/decodes these records to resume metadata synchronization across restarts and period changes. JSON decode/dump/test-instance declarations support admin/status tools and encoding tests.

State and persistence: all three structs use Ceph encoding with version gates; `period` and `realm_epoch` were added in version 2 for info/marker records. Defaults initialize sync to `StateInit`/`FullSync` with zero counts.

Dependencies/integration: depends on Ceph time, buffer encoding, JSON/Formatter declarations, and metadata sync engine code elsewhere.

Risks and test signals: stale or malformed markers can cause sync replay gaps or duplication. Tests should cover v1 decode compatibility, realm epoch propagation, JSON status round trips, and marker progress across shard boundaries.
