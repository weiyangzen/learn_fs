# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-mem-types.h

## Purpose
Defines leases translator memory accounting IDs.

## Important APIs, Types, and Functions
`enum gf_leases_mem_types_` covers private state, client records, inode records, fd ctx, inode ctx, lease ID entries, blocked fop stubs, timer data, and an end sentinel.

## Control Flow
No control flow. Used by allocation sites and `xlator_mem_acct_init()`.

## State and Persistence
No runtime state; values label allocations.

## Dependencies and Integration Points
Includes GlusterFS common memory type definitions.

## Risks and Edge Cases
New leases allocations should add enum IDs to keep memory diagnostics useful. Values must remain beyond `gf_common_mt_end`.

## Test Signals
Build and memory-accounting reports should include leases allocation classes.
