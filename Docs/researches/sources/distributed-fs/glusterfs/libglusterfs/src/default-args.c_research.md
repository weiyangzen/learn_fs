# sources/distributed-fs/glusterfs/libglusterfs/src/default-args.c

## Purpose
This file captures GlusterFS translator FOP arguments and callback results into `default_args_t` and `default_args_cbk_t` structures. It is used when operations need to be resumed, replayed, wound through default paths, or stored across asynchronous boundaries.

## Important APIs, types, and functions
The exported surface is a large family of `args_*_store()` and `args_*_cbk_store()` functions for lookup, stat, create, open, read/write, xattr, locks, readdir, setattr, fallocate, discard, zerofill, ipc, seek, active lock migration, leases, icreate, namelink, and copy-file-range. Cleanup helpers are `args_wipe()`, `args_cbk_wipe()`, and `args_cbk_init()`.

## Control flow
Each store function copies scalar arguments, duplicates `loc_t` through `loc_copy()`, references `fd_t`, `inode_t`, `dict_t`, and `iobref` objects, duplicates strings with `gf_strdup()`, and duplicates iovec or checksum buffers when needed. Callback store functions capture `op_ret`, `op_errno`, returned `iatt` structures, xdata, directory entries, and lock lists. Wipe functions release references and heap buffers after the captured call state is consumed.

## State and persistence behavior
The file creates only in-memory retained call state. Persistence is via referenced GlusterFS objects and duplicated buffers inside the provided args structure. Correct lifetime depends on callers invoking the matching wipe function after use. Directory entry and lock-list copies are stored in embedded linked lists.

## Dependencies and integration points
It depends on `glusterfs/defaults.h` and many core object ownership helpers: `loc_copy`, `loc_wipe`, `dict_ref`, `fd_ref`, `inode_ref`, `iobref_ref`, `iov_dup`, `gf_dirent_for_name2`, `entry_copy`, `gf_flock_copy`, and list macros. Default translators and stack-resume logic consume these snapshots.

## Risks and edge cases
Most functions return 0 even if a nested allocation fails, except selected lock-list helpers. Some functions dereference required inputs without validation, such as `fd_ref(fd)` or `iobref_ref(iobref)` in paths where callers are expected to pass non-NULL values. Partial failures while copying directory entries or lock migration entries can leave partially populated lists for cleanup. Ownership distinctions between borrowed scalars and referenced objects are critical.

## Test signals
Tests should verify every store/wipe pair under normal and NULL-optional arguments, reference-count increments/decrements, deep copies of iovec, directory entries, checksums, and lock migration lists, and fault-injection behavior for allocation failure mid-copy. Replay/resume tests should confirm captured args remain valid after original caller-owned inputs are released.
