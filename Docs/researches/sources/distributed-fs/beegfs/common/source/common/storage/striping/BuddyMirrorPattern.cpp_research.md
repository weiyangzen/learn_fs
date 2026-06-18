<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp

Purpose: Implements mutable target update and equality comparison for buddy-mirror stripe patterns.

Important APIs/functions: `updateStripeTargetIDs` validates that the incoming pattern is also buddy mirror, then copies its stripe target vector. `patternEquals` compares target IDs and default target count after casting to `BuddyMirrorPattern`.

Control flow/state/persistence: No persistence here; it mutates in-memory pattern target IDs for special repair/fsck-style flows.

Dependencies/integration: Depends on `BuddyMirrorPattern.h` and the virtual `StripePattern` API. Used by metadata and fsck code that manipulates stripe layouts.

Risks/test signals: Update rejects mismatched pattern types but does not validate minimum target count. Tests should cover mismatched type, equal/different target vectors, default target count differences, and repair paths that rely on mutable target IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp -->
