<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h

Purpose: Defines high-resolution raw and incremental statistics containers.

Important APIs/types: `HighResolutionStats` contains `RawVals` and `IncrementalVals` with serialization. `HighResolutionStatsTk` provides helpers to add raw/inc stats and reset stats.

Control flow/state/persistence: Stats are value-owned and serializable, typically transported in lists/vectors. Add helpers accumulate counters into existing structures.

Dependencies/integration: Used by performance monitoring and management reporting. Serialization traits declare list length behavior.

Risks/test signals: Counter accumulation can overflow if unbounded. Tests should cover serialization, reset behavior, incremental addition, raw addition, and list/vector transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h -->
