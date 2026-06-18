<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs

Purpose: implements the read-only RPC returning all buddy groups with member targets, storage pool, and consistency state.

Important APIs/types/functions: `get_buddy_groups()` queries `buddy_groups_ext`, joins primary/secondary `targets_ext`, optional `pools_ext`, and maps rows to `pm::get_buddy_groups_response::BuddyGroup`.

Control flow: one read transaction builds the full response. Node type and target consistency enums are converted through SQLite enum helpers into protobuf integer variants.

State and persistence: read-only; exposes persisted buddy group topology and target consistency states.

Dependencies and integration points: used by management clients/ctl tooling. Depends on DB views, protobuf `EntityIdSet`, and enum conversion helpers.

Risks: inner joins require primary and secondary targets to exist; inconsistent DB rows would disappear or error. There is no filtering or pagination, so very large clusters return one response containing all groups.

Test signals: no direct tests. Useful tests would verify meta versus storage groups, optional pool population, and consistency state mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs -->
