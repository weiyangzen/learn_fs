# sources/distributed-fs/ceph-client/fs/xfs/scrub/dabtree.h

Purpose: Declares the shared scrub interface and traversal state for XFS directory/attribute btrees.

Important APIs, types, and functions: Defines `struct xchk_da_btree`, which embeds `xfs_da_args`, per-level hash and max-record arrays, `xfs_da_state`, scrub context, private callback data, expected block bounds, and tree level. Defines callback type `xchk_da_btree_rec_fn` and declares `xchk_da_process_error()`, `xchk_da_set_corrupt()`, `xchk_da_set_preen()`, `xchk_da_btree_hash()`, and `xchk_da_btree()`.

Control flow: Directory and attribute scrubbers call `xchk_da_btree()` with the fork id and a leaf-record callback. The callback receives the active `struct xchk_da_btree` and level, and can use the stored DA state/path to inspect the current leaf entry.

State and persistence: The struct captures only transient traversal state. `lowest` and `highest` constrain legal DA block addresses for directory trees while attr trees leave the upper bound open.

Dependencies and integration points: Included by DA btree clients such as `dir.c` and attr scrubbers. It depends on `xfs_da_args`, `xfs_da_state`, scrub context, and DA geometry constants.

Risks and test signals: API risks include duplicate declaration of `xchk_da_set_preen()` and callback misuse if callers assume a leaf layout inconsistent with `blk->magic`. Test all callers with directory data fork and attr fork btrees, including short-format forks where the walker must return without invoking callbacks.
