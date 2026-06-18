# File Research: sources/block-storage/lvm2/libdm/regex/ttree.c

Purpose: implements a small ternary tree mapping fixed-length unsigned-integer key vectors to arbitrary data pointers.

Read coverage: complete file read, 118 lines.

Key responsibilities:
- Defines tree nodes with left, middle, and right links: left/right compare one key component, middle advances to the next key component.
- Creates `struct ttree` handles with a fixed key length and pool-backed allocation.
- Looks up keys by walking each key component through a binary-search branch, then descending through middle links.
- Inserts keys by creating missing component nodes and storing the supplied data pointer at the terminal node.

Important entry points:
- `ttree_create(struct dm_pool *mem, unsigned int klen)`
- `ttree_lookup(const struct ttree *tt, const unsigned int *key)`
- `ttree_insert(struct ttree *tt, const unsigned int *key, void *data)`

Dependencies:
- Uses `ttree.h` and libdm pool allocation helpers.

Risk and edge cases:
- `ttree_create()` rejects zero-length keys.
- Duplicate inserts replace terminal `data` without warning.
- No delete or rebalance exists; shape depends on key insertion order.
- The implementation casts away const in lookup to reuse pointer-to-pointer traversal.
