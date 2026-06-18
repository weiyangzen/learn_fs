# sources/distributed-fs/ceph-client/security/landlock/object.c

## Purpose

`object.c` implements generic Landlock object lifetime management for kernel objects referenced by rules, currently primarily inodes. It provides reference counting, locking, underlying-object release callbacks, and RCU freeing.

## Important APIs, Types, and Functions

`landlock_create_object()` allocates and initializes a `struct landlock_object` with usage count, spinlock, underops, and underlying object pointer. `landlock_put_object()` decrements usage and, when it reaches zero, locks the object, calls `underops->release()` with the lock held, and frees the object via `kfree_rcu()`.

## Control Flow

Rules and temporary operations call `landlock_get_object()` to pin objects and `landlock_put_object()` to release them. The final put uses `refcount_dec_and_lock()` so the transition to zero synchronizes with weak-pointer cleanup in filesystem code.

## State and Persistence Behavior

Object state persists while at least one rule or operation references it. The underlying object pointer is cleared by provider-specific release logic. RCU freeing allows lockless readers to observe object metadata safely while references drain.

## Dependencies and Integration Points

The generic object layer depends on provider callbacks declared in `object.h`; `fs.c` supplies inode release operations. It integrates with ruleset rule keys.

## Risks and Test Signals

Final put can sleep because provider release may call `iput()`, so callers must be in sleepable context. Lock ordering with inode locks is critical. Test concurrent rule insertion/removal, unmount cleanup, and KASAN/KCSAN lifetime stress.
