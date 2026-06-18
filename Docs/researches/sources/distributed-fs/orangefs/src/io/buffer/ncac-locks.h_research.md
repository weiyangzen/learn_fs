# sources/distributed-fs/orangefs/src/io/buffer/ncac-locks.h

## Purpose
Maps NCAC lock names to generic mutex operations.

## Important APIs, Types, And Functions
Includes `gen-locks.h` and defines `spin_lock_init`, `cache_lock`, `cache_unlock`, `inode_lock`, `inode_unlock`, `list_lock`, and `list_unlock` as `gen_mutex_*` wrappers.

## Control Flow
Buffer-cache code uses semantic lock macros for request lists, inodes, and cache stacks while all are implemented as generic mutexes.

## State And Persistence
No state is defined here. Lock objects are `gen_mutex_t` fields in NCAC structures.

## Dependencies And Integration Points
Used by `internal.h` and therefore all NCAC code. It depends on the OrangeFS generic lock abstraction.

## Risks And Test Signals
Risks include the misleading `spin_lock` name despite mutex semantics and no try-lock/read-write distinction. Threaded cache tests should validate absence of deadlocks under inode/cache/list lock ordering.
