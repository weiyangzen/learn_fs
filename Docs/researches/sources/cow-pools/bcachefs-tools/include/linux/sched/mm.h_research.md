# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/mm.h

Implements memory-allocation-scope helpers by toggling bits in `current->flags`: `memalloc_noio_save/restore`, `memalloc_nofs_save/restore`, and `memalloc_noreclaim_save/restore`.

The save helper records only flags newly added by the scope, and restore clears those bits. This approximates kernel GFP inheritance scopes for userspace allocator shims.
