# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.c

Implements a tracker for cache policy background work. It wraps `policy_work` in `bt_work`, maintains queued and issued lists, and uses an rb-tree keyed by origin block to prevent duplicate pending work for the same oblock.

The tracker counts pending promotions, writebacks, and demotions with atomics and enforces `max_work` before allocating from a `bt_work` slab cache. `btracker_queue()` inserts work into the pending rb-tree and either returns it as already issued via `pwork` or appends it to the queued list.

`btracker_issue()` moves queued work to issued; `btracker_complete()` updates stats, erases the pending rb-node, removes the list node, and frees the work object. Duplicate oblocks return `-EINVAL`; no available work returns `-ENODATA`; capacity/allocation failures return `-ENOMEM`.

The header comment notes lack of locking; callers are expected to serialize access, which the SMQ policy does with its policy spinlock.
