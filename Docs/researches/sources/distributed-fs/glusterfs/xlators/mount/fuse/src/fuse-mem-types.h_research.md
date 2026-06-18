# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-mem-types.h

## Purpose
Defines the FUSE mount translator's memory-accounting type range. The enum gives GlusterFS allocator call sites stable type identifiers for FUSE-specific objects so memory accounting can distinguish iovecs, bridge state, FD contexts, graph-switch helpers, gid lists, invalidation nodes, threads, timed messages, and interrupt records from common allocator classes.

## APIs, Types, and Functions
The only exported type is `enum gf_fuse_mem_types_`. It starts at `gf_common_mt_end + 1` and ends at `gf_fuse_mt_end`, matching Gluster's convention that each component owns a contiguous memory type block. Important values include `gf_fuse_mt_fuse_private_t`, `gf_fuse_mt_fuse_state_t`, `gf_fuse_mt_fd_ctx_t`, `gf_fuse_mt_graph_switch_args_t`, `gf_fuse_mt_gids_t`, and `gf_fuse_mt_interrupt_record_t`.

## Control Flow, State, and Persistence
There is no executable control flow. The enum is compile-time state consumed by allocation macros. Persistence is indirect: when memory accounting is enabled, allocations tagged with these identifiers are accumulated in GlusterFS runtime accounting data and logs.

## Dependencies and Integration
Depends on `<glusterfs/mem-types.h>` for `gf_common_mt_end`. It integrates with FUSE translator sources that call `GF_MALLOC`, `GF_CALLOC`, or related macros using FUSE memory type constants.

## Risks and Test Signals
Risks are mostly maintenance risks: enum values must stay after the common range, and new FUSE allocation classes need matching type additions before use. Test signals include successful FUSE translator builds with memory accounting enabled, leak/accounting reports showing these buckets, and compile failures if a type is renamed or removed while still referenced.
