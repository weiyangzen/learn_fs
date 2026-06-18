# sources/distributed-fs/ceph-client/net/rds/ib_ring.c

## Purpose
`ib_ring.c` provides the small ring-accounting primitive used by RDS/IB send and receive work request arrays. It tracks which WR slots are allocated by the producer and freed by completion handlers without embedding transport-specific state.

## Important APIs, Types, and Functions
The file operates on `struct rds_ib_work_ring` from `ib.h`. Public functions are `rds_ib_ring_init()`, `rds_ib_ring_resize()`, `rds_ib_ring_alloc()`, `rds_ib_ring_free()`, `rds_ib_ring_unalloc()`, `rds_ib_ring_empty()`, `rds_ib_ring_low()`, `rds_ib_ring_oldest()`, and `rds_ib_ring_completed()`. It also declares `rds_ib_ring_empty_wait`, used when shutdown or completion logic waits for all signaled sends/ring entries to drain.

## Control Flow
`rds_ib_ring_init()` zeroes the ring and sets capacity. Allocation computes `avail = w_nr - used`, returns the smaller of requested and available entries, stores the starting position, advances `w_alloc_ptr`, and increments `w_alloc_ctr`. Completion/free advances `w_free_ptr`, atomically adds to `w_free_ctr`, and wakes waiters when the ring becomes empty. `rds_ib_ring_unalloc()` rolls back producer-side allocation when later setup or credit acquisition fails. `rds_ib_ring_completed()` converts a completed WR id and oldest index into the number of contiguous entries completed.

## State and Persistence
Ring state is in-memory per connection: allocation pointer/counter and free pointer/counter. Counters are intentionally wraparound-friendly; used entries are derived from the difference between producer and atomic free counters. The capacity can be resized only before the QP is live and only when the ring is empty.

## Dependencies and Integration Points
Send and receive paths use the same primitive. The model assumes allocations are serialized by the caller, while frees happen from completion context and can race only with allocation. This contract is documented in the file and is required by `ib_send.c` and `ib_recv.c`.

## Risks
`rds_ib_ring_unalloc()` subtracts an unsigned value and relies on modulo arithmetic; callers must not unallocate more than they just allocated. `rds_ib_ring_completed()` assumes ordered completions and contiguous accounting; out-of-order completion behavior would break this model. `BUG_ON(diff > ring->w_nr)` catches accounting corruption but also means a bug can panic the kernel.

## Test Signals
Unit-style validation can exercise wraparound allocation/free, partial allocation, rollback, resize-before-use, oldest/completed math across the end of the ring, and empty/low thresholds. Integration signals include send/receive ring full counters and empty-ring warnings.
