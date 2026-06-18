<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp

Purpose: Implements mutable target update and equality comparison for RAID0 stripe patterns.

Important APIs/functions: `updateStripeTargetIDs` accepts only another RAID0 pattern and copies its stripe target vector. `patternEquals` compares target IDs and default target count.

Control flow/state/persistence: The implementation only mutates/comparisons in memory. Serialized representation is defined in the header and base pattern logic.

Dependencies/integration: Depends on `Raid0Pattern.h` and base `StripePattern`. Used for normal non-mirrored BeeGFS file striping.

Risks/test signals: Updates are intended for special cases because stripe targets are normally immutable. Tests should cover pattern type mismatch, vector differences, default target count differences, and cloned/serialized equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp -->
