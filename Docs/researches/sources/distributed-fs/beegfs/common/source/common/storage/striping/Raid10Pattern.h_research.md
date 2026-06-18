<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h

Purpose: Defines a stripe pattern with separate primary stripe and mirror target vectors.

Important APIs/types: `Raid10Pattern` derives from `StripePattern`, stores `stripeTargetIDs`, `mirrorTargetIDs`, and `defaultNumTargets`. It serializes default count, stripe IDs, and mirror IDs. It exposes mirror target accessors in addition to stripe accessors.

Control flow/state/persistence: Constructors perform debug-only vector length sanity checks. Serialized content order and target-vector length pairing define the persisted layout.

Dependencies/integration: Used for older RAID10-style mirror layouts and fsck conversions. Depends on serialization, storage pools, and base striping helpers.

Risks/test signals: The public `clone(const UInt16Vector&)` currently returns a copy and ignores its argument, which is suspicious. Tests should assert clone semantics, vector length mismatch handling, serialization, and mirror target lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h -->
