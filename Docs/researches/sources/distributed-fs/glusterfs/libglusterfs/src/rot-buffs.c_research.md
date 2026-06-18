# sources/distributed-fs/glusterfs/libglusterfs/src/rot-buffs.c

## Purpose

`rot-buffs.c` implements producer-favored rotating buffers for collecting variable-sized writes into reusable iovec-backed buffer lists. Writers reserve fixed-size regions from the current rotational buffer and later mark completion; consumers remove a filled buffer from rotation, wait for pending writers to finish, dispatch it, reset it, and return it to the free list.

## Important APIs, Types, and Functions

The main API is `rbuf_init()`, `rbuf_dtor()`, `rbuf_reserve_write_area()`, `rbuf_write_complete()`, `rbuf_get_buffer()`, and `rbuf_wait_for_completion()`. `rbuf_t` owns a lock, a `freelist` of `rbuf_list_t`, and the cached current buffer. Each `rbuf_list_t` tracks pending and completed reservations, an `awaiting` flag, a vector list, a cached current vector, vector usage counts, and condition/mutex pairs for completion waiting. `rbuf_iovec_t` combines list metadata with a 1 MiB data area.

## Control Flow and Data Flow

`rbuf_init()` allocates two buffers by default, initializes each `rbuf_list_t`, gives each at least one vector, and selects the first as current. A writer calls `rbuf_reserve_write_area()`, which locks the `rbuf_t`, reserves space in the current `rbuf_list_t`, allocates or advances an iovec if the current 1 MiB allocation is full, increments `pending`, and returns both the write pointer and an opaque `rbuf_list_t` handle. The writer must call `rbuf_write_complete()` with that opaque handle; completion increments `completed` and signals a waiter when a consumer is waiting and all pending writes finished.

Consumers call `rbuf_get_buffer()` to detach the current list if it has pending data and detaching it will not leave writers without a buffer. The consumer then calls `rbuf_wait_for_completion()` with a dispatch function. That function marks the detached list as waiting, waits until `completed == pending`, invokes the dispatcher without holding the rotation lock, clears counters, decays over-allocated vectors with an exponential shrink calculation, resets the first vector, and returns the list to the tail of the free list.

## State and Persistence Behavior

All state is volatile. Buffer contents live only until the consumer's dispatch function returns. The implementation intentionally reuses vector allocations to avoid churn and shrinks only outside the normal low/high watermark range. There is no disk persistence and no internal copy of writer payloads beyond the reserved memory area.

## Dependencies and Integration Points

The file depends on Gluster list primitives, `LOCK` wrappers, memory accounting types, `GF_CALLOC`/`GF_FREE`, and pthread condition variables. It integrates with producers that can follow the reserve/write-complete contract and consumers that can process `rbuf_list_t` iovec lists after all reservations complete.

## Risks and Edge Cases

The reservation size must be positive and no larger than the 1 MiB vector allocation. Missing `rbuf_write_complete()` will block the consumer forever. Consumers cannot detach the only buffer because that would starve writers. The `awaiting` flag is protected by `c_lock` when set but cleared later without that lock after exclusive consumer ownership is assumed. Shrink uses floating-point `pow()` and removes from the front of the vector list, so tests should guard count accounting after heavy bursts. Destroying an `rbuf_t` while writers or consumers still hold opaque handles is unsafe.

## Test Signals

Tests should reserve and complete multiple writes in one vector, across vector boundaries, and across buffer rotations. Consumer tests should exercise `RBUF_EMPTY`, `RBUF_WOULD_STARVE`, and `RBUF_CONSUMABLE`. Concurrency tests should verify a detached buffer waits until all pending writers complete and that missed completion calls hang or are detected by test timeouts. Burst tests should validate vector reuse and shrink behavior after large temporary growth.
