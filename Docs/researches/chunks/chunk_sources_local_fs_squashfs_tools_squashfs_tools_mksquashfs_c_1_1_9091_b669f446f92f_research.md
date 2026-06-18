# Chunk Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.c lines 1-9091

## Scope

This chunk covers almost all of the `mksquashfs` implementation: global option and filesystem-build state, compression and metadata writers, file block/fragment deduplication, directory scanning and mutation passes, pseudo/action/exclude handling, append/recovery support, thread-pipeline setup, `sqfstar`, and most of `main()`.

The line boundary cuts through `main()` while setting up append mode after `read_filesystem()`. The final cleanup/writeout sequence is immediately after this chunk.

## APIs And State

- Global build options include compression toggles (`noI`, `noD`, `noF`, `noX`, `noId`), block size/log, fragment policy, duplicate checking, exportability, sparse detection, root/global mode/uid/gid overrides, timestamp reproducibility controls, tar/cpio/source style, hardlink and filesystem-boundary policy, xattr regex/add state, logging/info/progress controls, output offset/streaming mode, and append/recovery state.
- Filesystem assembly state is centralized in globals: `sBlk`, `total_bytes`, inode and directory metadata buffers/caches, fragment table, id table/hash, inode hash, duplicate block/fragment hash tables, inode numbering, source list, destination fd/path, output virtual/physical position, and old-root-entry lists used during append.
- Threading state is also global: caches/queues (`fragment_buffer`, `reserve_cache`, `fwriter_buffer`, `bwriter_buffer`, `to_reader`, `to_deflate`, `to_frag`, `to_order`, `to_writer`, `to_main`), pthread ids, and mutexes for fragments, lseek/fd position, duplicate lookup, and disk position.
- Public or cross-module functions visible in this chunk include `pre_exit_squashfs()`, `restorefs()`, `mangle()`, `read_bytes()`, `read_fs_bytes()`, `write_destination()`, `generic_write_table()`, `get_checksum_mem()`, `add_file()`, `write_file()`, inode lookup helpers, directory entry helpers, `do_directory_scans()`, `excluded()`, `open_info_file()`, `convert_to_action()`, and `main()`.
- On-disk format emission is done through Squashfs structs and swap macros from `squashfs_fs.h` / `squashfs_swap.h`: inode variants, directory headers/entries/indexes, fragment entries, id table, lookup table, xattr table, and superblock.

## Control Flow

- Startup:
  - `main()` records command lines via `SQFS_CMDLINE`, configures pager/help behavior, dispatches to `sqfstar()` when invoked under that name, finds source/output argument split, pre-scans for compressor selection and stdin-consuming modes, parses all options, validates conflicts, opens/creates/truncates or reads the destination, processes excludes and sort files, initializes threads, initializes the compressor stream, and sets initial output position.
  - `sqfstar()` is a tar-focused alternate entry path with mostly parallel option parsing. It forces tar mode, disables append, defaults exportability off and tail-end packing on, opens destination/stdout, processes exclude paths, initializes the same thread/compression/dedup infrastructure, then calls `process_tar_file()`.
- Compression and metadata:
  - `mangle2()` compresses a block with the selected compressor unless disabled, stores uncompressed data if compression is ineffective, and marks Squashfs compressed/uncompressed bits.
  - `get_inode()`, `write_inodes()`, `write_directories()`, and `write_dir()` buffer metadata in `SQUASHFS_METADATA_SIZE` chunks, compress them, write metadata-block length headers, and update uncompressed/compressed byte accounting.
  - `create_inode()` converts in-memory `dir_ent`/`inode_info` data into the correct Squashfs inode variant, choosing long inode forms when size, nlink, sparse, xattr, or directory-index state requires it.
- File-data path:
  - Reader threads from `reader.c` feed `to_deflate`; `deflator()` compresses file blocks or marks all-zero sparse blocks and posts ordered results to `to_main`.
  - `write_file()` consumes file buffers and delegates to empty, fragment-only, normal block, or duplicate-checking block paths.
  - `orderer()` maps virtual positions to physical disk positions and hands buffers to `writer()`.
  - `frag_deflator()` compresses completed fragment blocks; `write_fragment()` queues them; `orderer()` records fragment table start/size before writing.
- Directory/source scanning:
  - `dir_scan1()` recursively builds the in-memory directory tree from real files, applying excludes, one-filesystem policy, depth limits, and exclude actions.
  - `do_directory_scans()` runs pseudo/action application, move, prune, empty-dir, deterministic sort/inode numbering, file-data writing, and final metadata emission.
  - Symlink dereference actions are two-phase: mark first, then mutate/delete/clone directory subtrees.
- Append and recovery:
  - Existing images are loaded through `read_super()` / `read_filesystem()`.
  - Recovery files store the original superblock and metadata tail; `restorefs()` can rewrite saved state after interrupted append.

## Dependencies

- Local Squashfs modules: format/swap macros, compressor abstraction, xattrs, pseudo files, actions, progress/info/error helpers, caches/queues/lists, existing-filesystem reader, restore thread, fragment processor, tar reader, sort lists, memory/alloc wrappers, reader threads, rate limit, virtual disk position map, uid/gid parsers, date and symbolic-mode helpers.
- POSIX/libc APIs: file I/O, directory traversal, stat/lstat/fstat, readlink, pthreads, signals, regex/fnmatch, user/group lookup, environment variables, and block-device/regular-file checks.
- External behavior depends on compressor plugins, xattr support, physical memory discovery, `SOURCE_DATE_EPOCH`, optional `SQFS_CMDLINE`, and tar parsing.

## Risks

- Large mutable global state is shared across passes and worker threads.
- `pathname()` and `subpathname()` return static buffers.
- `read_bytes()` / `write_bytes()` use GNU C `void *` pointer arithmetic.
- Deduplication depends on virtual-to-physical mapping, cache lookups, disk readback, and rollback correctness.
- Append mode has complex state snapshots and recovery paths.
- Many deep helpers terminate via `BAD_ERROR()` / `EXIT_MKSQUASHFS()`.
- UID/GID offset validation happens late, after most image work.

## Cross-Chunk References

- Lines after 9091 finish `main()` append setup, dispatch to the selected source-processing path, fill the final superblock, flush fragments, sync/cancel writer, write tables, pad/truncate, write superblock, close output/log, and return.
- External functions required to complete the pipeline include `initial_reader`, `frag_thrd`, `process_tar_file`, `eval_*_actions`, `sort_files_and_write`, `generate_file_priorities`, `read_super`, `read_filesystem`, `restore_xattrs`, `save_xattrs`, `write_xattrs`, `read_xattrs`, `get_frag_action`, and virtual-position helpers.