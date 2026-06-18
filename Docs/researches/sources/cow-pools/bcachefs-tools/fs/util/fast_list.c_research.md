# File Research: sources/cow-pools/bcachefs-tools/fs/util/fast_list.c

Implements a fast unordered list backed by a generic radix tree, IDA slot allocator, and per-CPU free-slot buffers. `fast_list_get_idx()` reserves a slot with allocation failures handled early, refilling the per-CPU buffer in batches. `fast_list_add()` reserves and stores an item; `fast_list_remove()` clears the radix slot and returns the index to the per-CPU buffer.

`fast_list_put_idx()` drains excess per-CPU buffered entries back to the IDA. Init sets up radix/IDA/percpu state; exit frees buffered slots, warns if live objects remain, destroys the IDA, and frees radix storage.
