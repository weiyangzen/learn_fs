<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h

Purpose: Represents a non-owning typed view over contiguous array data.

Important APIs/types: `ArraySlice<T>` stores a pointer and element count, exposes `data`, `count`, and iteration helpers as values, pointers, const pointers, refs, and const refs.

Control flow/state/persistence: No ownership or persistence; it is a lightweight view.

Dependencies/integration: Depends on `ArrayIteration.h`. Used by serialization/buffer helpers that need typed views without copies.

Risks/test signals: The class does not validate null pointer with nonzero count. Tests should cover view creation from arrays, empty views, constness, and mutation through refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h -->
