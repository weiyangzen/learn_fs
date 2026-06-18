# File Research: sources/block-storage/kvdo/vdo/data-vio-pool.c

## Purpose
Implements the preallocated `data_vio` pool used to service incoming bios while bounding concurrency and avoiding allocation during normal I/O.

## Core Design
The pool has two resource limiters:
- Main limiter for total active `data_vio` requests.
- Discard limiter for discard permits, preventing discards from starving reads/writes.

Completed VIOs are returned through a funnel queue and processed in batches on the CPU thread.

## Key Structures
- `struct limiter`: tracks limit, busy count, high-water mark, release/wake counts, waiter lists, permitted waiters, and blocked submitter wait queue.
- `struct data_vio_pool`: owns admin state, spinlock, limiters, permitted discard list, available VIO list, funnel queue, processing flag, and flexible array of `data_vios`.

## Key Functions
- `reset_data_vio()` clears reusable state while preserving separately allocated buffers and bio.
- `launch_bio()` classifies bio as read/write/read-modify-write/discard, handles partial-block state, copies full writes into `data_block`, detects zero blocks, computes LBN, and launches the VIO.
- `acquire_permit()` either consumes a limiter slot or queues the bio and blocks the submitter.
- `vdo_launch_bio()` obtains discard permit if needed, obtains data_vio permit, removes an available VIO, and launches it.
- `release_data_vio()` enqueues completed VIOs into the funnel queue and schedules release processing.
- `process_release_callback()` batches returned VIOs, acknowledges bios, transfers discard permits, reassigns VIOs to oldest eligible waiters, wakes blocked submitters, and completes drain if applicable.
- `make_data_vio_pool()` allocates pool and initializes every `data_vio`.
- `free_data_vio_pool()` asserts no busy VIOs/waiters and destroys all pooled VIOs.
- `drain_data_vio_pool()` and `resume_data_vio_pool()` integrate with admin state.
- Getter functions expose active/limit/max counts for discards and requests.

## Concurrency Notes
The fast release path avoids taking the pool lock in releasing threads by using a funnel queue and atomic `processing` flag. Memory barriers pair scheduling and release callback processing.

## Edge Cases
- Discard waiters first need discard permits, then data_vio permits.
- `bio->bi_private` stores arrival time from `jiffies`; comments note this assumes `jiffies` is not effectively only 32 bits.
- `set_data_vio_pool_discard_limit()` rejects limits above total request limit.
