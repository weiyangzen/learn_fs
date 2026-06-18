# sources/control-plane/mayastor/io-engine/tests/memory_pool.rs

Purpose: validates generic fixed-size `MemoryPool<T>` allocation, initialization, exhaustion, address uniqueness, reuse of freed entries, and clean drop after all entries are returned.

Important APIs/types/functions: `MemoryPool::<TestCtx>::create`, `get`, `put`, and `TestCtx` payload fields. `POOL_SIZE` is `128 * 1024 - 1`; `TEST_BULK_SIZE` is 32K.

Control flow: allocate every pool item with unique data, track returned pointers in a map, assert one extra allocation fails, free a subset, allocate the same number again and verify addresses are reused from freed entries, verify no pool growth occurred, return all entries, and drop the pool.

State and persistence: in-memory pool only. Stores a raw C string pointer from a `CString` created outside the spawn.

Dependencies and integration points: Mayastor memory pool implementation and raw pointer safety.

Risks and edge cases: large allocation count. Uses raw pointers and relies on the `CString` staying alive while the spawned future runs. Map iteration `.take(TEST_BULK_SIZE)` chooses arbitrary entries.

Test signals: strong allocator behavior signal for pool capacity, reuse, and drop safety.
