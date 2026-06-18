# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-mem-types.h

## Purpose
This header defines marker-specific memory accounting IDs used by GlusterFS allocation macros.

## Important APIs, Types, And Functions
The enum `gf_marker_mem_types_` starts at `gf_common_mt_end + 1` and defines accounting buckets for marker config, locs, volume marks, int64 allocations, quota inode contexts, marker inode contexts, contribution nodes, quota metadata, quota synctask args, and `gf_marker_mt_end`.

## Control Flow And State
There is no executable control flow. The enum values are consumed by `GF_CALLOC`, `GF_MALLOC`, and related macros in marker and quota code to attribute allocations.

## Dependencies And Integration Points
The file depends on `<glusterfs/mem-types.h>` and is included by marker quota headers and sources. It must remain consistent with `xlator_mem_acct_init` usage in the broader marker translator.

## Risks And Test Signals
Adding new marker allocation classes should happen before `gf_marker_mt_end`. Duplicating or reordering values can confuse memory accounting. Test signals are successful compilation and memory-accounting initialization.
