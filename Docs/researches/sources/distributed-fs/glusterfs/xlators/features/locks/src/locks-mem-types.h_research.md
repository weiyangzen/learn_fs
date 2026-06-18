# sources/distributed-fs/glusterfs/xlators/features/locks/src/locks-mem-types.h

## Purpose

`locks-mem-types.h` defines the memory-accounting type identifiers used by the posix-locks translator when allocating its private structures through Gluster's `GF_MALLOC`/`GF_CALLOC` wrappers.

## Important APIs, types, and functions

The only exported type is `enum gf_locks_mem_types_`, starting at `gf_common_mt_end + 1` and assigning identifiers for:

- `pl_dom_list_t`
- `pl_inode_t`
- `posix_lock_t`
- `pl_entry_lock_t`
- `pl_inode_lock_t`
- `pl_rw_req_t`
- `posix_locks_private_t`
- `pl_fdctx_t`
- `pl_meta_lock_t`
- `gf_locks_mt_end`

## Control flow

There is no runtime control flow. The enum values are consumed by allocation calls throughout the lock translator to classify memory usage.

## State and persistence behavior

The file contributes no runtime state and no persistence. It affects diagnostics, memory accounting, and leak attribution for lock-related allocations.

## Dependencies and integration points

It includes `<glusterfs/mem-types.h>` for `gf_common_mt_end` and is included by `locks.h`, which makes these identifiers available to all lock implementation files. Adding a new allocated lock structure should add a corresponding enum value before `gf_locks_mt_end`.

## Risks and edge cases

Enum ordering matters for Gluster memory accounting. Reordering existing values can make diagnostics harder to compare across versions; new values should be appended before the end marker. The guard name is generic enough for this module but must remain consistent with `locks.h`.

## Test signals

Build tests catch missing enum names when allocation sites use them. Runtime memory-accounting or leak tests should show allocations under the expected posix-locks categories.
