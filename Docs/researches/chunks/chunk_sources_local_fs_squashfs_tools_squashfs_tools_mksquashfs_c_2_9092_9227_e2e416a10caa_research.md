# Chunk Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c lines 9092-9227

## Scope

This report covers `sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c` lines 9092-9227 for subset A (`Docs/research_subset_a.md`). The chunk is the final tail of `main()`: it finishes append-mode state preservation, reconfigures in-memory inode/directory caches for appending, dispatches the selected input scanner, fills the Squashfs superblock, drains pending fragment writes, serializes metadata tables, pads/truncates the destination, writes the final superblock, and closes/logs/prints summary state. It does not create or update the merged per-file report.

## Public And Internal APIs Covered

- `write_recovery_data(&sBlk)` records the original metadata tail for append recovery before any new filesystem content is committed.
- `save_xattrs()` snapshots append-time xattr state so abort/recovery can restore xattr accounting consistently with the earlier saved inode, directory, fragment, id, and count globals.
- `add_old_root_entry(root_name, sBlk.root_inode, inode_dir_inode_number, SQUASHFS_DIR_TYPE)` records the previous root directory as an entry when `-root-becomes` turns the old root into a subdirectory of the new root.
- Source dispatch calls exactly one of `process_tar_file(progress)`, `process_source(progress, deref, deref_keep)`, `no_sources(progress)`, or `dir_scan(S_ISDIR(source_buf.st_mode), progress, deref, deref_keep)`.
- `SQUASHFS_MKFLAGS(...)` packages compression/id/xattr/fragment/export/duplicate options into `sBlk.flags`.
- `get_frag_action(fragment)` and `write_fragment(*fragment)` flush fragment buffers left open by the file scan.
- `sync_writer_thread()` waits for writer completion; `pthread_cancel(writer_thread)` stops the writer after all queued data should be drained.
- `check_id_table_offset()` validates final id-table entries after `-uid-gid-offset`.
- `write_filesystem_tables(&sBlk)` writes inode, directory, fragment, optional lookup, id, and xattr tables and updates superblock offsets, `bytes_used`, compression id, and total-size accounting.
- `progressbar_finish()`, `ftruncate()`, alignment padding, `write_superblock(&sBlk)`, `close(fd)`, recovery-file unlink, `print_summary()`, and log close finish the command.

## Control Flow And Behavior

- The chunk begins inside append setup after the existing filesystem has already been read. It continues saving old counts and id/duplicate state, then writes recovery data and saves xattrs.
- With `root_name` set, the old root becomes a child directory in the new root. The code reserves two new inode numbers, moves the uncompressed directory tail to the front of `directory_data_cache`, injects an old-root entry, updates directory totals, and increments `dir_count`.
- Without `root_name`, appending targets the original root directly. The code saves the compressed directory region for rollback, rewinds directory bytes/cache bytes to the original root directory boundary, and reserves one new inode number.
- In both append cases, inode and directory cache sizes/positions are reset so new metadata appends from the old root/table boundary.
- `inode_count` is recomputed from object counters, then later copied into `sBlk.inodes`.
- The scan dispatcher chooses tar input, tar/cpio-style source, pseudo-only source, or normal directory scan. The returned inode becomes `sBlk.root_inode`.
- Superblock identity and options are finalized: magic, version, block size/log, flags, and mkfs time. Time precedence is explicit: command-line `mkfs_time`, latest inode time, then `time(NULL)`.
- Remaining fragment actions are flushed before writer synchronization and final table writing.
- Regular non-streaming outputs are truncated to `start_offset + get_dpos()`. Block devices and streaming outputs skip truncation.
- Unless `nopad` is set, the output is zero-padded to a 4096-byte boundary. The final superblock is written after padding.
- On success, any recovery file is removed, summary/log output is closed, and `main()` returns `0`.

## State And Data Structures

- `sBlk` is mutated from append input state into final output state: `root_inode`, `inodes`, magic/version, block layout, flags, and mkfs time are set here.
- Append rollback globals saved/configured here include `sdir_count`, `sfifo_count`, `ssock_count`, `sdup_files`, `sid_count`, `sdirectory_bytes`, `sdirectory_compressed_bytes`, and `sdirectory_compressed`.
- Active metadata-position globals adjusted here include `inode_bytes`, `inode_size`, `directory_size`, `cache_size`, `directory_cache_size`, `directory_bytes`, `directory_cache_bytes`, and `cache_bytes`.
- Inode numbering state is reset through `root_inode_number`, `inode_no`, and `inode_start_no`.
- Directory buffers are manipulated directly with `memmove()` and `memcpy()`.
- Fragment state flows through `fragment_table`, `fragments`, fragment actions, fragment mutex/queue state, and the writer queue.
- Output positioning depends on `fd`, `start_offset`, `get_dpos()`, `block_device`, `streaming`, and `nopad`.

## Dependencies

- This chunk depends on the preceding append-read setup from `read_filesystem()`, which populates old superblock state, inode/directory caches, table offsets, object counts, fragment tables, and root directory metadata.
- Recovery depends on earlier failure handling and `restorefs()`, which consumes the saved `s*` globals.
- Directory/source ingestion is implemented earlier by `process_tar_file()`, `process_source()`, `no_sources()`, and `dir_scan()`.
- `add_old_root_entry()` feeds append-aware directory handling such as `handle_root_entries()`.
- Metadata table writing delegates to `write_inodes()`, `write_directories()`, `write_fragment_table()`, `write_inode_lookup_table()`, `write_id_table()`, and `write_xattrs()`.
- Thread/queue correctness depends on previously initialized writer, fragment, orderer, and progress infrastructure.
- POSIX/C dependencies include `memmove()`, `memcpy()`, `time()`, `pthread_cancel()`, `ftruncate()`, `strerror()`, `close()`, and `unlink()`.

## Risks And Invariants

- Append mode must snapshot original state before mutation; mismatched saved counters/cache slices could make `restorefs()` write a malformed recovery image.
- The `root_name` and non-`root_name` append paths preserve different directory-table regions, so directory/cache boundaries must match the selected mode.
- In the root-becomes case, `sdirectory_compressed_bytes` is zero and no compressed-directory allocation is made; later zero-length restore copies must remain harmless.
- Inode-number offsets differ by append mode. Off-by-one errors could collide with old root entries or corrupt lookup/export tables.
- The fragment flush loop assumes `get_frag_action()` terminates and all queued fragments are handled before writer sync completes.
- Cancelling `writer_thread` after sync assumes no further queued data writes remain before synchronous metadata writes.
- `check_id_table_offset()` must run before emitting the id table so invalid offset-adjusted ids do not enter the image.
- Padding affects physical file length, not logical Squashfs `bytes_used`.
- The final superblock is written last, preserving append safety against interrupted builds.

## Cross-Chunk References

- The preceding chunk contains most of `main()` argument parsing, destination setup, compressor option emission, append filesystem reading, and the first half of original-state saving.
- Earlier same-file helpers used here include `write_fragment()` around line 1752, `dir_scan()` around line 3808, `process_source()` around line 5361, `no_sources()` around line 5479, `add_old_root_entry()` around line 5610, `write_recovery_data()` around line 6049, `write_filesystem_tables()` around line 6198, `write_superblock()` around line 6227, and `print_summary()` around line 6576.
- Top-of-file globals define append rollback buffers/counters, destination state, compression/options state, progress/logging flags, and helper prototypes.
- Separate xattr support supplies `save_xattrs()`, `restore_xattrs()`, and `write_xattrs()`.
- This is the final chunk of `mksquashfs.c`; all control-flow dependencies point backward to setup, scanning, queueing, metadata writing, and recovery helpers.