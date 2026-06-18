# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.h

## Purpose
`marker-quota.h` defines the marker quota data model, xattr key macros, allocation helpers, and public transaction APIs used by the marker translator.

## Important APIs, Types, And Functions
Key constants are `QUOTA_XATTR_PREFIX`, `QUOTA_DIRTY_KEY`, `CONTRIBUTION`, `QUOTA_KEY_MAX`, and `READDIR_BUF`. Key-building macros include `GET_QUOTA_KEY`, `GET_CONTRI_KEY`, and `GET_SIZE_KEY`, which add version suffixes from `marker_conf_t`. Allocation macros include `QUOTA_ALLOC` and `QUOTA_ALLOC_OR_GOTO`.

Core types are `quota_inode_ctx_t`, `quota_synctask_t`, and `inode_contribution_t`. Public prototypes expose xattr request/inspection, quota update transactions, xattr creation, parent size reduction, and quota forget cleanup.

## Control Flow And State
The header defines state containers but no executable control flow. `quota_inode_ctx_t` stores current size, file count, directory count, dirty flag, transaction status flags, a lock, and contribution list. `quota_synctask_t` packages a translator, loc, contribution delta, nlink, and optional call stub for async work. `inode_contribution_t` tracks a parent gfid's contribution and is refcounted.

## Persistence Behavior
The macros define persistent trusted xattr names for quota metadata. Version-aware key construction means the same logic can address different quota schema generations.

## Dependencies And Integration Points
It depends on xlator types, marker memory types, GlusterFS refcounting, quota common utilities, and call stubs. It is included by marker quota source and helper files and forms their shared contract.

## Risks And Test Signals
Macro safety is important because key buffers are fixed at `QUOTA_KEY_MAX`. The `QUOTA_ALLOC` macro appears to pass `sizeof(type)` as the count and `1` as the size, which is equivalent in total bytes but unusual. Tests should cover key construction for versioned and unversioned volumes, root contribution keys, and memory-accounted allocation paths.
