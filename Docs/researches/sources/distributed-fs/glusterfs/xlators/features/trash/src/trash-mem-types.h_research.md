# sources/distributed-fs/glusterfs/xlators/features/trash/src/trash-mem-types.h

## Purpose
Defines trash translator memory-accounting categories.

## Important APIs, Types, and Functions
- `enum gf_trash_mem_types_` starts at `gf_common_mt_end + 1`.
- Categories include `gf_trash_mt_trash_private_t`, `gf_trash_mt_char`, `gf_trash_mt_uuid`, `gf_trash_mt_trash_elim_path`, and `gf_trash_mt_end`.

## Control Flow
No runtime control flow. Values are consumed by allocation calls and `xlator_mem_acct_init()`.

## State and Persistence
No state. Allocation categories become part of runtime memory accounting output.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `trash.c` for private state, path strings, UUID storage, and eliminate-path nodes.

## Risks
Changing enum order can confuse memory accounting. New allocation classes should be appended before `gf_trash_mt_end`.

## Test Signals
Compile-time usage and memory-accounting/statedump output should show trash categories.
