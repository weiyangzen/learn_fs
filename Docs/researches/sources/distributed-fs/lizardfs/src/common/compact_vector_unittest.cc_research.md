# sources/distributed-fs/lizardfs/src/common/compact_vector_unittest.cc

Purpose: GoogleTest coverage for `compact_vector` behavior against `std::vector` expectations.

Important APIs/types/functions: defines comparison helpers between `compact_vector<T>` and `std::vector<T>`, then tests construction/copy/move, range insert, erase, iterator arithmetic and conversion, internal storage, and a GCC6 regression around pushing a `uint32_t`.

Control flow: tests build equivalent standard and compact vectors, perform identical mutations, and assert content equality. The internal-storage test branches out on non-64-bit platforms, then checks object size, `max_size`, and whether `data()` points into the vector object before and after crossing inline capacity.

State and persistence: test-only heap/stack state; no persistence.

Dependencies and integration: includes `common/compact_vector.h`, `gtest`, `algorithm`, and `numeric`. It validates ABI-sensitive behavior that other compact data structures, notably `IdPoolBlock`, rely on.

Risks: coverage does not stress exceptions, non-trivial throwing element types, allocator variants, or all insert corner cases. It also relies on pointer-obfuscation assumptions that may differ under sanitizers or unusual allocators.

Test signals: the file itself is the signal; it verifies parity with `std::vector` for representative operations and explicitly guards the 64-bit packed/internal-storage contract.
