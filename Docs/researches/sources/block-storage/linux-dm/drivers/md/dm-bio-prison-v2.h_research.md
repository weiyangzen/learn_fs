# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.h

Declares the v2 bio-prison interface. Compared with v1, cells carry `exclusive_lock`, `exclusive_level`, `shared_count`, a quiesce continuation, rb-tree node, key, and detained bio list.

The API models two lock families. Shared locks are associated with bios and may be granted immediately or detained; callers drop them via `dm_cell_put_v2()`. Exclusive locks are bio-less, have lock levels, receive priority, and can force quiescing before work proceeds.

Return values are part of the contract: shared get returns true when granted; exclusive lock/promote return `<0` for error, `0` for locked without quiescing, and `1` for locked with quiescing required. Unlock returns whether the caller regains cell ownership and should free it.

The prison must be globally initialized with `dm_bio_prison_init_v2()` and torn down with `dm_bio_prison_exit_v2()`, while each prison instance is created with a workqueue used for deferred continuations.
