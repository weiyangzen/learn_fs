<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs

Purpose: deletes storage buddy groups through a multi-step check/notify/commit flow.

Important APIs/types/functions: `delete_buddy_group()` resolves the group, verifies storage type, calls `db::buddy_group::prepare_storage_deletion()`, sends BeeMsg `RemoveBuddyGroup` to both owning storage nodes, and then calls `db::buddy_group::delete_storage()`.

Control flow: the `execute` flag controls dry-run versus committed deletion. The first transaction validates deletion and obtains primary/secondary node UIDs. The handler sends check-only or execute removal messages to both nodes and requires both `OpsErr::SUCCESS`. A second transaction deletes the DB row if execution is requested; refresh notification follows successful execution.

State and persistence: removes a storage buddy group from SQLite only after both storage nodes accept removal. Sends `RefreshStoragePools` because group membership affects pool state.

Dependencies and integration points: mirroring license, DB deletion checks, BeeMsg request/response types, and storage-pool refresh.

Risks: the source notes this is racy: database state can change between validation, node RPCs, and final deletion. Dry-run mode performs validations and node check requests but does not commit.

Test signals: no direct tests in this file. DB helper tests cover mounted-client rejection and deletion. RPC tests should simulate primary/secondary node response failures and execute=false behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs -->
