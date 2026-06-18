<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp

Purpose: Converts between runtime metadata/stripe types and fsck-specific representations.

Important APIs/functions: `DirEntryTypeToFsckDirEntryType` maps directory entry types. `stripePatternToFsckStripePattern` maps `StripePattern` instances to fsck enum plus target vectors. `FsckStripePatternToStripePattern` creates runtime patterns from fsck type, chunk size, and targets.

Control flow/state/persistence: Conversion switches on enum values and allocates new `StripePattern` objects for reverse conversion. Caller owns returned pattern pointers.

Dependencies/integration: Uses `Raid0Pattern`, `BuddyMirrorPattern`, `StripePattern`, and fsck enums. Bridges online metadata with checker/repair tools.

Risks/test signals: Unsupported RAID10 conversion behavior and ownership of allocated patterns should be tested. Cover all dir entry types, null/unknown patterns, target vector preservation, and buddy mirror conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp -->
