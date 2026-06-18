# sources/distributed-fs/ceph-client/fs/jffs2/erase.c

## Purpose
`erase.c` manages eraseblock erasure, erase completion verification, cleanmarker writing, bad-block handling, and removal of raw node references belonging to blocks being erased. It is the bridge between JFFS2 GC/accounting lists and MTD erase/read/write operations.

## Important APIs, Types, And Functions
The public functions are `jffs2_erase_pending_blocks()` and `jffs2_free_jeb_node_refs()`. Internal helpers include `jffs2_erase_block()`, `jffs2_erase_succeeded()`, `jffs2_erase_failed()`, `jffs2_remove_node_refs_from_ino_list()`, `jffs2_block_check_erase()`, and `jffs2_mark_erased_block()`.

## Control Flow
`jffs2_erase_pending_blocks()` first processes completed erases by moving them to checking and calling `jffs2_mark_erased_block()`, then starts pending erases by moving block accounting from dirty/used/free/wasted into erasing state, freeing node refs, and calling MTD erase. Successful erases move to `erase_complete_list`; failed erases are retried for transient errors or moved to bad lists. Marking an erased block verifies all bytes are `0xff`, writes an in-band or OOB cleanmarker when needed, links a cleanmarker node ref, and moves the block to `free_list`.

## State And Persistence Behavior
Persistent effects are physical flash erase and optional cleanmarker writes. In-core effects update superblock size buckets, eraseblock lists, bad-block lists, `nr_erasing_blocks`, `nr_free_blocks`, raw-node-ref chains, inode-cache node lists, and wakeups on `erase_wait`. `erase_completion_lock` and `erase_free_sem` protect list/accounting and ref removal.

## Dependencies And Integration Points
It depends on MTD `mtd_erase()`, `mtd_point()`, `mtd_read()`, cleanmarker helpers from write-buffer/NAND code, CRC32, raw-node-ref allocation/linking, and GC trigger/wakeup paths.

## Risks And Test Signals
Risks include accounting drift across error paths, removing refs while inode/xattr code still observes them, bad-block policy differences for NAND, and verification cost on large eraseblocks. Tests should simulate erase success, `-ENOMEM`/`-EAGAIN` retries, permanent failures, cleanmarker write failure, short reads, non-erased bytes, NAND bad-block updates, and concurrent GC/list wakeups.
