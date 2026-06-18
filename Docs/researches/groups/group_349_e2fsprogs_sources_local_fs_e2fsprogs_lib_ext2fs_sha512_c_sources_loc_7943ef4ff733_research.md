# Group Research: group_349_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_sha512_c_sources_loc_7943ef4ff733

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/e2fsprogs` is in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sha512.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/sha512.c

Implements a standalone SHA-512 digest routine for libext2fs, copied from libtomcrypt and relicensed under LGPLv2 terms for this file. The public entry point is `ext2fs_sha512(const unsigned char *in, unsigned long in_size, unsigned char out[EXT2FS_SHA512_LENGTH])`.

The file defines SHA-512 constants, rotate/load/store macros, a compact hash state, and the usual init/process/compress/finalize pipeline. It assumes messages fit in a 64-bit bit-length counter during final padding. Under `UNITTEST`, it includes three standard SHA-512 test vectors: empty string, `"abc"`, and a longer NIST-style test string.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sha512.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sparse_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/sparse_io.c

Provides libext2fs I/O managers for Android sparse images: `sparse_io_manager` for filenames and `sparsefd_io_manager` for already-open fds. If `ENABLE_LIBSPARSE` is not enabled, both managers expose only open/close stubs returning `EXT2_ET_UNIMPLEMENTED`.

With libsparse enabled, it imports sparse chunks into an in-memory `blocks` array keyed by sparse block number, supports block-size remapping between ext2fs channel block size and sparse image block size, and writes the final sparse image on close. It implements read/write, partial negative-count I/O, discard/zeroout by freeing stored blocks, flush as a no-op, and readahead/set-option no-ops.

Important behavior: write-open truncates or uses the provided fd and rebuilds a sparse output file on close. Existing sparse images are imported through `sparse_file_foreach_chunk`. Writes past `blocks_count` silently stop. The parser accepts strings like `(file):blocks:block_size` or `(fd):blocks:block_size`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sparse_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/swapfs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/swapfs.c

Contains endian-swapping routines for ext2/ext3/ext4 on-disk structures. Major entry points include `ext2fs_swap_super`, `ext2fs_swap_group_desc2`, `ext2fs_swap_group_desc`, `ext2fs_swap_inode_full`, `ext2fs_swap_inode`, `ext2fs_swap_mmp`, and directory-entry swab helpers.

The superblock swap covers legacy and modern fields including 64-bit block counts, MMP, snapshot, quota, metadata checksum, encoding, and orphan-file fields. Build-time assertions are used to catch reserved-field layout drift. Group descriptor swapping handles 32-bit descriptors and 64-bit descriptor extensions depending on filesystem descriptor size.

Inode swapping is careful about in-place conversion: it determines symlink/extent/inline-data state before or after byte swapping depending on direction. Extent and inline-data payloads in `i_block` are intentionally not swapped here because they are swapped on access. Extended attributes inside large inodes are also swapped when present.

Directory entry swabbing validates record lengths and name lengths unless `EXT2_FLAG_IGNORE_SWAP_DIRENT` is set. The output path returns corruption for malformed directory records.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/swapfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/symlink.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/symlink.c

Implements `ext2fs_symlink`, the libext2fs helper for creating symlink inodes and optionally linking them into a directory. It validates the target length against filesystem block size, allocates an inode if the caller did not supply one, and supports fast symlinks, inline-data symlinks, and regular block-backed symlinks.

Fast symlinks store the target directly in `inode.i_block`. Inline symlinks are attempted when the filesystem has inline-data support; on failure the code falls back to block-backed storage. Regular symlinks allocate one data block, optionally mark the inode extents-based, set the block mapping with `ext2fs_bmap2`, and write the target block through the filesystem I/O channel.

Accounting is updated after inode/block writes. If later linking or setup fails, `drop_refcount` rolls back inode and block allocation stats. The companion `ext2fs_is_fast_symlink` detects symlink inodes with nonzero size smaller than `i_block`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.c

This is a standalone imported Samba TDB implementation, generated from Samba common TDB sources. The header comment identifies Samba branch source `source/lib/tdb/common`, revision `23590`, dated 2007-06-22. It implements a small hash-table database with fixed on-disk records, freelist allocation, fcntl locks, optional mmap, transactions, traversal, and CRUD operations.

The on-disk format is centered on `struct tdb_header` and `struct list_struct`. A database starts with magic/version/hash metadata, a freelist head, and hash-chain heads. Each record stores next offset, total record length, key length, data length, full hash, magic, then key/data/tailer payload. Magic values distinguish live, free, dead, and recovery records.

Locking is byte-range fcntl based. It supports per-chain locks, freelist lock, global lock, transaction lock, read/write chain locks, nonblocking lock variants, and special mark-only locks. It tracks locks in `tdb_context` because POSIX locks do not nest. Traversal uses record locks to prevent deletion under iteration; if deletion collides with traversal, records can be marked dead and purged later.

I/O abstracts through `tdb_methods`, normally backed by `tdb_read`, `tdb_write`, mmap management, out-of-bounds checks, file expansion, and byte-range locks. It can fall back to `pread`/`pwrite` when mmap is unavailable or disabled. Endian conversion is supported through `TDB_CONVERT`, operating on 4-byte quantities.

Transactions intercept reads/writes by swapping the methods table to transaction-specific methods. Writes are stored in ordered transaction elements, with a mirrored hash-head table for traversal. Commit writes recovery data unless `TDB_NOSYNC` is set, upgrades locks, writes all modified regions, fsyncs/msyncs, clears recovery magic, updates mtime via `utime` where available, and then cancels the transaction state. Recovery restores old data from the recovery area and truncates the file to the old size.

Freelist management uses best-fit allocation, record splitting, tailers, and coalescing with adjacent free records. `tdb_validate_freelist` detects freelist loops by using an internal memory-only TDB as a seen set.

Public operations include open/open_ex, close, fetch, parse_record, store, append, delete, exists, firstkey/nextkey, traverse/traverse_read, lockall variants, chainlock variants, transactions, sequence-number helpers, debug dumps, freelist printing/validation, reopen/reopen_all, and flush. The default hash is a simple byte-accumulating algorithm seeded by key length.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.h

Public header for the bundled TDB library. It defines flags for `tdb_store` and `tdb_open`, error codes, debug levels, `TDB_DATA`, logging/hash callback types, and `struct tdb_logging_context`.

For libext2fs integration, it macro-renames the generic TDB symbols to `ext2fs_tdb_*` names, avoiding collisions with system or Samba TDB libraries. Exposed APIs cover opening, closing, fetching, parsing, storing, appending, deleting, traversal, key iteration, whole-database and chain locking, transactions, sequence numbers, flags/sizes, flush, and debug/freelist utilities.

The context is opaque as `struct tdb_context` / `TDB_CONTEXT`; implementation details live in `tdb.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb/build-tdb -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb/build-tdb

Shell script used to rebuild the standalone bundled TDB files from a Samba checkout. It sets `BASE_DIR`, removes `.pc`, captures SVN metadata, starts a generated `tdb.c` with source URL/revision/date, appends `tdb_private.h`, and concatenates selected Samba common files after stripping includes up to `tdb_private.h`.

The source list includes error, lock, io, transaction, freelist, freelistcheck, traverse, dump, tdb, and open modules. It also copies `tdb.h` and `tdbtool.c`, then runs `quilt push -a`, implying local patch application after import.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdb/build-tdb -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdbtool.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdbtool.c

Interactive and command-line utility for inspecting and modifying TDB databases. It is imported from Samba tooling and uses the bundled `tdb.h` API.

Commands include create, open, erase, dump, insert, move, store, show, keys, hexkeys, delete, list hash/free chains, free, info, first/next iteration, shell escape, help, and quit. The tool can open a database passed as argv[1], then either run interactively or execute a command from argv.

It prints records as ASCII plus hex dumps, supports escaped byte input through backslash hex parsing, traverses for summary byte counts, and can move a record into another TDB. The `erase` command deletes records during traversal. The `!` command passes text to `system`, so this is a developer/debug utility rather than a constrained parser.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tdbtool.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/test_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/test_io.c

Implements `test_io_manager`, a wrapper I/O manager for libext2fs tests. It optionally delegates to `test_io_backing_manager` while logging or instrumenting operations.

Configuration is controlled by globals and environment variables. Callback globals can observe read/write/blocksize/write-byte operations. `TEST_IO_LOGFILE`, `TEST_IO_FLAGS`, `TEST_IO_BLOCK`, `TEST_IO_READ_ABORT`, and `TEST_IO_WRITE_ABORT` control output, logging flags, watched block, and intentional abort counts.

The manager supports open, close, set block size, read/write block, read/write block64, write byte, flush, set_option, get_stats, discard, cache_readahead, and zeroout. It can dump watched block contents with checksums and abort after configured read/write hits, making it useful for reproducible failure-injection tests.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/test_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_badblocks.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_badblocks.c

Standalone test program for the libext2fs badblocks list implementation. It builds several test vectors, checks sorted/duplicate behavior, validates membership queries, performs add/delete sequences, compares lists, and tests file serialization/deserialization.

`file_test` writes a badblocks list to a temporary file and reads it back with `ext2fs_read_bb_FILE2`. `file_test_invalid` creates a minimal fake filesystem, appends an invalid block number to the serialized file, verifies the invalid-block callback fires, and confirms the resulting list still matches the valid input.

The program reports failures through `test_fail` and returns that count as its exit status.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_badblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitmaps.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitmaps.c

Interactive/scriptable test shell for libext2fs bitmap operations. It uses the `ss` command subsystem and exposes commands for setting up an in-memory test filesystem, dumping block/inode bitmaps, setting/clearing/testing single bits and ranges, finding first zero/set blocks or inodes, and clearing entire bitmaps.

`setup_filesystem` initializes a synthetic filesystem through `ext2fs_initialize` and `test_io_manager`, sets the requested bitmap backend type, and allocates fresh block and inode bitmaps. The default mode uses 64-bit bitmaps.

The program can run interactively, execute one request via `-R`, or source a command file via `-f`. It carefully resets `getopt` state for command handlers so repeated shell commands parse correctly across different libc implementations.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitmaps.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitops.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitops.c

Tests low-level bit operation helpers. It verifies `ext2fs_test_bit`, `ext2fs_set_bit`, `ext2fs_clear_bit`, fast set/clear variants, and their 64-bit equivalents against a known byte array and expected bit list.

It also allocates a large scratch array and tests a high bit number `((1U << 31) + 42)`, confirming that both regular and fast 32/64-bit bit operations address large bit indexes correctly. Failures print details and exit nonzero.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_byteswap.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_byteswap.c

Small test program for `ext2fs_swab16` and `ext2fs_swab32`. It defines input/output pairs, checks both forward and reverse swaps, prints each conversion, counts errors, and returns the error count.

It covers representative values including single-bit, patterned, high-bit, and zero cases.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_byteswap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_fs_struct.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_fs_struct.c

Prints field offsets and sizes for `struct struct_ext2_filsys`. It is a layout inspection tool rather than a strict validator: if padding exists between fields, it prints a padding note and continues.

Under GCC 4 or newer, it lists offsets for core filesystem context fields including I/O channel, flags, superblock, group descriptors, bitmaps, callbacks, badblocks, dblist, image fields, allocation hooks, MMP state, cache, and private data.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_fs_struct.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsectsize.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsectsize.c

Command-line test utility for sector-size and direct-I/O alignment probing. It requires a device path, calls `ext2fs_get_device_sectsize` for logical sector size and `ext2fs_get_device_phys_sectsize` for physical sector size, then opens the device read-only and prints `ext2fs_get_dio_alignment(fd)`.

Errors from ext2fs helpers are reported through `com_err`; open failures use `perror`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsectsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsize.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsize.c

Command-line test for `ext2fs_get_device_size2`. It takes a device path, initializes the ext2 error table, requests the size in 1024-byte blocks, prints the resulting block count, and exits nonzero on errors.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_inode_size.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_inode_size.c

Validates the layout of `struct ext2_inode_large`. For GCC 4 or newer, it checks expected field sizes and exact offsets for the classic 128-byte inode portion plus large-inode extension fields.

It exits immediately on size or offset mismatches. Covered fields include mode/uid/gid/timestamps, blocks, flags, Linux OS-dependent fields, checksum fields, extra timestamps, creation time, high version, and project ID.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_inode_size.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_iscan.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_iscan.c

Tests inode table scanning behavior in the presence of bad blocks. It creates a synthetic filesystem with `test_io_manager`, allocates inode tables and bitmaps, installs read callbacks that record every block touched, and marks a fixed list of bad inode-table blocks.

During `ext2fs_get_next_inode` iteration, `EXT2_ET_BAD_BLOCK_IN_INODE_TABLE` marks the affected inode in `bad_inode_map`. After scanning, it verifies no bad block was read, no inode-table block was missed, and no block was read twice. It prints touched ranges and bad inodes, returning failure count.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_libext2fs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_libext2fs.c

Adds libext2fs-specific commands into the debugfs command environment for testing. It sets `debug_prog_name` to `tst_libext2fs` and hooks `extra_cmds` to `libext2fs_cmds`.

The implemented command here is `do_block_iterate`, which resolves a file argument to an inode, parses optional flags, forces `BLOCK_FLAG_READ_ONLY`, and calls `ext2fs_block_iterate3`. The callback prints logical block count, physical block number, reference offset, and reference block.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_libext2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_super_size.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_super_size.c

Validates the exact field layout of `struct ext2_super_block`. Under GCC 4 or newer, it checks field sizes and offsets in order and exits on mismatch.

The checked fields cover legacy ext2 superblock data, journal metadata, ext4 64-bit fields, MMP, RAID layout, snapshot fields, error tracking, mount options, quota inode numbers, encryption metadata, checksum seed, high timestamp bytes, encoding fields, orphan-file inode, reserved space, and final checksum. It verifies the final superblock size reaches 1024 bytes.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_super_size.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_types.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_types.c

Simple ABI sanity test for `ext2fs/ext2_types.h`. It verifies signed and unsigned fixed-width ext2 types have expected sizes: 8-bit types are 1 byte, 16-bit types 2 bytes, 32-bit types 4 bytes, and 64-bit types 8 bytes.

On mismatch it prints the offending type size and exits nonzero; on success it prints that the ext2 types are correct.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/tst_types.c -->