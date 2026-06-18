# sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.h

## Purpose
`dm-cache-background-tracker.h` declares the background-work tracker interface used between DM cache policies and the cache target. It documents that the tracker is an unlocked mediator for policy-selected promotions, demotions, and writebacks.

## Important APIs, Types, and Functions
The header defines `struct bt_work`, with list linkage, rb-tree node, and embedded `struct policy_work`. It forward-declares `struct background_tracker`, exports `btracker_work_cache`, and declares create, destroy, queue, issue, complete, demotion-count, and promotion-presence functions.

## Control Flow
The header itself has no execution path, but its contract is that policies queue copied work, the target issues queued work through the same internal pointer, and completion gives that pointer back so the tracker can remove exactly the tracked object.

## State and Persistence
No persistent state is declared. The documented state model is in-memory only, with queued, issued, and pending-by-oblock membership maintained by the implementation.

## Dependencies and Integration Points
It includes `dm-cache-policy.h` for policy work definitions and Linux vmalloc/list/rbtree visibility through included kernel headers. It is consumed by `dm-cache-policy-smq.c` and implemented by `dm-cache-background-tracker.c`.

## Risks and Edge Cases
The no-locking warning is the main risk: using the API without a surrounding spinlock or equivalent can corrupt lists/rbtrees or double-complete work. Callers must pass the same `policy_work *` received from queue/issue into completion, because the pointer identifies the containing `bt_work`.

## Test Signals
Compile coverage should verify all policy users agree on `struct bt_work` layout. Runtime tests are the implementation tests: no duplicate promotions, no leaked issued work, and stable behavior under concurrent policy decisions protected by the policy lock.
