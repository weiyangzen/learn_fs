# File Research: sources/cow-pools/bcachefs-tools/include/linux/osq_lock.h

This header defines optimistic spin queue structures but disables real locking behavior. `struct optimistic_spin_node` and `struct optimistic_spin_queue` mirror kernel shapes, and `osq_lock_init()` initializes the tail to `OSQ_UNLOCKED_VAL`.

`osq_lock()` always returns false, `osq_unlock()` is a no-op, and `osq_is_locked()` checks whether the tail differs from unlocked. This satisfies code paths that reference OSQ without enabling optimistic spinning in user space.
