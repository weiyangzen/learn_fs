<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h

Purpose: Defines the stripe pattern for buddy mirrored file placement.

Important APIs/types: `BuddyMirrorPattern` derives from `StripePattern`, stores `stripeTargetIDs` and `defaultNumTargets`, serializes default count plus target IDs, and implements target access, mutable update, clone, min/default target counts, and assigned target count.

Control flow/state/persistence: The pattern is serialized as a `StripePattern` header plus buddy content. It has no separate disk behavior, but serialized patterns are part of inode/message metadata.

Dependencies/integration: Integrates with `StripePattern`, `StoragePoolStore`, serialization, and fsck/metadata layout code. Buddy mirror target IDs represent mirror group IDs rather than direct storage targets.

Risks/test signals: Clone must preserve storage pool ID and default count expectations. Tests should cover serialization with and without storage pool IDs, target indexing through the base class, and update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h -->
