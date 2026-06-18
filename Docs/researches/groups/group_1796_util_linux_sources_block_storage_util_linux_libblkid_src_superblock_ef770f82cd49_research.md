# Group Research: group_1796_util_linux_sources_block_storage_util_linux_libblkid_src_superblock_ef770f82cd49

Scope: subset A from `Docs/research_subset_a.md`, covering the listed util-linux `libblkid` superblock/topology/tag/version files and `libmount` build/Python binding files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/nilfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/nilfs.c

## Scope

Implements NILFS2 filesystem probing for libblkid.

## Behavior

- Defines the packed NILFS superblock layout and primary/backup offsets.
- `nilfs_valid_sb()` validates magic, backup device size on whole-disk probes, superblock byte length, and CRC over the checksum-excluded region.
- `probe_nilfs2()` reads the primary superblock at `0x400` and backup near the end of the device, tolerating backup read errors when the primary is valid.
- Selects the newer valid superblock by checkpoint number, then exports label, UUID, revision, magic location, filesystem block size, and block size.

## Dependencies And Risks

- Uses `blkid_probe_get_buffer()`, checksum verification, endian helpers, and result setters from the superblock framework.
- Block-size shifts above 6 are ignored to avoid overflow and to match kernel NILFS limits.
- Backup probing depends on `pr->size`; invalid or tiny media can make only the primary usable.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ntfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ntfs.c

## Scope

Implements NTFS detection, validation, label extraction, UUID formatting, and the internal `blkid_probe_is_ntfs()` helper.

## Behavior

- Defines NTFS boot sector/BPB, MFT record, and resident attribute layouts.
- `__probe_ntfs()` validates sector size, cluster encoding, maximum cluster size, required-zero BPB fields, MFT record size encoding, MFT cluster bounds, and the first MFT record magic.
- Reads `$Volume` MFT record and scans resident attributes for `MFT_RECORD_ATTR_VOLUME_NAME`, converting UTF-16LE label to UTF-8.
- Exports filesystem block size, logical sector block size, filesystem size, and volume serial UUID.
- `blkid_probe_is_ntfs()` runs the same validations without saving label/UUID, for collision checks elsewhere.

## Dependencies And Risks

- Relies on safe buffer reads at calculated MFT offsets and guarded attribute length/offset checks.
- Rejects plausible-looking boot sectors unless the MFT can be read and starts with `FILE`.
- MFT size arithmetic must remain bounded because it controls direct device reads.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/nvidia_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/nvidia_raid.c

## Scope

Detects NVIDIA RAID member metadata.

## Behavior

- Reads a fixed-size metadata block two sectors from the end of a whole disk or regular file.
- Validates vendor signature, metadata size, and additive checksum.
- Exports RAID member version and records the signature as the magic.

## Dependencies And Risks

- Skips partitions/non-whole-disk block devices to avoid false positives.
- Depends on `pr->size` sector arithmetic; minimum size is enforced by idinfo.
- Checksum count is bounded by the buffer size before iteration.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/nvidia_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ocfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ocfs.c

## Scope

Implements probes for OCFS1/NTOCFS, OCFS2, and Oracle ASM disk labels.

## Behavior

- OCFS reads volume header and label structures at the magic offset and plus 512 bytes.
- Exports secondary type (`ocfs1` or `ntocfs`), label, mount name, UUID, and major/minor version.
- OCFS2 reads the superblock, exports label, UUID, version, and block size from `s_blocksize_bits`.
- Oracle ASM exports `dl_id` as the label when `ORCLDISK` is found.

## Dependencies And Risks

- Length fields for OCFS label and mount are checked against fixed array sizes before export.
- OCFS2 block-size shift is guarded below 32 to avoid invalid shifts.
- The three idinfos share one file but represent distinct libblkid signatures and usages.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ocfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/promise_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/promise_raid.c

## Scope

Detects Promise FastTrak RAID member metadata.

## Behavior

- Scans a fixed list of historical sector offsets from the end of the device.
- Requires whole-disk or regular-file probing.
- Matches the `Promise Technology, Inc.` signature and records it as the magic.

## Dependencies And Risks

- Stops when the device has fewer sectors than the next candidate offset.
- No checksum is available, so the offset list and whole-disk restriction are the main false-positive controls.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/promise_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/refs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/refs.c

## Scope

Declares static libblkid detection metadata for Microsoft ReFS.

## Behavior

- Registers filesystem name `ReFS`.
- Uses an 8-byte magic containing leading NULs and `ReFS`.

## Dependencies And Risks

- No probefunc exists, so detection depends entirely on the magic table.
- It exports only type/usage/magic-level information, not label, UUID, size, or block size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/refs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/reiserfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/reiserfs.c

## Scope

Implements ReiserFS v3 and Reiser4 filesystem probing.

## Behavior

- ReiserFS validates minimum block size and rejects superblocks that appear inside the journal.
- Exports label/UUID only for newer v3.6/JR signatures, and sets version `3.5`, `3.6`, or `JR`.
- Reiser4 reads its own layout, derives block size from a 256-byte multiplier, validates minimum 512 bytes, and exports label, UUID, and version `4`.
- Both set filesystem block size and block size.

## Dependencies And Risks

- Multiple ReiserFS magic offsets cover legacy layouts.
- Journal-position validation prevents accidental matches on journal copies.
- Reiser4’s compact block-size encoding is trusted after the minimum guard.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/reiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/romfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/romfs.c

## Scope

Implements ROMFS probing.

## Behavior

- Reads the ROMFS superblock and verifies a big-endian additive checksum over up to 512 bytes, capped by the filesystem full size.
- Exports nonempty volume name, filesystem size, filesystem block size, and block size.
- Uses static magic `-rom1fs-`.

## Dependencies And Risks

- Checksum length must be 32-bit aligned.
- Failure to read the checksum-covered buffer is treated as a failed validation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/romfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/scoutfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/scoutfs.c

## Scope

Implements ScoutFS data-device and metadata-device probing.

## Behavior

- Reads a fixed 4 KiB ScoutFS superblock block and verifies CRC32C excluding the stored CRC field.
- Exports format version, UUID, FSID, and a wipe range.
- Differentiates `scoutfs_meta` and `scoutfs_data` via magic hint and `SCOUTFS_FLAG_IS_META_BDEV`.
- Sets 64 KiB block size for metadata devices and 4 KiB for data devices.

## Dependencies And Risks

- Both device types use identical magic and layout, so flag validation is required to classify correctly.
- CRC validation must pass before metadata is exported.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/scoutfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/silicon_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/silicon_raid.c

## Scope

Detects Silicon Medley RAID member metadata.

## Behavior

- Reads the final sector of a whole disk or regular file into the packed Silicon metadata layout.
- Validates magic, disk number range, and a 16-bit checksum over words before `checksum1`.
- Exports major/minor version and records the magic field offset.

## Dependencies And Risks

- Uses `memcpy()` when reading packed 16-bit fields to avoid unaligned accesses.
- Whole-disk restriction and checksum reduce false positives for end-of-disk signatures.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/silicon_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/squashfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/squashfs.c

## Scope

Implements SquashFS v4+ and SquashFS v3 probing.

## Behavior

- SquashFS v4+ uses little-endian `hsqs`, rejects versions below 4, and exports version, block size, and bytes used as filesystem size.
- SquashFS3 handles both big-endian `sqsh` and little-endian `hsqs`, rejects versions above 3, and exports version, 1024-byte block size, and endianness.
- Registers separate idinfos: `squashfs` and `squashfs3`.

## Dependencies And Risks

- Version split is necessary because `hsqs` can identify both old and new little-endian formats.
- The v3 path does not export filesystem size from this shared structure.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/squashfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/stratis.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/stratis.c

## Scope

Detects Stratis block device metadata.

## Behavior

- Reads the first 16 sectors and checks two possible superblock copies at sectors 1 and 9.
- Validates CRC32C over the 512-byte superblock sector, excluding the stored CRC.
- Converts hyphenless 32-byte ASCII UUIDs into canonical UUID strings for device UUID and `POOL_UUID`.
- Exports block device sector count and initialization time.

## Dependencies And Risks

- Magic table covers both copy locations, but the probefunc independently validates CRC and chooses the first valid copy.
- UUID formatting assumes Stratis stores ASCII UUID hex without hyphens.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/stratis.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.c

## Scope

Implements the central libblkid superblock probing chain, supported idinfo ordering, safe-probe ambiguity handling, filters, and superblock result setters.

## Behavior

- Defines ordered `idinfos[]`: OPAL/LUKS and RAID/container formats first, then filesystems, with comments and ordering used to avoid unsafe reads and misclassification.
- `superblocks_probe()` iterates idinfos, applies filters, minimum size checks, CD/floppy exclusions, magic matching, optional probefunc validation, then exports `TYPE`, `USAGE`, and `SBMAGIC`.
- `superblocks_safeprobe()` repeatedly probes to detect multiple matches, returns the first tiny-device result, stops at RAID/crypto, and reports `BLKID_PROBE_AMBIGUOUS` when multiple intolerant filesystem signatures exist.
- Public APIs enable/disable superblock probing, configure flags, reset/invert filters, filter by type or usage, enumerate known names, and test known filesystems.
- Setter helpers gate exported fields by flags: version, usage, label/raw label, UUID/raw UUID, size, last block, fs block size, minimal block size, and endianness.

## Dependencies And Risks

- Correct idinfo ordering is a core invariant; moving probes can change collision behavior.
- Probe functions must clear partial values on failed validation, which this driver does via chain reset.
- Safe probing intentionally does not search past the first RAID/crypto result for filesystem collisions.
- Label/UUID setters trim whitespace and suppress empty values, while raw variants preserve original data when requested.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.h -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.h

## Scope

Declares superblock idinfo symbols, endianness helpers, and superblock result setter APIs.

## Behavior

- Defines `enum blkid_endianness` and native/other endian macros from compiler byte order.
- Declares all filesystem, RAID, crypto, and other superblock `blkid_idinfo` objects used by `superblocks.c`.
- Declares APIs for setting version, labels, UUIDs, block sizes, filesystem size, last block, and endianness.
- Declares collision helpers `blkid_probe_is_bitlocker()` and `blkid_probe_is_ntfs()`.
- Provides `blkid32_to_cpu()` for value conversion using a runtime endian tag.

## Dependencies And Risks

- Header is shared by all superblock probers, so declarations must stay synchronized with per-format files.
- `blkid32_to_cpu()` aborts on invalid enum values, making caller-controlled endianness validation important.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/swap.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/swap.c

## Scope

Implements Linux swap and suspend-image probing.

## Behavior

- Supports swap v0 (`SWAP-SPACE`), swap v1 (`SWAPSPACE2`), and suspend signatures including TuxOnIce and kernel hibernation variants.
- Rejects normal swap detection when TuxOnIce magic is present at the beginning of the device.
- For swap v1, validates version in either endian and nonzero last page, exports endianness, page-sized fs block size, filesystem size, and last block.
- Exports label and UUID when padding sanity suggests the v1 header region is valid.
- Registers signature offsets for several possible page sizes.

## Dependencies And Risks

- Page size is inferred from signature offset plus signature length.
- Endianness is derived from the version field.
- Suspend probing reuses swap header metadata but exports suspend-specific versions.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/sysv.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/sysv.c

## Scope

Implements Xenix and System V filesystem probing.

## Behavior

- Xenix uses static magic at known offsets and exports the short filesystem name as label.
- SysV manually probes four possible superblock positions and accepts either little-endian or big-endian magic.
- On SysV match, exports label and records the exact magic offset.

## Dependencies And Risks

- SysV uses `BLKID_NONE_MAGIC` because the offset/endian combinations are easier to express in code.
- Coherent FS is intentionally not probed because it lacks a reliable magic string.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/sysv.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ubi.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ubi.c

## Scope

Detects UBI erase counter headers.

## Behavior

- Reads `UBI#` erase counter header.
- Verifies header CRC over all bytes before `hdr_crc`.
- Exports UBI version and formats `image_seq` as UUID.

## Dependencies And Risks

- Uses big-endian fields for CRC and image sequence.
- Classified as RAID usage in libblkid because UBI is a volume/container layer rather than a regular filesystem.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ubi.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ubifs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ubifs.c

## Scope

Implements UBIFS filesystem probing.

## Behavior

- Defines UBIFS common header and superblock node structures.
- Verifies CRC32 over the superblock node starting at `sqnum`, matching UBIFS node checksum rules.
- Exports UUID, version as `w<fmt_version>r<ro_compat_version>`, and filesystem size as `leb_size * leb_cnt`.

## Dependencies And Risks

- Magic is little-endian byte sequence for UBIFS node magic.
- The packed 4 KiB superblock node is read as a complete structure before CRC validation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ubifs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/udf.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/udf.c

## Scope

Implements UDF probing, descriptor scanning, label/UUID/version extraction, and metadata identifier export.

## Behavior

- Scans Volume Structure Descriptors at session offset using sector size and candidate UDF block sizes.
- Looks for NSR descriptors, then validates Anchor Volume Descriptor Pointer at block 256 or 512.
- Walks the volume descriptor sequence, capped to 64 descriptors, and confirms real UDF via `*OSTA UDF Compliant` domain ID.
- Extracts volume ID, logical volume ID as primary label, volume set ID, generated UUID from volume set ID, application ID, and publisher ID from relevant descriptors.
- Reads Logical Volume Integrity Descriptor implementation-use data to refine UDF revision.
- Exports version, filesystem block size, and block size.

## Dependencies And Risks

- The idinfo is tolerant because initial magics are generic ECMA-167/ISO-13346 descriptors, not uniquely UDF.
- Descriptor string conversion depends on OSTA compressed Unicode CID mapping to Latin-1 or UTF-16BE.
- Descriptor sequence and LVID traversal are intentionally bounded to avoid crafted-media scanning costs.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/udf.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ufs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ufs.c

## Scope

Implements UFS/UFS2 probing across multiple historic superblock locations and endiannesses.

## Behavior

- Scans offsets 0, 8, 64, and 256 KiB for known UFS magic values in both endian forms.
- Classifies UFS2 vs UFS1, exports UFS2 volume name, and formats UUID from `fs_id` when present.
- Records the magic offset and exports fragment size as filesystem block size/block size.
- Exports filesystem endianness.

## Dependencies And Risks

- Uses manual scanning instead of a large static magic table.
- The detected magic/endian controls all later field interpretation.
- UFS variants share a large packed structure with unions for vendor/version-specific fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ufs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vdo.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vdo.c

## Scope

Detects VDO metadata.

## Behavior

- Reads a minimal VDO superblock with magic `dmvdo001`.
- Exports the VDO superblock UUID.
- Registers usage as `BLKID_USAGE_OTHER`.

## Dependencies And Risks

- No additional geometry or checksum validation is implemented in this file.
- The structure intentionally models only fields needed by libblkid.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vdo.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vfat.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vfat.c

## Scope

Implements FAT12/FAT16/FAT32 probing and the internal `blkid_probe_is_vfat()` helper.

## Behavior

- Defines FAT boot sector variants, directory entries, and FAT32 FSInfo layout.
- `fat_valid_superblock()` validates boot signature when needed, rejects JFS/HPFS pseudo-headers, checks FAT count, reserved sectors, media byte, cluster power-of-two, sector size, cluster count, and BitLocker collision.
- FAT12/16 probing searches the fixed root directory for a volume-label entry, exports boot label, serial UUID, `SEC_TYPE=msdos`, and FAT version.
- FAT32 probing walks the root directory cluster chain, bounded by `maxloop`, and validates FSInfo signatures when present.
- Exports label, FAT boot label, UUID, version, filesystem block size, sector block size, and filesystem size.

## Dependencies And Risks

- Ambiguous boot-sector magics require strong BPB validation to avoid false positives.
- FAT32 root traversal reads FAT entries from calculated offsets and is bounded to prevent runaway loops.
- `blkid_probe_is_vfat()` shares validation logic for partition-table collision handling.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vfat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/via_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/via_raid.c

## Scope

Detects VIA RAID member metadata.

## Behavior

- Reads metadata from the final sector of whole disks or regular files.
- Validates signature `0xAA55`, version <= 2, and 8-bit checksum over the first 50 bytes.
- Exports version and records the signature as magic.

## Dependencies And Risks

- No probing of partitions is allowed.
- The checksum includes the stored checksum byte behavior as defined by VIA metadata expectations.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/via_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vmfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vmfs.c

## Scope

Implements VMware VMFS filesystem and VMFS volume-member probing.

## Behavior

- VMFS filesystem probe exports byte-reordered UUID, label, and version.
- VMFS volume member probe exports `UUID_SUB`, version, and optionally reads an LVM UUID from a fixed offset inside the volume-info area.
- Registers separate idinfos for `VMFS` filesystem usage and `VMFS_volume_member` RAID usage.

## Dependencies And Risks

- UUID formatting uses VMFS-specific byte ordering.
- Optional LVM UUID extraction silently skips if the secondary buffer cannot be read.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vmfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vxfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vxfs.c

## Scope

Implements Veritas VxFS probing.

## Behavior

- Supports little-endian and big-endian magics at different offsets.
- Uses the magic hint to convert version and block size.
- Exports version, filesystem block size, block size, and endianness.

## Dependencies And Risks

- Correctness depends on the idinfo hint matching the magic byte order.
- No label or UUID extraction is implemented.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/vxfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/xfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/xfs.c

## Scope

Implements XFS filesystem probing and XFS external log detection.

## Behavior

- Defines the XFS superblock, converts big-endian disk fields into a CPU-order copy, and validates geometry beyond the `XFSB` magic.
- Checks sector size, block size, inode size, logs, realtime extent size, allocation group limits, inode percent, and total data blocks.
- For v5 superblocks, verifies required feature bits and CRC32C excluding the checksum field.
- Exports label, UUID, filesystem size excluding internal log blocks, last block count, filesystem block size, and sector block size.
- External log probing scans the first 256 KiB by 512-byte sectors, rejects regular XFS superblocks, validates log record headers, and exports `LOGUUID`.

## Dependencies And Risks

- XFS validation intentionally avoids trusting magic alone.
- External log detection requires minimum size and validates log format/version/body length.
- Filesystem size calculation depends on internal-vs-external log interpretation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/xfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/zfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/zfs.c

## Scope

Implements ZFS vdev label detection and nvlist metadata extraction.

## Behavior

- Computes the four ZFS label locations, skipping whole-disk label areas covered by partitions.
- Reads the nvpair area, validates XDR encoding, endian marker, and nonzero first nvpair size.
- Parses nested nvlists with bounds checks, first finding a plausible label by `guid`, `state`, and `txg`.
- Extracts pool label (`name`), device GUID as `UUID_SUB`, pool GUID as `UUID`, `ashift` block size, and version.
- Records the nvlist header as magic and exports native/other endianness.

## Dependencies And Risks

- Uses unaligned-safe big-endian reads for nvlist fields.
- Parser bounds checks name/value sizes and directory nesting, but only supports the needed scalar/string/directory types.
- Minimum device size is 64 MiB; labels on partition-covered areas are skipped for whole-disk probing.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/zonefs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/zonefs.c

## Scope

Implements zonefs filesystem probing.

## Behavior

- Reads the 4 KiB zonefs superblock at offset 0.
- Verifies CRC32 excluding the stored CRC field.
- Exports label, UUID, filesystem block size, and block size as 4096 bytes.

## Dependencies And Risks

- All superblock fields are little-endian.
- CRC validation is required despite the magic table also matching `SFOZ`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/zonefs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/tag.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/tag.c

## Scope

Implements libblkid cache/device tag allocation, mutation, parsing, iteration, and lookup by tag.

## Behavior

- Tags are linked both on the owning device (`bit_tags`) and under a cache-level head for the tag name (`bit_names`).
- `blkid_set_tag()` adds, updates, or deletes tags, keeps common direct device fields (`TYPE`, `LABEL`, `UUID`) synchronized, and marks the cache changed.
- `blkid_parse_tag_string()` parses `NAME=value` tokens with simple quote stripping.
- Public tag iteration wraps internal list traversal behind `blkid_tag_iterate_*`.
- `blkid_find_dev_with_tag()` searches the cache by type/value, prefers highest device priority, verifies stale entries, and triggers new/all probing if needed.

## Dependencies And Risks

- List membership is central; freeing a tag removes both list links.
- Direct device fields point at tag value allocations, so update/delete lifetime must stay coordinated.
- Lookup may mutate cache state through verification and probing retries.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/tag.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/dm.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/dm.c

## Scope

Provides legacy device-mapper topology probing via `dmsetup`.

## Behavior

- Detects device-mapper devices by major number/driver name.
- Finds `dmsetup` in standard sbin paths, forks it as `dmsetup table -j <maj> -m <min>`, and parses striped table output.
- Exports minimum I/O size as stripe size and optimal I/O size as stripe width.

## Dependencies And Risks

- Used as a fallback for systems lacking sysfs topology.
- Drops permissions before executing external helper.
- Only recognizes the simple `striped` table format parsed by `fscanf()`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/dm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/evms.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/evms.c

## Scope

Provides legacy EVMS topology probing.

## Behavior

- Detects EVMS devices by major number or driver name.
- Uses `EVMS_GET_STRIPE_INFO` ioctl to obtain stripe unit and width.
- Exports minimum I/O size and optimal I/O size in bytes.

## Dependencies And Risks

- Linux-specific fallback for old systems.
- Returns no topology for non-EVMS devices or ioctl failure.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/evms.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/ioctl.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/ioctl.c

## Scope

Provides generic Linux block topology probing through ioctls.

## Behavior

- Reads alignment offset, minimum I/O size, optimal I/O size, physical block size, and disk sequence number.
- Exports values through topology setter APIs.
- Fails the probe if any required ioctl in the sequence is unavailable.

## Dependencies And Risks

- Requires a block-device fd supporting modern topology ioctls.
- Since all ioctls are chained, partial availability does not produce a successful result from this driver.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/lvm.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/lvm.c

## Scope

Provides legacy LVM topology probing via `lvdisplay`.

## Behavior

- Detects LVM devices by major number or driver name.
- Resolves the device name, forks `lvdisplay`, and parses `Stripes` and `Stripe size (KByte)` lines.
- Exports minimum I/O size and optimal I/O size in bytes.

## Dependencies And Risks

- Used only as fallback for old systems.
- Runs an external helper after dropping permissions.
- Produces no result for non-striped volumes or missing helper output.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/md.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/md.c

## Scope

Provides Linux md RAID topology probing through md ioctls.

## Behavior

- Detects md devices by major number or driver name.
- Opens the whole disk if the probed device is a partition.
- Uses `GET_ARRAY_INFO` to read RAID level, chunk size, and disk counts.
- Adjusts effective data-disk count for RAID4/5/6 parity and exports minimum/optimal I/O sizes.

## Dependencies And Risks

- Ignores RAID levels that should not be stripe-aligned.
- Must close any auxiliary whole-disk fd.
- Optimal I/O size calculation depends on correct parity-disk deduction.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/md.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/sysfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/sysfs.c

## Scope

Provides primary Linux topology probing through `/sys/dev/block`.

## Behavior

- Reads sysfs attributes for alignment offset, minimum I/O size, optimal I/O size, physical block size, DAX, and disk sequence.
- For partitions, falls back to parent whole-disk attributes through the sysfs path context.
- Counts successfully exported values and returns success if any topology value was set.

## Dependencies And Risks

- Preferred topology source on modern Linux.
- Depends on util-linux sysfs path helpers and kernel ABI attribute names.
- Setter functions ignore zero values, so successful reads of zero may not count as exported topology.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/topology.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/topology.c

## Scope

Implements the libblkid topology probing chain, binary topology object, public topology APIs, and result setters/getters.

## Behavior

- Registers Linux topology probers in order: sysfs, ioctl, md, dm, lvm, evms.
- `topology_probe()` only works on block devices, resets binary/tag state, runs drivers until minimum I/O size is available, then adds logical sector size.
- Supports both NAME=value output and binary `blkid_topology` data.
- Setter helpers suppress zero values and write either probe values or struct fields.
- Public getters expose alignment offset, minimum/optimal I/O size, logical/physical sector size, DAX, and disk sequence.

## Dependencies And Risks

- Completeness is defined by `MINIMUM_IO_SIZE`; drivers that cannot provide it are skipped.
- Kernel `-1` alignment offset is hidden as zero.
- Binary topology data is overwritten on the next topology retrieval for the same probe.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/topology.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/topology.h -->
# File Research: sources/block-storage/util-linux/libblkid/src/topology/topology.h

## Scope

Declares internal topology setter APIs and Linux topology idinfo symbols.

## Behavior

- Exposes setters for alignment, minimum/optimal I/O size, physical sector size, DAX, and disk sequence.
- Declares ioctl, md, evms, sysfs, dm, and lvm topology probers under `__linux__`.

## Dependencies And Risks

- Internal header couples topology drivers to `topology.c` setter semantics.
- Non-Linux builds see no topology prober declarations.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/topology/topology.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/verify.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/verify.c

## Scope

Implements cache entry verification against current block-device state.

## Behavior

- `blkid_verify()` checks stat timestamps and a minimum re-probe interval to avoid unnecessary probing.
- Returns unverified cached data on permission/not-found access failures, but removes entries on other stat/open failures.
- Skips private device-mapper nodes.
- Reuses a cache-level probe to run safe superblock and partition probing, clears old tags, then repopulates current tags.
- Converts `PART_ENTRY_UUID`/`PART_ENTRY_NAME` into `PARTUUID`/`PARTLABEL` and suppresses auxiliary `_ID` tags from cache tags.

## Dependencies And Risks

- Mutates cache and device tag state during verification.
- Requires careful fd reset and filter reset after probing.
- Timestamp logic differs depending on nanosecond stat support.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/verify.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/version.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/version.c

## Scope

Implements libblkid runtime version reporting.

## Behavior

- Stores `LIBBLKID_VERSION` and `LIBBLKID_DATE` from headers.
- `blkid_parse_version_string()` collapses dotted numeric version strings into an integer until the first non-digit/non-dot.
- `blkid_get_library_version()` optionally returns version/date strings and always returns parsed version code.

## Dependencies And Risks

- Version code parsing ignores dots and stops at suffixes, matching legacy blkid behavior.
- Release version is not the SONAME version.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/version.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/Makemodule.am -->
# File Research: sources/block-storage/util-linux/libmount/Makemodule.am

## Scope

Autotools top-level inclusion file for libmount.

## Behavior

- Gates all libmount build content behind `BUILD_LIBMOUNT`.
- Includes source, Python, and samples module makefiles.
- Adds docs subdirectory when GTK-Doc is enabled.
- Installs `libmount/mount.pc`, tracks it as a generated path file, and distributes COPYING.

## Dependencies And Risks

- This file only wires sub-builds; actual source lists live in included makefiles.
- Python bindings are included only if their own nested conditions enable them.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/meson.build -->
# File Research: sources/block-storage/util-linux/libmount/meson.build

## Scope

Meson build definition for libmount, its generated public header, libraries, pkg-config metadata, tests, and Python subdirectory.

## Behavior

- Disables libmount dependencies and exits when `build_libmount` is false.
- Generates `libmount.h` with version macros.
- Defines core source list and adds Linux-only context/hook/monitor sources when building on Linux.
- Builds internal static `_mount`, static `mount_static`, and shared `mount` libraries with blkid/common dependencies.
- Applies linker version script when supported.
- Generates pkg-config metadata and Meson dependency override.
- Builds test executables when `program_tests` is enabled and symlinks them into the project build root.
- Enters `libmount/python`.

## Dependencies And Risks

- Requires either `dirfd` or `ddfd` when libmount is built.
- Optional dependencies include SELinux, cryptsetup/dlopen, realtime libs, systemd/udev support, and btrfs.
- Linux-only sources define most context and mount/umount behavior.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/mount.pc.in -->
# File Research: sources/block-storage/util-linux/libmount/mount.pc.in

## Scope

Pkg-config template for libmount.

## Behavior

- Defines prefix, exec prefix, libdir, and includedir substitutions.
- Publishes package name `mount`, description, version, Cflags, public libs, private requirements, and private dl libs.
- Requires private blkid, SELinux, and cryptsetup substitutions as configured.

## Dependencies And Risks

- Consumers get `-I${includedir}/libmount` and `-lmount`.
- Static/private linking depends on correct substitution of `@LIBSELINUX@`, `@LIBCRYPTSETUP@`, and `@LIBDL@`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/mount.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/Makemodule.am -->
# File Research: sources/block-storage/util-linux/libmount/python/Makemodule.am

## Scope

Autotools build definition for pylibmount.

## Behavior

- Gated by `BUILD_PYLIBMOUNT`.
- Installs the binary module and `__init__.py` into `$(pyexecdir)/libmount` so architecture-specific binary and Python files stay together.
- Builds `pylibmount.la` from shared Python binding sources and adds `context.c` only on Linux.
- Links against `libmount.la` and Python libraries.
- Adds Python binding tests to `dist_check_SCRIPTS`.

## Dependencies And Risks

- Uses `-avoid-version -module -shared -export-dynamic` for Python extension semantics.
- Linux gating controls whether context mount/umount APIs are available.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/__init__.py -->
# File Research: sources/block-storage/util-linux/libmount/python/__init__.py

## Scope

Python package initializer for libmount bindings.

## Behavior

- Imports all public symbols from the compiled `.pylibmount` extension module.

## Dependencies And Risks

- Package usability depends on the extension module being installed beside this file.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/context.c -->
# File Research: sources/block-storage/util-linux/libmount/python/context.c

## Scope

Implements the Python `libmount.Context` type wrapping `struct libmnt_context`.

## Behavior

- Defines object lifecycle: allocation initializes fields, init creates a libmount context, dealloc releases context-associated Python user data and frees the C context.
- Constructor accepts source, target, fstype, options, mount flags, type/options patterns, filesystem object, fstab table, and option mode.
- Provides Python methods for enabling/disabling mount behavior flags, canonicalization, helpers, mtab updates, swap matching, fake/force/lazy/loop delete/read-only/sloppy/verbose/fork modes.
- Exposes setters/getters for source, target, fstype, options, mount flags, user mount flags, fstab, mtab, fs object, status, syscall errno, and option mode.
- Wraps mount workflow calls: apply fstab, prepare/do/finalize mount, prepare/do/finalize umount, high-level mount/umount, helper initialization/options, and umount target lookup.
- Exposes state queries such as fake/force/lazy/nohelpers/nocanonicalize/restricted/syscall_called/helper_executed/tab_applied/parent/child/fork.
- Registers `ContextType` into the module as `Context`.

## Dependencies And Risks

- Depends on `pylibmount.h`, `FsType`, `TableType`, conversion helpers, and libmount `mnt_context_*` APIs.
- Reference ownership is manually coordinated through libmount userdata slots for fs/fstab/mtab Python objects.
- Several wrappers map positive libmount status/error returns to Python exceptions; callers are expected to inspect `status` after mount/umount errors.
- The file contains fragile binding code paths: argument parsing and status/query wrappers must be audited carefully because mismatched `PyArg_Parse*` logic or return-value conventions can turn libmount errors into Python API bugs.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/context.c -->