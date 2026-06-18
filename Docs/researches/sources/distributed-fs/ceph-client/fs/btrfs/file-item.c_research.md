# sources/distributed-fs/ceph-client/fs/btrfs/file-item.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file-item.c` implements Btrfs helpers for file extent items and data checksum items. It owns checksum tree lookup, checksum insertion/deletion, per-bio checksum buffer setup, checksum generation for write bios, dummy ordered sums for zoned nodatasum writes, conversion from on-disk file extent items into in-memory extent maps, and inode `disk_i_size` safety tracking for filesystems without `NO_HOLES`. The source was read as a complete 1407-line file for this report.

## Important APIs, Types, and Functions

`btrfs_inode_safe_disk_i_size_write()` updates `inode->disk_i_size`, either directly for `NO_HOLES` mode or by limiting it to the contiguous file-extent range recorded in `inode->file_extent_tree`. `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` maintain that in-memory extent bitmap when file extent items are inserted or dropped.

`btrfs_insert_hole_extent()` creates an explicit regular file extent item with `disk_bytenr == 0`, zero disk bytes, and logical `num_bytes`/`ram_bytes` for filesystems that represent holes explicitly. `btrfs_lookup_file_extent()` wraps `btrfs_search_slot()` for `BTRFS_EXTENT_DATA_KEY` lookups and supports read, COW, and insertion-search modes through the `mod` argument.

Checksum read APIs include private `btrfs_lookup_csum()` and `search_csum_tree()`, plus exported `btrfs_lookup_bio_sums()`, `btrfs_lookup_csums_list()`, `btrfs_lookup_csums_range()`, and `btrfs_lookup_csums_bitmap()`. They search `BTRFS_EXTENT_CSUM_KEY` items by logical disk byte address and return checksums either into a bio-owned buffer, a list of `struct btrfs_ordered_sum`, or a caller-provided bitmap/buffer pair.

Checksum write/delete APIs include `btrfs_csum_one_bio()`, `btrfs_alloc_dummy_sum()`, `btrfs_del_csums()`, and `btrfs_insert_data_csums()`. These calculate checksums from bio pages, attach ordered sums to ordered extents, split or truncate existing checksum items when deleting overlapping ranges, and insert or extend checksum items while respecting leaf space and log-tree overlap rules.

`btrfs_extent_item_to_extent_map()` translates regular, preallocated, hole, compressed, and inline file extent items into `struct extent_map`. `btrfs_file_extent_end()` returns the non-inclusive logical end of a file extent item, rounding inline extents to sectorsize.

## Control Flow

The checksum read path starts when the bio layer submits a data read and calls `btrfs_lookup_bio_sums()`. The function skips work for `NODATASUM` inodes or global no-data-csum state, allocates either `bbio->csum_inline` or a larger `kvcalloc()` buffer, optionally searches the commit root under `commit_root_sem`, and iterates sector-aligned chunks through `search_csum_tree()`. Missing checksums are converted to zeroed checksum slots; data relocation reads mark `EXTENT_NODATASUM`, while normal roots emit a rate-limited warning about checksum holes.

The checksum range lookup paths first search for the requested start key, then step back to a previous checksum item if it overlaps the requested start. They iterate csum items in key order, trim each item to the requested range, and either allocate ordered-sum records (`btrfs_lookup_csums_list()`/`range`) or copy bytes into a dense checksum buffer while setting a sector bitmap (`btrfs_lookup_csums_bitmap()`).

The checksum write path begins in the bio submit/write path with `btrfs_csum_one_bio()`. It allocates a `struct btrfs_ordered_sum` sized to the bio, attaches it to the ordered extent, and either computes checksums synchronously or schedules `csum_one_bio_work()`. Ordered extent completion later calls `btrfs_insert_data_csums()`, which repeatedly looks for an existing csum item ending at the new range, extends it when safe, or inserts a new item. Log-tree insertion has additional next-item checks to avoid overlapping checksum items.

The delete path in `btrfs_del_csums()` searches backward from the end of the target range. Fully covered checksum items are batched and deleted; prefix/suffix overlaps are truncated by `truncate_one_csum()`; ranges in the middle of a checksum item are split in place, then the newly formed overlapping item is processed again. This allows tree-log code to replace overlapping logged checksum ranges before inserting new ones.

The extent-map conversion path is used after a file extent item has already been found in a B-tree leaf. It reads the item type and fields, fills an extent map with logical start/length, disk bytenr, disk length, generation, RAM bytes, offset, compression, and prealloc flags, and emits an error for unknown types.

## State and Persistence Behavior

Persistent state modified here is Btrfs metadata: file extent items for holes and checksum tree items for data checksums. All such changes happen under `struct btrfs_trans_handle` and target either the checksum tree, a tree-log root, or a file's subvolume root. Checksum item layout is compact: item payload length is a multiple of `fs_info->csum_size`, and logical byte coverage is derived from sectorsize.

Runtime state includes `bbio->csum`, `bbio->sums`, `bbio->csum_inline`, async checksum work/completion, `struct btrfs_path` cursor reuse, temporary ordered-sum list nodes, and `inode->file_extent_tree`. `disk_i_size` is protected by `inode->lock`; extent bitmap updates rely on sectorsize-aligned ranges and preserve crash-consistency decisions made by truncation, hole punching, and extent replacement callers.

The file also preserves consistency between ordered extents and later metadata insertion. `btrfs_csum_one_bio()` stores checksums with ordered extents, while `btrfs_insert_data_csums()` persists them after I/O completion. For zoned nodatasum writes, `btrfs_alloc_dummy_sum()` persists no checksum bytes but keeps ordered-sum state so zone append completion can record the updated logical address.

## Dependencies and Integration Points

Direct dependencies include Btrfs B-tree accessors, extent buffers, transaction handles, checksum roots, ordered extents, bio wrappers, compression helpers, volume mapping, and inode extent I/O trees. Public prototypes are exported through `file-item.h`.

Major callers are the bio layer (`btrfs_lookup_bio_sums()` on data reads and checksum generation on writes), inode ordered extent completion (`btrfs_insert_data_csums()`), tree-log code (`btrfs_insert_data_csums()` and `btrfs_del_csums()` for logged checksum ranges), file/inode extent replacement and truncation paths (`btrfs_inode_*_file_extent_range()` and `btrfs_insert_hole_extent()`), and extent map lookup code (`btrfs_extent_item_to_extent_map()` and `btrfs_file_extent_end()`).

## Risks and Edge Cases

Important risks are off-by-one errors in inclusive/exclusive byte ranges, checksum-item splitting with a locked path, search cursor reuse across leaves, missing checksum roots returning corruption errors, and incorrect treatment of checksum holes for data relocation versus normal reads. Alignment assertions are central: most checksum and file-extent bitmap APIs require sectorsize-aligned ranges, while checksum item sizes must be multiples of `csum_size`.

`btrfs_insert_data_csums()` has subtle log-tree behavior because logged checksum items can overlap after reflink and fast fsync sequences. Extending an existing csum item beyond the next csum item would corrupt later lookup semantics. `btrfs_del_csums()` must preserve non-overlapping prefix/suffix checksums while deleting the requested range. `btrfs_extent_item_to_extent_map()` must treat inline extents specially because the disk-bytenr field location is inline data.

## Test Signals

Useful signals include xfstests covering reads with missing/bad checksums, data relocation of nodatasum extents, checksum tree deletion during truncation and hole punching, log replay after reflink plus fsync, compressed and inline file reads, zoned zone-append nodatasum writes, sectorsize larger than page size, and commit-root checksum lookup under free-space-cache reads. Debug builds should exercise alignment assertions, checksum item split/extend paths, extent map conversion for regular/prealloc/hole/inline items, and `disk_i_size` updates with and without `NO_HOLES`.
