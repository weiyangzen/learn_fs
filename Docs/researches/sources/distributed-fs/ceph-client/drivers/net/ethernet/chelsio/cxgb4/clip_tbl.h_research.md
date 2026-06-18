# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.h

## Purpose
This header declares the CLIP table data structures and public functions used by cxgb4 components that need to manage local IP entries for offload.

## Important APIs, Types, And Functions
- `struct clip_entry` stores a per-address spinlock, `refcount_t`, list linkage, and an IPv4/IPv6 sockaddr union.
- `struct clip_tbl` stores firmware CLIP range metadata, an rwlock, free-entry count, free list, backing allocation, and flexible hash bucket array.
- `CLIPT_MIN_HASH_BUCKETS` enforces a minimum split hash table size.
- Prototypes expose initialization, cleanup, get/release, debug display, and root-device IPv6 update functions.

## Control Flow
The header itself has no control flow. Its structure layout drives `clip_tbl.c`: hash buckets and free list share the same `list` field in each entry, table-wide mutations are protected by `rwlock_t`, and final reference updates are additionally protected by the entry spinlock.

## State And Persistence
The declarations define in-memory driver state only. `clip_entry` instances are allocated as one backing array and recycled between hash lists and the free list. Firmware state is implied by callers, not represented directly beyond the address/refcount.

## Dependencies And Integration Points
It depends on Linux `refcount.h`, list/spinlock/rwlock/netdevice types supplied by includers, and `struct adapter`. It is included by `clip_tbl.c` and by driver code that holds `adapter->clipt` or invokes CLIP APIs.

## Risks
The flexible array is annotated with `__counted_by(clipt_size)`, so allocation must set `clipt_size` consistently before use. Because IPv4 and IPv6 share a union, callers must use the address family consistently. The same list node is used for both free and hash membership, so all transitions must be list-safe and lock-protected.

## Test Signals
Compile tests should cover configs with this header included from different translation units. Runtime validation comes from CLIP allocation/release tests, free-list count consistency, debug display, and lockdep during concurrent offload address operations.
