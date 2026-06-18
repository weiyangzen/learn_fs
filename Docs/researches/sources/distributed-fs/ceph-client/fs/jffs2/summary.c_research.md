# sources/distributed-fs/ceph-client/fs/jffs2/summary.c

## Purpose

`summary.c` implements JFFS2 summary support. Summaries compactly describe the nodes in an eraseblock so mount scanning can reconstruct raw refs without reading and validating every node. The file also collects summary records during scanning/writing and writes summary nodes at the end of eraseblocks.

## Important APIs, Types, And Functions

Exported functions include `jffs2_sum_init()`, `jffs2_sum_exit()`, `jffs2_sum_add_padding_mem()`, `jffs2_sum_add_inode_mem()`, `jffs2_sum_add_dirent_mem()`, optional xattr/xref adders, `jffs2_sum_reset_collected()`, `jffs2_sum_disable_collecting()`, `jffs2_sum_is_disabled()`, `jffs2_sum_move_collected()`, `jffs2_sum_add_kvec()`, `jffs2_sum_scan_sumnode()`, and `jffs2_sum_write_sumnode()`.

Important internal helpers are `jffs2_sum_add_mem()`, `jffs2_sum_clean_collected()`, `sum_link_node_ref()`, `jffs2_sum_process_sum_data()`, and `jffs2_sum_write_data()`.

## Control Flow

Initialization allocates `c->summary` and a per-eraseblock write buffer capped by `MAX_SUMMARY_SIZE`. During full scan, `scan.c` calls `jffs2_sum_add_*_mem()` for each supported node. If a partially dirty block becomes nextblock, `jffs2_sum_move_collected()` transfers temporary scan collection into the superblock summary so future appends preserve the block's existing summary state.

During writes, `jffs2_flash_direct_writev()` or write-buffered `jffs2_flash_writev()` calls `jffs2_sum_add_kvec()`, which decodes the first kvec node type and records compact summary metadata. Unknown unsupported node types either BUG or disable summary collection, depending on compatibility.

At mount time, `jffs2_sum_scan_sumnode()` validates summary header, total length, node CRC, and summary data CRC. It optionally links a cleanmarker, processes each summary entry into raw refs/inode caches/dirents/xattrs, links the summary node itself, wastes any unexpected free remainder, and returns the block classification. Unsupported compatible entries reset the block accounting and return to full scan.

When a nextblock is being closed, `jffs2_sum_write_sumnode()` preallocates refs and calls `jffs2_sum_write_data()`, which serializes collected entries, appends a `jffs2_sum_marker`, computes CRCs, writes via `jffs2_flash_writev()`, and links the summary node or disables summary on write failure.

## State And Persistence Behavior

Summaries are persisted as `JFFS2_NODETYPE_SUMMARY` nodes near the end of an eraseblock, with a marker at the end pointing to the summary offset. In memory, `struct jffs2_summary` maintains a linked list of collected records, total summary byte size, entry count, padded byte count, and serialization buffer. `JFFS2_SUMMARY_NOSUM_SIZE` disables collection for the current block.

The summary is an optimization, not the sole source of truth. CRC failure or unsupported compatible entries cause fallback to full scanning. Successful summary parsing still creates `REF_UNCHECKED` for inode data, preserving later data validation by `readinode.c`.

## Dependencies And Integration Points

This file depends on `summary.h` data structures, raw node formats from `linux/jffs2.h`, MTD flash writes via `jffs2_flash_writev()`, block accounting and raw-ref helpers from `nodelist.h`, xattr setup under `CONFIG_JFFS2_FS_XATTR`, and scan/reservation hooks from `scan.c` and `nodemgmt.c`.

## Risks And Edge Cases

Summary size is capped at 64 KiB; oversized summaries are disabled for that block. The code must keep relative offsets, padded lengths, and dirty gaps accurate, because summary data omits explicit dirty-space entries and `sum_link_node_ref()` reconstructs gaps as dirty. `jffs2_sum_write_data()` consumes and frees collected entries while serializing; failure paths must leave the summary disabled or reset to avoid stale entries. A typo in the lock annotation references `erase_completion_block`, but the code uses `erase_completion_lock`.

## Test Signals

Tests should cover writing summary nodes, mount fast path through valid summaries, fallback on header/node/data CRC errors, unsupported compatible summary entries, summary overflow, summary disabled by lack of tail space, blocks with cleanmarkers, xattr summary entries, and write failures while writing summary data. Cross-checking full-scan and summary-scan block accounting should be part of validation.
