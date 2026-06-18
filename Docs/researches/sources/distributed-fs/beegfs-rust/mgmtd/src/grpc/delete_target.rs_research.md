<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs

Purpose: deletes standalone storage targets.

Important APIs/types/functions: `delete_target()` resolves a target, ensures it is a storage target and not a buddy-group member, calls `db::target::delete_storage()`, and returns the deleted target entity.

Control flow: the handler uses an immediate transaction and honors `execute` for commit/dry-run. After committed deletion it logs, sends `RefreshCapacityPools` to meta nodes, and sends `RefreshStoragePools` to meta/storage nodes.

State and persistence: removes a storage target row from SQLite. It does not contact the owning storage node; this is a management DB operation plus refresh notifications.

Dependencies and integration points: pre-shutdown guard, entity resolution, target DB helper, capacity-pool and storage-pool BeeMsg refresh messages.

Risks: only storage targets can be deleted directly; meta target deletion is tied to node deletion. Deleting a target with stale external node state may require operators to coordinate daemon state.

Test signals: no direct tests here. Needed tests include buddy-member rejection, execute=false, non-storage rejection, and notification types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs -->
