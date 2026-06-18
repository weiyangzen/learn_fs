# sources/distributed-fs/ceph-client/fs/exfat/dir.c

## Purpose
`dir.c` implements exFAT directory entry parsing, iteration, entry-set caching, filename dentry assembly, directory checksum updates, empty-slot validation, lookup scanning, subdirectory counting, new directory allocation, and volume label read/write. exFAT represents one file with a primary file dentry, a stream-extension dentry, one or more filename dentries, and optional secondary dentries; this file owns that multi-entry contract.

## Important APIs, types, and functions
Directory iteration uses `exfat_readdir()` and `exfat_iterate()` exported through `exfat_dir_operations`. Entry type decoding and construction use `exfat_get_entry_type()`, `exfat_set_entry_type()`, `exfat_init_dir_entry()`, `exfat_init_stream_entry()`, `exfat_init_name_entry()`, `exfat_init_ext_entry()`, and `exfat_calc_num_entries()`.

Entry-set cache APIs are `exfat_get_dentry()`, `exfat_get_dentry_cached()`, `exfat_get_dentry_set()`, `exfat_get_empty_dentry_set()`, and `exfat_put_dentry_set()`. `exfat_update_dir_chksum()` computes the primary-file checksum while skipping the checksum field. `exfat_remove_entries()` marks entry sets deleted and frees benign secondary allocated clusters.

Search and metadata helpers include `exfat_find_dir_entry()`, `exfat_count_dir_entries()`, `exfat_alloc_new_dir()`, `exfat_read_volume_label()`, and `exfat_write_volume_label()`.

## Control flow
`exfat_iterate()` emits dot entries, rounds VFS position to dentry size, allocates a temporary name buffer, and repeatedly calls `exfat_readdir()` under `s_lock`. `exfat_readdir()` uses directory hints, walks clusters, skips non-file entries, reads the full name from extension entries, converts UTF-16 to the mounted NLS/UTF-8 encoding, updates the directory bitmap hint, and advances `ctx->pos` past the whole entry set.

`exfat_get_dentry()` maps a logical directory entry index to sector/offset using `exfat_find_location()`, checks chain and bitmap validity, optionally triggers readahead, and returns a direct pointer into a buffer head. Entry-set fetches read enough adjacent sectors to cover all requested dentries; validation enforces file -> stream -> name -> optional benign-secondary ordering. Empty entry-set validation accepts deleted after unused for compatibility but reports used-after-unused corruption.

`exfat_find_dir_entry()` is the main case-insensitive scanner. It uses `hint_stat` to avoid restarting from zero, tracks a file/stream/name/secondary state machine, matches stream name hash and length before comparing filename dentries with `exfat_uniname_ncmp()`, records first-empty-entry hints, rewinds once to cover entries before the hint, and detects excessive cluster traversal. Volume label helpers scan root entries for `TYPE_VOLUME`, reuse the first empty slot if needed, and update a single dentry.

## State and persistence behavior
Persistent state is the directory entry stream itself: file, stream, name, volume label, bitmap, upcase, and secondary dentries. Modifications are made through buffer-head-backed entry sets; `es->modified` controls whether `exfat_update_bhs()` writes dirty buffers. Directory checksums are persisted in the file dentry. Runtime state includes directory hints (`hint_bmap`, `hint_stat`, `hint_femp`) in `exfat_inode_info`, temporary `exfat_entry_set_cache` buffer arrays, and name buffers allocated from the name cache.

## Dependencies and integration points
This file depends on FAT/cluster walking, bitmap testing, NLS conversion, checksum/time helpers, buffer-head I/O, VFS directory iteration, file ioctls/fsync from `file.c`, and inode building/lookup from `inode.c`/`namei.c`. It is central to mount-time bitmap/upcase discovery, path lookup, create/mkdir/rename/unlink, readdir, stat link counts, and filesystem label ioctls.

## Risks and test signals
Risks include entry-set validation accepting corrupt layouts, checksum drift after partial updates, stale hints after directory mutation, off-by-one positions across cluster boundaries, direct buffer-head pointer lifetime misuse, benign secondary cluster leaks, looped directory FAT chains, and compatibility behavior around unused/deleted dentries. Tests should cover long 255-character names, names spanning sector and cluster boundaries, directory growth, deletion/reuse hints, corrupted stream/name ordering, volume label create/clear/update, readdir while mutating, empty directories with zero-size and allocated clusters, and fsck images with loops or bitmap mismatches.
