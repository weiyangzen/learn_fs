# Group Research: group_692_linux_sources_os_linux_linux_block_partitions_core_c_sources_os_linu_14e77170ec1b

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/core.c -->
# File Research: sources/os/linux/linux/block/partitions/core.c

## Summary
Implements the Linux block partition scanning core. It orders partition-table probes, owns `parsed_partitions` allocation, creates/removes partition `block_device` instances, exposes partition sysfs attributes, and handles disk rescans.

## Main Responsibilities
- Defines the global partition probe order in `check_part[]`.
- Allocates and frees partition parse state and parse output buffers.
- Runs table recognizers until one succeeds.
- Adds, deletes, resizes, and drops partition devices.
- Handles `bdev_disk_changed()` rescans and media invalidation.
- Reads partition-table sectors through the whole-disk page cache.

## Key APIs
- `bdev_add_partition()`, `bdev_del_partition()`, `bdev_resize_partition()`.
- `bdev_disk_changed()`.
- `drop_partition()`.
- `read_part_sector()`.
- Internal helpers: `check_partition()`, `add_partition()`, `blk_add_partitions()`.

## Important Behavior
GPT is probed before MSDOS, and LDM is also probed before MSDOS so those table formats can claim disks before generic MBR parsing.

`add_partition()` creates a child block device, assigns either an in-range minor or an extended block minor, attaches metadata such as UUID/volume name, creates the `holders` kobject, and finally inserts it into `disk->part_tbl`.

Partition addition rejects host-managed zoned whole disks, duplicate partition numbers, and partitions beyond `DISK_MAX_PARTS`. Rescan paths remove existing partitions only while `open_mutex` is held and no partitions are open.

If a table or partition extends beyond end-of-device, the code can call `unlock_native_capacity()` once and retry scanning.

## State and Synchronization
Partition table mutation is serialized by `disk->open_mutex`. Partition lookup during overlap checks uses RCU over the disk xarray. Device lifetime is tied to block-device references, device refs, kobject refs, and `part_release()` cleanup.

## Risks
The probe order is behaviorally significant; moving recognizers can make stale or protective tables claim disks incorrectly. Rescan correctness depends on open counts, holder state, and xarray/device lifetime staying consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/efi.c -->
# File Research: sources/os/linux/linux/block/partitions/efi.c

## Summary
Implements EFI GPT partition-table detection, validation, and partition export.

## Main Responsibilities
- Handles the `gpt` kernel command-line override.
- Validates protective and hybrid MBRs.
- Reads GPT headers and partition entry arrays.
- Verifies GPT signatures, sizes, usable LBA ranges, and CRCs.
- Chooses primary or alternate GPT when one is invalid.
- Emits Linux partition entries with GPT UUID/name metadata.

## Key APIs
- `efi_partition()`.
- Internal helpers: `find_valid_gpt()`, `is_gpt_valid()`, `is_pmbr_valid()`, `alloc_read_gpt_header()`, `alloc_read_gpt_entries()`.

## Important Behavior
Without `gpt`, the parser requires a valid protective or hybrid MBR before accepting GPT data. With `gpt`, it may try alternate GPT locations even if the protective MBR path fails, including a disk-driver-provided `alternative_gpt_sector()`.

Header validation checks GPT signature, header size bounds, header CRC, `my_lba`, usable LBA bounds, partition entry size, partition entry allocation size, and partition-entry-array CRC.

`efi_partition()` maps GPT logical blocks to 512-byte kernel sectors, skips empty or out-of-range entries, marks Linux RAID GUID entries for md autodetect, stores partition GUID in `info->uuid`, and converts UTF-16LE partition names to printable 7-bit labels.

## State and Lifetime
GPT headers and entry arrays are dynamically allocated during scan and freed before return. Disk reads use `read_lba()`, which internally reads 512-byte sectors through the partition core.

## Risks
The UTF-16 partition name conversion is intentionally lossy. GPT validity depends on correct logical block sizing and CRC coverage; malformed tables can be ignored even when some entries look plausible.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/efi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/efi.h -->
# File Research: sources/os/linux/linux/block/partitions/efi.h

## Summary
Defines on-disk EFI GPT and protective-MBR structures, GPT constants, and common partition-type GUIDs.

## Main Contents
- Protective MBR constants: `MSDOS_MBR_SIGNATURE`, `EFI_PMBR_OSTYPE_EFI_GPT`.
- GPT constants: header signature, revision, primary header LBA.
- GUID constants for EFI system, legacy MBR, Microsoft reserved/basic data, Linux RAID, Linux swap, and Linux LVM partitions.
- Packed structures: `gpt_header`, `gpt_entry_attributes`, `gpt_entry`, `gpt_mbr_record`, `legacy_mbr`.

## Important Details
All GPT on-disk fields are little-endian and structures are packed. `gpt_entry` includes type GUID, unique partition GUID, start/end LBAs, attributes, and a 72-byte UTF-16LE name field.

## Risks
Consumers must use endian helpers and avoid assuming natural alignment. The header omits the reserved tail of a logical block; readers allocate a full logical block but validate only the header-sized portion.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/efi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/ibm.c -->
# File Research: sources/os/linux/linux/block/partitions/ibm.c

## Summary
Implements IBM s390 DASD partition recognition for VOL1, LNX1, and CMS1 labels.

## Main Responsibilities
- Locates DASD volume labels across ECKD, FBA, and CMS-formatted FBA layouts.
- Converts EBCDIC label type and volume IDs to ASCII.
- Parses VTOC format labels for VOL1 disks.
- Creates single Linux partitions for LNX1 and CMS1 labels.
- Uses DASD geometry and optional DASD driver metadata for compatibility cases.

## Key APIs
- `ibm_partition()`.
- Internal helpers: `find_label()`, `find_vol1_partitions()`, `find_lnx1_partitions()`, `find_cms1_partitions()`.

## Important Behavior
`find_label()` checks label sectors determined by DASD metadata when available, otherwise tries three known candidate locations. VOL1 parsing walks VTOC format 1/8 labels and skips format 4/5/7/9 labels.

LNX1 creates one partition after the label. For older LDL formats without large-volume support, it reconciles geometry-derived size with actual disk sectors and DASD metadata. CMS1 handles both reserved minidisks and ordinary CMS labels, including the FBA DIAG special case where the label may be at sector 1.

If DASD metadata is present but no valid label is found, the parser still claims DASD disks for backward compatibility and can synthesize an LDL partition.

## State and Dependencies
Uses `disk->fops->getgeo()` and dynamically resolves `dasd_biodasdinfo` with `symbol_get()`. Allocates temporary DASD info, geometry, and label buffers.

## Risks
Correct extents depend on DASD geometry conversion from CCHH/CCHHB values. The compatibility fallback deliberately claims unlabeled DASD devices, which is unusual compared with most partition recognizers.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/ibm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/karma.c -->
# File Research: sources/os/linux/linux/block/partitions/karma.c

## Summary
Recognizes the Rio Karma media-player partition label.

## Main Responsibilities
- Reads sector 0.
- Validates the Karma disklabel magic `0xAB56`.
- Exposes up to two partitions whose filesystem type byte is `0x4d`.

## Key API
- `karma_partition()`.

## Important Behavior
The on-disk label is defined locally as a packed structure. Partition offsets and sizes are little-endian 32-bit sector counts. Empty partitions are skipped but slot numbering still advances.

## Risks
The parser is intentionally narrow and accepts only two entries with a specific type byte. Any read failure returns `-1`, allowing the partition core to treat it as an I/O failure candidate.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/karma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/ldm.c -->
# File Research: sources/os/linux/linux/block/partitions/ldm.c

## Summary
Implements Windows Logical Disk Manager dynamic disk parsing. It recognizes MBR type `0x42`, validates the LDM database, parses VBLK records, and emits the data partitions that belong to the current disk.

## Main Responsibilities
- Detects candidate dynamic disks from the MBR partition type.
- Validates primary/backup `PRIVHEAD` records.
- Validates TOCBLOCK records and VMDB consistency.
- Reads and parses VBLK disk, disk-group, volume, component, and partition records.
- Reassembles fragmented VBLKs.
- Filters database partitions to the current physical disk GUID.
- Creates Linux partition entries sorted by on-disk start sector.

## Key APIs
- `ldm_partition()`.
- Validation helpers: `ldm_validate_partition_table()`, `ldm_validate_privheads()`, `ldm_validate_tocblocks()`, `ldm_validate_vmdb()`.
- VBLK helpers: `ldm_parse_vblk()`, `ldm_ldmdb_add()`, `ldm_frag_add()`, `ldm_frag_commit()`.
- Output helper: `ldm_create_data_partitions()`.

## Important Behavior
The parser accepts PRIVHEAD version 2.11 and 2.12, checks the database is within disk bounds, ensures logical disk and database regions do not overlap, and compares primary and backup metadata. Vista-style missing TOCBLOCK backups are tolerated as long as at least one valid TOCBLOCK exists and all found copies match.

VBLK fields use variable-width length-prefixed integers and strings. `ldm_relative()` range-checks each variable field offset before the type-specific parser reads it. Partition VBLKs carry start, size, volume offset, parent id, disk id, and optional partition number.

Fragmented VBLKs are grouped by record group id, deduplicated, marked incomplete when broken, and committed only when all fragments are present.

## State and Lifetime
`struct ldmdb` owns parsed global headers plus per-type linked lists of allocated `struct vblk`. All VBLK lists and fragment lists are freed before return.

## Risks
The format has many variable-length and versioned fields; correctness depends on the offset validation in every parser path. The emitted Linux partition numbers are based on discovered partition-object order for the current disk, not necessarily Windows volume numbering.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/ldm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/ldm.h -->
# File Research: sources/os/linux/linux/block/partitions/ldm.h

## Summary
Defines constants and in-memory structures for Windows LDM dynamic disk parsing.

## Main Contents
- Magic values for `VMDB`, `VBLK`, `PRIVHEAD`, and `TOCBLOCK`.
- VBLK type and flag constants.
- LDM database sector offsets and database size constants.
- On-parser structures for fragments, private headers, TOCs, VMDB headers, VBLK variants, generic VBLKs, and the cached `ldmdb`.

## Important Details
All offsets and sizes in `privhead` and LDM database constants are sector-based. `struct vblk` stores common VBLK identity fields and a union of parsed record-specific payloads, then links into one of several per-type lists.

## Risks
Many constants encode fixed offsets into undocumented Windows structures. Parser code must keep these structures synchronized with the offset logic in `ldm.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/ldm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/mac.c -->
# File Research: sources/os/linux/linux/block/partitions/mac.c

## Summary
Recognizes Apple Partition Map disks and exports map entries as Linux partitions.

## Main Responsibilities
- Validates the driver descriptor in block 0.
- Reads the first Apple partition map entry.
- Uses the map count to iterate partition entries.
- Marks `Linux_RAID` entries for md autodetect.
- On PowerMac, records the most plausible boot/root partition.

## Key API
- `mac_partition()`.

## Important Behavior
The parser requires the driver descriptor magic and a power-of-two on-disk block size. Partition entries may be offset within a 512-byte sector when the Mac block size is not a multiple of 512, so the parser computes the byte offset carefully.

For each valid entry, start and length are converted from Mac blocks to 512-byte sectors. On `CONFIG_PPC_PMAC`, it trims strings and scores bootable PowerPC Unix/Linux partitions to call `note_bootable_part()`.

## Risks
The parser depends on valid `block_size` and `map_count` values from disk. Non-power-of-two block sizes are rejected because partition entries could straddle sectors in ways `read_part_sector()` cannot safely handle.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/mac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/mac.h -->
# File Research: sources/os/linux/linux/block/partitions/mac.h

## Summary
Defines Apple Partition Map constants and packed-ish on-disk structures used by `mac.c`.

## Main Contents
- `MAC_PARTITION_MAGIC`, `MAC_DRIVER_MAGIC`, and `MAC_STATUS_BOOTABLE`.
- `APPLE_AUX_TYPE`.
- `struct mac_partition`.
- `struct mac_driver_desc`.

## Important Details
`mac_partition` stores big-endian map count, start block, block count, status, boot fields, and fixed-size name/type/processor strings. `mac_driver_desc` provides the block size needed to locate partition-map entries.

## Risks
Fields are big-endian and represent Apple block units, not Linux 512-byte sectors. Consumers must convert both endian and unit size.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/msdos.c -->
# File Research: sources/os/linux/linux/block/partitions/msdos.c

## Summary
Implements DOS/MBR partition parsing, extended partition traversal, and optional subpartition parsing for BSD, Solaris x86, UnixWare, and Minix layouts.

## Main Responsibilities
- Validates MBR `55 aa` signature and boot indicators.
- Avoids claiming AIX and GPT protective disks.
- Emits primary and extended partition entries.
- Traverses linked-list logical partitions inside extended partitions.
- Assigns MBR-derived partition UUID strings.
- Marks Linux RAID MBR partitions.
- Dispatches subtype parsers for known nested disklabel formats.

## Key APIs
- `msdos_partition()`.
- Internal helpers: `parse_extended()`, `parse_bsd()`, `parse_solaris_x86()`, `parse_unixware()`, `parse_minix()`.

## Important Behavior
The extended parser follows EBR links iteratively with a 100-link guard. It handles data entries first, then follows the first extended entry, and applies bounds checks to suspicious third/fourth EBR entries.

A valid FAT boot sector with an invalid boot indicator can be treated as a whole-disk FAT filesystem rather than a partition table. Protective GPT entries cause the MSDOS parser to return 0 so the GPT parser can own the disk.

Primary partitions receive metadata UUIDs formatted from the MBR disk signature and slot number. Logical partitions start at `state->next = 5`.

## Optional Subformats
- Solaris x86 VTOC slices.
- BSD/OpenBSD/NetBSD disklabels.
- UnixWare slices.
- Minix subpartitions.
- AIX delegation when configured.

## Risks
MBR formats are ambiguous with FAT boot sectors and legacy vendor overlays. Extended partition traversal must defend against loops, garbage entries, and out-of-container extents.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/of.c -->
# File Research: sources/os/linux/linux/block/partitions/of.c

## Summary
Creates block partitions from device-tree `fixed-partitions` nodes.

## Main Responsibilities
- Checks whether the disk device node is compatible with `fixed-partitions`.
- Validates each child `reg` property before adding any partitions.
- Converts byte offsets and sizes to 512-byte sectors.
- Applies `read-only` partition flags.
- Stores partition labels from `label` or `name`.

## Key API
- `of_partition()`.

## Important Behavior
Validation requires the `reg` length to match address and size cell counts, offset to be sector-aligned, and size to be nonzero and sector-aligned. The parser performs a full validation pass first, then a second pass that adds partitions.

## Risks
The implementation assumes the disk device node itself is the `fixed-partitions` node. Partition label handling assumes a usable `label` or `name` property is present.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/of.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/osf.c -->
# File Research: sources/os/linux/linux/block/partitions/osf.c

## Summary
Recognizes OSF/1-style disklabels stored in sector 0 at offset 64.

## Main Responsibilities
- Reads the disklabel from sector 0.
- Validates both disklabel magic fields.
- Bounds-checks the partition count against 18.
- Emits nonempty partitions.

## Key API
- `osf_partition()`.

## Important Behavior
Partition offsets and sizes are little-endian sector counts. Slot numbering follows disklabel order and advances even over empty entries.

## Risks
No checksum validation is performed despite the structure containing a checksum field. The parser trusts the bounded partition count after magic validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/osf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/sgi.c -->
# File Research: sources/os/linux/linux/block/partitions/sgi.c

## Summary
Recognizes SGI disklabels and emits up to 16 partition entries.

## Main Responsibilities
- Validates the SGI magic.
- Computes and verifies the disklabel checksum.
- Emits nonempty partitions.
- Marks SGI entries with Linux RAID type for md autodetect.

## Key API
- `sgi_partition()`.

## Important Behavior
The checksum is a 32-bit sum over the label interpreted as big-endian words and must equal zero. Partition start and block count are big-endian logical block values used directly as Linux sectors.

## Risks
The code increments output slots across all 16 SGI entries, including empty ones. It does not explicitly cap against `state->limit`, relying on historical assumptions about minor counts and sparse labels.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/sgi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/sun.c -->
# File Research: sources/os/linux/linux/block/partitions/sun.c

## Summary
Recognizes Sun disklabels and emits Sun partition entries.

## Main Responsibilities
- Validates Sun label magic and XOR checksum.
- Optionally validates and uses the embedded Sun VTOC.
- Converts cylinder-based starts to sectors.
- Marks Linux RAID and whole-disk entries from VTOC IDs.

## Key API
- `sun_partition()`.

## Important Behavior
Partition start sectors are computed as `start_cylinder * ntracks * nsect`; sizes are already sector counts. If VTOC sanity/version/count are valid, VTOC IDs control RAID and whole-disk flags. Empty legacy VTOC metadata is also treated as usable for old Linux-Sun compatibility.

## Risks
Geometry fields in the label drive start conversion. Corrupt or unexpected VTOC metadata can change whether special flags are applied.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/sun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/sysv68.c -->
# File Research: sources/os/linux/linux/block/partitions/sysv68.c

## Summary
Recognizes Motorola/System V/68 disk slice tables.

## Main Responsibilities
- Validates the `MOTOROLA` volume identifier in sector 0.
- Reads the slice table block indicated by the config block.
- Emits all nonempty slices except the final whole-disk slice.

## Key API
- `sysv68_partition()`.

## Important Behavior
The first disk sector is interpreted as two 256-byte structures: volume id and disk config. Slice count and slice table block are big-endian. The last slice is intentionally skipped because it represents the whole disk.

## Risks
The parser trusts the slice count and slice-table block after the volume identifier check, with no explicit range check beyond read failure and `state->limit`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/sysv68.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/partitions/ultrix.c -->
# File Research: sources/os/linux/linux/block/partitions/ultrix.c

## Summary
Recognizes Ultrix partition tables located near the 16 KiB boundary.

## Main Responsibilities
- Reads the sector containing the trailing Ultrix disklabel.
- Validates magic `0x032957` and valid flag `1`.
- Emits up to eight nonempty partitions.

## Key API
- `ultrix_partition()`.

## Important Behavior
The label is expected at the end of the 16 KiB area, so the parser reads sector `(16384 - sizeof(label)) / 512` and offsets within that sector.

## Risks
The on-disk fields are read in native layout rather than explicit endian helpers, matching the historical target format but making the recognizer architecture-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/partitions/ultrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/sed-opal.c -->
# File Research: sources/os/linux/linux/block/sed-opal.c

## Summary
Implements the Linux block-layer TCG OPAL self-encrypting drive command engine and ioctl backend.

## Main Responsibilities
- Discovers OPAL feature support and COMID.
- Builds OPAL tokenized command buffers.
- Parses OPAL responses and method status codes.
- Starts and ends AdminSP/LockingSP sessions.
- Manages SID/Admin/User authentication, passwords, and keyring fallback.
- Configures locking ranges, shadow MBR, single-user mode, and table I/O.
- Handles secure erase, revert, PSID revert, stack reset, and suspend unlock replay.
- Dispatches `IOC_OPAL_*` ioctls behind `CAP_SYS_ADMIN`.

## Key APIs
- `init_opal_dev()`, `free_opal_dev()`.
- `sed_ioctl()`.
- `opal_unlock_from_suspend()`.
- Internal command sequencer: `execute_steps()`, `opal_send_recv()`, `cmd_start()`, `cmd_finalize()`.

## Important Behavior
`init_opal_dev()` allocates DMA-safe command/response buffers, initializes locking state, and runs discovery. Discovery parses feature descriptors, records COMID, geometry, locking flags, MBR state, and single-user-mode support.

Commands are encoded as OPAL atoms into a fixed 2048-byte buffer. The builder tracks `dev->pos` and uses `can_add()` to prevent overrun. `cmd_finalize()` closes the parameter list, appends method status scaffolding, pads to 4 bytes, and fills OPAL packet lengths and session numbers.

Responses are parsed into up to `MAX_TOKS` token descriptors pointing into the response buffer. Status extraction expects the OPAL method-status list near the end of the response, with special handling for `OPAL_ENDOFSESSION`.

High-level operations are arrays of `opal_step`, usually discovery, session start, one or more method calls, and session end. On failures after a session starts, `execute_steps()` attempts to terminate the session.

## Key Management
The file creates a built-in `.sed_opal` keyring at late init, optionally seeds it from `sed_read_key()`, and updates it when passwords change. Runtime keys can be supplied directly or read from the keyring through `opal_get_key()`.

## User-Facing Operations
`sed_ioctl()` supports saving unlock keys, lock/unlock, ownership, LSP activation/reactivation/revert, user activation, password changes, locking range setup/status, shadow MBR control, erase/secure erase, table read/write, discovery export, geometry/status queries, SUM status, and stack reset.

## State and Synchronization
Each `opal_dev` has a `dev_lock` covering command buffers, session state, previous response data, and saved suspend unlock list. Saved unlock entries are replayed by `opal_unlock_from_suspend()` and cleared on successful TPer revert or device free.

## Risks
This code is security-sensitive: it handles credentials, copies user buffers, and issues destructive drive commands. Correctness depends on fixed buffer accounting, OPAL token parsing bounds, session cleanup on errors, and careful synchronization around saved keys and command buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/sed-opal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/t10-pi.c -->
# File Research: sources/os/linux/linux/block/t10-pi.c

## Summary
Implements generation, verification, and request remapping of T10/NVMe protection information tuples for block integrity.

## Main Responsibilities
- Computes guard checksums for CRC64, T10 DIF CRC, and IP checksum formats.
- Generates integrity tuples for outgoing bios.
- Verifies integrity tuples for completed bios.
- Handles metadata layouts with `pi_offset`.
- Supports tuple copies across split protection bvecs.
- Remaps reference tags between virtual bio seeds and request physical positions.

## Key APIs
- `bio_integrity_generate()`.
- `bio_integrity_verify()`.
- `blk_integrity_prepare()`.
- `blk_integrity_complete()`.

## Important Behavior
`blk_integrity_iterate()` walks data bvecs by integrity interval, accumulates checksum over each interval, and then reads or writes the corresponding protection tuple. Extended CRC64 tuples use 64-bit guards and 48-bit reference tags; T10/IP tuples use 16-bit guards and 32-bit reference tags.

Verification honors application/reference tag escape values. When `BLK_INTEGRITY_REF_TAG` is enabled, reference tags must match the current seed unless the app tag escapes checking.

Request prepare maps reference tags from bio-virtual seeds to request reference positions; completion maps them back. Already mapped integrity payloads are detected with `BIP_MAPPED_INTEGRITY`.

## State and Lifetime
All iteration state is local in `struct blk_integrity_iter`. Tuple handling uses stack storage when a tuple crosses protection-vector boundaries and maps bvecs locally otherwise.

## Risks
The code is highly offset-sensitive: `pi_offset`, tuple size, metadata size, interval size, and bvec boundaries must agree with queue integrity limits. Incorrect reference-tag remapping can cause false protection failures or missed corruption detection.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/t10-pi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/Kconfig -->
# File Research: sources/os/linux/linux/fs/9p/Kconfig

## Summary
Defines kernel configuration options for the 9p filesystem client.

## Main Contents
- `9P_FS`: tristate Plan 9 Resource Sharing filesystem, depending on `NET_9P` and selecting `NETFS_SUPPORT`.
- `9P_FSCACHE`: optional FS-Cache support for 9p clients.
- `9P_FS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `9P_FS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.

## Important Details
`9P_FSCACHE` has dependency logic covering both module and built-in combinations with `FSCACHE`. POSIX ACL is nested under `if 9P_FS`; security labels depend directly on `9P_FS`.

## Risks
Feature availability is compile-time gated. ACL and security xattr behavior in source files depends on these symbols being selected.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/Makefile -->
# File Research: sources/os/linux/linux/fs/9p/Makefile

## Summary
Builds the 9p filesystem module/object composition.

## Main Contents
- Builds `9p.o` when `CONFIG_9P_FS` is enabled.
- Core objects include superblock, inode, dotl inode, address-space, file, directory, dentry, session, fid, and xattr code.
- Adds `cache.o` when `CONFIG_9P_FSCACHE` is enabled.
- Adds `acl.o` when `CONFIG_9P_FS_POSIX_ACL` is enabled.

## Risks
Optional ACL and cache source files are linked only when their configuration symbols are enabled, so callers rely on header stubs for disabled ACL builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/acl.c -->
# File Research: sources/os/linux/linux/fs/9p/acl.c

## Summary
Implements POSIX ACL support for the 9p filesystem using server xattrs and inode ACL caching.

## Main Responsibilities
- Reads ACL xattrs through 9p fids and converts them to `struct posix_acl`.
- Caches access/default ACLs on inode instantiation.
- Provides inode and dentry ACL get/set operations.
- Updates remote ACL xattrs on chmod and create.
- Applies inherited default ACLs to create modes.

## Key APIs
- `v9fs_get_acl()`.
- `v9fs_iop_get_inode_acl()`, `v9fs_iop_get_acl()`, `v9fs_iop_set_acl()`.
- `v9fs_acl_chmod()`.
- `v9fs_set_create_acl()`.
- `v9fs_acl_mode()`.
- `v9fs_put_acl()`.

## Important Behavior
When access mode is not `V9FS_ACCESS_CLIENT` or ACL mode is not `V9FS_POSIX_ACL`, inode ACL caches are set to NULL and client-side ACL enforcement is bypassed.

For `access=client`, get operations use cached ACLs populated during inode creation. For other access modes, dentry get/set paths use server xattrs directly.

Setting an access ACL validates it, converts it to xattr format, may update inode mode via `posix_acl_update_mode()`, rejects symlinks, requires ownership/capability, and updates the cached ACL on success. Default ACLs are valid only on directories.

`v9fs_acl_mode()` applies a parent default ACL during create; without a default ACL it applies the current umask.

## State and Lifetime
ACL objects are reference-counted with `posix_acl_release()`. Serialized xattr buffers are dynamically allocated and freed after server calls.

## Risks
ACL behavior changes substantially based on mount/session flags. `v9fs_set_create_acl()` ignores return values from the two remote ACL writes, so create-time cache state can be updated even if server xattr persistence fails.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/acl.h -->
# File Research: sources/os/linux/linux/fs/9p/acl.h

## Summary
Declares 9p POSIX ACL interfaces and provides no-op stubs when ACL support is disabled.

## Main Contents
With `CONFIG_9P_FS_POSIX_ACL`, declares ACL get/set, chmod, create, mode, and release helpers. Without it, inode operation hooks are defined as `NULL` and helper functions return success without changing ACL state.

## Important Details
The disabled-ACL stubs let common 9p inode and create paths call ACL helpers unconditionally while compiling out ACL behavior.

## Risks
When ACL support is disabled, create-mode helper `v9fs_acl_mode()` returns 0 without applying any ACL-derived mode changes; callers must rely on non-ACL permission handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/acl.h -->