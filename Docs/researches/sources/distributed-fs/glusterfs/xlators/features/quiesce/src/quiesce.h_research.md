# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.h

## Purpose

`quiesce.h` defines the private queue, failover, and per-fop retry state used by the quiesce translator.

## Important APIs, Types, and Functions

`GF_FOPS_EXPECTED_IN_PARALLEL` sizes the local pool. `quiesce_failover_hosts_t` stores failover host list nodes, host address strings, and a `tried` flag. `quiesce_priv_t` stores timer/pass-through/lock/queue/thread/mem-pool/timeout/failover-list state. `quiesce_local_t` stores fd, name, volname, loc, offsets, mode, flags, stat buffer, iovec/iobref, dict, flock, entrylock fields, xattrop flags, write-behind flags, io flags, fallocate length, and seek type.

## Control Flow

The header has no executable flow. Its fields are consumed by enqueue/dequeue, pass-through callbacks, retransmit callbacks, failover, and cleanup code in `quiesce.c`.

## State and Persistence Behavior

All types are in-memory only. `quiesce_priv_t` lasts for the translator lifetime; `quiesce_local_t` is per-inflight fop and must be wiped after unwind or requeue.

## Dependencies and Integration Points

It includes quiesce memory/message headers and Gluster timer definitions, and it relies on Gluster list, lock, fd, loc, dict, iobuf, flock, xattrop, and seek types.

## Risks and Edge Cases

Because `quiesce_local_t` stores many borrowed or copied pointer types, each fop wrapper must ref/copy exactly the fields its callback will use. Missing cleanup for any populated field risks leaks, while storing borrowed pointers for queued retries risks use-after-free.

## Test Signals

Compile coverage plus fop-specific retry tests should validate that every populated `quiesce_local_t` field is cleaned and that failover list entries are allocated, marked tried, and freed correctly.
