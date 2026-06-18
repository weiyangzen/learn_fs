# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/ioc-mem-types.h

## Purpose
Defines io-cache-specific memory accounting type IDs.

## Important APIs, types, and functions
`enum gf_ioc_mem_types_` starts at `gf_common_mt_end + 1` and names allocation classes for iovecs, tables, strings, wait queues, priorities, list heads, call pools, inodes, fill records, and pages.

## Control flow
No runtime control flow exists. `mem_acct_init()` in `io-cache.c` registers up to `gf_ioc_mt_end`, and allocation sites pass these enum values to `GF_CALLOC`, `GF_MALLOC`, or related helpers.

## State and persistence behavior
The IDs feed runtime memory accounting. They are not persisted but affect diagnostics and leak attribution.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with Gluster's xlator memory accounting subsystem.

## Risks and test signals
Risks are enum overlap with common types, missing new allocation categories, or changing IDs in ways that confuse diagnostics. Test signals include successful `xlator_mem_acct_init()`, memory statedump categories, and leak tests for page/fill/waitq paths.
