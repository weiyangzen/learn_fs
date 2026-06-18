# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-mem-types.h

## Purpose
Defines AFR-specific memory allocation type IDs used by Gluster's memory accounting and debugging system.

## Important APIs, types, and functions
The `gf_afr_mem_types_` enum starts at `gf_common_mt_end + 1` and assigns IDs for AFR fd context, private state, integer/char helpers, xattr keys, dict/xlator arrays, inode context, self-heal daemon events, replies, healer structures, split-brain choice timeout/status, empty brick handling, lock-heal info, and `gf_lock`.

## Control flow
No runtime control flow exists in this header. Allocation sites pass these enum values to `GF_MALLOC`, `GF_CALLOC`, or related macros, allowing statedump and leak diagnostics to classify AFR allocations.

## State and persistence behavior
No persistent state is stored. The enum values are part of diagnostic ABI within the process; changing or reordering values can make memory accounting harder to interpret.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` for common allocator IDs. Used throughout AFR implementation files wherever typed allocation is performed.

## Risks and test signals
Risks include reusing or reordering IDs, forgetting to add a type for new long-lived structures, or using a misleading allocation type. Test signals are clean builds, memory-accounting statedumps showing expected buckets, and leak tests that can attribute AFR allocations.
