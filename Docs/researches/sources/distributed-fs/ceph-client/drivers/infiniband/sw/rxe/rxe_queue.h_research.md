# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.h

## Purpose

`rxe_queue.h` defines RXE's lock-free circular queue abstraction shared between the driver, userspace, and kernel ULPs.

## Important APIs, Types, and Functions

It defines `enum queue_type`, `struct rxe_queue`, queue creation/resizing/cleanup declarations, and inline helpers for producer/consumer indices, empty/full/count checks, index advancement, and element address calculation.

## Control Flow

Users select a queue type according to ownership. Producers and consumers read or advance only the indices they own, with acquire/release memory ordering when crossing driver/client boundaries.

## State and Persistence Behavior

The shared buffer stores producer and consumer indices plus data. Driver-owned indices may be mirrored through a private copy in `struct rxe_queue`, then published to shared memory.

## Dependencies and Integration Points

The header relies on RXE UAPI queue buffer layout and kernel memory-ordering primitives. It is used by QP, CQ, SRQ, requester, responder, and verbs code.

## Risks and Edge Cases

Wrong queue type usage can advance the wrong side or interpret ownership incorrectly. External locks are still required for multi-CPU access to the same owned end. Capacity is one less than slot count.

## Test Signals

Test wraparound, full/empty boundaries, all queue types, untrusted user indices, and concurrent post/poll under the owning locks.
