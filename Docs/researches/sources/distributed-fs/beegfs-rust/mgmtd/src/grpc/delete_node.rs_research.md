<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs

Purpose: implements node deletion, including special handling for meta nodes and their implicit targets.

Important APIs/types/functions: `delete_node()` resolves a node, rejects management node deletion, checks meta target buddy/root constraints, checks non-meta assigned targets, deletes the node, and optionally sends `RemoveNode`.

Control flow: an immediate transaction performs all validation and deletion, committing only when `execute` is true. Meta nodes first delete their one associated meta target if not in a buddy group and not hosting root inode. Storage/client paths require no assigned targets. After commit, notifications go to meta/client for meta deletion or meta/storage/client for storage deletion.

State and persistence: deletes from `nodes` and, for meta nodes, deletes the corresponding target row. Cascading entity cleanup depends on schema constraints/triggers.

Dependencies and integration points: entity resolution, DB node deletion, root/buddy checks, BeeMsg `RemoveNode`, and pre-shutdown guard.

Risks: execute=false still runs deletion SQL inside an uncommitted transaction to validate effects. Meta target assumptions require exactly one target per meta node. Notification delivery failure does not undo deletion.

Test signals: async test covers management deletion rejection, meta buddy member rejection, successful empty meta-node deletion, and database absence afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs -->
