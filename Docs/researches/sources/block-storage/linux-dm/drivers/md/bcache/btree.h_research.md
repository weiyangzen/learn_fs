# File Research: sources/block-storage/linux-dm/drivers/md/bcache/btree.h

## Purpose
Declares bcache btree node structures, btree write state, locking/traversal helpers, btree operation state, map APIs, key-buffer APIs, and GC/check entry points.

## Main Interfaces
- `struct btree_write`, `struct btree`, `struct btree_op`, and btree-check state structs.
- Node flag helpers for IO error, dirty, write-index, and journal-flush bits.
- Lock helpers `rw_lock()`/`rw_unlock()` and operation initializer `bch_btree_op_init()`.
- Recursion macros `bcache_btree()` and `bcache_btree_root()`.
- Public prototypes for node read/write, root set, node allocation/get, insert, GC, checking, mapping, keybuf, and bucket-use accounting.

## Control Flow
The macros hide recursive descent details: choose read versus write locks from `op->lock`, fetch child nodes from cache/disk, call the target implementation function, unlock, and restart on `-EINTR` at the root. Mapping constants select all nodes, leaf nodes, and optional end-key callbacks.

## State And Synchronization
Documents btree cache, IO, and locking rules. `struct btree` combines hash/list cache membership, key identity, parent, level, lock, write lock, IO closure, delayed work, and double-buffered write metadata.

## Integration Points
Included by `btree.c`, `debug.c`, `alloc.c`, and other bcache subsystems needing traversal or insertion. Depends on `bset.h` and `debug.h`.

## Notable Behaviors
- Interior-node keys point to child nodes and store the highest key in each child; the highest root range uses `MAX_KEY`.
- `op->lock` is the central mechanism for upgrading traversal locking when splits are required.
- `force_wake_up_gc()` makes GC likely by setting `sectors_to_gc` negative before waking the wait queue, but comments note it is not an absolute guarantee.

## Risks And Review Focus
- The recursion macros are control-flow-heavy and should be read as part of caller behavior.
- Incorrect `op->lock` values can lead to missed write locks or restart loops.
- `insert_lock()` is implemented in `btree.c` but used by root traversal macro in this header.
