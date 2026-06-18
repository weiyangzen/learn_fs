<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h

Purpose: Converts C arrays and `ArraySlice` values into byte-slice views.

Important APIs/types: `ArrayTypeTraits::Util<T,N>` exposes `As_ArraySlice`, `As_RO_Slice`, `As_WO_Slice`, and `As_Slice` overloads for fixed arrays and `ArraySlice<T>`.

Control flow/state/persistence: Pure compile-time/static conversion helpers. They compute byte lengths as element count times `sizeof(T)`.

Dependencies/integration: Depends on `ArraySlice` and `Slice` abstractions. Used by serialization and IO helpers that operate on raw byte spans.

Risks/test signals: Endianness and object representation are caller concerns when converting typed data to bytes. Tests should validate byte lengths, const correctness, and zero-length array/slice handling where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h -->
