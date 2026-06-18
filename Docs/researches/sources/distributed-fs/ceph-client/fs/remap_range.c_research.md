# sources/distributed-fs/ceph-client/fs/remap_range.c

Purpose: Implements generic validation and VFS dispatch for file range cloning and deduplication, including data comparison for dedupe and exported helpers for filesystem remap implementations.

Important APIs, types, and functions: Exports `remap_verify_area()`, `generic_remap_file_range_prep()`, `vfs_clone_file_range()`, `vfs_dedupe_file_range_one()`, and `vfs_dedupe_file_range()`. Internal helpers include `generic_remap_checks()`, `generic_remap_check_len()`, folio locking helpers, `vfs_dedupe_file_range_compare()`, and `may_dedupe_file()`.

Control flow: Clone validation checks same-superblock, regular files, read/write modes, remap operation availability, permissions, and destination write bracketing before calling filesystem `remap_file_range`. Dedupe validates source metadata, caps length to 1 GiB, preinitializes per-destination statuses, verifies each destination fd, takes mount write access, checks ownership or write permission, and dispatches with `REMAP_FILE_DEDUP`. Generic prep checks block alignment, offsets, EOF, overlap, write limits, direct I/O completion, dirty page writeback, optional byte-for-byte compare, partial EOF block constraints, and `file_modified()`.

State and persistence: Mutates destination filesystem extent mappings through filesystem remap operations. Dedupe comparison reads page-cache or DAX data but persists only if the filesystem replaces duplicate destination ranges. Per-destination status is written back into the user-provided dedupe request structure before return.

Dependencies and integration points: Depends on generic VFS read/write checks from `read_write.c`, LSM and fsnotify permission checks, page cache folios, DAX compare support, mount write access, filesystem `remap_file_range`, and ioctl-level dedupe callers.

Risks and test signals: Risks include deduping non-identical data, overlapping same-file ranges, partial EOF block corruption, missing write permission on destination, stale page-cache compare races, DAX/non-DAX divergence, and incorrect shortened-length reporting. Test clone and dedupe across filesystems, same-file overlaps, unaligned ranges, partial EOF blocks, dirty data, DAX files, immutable and swapfile inodes, no-write-permission destinations, and multi-destination dedupe statuses.
