# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.h

## Purpose
`rcbag.h` declares the opaque refcount bag API used by scrub/repair code.

## Important APIs, Types, And Functions
It forward-declares `struct rcbag` and exposes initialization, destruction, add, count, next-edge, remove-ending-at, and dump functions.

## Control Flow
Callers create a bag with `rcbag_init`, add rmap records while scanning, repeatedly ask for next refcount edges, remove records ending at each edge, optionally dump diagnostics, and free the bag.

## State And Persistence Behavior
The API represents volatile in-memory btree state. Persistence is limited to the caller's eventual repair decisions.

## Dependencies And Integration Points
It depends on XFS mount, transaction, buftarg, and rmap record types. Implementation requires in-memory btree support through `rcbag_btree`.

## Risks And Edge Cases
The header does not expose feature guards itself, so build configuration must ensure callers are only present when the implementation is available. Ownership and lifetime of `struct rcbag **` are explicit: `rcbag_free` nulls the caller pointer.

## Test Signals
API-level tests should verify init/free lifetime, count behavior after duplicates, and next-edge/remove sequencing.
