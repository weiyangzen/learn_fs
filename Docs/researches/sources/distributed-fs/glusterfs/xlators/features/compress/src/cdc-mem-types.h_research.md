# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-mem-types.h

## Purpose
Defines memory accounting tags for the CDC compression translator.

## Important APIs, types, and functions
Enum `gf_cdc_mem_types` defines tags for private state, vectors, gzip trailer, and range end.

## Control flow
`mem_acct_init()` in `cdc.c` registers `gf_cdc_mt_end`.

## State and persistence behavior
No persistence; affects memory diagnostics for CDC allocations.

## Dependencies and integration points
Includes GlusterFS common memory types and is used by `cdc.c` and `cdc-helper.c`.

## Risks and test signals
Low risk. Test memory accounting on compression/decompression paths, especially trailer allocation.
