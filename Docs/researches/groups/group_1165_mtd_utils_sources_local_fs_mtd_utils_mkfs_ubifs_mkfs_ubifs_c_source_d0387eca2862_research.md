# Group Research: group_1165_mtd_utils_sources_local_fs_mtd_utils_mkfs_ubifs_mkfs_ubifs_c_source_d0387eca2862

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/mtd-utils`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.c -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.c

## Purpose
Implements the `mkfs.ubifs` image builder. It creates a UBIFS filesystem from a host directory tree, an empty root, or directly onto an existing UBI volume.

## Main Behavior
- Parses filesystem geometry, compression, journal, LPT, orphan, key hash, device-table, UID squash, and UBI/file output options.
- Derives UBIFS geometry in `struct ubifs_info`, opens either a plain output file or a UBI volume, and optionally checks that the UBI volume is empty.
- Walks the source tree, applies device-table overrides, handles hard-linked files through an inode mapping hash table, and emits UBIFS inode, data, directory-entry, symlink, device, FIFO, and socket nodes.
- Skips all-zero file blocks as sparse holes and compresses non-zero file data through the mkfs compression layer.
- Records every emitted data/dent/inode node in an in-memory index list, sorts it by UBIFS key/name, then builds the on-flash index tree.
- Writes all UBIFS areas in dependency order: data, GC LEB, index, final LEB counts, LPT, superblock, master nodes, log, and orphan area.

## Key Entry Points
- `get_options()` initializes defaults and parses all CLI state.
- `init()` calculates LPT geometry, allocates LPT/node/block/hash/compression state, and positions the write head at the main area.
- `write_data()` recursively emits the filesystem payload.
- `write_index()` creates the UBIFS TNC index from the collected node list.
- `write_super()`, `write_master()`, `write_log()`, `write_lpt()`, and `write_orphan_area()` serialize fixed UBIFS areas.
- `mkfs()` coordinates the whole build.

## Dependencies
Uses UBIFS media definitions, local UBIFS key/LPT/compression/device-table helpers, libubi, libuuid, Linux inode flags, POSIX filesystem APIs, and mtd-utils CRC/common helpers.

## Notes
The implementation is intentionally global-state based around `info_`, output descriptors, write-head state, scratch buffers, and index/hardlink tables. `is_contained()` uses substring matching on canonical paths, so path-prefix false positives are possible. In device-table-created fake entries, `fake_st.st_uid` is assigned twice and `st_gid` is not set from the entry. `cmp_idx()` falls back to `namecmp()` for equal keys, which assumes names are non-NULL.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.h

## Purpose
Central private header for the `mkfs.ubifs` program.

## Main Contents
- Pulls in libc/POSIX, Linux filesystem, UBIFS media, libubi, CRC, key, LPT, compression, and device-table dependencies.
- Defines `PROGRAM_NAME`, debug/error helper macros, and compile-time checks that mkfs compression enums match UBIFS on-media compression constants.
- Declares the global `struct ubifs_info info_`, verbosity/debug globals, the LEB writer, and device-table lookup/override/free APIs.
- Defines `struct path_htbl_element` and `struct name_htbl_element` used by device-table parsing.

## Notes
This header couples the mkfs translation units through shared globals and helper macros. Its `err_msg()`/`sys_err_msg()` macros return `-1` as expression blocks, so callers depend on GNU C extensions.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/ubifs.h -->
# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/ubifs.h

## Purpose
Provides the subset of UBIFS kernel data structures and inline helpers needed by `mkfs.ubifs`.

## Main Contents
- Defines UBIFS size constants, key storage union, and logical eraseblock property categories/flags.
- Declares in-memory LPT structures: cnodes, pnodes, nnodes, nbranches, LPT statistics, and LPT lprops.
- Declares index/TNC structures: `ubifs_zbranch` and flexible-array `ubifs_znode`.
- Defines the mkfs-oriented `struct ubifs_info` containing filesystem geometry, journal/log/LPT/index state, lprops accounting, UBI device/volume metadata, reserved pool state, and LPT serialization positions.
- Provides `ubifs_idx_node_sz()` and `ubifs_idx_branch()` helpers for variable-width index nodes.

## Notes
This is not a full kernel UBIFS header. It is a userspace-compatible subset sized around mkfs and LPT creation, with many fields retained because kernel-derived helper code expects the same conceptual state object.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mkfs.ubifs/ubifs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mtd_debug.c -->
# File Research: sources/local-fs/mtd-utils/mtd_debug.c

## Purpose
Small diagnostic utility for querying, reading, writing, and erasing raw MTD devices.

## Main Behavior
- `info` prints MTD type, capability flags, size, erase size, write size, OOB size, and erase-region geometry using `MEMGETINFO`, `MEMGETREGIONCOUNT`, and `MEMGETREGIONINFO`.
- `read` seeks to an offset and copies bytes from flash into a destination file.
- `write` seeks to an offset and writes bytes from a source file to flash.
- `erase` issues `MEMERASE` for an offset/length pair.

## Dependencies
Uses legacy Linux MTD ioctls from `mtd/mtd-user.h`, POSIX open/read/write/lseek, and common mtd-utils error helpers.

## Notes
This utility does minimal validation and does not use libmtd. The read/write loops treat partial reads and writes simplistically. `file_to_flash()` uses `fread(buf, size, 1, fp)`, so short source files are fatal rather than naturally writing fewer bytes.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mtd_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/mtdpart.c -->
# File Research: sources/local-fs/mtd-utils/mtdpart.c

## Purpose
Adds or removes kernel partitions on an MTD device using the block partitioning ioctl interface.

## Main Behavior
- Supports `add <MTD_DEVICE> <PART_NAME> <START> <SIZE>` and `del <MTD_DEVICE> <PART_NUMBER>`.
- Parses numeric start, length, and partition number with mtd-utils simple integer helpers.
- Fills `struct blkpg_partition` and `struct blkpg_ioctl_arg`, then issues `ioctl(fd, BLKPG, &arg)` with `BLKPG_ADD_PARTITION` or `BLKPG_DEL_PARTITION`.

## Dependencies
Uses Linux `blkpg.h`, POSIX file APIs, getopt, and common mtd-utils helpers.

## Notes
The tool validates non-negative values and partition-name length, but alignment to eraseblock size is documented rather than checked. It assumes the kernel exposes BLKPG behavior for the target MTD node.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/mtdpart.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/nanddump.c -->
# File Research: sources/local-fs/mtd-utils/nanddump.c

## Purpose
Dumps NAND page data, and optionally OOB data, from an MTD partition to a file or stdout.

## Main Behavior
- Parses output file, start, length, ECC/raw mode, pretty/canonical hex output, OOB inclusion, quiet mode, and bad-block policy.
- Opens libmtd and obtains device geometry.
- Optionally enters raw mode with `MTDFILEMODE`.
- Iterates page by page, detecting bad eraseblocks with `mtd_is_bad()`.
- Handles bad blocks by skipping them, dumping them, or padding them with `0xFF`.
- Reads data with `mtd_read()` and OOB with `mtd_read_oob()`.
- Reports ECC corrected/failed deltas when `ECCGETSTATS` is available.

## Dependencies
Depends on libmtd, Linux MTD ioctls, mtd-utils common helpers, and local pretty-print formatting adapted from kernel hexdump logic.

## Notes
Binary output to a TTY is blocked unless forced. Buffer allocation multiplies by `sizeof(pointer)` instead of byte size, which over-allocates rather than under-allocates on normal platforms. The `-c` option intentionally falls through to enable pretty printing.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/nanddump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/nandtest.c -->
# File Research: sources/local-fs/mtd-utils/nandtest.c

## Purpose
Destructive NAND erase/write/read verification test.

## Main Behavior
- Opens an MTD device read-write and gets geometry with `MEMGETINFO`.
- Tests a selected offset/length range in eraseblock-sized units.
- For each non-bad block, generates deterministic pseudo-random data from a recorded seed, erases the block, writes it, and reads/verifies it multiple times.
- Tracks ECC corrected and failed counters through `ECCGETSTATS`.
- Optionally marks erase/write-failed blocks bad and optionally restores original contents after each block test.

## Dependencies
Uses raw Linux MTD ioctls (`MEMERASE`, `MEMGETBADBLOCK`, `MEMSETBADBLOCK`, `ECCGETSTATS`) and POSIX `pread`/`pwrite`.

## Notes
This is destructive unless `--keep` is used, and even `--keep` still erases and rewrites the flash. Offsets and lengths are stored as 32-bit values, limiting suitability for larger devices.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/nandtest.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/nandwrite.c -->
# File Research: sources/local-fs/mtd-utils/nandwrite.c

## Purpose
Writes a page-aligned image, optionally including OOB data, to a NAND MTD device.

## Main Behavior
- Parses start offset, input skip/size, padding, OOB-only/OOB-included modes, ECC/raw/autoplace mode, bad-block skipping, bad-block marking, quiet mode, and eraseblock alignment.
- Obtains device geometry through libmtd and validates page alignment and image fit.
- Reads input in page-sized chunks, optionally with OOB bytes after each page.
- Skips bad eraseblocks unless `--noskipbad` is set.
- Writes data/OOB via `mtd_write()`.
- On EIO write failure, erases the aligned eraseblock range, optionally marks the failing block bad, rewinds buffered data, and retries at the next eraseblock range.

## Dependencies
Uses libmtd, Linux MTD raw-file mode, POSIX file APIs, and mtd-utils common helpers.

## Notes
The buffer holds one aligned eraseblock worth of input so writes can be replayed after bad-block failure. Padding is prohibited with OOB-bearing input except in OOB-only mode. Partial-write cleanup treats any remaining buffered/input data as fatal at exit.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/nandwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/nftl_format.c -->
# File Research: sources/local-fs/mtd-utils/nftl_format.c

## Purpose
Formats an MTD device or region as NFTL or INFTL media.

## Main Behavior
- Opens the target MTD device, validates supported erase sizes, derives partition size and erase-zone count, and limits NFTL zones to `MAX_ERASE_ZONES`.
- Checks factory bad-block markers in OOB and optionally performs erase/write/read pattern tests.
- Can use a device bad-block table instead of OOB/RWE checks.
- Builds NFTL or INFTL media headers and a bad unit table.
- Writes primary and spare media headers/bad-unit tables, then writes Unit Control Information OOB records for good erase units.

## Dependencies
Uses legacy Linux MTD data/OOB ioctls, NFTL/INFTL UAPI headers, mtd endian helpers, and direct 512-byte sector assumptions.

## Notes
The file is explicitly old and marked under-tested. It assumes 512-byte page/OOB layouts in several places and only implements `UnitSizeFactor == 0xFF` handling. The tool is destructive.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/nftl_format.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/nftldump.c -->
# File Research: sources/local-fs/mtd-utils/nftldump.c

## Purpose
Inspects and optionally extracts data from NFTL-formatted flash.

## Main Behavior
- Scans eraseblock boundaries for primary/spare `ANAND` NFTL media headers.
- Reads the bad unit table and allocates a Virtual Unit Chain table.
- Reads Unit Control Information from OOB for each erase unit, reports free/bad/chain/replacement state, and records starts of virtual unit chains.
- Walks virtual unit chains and, if an output file is supplied, reconstructs 512-byte sectors from the last used sector in each chain.

## Dependencies
Uses NFTL UAPI structures, Linux MTD OOB ioctls, mtd endian helpers, and fixed 512-byte sector logic.

## Notes
`ERASESIZE` and `NUMVUNITS` are fixed compile-time assumptions for parts of extraction, so dumps may be wrong for non-8KiB erase units. `find_media_headers()` uses a static scan offset, letting `main()` continue scanning for additional NFTL partitions across the device.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/nftldump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/rbtree.c -->
# File Research: sources/local-fs/mtd-utils/rbtree.c

## Purpose
User-space copy of the Linux red-black tree balancing and traversal implementation.

## Main Entry Points
- `rb_insert_color()` rebalances after caller-performed binary-search-tree insertion.
- `rb_erase()` removes a node and rebalances.
- `rb_first()`, `rb_last()`, `rb_next()`, and `rb_prev()` traverse ordered nodes.
- `rb_replace_node()` swaps a node in place without rebalancing.

## Dependencies
Includes only `rbtree.h` and libc. Callers provide their own search/insert comparisons and embed `struct rb_node`.

## Notes
This is generic infrastructure ported from the kernel. Correctness depends on callers using `rb_link_node()` before insertion and not mutating ordering keys while nodes are in the tree.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/rbtree.h -->
# File Research: sources/local-fs/mtd-utils/rbtree.h

## Purpose
Declares the generic red-black tree node/root types, color/parent packing helpers, traversal APIs, and embedding macros.

## Main Contents
- `struct rb_node` stores parent pointer and color in `rb_parent_color`.
- `struct rb_root` stores the root node.
- Macros expose parent/color checks, `container_of`, `rb_entry`, empty-node/root checks, and `RB_ROOT`.
- `rb_link_node()` links a new red leaf before `rb_insert_color()` is called.

## Dependencies
Includes Linux-style `kernel.h` and `stddef.h` headers from the mtd-utils include environment.

## Notes
The API mirrors old Linux kernel rbtree conventions: there are no callbacks, so users implement type-specific search/insert logic.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/recv_image.c -->
# File Research: sources/local-fs/mtd-utils/recv_image.c

## Purpose
Receives a multicast/unicast UDP image stream with FEC redundancy and writes the reconstructed image to an MTD device or regular file.

## Main Behavior
- Opens the target as an MTD device if possible, otherwise as a regular file with assumed eraseblock size.
- Joins IPv4/IPv6 multicast groups when applicable and binds a datagram socket.
- Uses the first packet to learn eraseblock size, block count, total CRC, and FEC packet count.
- Buffers received packet indices per eraseblock, rejects duplicate and bad-CRC packets, and writes incoming payload data temporarily to flash/file.
- Uses FEC to reconstruct each eraseblock once enough packets are available.
- Verifies reconstructed block CRC, erases temporary flash contents on MTD targets, then writes the final decoded eraseblock.
- Tracks and prints network, flash read/write/erase, CRC, and FEC timing.

## Dependencies
Uses `mcast_image.h` FEC APIs, mtd-utils CRC, Linux MTD erase/bad-block ioctls, POSIX sockets, multicast membership APIs, and POSIX file I/O.

## Notes
The program is experimental in places, including comments about deliberately using bad blocks and recovering from write failures. The allocation check for `eb_buf` and `decode_buf` uses `&&`, so one failed allocation can go unnoticed. It writes temporary encoded data to flash before final reconstruction, making it destructive for target MTD devices.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/recv_image.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/rfddump.c -->
# File Research: sources/local-fs/mtd-utils/rfddump.c

## Purpose
Extracts a Resident Flash Disk (RFD) image from NOR flash or a block-size-specified input file.

## Main Behavior
- Determines block geometry from MTD `MEMGETINFO` or a user-provided block size.
- Computes header sectors, data sectors, CHS-style sector count, and a logical-sector map.
- Scans each block for `RFD_MAGIC`, reads the sector mapping header, and records physical offsets for logical sectors.
- Emits a flat 512-byte-sector output image, filling missing sectors with zeroes.

## Dependencies
Uses Linux MTD geometry for NOR targets, POSIX file APIs, getopt, fixed 512-byte sectors, and mtd endian helpers.

## Notes
The tool only accepts MTD devices of type `MTD_NORFLASH` when deriving geometry automatically. Duplicate sector mappings and out-of-range entries are warnings. A failed `sector_map` allocation frees the wrong pointer (`rfd.sector_map`) after it is known NULL, leaking `header` in that path.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/rfddump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/rfdformat.c -->
# File Research: sources/local-fs/mtd-utils/rfdformat.c

## Purpose
Formats NOR flash for Resident Flash Disk use.

## Main Behavior
- Opens an MTD device read-write and validates it is NOR flash no larger than 32 MiB.
- Requires at least two erase units.
- Erases every eraseblock with `MEMERASE`.
- Writes the two-byte RFD magic value at the beginning of each eraseblock.

## Dependencies
Uses Linux MTD geometry/erase ioctls and POSIX `pwrite`.

## Notes
The operation is fully destructive. The formatter is intentionally simple and does not build a populated sector map beyond placing per-block magic.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/rfdformat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/serve_image.c -->
# File Research: sources/local-fs/mtd-utils/serve_image.c

## Purpose
Continuously transmits an image over UDP with per-block FEC redundancy for `recv_image`.

## Main Behavior
- Opens and mmaps an image file, requires its size to be a multiple of the supplied eraseblock size, and computes full-image and per-block CRCs.
- Splits each eraseblock into `PKT_SIZE` data packets and creates 50% extra FEC packets.
- Fills `struct image_pkt` headers with total CRC, block CRC, block number, packet number, packet sequence, eraseblock size, and packet count.
- Sends packets in an infinite cycle, alternating packet order across blocks to spread FEC encode cost.
- Rate-limits packet sends with `nanosleep()` based on requested KiB/s.

## Dependencies
Uses `mcast_image.h` FEC APIs, mtd-utils CRC, POSIX sockets, `mmap`, and time APIs.

## Notes
The transmitter never exits normally. It sends host-independent integer fields through explicit network byte order but relies on the shared packet struct layout. The rate-slip condition compares `now.tv_usec` to an expression beginning with `now.tv_usec`, which appears logically wrong and may not reset timing as intended.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/serve_image.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/summary.h -->
# File Research: sources/local-fs/mtd-utils/summary.h

## Purpose
Defines JFFS2 summary record structures and accounting helpers used by `sumtool`.

## Main Contents
- Space accounting macros for dirty, used, wasted, and unchecked space.
- Block state constants and summary size macros.
- Packed on-flash summary record types for unknown, inode, dirent, xattr, and xref nodes.
- Packed in-memory linked-list summary record types mirroring the flash forms.
- `struct jffs2_summary` collection state and end-of-eraseblock summary marker structure.

## Dependencies
Includes Linux JFFS2 node definitions from `linux/jffs2.h`.

## Notes
The structures are packed to match on-flash layout. Several comments retain old typos, but the definitions directly support JFFS2 summary-node serialization.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/summary.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/sumtool.c -->
# File Research: sources/local-fs/mtd-utils/sumtool.c

## Purpose
Converts a JFFS2 image into a summarized JFFS2 image to reduce mount-time scanning.

## Main Behavior
- Parses input/output files, eraseblock size, target endian, cleanmarker policy/size, verbosity, and final padding.
- Loads the input image eraseblock by eraseblock.
- Scans JFFS2 nodes, validates header/node/data/name CRCs for supported node types, and skips invalid or padding/cleanmarker nodes as appropriate.
- Copies inode, dirent, xattr, and xref nodes into an output eraseblock buffer and records compact summary entries.
- Flushes summary nodes and summary markers near the end of each output eraseblock.
- Optionally inserts cleanmarkers and pads the final output eraseblock with `0xFF`.

## Main Entry Points
- `process_options()` sets input/output and format behavior.
- `create_summed_image()` parses one input eraseblock.
- `add_sum_*_mem()` and `write_*_to_buff()` collect records and copy nodes.
- `dump_sum_records()` serializes a `JFFS2_NODETYPE_SUMMARY` node and marker.
- `flush_buffers()` writes remaining data/summary state.

## Dependencies
Uses JFFS2 user headers, `summary.h`, mtd-utils CRC/common helpers, endian conversion macros, and POSIX file APIs.

## Notes
The parser advances by four bytes after many malformed-node cases, so it is tolerant but can be slow/noisy on corrupt input. `process_options()` uses `errmsg_die()` for help/version paths, which may exit as an error depending on helper semantics. The tool rewrites only recognized live node types into summarized output.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/sumtool.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/Makefile

## Purpose
Top-level test makefile for mtd-utils tests.

## Behavior
Defines `SUBDIRS = checkfs fs-tests jittertest ubi-tests` and forwards `all`, `clean`, and `tests` targets to each subdirectory with `$(MAKE) -C $@ $(MAKECMDGOALS)`.

## Notes
This is a recursive dispatcher; it contains no compile rules itself.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/checkfs/Makefile

## Purpose
Builds the checkfs power-failure test utilities.

## Behavior
Sets `TARGETS = checkfs makefiles`, includes the shared `../../common.mk`, and links both targets with `comm.o` from the build directory.

## Notes
`comm.o` is shared because `checkfs` needs the power-down signaling routine; `makefiles` does not directly call it but receives the same dependency through this make rule.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/checkfs.c -->
# File Research: sources/local-fs/mtd-utils/tests/checkfs/checkfs.c

## Purpose
Power-failure filesystem integrity test harness. It verifies a set of checksum-protected files after each boot, signals an external power controller, then continuously rewrites random files until power is cut.

## Main Behavior
- Configures a serial port at 9600 baud, 7-bit, even parity for sending power-down permission.
- Verifies `file0` through `file99` using a CRC-CCITT table and the file format generated by `makefiles`.
- Logs each run and CRC error to `logfile`, syncing log data.
- Repairs files with failed CRCs until an allowed error threshold is exceeded.
- Updates and syncs `cycleCnt`, then writes an “ok to power me down” message via `do_pwr_dn()`.
- Enters an endless loop rewriting random-sized checksum-protected files with single `write()` calls followed by truncation.

## Options
Supports serial device selection (`-p`), maximum file size (`-s`), maximum tolerated CRC errors (`-e`), and help.

## Dependencies
Uses `common.h` constants, `comm.c` for power-down signaling, POSIX file/serial APIs, and local CRC logic.

## Notes
The test is designed for destructive/rebooting environments. `send_pwrdn_ok()` calls `fileno(cyclefp)` before checking whether `fopen("cycleCnt","wb")` succeeded. File names are `file%i`, despite older comments referring to zero-padded names.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/checkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/comm.c -->
# File Research: sources/local-fs/mtd-utils/tests/checkfs/comm.c

## Purpose
Communication shim for the checkfs power-cycle harness.

## Main Entry Point
- `do_pwr_dn(int fd, int cycleCnt)` formats and writes an “ok to power me down” message plus the current cycle count to an already-open communication file descriptor.

## Dependencies
Uses POSIX `write()` and libc string formatting.

## Notes
The file is intentionally replaceable so the checkfs harness can use a different power-control mechanism. It treats short writes as failure.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/comm.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/common.h -->
# File Research: sources/local-fs/mtd-utils/tests/checkfs/common.h

## Purpose
Tiny shared header for the checkfs file generator and checker.

## Main Definitions
Defines boolean-style `TRUE`/`FALSE` macros and `MAX_NUM_FILES` as `100`.

## Notes
No include guard is present, but the header is small and only macro-based.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/makefiles.c -->
# File Research: sources/local-fs/mtd-utils/tests/checkfs/makefiles.c

## Purpose
Initializes the checkfs test directory by generating checksum-protected random files and a cycle counter.

## Main Behavior
- Creates `MAX_NUM_FILES` files named `file0` through `file99`.
- For each file, writes a leading byte-size integer followed by random integer data, then appends a little-endian CRC-CCITT checksum.
- Reopens each file to verify the checksum reaches the expected final CRC value.
- Creates `cycleCnt` initialized to binary integer zero.

## Dependencies
Uses the local `common.h` constants, libc file APIs, and endian conversion for the appended checksum.

## Notes
The file format is consumed by `checkfs.c`. Random generation is not explicitly seeded, so initial files are deterministic under the C library’s default `rand()` seed.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/checkfs/makefiles.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/Makefile

## Purpose
Recursive makefile for filesystem tests under `tests/fs-tests`.

## Behavior
Defines `SUBDIRS = lib simple stress integrity utils` and forwards `all`, `clean`, and `tests` targets to each subdirectory.

## Notes
This dispatcher coordinates the test-suite subtrees but has no compile commands of its own.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/help_all.sh -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/help_all.sh

## Purpose
Convenience script to print help output for the filesystem test binaries.

## Behavior
Runs `-h` for simple tests, stress atom tests, and `integrity/integck`, printing separator lines between each invocation.

## Dependencies
Expects test binaries to be built and runnable from the `tests/fs-tests` directory layout.

## Notes
The script is POSIX shell and does not use `set -e`; it continues even if one help command fails.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/help_all.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/integrity/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/integrity/Makefile

## Purpose
Builds the filesystem integrity checker `integck`.

## Behavior
- Defaults `CC` to `gcc` when not supplied.
- Adds include paths for shared mtd-utils headers and libubi headers.
- Builds a local `libubi.a` by compiling `../../../ubi-utils/libubi.c`.
- Builds `integck` against that local libubi archive.
- Provides a `debug` target using `-O0`, `-D INTEGCK_DEBUG`, and `-rdynamic`.
- `clean` removes objects, target binary, and local archive.

## Notes
This makefile embeds a local static libubi build rather than depending on a preinstalled library.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/integrity/Makefile -->