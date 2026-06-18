# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.c

This file implements low-level B-tree node writeback.

Key flow:
- `__bch2_btree_node_write()` atomically claims dirty nodes, builds a bounce buffer containing sorted unwritten keys and required whiteouts, validates metadata, encrypts/checksums the bset, and submits replica writes.
- Write completion updates IO accounting, records device failures, frees bounce buffers, and queues post-write work.
- Post-write work updates the B-tree pointer after first writes or degraded writes and then clears/rearms node write state.
- `__btree_node_write_done()` drops journal pins, handles `will_make_reachable`, re-arms writes if the node was dirtied again, or transitions the node clean.
- `bch2_btree_post_write_cleanup()` compacts written bsets, drops whiteouts, initializes the next writable bset, and rebuilds aux trees under write lock.
- `bch2_btree_init_next()` creates a new unwritten bset, compacting or writing first if the node is full.
- Flush helpers wait for all read/write in-flight bits, including freeable nodes no longer in the rhashtable.
- Cancel logic clears dirty nodes and drains writes when journal error/emergency read-only prevents clean shutdown.

Important invariants:
- First writes correspond to nodes not yet reachable; later writes must not run while `will_make_reachable` is set.
- A write may be rearmed if the node became dirty again before completion.
- Journal errors prevent submitting further B-tree writes to avoid exposing unjournaled updates.
- Writeback validation failure marks the node no-evict and can force emergency read-only.

Dependencies include read/checksum compatibility, sort/whiteout compaction, data write submission, reconciliation triggers, journal reclaim, cache state transitions, and async object tracking.
