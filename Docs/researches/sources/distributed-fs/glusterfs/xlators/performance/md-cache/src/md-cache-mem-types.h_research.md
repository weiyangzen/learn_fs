# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/md-cache-mem-types.h

## Purpose
Defines md-cache-specific memory accounting categories.

## Important APIs, types, and functions
`enum gf_mdc_mem_types_` assigns allocation IDs for `mdc_local_t`, metadata cache objects, translator config, IPC/upcall helpers, and the enum end marker.

## Control flow
No executable control flow exists. The md-cache implementation uses these IDs through Gluster allocation macros after memory accounting init.

## State and persistence behavior
The IDs affect runtime diagnostics only and are not durable.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with the xlator memory accounting subsystem used by md-cache.

## Risks and test signals
Risks include overlapping IDs, missing categories for new md-cache allocations, and misleading leak reports. Test signals are successful md-cache `mem_acct_init()` and memory statedump output under these categories.
