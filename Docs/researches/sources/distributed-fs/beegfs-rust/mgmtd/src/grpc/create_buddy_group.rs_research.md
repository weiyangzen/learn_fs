<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs

Purpose: handles creation of metadata or storage buddy mirror groups through gRPC.

Important APIs/types/functions: `create_buddy_group()` parses request node type, alias, optional numeric group ID, and primary/secondary target entities; calls `db::buddy_group::insert()`; returns the created `EntityIdSet`.

Control flow: after license/pre-shutdown checks, the handler resolves both targets in a write transaction, creates the group, logs success, sends `SetMirrorBuddyGroup` to meta, storage, and client nodes, and sends `RefreshStoragePools` for storage groups.

State and persistence: writes a buddy group entity and row. For storage groups, group creation also implies storage-pool membership relationships used by pool refresh consumers.

Dependencies and integration points: depends on mirroring license, entity resolution, DB group constraints, BeeMsg `SetMirrorBuddyGroup`, and storage-pool refresh notifications.

Risks: notification happens after DB commit; failures to deliver are not rolled back. Target/node-type mismatches and root-inode secondary restrictions are enforced in DB helper. Storage-pool refresh is needed for grouped targets to be interpreted correctly by other nodes.

Test signals: no direct test in this file; DB buddy group tests cover constraints. RPC tests should verify notifications and proto response fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs -->
