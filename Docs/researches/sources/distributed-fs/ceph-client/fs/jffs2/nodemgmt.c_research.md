# sources/distributed-fs/ceph-client/fs/jffs2/nodemgmt.c

## Purpose

`nodemgmt.c` owns the core physical-node allocation and obsolescence machinery for JFFS2. It reserves writable space in eraseblocks, chooses and closes `c->nextblock`, links newly written raw node references into eraseblock and inode accounting, marks old nodes obsolete, and decides when the garbage-collection thread should wake. It is the bridge between high-level write operations in `write.c`, mount-time accounting from `scan.c`, summary handling, and erase/GC scheduling.

## Important APIs, Types, And Functions

The main exported entry points are `jffs2_reserve_space()`, `jffs2_reserve_space_gc()`, `jffs2_add_physical_node_ref()`, `jffs2_complete_reservation()`, `jffs2_mark_node_obsolete()`, and `jffs2_thread_should_wake()`. They work on `struct jffs2_sb_info`, `struct jffs2_eraseblock`, `struct jffs2_raw_node_ref`, and inode caches from `nodelist.h`.

`jffs2_rp_can_write()` enforces the reserved-pool mount option, allowing privileged `CAP_SYS_RESOURCE` writers to proceed when ordinary writes would consume the reserve. `jffs2_find_nextblock()` pulls a block from `free_list`, may force erases or write-buffer flushes, and resets collected summaries for the newly selected block. `jffs2_do_reserve_space()` handles summary reservation, end-of-block padding, cleanmarker obsolescence, and returns the usable length in the current block.

`jffs2_mark_node_obsolete()` is the most stateful routine. It moves node length from unchecked or used accounting to dirty or wasted accounting, refiles eraseblocks across clean, dirty, very-dirty, erasable, erase-pending, and write-buffer-pending lists, optionally clears `JFFS2_NODE_ACCURATE` on NOR-like media, and removes obsolete refs from inode/xattr chains when safe.

## Control Flow

Normal writers call `jffs2_reserve_space()`, which pads the minimum size, takes `alloc_sem`, then works under `erase_completion_lock`. It first applies reserved-pool policy, then loops while there are not enough free or erasing blocks. The loop checks whether enough dirty or possibly available space exists, triggers `jffs2_garbage_collect_pass()`, may sleep on `erase_wait`, and aborts on signals. Once block pressure is acceptable it calls `jffs2_do_reserve_space()`, preallocates raw node refs for the selected nextblock, and keeps `alloc_sem` held until `jffs2_complete_reservation()`.

GC uses `jffs2_reserve_space_gc()`, which repeatedly calls `jffs2_do_reserve_space()` without taking `alloc_sem` itself and yields on `-EAGAIN`. Both reservation paths depend on `jffs2_do_reserve_space()` to either reuse the existing nextblock, write a summary node and close it, waste insufficient tail space, or choose a new free block.

After a physical flash write, writers call `jffs2_add_physical_node_ref()` to link the node at the current write offset. If the block is now full and clean, it may flush the write buffer and move the block to `clean_list`. `jffs2_complete_reservation()` then wakes GC and releases `alloc_sem`.

## State And Persistence Behavior

This file maintains persistent-space accounting: `free_size`, `used_size`, `dirty_size`, `wasted_size`, `unchecked_size`, `erasing_size`, per-block equivalents, and list membership. It also changes medium state on media where obsolete nodes can be physically marked by clearing `JFFS2_NODE_ACCURATE` in the node header. On write-buffered/NAND media it cannot rely on in-place marking, so logical refs and deletion nodes carry more of the persistence semantics.

Summary state is integrated in reservation. A nextblock can reserve room for `c->summary->sum_size`, the incoming node summary size, and `JFFS2_SUMMARY_FRAME_SIZE`; if the node no longer fits, `jffs2_sum_write_sumnode()` is called and the block is closed before selecting another block.

## Dependencies And Integration Points

The code depends on MTD read/write through `jffs2_flash_read()` and `jffs2_flash_write()`, GC through `jffs2_garbage_collect_pass()` and `jffs2_garbage_collect_trigger()`, erase scheduling through `jffs2_erase_pending_blocks()`, summary APIs from `summary.h`, write-buffer helpers such as `jffs2_wbuf_dirty()` and `jffs2_flush_wbuf_pad()`, and inode/xattr cache release helpers. High-level file operations in `write.c` rely on its reservation and obsolescence contract.

## Risks And Edge Cases

The main risks are accounting drift and list corruption. Many branches manually move byte counts between global and per-block buckets, and debug paranoia checks are important signals. `jffs2_add_physical_node_ref()` rejects non-obsolete refs written anywhere other than the current nextblock write offset. `jffs2_mark_node_obsolete()` has subtle media-dependent locking: `erase_free_sem` is only taken when it may physically mark obsolete and release refs, and scanning/building modes deliberately avoid list changes or medium writes.

Space-pressure behavior is also sensitive. Incorrect `dirty`, `avail`, or reserve-block calculations can produce endless GC loops or premature `-ENOSPC`. Summary writes can be disabled for a block if there is not enough room, and write-buffered erase-pending blocks require flush coordination before they can be reused.

## Test Signals

Useful tests include forced low-free-space writes, deletion writes under reserve-pool pressure, GC-trigger wakeups, summary-enabled block closure, write-buffer tail padding, NOR obsolete marking, NAND/no-mark-obsolete behavior, and fault injection for failed flash reads/writes during obsolescence. Assertions and debug checks around `jffs2_dbg_acct_sanity_check*`, unexpected nextblock offsets, and list transitions are high-value runtime signals.
