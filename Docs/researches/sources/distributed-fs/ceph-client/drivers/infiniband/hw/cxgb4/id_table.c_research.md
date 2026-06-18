# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/id_table.c

Purpose: small bitmap-backed ID allocator used by the cxgb4 RDMA resource layer for logical resource IDs such as TPT/STAG indices, QIDs, PDIDs, and SRQ table IDs.

Important APIs, types, and functions: `c4iw_id_table_alloc()` initializes `struct c4iw_id_table` with a start offset, number of entries, reserved entries, flags, spinlock, and bitmap. `c4iw_id_alloc()` finds the next clear bit from `last`, wraps to the first clear bit, marks it allocated, updates `last` either sequentially or pseudo-randomly, and returns logical ID `start + bit`. `c4iw_id_free()` clears an allocated bit. `c4iw_id_table_free()` frees the bitmap. Flags are `C4IW_ID_TABLE_F_RANDOM` and `C4IW_ID_TABLE_F_EMPTY`; `RANDOM_SKIP` bounds pseudo-random advancement.

Control flow: callers create a table during resource initialization, optionally pre-reserve low IDs unless the table starts empty, allocate/free IDs under the table spinlock, and destroy the table at device teardown. The random mode does not choose a fully random free bit; it randomizes the next starting hint after an allocation.

State and persistence: state is in-memory only: bitmap allocation state, logical start, maximum bit count, flags, `last` search hint, and spinlock. No hardware state is modified directly by this file; higher layers use returned IDs to program hardware tables.

Dependencies and integration points: depends on Linux bitmap helpers, random number generation, and `struct c4iw_id_table` from `iw_cxgb4.h`. It is consumed by resource initialization and allocation helpers outside this item, which feed CQ/QP/MR/PD/SRQ creation.

Risks: `c4iw_id_free()` does not validate that `obj` is within range or currently allocated; caller bugs can clear arbitrary bitmap bits after unsigned subtraction. `c4iw_id_alloc()` returns `-1` in a `u32`, so callers must handle `0xffffffff` correctly. Random mode only changes the next search hint and can still return predictable nearby IDs when the bitmap is sparse. Reserved-count validation is not local, so `reserved > num` would rely on bitmap helper behavior.

Test signals: allocate/free all IDs for sequential and random flags, wrap from end to beginning, reserve low IDs and verify they are skipped, empty-table flag behavior, exhaustion return handling, invalid free under KASAN/KMSAN-style tests, and concurrent allocate/free stress under IRQ-safe spinlock use.
