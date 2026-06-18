<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h

Purpose: Provides iterator adapters for raw arrays/slices.

Important APIs/types: `ValueIter`, `PointerIter`, `IterateAsValues`, `IterateAsPointers`, and `IterateAsRefs` allow range-style iteration over contiguous arrays as values, pointers, or references.

Control flow/state/persistence: Iterators advance raw pointers and dereference according to adapter type. No state beyond pointer positions.

Dependencies/integration: Used by `ArraySlice` to expose typed iteration over raw buffers.

Risks/test signals: Pointer lifetime and bounds are caller-owned. Tests should cover empty slices, const/non-const refs, pointer iteration, value copies, and compatibility with range-for loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h -->
