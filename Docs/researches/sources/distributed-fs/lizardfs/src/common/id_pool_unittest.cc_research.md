# sources/distributed-fs/lizardfs/src/common/id_pool_unittest.cc

Purpose: validates bounded ID allocation and recycling.

Important APIs/types/functions: tests `acquire`, `release`, `nullId`, `maxSize`, and `markAsAcquired` using `IdPool<uint32_t>`.

Control flow: tests consume entire pools, verify exhaustion returns zero, repeatedly release/acquire IDs, reject null release, check all IDs are unique, and ensure marked IDs are never acquired.

State and persistence: test-only pool objects and a `std::set` of taken IDs.

Dependencies and integration: includes `id_pool.h` and `gtest`.

Risks: tests use small ranges/block sizes; they do not stress very large ranges, cache overflow patterns with random release orders, or multi-threaded use.

Test signals: good coverage for core allocator contract and edge handling around zero.
