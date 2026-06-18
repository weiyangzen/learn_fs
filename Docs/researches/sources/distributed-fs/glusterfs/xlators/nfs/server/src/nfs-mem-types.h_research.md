# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-mem-types.h

## Purpose

`nfs-mem-types.h` assigns Gluster memory-accounting type IDs for the NFS translator and its protocol helpers. These IDs let allocations in mount, NFSv3, NLM, auth-cache, inode-context, and helper code be attributed under the NFS component in memory accounting and statedump output.

## Important APIs, types, and functions

The central type is `enum gf_nfs_mem_types_`, starting at `gf_common_mt_end + 1` and ending at `gf_nfs_mt_end`. Important entries include `gf_nfs_mt_nfs_state`, `gf_nfs_mt_nfs3_state`, `gf_nfs_mt_nfs3_fh`, `gf_nfs_mt_nfs_initer_list`, `gf_nfs_mt_xlator_t`, `gf_nfs_mt_inode_ctx`, auth-cache entries, NLM share/client structures, and generic `gf_nfs_mt_char`/`gf_nfs_mt_arr` utility buckets.

## Control flow

The header has no runtime control flow. It is consumed by allocation macros such as `GF_CALLOC`, `GF_MALLOC`, and mempool setup. `nfs.c` initializes accounting with `xlator_mem_acct_init(this, gf_nfs_mt_end)`, so every ID before `gf_nfs_mt_end` must remain valid.

## State and persistence behavior

Memory type IDs are process-local accounting metadata; they are not persisted. They influence diagnostics and leak attribution rather than behavior of the NFS protocol itself.

## Dependencies and integration points

The header depends on `<glusterfs/mem-types.h>` for the common base. It is included by `nfs.c`, `nfs3-helpers.c`, file-handle code, mount/NLM/auth modules, and any NFS allocation site that wants component-specific accounting.

## Risks and edge cases

- IDs must only be appended, not renumbered, if external diagnostics expect stable names.
- A missing or wrong allocation type will not usually break behavior, but it weakens leak and pressure analysis.
- `gf_nfs_mt_end` must remain the final enumerator passed to memory accounting initialization.

## Test signals

Build coverage catches duplicate or missing enum names. Runtime memory-accounting/statedump tests should show NFS allocations under expected buckets when NFS starts, serves requests, and shuts down.
