<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h

Purpose: Tracks minimum, maximum, sum, and count for entered values.

Important APIs/types: `MinMaxStore<T>` exposes constructors for default, single-value, and explicit min/max initialization, plus `getMin`, `getMax`, and `enter`.

Control flow/state/persistence: `enter` updates min/max in memory using BeeGFS min/max macros. The default constructor initializes min to `numeric_limits<T>::max()` and max to `numeric_limits<T>::min()`. No persistence.

Dependencies/integration: Template utility for statistics gathering.

Risks/test signals: Empty/default-state getter behavior is the main concern. Tests should cover no values, one value, increasing/decreasing sequences, negative values for signed types, and explicit min/max constructor invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h -->
