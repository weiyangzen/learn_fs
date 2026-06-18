<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h

Purpose: Defines the basic BeeGFS RAID0 stripe layout.

Important APIs/types: `Raid0Pattern` derives from `StripePattern`, stores `stripeTargetIDs` and `defaultNumTargets`, serializes default count plus target list, exposes target accessors, update, clone, min target count, and assigned target count.

Control flow/state/persistence: Base-class serialization writes the common header, then RAID0-specific target content. Persistent/wire compatibility depends on this content order.

Dependencies/integration: Integrates with metadata inode patterns, file creation target selection, fsck conversion helpers, and storage pool assignment.

Risks/test signals: Minimum target count is one, but empty target vectors can still be constructed by bad callers. Tests should cover chunk-size defaulting, storage pool ID preservation, target indexing, and empty-vector handling in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h -->
