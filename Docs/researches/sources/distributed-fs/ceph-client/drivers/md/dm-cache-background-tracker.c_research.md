# sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.c

## Purpose
`dm-cache-background-tracker.c` tracks pending cache policy background work for the DM cache target. It de-duplicates work by origin block, caps the amount of outstanding work, separates queued and issued work, and maintains counters for promotions, writebacks, and demotions.

## Important APIs, Types, and Functions
The private `struct background_tracker` stores `max_work`, atomic pending counters, `issued` and `queued` lists, and an rb-tree keyed by `policy_work.oblock`. Public functions are `btracker_create()`, `btracker_destroy()`, `btracker_queue()`, `btracker_issue()`, `btracker_complete()`, `btracker_nr_demotions_queued()`, and `btracker_promotion_already_present()`. The exported global `btracker_work_cache` supplies `struct bt_work` allocations.

## Control Flow
`btracker_queue()` allocates a `bt_work`, copies the policy work, inserts it in the rb-tree if no work for that origin block is already pending, and then places it either on `issued` when the caller wants the work pointer immediately or on `queued` for later issue. `btracker_issue()` moves the first queued item to `issued`. `btracker_complete()` uses `container_of()` on the policy work pointer, decrements counters, erases the rb-tree node, unlinks the list entry, and frees the object.

## State and Persistence
All state is volatile and expected to be protected by the caller, normally the policy spinlock. The rb-tree represents every pending queued or issued work item so duplicate origin-block migrations are rejected until completion. Atomic counters allow quick policy decisions such as counting queued demotions for free-space targets.

## Dependencies and Integration Points
The tracker depends on `dm-cache-policy.h` for `struct policy_work` and operation values, Linux lists/rbtrees/atomics/slab caches, and DM logging. The SMQ policy owns a tracker and calls it while deciding promotions, demotions, and writebacks. The cache target later performs the returned `policy_work` and calls back into policy completion, which completes the tracker entry.

## Risks and Edge Cases
The header explicitly says there is no internal locking; callers must serialize every operation. `btracker_destroy()` asserts that no issued work remains, so policy teardown must first drain or complete issued operations. Duplicate work returns `-EINVAL` after freeing the second allocation, which policy callers treat as a benign race. Reaching `max_work` returns `-ENOMEM`, so callers must restore entry queue state when queueing fails.

## Test Signals
Tests should cover duplicate oblock queue rejection, queue-to-issued transitions, immediate issue through the `pwork` argument, correct pending counters by work type, max-work backpressure, destroy with queued but unissued work, and destroy assertions catching leaked issued work.
