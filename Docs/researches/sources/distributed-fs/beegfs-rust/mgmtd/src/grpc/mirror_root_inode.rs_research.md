<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs

Purpose: enables metadata mirroring for the root inode after strict cluster-safety checks.

Important APIs/types/functions: `mirror_root_inode()` reads `db::misc::get_meta_root()`, validates prerequisites, sends `SetMetadataMirroring` to the root meta node, and commits `db::misc::enable_metadata_mirroring()` if the node returns success.

Control flow: handler requires mirroring license and no pre-shutdown. It rejects already mirrored/unknown roots, requires the root target to be primary in a meta buddy group, requires no mounted clients, and requires all other meta/storage nodes to have been quiet beyond `node_offline_timeout`. Only then does it contact the root meta node.

State and persistence: after successful node-side mirroring, updates `root_inode` to point to the buddy group and marks the secondary meta target `NeedsResync`.

Dependencies and integration points: integrates DB root helpers, BeeMsg root-mirroring message, node last-contact tracking, and client-node state.

Risks: there remains a documented race where clients may mount after the check but before node-side operation; operators must coordinate. If node-side success occurs but DB update fails, reconciliation may be required.

Test signals: no direct tests. Needed tests should cover each precondition, node failure response, and DB transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs -->
