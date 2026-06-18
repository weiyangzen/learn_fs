# sources/distributed-fs/lustre-release/lustre/llite/dcache.c

## Purpose
`dcache.c` implements llite dentry operations and lookup-intent cleanup for Lustre-specific dentry validity and LDLM lock handling.

## Important APIs, Types, and Functions
`ll_d_init()`, `ll_release()`, `ll_dcompare()`, `ll_ddelete()`, and `ll_revalidate_dentry()` form `ll_d_ops`. `ll_intent_drop_lock()`, `ll_intent_release()`, `ll_lookup_finish_locks()`, `ll_prune_aliases()`, and `ll_revalidate_it_finish()` manage intent locks, request references, alias invalidation, and lookup completion.

## Control Flow
Dentry init allocates private data and marks entries invalid. Release clears `d_fsdata` and frees through RCU. Compare matches names but rejects invalid dentries except for mountpoints and in-progress parallel lookups. Revalidation first consults llcrypt, accepts parent-component lookups, handles symlink/foreign symlink rules, forces relookup under `LOOKUP_REVAL`, rejects RCU with `-ECHILD`, and otherwise performs statahead and directory-depth updates.

## State and Persistence Behavior
State is in-memory only: dentry private data, invalid flags, inode alias lists, lookup-intent lock modes/handles, and ptlrpc request references.

## Dependencies and Integration Points
The file integrates with VFS dentry operations, RCU, LDLM, ptlrpc, llcrypt dentry validation, statahead, and llite inode/FID helpers.

## Risks and Edge Cases
Intent locks must not be double-decremented, NFS can copy dentry ops leaving no private data, invalid dentries must still serialize parallel lookup, and revalidation differs across symlink, parent, RCU, and explicit revalidation paths.

## Test Signals
Test invalid dentry comparisons, parallel lookups, mountpoints, repeated intent release, open/create request drops, encrypted nokey revalidation, `LOOKUP_RCU`, `LOOKUP_PARENT`, `LOOKUP_REVAL`, symlink no-follow behavior, and alias pruning.
