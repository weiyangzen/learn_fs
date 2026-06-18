<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c

## Purpose

`mmzone.c` implements the minimal node/zone functions declared by the simulator `linux/mmzone.h`.

## Important APIs, Types, and Functions

It defines `first_online_pgdat()` and `next_online_pgdat()` to return `NULL`, and `atomic_long_set(atomic_long_t *v, long i)` as an empty stub.

## Control Flow

Online-node iteration immediately terminates because the first iterator returns `NULL`. Atomic set call sites compile but do not alter storage.

## State and Persistence Behavior

No pgdat or atomic state is maintained by this file. It deliberately avoids modeling kernel zone lists.

## Dependencies and Integration Points

It includes `<linux/mmzone.h>` and links with memblock code that references online pgdat helpers or atomic zone counters.

## Risks and Edge Cases

Any future test that expects managed page accounting or online pgdat traversal will be under-modeled. The empty `atomic_long_set()` can hide state updates if memblock starts relying on its side effects in tested paths.

## Test Signals

Current tests should pass without iterating online pgdats. New failures or missing side effects around zone accounting indicate this shim needs a fuller implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c -->
