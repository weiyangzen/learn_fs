# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.c

## Purpose

`rxe_queue.c` allocates, mmap-prepares, resets, resizes, and destroys RXE circular queue buffers used for SQ, RQ, SRQ, and CQ storage.

## Important APIs, Types, and Functions

The core functions are `do_mmap_info()`, `rxe_queue_init()`, `rxe_queue_reset()`, `rxe_queue_resize()`, internal `resize_finish()`, and `rxe_queue_cleanup()`.

## Control Flow

Creation rounds element size and slot count to powers of two, allocates `vmalloc_user()` memory, fills the queue header, and returns effective capacity. Resize creates a new queue and mmap metadata, locks consumer/producer sides, copies live entries in order, swaps queue headers so existing pointers remain valid, and cleans up the old allocation.

## State and Persistence Behavior

Persistent queue state includes the queue descriptor, shared queue buffer, index mask, element size/log2, private driver index, queue type, and optional mmap info. User-visible mappings persist until cleanup or resize replacement.

## Dependencies and Integration Points

It depends on vmalloc user memory, RXE mmap helpers, queue inline helpers, and locks provided by QP/SRQ/CQ owners.

## Risks and Edge Cases

Resize must reject shrinking below occupancy and must preserve order under concurrent producer/consumer protection. Capacity is rounded and one slot is reserved empty. Reset clears only element memory, so callers must reset indices consistently.

## Test Signals

Test queue creation, mmap metadata, wraparound, reset, CQ/SRQ resize with live entries, shrink rejection, and mmap release on destroy.
