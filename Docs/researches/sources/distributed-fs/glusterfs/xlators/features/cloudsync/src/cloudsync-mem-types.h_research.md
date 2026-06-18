# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-mem-types.h

## Purpose
Defines memory accounting tags for the cloudsync translator.

## Important APIs, types, and functions
Enum values cover `cs_private_t`, `cs_remote_stores`, `cs_inode_ctx_t`, and `cs_loc_xattr_t`, ending at `gf_cs_mt_end`.

## Control flow
`cs_mem_acct_init()` registers the range with `xlator_mem_acct_init()`. Allocations in cloudsync use these tags for accounting and diagnostics.

## State and persistence behavior
No runtime persistence. It affects memory accounting categorization.

## Dependencies and integration points
Includes GlusterFS common memory type definitions. Used by `cloudsync.c` and `cloudsync-common.c`.

## Risks and test signals
Memory tag overlap can corrupt accounting. Test by enabling memory accounting and checking cloudsync allocation classes during init, fop, and teardown paths.
