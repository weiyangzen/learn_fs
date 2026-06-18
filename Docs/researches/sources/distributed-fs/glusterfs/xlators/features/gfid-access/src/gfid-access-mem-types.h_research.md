# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access-mem-types.h

## Purpose
Defines memory accounting tags for the gfid-access translator.

## Important APIs, types, and functions
Enum values reserve `gf_gfid_access_mt_priv_t`, `gf_gfid_access_mt_gfid_t`, and `gf_gfid_access_mt_end`.

## Control flow
The gfid-access implementation registers this range during memory-accounting initialization and uses the tags for private state and gfid allocations.

## State and persistence behavior
No durable state. It classifies allocations.

## Dependencies and integration points
Includes GlusterFS common memory type definitions and is compiled with `gfid-access.c`.

## Risks and test signals
The enum name is `gf_changelog_mem_types`, likely copied from another translator; this can confuse diagnostics but not necessarily compiled symbol behavior. Tests should check memory accounting names and compile warnings.
