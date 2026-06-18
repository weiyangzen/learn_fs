# sources/distributed-fs/lizardfs/src/common/compact_vector.h

Purpose: implements `compact_vector`, a memory-compact `std::vector`-like container for cases where payload storage matters more than amortized growth. It deliberately keeps capacity equal to size and uses internal storage or pointer/size packing on 64-bit builds.

Important APIs/types/functions: `detail::compact_vector_storage` has three storage variants: generic pointer+size, trivial small internal buffer, and 64-bit pointer-obfuscating storage that packs size into unused pointer bits. `compact_vector_base` owns allocation/deallocation. `detail::normal_iterator` provides random-access iterator behavior. `compact_vector` exposes constructors, assignment, `resize`, iterators, element access, `push_back`, `emplace`, `insert`, `erase`, relational operators, and `swap`.

Control flow: mutating operations allocate exactly the new size, construct new elements, move/copy existing ranges, then call `set_new_ptr` to destroy/deallocate old storage. In-place insert paths are used when the allocator returns the same internal buffer. Exception paths destroy partially constructed ranges and restore the old pointer.

State and persistence: state is only in-memory: packed storage, optional debug pointer, size, and element payload. It has no persistence or synchronization. Iterator/pointer invalidation is aggressive because any size change can reallocate.

Dependencies and integration: depends on allocator traits, `platform.h`, standard algorithms, and raw placement/destruction. Used by `id_pool.h` as a dense bit-vector block and likely throughout common code where lower object size is desirable.

Risks: the 64-bit pointer packing relies on allocator alignment and virtual-address assumptions; `assert` guards vanish in release builds. `reserve` is a no-op, so callers expecting vector amortization can get O(n^2) behavior. The overload set at the bottom uses `compact_vector<Tp, Alloc>` and therefore treats the second template argument as the size type, not allocator, which is easy to misuse with the three-parameter template.

Test signals: `compact_vector_unittest.cc` compares core behavior with `std::vector`, checks iterator traversal, insert/erase, move assignment, and validates internal-storage size and address behavior on 64-bit builds.
