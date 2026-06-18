# Group Research: group_1164_mtd_utils_sources_local_fs_mtd_utils_lib_libfec_c_sources_local_fs__2d12e932a353

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/lib/libfec.c -->
# File Research: sources/local-fs/mtd-utils/lib/libfec.c

## Purpose
Implements a standalone forward-error-correction library based on systematic Vandermonde matrices over Galois fields. It is used by the multicast image tooling API declared in `mcast_image.h`.

## Main Entry Points
- `fec_new()` initializes global GF tables on first use, validates `k`/`n`, builds the systematic encoding matrix, and returns a `struct fec_parms`.
- `fec_free()` validates the descriptor magic and frees the encoding matrix.
- `fec_encode()` encodes from an array of source packet pointers.
- `fec_encode_linear()` encodes from one contiguous source buffer.
- `fec_decode()` reconstructs missing original packets in place from any `k` unique packet/index pairs.

## Internal Mechanics
The file generates GF exponent, log, inverse, and optional multiplication tables for `GF_BITS` elements, defaulting to GF(256). Encoding starts from a Vandermonde matrix, inverts the top `k x k` portion, multiplies the lower rows by that inverse, and installs an identity matrix in the upper rows so original packets pass through unchanged.

Decoding first `shuffle()`s packets that already belong in original positions, builds a decode matrix from original rows or encoding rows, inverts that matrix with Gauss-Jordan elimination, then rebuilds missing source packets with GF multiply-add loops.

## Dependencies
Uses only libc headers and the matching public prototypes in `mcast_image.h`. It has optional `TEST`/`DEBUG` timing and consistency code.

## Risks and Notes
Allocation failures abort via `exit(1)` in `my_malloc()`, so callers cannot recover from memory pressure. The global GF tables and `fec_initialized` are lazily initialized without synchronization. The `GF_BITS` validation preprocessor condition uses `&&` where a range check would normally use `||`, so invalid values are not rejected by that directive.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/lib/libfec.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd.c -->
# File Research: sources/local-fs/mtd-utils/lib/libmtd.c

## Purpose
Provides the main libmtd implementation for discovering MTD devices, reading sysfs attributes, mapping device nodes to MTD numbers, and performing erase, lock, bad-block, read, write, OOB, image-write, and probe operations.

## Main Entry Points
- `libmtd_open()` builds sysfs path patterns under `/sys/class/mtd` and detects whether the kernel has usable MTD sysfs support.
- `libmtd_close()` releases path templates and descriptor state.
- `mtd_dev_present()`, `mtd_get_info()`, `mtd_get_dev_info1()`, and `mtd_get_dev_info()` expose inventory and per-device metadata.
- `mtd_lock()`, `mtd_unlock()`, `mtd_erase()`, `mtd_regioninfo()`, and `mtd_is_locked()` wrap MTD ioctls.
- `mtd_torture()`, `mtd_is_bad()`, and `mtd_mark_bad()` exercise or manage eraseblocks and NAND bad-block state.
- `mtd_read()`, `mtd_write()`, `mtd_read_oob()`, `mtd_write_oob()`, `mtd_write_img()`, and `mtd_probe_node()` implement data/OOB I/O and node validation.

## Control Flow and State
Sysfs-backed discovery reads per-device files such as `dev`, `name`, `type`, `erasesize`, `size`, `writesize`, `subpagesize`, `oobsize`, `numeraseregions`, and `flags`. If sysfs is not available, public inventory calls delegate to `libmtd_legacy.c`.

The descriptor caches whether 64-bit offset ioctls are supported. Erase and OOB helpers first try `MEMERASE64`, `MEMREADOOB64`, or `MEMWRITEOOB64` when support is unknown or known-present, then fall back to legacy 32-bit ioctls when the kernel reports unsupported operations.

## Dependencies
Depends on Linux MTD UAPI (`mtd/mtd-user.h`), `libmtd.h`, `common.h` logging/allocation helpers, sysfs, character-device metadata, and standard POSIX file APIs.

## Risks and Notes
`mtd_torture()` sets `err = 0` on success but returns `-1` unconditionally at the `out:` label, which makes a successful torture test report failure. `mtd_read()` loops until the requested length is read but passes the original buffer pointer and original length to every `read()`, so short reads can overwrite earlier data and over-count progress. The OOB fallback path logs some 64-bit ioctl failures but still proceeds to the legacy ioctl unless the fallback itself rejects the request.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd_int.h -->
# File Research: sources/local-fs/mtd-utils/lib/libmtd_int.h

## Purpose
Defines libmtd-private constants, sysfs filename fragments, 64-bit ioctl support states, the internal `struct libmtd`, and prototypes for legacy fallback functions.

## Main Definitions
- Sysfs constants cover `/sys/class/mtd/mtd%d` and attribute files used by `libmtd.c`.
- `OFFS64_IOCTLS_UNKNOWN`, `OFFS64_IOCTLS_NOT_SUPPORTED`, and `OFFS64_IOCTLS_SUPPORTED` describe lazy probing state for 64-bit erase/OOB ioctls.
- `struct libmtd` stores path templates for sysfs reads and bitfields for sysfs and 64-bit ioctl support.

## Dependencies
Includes `libmtd.h` indirectly through users of the prototypes and provides C++ linkage guards for internal functions.

## Risks and Notes
The header documents why 64-bit ioctl support is discovered later rather than during `libmtd_open()`: probing requires a real MTD device file descriptor.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd_int.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd_legacy.c -->
# File Research: sources/local-fs/mtd-utils/lib/libmtd_legacy.c

## Purpose
Implements libmtd compatibility for kernels without the modern MTD sysfs interface, using `/proc/mtd`, `/dev/mtd%d`, and older MTD ioctls.

## Main Entry Points
- `legacy_libmtd_open()` checks whether `/proc/mtd` exists.
- `legacy_dev_present()` scans `/proc/mtd` for an MTD number.
- `legacy_mtd_get_info()` counts devices and determines lowest/highest MTD numbers.
- `legacy_get_dev_info()` validates a character node, calls `MEMGETINFO`, probes bad-block support, fills `struct mtd_dev_info`, and obtains the name from `/proc/mtd`.
- `legacy_get_dev_info1()` formats `/dev/mtd%d` and delegates to `legacy_get_dev_info()`.

## Control Flow
`proc_parse_start()` reads `/proc/mtd` into a bounded buffer and verifies the header. `proc_parse_next()` walks one line at a time, extracting the device number, size, erase size, and quoted device name.

## Dependencies
Uses Linux MTD legacy ioctls, `common.h` helpers, POSIX file/stat APIs, and the internal libmtd declarations.

## Risks and Notes
The fallback cannot discover NAND subpage size, so it sets `subpage_size` equal to `min_io_size`. Some early returns from `/proc/mtd` scanning paths do not free the parser buffer before returning, causing small process-lifetime leaks in these short-lived utility contexts.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/lib/libmtd_legacy.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/load_nandsim.sh -->
# File Research: sources/local-fs/mtd-utils/load_nandsim.sh

## Purpose
Loads the Linux `nandsim` module with ID bytes selected to emulate a supported NAND flash size, eraseblock size, and page size combination.

## Behavior
The script rejects execution if `/proc/mtd` already contains a NAND simulator. It accepts size in MiB plus optional eraseblock size in KiB and page size, defaulting to `16` KiB eraseblocks and `512` byte pages.

For 512-byte pages, it only permits 16 KiB eraseblocks and maps sizes 16, 32, 64, 128, and 256 MiB to two-byte NAND IDs. For 2048-byte pages, it maps eraseblock sizes 64, 128, 256, or 512 KiB plus sizes 64 through 1024 MiB to four ID bytes.

## Dependencies
Requires `/proc/mtd`, `grep`, and root/module privileges for `modprobe nandsim`.

## Risks and Notes
The script runs with `set -euf`, but it assigns `eb_size="$2"` and `page_size="$3"` before checking whether optional arguments exist. With only the mandatory size argument, `set -u` can abort before defaults are applied.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/load_nandsim.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/make_a_release.sh -->
# File Research: sources/local-fs/mtd-utils/make_a_release.sh

## Purpose
Automates the mtd-utils release preparation flow: version validation, Makefile version update, signed tag creation, tarball generation, detached GPG signature, and release announcement template.

## Control Flow
The script requires `<new_ver> <outdir>`, validates `X.Y.Z` version syntax, verifies the Makefile contains a version line, rejects dirty git state and pre-existing tags, edits `VERSION = ...`, commits the change, creates a signed `vX.Y.Z` tag, archives it as `mtd-utils-X.Y.Z.tar.bz2`, signs the tarball, and prints upload/send-email instructions.

## Dependencies
Requires a clean git checkout, `sed`, `git`, `bzip2`, `gpg`, and release infrastructure access for the printed `scp` target.

## Risks and Notes
The script intentionally mutates git history by committing and tagging. It assumes the release branch is `master` in the printed push command. The error message for bad argument count contains a typo but does not affect behavior.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/make_a_release.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mcast_image.h -->
# File Research: sources/local-fs/mtd-utils/mcast_image.h

## Purpose
Defines multicast image packet layout and declares the FEC API used for packet recovery.

## Main Data
- `PKT_SIZE` is `2820` bytes of payload per image packet.
- `struct image_pkt_hdr` carries resend flag, total CRC, image block count/size, block CRC/number, packet sequence, packet number/count, current length, and packet CRC.
- `struct image_pkt` combines the header and payload buffer.
- `struct fec_parms` is opaque to callers.

## Dependencies
Uses fixed-width integer types from `<stdint.h>` and corresponds to the implementation in `lib/libfec.c`.

## Risks and Notes
The packet structures are plain C layout with no explicit packing or byte-order conversion in this header, so protocol users must agree on ABI layout and serialization conventions elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mcast_image.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.jffs2.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.jffs2.c

## Purpose
Implements the `mkfs.jffs2` utility, building a JFFS2 image from a host directory tree with optional device-table entries, compression settings, xattrs, endian selection, cleanmarkers, padding, ownership/permission squashing, fake timestamps, and incremental image parsing.

## Main Data Model
`struct filesystem_entry` represents the target filesystem tree. It stores target and host paths, stat metadata, symlink target, parent/child/sibling links, JFFS2 inode number, and a red-black node for hardlink tracking.

## Build Flow
`main()` parses options, initializes compressors, chooses page and eraseblock sizes, opens output and optional incremental input, `chdir()`s into the root, optionally parses an existing image to continue inode numbering, recursively scans the host tree, applies a device table, and calls `create_target_filesystem()`.

Host scanning is handled by `recursive_add_host_directory()` and `add_host_filesystem_entry()`. Device table parsing can create or override files, directories, FIFOs, and character/block devices. `find_hardlink()` records host `(st_dev, st_ino)` pairs to emit later hardlinks as additional dirents to an existing JFFS2 inode.

## Image Serialization
The writer emits raw JFFS2 dirent and inode nodes with CRCs and target-endian conversions. Regular files are split by page and eraseblock space, compressed through the JFFS2 compressor framework, and padded to word alignment. Directories, FIFOs, sockets, symlinks, and special files have specialized writers. `pad_block_if_less_than()` handles cleanmarker insertion and eraseblock boundary padding.

When xattr support is enabled, xattrs are read from the host with `llistxattr()`/`lgetxattr()`, ACLs are converted to JFFS2 ACL format, duplicate xattr bodies are interned, and xref nodes connect inodes to xattr IDs.

## Dependencies
Uses JFFS2 UAPI structures, `crc32`, the local compressor framework, local red-black tree helpers, POSIX filesystem APIs, and optional xattr/ACL headers.

## Risks and Notes
This is a stateful single-process image builder with global output offset, inode counter, compression state, and endian mode. Incremental parsing only scans node headers to advance inode numbering; it does not validate or rewrite the old image. The `cleanup()` routine clears `e->next` before advancing, so it can stop after the first child and leak the rest of a directory tree.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.jffs2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/compr.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/compr.c

## Purpose
Implements mkfs.ubifs data compression using LZO, zlib/deflate, no-compression fallback, and an optional mode that favors LZO unless zlib is sufficiently better.

## Main Entry Points
- `compress_data()` selects and runs a compressor, then falls back to uncompressed data for short input, compressor failure, or non-beneficial compression.
- `init_compression()` allocates LZO work memory and a temporary zlib output buffer.
- `destroy_compression()` frees buffers and reports accumulated compression errors.

## Compression Logic
`zlib_deflate()` uses raw deflate settings chosen to match the kernel crypto API. `lzo_compress()` uses `lzo1x_999_compress()`. `favor_lzo_compress()` runs both compressors, compares output sizes, and chooses LZO if it is no larger or if zlib's win is within `info_.favor_percent`; otherwise it copies the zlib result into the caller's output buffer.

## Dependencies
Depends on zlib, LZO, Linux types, `compr.h`, and `mkfs.ubifs.h` global configuration (`info_`, `UBIFS_MIN_COMPR_LEN`, `UBIFS_BLOCK_SIZE`, `favor_lzo`, `favor_percent`).

## Risks and Notes
The implementation is global-state based: buffers, error count, and `info_` are not instance-local. `compress_data()` returns the selected mkfs compression enum, not a conventional negative error code.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/compr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/compr.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/compr.h

## Purpose
Declares the mkfs.ubifs compression interface and compression type identifiers.

## Main Definitions
- `WORST_COMPR_FACTOR` is the assumed maximum expansion factor for temporary compressor output buffers.
- `enum compression_type` defines `MKFS_UBIFS_COMPR_NONE`, `MKFS_UBIFS_COMPR_LZO`, and `MKFS_UBIFS_COMPR_ZLIB`.
- Declares `compress_data()`, `init_compression()`, and `destroy_compression()`.

## Dependencies
Requires standard `size_t` visibility from includers and is implemented by `compr.c`.

## Risks and Notes
The enum is mkfs-specific and should be mapped carefully to on-media UBIFS compression constants by callers.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/compr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.c

## Purpose
Provides a table-driven CRC-16 implementation used by UBIFS LPT node packing.

## Main Data and Entry Point
- `crc16_table[256]` is the lookup table for the standard CRC-16 polynomial `0x8005`.
- `crc16()` updates a supplied CRC over a byte buffer using `crc16_byte()`.

## Dependencies
Includes `crc16.h`; the code notes that it was taken from the Linux kernel under GPLv2.

## Risks and Notes
The function is incremental: callers supply the initial or previous CRC value. LPT code uses an initial value of `-1`, relying on truncation to `uint16_t`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.h

## Purpose
Declares CRC-16 table/function symbols and provides the inline one-byte update helper.

## Main Definitions
- `extern uint16_t const crc16_table[256]`.
- `extern uint16_t crc16(uint16_t crc, const uint8_t *buffer, size_t len)`.
- `crc16_byte()` performs one lookup-table update.

## Dependencies
Includes `<stdlib.h>` for `size_t` and `<stdint.h>` for fixed-width integer types.

## Risks and Notes
The implementation assumes callers use the same CRC initialization convention as the UBIFS/JFFS code paths that consume it.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/defs.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/defs.h

## Purpose
Supplies user-space glue definitions borrowed from kernel UBIFS expectations: endian conversions, branch prediction/assertion stubs, `struct qstr`, `fls()`, and `do_div()`.

## Main Definitions
- `t16()`, `t32()`, and `t64()` conditionally byte-swap based on host endianness.
- `cpu_to_le*()` and `le*_to_cpu()` wrap little-endian conversions for UBIFS on-media structures.
- `unlikely()` and `ubifs_assert()` are no-op user-space stand-ins.
- `struct qstr` stores a name pointer and length.
- `fls()` returns the position of the most significant set bit in a 32-bit int.
- `do_div()` divides an integer-like lvalue and returns the remainder.

## Dependencies
Assumes includers provide byte-swap macros, endian macros, integer types, and `INT_MAX`.

## Risks and Notes
`do_div()` casts through `unsigned long`, so it is only a faithful 64-bit helper on platforms where `unsigned long` is wide enough for the values used by mkfs.ubifs. The file enforces 32-bit `int` and 64-bit `long long` at compile time.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/devtable.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/devtable.c

## Purpose
Parses mkfs.ubifs device table files and stores requested filesystem entries or attribute overrides for later use while walking the host root.

## Main Entry Points
- `parse_devtable()` reads and validates a device table file, creating the top-level path hash table.
- `devtbl_find_path()` and `devtbl_find_name()` look up pending table entries by parent path and basename.
- `override_attributes()` applies UID, GID, and mode overrides to an existing host entry and removes the consumed table entry.
- `first_name_htbl_element()` and `next_name_htbl_element()` iterate remaining entries under a path so mkfs.ubifs can synthesize nodes not present on the host.
- `free_devtable_info()` destroys all nested hash tables.

## Data Model
`path_htbl` maps a directory path such as `/dev` to a `struct path_htbl_element`. Each path element owns a second hashtable of `struct name_htbl_element` objects keyed by basename. Counted device-table entries expand names like `tty0`, `tty1`, etc. with calculated device minor numbers.

## Parsing Rules
Entries must use absolute, normalized paths without trailing slash, `//`, `.`, or `..`. Supported types are directory, regular file, FIFO, character device, and block device. Existing host special files cannot also be created from the table; regular files/directories must match type if overridden.

## Dependencies
Uses mkfs.ubifs types from `mkfs.ubifs.h` and the bundled Christopher Clark hashtable implementation.

## Risks and Notes
The parser stores allocated strings as hashtable keys and also as element names, relying on the hashtable's key-freeing behavior for cleanup. Several duplicate/error paths return immediately after allocation or lookup failures and can leak small intermediate allocations before process exit.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/devtable.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.c

## Purpose
Implements a generic separate-chaining hashtable with prime table sizes, load-factor expansion, caller-provided hash/equality functions, and ownership of key memory.

## Main Entry Points
- `create_hashtable()` chooses the first prime larger than the requested minimum, allocates the bucket table, and records hash/equality callbacks.
- `hash()` mixes the caller's hash output to reduce sensitivity to poor hash functions.
- `hashtable_insert()` inserts a key/value pair and expands when load exceeds `0.65`.
- `hashtable_search()` returns the value for a matching key.
- `hashtable_remove()` removes an entry, frees its key, and returns the value.
- `hashtable_count()` and `hashtable_destroy()` expose count and teardown.

## Dependencies
Includes `common.h` for `ARRAY_SIZE`, the public/private hashtable headers, libc allocation/string headers, and `ceil()` from libm.

## Risks and Notes
The table permits duplicate keys; callers must remove first if uniqueness matters. `hashtable_destroy(..., free_values)` always frees keys and optionally frees values. The realloc fallback in `hashtable_expand()` appears to call `memset(newtable[h->tablelength], ...)` instead of taking the address of the first new bucket and sizing in bytes, which would be unsafe if that rare fallback path executes.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.h

## Purpose
Public header for the bundled generic hashtable library.

## Main API
Declares opaque `struct hashtable` plus `create_hashtable()`, `hashtable_insert()`, `hashtable_search()`, `hashtable_remove()`, `hashtable_count()`, and `hashtable_destroy()`.

## Convenience Macros
`DEFINE_HASHTABLE_INSERT`, `DEFINE_HASHTABLE_SEARCH`, and `DEFINE_HASHTABLE_REMOVE` generate typed wrappers around the void-pointer API for stronger compile-time checking in users that opt in.

## Dependencies
Implemented by `hashtable.c` and accompanied by iterator headers/source for traversal.

## Risks and Notes
The documented ownership model is important: inserted keys become owned by the table and are freed on removal/destruction, while values are only freed by `hashtable_destroy()` when requested.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.c

## Purpose
Implements external iterators for the bundled hashtable.

## Main Entry Points
- `hashtable_iterator()` allocates an iterator positioned at the first entry, or an empty iterator if the table has no entries.
- `hashtable_iterator_advance()` moves within a bucket chain or to the next non-empty bucket.
- `hashtable_iterator_remove()` removes the current entry, frees its key, advances the iterator, and returns whether iteration can continue.
- `hashtable_iterator_search()` positions an existing iterator at a key match.

## Dependencies
Uses the public, private, and iterator hashtable headers. It relies on the concrete table and entry layout from `hashtable_private.h`.

## Risks and Notes
Iterator allocation is caller-owned, but some users in this tree do not free iterator objects after traversal, causing small leaks in utility execution. Removing through the iterator does not free the value, so callers must capture and release values themselves if needed.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.h

## Purpose
Declares and partially defines the hashtable iterator API.

## Main Definitions
- Concrete `struct hashtable_itr` stores the table, current entry, parent entry, and bucket index.
- `hashtable_iterator_key()` and `hashtable_iterator_value()` inline access to the current entry.
- Declares iterator construction, advance, remove, and search functions.
- `DEFINE_HASHTABLE_ITERATOR_SEARCH` generates typed search wrappers.

## Dependencies
Includes `hashtable.h` and `hashtable_private.h` so accessors can inline against `struct entry`.

## Risks and Notes
Because the iterator structure is public in this header, callers can depend on internals that are otherwise private to the hashtable implementation.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_itr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_private.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_private.h

## Purpose
Defines the private storage layout for the bundled hashtable implementation.

## Main Definitions
- `struct entry` stores key, value, cached mixed hash, and next-chain pointer.
- `struct hashtable` stores bucket count, bucket array, entry count, load limit, prime-table index, and hash/equality callbacks.
- Declares `hash()` for internal and iterator use.
- `indexFor()` maps a hash to a bucket using modulo.
- `freekey()` currently maps to `free()`.

## Dependencies
Includes the public hashtable header and assumes libc `free()` is visible through implementation includes.

## Risks and Notes
The `freekey()` macro makes heap allocation of keys part of the table contract. Static or borrowed key strings cannot safely be inserted unless `freekey` is changed.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_private.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/key.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/key.h

## Purpose
Provides UBIFS key construction, hashing, serialization, and comparison helpers for the simple 64-bit key scheme used by mkfs.ubifs.

## Main Helpers
- `key_mask_hash()` masks directory-entry hashes and avoids reserved values for `.`, `..`, and end-of-readdir.
- `key_r5_hash()` implements the ReiserFS-derived R5 name hash.
- `key_test_hash()` creates a predictable test hash from up to four name bytes.
- `ino_key_init()`, `dent_key_init()`, and `data_key_init()` build inode, direntry, and data keys.
- `key_write()` and `key_write_idx()` serialize in-memory keys to little-endian on-media form.
- `keys_cmp()` compares two UBIFS keys lexicographically.

## Dependencies
Relies on UBIFS constants and types from `mkfs.ubifs.h`/included headers, endian helpers from `defs.h`, and `struct qstr`.

## Risks and Notes
`key_r5_hash()` accepts a length parameter but walks until NUL rather than using `len`; callers must pass NUL-terminated names for that hash mode. `key_write()` zero-fills the unused part of the maximum key length, while `key_write_idx()` writes only the active 64-bit key.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/key.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.c

## Purpose
Calculates and writes the UBIFS Logical Properties Tree (LPT) area for a newly created UBIFS image.

## Main Entry Points
- `calc_dflt_lpt_geom()` iteratively determines the default number of LPT LEBs, main-area LEBs, and whether the filesystem needs the big LPT model.
- `create_lpt()` serializes pnodes, nnodes, optional lsave, and ltab data into LPT LEBs.

## Geometry Calculation
`do_calc_lpt_geom()` derives pnode and nnode counts, tree height, bit widths for space, LPT LEB number, offset, pnode count, and main LEB number fields. It then computes packed node sizes and total LPT size, adding expected per-LEB wastage and min-I/O alignment.

`calc_dflt_lpt_geom()` starts with minimum LPT LEBs and small-LPT assumptions, switches to big LPT if needed, and repeats until the computed geometry fits within the number of reserved LPT LEBs.

## Serialization
`pack_bits()` writes variable-width fields into byte streams. `pack_pnode()`, `pack_nnode()`, `pack_ltab()`, and `pack_lsave()` encode LPT records and prepend CRC-16 checksums. `create_lpt()` lays out pnodes first, then internal nnodes bottom-up, records root/head/ltab/lsave addresses in `struct ubifs_info`, maintains LPT LEB free/dirty accounting through `set_ltab()`, aligns writes to min I/O size, fills unwritten bytes with `0xff`, and emits buffers via `write_leb()`.

## Dependencies
Depends on UBIFS constants/types from `mkfs.ubifs.h`, `crc16()`, `fls()`/`do_div()` from `defs.h`, alignment macros, and the image writer `write_leb()`.

## Risks and Notes
The packing code assumes the geometry bit widths have already been calculated consistently. `create_lpt()` allocates temporary pnode/nnode/buffer/lsave objects and returns negative errno-style failures on allocation or write errors.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.h

## Purpose
Declares the mkfs.ubifs LPT geometry and creation functions.

## Main API
- `calc_dflt_lpt_geom(struct ubifs_info *c, int *main_lebs, int *big_lpt)`.
- `create_lpt(struct ubifs_info *c)`.

## Dependencies
Requires `struct ubifs_info` to be visible from includers, normally via `mkfs.ubifs.h`.

## Risks and Notes
This header is intentionally minimal; all LPT structure layout details stay in `lpt.c` and UBIFS shared headers.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.h -->