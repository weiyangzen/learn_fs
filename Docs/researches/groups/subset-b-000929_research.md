# subset-b-000929 research

This grouped report covers the requested Linux kernel source snapshot files under `sources/distributed-fs/ceph-client`. Each section is source-tree aligned and bounded by reconciliation markers for splitting into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ibm.c -->
# sources/distributed-fs/ceph-client/block/partitions/ibm.c

## Purpose

`ibm.c` implements IBM s390 DASD partition recognition for the generic Linux block partition scanner. It detects and interprets DASD volume labels in EBCDIC form, including `VOL1` CDL labels, `LNX1` Linux LDL labels, and `CMS1` VM/CMS labels, then emits Linux partitions through `put_partition()`.

Although the source is stored under a `ceph-client` snapshot, this file is kernel block-layer partition code. It integrates through `check.h` and the partition parser table, not through Ceph request or object paths.

## Important APIs, Types, And Functions

The public entry point is `ibm_partition(struct parsed_partitions *state)`. It obtains block geometry with `disk->fops->getgeo`, optional DASD metadata via the exported `dasd_biodasdinfo` symbol, logical block size from `bdev_logical_block_size()`, and disk capacity from `bdev_nr_sectors()`.

Local helpers `cchh2blk()` and `cchhb2blk()` convert IBM cylinder/head/block VTOC addresses into linear block numbers using `struct hd_geometry`, including the DASD large-volume cylinder encoding. `find_label()` probes the possible label sectors, copies the label into `union label_t`, converts type and volume id from EBCDIC to ASCII with `EBCASC()`, and selects the label parser. `find_vol1_partitions()`, `find_lnx1_partitions()`, and `find_cms1_partitions()` implement the three supported label formats.

Important structures come from architecture DASD and VTOC headers: `dasd_information2_t`, `vtoc_volume_label_cdl`, `vtoc_volume_label_ldl`, `vtoc_cms_label`, `vtoc_format1_label`, `vtoc_cchh`, and `vtoc_cchhb`.

## Control Flow

`ibm_partition()` exits early when geometry or capacity is unavailable. It dynamically pins `dasd_biodasdinfo` with `symbol_get()`, allocates temporary `info`, `geo`, and label objects, seeds `geo->start`, calls `getgeo`, and falls back to a generic scan if DASD info cannot be obtained.

`find_label()` probes exactly one known label location when DASD info is available, otherwise it tries sector 1, block 1, and block 2 adjusted for logical block size. Once a valid label type is found, `ibm_partition()` dispatches by label type. `VOL1` parsing walks VTOC format labels beginning at the VTOC pointer, skipping FMT4/FMT5/FMT7/FMT9, accepting FMT1/FMT8 extents, and emitting one partition per extent. `LNX1` parsing creates a single Linux partition after the label, using formatted-block metadata when the label has large-volume support and geometry/capacity checks otherwise. `CMS1` parsing creates one partition for the CMS data region, with special handling for reserved minidisks and DIAG FBA label placement.

If no valid label is found but the device responded to DASD info, the parser still claims the disk for backward compatibility; LDL-formatted DASDs get a synthetic single partition after the label block.

## State And Persistence Behavior

The file has no persistent kernel state. It builds temporary parse state from on-disk DASD labels and releases every sector with `put_dev_sector()` and every allocation with `kfree()`. The persistent state is the disk-resident volume label/VTOC/CMS metadata; emitted partition state is stored in `parsed_partitions` for the block layer to publish later.

## Dependencies And Integration Points

Dependencies include `linux/buffer_head.h`, `linux/hdreg.h`, `asm/dasd.h`, `asm/vtoc.h`, `asm/ebcdic.h`, `linux/dasd_mod.h`, and the local partition scanner API in `check.h`. Runtime DASD-specific integration is optional through `symbol_get(dasd_biodasdinfo)`, which allows this parser to run when DASD support is modular.

## Risks And Edge Cases

The parser depends on reliable geometry. Incorrect heads/sectors values can produce wrong VTOC extent starts and sizes. Label probing without DASD info intentionally tries multiple sectors, which can claim unusual disks if label-like data is present. `VOL1` parsing must stop on invalid format ids and avoid exceeding `state->limit`. `LNX1` has careful geometry-versus-capacity fallback for old labels; without real DASD info it may decline to create a partition rather than guess. `CMS1` must handle sector-1 labels on block sizes larger than 512 bytes while still starting the partition at block 2.

## Test Signals

Useful tests include DASD images with `VOL1`, `LNX1` old and new large-volume versions, `CMS1` regular and reserved-minidisk labels, missing labels on a DASD device, and malformed VTOC entries. Signals are the parser return value, `pp_buf` strings such as `VOL1/`, `LNX1/`, `CMS1/`, `(nonl)`, correct partition starts/sizes, no leaked sector references, and graceful `-1` only for real read/allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ibm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/karma.c -->
# sources/distributed-fs/ceph-client/block/partitions/karma.c

## Purpose

`karma.c` recognizes the simple Rio Karma media-player partition label. It is a small partition parser that reads sector 0, checks a `0xAB56` little-endian magic, and publishes up to two firmware-defined data partitions.

## Important APIs, Types, And Functions

The only entry point is `karma_partition(struct parsed_partitions *state)`. It uses a packed local `disklabel` containing two `d_partition` records, each with filesystem type, offset, and size. It calls `read_part_sector()`, `put_partition()`, `seq_buf_puts()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0 and returns `-1` on read failure. If `d_magic` is not `KARMA_LABEL_MAGIC`, it releases the sector and returns `0` so other partition parsers may try. When the magic matches, it scans two entries, emits a partition only when `p_fstype == 0x4d` and `p_size` is nonzero, increments the visible slot for each table entry, and stops when reaching `state->limit`.

## State And Persistence Behavior

There is no mutable or persistent kernel state. The persistent format is the Rio Karma on-disk sector-0 label; the parser only fills `parsed_partitions` for the current scan.

## Dependencies And Integration Points

It depends only on `check.h` and core compiler attributes. Its integration point is the block partition parser dispatch that calls `karma_partition()` when the corresponding partition support is configured.

## Risks And Edge Cases

The parser assumes the label layout is packed and sector 0 is readable. It intentionally accepts only type `0x4d`; other entries are ignored even if they have sizes. Slot accounting still advances for ignored entries, preserving physical table position but possibly leaving holes. `state->limit` prevents overflowing the parser result table.

## Test Signals

Tests should cover absent magic, a read failure, two valid partitions, zero-size entries, wrong filesystem types, and a small `state->limit`. Expected signals are return `0` for non-Karma disks, return `1` with a trailing newline for valid labels, and partition offsets/sizes matching little-endian fields exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/karma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.c -->
# sources/distributed-fs/ceph-client/block/partitions/ldm.c

## Purpose

`ldm.c` implements Linux partition scanning for Microsoft Logical Disk Manager dynamic disks. It first verifies an MS-DOS partition table containing type `0x42`, then reads the LDM private headers, TOC blocks, VMDB header, and VBLK database to create Linux block partitions for the data extents that belong to the current disk.

The implementation is read-only parser code. It does not manage Windows dynamic volumes or assemble striped/RAID volumes; it exposes the disk-local partition extents described in LDM metadata.

## Important APIs, Types, And Functions

The public entry point is `ldm_partition(struct parsed_partitions *state)`. Validation helpers include `ldm_validate_partition_table()`, `ldm_validate_privheads()`, `ldm_validate_tocblocks()`, and `ldm_validate_vmdb()`. Low-level parsers include `ldm_parse_privhead()`, `ldm_parse_tocblock()`, `ldm_parse_vmdb()`, and `ldm_parse_vblk()`.

VBLK-specific parsers are `ldm_parse_cmp3()`, `ldm_parse_dgr3()`, `ldm_parse_dgr4()`, `ldm_parse_dsk3()`, `ldm_parse_dsk4()`, `ldm_parse_prt3()`, and `ldm_parse_vol5()`. Variable-length fields are decoded by `ldm_relative()`, `ldm_get_vnum()`, and `ldm_get_vstr()`. Database assembly is handled by `ldm_ldmdb_add()`, `ldm_frag_add()`, `ldm_frag_commit()`, `ldm_get_vblks()`, and `ldm_free_vblks()`. `ldm_create_data_partitions()` filters partition VBLKs to the current disk and emits them.

Logging is centralized in `_ldm_printk()` behind `ldm_debug`, `ldm_info`, `ldm_error`, and `ldm_crit`.

## Control Flow

`ldm_partition()` performs a cheap signature gate first: sector 0 must have an MS-DOS magic and at least one primary entry with `LDM_PARTITION`. It allocates an `ldmdb`, validates the three private headers, uses `ph.config_start` as the database base, then validates at least one matching TOC block and the VMDB. VBLK lists are initialized only after the database headers are consistent.

`ldm_validate_privheads()` reads primary and backup `PRIVHEAD` records at fixed offsets. Backup offsets are interpreted relative to the primary `config_start` after the primary is parsed. It checks version `2.11` or `2.12`, disk/config ranges, GUID validity, and primary/first-backup equality. The third private header is tolerated when it fails on odd-sized disks.

`ldm_validate_tocblocks()` reads up to four TOC blocks. Vista-era databases may not have all four, so at least one valid TOC is required and any additional valid TOCs must match. `ldm_validate_vmdb()` checks VMDB magic/version, committed-transaction state, nonzero VBLK size, and that `last_vblk_seq` does not exceed the configured bitmap region.

`ldm_get_vblks()` walks VBLK sectors under the VMDB, validates `MAGIC_VBLK`, parses single-record VBLKs immediately, collects fragmented multi-record VBLKs in a temporary list, then commits complete fragments. `ldm_ldmdb_add()` classifies parsed VBLKs into disk group, disk, volume, component, and partition lists, sorting partition VBLKs by start sector per disk. Finally, `ldm_create_data_partitions()` matches the current disk GUID to a disk object id and publishes every partition VBLK whose `disk_id` points at that disk.

## State And Persistence Behavior

All mutable state is temporary in-memory scan state. `struct ldmdb` caches parsed private-header, TOC, VMDB, and VBLK lists only for the duration of `ldm_partition()`. Fragmented VBLKs are held in temporary `struct frag` allocations until committed. All lists are freed before return.

Persistent state is entirely on disk: MBR type `0x42`, LDM private headers, TOCs, VMDB, VBLKs, GUIDs, object ids, partition starts, sizes, and database sequence numbers. The parser emits transient `parsed_partitions` entries; it does not write LDM metadata.

## Dependencies And Integration Points

The file depends on `ldm.h`, `check.h`, `linux/msdos_partition.h`, unaligned big-endian accessors, UUID helpers, list APIs, and kernel allocation primitives. Its main integration point is the generic block partition scanner. It also relies on the MBR parser contract because type `0x42` is the dynamic-disk discriminator.

## Risks And Edge Cases

The highest-risk area is parsing variable-length VBLK fields. `ldm_relative()` protects many offsets, but `ldm_get_vnum()` and `ldm_get_vstr()` intentionally trust already range-checked field starts, so any missed bound check can become an out-of-bounds read. Fragment handling must reject duplicate, incomplete, or impossible record groups and preserve the common header from record 0.

Database range checks are security-sensitive because malformed disk images are attacker-controlled input. Incorrect `config_start`, `config_size`, `vblk_size`, `last_vblk_seq`, or TOC bitmap ranges could otherwise make the scanner read outside the disk or loop over invalid metadata. The code also intentionally ignores some third-private-header mismatch cases for compatibility.

The implementation exposes disk-local partitions, not composed LDM volumes. Users may see extents for dynamic disks but not necessarily usable higher-level Windows dynamic volumes such as stripes or RAID sets.

## Test Signals

Tests should include non-LDM MBRs, LDM type without valid private headers, mismatched backup private headers, missing Vista TOCs with one valid TOC, inconsistent TOCs, uncommitted VMDB transactions, out-of-range VBLK sequences, single-record and fragmented VBLKs, duplicate fragments, missing disk object id, and multiple partition VBLKs sorted by start. Expected signals are return `0` for non-LDM disks, `-1` for corrupt dynamic disks, `1` plus `[LDM]` output for valid databases, and no memory leaks across all failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.h -->
# sources/distributed-fs/ceph-client/block/partitions/ldm.h

## Purpose

`ldm.h` defines the constants and in-memory structures used by `ldm.c` to parse Microsoft Logical Disk Manager dynamic-disk metadata. It names magic values, VBLK types, VBLK flags, fixed offsets in the 1 MiB database, and cache structures for parsed database objects.

## Important APIs, Types, And Functions

There are no functions in this header. Important constants include `MAGIC_VMDB`, `MAGIC_VBLK`, `MAGIC_PRIVHEAD`, `MAGIC_TOCBLOCK`, `VBLK_VOL5`, `VBLK_CMP3`, `VBLK_PRT3`, `VBLK_DSK3`, `VBLK_DSK4`, `VBLK_DGR3`, `VBLK_DGR4`, `LDM_DB_SIZE`, `OFF_PRIV*`, `OFF_TOCB*`, `OFF_VMDB`, `LDM_PARTITION`, `TOC_BITMAP1`, and `TOC_BITMAP2`.

Important types are `struct frag`, `struct privhead`, `struct tocblock`, `struct vmdb`, the VBLK payload structs (`vblk_comp`, `vblk_dgrp`, `vblk_disk`, `vblk_part`, `vblk_volu`), `struct vblk_head`, `struct vblk`, and `struct ldmdb`.

## Control Flow

Control flow is supplied by `ldm.c`; this header shapes it by giving the parser fixed offsets and typed destinations. `struct ldmdb` is the central control object: validation fills `ph`, `toc`, and `vm`, then VBLK parsing populates the five `list_head` collections used by partition creation.

## State And Persistence Behavior

The structures here are in-memory normalized forms of on-disk LDM records. Numeric fields are stored in CPU-endian form after parsing. Lists are transient parser state and are not persisted. The persistent representation remains the disk database; the header deliberately does not define packed on-disk structs for most VBLKs because the format uses variable-width fields.

## Dependencies And Integration Points

The header includes Linux type, list, filesystem, unaligned-access, and byteorder headers. It forward-declares `struct parsed_partitions` for the parser integration. It is private to the partition parser implementation and is not a general LDM kernel API.

## Risks And Edge Cases

Constants in this file are format contracts. Incorrect VBLK fixed sizes, offsets, or flags would break parsing and could cause invalid range checks in `ldm.c`. The flexible-array `struct frag` assumes allocations size `sizeof(*f) + size * num`; callers must ensure `num` and `size` are bounded.

## Test Signals

Signals are indirect through `ldm.c`: valid Windows 2000/XP and Vista dynamic-disk images should parse, unsupported VBLK types should be ignored or rejected as designed, and structures should compile cleanly across 32-bit and 64-bit architectures with correct UUID and list alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ldm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.c -->
# sources/distributed-fs/ceph-client/block/partitions/mac.c

## Purpose

`mac.c` parses Apple Partition Map disk labels. It verifies the driver descriptor in block 0, reads the partition map entries using the media block size recorded by the descriptor, publishes every valid map entry, and marks Linux RAID entries.

## Important APIs, Types, And Functions

The public entry point is `mac_partition(struct parsed_partitions *state)`. It uses `struct mac_driver_desc` and `struct mac_partition` from `mac.h`. On PowerMac builds, `mac_fix_string()` trims trailing spaces and `note_bootable_part()` is called to report the most plausible root partition.

## Control Flow

The parser reads sector 0 and requires `MAC_DRIVER_MAGIC`. It extracts the Apple block size, rejects non-power-of-two block sizes because entries could straddle unreadable sector boundaries, then reads the first partition entry. The first entry must have `MAC_PARTITION_MAGIC`; its `map_count` determines how many entries to scan, capped by `DISK_MAX_PARTS` and `state->limit`.

For each slot, the parser reads `slot * secsize`, checks the entry signature, emits start and size in 512-byte sectors, and flags `Linux_RAID` entries with `ADDPART_FLAG_RAID`. PowerMac-specific logic scores bootable PowerPC/Linux/root-like partitions and reports the best one.

## State And Persistence Behavior

No persistent kernel state is stored, except the optional PowerMac bootable partition note. The on-disk Apple Partition Map persists names, types, status bits, starts, and sizes. The parser emits transient `parsed_partitions` entries.

## Dependencies And Integration Points

It depends on `check.h`, `mac.h`, `linux/ctype.h`, endian conversion helpers, and optionally `asm/machdep.h`. Its integration is the Linux partition parser table and, on PowerMac, architecture setup code that consumes `note_bootable_part()`.

## Risks And Edge Cases

The block-size logic is the main edge case. Non-power-of-two block sizes are rejected, and entries whose structure would exceed the readable rounded-down data area return `-1`. `blocks_in_map` is unsigned in use, so the `blocks_in_map < 0` check is redundant, but the upper-bound check prevents impossible map counts. Strings from disk may not be NUL-terminated; PowerMac scoring trims before comparisons.

## Test Signals

Tests should cover absent driver magic, bad partition signature, non-power-of-two block sizes, valid maps with multiple entries, oversized map counts, RAID type detection, and PowerMac root scoring. Expected output includes ` [mac]`, correct 512-sector scaling, and a clean newline on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.h -->
# sources/distributed-fs/ceph-client/block/partitions/mac.h

## Purpose

`mac.h` defines the Apple Partition Map structures and constants used by `mac.c`. It captures the big-endian on-disk layout for partition entries and driver descriptors.

## Important APIs, Types, And Functions

The header defines `MAC_PARTITION_MAGIC`, `APPLE_AUX_TYPE`, `MAC_STATUS_BOOTABLE`, and `MAC_DRIVER_MAGIC`. `struct mac_partition` contains signature, map count, start block, block count, name, type, data/boot fields, status, boot addresses, checksum, processor, and padding. `struct mac_driver_desc` contains driver descriptor signature, block size, block count, device metadata, and driver count. There are no functions.

## Control Flow

`mac.c` uses `mac_driver_desc.block_size` to determine how to address partition entries and `mac_partition.map_count` to bound the scan. It uses `start_block`, `block_count`, `type`, `status`, `name`, and `processor` to emit partitions and optional boot hints.

## State And Persistence Behavior

These structs model persistent on-disk Apple metadata. They are read directly from sector buffers and interpreted with big-endian accessors. The header itself stores no state.

## Dependencies And Integration Points

It depends on Linux fixed-width integer types already available to includers. It is private to the block partition parser and should remain layout-compatible with the Apple Partition Map disk format.

## Risks And Edge Cases

Because the structures are disk layouts, field size or ordering changes would break parsing. String fields are fixed-width and may lack terminators, so users must compare with bounded string APIs. Numeric fields must be converted from big endian by callers.

## Test Signals

Compile coverage plus `mac.c` parser tests validate this header. Valid images should decode starts and sizes correctly; malformed signatures should not be accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/msdos.c -->
# sources/distributed-fs/ceph-client/block/partitions/msdos.c

## Purpose

`msdos.c` implements the Linux parser for DOS/MBR partition tables and several MBR-contained subpartition formats. It recognizes primary and extended partitions, protects GPT disks by ignoring protective MBRs, detects AIX labels, and optionally parses Solaris x86 VTOC, BSD disklabels, UnixWare slices, and Minix subpartitions.

## Important APIs, Types, And Functions

The public entry point is `msdos_partition(struct parsed_partitions *state)`. Core helpers are `nr_sects()`, `start_sect()`, `is_extended_partition()`, `msdos_magic_present()`, `aix_magic_present()`, `set_info()`, and `parse_extended()`.

Subpartition support is split across `parse_solaris_x86()`, `parse_bsd()`, `parse_freebsd()`, `parse_netbsd()`, `parse_openbsd()`, `parse_unixware()`, and `parse_minix()`, gated by Kconfig symbols. The `subtypes[]` table maps MBR type ids to subparsers. Local disk-format structs model Solaris VTOC, BSD disklabels, UnixWare slices, and Minix secondary MBRs.

## Control Flow

`msdos_partition()` reads sector 0. Before checking the DOS `55 aa` magic, it calls `aix_magic_present()` because some AIX disks lack DOS magic. AIX detection returns to `aix_partition()` when configured, otherwise prints `[AIX]` and declines the disk.

When DOS magic is present, the parser validates all four boot indicators as either `0` or `0x80`; if the first invalid indicator still looks like a FAT boot sector, it treats the disk as a whole-disk FAT volume and returns success without partitions. It then ignores GPT protective MBRs when EFI partition support is configured.

The first pass emits primary partitions and follows extended partitions. Extended partition parsing treats logical partitions as a linked list of partition tables, emits data entries, follows the first extended link, guards against loops with `loopct > 100`, and validates suspicious third/fourth entries against parent extended bounds. The second pass invokes subtype parsers for recognized primary partition ids.

## State And Persistence Behavior

The parser mutates `state->next` for logical and subpartition allocation, fills per-slot metadata UUIDs from the MBR disk signature in `set_info()`, and sets RAID flags for Linux RAID ids. It does not persist data. On-disk persistent inputs include the MBR, EBR chain, disk signature, type ids, and optional nested labels.

## Dependencies And Integration Points

Dependencies include `linux/msdos_fs.h`, `linux/msdos_partition.h`, `linux/unaligned.h`, `check.h`, and `efi.h`. It integrates with AIX and EFI parsers through conditional calls and with the generic partition scanner through `parsed_partitions`. FAT boot-sector checks use `struct fat_boot_sector` and `fat_valid_media()`.

## Risks And Edge Cases

Extended partition chains are attacker-controlled linked lists; the loop counter, `state->limit`, DOS magic checks, and bounds checks on unusual entries prevent infinite loops and bogus partitions. Logical block sizes larger than 512 bytes are handled with `sector_size`, but the protective one-sector extended partition placeholder is intentionally approximate. AIX and Solaris share confusing signatures/type ids with Linux swap/data cases, so detection includes compatibility heuristics. Subparsers must avoid duplicating parent whole-disk entries and reject out-of-parent BSD subpartitions.

## Test Signals

Tests should cover plain MBRs, invalid boot indicators, whole-disk FAT, GPT protective MBR, AIX magic with and without Linux partitions, extended chains including loops and OS/2-style extra entries, Linux RAID flags, DM/EZD annotations, and each configured subparser. Expected signals include stable primary slots 1-4, logical slots starting at 5, disk-signature UUIDs like `<disk>-<slot>`, and graceful stop at `state->limit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/msdos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/of.c -->
# sources/distributed-fs/ceph-client/block/partitions/of.c

## Purpose

`of.c` implements partition discovery from Open Firmware device-tree nodes. It scans child nodes of the block device's Open Firmware node, validates `partition-*` nodes, reads their `reg` ranges, and publishes them as Linux partitions.

## Important APIs, Types, And Functions

The entry point is `of_partition(struct parsed_partitions *state)`. `validate_of_partition()` checks node names and slot ranges. `add_of_partition()` reads properties and calls `put_partition()`. It uses Open Firmware helpers such as `disk_to_dev()`, `dev_of_node()`, `for_each_child_of_node()`, `of_node_name_eq()`, `of_property_read_u32()`, and `of_property_read_reg()`.

## Control Flow

`of_partition()` obtains the disk device node and returns `0` when no OF node exists. For each child, `validate_of_partition()` requires a `partition-` prefix and a valid numeric suffix, then rejects slot `0` or slots beyond `state->limit`. `add_of_partition()` reads a 64-bit start and size from `reg`, emits the partition, optionally fills `volname` from `label`, and optionally marks the slot read-only from the `read-only` property.

## State And Persistence Behavior

The parser does not write persistent state. Device-tree properties are the persistent firmware-provided source. It fills `state->parts[slot]`, including metadata and flags, for the current scan.

## Dependencies And Integration Points

It depends on the driver core and Open Firmware APIs plus `check.h`. It integrates with platforms that describe fixed partitions in firmware rather than on the block media itself.

## Risks And Edge Cases

Node naming is strict; malformed `partition-*` suffixes are ignored. Slot `0` is rejected because it represents the whole disk. Missing or invalid `reg` causes the node to be skipped. Labels are copied with `strscpy()`, avoiding unterminated strings. Firmware data can conflict with on-disk partition tables, so parser ordering determines final behavior.

## Test Signals

Tests should include no OF node, valid partition child nodes, malformed names, slot zero, slots beyond limit, missing `reg`, labels, and read-only properties. Expected signals are ` [of]` output on at least one valid partition, correct slot placement, `has_info` for labels, and `ADDPART_FLAG_READONLY` when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/osf.c -->
# sources/distributed-fs/ceph-client/block/partitions/osf.c

## Purpose

`osf.c` parses OSF/1 disklabels. It reads the disklabel from sector 0, verifies the OSF magic, and publishes up to 18 partitions from the embedded table.

## Important APIs, Types, And Functions

The entry point is `osf_partition(struct parsed_partitions *state)`. It defines `MAX_OSF_PARTITIONS` and `DISKLABELMAGIC`, uses a local packed view of the disklabel, and calls `read_part_sector()`, `put_partition()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0, checks `d_magic`, then scans `d_partitions` until either the configured maximum or `state->limit - 1` is reached. Entries with zero size are skipped. Nonzero entries are emitted with little-endian start and size.

## State And Persistence Behavior

There is no persistent kernel state. The persistent state is the OSF disklabel. The parser only populates `parsed_partitions` for the current scan.

## Dependencies And Integration Points

It depends on `check.h` and endian helpers. Its integration is the generic partition parser dispatch for OSF disklabel support.

## Risks And Edge Cases

Malformed sector reads return `-1`; wrong magic returns `0`. The parser trusts the fixed label layout and does not validate checksums or parent bounds. `state->limit` prevents writing past available partition slots.

## Test Signals

Test wrong magic, valid labels with sparse entries, maximum partition count, and read failures. Signals are return codes, emitted slot count, and exact little-endian starts/sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/osf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sgi.c -->
# sources/distributed-fs/ceph-client/block/partitions/sgi.c

## Purpose

`sgi.c` parses SGI disk labels. It validates the SGI label magic and checksum, then publishes non-volume partitions from the SGI partition array.

## Important APIs, Types, And Functions

The entry point is `sgi_partition(struct parsed_partitions *state)`. It defines `SGI_LABEL_MAGIC`, SGI partition constants, local `struct sgi_disklabel`, and uses big-endian conversion for label fields. It calls `read_part_sector()` and `put_partition()`.

## Control Flow

The parser reads sector 0, checks the big-endian magic, computes the label checksum by summing 32-bit words, and rejects labels whose checksum is nonzero. It scans up to the SGI partition count and `state->limit`, skips empty entries and whole-volume entries, emits start/size pairs, and prints ` [sgi]`.

## State And Persistence Behavior

The parser holds only a sector mapping during the scan. SGI disklabel contents are persistent on disk; emitted partitions are transient parser results.

## Dependencies And Integration Points

It depends on `check.h` and endian helpers. It integrates through the block partition parser framework.

## Risks And Edge Cases

Checksum handling is important because SGI labels use a zero-sum scheme over the label block. The parser must skip volume-header/entire-volume entries to avoid duplicate whole-disk partitions. It does not deeply validate that starts and sizes fall inside device capacity.

## Test Signals

Tests should include wrong magic, bad checksum, empty entries, whole-volume entries, and valid SGI partitions. Expected signals are `0` for non-SGI, `1` with ` [sgi]` for valid labels, and correct big-endian start/size decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sgi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sun.c -->
# sources/distributed-fs/ceph-client/block/partitions/sun.c

## Purpose

`sun.c` parses Sun disk labels. It verifies the Sun label magic and checksum, supports optional VTOC sanity checks, and publishes up to eight Sun partition entries.

## Important APIs, Types, And Functions

The entry point is `sun_partition(struct parsed_partitions *state)`. It uses constants `SUN_LABEL_MAGIC`, `SUN_VTOC_SANITY`, and partition ids such as `SUN_WHOLE_DISK`. It reads `struct sun_disklabel` from sector 0 and emits partitions through `put_partition()`.

## Control Flow

The parser reads sector 0, verifies the magic, and computes the checksum across 16-bit words. It determines the number of entries from the VTOC when sane, otherwise defaults to the classic Sun count. For each entry, it skips empty partitions and whole-disk entries, computes the start from cylinder and sector geometry encoded in the label, emits size, and prints ` [sun]`.

## State And Persistence Behavior

There is no persistent kernel state. The persistent input is the Sun disk label. The parser fills `parsed_partitions` only during the scan.

## Dependencies And Integration Points

It depends on `check.h` and Sun partition definitions available through kernel partition headers. It is called by the generic block partition scanner.

## Risks And Edge Cases

Checksum validation and endian conversion are key correctness points. Whole-disk entries are skipped to avoid duplicate device nodes. Geometry-derived starts can be wrong if the on-disk label is malformed. `state->limit` bounds output slots.

## Test Signals

Tests should cover wrong magic, checksum failure, sane and legacy VTOC entry counts, whole-disk entries, sparse entries, and starts computed from cylinder offsets. Expected output includes ` [sun]` only for accepted labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sysv68.c -->
# sources/distributed-fs/ceph-client/block/partitions/sysv68.c

## Purpose

`sysv68.c` parses Motorola/System V/68 disk labels. It reads the volume id, disk configuration, and slice table from sector 0 and publishes valid slices.

## Important APIs, Types, And Functions

The entry point is `sysv68_partition(struct parsed_partitions *state)`. Local structures `volumeid`, `dkconfig`, `dkblk0`, and `slice` describe the disk-resident label. The parser uses `read_part_sector()`, endian/access helpers, and `put_partition()`.

## Control Flow

The parser reads sector 0, validates the expected volume id and configuration magic/checksum fields, then scans the fixed slice table. Valid slices are emitted until `state->limit` is reached. It prints a label marker on success and releases the sector on all paths.

## State And Persistence Behavior

No state persists in the kernel. The persistent state is the SysV68 disk label and slice table; emitted `parsed_partitions` entries are transient.

## Dependencies And Integration Points

It depends on `check.h` and kernel integer/endian APIs. It integrates only with the generic partition parser framework.

## Risks And Edge Cases

Because this is a legacy format with fixed structs, layout and endian interpretation are the main risks. Bad checksum/magic should cause return `0`, while read failure returns `-1`. Slice starts and sizes are trusted after label validation.

## Test Signals

Tests should include invalid volume ids, invalid configuration/checksum, empty slices, maximum slices, and valid labels. Expected signals are no output for rejected labels and correctly emitted slice starts/sizes for accepted images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sysv68.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ultrix.c -->
# sources/distributed-fs/ceph-client/block/partitions/ultrix.c

## Purpose

`ultrix.c` parses Ultrix partition tables. It checks for Ultrix magic and validity flags in sector 0 and publishes the fixed set of partition entries.

## Important APIs, Types, And Functions

The entry point is `ultrix_partition(struct parsed_partitions *state)`. It defines `PT_MAGIC` and `PT_VALID`, uses local disklabel structures, and calls `read_part_sector()`, `put_partition()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0. If the magic or valid flag is absent, it returns `0`. For valid labels, it scans the table, skips zero-size entries, emits partitions up to `state->limit`, appends a newline, and returns `1`.

## State And Persistence Behavior

There is no long-lived state. The on-disk Ultrix table is persistent input, while `parsed_partitions` is the transient output of the scan.

## Dependencies And Integration Points

It depends on `check.h` and standard kernel integer helpers. It integrates through the block partition parser list.

## Risks And Edge Cases

The parser is intentionally simple and trusts the label once magic/valid checks pass. It does not do deep capacity validation. Read failures must release no invalid sectors and return `-1`.

## Test Signals

Tests should cover wrong magic, invalid flag, sparse entries, full entry count, and partition-table limits. Expected signals are return `0` for non-Ultrix disks and correct partition emission for valid labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ultrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/sed-opal.c -->
# sources/distributed-fs/ceph-client/block/sed-opal.c

## Purpose

`sed-opal.c` implements the kernel block-layer support for TCG Opal self-encrypting drives. It builds and parses Opal protocol packets, manages sessions, performs discovery, exposes privileged ioctl operations for ownership, locking ranges, passwords, MBR shadowing, revert, secure erase, SUM status, generic table I/O, and stack reset, and stores an optional SED authentication key in a kernel keyring.

## Important APIs, Types, And Functions

The exported lifecycle/API functions are `init_opal_dev()`, `free_opal_dev()`, `sed_ioctl()`, and `opal_unlock_from_suspend()`. `struct opal_dev` owns the transport callback, command/response buffers, COMID/session identifiers, geometry, flags, parsed response tokens, saved suspend unlock data, and `dev_lock`.

Protocol construction uses `cmd_start()`, `cmd_finalize()`, `finalize_and_send()`, `add_token_u8()`, `add_token_u64()`, `add_token_bytestring()`, `add_bytestring_header()`, and UID builders such as `build_locking_range()` and `build_locking_user()`. Response parsing uses `response_parse()`, `response_get_token()`, `response_get_string()`, `response_get_u64()`, `response_status()`, and `parse_and_check_status()`.

High-level operations are expressed as arrays of `struct opal_step` executed by `execute_steps()`, which automatically runs discovery first and closes a session on mid-sequence failure. Operation wrappers include `opal_take_ownership()`, `opal_activate_lsp()`, `opal_reactivate_lsp()`, `opal_setup_locking_range()`, `opal_lock_unlock()`, `opal_reverttper()`, `opal_revertlsp()`, `opal_set_new_pw()`, `opal_set_new_sid_pw()`, `opal_activate_user()`, `opal_secure_erase_locking_range()`, `opal_generic_read_write_table()`, `opal_get_status()`, `opal_get_geometry()`, and `opal_stack_reset()`.

## Control Flow

`init_opal_dev()` allocates the device state and two 2048-byte DMA-safe buffers, initializes the mutex/list, stores the transport callback, and calls `check_opal_support()`. Discovery sets COMID to the discovery COMID, receives a discovery0 page, validates feature descriptors, records locking/MBR/SUM flags and geometry, and stores the real COMID for later commands.

Every ioctl enters through `sed_ioctl()`, which requires `CAP_SYS_ADMIN`, a supported `opal_dev`, and copies input payloads with `memdup_user()` for commands with `IOC_IN`. It dispatches to the matching wrapper and copies output for status, geometry, discovery, LR status, and SUM status paths.

Most wrappers resolve keys through `opal_get_key()`, lock `dev_lock`, reset session scratch state with `setup_opal_dev()`, and execute an ordered command sequence. Session start functions authenticate as Anybody, SID, PSID, Admin1, or a locking-range user, then `start_opal_session_cont()` extracts host and TPer session numbers. Individual command builders modify Opal tables or invoke methods, and `end_opal_session()` clears session ids after a successful end-session response.

Suspend support stores selected unlock requests in `dev->unlk_lst` via `IOC_OPAL_SAVE`. `opal_unlock_from_suspend()` replays saved unlocks and optionally sets MBR Done on resume.

## State And Persistence Behavior

Kernel state persists for the lifetime of `struct opal_dev`: support flags, COMID, geometry, command buffers, saved suspend unlock list, and the SED keyring pointer. Session ids, parsed responses, and `prev_data` are transient per command sequence. `sed_opal_init()` creates `.sed_opal`, seeds it from `sed_read_key(OPAL_AUTH_KEY)`, and updates it after password changes with `update_sed_opal_key()`; it also attempts to write new keys to the platform key store with `sed_write_key()`.

Persistent device state lives inside the Opal drive: ownership PINs, LockingSP lifecycle, locking-range start/length/enabled/locked bits, generated active keys, MBR table contents, SUM configuration, and revert state. The kernel issues authenticated protocol commands to change that persistent state.

## Dependencies And Integration Points

The file depends on block device headers, `uapi/linux/sed-opal.h`, `linux/sed-opal.h`, `linux/sed-opal-key.h`, kernel keyrings, user-copy APIs, and local `opal_proto.h`. Its transport is supplied by the block driver through a `sec_send_recv` callback using `TCG_SECP_01` and `TCG_SECP_02`. User space reaches it through block ioctls.

## Risks And Edge Cases

This file handles privileged secrets and device-bricking operations. Key handling must avoid accepting empty or oversized keys, leaking copied keys, or using saved unlock keys for the wrong locking range. All user pointers in table read/write and discovery paths must be range-checked and copied safely.

Packet construction is bounded by `IO_BUFFER_LENGTH`; `can_add()`, `remaining_size()`, and finalize padding prevent buffer overruns, but every command builder must propagate `err`. Response parsing is bounded by header lengths and `MAX_TOKS`; responses with more tokens than expected are a risk because the token array is fixed-size and parser changes must preserve that bound.

Protocol state is subtle. Some controller methods terminate sessions themselves, while normal sequences must call `end_opal_session()`. `execute_steps()` only attempts session cleanup after a session-start step has plausibly run. Discovery feature flags must be refreshed because device lock state can change across commands and suspend/resume.

## Test Signals

Useful tests include devices with no Opal support, discovery pages for Opal v1/v2, invalid discovery lengths, all ioctl permission failures, included-key and keyring-key paths, lock/unlock RO/RW/LK transitions, SUM and non-SUM locking, setup range start/length, MBR enable/done/write, table read/write chunking, PSID/SID/Admin1 session failures, revert cleanup of saved unlocks, stack reset pending/failure/success, and suspend replay. Expected signals are correct errno propagation, no command buffer overflow, proper user-copy behavior, and serialized operations under `dev_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/sed-opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/t10-pi.c -->
# sources/distributed-fs/ceph-client/block/t10-pi.c

## Purpose

`t10-pi.c` generates, verifies, and remaps T10/NVMe protection information for block I/O integrity payloads. It supports CRC64 extended PI, T10 DIF CRC, and IP checksum formats, including guard tags, application tag escape handling, reference tag validation, and reference tag remapping when requests are mapped to device LBAs.

## Important APIs, Types, And Functions

The exported block-layer entry points are `bio_integrity_generate()`, `bio_integrity_verify()`, `blk_integrity_prepare()`, and `blk_integrity_complete()`. `struct blk_integrity_iter` carries the current bio, integrity payload, integrity profile, data/protection iterators, interval bytes remaining, seed/reference value, and running checksum.

Checksum helpers are `blk_calculate_guard()`, `blk_integrity_csum_finish()`, and `blk_integrity_csum_offset()`. Tuple access helpers are `blk_integrity_copy_from_tuple()`, `blk_integrity_copy_to_tuple()`, `blk_tuple_remap_begin()`, and `blk_tuple_remap_end()`. Verification/generation functions split by tuple type: `blk_verify_ext_pi()`, `blk_verify_pi()`, `blk_verify_t10_pi()`, `blk_verify_ip_pi()`, `blk_set_ext_pi()`, `blk_set_t10_pi()`, and `blk_set_ip_pi()`.

Reference remapping is handled by `__blk_reftag_remap()`, `blk_integrity_remap()`, `blk_reftag_remap_prepare()`, and `blk_reftag_remap_complete()`.

## Control Flow

`bio_integrity_generate()` and `bio_integrity_verify()` switch on `bi->csum_type` and call `blk_integrity_iterate()`. The iterator walks data bvecs, maps each segment locally, accumulates checksums over integrity intervals, and calls `blk_integrity_interval()` when an interval completes. That interval function accounts for metadata padding before the PI tuple, maps or copies the tuple even when split across protection bvecs, verifies or writes tuple fields, advances the seed, and resets checksum state.

Verify paths compare guard tags and, when `BLK_INTEGRITY_REF_TAG` is set, compare reference tags against the seed unless the app tag escape permits bypass. Generate paths write guard, app tag zero, and reference tag from the seed.

`blk_integrity_prepare()` remaps virtual reference tags to request/device reference tags before dispatch. `blk_integrity_complete()` remaps them back after completion for the completed byte count. Already mapped integrity payloads are marked with `BIP_MAPPED_INTEGRITY` to avoid double prepare.

## State And Persistence Behavior

There is no global state. Per-I/O state lives in bio/request integrity payloads and the stack-local iterator. The persistent data is the protection information stored alongside data on the device or in integrity buffers. Prepare/complete mutate reference tags in the bio integrity payload in place.

## Dependencies And Integration Points

The file depends on `linux/t10-pi.h`, `linux/blk-integrity.h`, CRC T10 DIF, CRC64 NVMe, networking checksum helpers, bvec mapping helpers, and block request helpers from `blk.h`. It integrates with bio integrity generation/verification and request mapping in the block layer.

## Risks And Edge Cases

Split protection tuples across bvecs are a key edge case; tuple copying must preserve iterator state and copy changes back only when needed. Metadata padding before `pi_offset` must be included in checksum calculations for formats that require it. Reference tag escape semantics differ for 32-bit T10 tuples and 48-bit extended PI. Remap paths must avoid double-mapping and must process only the completed intervals on completion.

Checksum endian handling differs by checksum type: T10 CRC uses big-endian guard storage, IP checksum uses host unaligned guard access, and CRC64 uses big-endian 64-bit guard plus 48-bit reference tags.

## Test Signals

Tests should cover successful generate/verify for all checksum types, guard mismatch, reference mismatch, app/ref escape cases, nonzero `pi_offset`, split tuples across protection bvecs, multi-bvec data intervals, remap prepare/complete for partial completions, `BIP_MAPPED_INTEGRITY`, and profiles without `BLK_INTEGRITY_REF_TAG`. Expected failure signal is `BLK_STS_PROTECTION` with diagnostic logging for guard/ref errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/t10-pi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Kconfig -->
# sources/distributed-fs/ceph-client/certs/Kconfig

## Purpose

`certs/Kconfig` defines kernel configuration options for module signing keys, system trusted keyrings, extra certificates, secondary trust, blacklists, revocation certificates, authenticated blacklist updates, and OpenSSL ML-DSA capability probing.

## Important APIs, Types, And Functions

This is Kconfig data, not C code. Important symbols are `MODULE_SIG_KEY`, `MODULE_SIG_KEY_TYPE_RSA`, `MODULE_SIG_KEY_TYPE_ECDSA`, `MODULE_SIG_KEY_TYPE_MLDSA_44`, `MODULE_SIG_KEY_TYPE_MLDSA_65`, `MODULE_SIG_KEY_TYPE_MLDSA_87`, `SYSTEM_TRUSTED_KEYRING`, `SYSTEM_TRUSTED_KEYS`, `SYSTEM_EXTRA_CERTIFICATE`, `SYSTEM_EXTRA_CERTIFICATE_SIZE`, `SECONDARY_TRUSTED_KEYRING`, `SECONDARY_TRUSTED_KEYRING_SIGNED_BY_BUILTIN`, `SYSTEM_BLACKLIST_KEYRING`, `SYSTEM_BLACKLIST_HASH_LIST`, `SYSTEM_REVOCATION_LIST`, `SYSTEM_REVOCATION_KEYS`, `SYSTEM_BLACKLIST_AUTH_UPDATE`, and `OPENSSL_SUPPORTS_ML_DSA`.

## Control Flow

Kconfig dependency resolution controls which certificate objects are built and which runtime keyring paths are compiled. Module signing key type selection is a `choice`. ML-DSA options depend on `OPENSSL_SUPPORTS_ML_DSA`, which probes the host OpenSSL binary. Secondary keyring and revocation options depend on the foundational trusted or blacklist keyrings.

## State And Persistence Behavior

The selected symbols persist in the kernel `.config` and determine build artifacts and runtime policy. They influence whether generated signing keys, compiled-in X.509 blobs, revocation lists, and runtime keyring write permissions exist.

## Dependencies And Integration Points

These options integrate with `certs/Makefile`, module signature code, IMA appraisal, asymmetric key parsing, PKCS#7 parsing, system data verification, and crypto algorithms such as ECDSA and ML-DSA.

## Risks And Edge Cases

Misconfigured `MODULE_SIG_KEY` can fail builds or omit intended trust anchors. Enabling secondary trust broadens the trust surface unless restrictions are understood. ML-DSA support depends on host toolchain capability. Authenticated blacklist updates require system data verification and must not allow unsigned deny-list changes.

## Test Signals

Test signals include `oldconfig` dependency behavior, builds with generated RSA/ECDSA/ML-DSA keys, PKCS#11 key URIs, empty and populated trusted/blacklist/revocation inputs, and expected object inclusion from `certs/Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Makefile -->
# sources/distributed-fs/ceph-client/certs/Makefile

## Purpose

`certs/Makefile` builds kernel certificate and blacklist artifacts. It compiles trusted keyring, blacklist, and revocation objects based on Kconfig, generates or extracts signing certificates, validates blacklist hash lists, embeds certificate lists, and builds the host `extract-cert` utility.

## Important APIs, Types, And Functions

Key build targets are `blacklist_hash_list`, `x509_certificate_list`, `signing_key.pem`, `x509.genkey`, `signing_key.x509`, and `x509_revocation_list`. Important commands are `cmd_check_and_copy_blacklist_hash_list`, `cmd_extract_certs`, `cmd_gen_key`, and `cmd_copy_x509_config`. The host program is `extract-cert`.

## Control Flow

Object inclusion follows `CONFIG_SYSTEM_TRUSTED_KEYRING`, `CONFIG_SYSTEM_BLACKLIST_KEYRING`, and `CONFIG_SYSTEM_REVOCATION_LIST`. The blacklist hash list is either generated as `NULL` or validated with the AWK checker and copied with a trailing `NULL`. Trusted certificate lists are produced by running `extract-cert` over configured PEM/PKCS#11 inputs. If the module signing key is the default path, the build generates a long-lived self-signed PEM key/cert using OpenSSL and the chosen key type.

## State And Persistence Behavior

The Makefile creates build-tree artifacts that are embedded into kernel objects by assembly files and C includes. Generated signing keys persist in the object tree unless removed. It does not mutate source files except through normal build outputs.

## Dependencies And Integration Points

It integrates with Kbuild variables, OpenSSL, `HOSTPKG_CONFIG`, `check-blacklist-hashes.awk`, `extract-cert.c`, `system_certificates.S`, `revocation_certificates.S`, and `blacklist_hashes.c`.

## Risks And Edge Cases

Build reproducibility and key secrecy matter. Auto-generated `signing_key.pem` must not be accidentally treated as a source-controlled production key. PKCS#11 URIs require special dependency filtering. Blacklist hash validation must run before C inclusion to avoid malformed source. ML-DSA key generation depends on host OpenSSL support.

## Test Signals

Tests should cover empty and populated certificate inputs, PKCS#11 input selection, generated key paths for each key type, invalid blacklist hashes failing the build, and object dependencies rebuilding when configured inputs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.c -->
# sources/distributed-fs/ceph-client/certs/blacklist.c

## Purpose

`blacklist.c` implements the system blacklist keyring used to reject blacklisted certificate hashes, binary hashes, and optional revocation certificates. It defines a custom `blacklist` key type whose description is the hash identifier and loads compiled-in blacklist material at boot.

## Important APIs, Types, And Functions

Exported functions include `mark_hash_blacklisted()`, `is_hash_blacklisted()`, and `is_binary_blacklisted()`. With revocation support, it also provides `add_key_to_revocation_list()` and `is_key_on_revocation_list()`. Key type operations are `blacklist_vet_description()`, `blacklist_key_instantiate()`, `blacklist_key_update()`, and `blacklist_describe()`.

Initialization is split between `blacklist_init()` as a `device_initcall()` and `load_revocation_certificate_list()` as a `late_initcall()` when configured.

## Control Flow

`blacklist_init()` registers the `blacklist` key type, allocates `.blacklist` with a link restriction that accepts only blacklist keys, then iterates `blacklist_hashes` to add built-in hash descriptions. Built-in hashes bypass PKCS#7 authentication by using `KEY_ALLOC_BUILT_IN`.

Runtime hash checks use `get_raw_hash()` to format binary hashes as `tbs:<hex>` or `bin:<hex>`, then search `.blacklist`. A match returns rejection. Authenticated userspace updates, when enabled, verify a PKCS#7 signature over the description against the builtin trusted keyring before instantiating a new blacklist key. Revocation certificates are stored as asymmetric keys in the same keyring and checked by validating PKCS#7 trust against `.blacklist`.

## State And Persistence Behavior

The persistent runtime state is the global `.blacklist` keyring and its keys. Built-in hashes and revocation certificates originate from build-time embedded data. Blacklist keys cannot be updated or removed through this type; additions are monotonic for the running kernel.

## Dependencies And Integration Points

The file depends on kernel keyrings, asymmetric keys, PKCS#7 verification, X.509 certificate loading, `blacklist.h`, and `keys/system_keyring.h`. It integrates with module signature verification and other callers that use exported blacklist checks.

## Risks And Edge Cases

Description validation is security-critical. It permits only `tbs:` or `bin:` prefixes, lowercase even-length hex, and at most 128 hex characters. Initialization panics on keyring/key-type allocation failure because silent blacklist absence would weaken signature enforcement. Authenticated update mode must ensure the payload signature covers the exact description.

## Test Signals

Tests should cover valid and invalid descriptions, duplicate built-in hashes, binary and X.509 TBS hash lookups, authenticated update success/failure, revocation certificate loading, PKCS#7 messages signed by revoked keys, and init failure injection. Expected rejection codes are `-EKEYREJECTED` for hash matches and `-EPERM` from `is_binary_blacklisted()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.h -->
# sources/distributed-fs/ceph-client/certs/blacklist.h

## Purpose

`blacklist.h` declares the build-time blacklist hash array used by `blacklist.c` and pulls in the hash type definitions needed by blacklist callers.

## Important APIs, Types, And Functions

It includes `linux/kernel.h`, `linux/errno.h`, and `crypto/pkcs7.h`. It declares `extern const char __initconst *const blacklist_hashes[];`. The relevant enum `blacklist_hash_type` is provided through included kernel headers for callers of blacklist functions.

## Control Flow

There is no control flow. `blacklist.c` iterates the `blacklist_hashes` array during `blacklist_init()`.

## State And Persistence Behavior

The declaration points to init-time constant data generated by `blacklist_hashes.c` and `blacklist_hash_list`. That data is used during initialization and can be discarded with init memory.

## Dependencies And Integration Points

The header integrates `blacklist.c` with `blacklist_hashes.c` and the generated build artifact. It is private to the certificate blacklist code.

## Risks And Edge Cases

The array must be NULL-terminated by the generated list. If the build artifact is malformed, initialization may read beyond intended entries; the Makefile and AWK checker are intended to prevent that.

## Test Signals

Build tests with empty and nonempty blacklist lists validate the declaration and generated definition. Runtime boot logs should show blacklist loading without invalid memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist_hashes.c -->
# sources/distributed-fs/ceph-client/certs/blacklist_hashes.c

## Purpose

`blacklist_hashes.c` defines the compiled-in blacklist hash array by including the generated `blacklist_hash_list` file.

## Important APIs, Types, And Functions

The sole symbol is `const char __initconst *const blacklist_hashes[]`. There are no functions. It includes `blacklist.h` and then includes the generated list inside the array initializer.

## Control Flow

Control flow occurs in `blacklist.c`, which iterates this array until `NULL`. This file only contributes data.

## State And Persistence Behavior

The data is `__initconst`, used during boot initialization and discardable afterward. The persistent source is the configured `CONFIG_SYSTEM_BLACKLIST_HASH_LIST` input in the build environment.

## Dependencies And Integration Points

It depends on the generated `blacklist_hash_list` header-like file produced by `certs/Makefile`. The Makefile adds `-I $(obj)` so the generated include is found from the object directory.

## Risks And Edge Cases

If `blacklist_hash_list` lacks a terminating `NULL` or contains invalid C strings, this file can break compilation or boot. The Makefile generates `NULL` for an empty config and validates populated lists with the AWK checker.

## Test Signals

Build with empty and populated hash list configurations. Inspect the preprocessed initializer or boot behavior to ensure all entries are loaded and duplicate entries are reported without fatal failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist_hashes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk -->
# sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk

## Purpose

`check-blacklist-hashes.awk` validates the configured blacklist hash list before it is included into C source. It enforces the string, prefix, lowercase hex, maximum length, and even-length rules described by Kconfig.

## Important APIs, Types, And Functions

This is an AWK script. It sets `RS = ","` so each comma-separated initializer item is validated independently. It uses `match()` to extract the quoted string, split prefix and hash, and check hex constraints.

## Control Flow

For each comma-separated item, the script requires a quoted string. The string must match `tbs:<hash>` or `bin:<hash>`. The hash must be lowercase hexadecimal, no longer than 128 characters, and have an even number of characters. On any violation, it prints a specific error message with item number and exits with status `1`.

## State And Persistence Behavior

The script holds only AWK variables while validating build input. It does not write output; the Makefile handles copying after validation succeeds.

## Dependencies And Integration Points

It is invoked by `cmd_check_and_copy_blacklist_hash_list` in `certs/Makefile`. Its output goes to stderr so build failures explain which item is invalid.

## Risks And Edge Cases

Because the record separator is a comma, embedded commas inside strings are not supported and would fail validation. Uppercase hex is intentionally rejected to match runtime `blacklist_vet_description()`. An empty hash is rejected because the hex match requires at least one digit.

## Test Signals

Tests should feed valid `tbs` and `bin` strings, unknown prefixes, unquoted input, uppercase hex, odd-length hashes, overlong hashes, empty hashes, and multiple comma-separated entries. Expected invalid cases exit nonzero with a diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/extract-cert.c -->
# sources/distributed-fs/ceph-client/certs/extract-cert.c

## Purpose

`extract-cert.c` is a host build utility that extracts X.509 certificates in DER form from PEM files or PKCS#11 URIs. Kbuild uses it to produce certificate blobs embedded into the kernel for trusted and revocation keyrings.

## Important APIs, Types, And Functions

The program entry point is `main()`. `write_cert()` writes one DER certificate to the output BIO and optionally logs its subject. `load_cert_pkcs11()` loads one certificate from a PKCS#11 URI using either OpenSSL 3 providers and `OSSL_STORE` or the legacy pkcs11 engine path. `format()` prints usage and exits.

Global state includes `wb`, `cert_dst`, `verbose`, and, for engine builds, `key_pass`.

## Control Flow

`main()` initializes OpenSSL, reads `KBUILD_VERBOSE` and optionally `KBUILD_SIGN_PIN`, validates two arguments, and handles three cases. Empty source creates an empty destination file. `pkcs11:` sources load one certificate with the provider/engine path and write it. Other sources are opened as PEM and read in a loop with `PEM_read_bio_X509()`, writing every certificate until a clean `PEM_R_NO_START_LINE` end condition after at least one write.

## State And Persistence Behavior

The utility persists DER output to the destination file and otherwise keeps only process-local OpenSSL/BIO state. It does not modify input PEM files or PKCS#11 tokens.

## Dependencies And Integration Points

It depends on libcrypto/OpenSSL, optional pkcs11 provider or engine APIs, and `scripts/ssl-common.h` for error handling. Kbuild compiles it as a host program and invokes it from `certs/Makefile`.

## Risks And Edge Cases

Host OpenSSL version changes select different PKCS#11 code paths. Missing pkcs11 support is a fatal error for PKCS#11 sources. PEM parsing treats an immediate failure as an error but a no-start-line after prior certificates as normal EOF. Output is opened lazily only when a certificate is written, except for empty input.

## Test Signals

Tests should cover empty source, single and multi-certificate PEM files, invalid PEM files, PKCS#11 provider/engine availability, PIN handling through `KBUILD_SIGN_PIN`, verbose logging, and output DER concatenation accepted by kernel X.509 loaders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/extract-cert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/revocation_certificates.S -->
# sources/distributed-fs/ceph-client/certs/revocation_certificates.S

## Purpose

`revocation_certificates.S` embeds the generated `certs/x509_revocation_list` binary blob into the kernel image and exports its start pointer and size for revocation-list loading.

## Important APIs, Types, And Functions

It defines global symbols `revocation_certificate_list` and `revocation_certificate_list_size`, with internal labels `__revocation_list_start` and `__revocation_list_end`. It uses `.incbin`, `.align`, and either `.quad` or `.long` depending on `CONFIG_64BIT`.

## Control Flow

There is no runtime control flow. The assembler emits init read-only data; `blacklist.c` later references the symbols when `CONFIG_SYSTEM_REVOCATION_LIST` is enabled.

## State And Persistence Behavior

The embedded bytes are `__INITRODATA`, loaded during boot and available to the revocation loader. The source of persistence is the build artifact generated from configured revocation certificates.

## Dependencies And Integration Points

It depends on `linux/export.h`, `linux/init.h`, and the generated file `certs/x509_revocation_list`. It integrates with `load_revocation_certificate_list()` in `blacklist.c`.

## Risks And Edge Cases

The generated file must exist when this object is built. Size symbol width must match architecture word size. Empty revocation lists should produce a zero size and be handled gracefully by the loader.

## Test Signals

Build with empty and populated `CONFIG_SYSTEM_REVOCATION_KEYS`, verify exported size, and confirm boot logs/load behavior for compiled-in revocation certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/revocation_certificates.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_certificates.S -->
# sources/distributed-fs/ceph-client/certs/system_certificates.S

## Purpose

`system_certificates.S` embeds module-signing and trusted X.509 certificate blobs into the kernel image and exposes their total size and module-certificate subset size. It can also reserve writable image space for an extra certificate.

## Important APIs, Types, And Functions

It defines `system_certificate_list`, `system_certificate_list_size`, `module_cert_size`, and internal labels around `certs/signing_key.x509` and `certs/x509_certificate_list`. With `CONFIG_SYSTEM_EXTRA_CERTIFICATE`, it also defines `system_extra_cert` and `system_extra_cert_used`.

## Control Flow

There is no executable control flow. The assembler concatenates the signing key certificate and additional trusted certificates. `system_keyring.c` later chooses whether to load all certificates or skip the module-cert subset depending on module-signature configuration.

## State And Persistence Behavior

The embedded certificate list is init read-only data. Optional `system_extra_cert` reserves zero-filled image space for post-build certificate insertion without recompilation.

## Dependencies And Integration Points

It depends on generated certificate list files from `certs/Makefile` and integrates with `load_system_certificate_list()` and `load_module_cert()` in `system_keyring.c`.

## Risks And Edge Cases

Ordering matters: module signing certificate bytes must be first so `module_cert_size` can identify the subset. Empty certificate inputs should still yield valid start/end symbols. Reserved extra certificate size must match the configured image patching workflow.

## Test Signals

Build with module signing enabled and disabled, with extra trusted keys, and with `SYSTEM_EXTRA_CERTIFICATE`. Verify symbol sizes and that runtime keyring loading reports the expected certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_certificates.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_keyring.c -->
# sources/distributed-fs/ceph-client/certs/system_keyring.c

## Purpose

`system_keyring.c` creates and populates the kernel trusted keyrings and provides PKCS#7 signature verification against builtin, secondary, machine, or platform trust roots. It is central to module signature checking and other system data verification paths.

## Important APIs, Types, And Functions

Restriction functions include `restrict_link_by_builtin_trusted()`, `restrict_link_by_digsig_builtin()`, `restrict_link_by_builtin_and_secondary_trusted()`, `restrict_link_by_digsig_builtin_and_secondary()`, and, with machine keyring support, `restrict_link_by_builtin_secondary_and_machine()`.

Initialization and loading functions are `system_trusted_keyring_init()`, `load_module_cert()`, `load_system_certificate_list()`, `add_to_secondary_keyring()`, `set_machine_trusted_keys()`, and `set_platform_trusted_keys()`. Verification APIs are `verify_pkcs7_message_sig()` and exported `verify_pkcs7_signature()`.

Global keyring pointers include `builtin_trusted_keys`, optional `secondary_trusted_keys`, optional `machine_trusted_keys`, and optional `platform_trusted_keys`.

## Control Flow

`system_trusted_keyring_init()` runs as a `device_initcall()`, allocates `.builtin_trusted_keys`, optionally allocates `.secondary_trusted_keys` with a restriction, and links builtin trust into secondary trust. `load_system_certificate_list()` runs later, selects the embedded certificate range, and loads certificates into the builtin keyring. `load_module_cert()` separately loads module certificates for IMA appraise-modsig when needed.

Restriction callbacks route key additions through signature verification against the configured trust root and optionally require digitalSignature usage. Secondary trust permits linking builtin and machine keyrings into the secondary ring so searches can traverse them.

`verify_pkcs7_signature()` parses raw PKCS#7, delegates to `verify_pkcs7_message_sig()`, then frees the message. Message verification supplies detached data, verifies PKCS#7 structure for the intended usage, rejects revoked signing keys via the revocation list, resolves the requested trust keyring, validates signer trust, and optionally exposes embedded content through a callback.

## State And Persistence Behavior

Trusted keyrings persist for the lifetime of the kernel. Certificates embedded by `system_certificates.S` are loaded during init. Secondary and machine/platform links persist after setup. There is no filesystem persistence here; trust state comes from compiled-in blobs and keyring additions allowed by restrictions.

## Dependencies And Integration Points

The file depends on kernel key management, asymmetric key type support, X.509 loading, PKCS#7 parsing/verification, revocation checks from blacklist code, and `keys/system_keyring.h`. Callers include module signature verification, firmware/system data verification, IMA, and integrity keyring setup.

## Risks And Edge Cases

Trust routing must match caller intent. `VERIFY_USE_SECONDARY_KEYRING` falls back to builtin if secondary is absent; platform trust returns `-ENOKEY` if unavailable. Revocation checks must happen before trust success is accepted. Keyring allocation failures panic because missing trust roots break core security assumptions. Secondary keyring policy can broaden trust if machine keyrings are linked without appropriate constraints.

## Test Signals

Tests should cover boot allocation/loading of builtin and secondary keyrings, valid and invalid certificate chains, digitalSignature usage restrictions, machine/platform keyring selection, revoked PKCS#7 signers, detached-data mismatch, embedded-content callback handling, absent secondary/platform keyrings, and exported verification return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/system_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/842.c -->
# sources/distributed-fs/ceph-client/crypto/842.c

## Purpose

`crypto/842.c` registers the software 842 compression algorithm with the Linux crypto scomp API. It adapts the generic `lib/842` software compressor/decompressor into the crypto framework under the names `842` and `842-generic`.

## Important APIs, Types, And Functions

Context management is implemented by `crypto842_alloc_ctx()` and `crypto842_free_ctx()`. Compression and decompression callbacks are `crypto842_scompress()` and `crypto842_sdecompress()`, which call `sw842_compress()` and `sw842_decompress()`. The `scomp_alg scomp` structure advertises the algorithm and stream callbacks. Module entry/exit are `crypto842_mod_init()` and `crypto842_mod_exit()`.

## Control Flow

Module initialization registers the `scomp` algorithm with `crypto_register_scomp()`. Callers allocate a compression context of `SW842_MEM_COMPRESS` bytes for compression streams, compress or decompress through the callbacks, and free the context. Module exit unregisters the algorithm.

## State And Persistence Behavior

There is no persistent data beyond crypto algorithm registration. Compression contexts are per-stream heap allocations. Compressed data format persistence is defined by the 842 format and the `sw842` library, not this adapter.

## Dependencies And Integration Points

It depends on `crypto/internal/scompress.h`, `linux/sw842.h`, module infrastructure, and the software 842 library. Crypto API consumers select the algorithm by `842` or `842-generic`; hardware 842 acceleration lives elsewhere and can have different priority.

## Risks And Edge Cases

The software implementation is intentionally slow and should not be assumed competitive with hardware 842. Allocation failure returns `ERR_PTR(-ENOMEM)`. Compression requires a valid scratch context; decompression does not use it. Output length pointers are owned by the crypto API caller and must be honored by the `sw842` routines.

## Test Signals

Tests should load/unload the module, allocate scomp transforms by both aliases, round-trip known 842 data, handle too-small destination buffers, inject context allocation failure, and compare behavior with hardware 842 when present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/842.c -->
