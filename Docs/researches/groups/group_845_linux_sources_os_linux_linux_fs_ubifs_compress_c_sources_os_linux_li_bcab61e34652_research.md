# Group Research: group_845_linux_sources_os_linux_linux_fs_ubifs_compress_c_sources_os_linux_li_bcab61e34652

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/linux/linux`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/compress.c -->
# File Research: sources/os/linux/linux/fs/ubifs/compress.c

Read completely: 369 lines.

This file centralizes UBIFS compression and decompression. It defines the UBIFS compressor registry for `none`, LZO, zlib/deflate, and zstd, backed by the kernel async compression API when the corresponding `CONFIG_UBIFS_FS_*` option is enabled.

Main entry points: `ubifs_compress`, `ubifs_compress_folio`, `ubifs_decompress`, `ubifs_decompress_folio`, `ubifs_compressors_init`, and `ubifs_compressors_exit`.

Key behavior: compression is skipped for `UBIFS_COMPR_NONE`, too-small inputs, compressor errors, or outputs that fail to save at least `UBIFS_MIN_COMPRESS_DIFF` bytes. In those cases the input is copied verbatim and the returned compression type is changed to `UBIFS_COMPR_NONE`. Folio and linear-buffer paths share common helpers, with folio-aware source/destination setup.

Decompression validates the compression type, rejects algorithms not compiled in, copies `none` data directly, and reports decompression failures through `ubifs_err`.

Important interactions: data write/read paths in `file.c` and journal data-node code rely on this file to preserve `compr_type` and output length semantics. `crypto.c` can further encrypt compressed data after compression and decrypt before decompression.

Reliability notes: the async compression path retries `-EAGAIN` with a cloned request and `crypto_wait_req`. Unsupported on-flash compression types or disabled compressors return `-EINVAL`, which turns read-side corruption or feature mismatch into an explicit failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/crypto.c -->
# File Research: sources/os/linux/linux/fs/ubifs/crypto.c

Read completely: 97 lines.

This file integrates UBIFS with fscrypt. It supplies the filesystem encryption operations, stores encryption contexts as UBIFS xattrs, checks encrypted-directory emptiness, and encrypts/decrypts UBIFS data-node payloads in place.

Main entry points: `ubifs_encrypt`, `ubifs_decrypt`, and `ubifs_crypt_operations`.

Key behavior: `ubifs_encrypt` records the pre-encryption compressed length in `dn->compr_size`, pads the data area to `UBIFS_CIPHER_BLOCK_SIZE`, zero-fills padding, and calls `fscrypt_encrypt_block_inplace`. `ubifs_decrypt` validates `compr_size`, decrypts the full encrypted payload length, and returns the original compressed length to the caller.

Important interactions: `dir.c` uses fscrypt preparation APIs for lookup/create/link/rename/readdir names and calls `ubifs_check_dir_empty` through the fscrypt empty-dir hook. `file.c` decrypts data nodes before decompression and encrypts data after compression through the journal write path.

Reliability notes: decrypt-side validation rejects zero, oversized, or buffer-exceeding compressed sizes. Encryption assumes the caller allocated enough space for block padding and asserts that invariant.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/debug.c -->
# File Research: sources/os/linux/linux/fs/ubifs/debug.c

Read completely: 3052 lines.

This file implements UBIFS debug-only dumping, consistency checking, power-cut fault injection, debugfs controls, and assertion handling.

Main responsibilities:
- Formats keys, node types, commit states, journal heads, inodes, nodes, lprops, budgeting state, LPT state, LEB scans, TNC znodes, heaps, pnodes, and the on-flash index.
- Saves and checks space-accounting snapshots.
- Checks synchronized inode sizes, directory size/link counts, TNC ordering and znode invariants, index size, full filesystem inode/link/xattr consistency, and scan-node ordering.
- Emulates power cuts around UBI LEB write/change/unmap/map operations and can corrupt a partial write buffer before returning `-EROFS`.
- Exposes per-mount and global debugfs knobs for extra checks, recovery testing, forced read-only error state, and dump triggers.
- Implements `ubifs_assert_failed` behavior for panic, read-only transition, or stack reporting.

Key APIs: `ubifs_dump_inode`, `ubifs_dump_node`, `ubifs_dump_lprops`, `ubifs_dump_budg`, `ubifs_dump_tnc`, `ubifs_dump_index`, `dbg_walk_index`, `dbg_check_tnc`, `dbg_check_idx_size`, `dbg_check_filesystem`, `dbg_check_space_info`, `dbg_leb_write`, `dbg_leb_change`, `dbg_leb_unmap`, `dbg_leb_map`, `dbg_debugfs_init_fs`, `dbg_debugfs_exit_fs`, `dbg_debugfs_init`, `dbg_debugfs_exit`, `ubifs_debugging_init`, and `ubifs_debugging_exit`.

Important behavior: node dumping is defensive about bad magic, unknown types, truncated lengths, and invalid name lengths. TNC checking verifies parent/child relationships, dirty-parent ordering, key ranges, duplicate/colliding key order, and clean/dirty znode counters. Full filesystem checking walks the index, reads all leaf nodes, builds an RB-tree of inode facts, and compares stored inode link/xattr/size metadata against calculated references.

Important interactions: this file is called from many UBIFS subsystems through `dbg_*` helpers and wraps low-level UBI I/O when recovery testing is enabled. It depends on TNC, LPT/lprops, budgeting, scan, journal, xattr, and VFS inode state being internally coherent.

Reliability notes: debug checks are intentionally heavyweight and normally gated by global/per-mount flags. Fault injection can intentionally corrupt data and force `-EROFS`; it must remain confined to recovery testing. Debugfs knobs are writable by root and can trigger expensive dumps or force `c->ro_error`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/debug.h -->
# File Research: sources/os/linux/linux/fs/ubifs/debug.h

Read completely: 305 lines.

This header declares UBIFS debug data structures, debug message macros, assertion helpers, check enablement helpers, dump/check APIs, fault-injection UBI wrappers, and debugfs lifecycle functions.

Main contents:
- `struct ubifs_debug_info`, the per-filesystem debug state for saved old index roots, emulated power-cut state, LPT size-check state, saved budgeting/lprops snapshots, per-mount check flags, recovery-test flag, and debugfs dentries.
- `struct ubifs_global_debug_info`, the global check/recovery-test switches.
- `ubifs_assert`, `ubifs_assert_cmt_locked`, and categorized `dbg_*` logging macros.
- Inline helpers such as `dbg_is_chk_gen`, `dbg_is_chk_index`, `dbg_is_chk_fs`, `dbg_is_tst_rcvry`, and `dbg_is_power_cut`.
- Prototypes for all dumpers, checkers, index walking, LEB wrappers, and debugfs init/exit functions.

Important interactions: most UBIFS files include this through `ubifs.h` and use the macros as low-cost gates around optional validation. `debug.c` provides the backing storage and implementations.

Reliability notes: when debug support is active, assertion action is runtime-controlled by `c->assert_action`. The check-enable helpers combine global and per-mount flags, so enabling a global debugfs knob affects all UBIFS mounts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/dir.c -->
# File Research: sources/os/linux/linux/fs/ubifs/dir.c

Read completely: 1772 lines.

This file implements UBIFS directory and namespace VFS operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, tmpfile, rename/exchange/whiteout, getattr for directories/files, and directory file operations.

Main entry points: `ubifs_new_inode`, `ubifs_check_dir_empty`, `ubifs_getattr`, `ubifs_dir_inode_operations`, and `ubifs_dir_operations`.

Key behavior: all mutating operations budget space before journaling, except deletion paths (`unlink`, `rmdir`, zero-size-like deletion cases) can continue on `-ENOSPC` using reserved deletion space. Newly created non-xattr inodes start with zero links and are placed on the orphan list until the journal update links them, which protects power-cut consistency around security/encryption xattrs and dentries.

Filesystem semantics covered:
- `lookup` handles fscrypt nokey names, hash/minor-hash lookups, dead-dentry detection, and encrypted context compatibility checks.
- `readdir` maps UBIFS dentry hash keys to VFS offsets and saves the last full dentry in `file->private_data` to handle collisions across consecutive calls.
- create/mkdir/mknod/symlink/tmpfile initialize security, encryption context, inherited flags, data payloads, link counts, parent sizes, and journal updates.
- unlink/rmdir purge xattrs, update link counts and parent sizes, and clear no-space flags when deletion succeeded without a budget.
- rename supports `RENAME_NOREPLACE`, `RENAME_WHITEOUT`, and `RENAME_EXCHANGE`, with multi-inode locking, parent link-count repair, whiteout inode creation, and atomic journal rename records.

Important interactions: uses fscrypt name setup/preparation extensively, calls journal update helpers for atomic media changes, uses UBIFS inode `ui_mutex` for internal size/link updates, and relies on `file.c` for `ubifs_fsync`, `ubifs_setattr`, and file operations assigned to regular inodes.

Reliability notes: directory offsets are hash-based, so full `seekdir`/`telldir` semantics are not guaranteed and NFS is explicitly unsuitable. Error unwind paths restore parent sizes, link counts, budgets, inode refs, and fscrypt names carefully; rename/whiteout remains the most stateful path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/file.c -->
# File Research: sources/os/linux/linux/fs/ubifs/file.c

Read completely: 1666 lines.

This file implements UBIFS regular-file, symlink, device-node inode, file, mmap, and address-space operations. It owns folio read/write behavior, write budgeting, dirty-folio accounting, writeback ordering, truncation, setattr, fsync, time updates, mmap write faults, and symlink resolution.

Main entry points: `ubifs_setattr`, `ubifs_fsync`, `ubifs_update_time`, `ubifs_file_address_operations`, `ubifs_file_inode_operations`, `ubifs_symlink_inode_operations`, and `ubifs_file_operations`.

Key read behavior: `read_block` looks up data nodes in the TNC, treats `-ENOENT` as holes, decrypts encrypted nodes, decompresses data into folios, validates logical sizes, and zero-fills short blocks. `do_readpage` handles multi-block folios and beyond-EOF reads. Bulk-read can read consecutive data nodes from one LEB into a shared buffer after detecting sequential access.

Key write behavior: `write_begin` has fast and slow budgeting paths to avoid deadlocking on locked folios when budgeting may force writeback. `PG_private` tracks UBIFS-budgeted dirty folios, while `PG_checked` distinguishes holes/new-page budgeting from existing-page changes. `write_end`, invalidation, release, and writeback release or convert the corresponding budgets and maintain `dirty_pg_cnt`.

Writeback and size consistency: `ubifs_writepage` avoids writing data beyond the last synchronized inode size unless it first writes the inode, preventing committed data nodes beyond on-flash inode size after power loss. Truncation writes a dirty partial last block before journaling a truncate node when needed.

Other VFS behavior: `ubifs_fsync` writes dirty ranges, optionally writes the inode, and flushes write buffers by inode. `ubifs_write_iter` updates mtime/ctime before generic writes. `ubifs_vm_page_mkwrite` budgets mmap writes before folio lock, handles races with truncation, dirties the folio, and updates timestamps. Symlink operations route encrypted symlinks through fscrypt.

Important interactions: depends on `compress.c` for decompression, `crypto.c` for decryption, journal helpers for data and truncate records, budgeting helpers for page/inode reservations, and debug checks for synchronized inode size.

Reliability notes: this is one of UBIFS’s most budget-sensitive files. Correctness depends on matching every dirty-folio state transition with the correct budget release and on preserving `ui_size`, `synced_i_size`, and VFS `i_size` ordering across writeback, append, mmap, and truncate races.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/find.c -->
# File Research: sources/os/linux/linux/fs/ubifs/find.c

Read completely: 963 lines.

This file implements UBIFS logical eraseblock selection for data allocation, garbage collection, and index allocation/GC. It searches lprops heaps/lists first and scans the LPT only when in-memory categories do not contain a suitable LEB.

Main entry points: `ubifs_find_dirty_leb`, `ubifs_find_free_space`, `ubifs_find_free_leb_for_idx`, `ubifs_save_dirty_idx_lnums`, and `ubifs_find_dirty_idx_leb`.

Key behavior:
- `valuable` decides whether lprops discovered during an LPT scan should be cached in memory based on category, heap capacity, and useful free+dirty space.
- dirty-LEB selection prefers dirty or dirty-index heaps, can pick empty/freeable LEBs when requested, avoids index-reserved LEBs when necessary, and marks the result `LPROPS_TAKEN`.
- free-space selection balances empty LEB preservation for index/commit needs with allocation of non-index LEBs that have enough free space; offset zero results are unmapped before use.
- index allocation only uses empty/freeable LEBs, marks them `LPROPS_TAKEN | LPROPS_INDEX`, and unmaps before returning.
- dirty index selection uses a commit-time sorted dirty-index array first, then full LPT scan, then trivial-GC candidates.

Important interactions: tightly coupled to lprops categories/heaps, LPT scanning, budgeting state (`min_idx_lebs`, `idx_lebs`, `taken_empty_lebs`), journal/GC allocation, and commit-time in-the-gaps index writing.

Reliability notes: the file carefully avoids selecting `LPROPS_TAKEN` LEBs, index LEBs for data when reserved index space is tight, and free+dirty data LEBs whose obsolete content may still depend on write-buffer state. Short-lived adjustments to `taken_empty_lebs` make budgeting pessimistic while the lprops update completes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/find.c -->