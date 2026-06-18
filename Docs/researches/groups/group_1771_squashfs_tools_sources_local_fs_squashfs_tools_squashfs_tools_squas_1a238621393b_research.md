# Group Research: group_1771_squashfs_tools_sources_local_fs_squashfs_tools_squashfs_tools_squas_1a238621393b

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_compat.h

This header defines compatibility on-disk layouts for Squashfs 1.x, 2.x, and 3.x filesystems. It is consumed by the legacy `unsquash-*` readers to parse old superblocks, inode formats, directory entries, fragment entries, and bitfield-packed structures.

Key contents:
- 3.x layout: `squashfs_super_block_3`, v3 inode headers, directory index/header/entry types, fragment entry, and swap macros.
- 1.x layout: compact inode headers with 4-bit uid/gid indexes and no fragment table support.
- 2.x layout: v2 inode and directory formats, fragment entries, and packed directory index fields.
- Compatibility constants such as `SQUASHFS_UIDS`, `SQUASHFS_GUIDS`, `SQUASHFS_TYPES`, and old `SQUASHFS_CHECK_DATA`.
- Bitfield-aware `SQUASHFS_SWAP_*_{1,2,3}` macros for cross-endian legacy metadata.

Important behavior:
- The swap macros reconstruct bitfields by copying raw bytes into a 64-bit scratch value and shifting according to host byte order.
- `SQUASHFS_MEMSET(s, d, n)` zeroes the destination structure before assigning swapped fields, which avoids stale padding or unused fields.
- v2 and v3 use different fragment index widths: v2 indexes are 32-bit, v3 indexes are 64-bit.

Corruption-sensitive details:
- Legacy readers depend on exact bit positions in these macros; changing structure fields or swap offsets breaks old-image compatibility.
- The header assumes `SQUASHFS_METADATA_SIZE` and core v4 types from `squashfs_fs.h` are already available.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_fs.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_fs.h

This is the primary Squashfs 4.0 on-disk format header. It defines current filesystem constants, flag encodings, inode/address helpers, table sizing macros, compression ids, and all v4 disk structures.

Key contents:
- Filesystem identity: `SQUASHFS_MAGIC`, streamed variants, major/minor `4:0`.
- Metadata sizing: 8192-byte metadata blocks, default 128 KiB data blocks, max 1 MiB block setting.
- Flag bits and helpers for uncompressed inodes/data/fragments/xattrs/ids, fragments, duplicates, exportability, compressor options, and xattr disabling.
- Inode address helpers: `SQUASHFS_INODE_BLK`, `SQUASHFS_INODE_OFFSET`, `SQUASHFS_MKINODE`.
- Table sizing macros for fragments, lookup/export table, id table, and xattr id table.
- Current structures: `squashfs_super_block`, inode variants, directory entries, fragment entries, xattr entries, and xattr table.

Important behavior:
- v4 inode structures separate “short” and “long” forms; long forms carry fields such as xattr id, sparse count, larger size, or nlink.
- Fragment, id, lookup, and xattr tables use metadata-block indexed tables whose byte counts are calculated here.
- Compression ids map on-disk numeric values to compressor implementations: gzip/zlib, LZMA, LZO, XZ, LZ4, ZSTD.

Corruption-sensitive details:
- Many readers use these macros for allocation sizes. Overflow assumptions matter when converting counts to bytes.
- `SQUASHFS_NAME_LEN` is 256, and code treats names with size >= this as corrupted.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_swap.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_swap.h

This header provides endian conversion macros for Squashfs 4.0 disk structures. It is designed so little-endian hosts mostly copy or no-op, while big-endian hosts use byte-swap helpers from `swap.c`.

Key contents:
- Big-endian declarations for `swap_le16/32/64`, bulk swap helpers, and in-place swap helpers.
- `_SQUASHFS_SWAP_*` macros for superblock, directory indexes, inode variants, directory entries, fragment entries, and xattr structures.
- Public copy-swap macros such as `SQUASHFS_SWAP_SUPER_BLOCK`.
- Public in-place macros such as `SQUASHFS_INSWAP_SUPER_BLOCK`.
- Little-endian definitions that map copy operations to `memcpy` and in-place operations to no-ops.

Important behavior:
- Signed directory entry inode deltas are handled with `SWAP_LES`/`INSWAP_LES` to preserve sign.
- v4 `unsquash-4.c` reads disk data into native structs, then calls `SQUASHFS_INSWAP_*`; this header determines whether anything changes.
- Bulk table swaps cover fragment indexes, lookup blocks, id blocks, shorts, ints, and long longs.

Corruption-sensitive details:
- The macro field lists must match `squashfs_fs.h` exactly.
- The little-endian path intentionally does not validate values; callers perform sanity checks after in-place conversion.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_swap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/swap.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/swap.c

This source implements the byte-swap functions declared by `squashfs_swap.h` for big-endian builds. On little-endian builds, the file compiles to no operational code because all definitions are inside `#if __BYTE_ORDER == __BIG_ENDIAN`.

Key functions:
- `swap_le16`, `swap_le32`, `swap_le64`: copy bytes from source to destination in reverse order.
- `inswap_le16`, `inswap_le32`, `inswap_le64`: return swapped scalar values.
- Macro-generated `swap_le{16,32,64}_num`: copy-swap arrays.
- Macro-generated `inswap_le{16,32,64}_num`: in-place swap arrays.

Important behavior:
- The code operates on `void *` byte pointers for copy-swap paths, so callers can pass field addresses from packed on-disk structures.
- `inswap_le64` casts input to `unsigned long long` before shifting, avoiding signed right-shift issues.

Corruption-sensitive details:
- No bounds checking occurs here; array counts must already be validated by callers.
- These helpers are only v4 endian helpers. Older v1/v2/v3 bitfield swapping is implemented by macros in `squashfs_compat.h`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.c

This file parses and applies chmod-style mode specifications used by mksquashfs/tar processing options. It supports both octal modes and symbolic mode clauses.

Key functions:
- `parse_octal_mode_args`: accepts a single octal argument in range `0000..07777`.
- `parse_sym_mode_arg`: parses `[ugoa]*[[+-=]PERMS]+`, where `PERMS` is `[rwxXst]+` or one of `u/g/o`.
- `parse_mode_args`: dispatches octal parsing first, then symbolic parsing.
- `parse_mode`: splits a comma-separated mode string into arguments.
- `mode_execute`: applies the linked list of parsed `mode_data` operations to a `st_mode`.

Important behavior:
- Missing ownership specifier defaults to `a` with mask `0777`.
- `X` adds execute bits only for directories or files that already have at least one execute bit.
- Copy permissions such as `g=u` are encoded as negative `mode` values and expanded during execution.
- Octal mode preserves file type bits by applying `(st_mode & S_IFMT) | mode`.

Corruption/edge details:
- Syntax errors are reported through the `SYNTAX_ERR` macro with positional context when a source action string is supplied.
- `parse_mode` allocates duplicated argument strings but only frees the argv vector, not each duplicated string in this file.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.h

This header declares the symbolic/octal mode parser interface and the `mode_data` linked-list representation used by `symbolic_mode.c`.

Key contents:
- `SYNTAX_ERR` macro for formatted parse errors, optionally including the original action string and parse position.
- Operation constants: `SYMBOLIC_MODE_SET`, `SYMBOLIC_MODE_ADD`, `SYMBOLIC_MODE_REM`, `SYMBOLIC_MODE_OCT`.
- `struct mode_data`: linked list node with operation, mode bits, mask, and `X` flag.
- Extern declarations for parsing and execution functions.

Important behavior:
- `SYNTAX_ERR` uses allocation helpers from `alloc.h` and writes into `char **error`.
- The parser can be reused by command-line argument parsers that pass `(source, cur_ptr, args, argv, data, error)` and by direct `parse_mode`.

Dependency notes:
- Consumers must include or have available system mode bits such as `S_IFMT` where `mode_execute` is used.
- Ownership of allocated `mode_data` lists is not handled here; callers need to free when appropriate.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/symbolic_mode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar.c

This file implements `sqfstar` tar ingestion: it reads tar headers and file data from stdin, handles tar/PAX/GNU extensions, queues file data for compression, and builds the Squashfs directory tree from tar entries.

Key phases:
- Header parsing in `read_tar_header`.
- Data buffering in `read_tar_data`.
- Reader loop in `read_tar_file`.
- Tree construction and final directory scan in `process_tar_file`.

Tar format handling:
- Supports V7/ustar/GNU-style header fields, octal and base-256 numeric encodings, signed mtimes, long names/links, global and per-file PAX headers.
- Recognizes regular files, directories, symlinks, hardlinks, char/block devices, FIFOs, GNU sparse files, and PAX sparse variants.
- Handles `LIBARCHIVE.xattr.*` and `SCHILY.xattr.*` through `read_tar_xattr` when xattr support is enabled.
- Skips leading `/`, `./`, and `../` path components and rejects path components `.` or `..` during tree insertion.

Sparse file handling:
- GNU old sparse headers are parsed by `read_sparse_headers`.
- PAX sparse 1.0 maps are parsed by `read_sparse_map`.
- `check_sparse_map` validates that data extents plus holes match the logical file size.
- `read_sparse_block` synthesizes zero-filled holes while reading real data from stdin.

Tree behavior:
- `add_tarfile` creates/intersects directory entries, rejects conflicting file/directory definitions, and optionally copies hardlink targets when `no_hardlinks` is set.
- `lookup_pathname` resolves hardlink targets already seen in the tar stream.
- `fixup_tree` creates default inode metadata for implicit directories and empty subdirectory structures for explicit empty directories.

Important globals/options:
- `ignore_zeros`, `default_uid/gid/mode`, `numeric_owner`, fragment flags, root/global override options, queues, and progress state.
- `sequence` orders metadata/data buffers through queues.

Corruption-sensitive details:
- Header checksum accepts both unsigned and historical signed byte sums.
- Unknown tar types are ignored after skipping their data.
- Truncated reads call `BAD_ERROR` or return `TAR_ERROR`.
- Negative timestamps are rounded to epoch in `new_inode` because Squashfs cannot store pre-1970 times.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar.h

This header defines tar header structures, GNU sparse header structures, tar-entry state, tar type constants, and the public tar processing interface.

Key structures:
- `struct tar_header`: 512-byte tar header overlay with raw signed/unsigned views and named fields.
- `struct sparse_entry`, `short_sparse_header`, `long_sparse_header`: GNU sparse metadata formats.
- `struct file_map`: sparse extent pair.
- `struct tar_file`: parsed tar entry with stat data, xattrs, sparse map, path/link/user/group strings, and PAX override flags.

Key constants:
- Tar type flags: regular, hardlink, symlink, char, block, directory, FIFO, global/per-file PAX.
- GNU extension types: long name, long link, sparse.
- Magic strings for V7/GNU/ustar.
- Status codes: `TAR_OK`, `TAR_EOF`, `TAR_ERROR`, `TAR_IGNORED`.
- Xattr encodings: base64 and binary.

Public interface:
- `read_tar_file()`: producer that reads tar input and queues metadata/data buffers.
- `process_tar_file(int progress)`: consumer/tree builder returning the root squashfs inode.
- Extern option globals for default uid/gid/mode and numeric owner handling.
- Xattr hooks compile to real functions under `XATTR_SUPPORT`, otherwise no-op macros.

Important detail:
- `S_IFHRD` is encoded as `S_IFMT`, creating a synthetic mode class for tar hardlink entries before they are resolved to real inode references.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar_xattr.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar_xattr.c

This file imports extended attributes from tar PAX headers into Squashfs xattr lists.

Key functions:
- `read_tar_xattr`: adds one tar xattr to a `tar_file`.
- `read_xattrs_from_tarfile`: returns xattr list/count for an inode backed by a tar entry.
- `free_tar_xattrs`: frees xattr names and the list array.

Important behavior:
- Duplicate xattr names are ignored. This avoids double definitions when archives contain both libarchive and SCHILY encodings for the same xattr.
- Exclude regex is applied first; include regex is applied second.
- `LIBARCHIVE.xattr.*` values are base64-decoded; `SCHILY.xattr.*` values are treated as binary.
- `xattr_get_prefix` maps full names into Squashfs xattr prefix types and fills xattr metadata.

Corruption/edge details:
- Invalid base64 values are logged and ignored.
- Unknown xattr prefixes are logged and ignored, with decoded/copied value storage freed.
- `free_tar_xattrs` frees `full_name` fields and the list container but not `value` fields here, implying value ownership is transferred or handled elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/tar_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/thread.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/thread.c

This file tracks active block and fragment deflator threads and enforces an overcommit limit for fragment work.

Key globals:
- `thread_mutex`: exported mutex protecting thread accounting.
- `idle`: condition variable signaled when a thread becomes idle.
- Static `threads` array, current index, active fragment/block counters, waiter count, and overcommit count.

Key functions:
- `set_overcommit`: computes extra allowed active threads from processor count and percent.
- `get_thread_id`: lazily allocates `processors * 2` thread records, assigns type/state, and increments active counters.
- `set_thread_idle`: decrements active counters, marks idle, and signals a waiter.
- `wait_thread_idle`: throttles fragment threads while total active threads exceeds `processors + overcommit`.
- `dump_threads`: prints active fragment/block thread ids.

Important behavior:
- Block threads are reactivated directly if idle.
- Fragment threads may sleep on `idle` while over the active-thread budget.
- The code assumes callers hold the relevant queue mutex when calling `wait_thread_idle`; comments state it is called with the thread mutex held, but the function waits on the passed queue mutex.

Concurrency-sensitive details:
- `pthread_cleanup_push/pop` protects `get_thread_id` and `dump_threads` mutex unlocks on cancellation.
- The fixed allocation size assumes exactly two thread classes with up to `processors` threads each.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/thread.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/thread.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/thread.h

This header exposes thread accounting types and functions used by compression/reader code.

Key contents:
- `struct thread` with `type` and `state`.
- Thread type constants: `THREAD_BLOCK`, `THREAD_FRAGMENT`.
- State constants: `THREAD_ACTIVE`, `THREAD_IDLE`.
- Overcommit defaults/stringification macros.
- Extern `pthread_mutex_t thread_mutex`.
- Public functions for id allocation, idle transitions, waiting, dumping state, and configuring overcommit.

Important behavior:
- Callers coordinate via the exported `thread_mutex`.
- The overcommit default is `0%`, meaning fragment throttling defaults to at most the processor count unless configured otherwise.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/thread.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/time_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/time_compat.h

This small compatibility header abstracts timestamp setting for extracted unsquashfs output, especially symlinks.

Key function:
- `set_timestamp(char *pathname, struct inode *i)`: inline wrapper that sets both access and modification times to `i->time`.

Platform behavior:
- On OpenBSD, uses `utimensat(AT_FDCWD, pathname, times, AT_SYMLINK_NOFOLLOW)` with `struct timespec`.
- On other platforms, uses `lutimes(pathname, times)` with `struct timeval`.

Important detail:
- Both implementations avoid following symlinks, preserving symlink timestamps where supported.
- The header assumes `struct inode` has a `time` field and that the including file has suitable system headers/constants available.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/time_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.c

This file parses user/group arguments into numeric 32-bit ids for command-line options.

Key functions:
- `get_uid_from_arg(char *arg, unsigned int *uid)`.
- `get_gid_from_arg(char *arg, unsigned int *gid)`.

Behavior:
- First attempts decimal numeric parsing via `strtoll`.
- If the whole argument is numeric, validates range `0..2^32-1`.
- If nonnumeric, resolves username with `getpwnam` or group name with `getgrnam`.
- Retries name lookup on `EINTR`.

Return values:
- `0`: success.
- `-1`: name lookup failed or nonnumeric name not found.
- `-2`: numeric id was outside the supported unsigned 32-bit range.

Important details:
- The numeric parser does not reset/check `errno` for `strtoll` overflow; range validation catches many, but not all, overflow-reporting subtleties.
- Returned ids are stored in `unsigned int`, matching Squashfs id-table storage expectations.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.h

This header declares the UID/GID parsing helpers.

Public interface:
- `get_uid_from_arg(char *arg, unsigned int *uid)`.
- `get_gid_from_arg(char *arg, unsigned int *gid)`.

Expected semantics:
- Numeric strings resolve directly after range checking.
- Nonnumeric strings resolve through system passwd/group databases.
- Callers should distinguish `-1` not found from `-2` out of range for diagnostics.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1.c

This file implements unsquashfs support for Squashfs 1.0 images. It maps the v1 on-disk format into the shared unsquashfs operation interface.

Key functions:
- `read_block_list`: reads 16-bit v1 block sizes and expands them into current block-size flags.
- `read_inode`: parses v1 inodes and fills a shared `struct inode`.
- `squashfs_opendir`: reads v1/v2-style directory headers and entries.
- `read_filesystem_tables`: validates and reads v1 uid/gid tables.
- `read_super_1`: recognizes v1.0 superblocks and normalizes fields into `sBlk`.
- `squashfs_stat`: prints v1 filesystem details.

Version-specific behavior:
- v1 encodes uid through inode type grouping plus 4-bit uid index.
- gid value `15` means “same as uid”.
- No fragment table is used; `fragment_table_start` is set invalid.
- Symlinks/devices/FIFOs/sockets use filesystem creation time unless overridden.
- Compression is always gzip.

Corruption checks:
- Bounds-check uid/gid indexes.
- Rejects too many v1 uids/gids.
- Validates table ordering: inode table before directory table before uid/gid tables.
- Directory reading validates filename length, name characters, duplicate names, and sorts before duplicate checks.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-12.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-12.c

This helper file provides shared functionality for the Squashfs 1.x and 2.x readers.

Key content:
- Includes `merge_sort.h`.
- Instantiates `SORT(sort_directory, dir_ent, name, next)`.

Behavior:
- Generates a linked-list merge sort function named `sort_directory`.
- Sorts `struct dir_ent` nodes by their `name` field using the `next` pointer.
- Used by v1 and selected v2 directory handling before calling `check_directory`.

Importance:
- Older filesystem versions may require sorting before duplicate-name validation.
- Keeping this helper separate avoids duplicating the macro instantiation in both legacy readers.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-12.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-123.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-123.c

This helper file provides shared uid/gid table reading for Squashfs 1.x, 2.x, and 3.x compatibility readers.

Key function:
- `read_ids(int ids, long long start, long long end, unsigned int **id_table)`.

Behavior:
- Computes table byte length as `ids * sizeof(unsigned int)`.
- Verifies the computed length equals `end - start`.
- Allocates the output id table.
- Reads raw table bytes from disk.
- Uses `SQUASHFS_SWAP_INTS_3` when the filesystem endian differs from host endian.

Important details:
- The function is for old flat id tables, not the v4 metadata-block indexed id table.
- It assumes callers already validated the number of ids for the relevant version.
- Failure returns `FALSE` after logging an error; partial allocations may remain in some failure paths.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-123.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1234.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1234.c

This helper file provides shared directory validation and cleanup for all unsquashfs format readers.

Key functions:
- `check_name`: validates one directory entry name.
- `squashfs_closedir`: frees a `struct dir` and its linked entries.
- `check_directory`: verifies directory entries are strictly sorted and have no duplicates.

Name validation rules:
- Rejects `.`, `./`, `..`, and `../`.
- Rejects any slash in the entry name.
- Rejects names shorter than the expected size.

Directory validation:
- Requires strictly increasing `strcmp` order for adjacent names.
- Because duplicates would sort adjacent, `strcmp >= 0` rejects both duplicates and unsorted entries.

Importance:
- This file is part of corruption hardening. It prevents malicious directory entries from escaping extraction paths or hiding duplicates through ordering tricks.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1234.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-2.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-2.c

This file implements unsquashfs support for Squashfs 2.0 and 2.1 images.

Key functions:
- `read_block_list`: reads 32-bit block-size list entries.
- `read_fragment_table`: reads v2 fragment index/table data.
- `read_fragment`: returns fragment start and size.
- `read_inode`: parses v2 inode variants.
- `squashfs_opendir`: reads v2 directories.
- `read_filesystem_tables`: validates uid/gid, fragment, directory, and inode table layout.
- `read_super_2`: recognizes v2 superblocks and normalizes `sBlk`.
- `squashfs_stat`: prints v2 feature summary.

Version-specific behavior:
- Supports fragments, unlike v1.
- v2.0 may need directory sorting; `needs_sorting` is set for minor 0.
- gid value `SQUASHFS_GUIDS` means “same as uid”.
- Compression is always gzip.
- xattrs are absent and marked invalid.

Corruption checks:
- Fragment table index byte count must match table boundaries.
- Fragment count cannot exceed inode count.
- Directory count, filename length, and names are validated.
- Sortedness/duplicates are checked, with different diagnostics depending on whether sorting was expected.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-3.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-3.c

This file implements unsquashfs support for Squashfs 3.0 and 3.1 images.

Key functions:
- `salloc_index_table`: scratch allocation for swapped index tables.
- `read_block_list`: reads v3 block lists.
- `read_fragment_table` and `read_fragment`: handle v3 64-bit fragment indexes and entries.
- `read_inode`: parses v3 inode variants, including large regular files.
- `squashfs_opendir`: reads v3 directories.
- `parse_exports_table`: validates and steps over the export lookup table.
- `read_filesystem_tables`: validates old uid/gid, export, fragment, directory, and inode tables.
- `read_super_3`: reads, endian-swaps if needed, recognizes v3 superblocks, and normalizes `sBlk`.
- `squashfs_stat`: prints v3 metadata.

Version-specific behavior:
- v3 adds real inode numbers and optional export lookup table support.
- Directory data size treats `3` as empty and subtracts `3` during parsing.
- Large regular files support 64-bit sizes.
- Regular files mark `i.sparse = 1`.
- Compression is always gzip.

Corruption checks:
- Rejects inode type outside `1..9`, inode number zero, and inode number greater than superblock inode count.
- Validates negative large file sizes.
- Validates table ordering and fragment/export index lengths.
- Checks directory sortedness and duplicate names.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-34.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-34.c

This helper file provides utilities shared by Squashfs 3.x and 4.x readers.

Key functions:
- `alloc_index_table`: reusable static allocation for 64-bit filesystem index tables.
- `inumber_lookup`: tracks visited directory inode numbers with an on-demand bit table.
- `free_inumber_table`: frees the visited-directory table.
- `lookup`: finds a previously extracted non-directory inode pathname by inode number.
- `insert_lookup`: records a pathname for an inode number.
- `free_lookup_table`: frees the hardlink lookup table, optionally freeing stored pathnames.

Important behavior:
- The inode-number table prevents invalid multiple directory links and directory loops during extraction.
- The hardlink lookup table lets unsquashfs create hardlinks for repeated non-directory inode numbers.
- Both structures allocate index pages lazily so partial filesystem traversal does not allocate for every inode.

Dependency notes:
- Index/offset/bit sizing macros such as `INUMBER_INDEXES` and `LOOKUP_INDEXES` come from `unsquashfs.h`.
- `alloc_index_table(0)` frees its static buffer and is used by readers after table parsing.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-34.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-4.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-4.c

This file implements unsquashfs support for current Squashfs 4.0 images.

Key functions:
- `read_block_list`: reads and endian-converts file block sizes.
- `read_fragment_table` and `read_fragment`: read and serve fragment entries.
- `read_inode`: parses all v4 inode variants, including long inode forms with xattrs.
- `squashfs_opendir`: reads v4 directories.
- `read_id_table`: reads metadata-block indexed id table.
- `parse_exports_table`: validates export lookup table index.
- `read_filesystem_tables`: validates and reads xattrs, ids, exports, fragments, and table boundaries.
- `read_super_4`: recognizes normal and streamed v4 superblocks, handles endian conversion, and selects compressor by id.
- `read_xattr_ids` and `squashfs_stat`: report xattr and filesystem stats.

Version-specific behavior:
- Supports xattrs, id table compression, compressor options, sparse long regular files, and long inode types for xattr-bearing objects.
- Streamed Squashfs magic causes the reader to seek to the final superblock.
- Uses `SQUASHFS_INSWAP_*` macros, making endian handling host-dependent.
- `no_xattrs` can suppress xattr use by invalidating `xattr_id_table_start`.

Corruption checks:
- Validates uid/gid indexes against `no_ids`, inode type `1..14`, inode numbers, symlink size, fragment indexes, id count, table ordering, and negative file sizes.
- Ensures id count is nonzero and not more than twice inode count.
- Fragment count cannot exceed inode count.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-4.c -->