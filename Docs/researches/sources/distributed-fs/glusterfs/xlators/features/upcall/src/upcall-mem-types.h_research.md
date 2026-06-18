# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-mem-types.h

## Purpose
Defines memory-accounting categories for upcall.

## Important APIs, Types, and Functions
- `enum gf_upcall_mem_types_` includes `gf_upcall_mt_conf_t`, `gf_upcall_mt_private_t`, `gf_upcall_mt_upcall_inode_ctx_t`, `gf_upcall_mt_upcall_client_entry_t`, and `gf_upcall_mt_end`.

## Control Flow
No runtime control flow.

## State and Persistence
No mutable state. Categories classify allocations in memory accounting.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `upcall.c` and `upcall-internal.c` allocations and `xlator_mem_acct_init()`.

## Risks
Enum reordering can confuse memory accounting; append new categories before the end marker.

## Test Signals
Compile and statedump/memory-accounting checks for upcall allocations.
