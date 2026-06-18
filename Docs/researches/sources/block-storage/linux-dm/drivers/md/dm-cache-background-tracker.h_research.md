# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.h

Declares the background tracker used by cache policies. The API creates/destroys a tracker, queries queued writeback/demotion counts, queues work, issues queued work, completes issued work, and tests whether a promotion for an origin block is already pending.

The queue contract distinguishes duplicate work from allocation/capacity failure: `-EINVAL` means already queued, while `-ENOMEM` means it could not be queued for another reason. `btracker_issue()` returns `-ENODATA` when no work is available.

The file deliberately forward-declares tracker internals and includes `dm-cache-policy.h` for `struct policy_work` and block types. A FIXME explicitly calls out that locking semantics are undocumented.
