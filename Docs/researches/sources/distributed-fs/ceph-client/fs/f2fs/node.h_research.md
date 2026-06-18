# sources/distributed-fs/ceph-client/fs/f2fs/node.h

## Purpose

`node.h` defines the F2FS node-manager data structures and inline helpers shared across node allocation, NAT persistence, node-page footer handling, fsync recovery, and file block tree traversal. It captures the on-disk NAT address math and the in-memory `node_info`, `nat_entry`, `nat_entry_set`, and `free_nid` abstractions used by `node.c` and recovery code.

## Important APIs, macros, and types

- NAT layout macros `START_NID()`, `NAT_BLOCK_OFFSET()`, `current_nat_addr()`, `next_nat_addr()`, and `set_to_next_nat()` translate nids to active/next NAT block copies.
- Cache thresholds such as `MAX_FREE_NIDS`, `DEF_RAM_THRESHOLD`, `DEF_DIRTY_NAT_RATIO_THRESHOLD`, `DEF_NAT_CACHE_THRESHOLD`, and `DEF_RF_NODE_BLOCKS` provide default memory and recovery limits.
- `struct node_info` is the canonical in-memory nid-to-node mapping: nid, owner ino, block address, version, and flags.
- `struct nat_entry` wraps `node_info` for radix-tree and clean/dirty list membership.
- `struct nat_entry_set` groups dirty NAT entries by NAT block so checkpoint can flush one NAT page or journal batch at a time.
- `struct free_nid` stores a cached free/preallocated nid and state.
- `enum mem_type` identifies cache classes for `f2fs_available_free_memory()`.
- Footer helpers `ino_of_node()`, `nid_of_node()`, `ofs_of_node()`, `cpver_of_node()`, `next_blkaddr_of_node()`, `fill_node_footer()`, `copy_node_footer()`, `fill_node_footer_blkaddr()`, and `is_recoverable_dnode()` read/write node footer metadata.
- Node tree helpers `IS_DNODE()`, `set_nid()`, and `get_nid()` classify node pages and mutate child nid pointers.
- Mark helpers `is_cold_node()`, `is_fsync_dnode()`, `is_dent_dnode()`, `set_cold_node()`, `set_dentry_mark()`, and `set_fsync_mark()` manage footer bits used by writeback and recovery.

## Control flow and state

The NAT address helpers implement the two-copy NAT area scheme. `current_nat_addr()` computes the current physical NAT block using `nat_blkaddr`, block offset, segment size, and the NAT bitmap. `next_nat_addr()` flips the segment-copy bit to locate the alternate block. `set_to_next_nat()` changes the NAT bitmap after checkpoint code prepares the next copy.

`node_info_from_raw_nat()` and `raw_nat_from_node_info()` are the boundary between on-disk little-endian `struct f2fs_nat_entry` and host-endian `struct node_info`. `copy_node_info()` deliberately does not copy `flag`, because cache/checkpoint state bits are not part of the raw NAT mapping.

Node footers carry recovery-critical fields. `fill_node_footer()` initializes nid, owner ino, and node offset while preserving non-offset flag bits if requested. `fill_node_footer_blkaddr()` stamps the current checkpoint version and, when CRC recovery is enabled, checkpoint CRC into `cp_ver`, plus the next block address for roll-forward scanning. `is_recoverable_dnode()` checks a node footer against checkpoint version/CRC flags and supports no-CRC recovery mode.

`IS_DNODE()` encodes the F2FS node tree layout: inode node offset zero, direct nodes, indirect nodes, and double-indirect nodes. It treats xattr blocks as dnodes for data-bearing purposes and excludes indirect node offsets that only contain child nids.

## Persistence behavior

The header directly describes persistent NAT and node footer layout semantics. NAT block selection determines which NAT copy checkpoint will persist. Footer checkpoint version, CRC, next block address, fsync mark, dentry mark, cold mark, nid, ino, and offset are all read after crashes by roll-forward recovery. Child nid writes through `set_nid()` dirty node folios, causing later node writeback and NAT updates.

## Dependencies and integration points

`node.h` depends on F2FS superblock, checkpoint, NAT entry, folio, and node layout definitions from broader F2FS headers. It is consumed by `node.c`, `namei.c`, `recovery.c`, xattr/inline paths, data block mapping code, and fsync/checkpoint code. The helper `set_mark()` conditionally updates inode checksums under `CONFIG_F2FS_CHECK_FS`, so footer flag changes integrate with metadata integrity checks.

## Risks and edge cases

- NAT address math is tightly coupled to segment geometry and mirror-copy layout; incorrect bit arithmetic can make checkpoint read or write the wrong NAT half.
- `MAX_IOSTAT_PERIOD_MS` is elsewhere, but node defaults here also encode policy; changing thresholds without mount-option plumbing may alter memory and recovery behavior globally.
- `fill_node_footer()` preserves low flag bits when `reset` is false; callers must choose reset mode correctly or stale fsync/dentry/cold bits can leak.
- `is_recoverable_dnode()` has different comparison behavior under CRC and no-CRC checkpoint flags; recovery tests need both.
- `set_nid()` waits for node folio writeback before mutating child pointers, so callers must be ready for blocking behavior.
- `IS_DNODE()` depends on exact offset formulas; future changes to the inode node layout must update both the comment and logic.

## Test signals

Tests should verify NAT current/next address selection across segment boundaries, NAT bitmap flips, raw NAT conversion endianness, node footer fill/copy behavior, recovery version matching with CRC and no-CRC checkpoint modes, direct/indirect/double-indirect `IS_DNODE()` classification, xattr-node classification, child nid mutation dirtying, and checksum updates when check-fs instrumentation is enabled.
