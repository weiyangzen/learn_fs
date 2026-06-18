# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.c

## Purpose
`marker-common.c` provides shared inode-context allocation for the marker translator. It creates `marker_inode_ctx_t` objects and guarantees an inode has a marker context attached.

## Important APIs, Types, And Functions
`marker_inode_ctx_new` allocates a zeroed `marker_inode_ctx_t` with `quota_ctx` initially `NULL`. `marker_force_inode_ctx_get` retrieves the marker inode context from `inode_ctx`; if absent, it allocates one and stores it under the translator key.

## Control Flow
`marker_force_inode_ctx_get` locks `inode->lock`, attempts `__inode_ctx_get`, and either returns the existing context or allocates and installs a new one via `__inode_ctx_put`. On install failure it frees the new context before unlocking.

## State And Persistence Behavior
State is per-inode in-memory translator context. The marker context owns the pointer to quota-specific context but this file does not allocate that nested quota context. There is no disk persistence.

## Dependencies And Integration Points
It depends on `marker.h` for `marker_inode_ctx_t`, GlusterFS memory accounting through `gf_marker_mt_marker_inode_ctx_t`, and inode context APIs. `marker-quota-helper.c` uses it before creating quota inode contexts.

## Risks And Test Signals
Correct locking is critical because multiple operations may race to create marker contexts. Tests should exercise repeated context creation on the same inode and allocation failure paths. Consumers must free nested quota state during forget paths; this helper only manages the wrapper.
