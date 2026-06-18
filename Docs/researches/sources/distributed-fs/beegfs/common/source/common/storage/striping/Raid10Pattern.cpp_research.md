<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp

Purpose: Implements mutable stripe target update and equality comparison for legacy RAID10 patterns.

Important APIs/functions: `updateStripeTargetIDs` requires another RAID10 pattern and copies only stripe target IDs. `patternEquals` compares stripe IDs, mirror IDs, and default target count.

Control flow/state/persistence: Runtime state mutation is limited to target-vector updates. Mirror target IDs remain separately tracked and are compared for equality.

Dependencies/integration: Depends on `Raid10Pattern.h` and `StripePattern`. RAID10 appears in fsck conversion and old pattern compatibility paths.

Risks/test signals: Updating only stripe IDs but not mirror IDs can produce inconsistent layouts if misused. Tests should cover equal-length stripe/mirror vectors, mismatches, update semantics, and clone/equality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp -->
