# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-mem-types.h

## Purpose
Allocates changelog-specific memory accounting IDs above `gf_common_mt_end`.

## APIs, Types, and Functions
`enum gf_changelog_mem_types` defines IDs for xlator private state, strings, batches, runtime dispatcher data, inode ctx, RPC clients, libgfchangelog connection and entry state, rate-limit/listener state, changelog buffers, history data, lib call pools, events, event dispatchers, and an end marker.

## Control Flow, State, and Persistence
No control flow or persistent state. The IDs are used with `GF_CALLOC`, mem pools, and `xlator_mem_acct_init()` to attribute allocations.

## Dependencies and Integration
Includes `glusterfs/mem-types.h`. Used by both the xlator and libgfchangelog code, so IDs must remain stable enough for diagnostics across the shared component.

## Risks and Test Signals
Risks include collisions if `gf_common_mt_end` moves unexpectedly or new IDs are inserted without updating init bounds. Test signals are successful `xlator_mem_acct_init(..., gf_changelog_mt_end)` and allocation accounting reports showing expected buckets.
