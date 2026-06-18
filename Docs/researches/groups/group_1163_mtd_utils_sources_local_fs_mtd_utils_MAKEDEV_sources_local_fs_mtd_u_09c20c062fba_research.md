# Group Research: group_1163_mtd_utils_sources_local_fs_mtd_utils_MAKEDEV_sources_local_fs_mtd_u_09c20c062fba

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/mtd-utils`. Every file listed in this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/MAKEDEV -->
# File Research: sources/local-fs/mtd-utils/MAKEDEV

## Purpose
Shell helper for creating legacy MTD, FTL, NFTL, RFD, and INFTL device nodes under `/dev`.

## Key Elements
Defines `mkftl`, `mknftl`, `mkrfd`, and `mkinftl`, each creating one base block device and 15 partition nodes. Iterates letters `a` through `p`, allocating minors in groups of 16, then creates `/dev/mtdN`, `/dev/mtdrN`, and `/dev/mtdblockN` for `0..16`.

## Dependencies
Requires bash plus privileged `mknod`, `seq`, and `expr`. Encodes historical major numbers: FTL 44, NFTL 93, RFD 256, INFTL 96, MTD char 90, MTD block 31.

## Risks
Hard-codes `/dev` paths and old static device numbering, so it is unsafe on systems managed by `udev`/`devtmpfs` and must be run with root privileges.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/MAKEDEV -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/Makefile -->
# File Research: sources/local-fs/mtd-utils/Makefile

## Purpose
Top-level build script for this vendored `mtd-utils` tree, version `1.5.2`.

## Key Elements
Declares top-level MTD utilities, UBI utilities, `mkfs.ubifs`, static libraries, and installed scripts. Generates `include/version.h`, includes `common.mk`, and defines object/library relationships for `mkfs.jffs2`, `lib/libmtd.a`, `mkfs.ubifs`, and `ubi-utils` libraries.

## Dependencies
Uses zlib, optional LZO, UUID libraries, `ubi-utils`, `mkfs.ubifs`, local `include`, and `lib/libmtd.a`. Build toggles include `WITHOUT_XATTR`, `WITHOUT_LZO`, and externally supplied `ZLIB*`, `LZO*`, `UUID*` flags.

## Behavior/Risks
The `install` target installs all binaries/scripts to `${DESTDIR}/${SBINDIR}` and gzips man pages. `clean` conditionally removes `$(BUILDDIR)`, guarded to avoid deleting the source directory, but still expects make variables to be correct.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/common.mk -->
# File Research: sources/local-fs/mtd-utils/common.mk

## Purpose
Shared make rules and compiler/linker defaults for `mtd-utils`.

## Key Elements
Defines `CC`, `AR`, `RANLIB`, warning probes, large-file support, install directories, `BUILDDIR`, quiet/verbose echo helpers, archive/link/compile rules, dependency generation, and `all`, `clean`, `install` phony targets.

## Dependencies
Relies on GNU make features, compiler option probing through shell commands, and `.c` source to `.o` dependency generation with `-MMD -MF`.

## Behavior/Risks
Uses GCC extensions and assumes compatible make semantics. `SECTION_CFLAGS` probes linker garbage collection by passing linker flags through a compile test, which may vary across toolchains.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/common.mk -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/compr.c -->
# File Research: sources/local-fs/mtd-utils/compr.c

## Purpose
User-space JFFS2 compression registry and compressor selection logic used by `mkfs.jffs2`.

## Key Elements
Implements a small Linux-style intrusive list, global compression mode state, optional compression self-checking, compressor registration/unregistration, priority changes, enable/disable by name, compressor listings, and statistics. `jffs2_compress()` supports `none`, `priority`, `size`, and `favourlzo` modes.

## Dependencies
Depends on `compr.h`, local JFFS2 constants, allocator macros mapped to libc, and external compressor modules initialized by `jffs2_zlib_init`, `jffs2_rtime_init`, and `jffs2_lzo_init`.

## Behavior/Risks
The module uses global mutable state and fixed 16 KiB buffers for formatted stats/list output. Size-selection mode allocates per-compressor buffers and transfers ownership of the winning buffer to the caller. Error handling is mostly stderr messages plus fallback to uncompressed data.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/compr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/compr.h -->
# File Research: sources/local-fs/mtd-utils/compr.h

## Purpose
Public interface for the JFFS2 compression subsystem in this user-space build.

## Key Elements
Defines enabled compressors, priorities, compression modes, kernel compatibility shims (`kmalloc`, `printk`, `KERN_*`), a minimal `list_head`, and `struct jffs2_compressor`.

## Dependencies
Includes stdio/stdlib/stdint and `linux/jffs2.h`. Declares zlib, rtime, and LZO compressor init/exit functions when configured.

## Behavior/Risks
The header intentionally emulates kernel APIs in user space. Callers must treat returned compression buffers and allocated stats/list strings as heap-owned.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/compr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/compr_lzo.c -->
# File Research: sources/local-fs/mtd-utils/compr_lzo.c

## Purpose
JFFS2 LZO compressor adapter.

## Key Elements
When LZO is enabled, allocates LZO work memory and a worst-case temporary output buffer, uses `lzo1x_999_compress`, checks destination size before copying, and uses `lzo1x_decompress_safe`. Registers compressor name `lzo`, type `JFFS2_COMPR_LZO`, priority `80`, disabled by default.

## Dependencies
Depends on `lzo/lzo1x.h`, `linux/jffs2.h`, `compr.h`, and external `page_size`. If `WITHOUT_LZO` is defined, init/exit become no-ops.

## Behavior/Risks
Compression uses global work buffers, so it is not reentrant. LZO is registered disabled, requiring explicit enablement by name or policy.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/compr_lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/compr_rtime.c -->
# File Research: sources/local-fs/mtd-utils/compr_rtime.c

## Purpose
JFFS2 RTIME compressor adapter implementing a simple byte-history encoder.

## Key Elements
Tracks last positions for each byte value, emits literal byte plus run length pairs, and reconstructs output with overlapping-copy handling. Registers compressor name `rtime`, type `JFFS2_COMPR_RTIME`, priority `50`, enabled by default.

## Dependencies
Uses `stdint.h`, `string.h`, and `compr.h`.

## Behavior/Risks
The decompressor trusts the encoded stream and target `destlen`; malformed input can make it read beyond compressed data because `srclen` is unused.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/compr_rtime.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/compr_zlib.c -->
# File Research: sources/local-fs/mtd-utils/compr_zlib.c

## Purpose
JFFS2 zlib compressor adapter.

## Key Elements
Uses `deflateInit` level 3, partial flushes, and a 12-byte reserved stream ending area. Decompression wraps zlib `inflate`. Registers compressor name `zlib`, type `JFFS2_COMPR_ZLIB`, priority `60`, enabled by default.

## Dependencies
Depends on zlib, `common.h`, `compr.h`, and JFFS2 type definitions. Temporarily renames zlib's `crc32` symbol to avoid conflicts.

## Behavior/Risks
The decompressor ignores the final inflate status and returns success after `inflateEnd`, so corrupt compressed input may not always be surfaced correctly.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/compr_zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/doc_loadbios.c -->
# File Research: sources/local-fs/mtd-utils/doc_loadbios.c

## Purpose
Loads a firmware/BIOS image into a DiskOnChip MTD device, preserving an optional IPL prefix/tail.

## Key Elements
Opens flash and firmware, reads MTD geometry with `MEMGETINFO`, optionally preserves bytes before the requested IPL offset, erases affected eraseblocks, rewrites preserved IPL bytes, then writes firmware in 512-byte chunks padded with `0xff`.

## Dependencies
Uses raw MTD ioctls and `mtd/mtd-user.h`.

## Behavior/Risks
Destructive raw flash writer. It does not enforce the disabled 64 KiB firmware size check and has minimal validation of offset/geometry beyond ioctl success.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/doc_loadbios.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/docfdisk.c -->
# File Research: sources/local-fs/mtd-utils/docfdisk.c

## Purpose
Inspects and rewrites INFTL partition tables on DiskOnChip devices.

## Key Elements
Scans the first 10 eraseblocks for an INFTL media header (`BNAND`), reads OOB data, prints partition details, accepts up to four requested partition sizes, rewrites partition metadata, duplicates the media header at `buf + 4096`, erases the header block, restores OOB, and writes pages back.

## Dependencies
Uses MTD ioctls, `mtd/inftl-user.h`, `mtd/mtd-user.h`, and `mtd_swab.h` endian helpers.

## Behavior/Risks
Highly destructive and legacy-specific. It warns that failure while erasing/writing may leave the MediaHeader damaged. Uses global buffer pointers and assumes media-header layout details such as the spare copy at offset 4096.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/docfdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/fectest.c -->
# File Research: sources/local-fs/mtd-utils/fectest.c

## Purpose
Standalone forward-error-correction test for multicast image packet recovery.

## Key Elements
Creates deterministic random eraseblock-sized data, splits it into packets, intentionally drops selected packet numbers, uses `fec_new`, `fec_encode`, and `fec_decode`, compares the recovered data, and writes `before`/`after` files on mismatch.

## Dependencies
Depends on `mcast_image.h` for FEC APIs and packet size, and includes `crc32.h` though this file does not call CRC directly.

## Behavior/Risks
Test harness only. Packet drop patterns and random seed are hard-coded; allocated packet buffers are not freed before process exit.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/fectest.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_erase.c -->
# File Research: sources/local-fs/mtd-utils/flash_erase.c

## Purpose
Erases ranges of MTD eraseblocks, optionally writing JFFS2 cleanmarkers.

## Key Elements
Parses `--jffs2`, `--noskipbad`, `--unlock`, and quiet/help/version options. Uses libmtd to get device geometry, skips bad blocks by default, optionally unlocks each eraseblock, erases with `mtd_erase`, and writes cleanmarkers either to NAND OOB or NOR/main area.

## Dependencies
Uses `common.h`, `crc32.h`, `libmtd.h`, `mtd/mtd-user.h`, and `mtd/jffs2-user.h`.

## Behavior/Risks
Destructive flash operation. It refuses JFFS2 formatting on MLC NAND, but otherwise assumes caller-provided offsets/counts are appropriate. Bad-block skipping can be disabled with `-N`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_erase.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_eraseall -->
# File Research: sources/local-fs/mtd-utils/flash_eraseall

## Purpose
Compatibility wrapper for the removed `flash_eraseall` command.

## Key Elements
Prints a deprecation message, appends `0 0` when arguments are present, and execs `flash_erase`.

## Dependencies
Requires `/bin/sh` and `flash_erase` in `PATH`.

## Behavior/Risks
Maintains old command behavior by erasing from offset 0 to end of device; this is destructive by design.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_eraseall -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_lock.c -->
# File Research: sources/local-fs/mtd-utils/flash_lock.c

## Purpose
Builds the locking variant of the shared flash lock/unlock utility.

## Key Elements
Defines `PROGRAM_NAME` as `flash_lock` and includes `flash_unlock.c`, causing the shared code to compile with `FLASH_UNLOCK` set to `0` and use `MEMLOCK`.

## Dependencies
Depends entirely on `flash_unlock.c` implementation and MTD lock ioctl support.

## Behavior/Risks
This include-based reuse is intentional but fragile: macro state before inclusion determines whether the compiled utility locks or unlocks.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_dump.c -->
# File Research: sources/local-fs/mtd-utils/flash_otp_dump.c

## Purpose
Dumps factory or user One-Time Programmable MTD data as hexadecimal rows.

## Key Elements
Accepts `-f` or `-u`, opens the device read-only, selects `MTD_OTP_FACTORY` or `MTD_OTP_USER` with `OTPSELECT`, and reads/prints 16 bytes per line.

## Dependencies
Uses MTD OTP ioctls from `mtd/mtd-user.h`.

## Behavior/Risks
Read-only utility. Return values are errno-style integers, and the printed offset is relative to the selected OTP data stream.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_info.c -->
# File Research: sources/local-fs/mtd-utils/flash_otp_info.c

## Purpose
Reports factory or user OTP region count, offsets, sizes, and lock state.

## Key Elements
Selects OTP mode, queries region count with `OTPGETREGIONCOUNT`, allocates a stack VLA of `struct otp_info`, then queries and prints all regions.

## Dependencies
Uses `mtd/mtd-user.h` OTP ABI.

## Behavior/Risks
Read-only, but uses a variable-length stack array sized by kernel-reported count. Error message for `OTPGETREGIONINFO` incorrectly says `OTPGETREGIONCOUNT`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_lock.c -->
# File Research: sources/local-fs/mtd-utils/flash_otp_lock.c

## Purpose
Locks a user OTP range permanently.

## Key Elements
Requires `-u <device> <offset> <size>`, selects user OTP mode, parses offset/size with `strtoul`, prompts for confirmation, and issues `OTPLOCK`.

## Dependencies
Uses `mtd/mtd-user.h` and `common.h` for prompting.

## Behavior/Risks
Irreversible operation. The tool warns that locked OTP regions cannot be unlocked but relies on the caller to provide exact region boundaries.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_write.c -->
# File Research: sources/local-fs/mtd-utils/flash_otp_write.c

## Purpose
Writes raw stdin data into user OTP storage at a requested offset.

## Key Elements
Selects user OTP mode, queries MTD geometry, seeks to the offset, reads stdin in write-size chunks for NAND or 256-byte chunks otherwise, pads partial NAND writes with `0xff`, and writes until EOF.

## Dependencies
Uses `common.h`, `mtd/mtd-user.h`, and `mtd_type_is_nand_user`.

## Behavior/Risks
Destructive and irreversible at the bit level: OTP bits set to 0 cannot be erased. It uses a fixed 2048-byte buffer and errors if NAND writesize exceeds it.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_otp_write.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flash_unlock.c -->
# File Research: sources/local-fs/mtd-utils/flash_unlock.c

## Purpose
Shared implementation for `flash_unlock` and, when included by `flash_lock.c`, `flash_lock`.

## Key Elements
Parses `<mtd device> [offset] [block count]`, reads device size and erase size using `MEMGETINFO`, validates range, and issues either `MEMUNLOCK` or `MEMLOCK` depending on compile-time macros.

## Dependencies
Uses `common.h` and `mtd/mtd-user.h`.

## Behavior/Risks
Offset and count parsing uses `strtol` without full validation. A block count of `-1` means the entire device.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flash_unlock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/flashcp.c -->
# File Research: sources/local-fs/mtd-utils/flashcp.c

## Purpose
Copies a regular file to an MTD flash device, erasing first and verifying afterward.

## Key Elements
Parses `-v/--verbose`, validates input file fits device size, erases enough eraseblocks, writes data in 10 KiB chunks, rewinds both descriptors, reads both back, and compares.

## Dependencies
Uses raw `MEMGETINFO` and `MEMERASE` ioctls from `mtd/mtd-user.h`.

## Behavior/Risks
Destructive writer. It does not handle bad NAND blocks and contains a compile-time `#warning` noting smaller erase regions are not handled.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/flashcp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ftl_check.c -->
# File Research: sources/local-fs/mtd-utils/ftl_check.c

## Purpose
Inspects an FTL-formatted MTD character device and prints erase-unit allocation information.

## Key Elements
Finds a plausible FTL erase-unit header, prints formatted size and erase-unit size, scans each erase unit, checks header consistency, identifies transfer units, reads BAM entries, and counts control/data/free/deleted blocks.

## Dependencies
Uses `mtd/mtd-user.h`, `mtd/ftl-user.h`, `mtd_swab.h`, and `common.h`.

## Behavior/Risks
Read-only diagnostic. It assumes classic FTL layout and validates only enough fields to choose a header.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ftl_check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/ftl_format.c -->
# File Research: sources/local-fs/mtd-utils/ftl_format.c

## Purpose
Formats an MTD character device as a legacy FTL partition.

## Key Elements
Builds FTL erase-unit headers, computes transfer units, reserve percentage, BAM offset, formatted size, erases the partition, writes headers, and initializes BAM blocks as control blocks. Options include quiet, confirmation prompt, spare transfer blocks, reserve percent, and boot image size.

## Dependencies
Uses `mtd/mtd-user.h`, `mtd/ftl-user.h`, `mtd_swab.h`, and `common.h`.

## Behavior/Risks
Destructive formatter. It assumes 512-byte logical blocks and classic FTL structures; allocation failures for the BAM buffer are not explicitly checked.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/ftl_format.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/common.h -->
# File Research: sources/local-fs/mtd-utils/include/common.h

## Purpose
Common utility macros and inline helpers used across `mtd-utils`.

## Key Elements
Provides min/max/alignment helpers, off_t printf format macros, standard message/error/warning macros, a fallback `rpmatch`, `prompt`, `is_power_of_2`, simple full-string numeric parsers, and `common_print_version`.

## Dependencies
Requires `PROGRAM_NAME` to be defined before inclusion and includes generated `version.h` plus `xalloc.h`.

## Behavior/Risks
Uses GNU C statement expressions and `typeof`. `prompt` defaults to the provided answer when input cannot be read.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/crc32.h -->
# File Research: sources/local-fs/mtd-utils/include/crc32.h

## Purpose
Declares the local MTD CRC32 routine.

## Key Elements
Includes `stdint.h` and declares `uint32_t mtd_crc32(uint32_t val, const void *ss, int len)`.

## Dependencies
Implemented by `lib/libcrc32.c`.

## Behavior/Risks
The caller controls the initial CRC value; this project commonly passes `0` for JFFS2 node CRCs and uses other constants for UBI/UBIFS elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/libmtd.h -->
# File Research: sources/local-fs/mtd-utils/include/libmtd.h

## Purpose
Public API for the `libmtd` user-space helper library.

## Key Elements
Defines `libmtd_t`, `struct mtd_info`, `struct mtd_dev_info`, and functions for opening/closing the library, discovering devices, querying geometry, locking/unlocking, erasing, bad-block handling, OOB I/O, data I/O, image writing, torture testing, and probing nodes.

## Dependencies
Depends on MTD ABI structs such as `region_info_user`; implementations are in the libmtd sources outside this group.

## Behavior/Risks
This is a thin abstraction over sysfs and MTD ioctls. Callers must still open device nodes and pass valid eraseblock indexes and offsets.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/libmtd.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/linux/jffs2.h -->
# File Research: sources/local-fs/mtd-utils/include/linux/jffs2.h

## Purpose
User-space copy of JFFS2 on-flash constants and node layout definitions.

## Key Elements
Defines JFFS2 magic values, compression IDs, compatibility flags, node types, xattr prefixes, endian wrapper structs, raw inode/dirent/xattr/xref/summary structs, and `union jffs2_node_union`.

## Dependencies
Requires C99 fixed-width integer types to be included before use.

## Behavior/Risks
All raw structs are packed and model physical media layout. Any changes must remain ABI-compatible with kernel JFFS2 format.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/linux/jffs2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ftl-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/ftl-user.h

## Purpose
Userspace definitions for legacy Flash Translation Layer metadata.

## Key Elements
Defines `erase_unit_header_t`, header flags, and block allocation macros/constants for free, deleted, control, data, replacement, and bad blocks.

## Dependencies
Uses `u_int*` typedefs from system headers included by callers.

## Behavior/Risks
Represents old on-flash FTL layout used by `ftl_check` and `ftl_format`; packed/endianness handling is left to callers.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ftl-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/inftl-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/inftl-user.h

## Purpose
Userspace definitions for INFTL DiskOnChip metadata.

## Key Elements
Defines OSAK/PERCENT constants, sector size, INFTL OOB block-control/unit-control structures, partition records, media header, and partition flags `INFTL_BINARY`, `INFTL_BDTL`, `INFTL_LAST`.

## Dependencies
Uses Linux integer typedefs such as `__u32` supplied by included system headers in callers.

## Behavior/Risks
On-flash structs are packed and legacy-specific. `docfdisk` relies on these layouts directly.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/inftl-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/jffs2-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/jffs2-user.h

## Purpose
User-space endian and xattr helpers for JFFS2 tooling.

## Key Elements
Includes `linux/jffs2.h`, declares external `target_endian`, defines conversion macros for JFFS2 endian-wrapped types, little-endian helpers, xattr namespace strings, JFFS2 ACL structs, and POSIX ACL xattr structs.

## Dependencies
Depends on `endian.h`, `byteswap.h`, and a program-defined `target_endian` global.

## Behavior/Risks
Conversion macros depend on mutable global `target_endian`; tools parsing images must set it correctly for cross-endian images.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/jffs2-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/mtd-abi.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/mtd-abi.h

## Purpose
User-space MTD ioctl ABI definitions.

## Key Elements
Defines erase, OOB, write-request, MTD info, region info, OTP info, legacy NAND OOB/ECC layout, ECC stats, device type/capability constants, OTP modes, operation modes, ioctl numbers, file modes, and `mtd_type_is_nand_user`.

## Dependencies
Includes `linux/types.h` and relies on ioctl macros from system headers included by users.

## Behavior/Risks
This is ABI surface shared with the kernel. Several interfaces are explicitly obsolete but retained for compatibility, such as `MEMGETOOBSEL` and `nand_ecclayout_user`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/mtd-abi.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/mtd-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/mtd-user.h

## Purpose
Small compatibility wrapper for userspace MTD ABI inclusion.

## Key Elements
Includes `stdint.h` and `mtd/mtd-abi.h`, then typedefs common old names such as `mtd_info_t`, `erase_info_t`, `region_info_t`, `nand_oobinfo_t`, and `nand_ecclayout_t`.

## Dependencies
Depends on `mtd/mtd-abi.h`.

## Behavior/Risks
Keeps older code compiling against newer ABI struct names.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/mtd-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/nftl-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/nftl-user.h

## Purpose
Userspace definitions for NFTL media and OOB metadata.

## Key Elements
Defines NFTL block-control info, unit-control variants, OOB wrapper, media header, max erase zones, erase/fold markers, sector states, and zone states.

## Dependencies
Uses fixed-width integer typedefs supplied by callers.

## Behavior/Risks
Models legacy on-flash structures for DiskOnChip/NFTL tooling; packed structs must match media format exactly.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/nftl-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubi-media.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/ubi-media.h

## Purpose
Defines UBI on-flash media format structures and constants.

## Key Elements
Includes UBI version, erase counter limits, CRC init, EC/VID magic values, volume type/flag/compat constants, EC header, VID header, internal layout volume constants, volume limits, and volume table record layout.

## Dependencies
Uses big-endian Linux types from `asm/byteorder.h`.

## Behavior/Risks
This is persistent media ABI. Fields such as CRCs, sequence numbers, erase counters, and volume table records must remain compatible with kernel UBI.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubi-media.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubi-user.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/ubi-user.h

## Purpose
Defines the user-space UBI ioctl API.

## Key Elements
Documents attach/detach, volume create/remove/resize/rename/update, LEB erase/change/map/unmap/is-mapped, property setting, and block-device creation/removal. Defines ioctl numbers and request structs including `ubi_attach_req`, `ubi_mkvol_req`, `ubi_rsvol_req`, `ubi_rnvol_req`, `ubi_leb_change_req`, `ubi_map_req`, `ubi_set_vol_prop_req`, and `ubi_blkcreate_req`.

## Dependencies
Uses standard fixed-width integer types expected from the surrounding build environment.

## Behavior/Risks
Reserved padding fields must be zeroed by callers. Some fields such as `dtype` are obsolete but kept for old-kernel compatibility.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubi-user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubifs-media.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd/ubifs-media.h

## Purpose
Defines UBIFS on-flash format constants and node layouts.

## Key Elements
Declares UBIFS magic/version/minimum sizes, key format constants, inode/file/node/compression enums, filesystem area limits, node size macros, inode flags, common node header, device descriptor, inode, dent, data, truncation, padding, superblock, master, reference, branch, index, commit-start, and orphan node structs.

## Dependencies
Uses Linux endian types from `asm/byteorder.h`.

## Behavior/Risks
This is persistent media ABI. Packed structs and padding sizes are part of disk format and must be kept synchronized with kernel UBIFS.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd/ubifs-media.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd_swab.h -->
# File Research: sources/local-fs/mtd-utils/include/mtd_swab.h

## Purpose
Simple endian byte-swap and CPU/endian conversion helpers.

## Key Elements
Defines `swab16`, `swab32`, `swab64`, `cpu_to_le*`, `cpu_to_be*`, `le*_to_cpu`, and `be*_to_cpu`, selected by `__BYTE_ORDER`.

## Dependencies
Includes `endian.h` and expects fixed-width integer types to be available from callers.

## Behavior/Risks
Uses GNU statement expressions for conversion macros on swapped paths. It may conflict with system headers that already define similarly named macros.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/mtd_swab.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/include/xalloc.h -->
# File Research: sources/local-fs/mtd-utils/include/xalloc.h

## Purpose
Inline allocation wrappers that terminate the program on allocation failure.

## Key Elements
Defines `xmalloc`, `xcalloc`, `xzalloc`, `xrealloc`, `xstrdup`, and, under `_GNU_SOURCE`, `xasprintf`. Functions are marked `unused` to avoid warnings.

## Dependencies
Requires `sys_errmsg_die` from `common.h`, plus stdlib/string/stdarg.

## Behavior/Risks
These helpers exit the process instead of returning allocation errors, simplifying callers but making recovery impossible.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/include/xalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/jffs-dump.c -->
# File Research: sources/local-fs/mtd-utils/jffs-dump.c

## Purpose
Raw diagnostic dumper for old JFFS filesystem images.

## Key Elements
Defines old JFFS raw inode structures and constants, checksum/endian helper routines, raw inode printing, then scans an image word-by-word for empty, dirty, and magic regions. Optionally filters by inode number and prints names.

## Dependencies
Uses `common.h`, Linux byteorder macros, and direct `pread` over an image file.

## Behavior/Risks
Diagnostic only. Several declared functions are unused leftovers, and scan logic trusts raw inode sizes from the image when advancing offsets.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/jffs-dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/jffs2dump.c -->
# File Research: sources/local-fs/mtd-utils/jffs2dump.c

## Purpose
Dumps and optionally endian-converts binary JFFS2 images.

## Key Elements
Parses image endian, content dumping, endian conversion output, CRC recalculation, and NAND data/OOB peeling options. `do_dumpcontent()` walks JFFS2 nodes, validates header/node/data/name/summary CRCs, and prints node details. `do_endianconvert()` writes a byte-swapped image with optional recalculated CRCs.

## Dependencies
Uses `mtd/jffs2-user.h`, `summary.h`, `crc32.h`, `common.h`, endian/byteswap headers, and full-file in-memory loading.

## Behavior/Risks
Global state and fixed `cnvfile[256]` are used. Option table marks `--recalccrc` as requiring an argument while short `-r` does not. Conversion logic handles many node types but has fragile manual pointer arithmetic.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/jffs2dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/jffs2reader.c -->
# File Research: sources/local-fs/mtd-utils/jffs2reader.c

## Purpose
Reads JFFS2 images to list directories recursively or extract a regular file to stdout.

## Key Elements
Loads the whole image, reconstructs files and directories by scanning nodes in version order, supports zlib/none/zero compression, resolves absolute and relative paths including `.`/`..` and symlinks, prints ls-like metadata, and extracts selected files using a 5 MiB scratch buffer.

## Dependencies
Uses zlib, `mtd/jffs2-user.h`, and `common.h` allocation/error helpers.

## Behavior/Risks
The file documents that CRC checking is missing. It does not support all JFFS2 compression methods, uses fixed buffers for names/symlinks/scratch extraction, and trusts many image lengths after only basic magic scanning.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/jffs2reader.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/lib/libcrc32.c -->
# File Research: sources/local-fs/mtd-utils/lib/libcrc32.c

## Purpose
Implements the local CRC32 routine used by JFFS2/MTD utilities.

## Key Elements
Contains a 256-entry CRC32 table for polynomial `0xedb88320` and `mtd_crc32()`, which updates an initial CRC value over a byte buffer.

## Dependencies
Only includes `stdint.h`; declared by `include/crc32.h`.

## Behavior/Risks
Straight table-driven CRC implementation. It does not apply final xor or inversion by itself; callers must use the convention required by their on-flash format.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/lib/libcrc32.c -->