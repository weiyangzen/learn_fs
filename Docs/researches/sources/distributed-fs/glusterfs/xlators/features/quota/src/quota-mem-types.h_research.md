# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-mem-types.h

## Purpose
`quota-mem-types.h` defines the memory accounting type IDs used by the quota and quotad translators. It reserves quota-specific allocation categories after `gf_common_mt_end` so GlusterFS memory accounting can attribute quota private state, inode context, dentry tracking, and quotad aggregator state.

## Important APIs and Types
- `enum gf_quota_mem_types_` declares:
  - `gf_quota_mt_quota_priv_t` for `quota_priv_t` allocations.
  - `gf_quota_mt_quota_inode_ctx_t` for per-inode quota state.
  - `gf_quota_mt_quota_dentry_t` for tracked parent/dentry list entries.
  - `gf_quota_mt_aggregator_state_t` for `quotad_aggregator_state_t`.
  - `gf_quota_mt_end`, passed to `xlator_mem_acct_init()`.

## Control Flow
There is no runtime flow in this header. It is consumed by `quota.c`, `quotad.c`, and helpers through allocation macros such as `QUOTA_ALLOC_OR_GOTO()` and direct `GF_CALLOC()`.

## State and Persistence
The values are compile-time identifiers only. They do not persist state, but they affect the labels attached to allocated quota objects in memory accounting and statedump diagnostics.

## Dependencies and Integration Points
The header depends on `<glusterfs/mem-types.h>`. `mem_acct_init()` in both quota and quotad calls `xlator_mem_acct_init(this, gf_quota_mt_end)`, so all enum values must remain below `gf_quota_mt_end`.

## Risks
Adding new quota allocation types without keeping `gf_quota_mt_end` last can break accounting coverage. Reusing IDs across components would make memory diagnostics ambiguous.

## Test Signals
Build coverage is the primary signal. Runtime statedump or memory accounting tests should show quota allocations under these categories when quota and quotad are active.
