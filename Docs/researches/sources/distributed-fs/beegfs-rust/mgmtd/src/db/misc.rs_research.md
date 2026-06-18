<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs

Purpose: contains cross-cutting database helpers for numeric ID allocation and metadata-root state.

Important APIs/types/functions: `find_new_id()` finds an unused numeric ID in a table/field/node-type/range. `MetaRoot` represents unknown, normal node-hosted, or mirrored buddy-group-hosted root state. `get_meta_root()` reads `root_inode` joined to targets/nodes/groups. `enable_metadata_mirroring()` moves the root from a meta target to its buddy group and marks the secondary target `NeedsResync`.

Control flow: ID allocation uses SQL to find the smallest gap or the range minimum when unused. Metadata mirroring updates `root_inode` through a primary-target buddy-group join, then updates the secondary meta target consistency.

State and persistence: mutates `root_inode` and `targets.consistency` during metadata mirroring. Reads target/node/group topology and generates IDs for multiple object tables.

Dependencies and integration points: called by node/target/pool/buddy insert paths, gRPC root-mirroring handler, node insertion, and import code. It depends on trusted static table/field arguments.

Risks: `find_new_id()` builds SQL from `table` and `field`; its warning is correct that user-supplied names would be SQL injection. Metadata mirroring assumes a valid primary buddy group exists and one root row is affected.

Test signals: unit tests cover gap/min/all-taken ID allocation and normal-to-mirrored root transition, including a second mirroring attempt failing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs -->
