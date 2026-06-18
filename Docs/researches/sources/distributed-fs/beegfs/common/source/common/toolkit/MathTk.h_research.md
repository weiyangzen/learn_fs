<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h

Purpose: Provides small math helper functions.

Important APIs/types: `MathTk` exposes integer log2 helpers for 64-bit and 32-bit values, `isPowerOfTwo`, and `medianOfSorted` returning `boost::optional<T>`.

Control flow/state/persistence: Pure computations, no state. `medianOfSorted` assumes the input vector is already sorted and returns empty for no values.

Dependencies/integration: Used by striping and configuration validation logic where power-of-two chunk sizes and medians are needed.

Risks/test signals: Tests should cover zero, one, powers/non-powers of two, max values, even/odd median lengths, empty vectors, and unsorted caller behavior documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h -->
