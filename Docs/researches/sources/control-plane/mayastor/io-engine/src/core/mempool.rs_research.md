# sources/control-plane/mayastor/io-engine/src/core/mempool.rs

## Purpose
Wraps SPDK/DPDK mempools for allocation-free hot-path object reuse with drop-time accounting.

## Important APIs, Types, and Functions
- `MemoryPool<T>` stores the raw `spdk_mempool`, name, capacity, and element type marker.
- `MemoryPool::create(name, size)` creates a pool sized for `T`.
- `get(val)` obtains an element and writes `val` into the slot.
- `put(ptr)` returns a slot to the pool.
- `Drop` asserts all elements have been returned and frees the SPDK pool.

## Control Flow and State
Creation calls `spdk_mempool_create` with `size_of::<T>()` and SPDK default cache sizing. `get` calls `spdk_mempool_get`, writes the provided object into raw memory, and returns a typed pointer. `put` returns the pointer without running `drop` for `T`. On pool drop, `spdk_mempool_count` must equal capacity or the process panics.

State is the SPDK pool and outstanding borrowed elements. No persistence exists.

## Dependencies and Integration Points
Depends on `spdk_rs::libspdk` mempool functions and `IntoCString`. Used by bdev and NVMe I/O context pool initialization from `env.rs`.

## Risks and Test Signals
`put` does not drop values, which is only safe for pool element types designed for this lifecycle. Drop-time assert catches leaks but can panic during shutdown. Tests should cover exhausted pools, returned counts, capacity accounting, and element types with destructor-sensitive behavior.
