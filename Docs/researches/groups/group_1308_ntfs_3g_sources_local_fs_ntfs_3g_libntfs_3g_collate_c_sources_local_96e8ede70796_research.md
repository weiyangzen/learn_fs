# Group Research: group_1308_ntfs_3g_sources_local_fs_ntfs_3g_libntfs_3g_collate_c_sources_local_96e8ede70796

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/local-fs/ntfs-3g/libntfs-3g` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/collate.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/collate.c

## Scope

This file implements the collation dispatch and comparison routines used by NTFS indexes. It provides comparison functions for binary keys, little-endian integer keys, security descriptor hash keys, arrays of little-endian integers, and filename index keys.

## Public And Internal APIs Covered

- Public dispatcher: `ntfs_get_collate_function()`.
- Internal collators:
  - `ntfs_collate_binary()`
  - `ntfs_collate_ntofs_ulong()`
  - `ntfs_collate_ntofs_ulongs()`
  - `ntfs_collate_ntofs_security_hash()`
  - `ntfs_collate_file_name()`

## Control Flow And Behavior

- `ntfs_get_collate_function()` maps `COLLATION_RULES` enum values to a `COLLATE` function pointer. Unsupported collation rules set `errno = EOPNOTSUPP` and return `NULL`.
- Binary collation uses `memcmp()` over the shorter length, then sorts shorter data before longer data when common prefixes match.
- `COLLATION_NTOFS_ULONG` validates both key lengths are exactly 4 bytes, decodes little-endian `u32` values, and returns -1, 0, or 1.
- `COLLATION_NTOFS_ULONGS` validates equal positive lengths aligned to 4 bytes, then compares each little-endian `u32` element in order.
- Security-hash collation validates an 8-byte key and compares the first little-endian `u32`, then the second as a tie-breaker.
- Filename collation treats the key payload as `FILE_NAME_ATTR` and delegates Unicode comparison to `ntfs_names_full_collate()` using the volume upcase table and case-sensitive mode.

## Dependencies

- Uses NTFS layout types from `attrib.h` and `index.h`.
- Uses Unicode filename comparison from `unistr.h`.
- Uses logging through `logging.h`.
- Called by generic index lookup/insertion/removal logic in `index.c`.

## Risks And Invariants

- Integer and security-hash collators require exact byte lengths; malformed index keys return `NTFS_COLLATION_ERROR`.
- Filename keys must contain valid `FILE_NAME_ATTR` data; structural bounds are expected to be checked by callers such as `ntfs_index_entry_inconsistent()`.
- Unsupported collation rules prevent generic index operations from proceeding.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/collate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/compat.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/compat.c

## Scope

This file provides small libc compatibility implementations used when the host platform lacks specific functions. Implementations are conditionally compiled based on configure results.

## Public APIs Covered

- `ffs()` when `HAVE_FFS` is not defined.
- `daemon()` when `HAVE_DAEMON` is not defined.
- `strsep()` when `HAVE_STRSEP` is not defined.

## Control Flow And Behavior

- `ffs()` returns the one-based bit position of the least significant set bit, or 0 for input 0. It narrows by 16, 8, 4, 2, and 1-bit chunks.
- `daemon()` forks, exits the parent with `_exit(0)`, creates a new session with `setsid()`, optionally changes directory to `/`, and optionally redirects standard input/output/error to `/dev/null`.
- `strsep()` scans `*stringp` for any delimiter byte, replaces the delimiter with `NUL`, advances `*stringp`, and returns the current token. It supports empty fields and returns `NULL` when `*stringp` is `NULL`.

## Dependencies

- Includes only the headers needed for each fallback path.
- Depends on configure macros in `config.h`.
- Supplies portability functions for the rest of ntfs-3g without changing call sites.

## Risks And Invariants

- `daemon()` intentionally exits the parent process and must only be used in daemonization paths.
- `strsep()` mutates the caller-provided string buffer.
- These fallbacks must match expected libc semantics closely because platform-dependent code may assume standard behavior.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/compress.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/compress.c

## Scope

This file implements NTFS compressed attribute support. It contains LZNT1-style 4 KiB sub-block compression/decompression, compressed attribute reads, compressed writes, close-time compression of the final partial block, and runlist/cluster freeing logic needed when compressed data occupies fewer clusters than originally allocated.

## Public And Internal APIs Covered

- Public compressed I/O APIs:
  - `ntfs_compressed_attr_pread()`
  - `ntfs_compressed_pwrite()`
  - `ntfs_compressed_close()`
- Compression codec internals:
  - `ntfs_hash()`
  - `ntfs_best_match()`
  - `ntfs_skip_position()`
  - `ntfs_compress_block()`
  - `ntfs_decompress()`
- Compression-block and cluster helpers:
  - `ntfs_is_cb_compressed()`
  - `read_clusters()`
  - `write_clusters()`
  - `ntfs_comp_set()`
  - `valid_compressed_run()`
  - `ntfs_compress_overwr_free()`
  - `ntfs_compress_free()`
  - `ntfs_read_append()`
  - `ntfs_flush()`

## Control Flow And Behavior

- Compression uses 4 KiB NTFS sub-blocks. `ntfs_compress_block()` builds literal/phrase token streams with lazy parsing, a 3-byte hash table, bounded search depth, and a “nice match” cutoff. If compression is not beneficial, it emits an uncompressed sub-block header and a padded 4 KiB block.
- `ntfs_decompress()` parses NTFS compression blocks into a destination buffer, handling uncompressed sub-blocks, compressed tag bytes, symbol tokens, phrase tokens, overlapping back-references, partial sub-block zero-fill, and stream termination. Structural overflow is reported with `errno = EOVERFLOW`.
- `ntfs_compressed_attr_pread()` validates the attribute, rejects encrypted compressed data, truncates reads at `data_size`, zero-fills beyond `initialized_size`, handles resident attributes by delegating to `ntfs_attr_pread()`, then processes each compression block as sparse, physically uncompressed, or compressed.
- For uncompressed and compressed physical blocks, the read path temporarily clears compressed flags and widens `data_size`/`initialized_size` to `allocated_size` so raw data can be read through `ntfs_attr_pread()`, then restores the original attribute state.
- `ntfs_is_cb_compressed()` walks the runlist for one compression block. A full non-sparse run means physically uncompressed; a hole within the compression block means compressed/sparse representation.
- `ntfs_comp_set()` compresses a full compression-block-sized buffer into sub-blocks, detects all-zero compressed forms so nothing needs to be written, rounds physical writes to full clusters, and returns distinct values for all-zero, compression failure, and irrecoverable I/O failure.
- `ntfs_compressed_pwrite()` is the main compressed write engine. It validates runlist invariants, requires reserved spare runlist entries, decides whether the write completes a compression block, reads/decompresses previous compressed data when appending into an existing compressed block, compresses full blocks when possible, falls back to uncompressed writes, and updates the caller’s lowest dirty VCN.
- `ntfs_compress_free()` and `ntfs_compress_overwr_free()` mutate runlists after compression, free clusters no longer needed, insert or merge holes, update `compressed_size`, mark the runlist dirty, and preserve compression-block alignment.
- `ntfs_compressed_close()` compresses the final partial compression block on close. If compression fails in the ordinary “not worth compressing” sense, it leaves the data uncompressed; hard errors propagate.

## State And Data Structures

- `struct COMPRESS_CONTEXT` stores the current input, buffer size, best match length/relative offset, maximum match length, and hash-chain arrays used while compressing one sub-block.
- Compressed attributes rely on `ntfs_attr` fields such as `compression_block_size`, `compression_block_clusters`, `compression_block_size_bits`, `data_flags`, `data_size`, `initialized_size`, `allocated_size`, `compressed_size`, `unused_runs`, and `rl`.
- Runlists encode sparse holes using `LCN_HOLE`; compressed physical layout requires holes to align with compression-block boundaries.

## Dependencies

- Uses raw device I/O through `ntfs_pread()` and `ntfs_pwrite()`.
- Uses attribute I/O and MST-aware attribute paths from `attrib.c`.
- Uses runlist mapping and cluster allocation/freeing helpers from `runlist.h` and `lcnalloc.h`.
- Uses NTFS volume geometry, cluster size, and logging facilities.

## Risks And Invariants

- The write path assumes spare runlist entries have been reserved before compression can split or insert holes.
- Compression-block hole layout must remain valid; adjacent holes and non-adjacent VCN sequences are treated as corruption.
- Temporary clearing of compressed flags during raw reads must be restored on every path.
- Partial cluster writes are avoided by rounded writes; failures after some compressed data is written may leave damaged data and are logged as serious errors.
- Unsupported compression block sizes below 4 KiB are rejected.
- Decompression is deliberately strict about source and destination bounds to avoid accepting malformed compressed streams.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/debug.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/debug.c

## Scope

This file contains debug-only helper output for NTFS runlists. Its code is compiled only when `DEBUG` is defined.

## Public API Covered

- `ntfs_debug_runlist_dump()`

## Control Flow And Behavior

- `ntfs_debug_runlist_dump()` logs a runlist table with VCN, LCN, and run length columns.
- Negative special LCN values are rendered with labels for `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_EINVAL`, or a fallback unknown label.
- The loop stops at the runlist terminator entry whose `length` is zero.
- A `NULL` runlist logs that no runlist is present.

## Dependencies

- Uses `runlist_element` from `runlist.h`.
- Uses debug logging from `logging.h`.

## Risks And Invariants

- The function assumes a valid runlist is terminated by a zero-length entry.
- It is diagnostic-only and does not modify state.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/device.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/device.c

## Scope

This file implements the low-level `ntfs_device` abstraction and positioned I/O utilities. It wraps device operation callbacks, handles partial reads/writes, applies NTFS multi-sector transfer fixups, reads/writes clusters, and queries device size, geometry, sector size, partition offset, and block size.

## Public And Internal APIs Covered

- Device lifecycle and state:
  - `ntfs_device_alloc()`
  - `ntfs_device_free()`
  - `ntfs_device_sync()`
- Positioned I/O:
  - `ntfs_pread()`
  - `ntfs_pwrite()`
- MST-protected record I/O:
  - `ntfs_mst_pread()`
  - `ntfs_mst_pwrite()`
- Cluster I/O:
  - `ntfs_cluster_read()`
  - `ntfs_cluster_write()`
- Device information:
  - `ntfs_device_size_get()`
  - `ntfs_device_partition_start_sector_get()`
  - `ntfs_device_heads_get()`
  - `ntfs_device_sectors_per_track_get()`
  - `ntfs_device_sector_size_get()`
  - `ntfs_device_block_size_set()`
- Internal helpers:
  - `ntfs_device_offset_valid()`
  - `ntfs_device_get_geo()`

## Control Flow And Behavior

- `ntfs_device_alloc()` copies the device name, stores callbacks/private data/state, and initializes cached geometry values to -1.
- `ntfs_device_free()` rejects `NULL` devices and open devices, then frees the copied name and device structure.
- `ntfs_device_sync()` calls the device sync callback only when the device is marked dirty.
- `ntfs_pread()` and `ntfs_pwrite()` loop until the requested byte count is satisfied, EOF/short I/O occurs, or an error occurs before any progress. Writes reject read-only devices, mark the device dirty, and optionally sync after a successful write.
- `ntfs_mst_pread()` reads complete records and applies post-read MST fixups to each full block. It returns the number of complete blocks read, not bytes.
- `ntfs_mst_pwrite()` applies pre-write MST protection to each block, writes the protected bytes, then immediately applies post-write deprotection to the caller’s buffer to keep cached records in normal form.
- `ntfs_cluster_read()` and `ntfs_cluster_write()` convert LCN/count to byte offsets and lengths, reject accesses beyond `vol->nr_clusters`, and return cluster counts.
- `ntfs_device_size_get()` tries platform ioctls first (`BLKGETSIZE64`, `BLKGETSIZE`, floppy parameters, FreeBSD media size, macOS block count), then falls back to probing with exponential growth and binary search.
- Geometry lookup prefers libhd/EDD BIOS legacy geometry when enabled, otherwise falls back to `HDIO_GETGEO`. Results are cached in `d_heads` and `d_sectors_per_track`.
- Sector and block size helpers use platform ioctls where available and treat block-size setting as success for non-block devices.

## Dependencies

- Uses the callback table in `struct ntfs_device_operations`.
- Uses MST helpers from `mst.h`.
- Uses volume geometry from `ntfs_volume`.
- Uses Linux, FreeBSD, macOS, and optional libhd ioctls guarded by preprocessor checks.

## Risks And Invariants

- All callers must distinguish byte counts from block or cluster counts depending on API.
- MST write mutates the caller’s buffer during protection/deprotection and increments update sequence numbers.
- `ntfs_pwrite()` can report a partially written count if post-write sync fails.
- Device-size fallback probing depends on seek/read behavior and may be less reliable than native ioctls.
- Cluster access bounds are checked against `vol->nr_clusters`; bypassing these helpers would avoid that safety check.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/device.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/dir.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/dir.c

## Scope

This file implements NTFS directory operations and filename/link management for libntfs-3g. It handles directory lookup, pathname traversal, readdir, object creation, deletion, hard links, parent lookup, DOS short-name xattrs, cache integration, WSL/Interix special-file handling, and POSIX-style link count calculation.

## Public And Internal APIs Covered

- Index name constants: `NTFS_INDEX_I30`, `NTFS_INDEX_SII`, `NTFS_INDEX_SDH`, `NTFS_INDEX_O`, `NTFS_INDEX_Q`, `NTFS_INDEX_R`.
- Cache helpers when enabled:
  - `ntfs_dir_inode_hash()`
  - `ntfs_dir_lookup_hash()`
  - inode and lookup cache comparison/invalidation helpers.
- Lookup and path traversal:
  - `ntfs_inode_lookup_by_name()`
  - `ntfs_inode_lookup_by_mbsname()`
  - `ntfs_inode_update_mbsname()`
  - `ntfs_pathname_to_inode()`
- Directory iteration:
  - `ntfs_interix_types()`
  - `ntfs_readdir()`
  - internal `ntfs_dir_entry_type()`, `ntfs_filldir()`, and `ntfs_mft_get_parent_ref()`.
- Creation:
  - internal `__ntfs_create()`
  - wrappers `ntfs_create()`, `ntfs_create_device()`, `ntfs_create_symlink()`.
- Deletion and linking:
  - `ntfs_check_empty_dir()`
  - `ntfs_delete()`
  - `ntfs_link()`
  - `ntfs_dir_parent_inode()`
  - internal `ntfs_check_unlinkable_dir()` and `ntfs_link_i()`.
- DOS-name xattr support:
  - `ntfs_get_ntfs_dos_name()`
  - `ntfs_set_ntfs_dos_name()`
  - `ntfs_remove_ntfs_dos_name()`
  - internal `get_dos_name()`, `get_long_name()`, `set_namespace()`, and `set_dos_name()`.
- Link count:
  - `ntfs_dir_link_cnt()`

## Control Flow And Behavior

- `ntfs_inode_lookup_by_name()` searches `$I30` first in `INDEX_ROOT`, then descends through `INDEX_ALLOCATION` blocks as needed. It validates index block sizes, entry bounds, index-entry filename consistency, child-node VCNs, and uses case-sensitive or case-insensitive collation depending on volume flags.
- `ntfs_inode_lookup_by_mbsname()` converts multibyte names to NTFS Unicode, optionally uppercases the cache key on case-insensitive volumes, consults the lookup cache when enabled, and caches both successful and negative results.
- `ntfs_pathname_to_inode()` splits a path on `/`, optionally starts from a supplied parent or root, translates each component to Unicode, does directory lookup, opens each next inode, and uses the inode cache for full or partial absolute paths when enabled.
- `ntfs_readdir()` emits synthetic `.` and `..`, reads `INDEX_ROOT`, then walks in-use `INDEX_ALLOCATION` blocks according to the directory bitmap. It resumes from `*pos`, validates each entry, and invokes the caller’s `filldir` callback.
- `ntfs_filldir()` converts index entries into callback records, filters hidden/system/metadata entries according to volume flags, resolves reparse/system special file types when needed, lowercases names on case-insensitive mounts, and skips the root self-reference.
- `ntfs_interix_types()` decodes Interix special-file markers from unnamed `$DATA`; `ntfs_dir_entry_type()` opens the referenced inode to distinguish symlinks, reparse points, Interix devices/FIFOs/sockets, directories, and regular files.
- `__ntfs_create()` allocates an MFT record, creates `STANDARD_INFORMATION`, security descriptor or inherited security id, directory `INDEX_ROOT` or file `$DATA`, `FILE_NAME`, and parent directory index entry. It handles inherited compression, dotfile hidden flags, Interix special-file payloads, WSL reparse data and EAs, and detailed rollback of partially created metadata.
- `ntfs_delete()` finds the matching `FILE_NAME` attribute, handles DOS/Win32 namespace pairs, checks directory unlinkability, removes the parent index entry, decrements link count, invalidates caches, updates times, and when the last link is gone frees reparse/object-id indexes, nonresident clusters, extent MFT records, and the base MFT record.
- `ntfs_link_i()` adds a new `FILE_NAME` attribute and directory index entry, updates hidden flags for dotfiles, and increments the MFT link count. `ntfs_link()` exposes the POSIX-name variant.
- DOS-name xattr operations expose and modify NTFS short-name state. They retrieve DOS and long names, validate short-name characters, adjust namespace flags between POSIX, DOS, WIN32, and WIN32_AND_DOS, add/remove alternate names through index and attribute operations, and close the involved inodes on completion.
- `ntfs_dir_link_cnt()` computes POSIX link counts by counting non-DOS directory children for directories, including `.` and `..`, or non-DOS `FILE_NAME` attributes for non-directories.

## State And Data Structures

- Uses NTFS directory index structures: `INDEX_ROOT`, `INDEX_ALLOCATION`, `INDEX_HEADER`, `INDEX_ENTRY`, and `FILE_NAME_ATTR`.
- Uses MFT link count, sequence number, flags, timestamps, and extent inode chains.
- Optional caches store pathname-to-inode and parent/name-to-inode lookup entries.
- WSL and Interix special-file behavior depends on `vol->special_files`.

## Dependencies

- Heavy integration with `attrib.c`, `inode.c`, `mft.c`, `index.c`, `reparse.c`, `object_id.c`, `security.c`, `ea.c`, `cache.c`, and Unicode conversion helpers.
- Uses volume flags for case sensitivity, hidden/system visibility, dotfile hiding, compression, and locale/upcase/locase behavior.
- Uses cluster freeing through runlist decompression when deleting final links.

## Risks And Invariants

- Directory index and filename attributes must stay synchronized; rollback failures are logged as leaving inconsistent metadata.
- Deletion intentionally preserves the last filename attribute in the base record for undeletion unless it is in an extent.
- Cache invalidation is necessary after delete/rename-like namespace changes to avoid stale path and lookup results.
- DOS/Win32 namespace transitions are subtle because some names collapse to the same uppercase representation and some require alternate name deletion/reinsertion.
- Hard links to directories are allowed internally for rename-like temporary states but are unsafe as durable external state.
- Readdir `*pos` encodes root and allocation positions and must remain consistent with index block size and MFT record size.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/ea.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/ea.c

## Scope

This file implements NTFS extended attribute handling for raw `AT_EA` and `AT_EA_INFORMATION` attributes, plus helpers for WSL special-file EAs `$LXMOD` and `$LXDEV`.

## Public And Internal APIs Covered

- Public APIs:
  - `ntfs_get_ntfs_ea()`
  - `ntfs_set_ntfs_ea()`
  - `ntfs_remove_ntfs_ea()`
  - `ntfs_ea_check_wsldev()`
  - `ntfs_ea_set_wsl_not_symlink()`
- Internal helpers:
  - `ntfs_need_ea()`
  - `restore_ea_info()`
  - `ntfs_update_ea()`

## Control Flow And Behavior

- `ntfs_need_ea()` ensures a required `AT_EA` or `AT_EA_INFORMATION` attribute exists. It creates missing attributes on NTFS version 3 or newer unless `XATTR_REPLACE` was requested.
- `restore_ea_info()` restores the old `EA_INFORMATION` value, or removes the current one, after an EA update failure. It preserves the caller’s original `errno`.
- `ntfs_update_ea()` writes `EA_INFORMATION` first, then truncates/writes `AT_EA`. If the EA write fails, it attempts to restore previous EA metadata.
- `ntfs_get_ntfs_ea()` reads the entire raw `AT_EA` attribute and returns its size, copying into the caller buffer only when it fits.
- `ntfs_set_ntfs_ea()` validates the packed EA list: increasing aligned `next_entry_offset`, non-empty name, NUL-terminated name, bounded name/value data, and final packed/query length accounting. It computes `need_ea_count`, packed length, and query length, saves the old information attribute if present, creates missing attributes, then updates both attributes.
- `ntfs_remove_ntfs_ea()` removes `AT_EA_INFORMATION` and `AT_EA`, attempting restoration if removal partially fails. It marks filename and inode state dirty.
- `ntfs_ea_check_wsldev()` scans raw EAs for `$LXDEV`, decodes little-endian major/minor values, and returns a `dev_t` for WSL block/character devices.
- `ntfs_ea_set_wsl_not_symlink()` constructs `$LXMOD` for WSL special-file mode and optionally `$LXDEV` for block/character devices, then writes the packed EA list.

## State And Data Structures

- Uses on-disk `EA_ATTR` records and `EA_INFORMATION`.
- WSL EA names are fixed as `$LXMOD` and `$LXDEV`.
- Device EAs store little-endian 32-bit major/minor values.

## Dependencies

- Uses attribute existence, creation, opening, truncation, reading, writing, and removal APIs from `attrib.c`.
- Uses dirty inode/file-name flags for metadata propagation.
- Uses xattr flags `XATTR_CREATE` and `XATTR_REPLACE`.
- Uses platform `major()`, `minor()`, and `makedev()` macros.

## Risks And Invariants

- `EA_INFORMATION` and `AT_EA` must be updated together; inconsistency is logged when rollback fails.
- The setter deliberately does not validate EA name character sets because Windows `chkdsk` accepts broad input.
- The code no longer forbids simultaneous EA and reparse point presence, matching newer Windows behavior but possibly affecting older Windows versions.
- WSL EA scanning assumes the stored EA list is structurally sane enough to follow `next_entry_offset`.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/efs.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/efs.c

## Scope

This file provides limited support for NTFS EFS encrypted-file metadata. It can get and set EFS logged utility stream data and fix raw encrypted data attributes restored from backup-style formats.

## Public And Internal APIs Covered

- Public APIs:
  - `ntfs_get_efs_info()`
  - `ntfs_set_efs_info()`
  - `ntfs_efs_fixup_attribute()`
- Internal helper:
  - `fixup_loop()`

## Control Flow And Behavior

- `ntfs_get_efs_info()` requires the inode to have `FILE_ATTR_ENCRYPTED`, reads `AT_LOGGED_UTILITY_STREAM`, verifies the EFS header length equals the attribute size, and copies the data to the caller buffer when it fits.
- `ntfs_set_efs_info()` rejects already encrypted or compressed inodes, validates that the supplied EFS header length equals the supplied size, creates a `$EFS` logged utility stream if absent and replacement was not requested, writes the supplied EFS data, then fixes all non-directory data attributes and marks the inode encrypted.
- `fixup_loop()` iterates all `AT_DATA` attributes, opens each one, forces unencrypted data streams to nonresident form when needed, and calls `ntfs_efs_fixup_attribute()`. If making an attribute nonresident reorganizes the MFT record, it restarts attribute enumeration with progress checks to avoid repeated failure loops.
- `ntfs_efs_fixup_attribute()` converts a raw encrypted stream into NTFS encrypted-attribute form. It reads the two-byte appended padding length, validates stream size and padding, truncates away the appended padding-length marker, ensures the attribute is nonresident, updates unnamed inode data/allocated sizes, sets data and initialized sizes in the attribute record, and sets `ATTR_IS_ENCRYPTED`.

## State And Data Structures

- The named logged utility stream is `$EFS`.
- EFS metadata is expected to start with `EFS_ATTR_HEADER`.
- Encrypted data attributes must be nonresident and flagged with `ATTR_IS_ENCRYPTED`.

## Dependencies

- Uses attribute APIs for stream creation, open, truncate, read, write, lookup, and nonresident conversion.
- Uses inode dirty and filename dirty flags.
- Uses xattr replacement flags for set semantics.
- Uses directory/inode flags to skip data-attribute fixup for directories.

## Risks And Invariants

- The implementation does not decrypt data; it only preserves/restores EFS metadata and raw encrypted stream layout.
- Setting EFS on compressed files is rejected; a comment notes restored encrypted files in compressed directories may need decompression first.
- `ntfs_set_efs_info()` warns that the new EFS data is not deeply checked beyond header length.
- Raw encrypted stream sizes must satisfy NTFS padding layout: nonzero raw size has `(oldsize & 511) == 2`, with a valid final two-byte padding count.
- Attribute-record relocation during nonresident conversion requires search-context reinitialization.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/efs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/index.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/index.c

## Scope

This file implements the generic NTFS index engine used for directory and metadata indexes. It provides index contexts, lookup by collation, index entry insertion, B+tree block split/reparenting, entry removal, index block bitmap management, consistency checks, filename index insertion/removal wrappers, index root extraction, and in-order index traversal.

## Public And Internal APIs Covered

- Public context and dirty APIs:
  - `ntfs_index_ctx_get()`
  - `ntfs_index_ctx_put()`
  - `ntfs_index_ctx_reinit()`
  - `ntfs_index_entry_mark_dirty()`
- Public lookup and traversal:
  - `ntfs_index_lookup()`
  - `ntfs_index_next()`
  - `ntfs_ie_get_vcn()`
- Public mutation APIs:
  - `ntfs_ie_add()`
  - `ntfs_index_add_filename()`
  - `ntfs_index_rm()`
  - `ntfs_index_remove()`
- Validation and extraction:
  - `ntfs_index_block_inconsistent()`
  - `ntfs_index_entry_inconsistent()`
  - `ntfs_index_root_get()`
- Debug helpers:
  - `ntfs_ie_filename_get()`
  - `ntfs_ie_filename_dump()`
  - `ntfs_ih_filename_dump()`
- Internal helpers cover index-entry navigation/copy/insert/delete, root lookup and resizing, index block read/write/allocation, bitmap allocation/free, root-to-block conversion, block splitting, parent stack manipulation, deletion cleanup, and tree walking.

## Control Flow And Behavior

- `ntfs_index_lookup()` opens the named `INDEX_ROOT`, validates block size, chooses the collation function from the root collation rule, searches root entries, and descends through `INDEX_ALLOCATION` blocks until it finds a matching key, an insertion point, or corruption.
- `ntfs_ie_lookup()` scans one `INDEX_HEADER`, validates entry bounds and key/data layout, collates the search key against each entry, returns a found entry, an insertion point, or the child VCN to continue searching.
- `ntfs_index_context` tracks the current inode, index name, root search context, allocation attribute, current index block, current entry/data, dirty state, root-vs-block location, block size, VCN size, collation function, and parent VCN/position stack for later insert/remove operations.
- `ntfs_index_entry_mark_dirty()` marks the owning inode dirty for root entries or marks the loaded index block dirty for allocation entries. `ntfs_index_ctx_put()` writes dirty index blocks before freeing context resources.
- Insertions use `ntfs_ie_add()`: lookup determines the insertion point, enough room is required in the current root/block, and otherwise `ntfs_ir_make_space()` or `ntfs_ib_split()` grows the tree before retrying.
- Root growth first tries resident `$INDEX_ROOT` resize. If it no longer fits, `ntfs_ir_reparent()` creates `$BITMAP` and `$INDEX_ALLOCATION`, moves existing root entries into a new index block, converts root to a large-index node pointing at that block, and can add an attribute list or move records when MFT space is tight.
- Index block splitting chooses a median entry, allocates a free index block VCN through the bitmap, copies the tail to the new block, inserts the median into the parent root/block, and cuts the old block tail.
- `ntfs_index_add_filename()` wraps filename insertion by building an `INDEX_ENTRY` from a `FILE_NAME_ATTR` and MFT reference, then inserting it into `$I30`.
- Removal uses `ntfs_index_rm()`. Leaf entries are deleted directly unless the block would become empty; node entries are replaced with a successor from the leftmost descendant of the following child, then the successor is removed. Empty leaf blocks are cleared in the bitmap and parent entries are adjusted or root is converted back to a leaf.
- `ntfs_index_remove()` wraps lookup plus removal for `$I30`, retrying when tree restructuring requests another pass.
- Bitmap helpers create `$BITMAP` when needed, set/clear allocation bits, extend bitmap size in 8-byte increments, and find a free VCN for new index blocks.
- `ntfs_index_next()` walks the B+tree in collation order from a lookup result, descending into child nodes and walking back up through the parent stack when reaching end entries.

## State And Data Structures

- Uses `INDEX_ROOT`, `INDEX_BLOCK`, `INDEX_HEADER`, and `INDEX_ENTRY` on-disk layouts.
- Uses `AT_INDEX_ROOT`, `AT_INDEX_ALLOCATION`, and `AT_BITMAP` attributes.
- Maintains parent navigation in `parent_vcn[]`, `parent_pos[]`, and `pindex`, bounded by `MAX_PARENT_VCN`.
- Index blocks are MST-protected records written through `ntfs_attr_mst_pwrite()` and read through `ntfs_attr_mst_pread()`.

## Dependencies

- Relies on `collate.c` for collation-rule dispatch.
- Relies on `attrib.c` for attribute lookup, resize, add, truncate, read/write, and resident value manipulation.
- Uses `bitmap.c`, `mst.h`, `dir.h`, `reparse.h`, and common NTFS layout definitions.
- Directory creation/deletion/link code in `dir.c` depends on these index mutation APIs.

## Risks And Invariants

- Index root must remain resident; when it fills, entries are moved to index allocation blocks instead of making root nonresident.
- Every allocated index block must be reflected in the `$BITMAP`; split and reparent failure paths clear bitmap bits where possible.
- Parent stack depth is bounded; deeper trees return `EOPNOTSUPP`.
- Entry lengths, key lengths, data offsets, index lengths, allocated sizes, VCNs, and magic signatures are validated before traversal.
- Some cleanup paths note limited error recovery; failure to write dirty blocks or rollback root changes can leave inconsistent indexes.
- Removal logic depends on preserving B+tree ordering while replacing internal-node keys with successor entries.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/index.c -->