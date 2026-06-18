# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/fd-lk.h

## Purpose
Defines per-fd POSIX lock tracking context used to remember and merge locks associated with a GlusterFS fd.

## APIs, Types, and Functions
`fd_lk_ctx_t` contains a lock list, atomic refcount, and `gf_lock_t`. `fd_lk_ctx_node_t` stores command, lock type, start/end offsets, list link, and original `gf_flock`. Helper macros stringify `F_UNLCK`, `F_RDLCK`, `F_WRLCK`, `F_SETLK`, `F_SETLKW`, and `F_GETLK`. APIs include `fd_lk_ctx_create()`, `fd_lk_ctx_ref()`, `fd_lk_ctx_unref()`, `fd_lk_insert_and_merge()`, and `fd_lk_ctx_empty()`.

## Control Flow, State, and Persistence
Lock state is process-local and tied to `fd_t->lk_ctx`. Insert/merge records new lock ranges, combines compatible ranges, and removes or adjusts unlocked ranges. Refcounting controls lifetime while the fd or lock migration code references the context.

## Dependencies and Integration
Depends on `locking.h`, `list.h`, `gf_flock`, and `fd.h`. It integrates with `GF_FOP_LK`, active lock migration, reconnect handling, and fd cleanup.

## Risks and Test Signals
Risks include off-by-one lock range merging, unlock-before-lock accounting, stale lock state after fd close, and thread races around `lk_list`. Test signals include overlapping lock merge tests, unlock split tests, migration/reconnect scenarios, refcount leak checks, and concurrency tests around fd lock updates.
