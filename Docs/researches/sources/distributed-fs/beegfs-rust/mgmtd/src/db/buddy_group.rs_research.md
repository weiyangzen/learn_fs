<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs

Purpose: implements database operations for metadata and storage buddy mirror groups, including validation, creation, storage-pool reassignment, automatic switchover, and storage group deletion.

Important APIs/types/functions: `validate_ids()` checks existence by numeric group IDs and server node type. `insert()` creates a `BuddyGroup` entity, validates primary/secondary targets, enforces same storage pool for storage groups, rejects secondary ownership of the meta root, and auto-generates aliases/IDs when needed. `update_storage_pools()`, `check_and_swap_buddies()`, `prepare_storage_deletion()`, and `delete_storage()` support pool moves, failover, and delete workflows.

Control flow: creation first chooses/validates numeric ID, checks target existence and group membership, applies storage/meta-specific constraints, creates a global entity, derives storage pool if applicable, and inserts the group. Switchover queries groups where the primary is offline, secondary is good, and secondary contact is recent, then swaps primary/secondary IDs in the DB.

State and persistence: writes `entities` and `buddy_groups`; switchover mutates group primary/secondary assignments; deletion removes storage groups. It reads `targets`, `storage_targets`, `root_inode`, and client-node state for safety checks.

Dependencies and integration points: used by gRPC create/delete/assign/mirror/root resync flows and by `timer.rs` switchover. Notifications are sent by callers after DB mutations.

Risks: `delete_buddy_group` is explicitly racy because it checks DB, calls nodes, then mutates DB. Switchover is DB-only until callers broadcast refresh notifications. Meta root and client-unmounted constraints are critical for data safety.

Test signals: unit tests cover insertion, pool updates, switchover positive and negative cases, deletion prechecks with mounted clients, returned node UIDs, and storage deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs -->
