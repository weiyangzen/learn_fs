# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt-mem-types.h

## Purpose
Defines memory accounting tags for the CVLT plugin.

## Important APIs, types, and functions
Enum `libcvlt_mem_types_` reserves `gf_libcvlt_mt_cvlt_private_t` and `gf_libcvlt_mt_end`.

## Control flow
`mem_acct_init()` in `libcvlt.c` registers this range.

## State and persistence behavior
No runtime persistence; affects memory accounting for `archive_t`.

## Dependencies and integration points
Includes GlusterFS common memory types and is included by `libcvlt.h`.

## Risks and test signals
Low risk. Test memory accounting during CVLT init/fini and request allocation paths.
