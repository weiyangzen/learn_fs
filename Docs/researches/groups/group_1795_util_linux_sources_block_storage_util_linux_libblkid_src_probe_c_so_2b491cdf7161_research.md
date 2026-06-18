# Group Research: group_1795_util_linux_sources_block_storage_util_linux_libblkid_src_probe_c_so_2b491cdf7161

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/util-linux` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/probe.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/probe.c

Low-level libblkid probing core. It allocates and owns `blkid_probe` state, opens devices/files, configures probing dimensions, initializes probing chains for superblocks, topology, and partitions, and exposes the string-based and binary result APIs used by the rest of libblkid.

Its central data flow is: set a device with offset/size, read aligned cached buffers from the target, run enabled chain drivers, store `NAME=value` results, and optionally wipe or hide detected signatures. The buffer layer uses anonymous `mmap`, read caching, parent-probe sharing for clones, prunable superseded buffers, O_DIRECT retry support, and range hiding for dry-run wipe loops.

Important behaviors include hidden/private device-mapper suppression, floppy and CD-ROM handling, OPAL lock detection, zoned-device wipe handling, whole-disk helper probes, chain filters, safe/full/progressive probe modes, checksum validation with optional bad-checksum acceptance, result lookup/enumeration, UUID formatting, wiper heuristics for signature conflict resolution, and numeric probing hints such as CD session offsets. Risk concentrates around offset arithmetic, device-size boundaries, I/O error interpretation, and preserving chain position semantics after filters or wipes.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/probe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/read.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/read.c

Parser for the on-disk blkid cache. It reads XML-like single-line device entries of the form `<device TAG="value"...>/dev/name</device>`, reconstructs `blkid_dev` objects in a cache, and restores direct fields such as `DEVNO`, `PRI`, and `TIME` plus generic tags like `TYPE`, `LABEL`, and `UUID`.

The parser trims whitespace, skips comments and unknown XML-ish lines, handles backslash-escaped quoted values, supports line continuations ending in backslash, and rejects malformed cache records without aborting the whole cache load. Device records without `TYPE` are discarded because the cache cannot meaningfully identify their content.

`blkid_read_cache` avoids rereading unchanged cache files by comparing `st_mtime` and the cache changed flag. It depends on cache/device/tag helpers from `blkidP.h`. Main risks are the intentionally lenient legacy cache grammar and fixed 4096-byte line buffer, though continuation support reduces ordinary truncation issues.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/read.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/resolve.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/resolve.c

Small cache lookup API for resolving device names and tag values. `blkid_get_tag_value` finds a tag such as `LABEL` or `UUID` on a named device and returns a duplicated string. `blkid_get_devname` accepts either `NAME=value`, a `(name,value)` pair, or a raw device name; tag inputs are resolved through the blkid cache and raw device names are copied through unchanged.

If no cache is supplied, both functions create and release a default cache internally. The code relies on `blkid_get_cache`, `blkid_get_dev`, `blkid_find_tag_dev`, `blkid_parse_tag_string`, and `blkid_find_dev_with_tag`. Behavior is intentionally simple: no probing is done here directly beyond whatever cache acquisition does, and all returned strings are caller-owned.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/save.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/save.c

Writer for the blkid cache file. It serializes non-removable cache devices with known types into `<device ...>path</device>` records, quoting tag values and escaping only `"` and `\`. Device metadata includes `DEVNO`, `TIME`, optional `PRI`, and all tags attached to the device.

`blkid_flush_cache` skips unchanged or empty caches, creates the default runtime directory when needed, checks write access, and prefers a temporary file in the same directory for regular cache files. On successful temp-file writes it creates a `.old` hard-link backup when possible and renames the temp file into place.

The file depends on `mkstemp_cloexec`, `close_stream`, and blkid cache/list structures. Error handling is conservative: inability to write the cache often returns success-like no-op behavior so probing tools are not failed just because persistence is unavailable.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/save.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/adaptec_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/adaptec_raid.c

Adaptec RAID member detector. It checks only regular files or whole-disk block devices, reads vendor metadata from the last 512-byte sector, and validates two big-endian markers: the `DPTM` signature and the Adaptec magic value.

On match, it reports `adaptec_raid_member`, usage `BLKID_USAGE_RAID`, stores the metadata revision as `VERSION`, and records the signature location through `blkid_probe_set_magic` when magic reporting is enabled. It has no magic table because the probe location is computed from device size. False-positive resistance is based on whole-disk restriction plus dual magic validation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/adaptec_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/apfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/apfs.c

APFS container superblock detector. It recognizes `NXSB` at offset 32, reads the 4096-byte container header subset, validates the APFS Fletcher64 checksum over the object payload area, and requires container object type, subtype zero, zero padding, and a standard 4096-byte block size.

On success it reports filesystem type `apfs`, sets the container UUID, and records filesystem/device block size. The implementation is intentionally strict because APFS documentation is limited in the comment’s context. It does not parse volumes inside the APFS container, labels, feature flags, or container size beyond the minimal validation fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/apfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bcache.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bcache.c

Detector for both legacy bcache backing/cache devices and bcachefs filesystems. The bcache path validates the CRC64 checksum across the active journal-bucket portion of the superblock, checks the recorded offset, emits version, UUID, label, block size, and marks the initial bcache metadata area as a wiper region.

The bcachefs path validates the superblock offset, device index/count, variable superblock size, maximum layout size, and checksum type. It supports none, CRC32C, CRC64, and XXH64 checksums, then emits user UUID, primary label, bcachefs major/minor version, block sizes, total filesystem size, and UUID_SUB for the current member.

It also parses variable bcachefs superblock fields for members v1/v2 and disk groups. That logic bounds every dynamic field against the read superblock, sums member bucket sizes into FSSIZE, and reconstructs hierarchical disk-group labels into `LABEL_SUB`. Risk centers on dynamic field size arithmetic, but the code uses explicit range checks before walking variable data.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/befs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/befs.c

BeFS detector with substantial metadata traversal. It recognizes little- and big-endian BeFS superblocks at primary and alternate offsets, validates all three superblock magic fields, confirms block size/shift consistency, and avoids undefined shifts by checking allocation-group plus block-shift bounds.

Beyond the superblock, it attempts to recover the BeFS volume UUID from the root inode’s small data area or from the attribute B+tree. Helpers translate BeFS block runs through direct, indirect, and double-indirect data streams, compare B+tree keys, and follow bounded B+tree loops to find `be:volume_id`.

On success it emits label, endian-specific version string, formatted 64-bit UUID when found, filesystem/device block size, and endianness. The file’s complexity is in defensive parsing of BeFS inode and B+tree metadata; malformed structures generally return no match rather than crashing or trusting the initial magic.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/befs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bfs.c

Minimal BFS filesystem descriptor. It declares `bfs_idinfo` with filesystem usage and a single four-byte magic value. There is no custom probe function; libblkid’s generic superblock magic matching is enough.

The comment notes BFS has two short labels in the superblock, but this detector intentionally ignores them because their meaning is unclear. As a result, detection only reports type and usage, not label, UUID, version, or block geometry.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bitlocker.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bitlocker.c

BitLocker detector and collision helper. It recognizes Vista, Windows 7, and BitLocker To Go boot signatures, then for newer formats follows the metadata offset to the FVE metadata header and validates the `-FVE-FS-` block signature. `blkid_probe_is_bitlocker` exposes this logic so NTFS/vFAT probes can avoid misidentifying encrypted volumes.

The main probe reports `BitLocker` with crypto usage. When FVE metadata is available it sets the metadata version, scans metadata entries for a UTF-16LE description label, and formats the volume identifier using Microsoft GUID byte ordering.

The implementation bounds metadata entry walking by the declared metadata size and checks entry alignment/size before use. Vista detection can succeed from the boot signature alone and therefore has less metadata output than Win7/To Go.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bitlocker.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bluestore.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bluestore.c

Ceph BlueStore backing block-device detector. It matches the literal `bluestore block device` magic string and reads the small physical header structure through the generic superblock helper.

The custom probe only verifies the buffer can be read; all actual identity comes from the magic table. It reports name `ceph_bluestore` with `BLKID_USAGE_OTHER` and does not expose UUID, label, version, or geometry.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/bluestore.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/btrfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/btrfs.c

Btrfs superblock detector, including zoned-device handling. For ordinary devices it reads the standard superblock at 64 KiB; for zoned devices it locates the active superblock log position by querying zone reports and interpreting conventional, empty, in-use, and full log-zone states.

Checksum validation supports CRC32C, XXH64, and SHA256 over the superblock payload, while unknown checksum types are logged and tolerated. On success it emits label, filesystem UUID, per-device UUID as `UUID_SUB`, sector/block size, total logical filesystem size, and last block.

False-positive defenses include checksum verification, nonzero sector size validation, magic offsets for both normal and zoned layouts, and careful zone-state validation. FSSIZE is explicitly logical and does not account for Btrfs RAID redundancy because that requires tree parsing.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/cramfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/cramfs.c

Cramfs detector supporting little- and big-endian magic. It converts fields according to the magic hint, detects v1 versus v2 via the FSID version flag, and validates the v2 checksum by reading the declared filesystem image size and excluding the checksum field from CRC32 calculation.

On success it reports label, filesystem size, version `1` or `2`, and endianness. The checksum path bounds the declared size to a small sane range before reading. Version 1 lacks checksum validation, so detection relies mainly on the magic and extracted fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/cramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/cs_fvault2.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/cs_fvault2.c

Apple Core Storage/FileVault2 physical-volume detector. It matches `CS` at the physical-volume header magic offset, requires version 1 and checksum algorithm 1, verifies a seeded CRC32C over the header after the checksum field, and then narrows detection to FileVault2-like block type `0x10`, 16-byte key data, and AES-XTS cipher id.

On success it reports `cs_fvault2`, crypto usage, version, and physical-volume UUID. The file deliberately does not derive filesystem size or block geometry because the actual filesystem lives above Core Storage/dm-crypt and would require parsing additional metadata blocks.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/cs_fvault2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ddf_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ddf_raid.c

SNIA DDF RAID member detector. It checks possible secondary header locations near the end of the disk, validates the big-endian DDF signature and CRC32 with the CRC field excluded and treated as `0xff`, and optionally confirms the primary header by reading the recorded primary LBA.

On match it stores the 24-byte DDF GUID as UUID, copies the revision string into `VERSION`, and records the magic offset for wiping/reporting. It reports `ddf_raid_member` with RAID usage and a minimum size. Detection is size-position based rather than static magic-table based.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ddf_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbd.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbd.c

DRBD metadata detector for v08/v8.4 and v09. It defines compact on-disk metadata structures, recognizes clean and unclean v08 magics and v09 magic near the end of the device, and dispatches by a magic-table hint.

Both version-specific probes validate the bitmap bytes-per-bit field against DRBD’s 4 KiB bitmap block size and require the aligned padding region to be zero. They then format DRBD’s 64-bit device UUID as a hex UUID-like value and set version `v08` or `v09`.

The detector reports RAID usage because DRBD is a replicated block layer. It avoids parsing the full DRBD metadata state and focuses on robust identification from magic, geometry, padding, and device UUID fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbdmanage.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbdmanage.c

DRBDmanage control-volume detector. It matches `$DRBDmgr=q` at offset zero, reads the fixed header, verifies the 32-byte UUID field is all hex digits and followed by newline, and stores it as the UUID.

It then reads a persistence header at 0x1000. If the binary persistence magic is present, it emits the version from the version field. The detector reports `drbdmanage_control_volume` with `BLKID_USAGE_OTHER` and a 64 KiB minimum size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbdmanage.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbdproxy_datalog.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbdproxy_datalog.c

DRBD Proxy datalog detector. It matches `DRBDdlh*` at the start of the device, reads a small log header, emits the embedded UUID, and formats the little-endian version as `v<version>`.

The idinfo reports `drbdproxy_datalog` with filesystem usage and a 16 KiB minimum size. The probe is intentionally lightweight and does not validate flags or log layout beyond the magic and readable header.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/drbdproxy_datalog.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/erofs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/erofs.c

EROFS filesystem detector. It matches the v1 magic at 1024 bytes, validates block-size bits in the 512-byte to 64 KiB range, and if the superblock checksum feature is present, computes CRC32C over the superblock block with the checksum field excluded.

On success it emits label, UUID, filesystem/device block size, and filesystem size from block count times block size. The checksum code guards against underflow by requiring the block size to exceed the superblock offset before computing the checksummed span.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/erofs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/exfat.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/exfat.c

exFAT detector and MBR collision helper. It validates the boot sector signature, jump code, `EXFAT   ` name, zeroed legacy BPB area, FAT count, sector/cluster shifts, FAT and cluster heap ranges, root directory cluster, and the required boot checksum over the first 11 sectors against all repeated checksum words in sector 12.

The probe walks the root directory cluster chain through the FAT to find a volume label entry, bounded by a 256 MiB directory scan cap. It emits the UTF-16LE label, serial-number UUID, filesystem revision, block size, and filesystem size. `blkid_probe_is_exfat` lets the DOS partition parser distinguish exFAT from vFAT-like boot sectors.

Risk is mainly in boot-sector arithmetic and FAT chain traversal; the code clamps shift ranges and cluster bounds before using computed offsets.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/exfat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/exfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/exfs.c

EXFS filesystem detector. It reads a big-endian superblock, converts the fields needed for validation into a temporary CPU-endian structure, and performs extensive sanity checks on sector size, block size, inode size, inodes-per-block log relationship, realtime extent size, allocation-group count, total data blocks, and inode percentage.

On success it emits the filesystem label, UUID, and block sizes. The magic is `EXFS` at the superblock start. False-positive resistance comes mostly from the many geometry and consistency checks rather than a checksum.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/exfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ext.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ext.c

ext-family detector for JBD, ext2, ext3, ext4, and ext4dev. It reads the ext superblock at 1024 bytes, validates metadata checksums when the metadata-csum feature is set, and retries with O_DIRECT after a checksum failure to avoid races with concurrent superblock writes. Legacy filesystems without checksums get an additional block-size sanity check.

The shared `ext_get_info` path emits label, filesystem UUID, journal UUID when present, optional `SEC_TYPE=ext2`, version, block size, last block, and filesystem size. Individual probes distinguish JBD journal devices, ext2 without journal/unsupported features, ext3 with journal but without ext4-only features, ext4 with ext4-only features, and ext4dev test filesystems.

The file’s correctness depends on feature-bit classification and conservative unsupported-feature masks. FSSIZE intentionally uses raw block count and does not subtract ext metadata/journal overhead.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/ext.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/f2fs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/f2fs.c

F2FS detector. It matches the magic at the primary superblock offset, extracts major/minor version, and treats version 1.0 specially because the current structure layout cannot be assumed. For newer versions it validates the optional superblock checksum at the declared checksum offset using the F2FS seed.

On success it emits UTF-16LE volume name, UUID, version, block sizes, and filesystem size from block count times block size. The code bounds checksum offset alignment and size, and avoids shifts above 16 when computing block size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/f2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/gfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/gfs.c

GFS and GFS2 detector. Both formats share the same magic at 64 KiB, then diverge by filesystem and multihost format ranges. GFS1 requires exact legacy format constants, while GFS2 accepts format ranges 1800-1899 and 1900-1999.

Both probes emit the lock table as label when present and the superblock UUID. GFS2 also emits version `1` and block size. The idinfos set a 32 MiB minimum size reflecting the minimal GFS journal size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/gfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/hfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/hfs.c

HFS and HFS+ detector. The HFS path reads the master directory block, rejects embedded HFS+ volumes, validates allocation block size alignment, derives a UUID from Finder info using the HFS MD5 namespace algorithm, and sets the Pascal-style HFS label.

The HFS+ path handles both native HFS+ and HFS+-embedded-in-HFS layouts. It validates signatures, computes embedded offsets from HFS allocation metadata when needed, checks HFS+ block size, emits UUID and block size, then reads the catalog B-tree header and first leaf node to recover the UTF-16BE volume label from the catalog key.

HFS is marked tolerant because it can coexist as a wrapper around embedded HFS+. The HFS+ catalog walk is partial but defensive: it validates node size, leaf count, extent coverage, leaf type, record count, parent id, and Unicode length before using label data.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/hfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/highpoint_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/highpoint_raid.c

HighPoint RAID detector for hpt45x and hpt37x formats. The hpt45x probe is computed-location based: it checks regular files or whole disks only, reads metadata 11 sectors from the end, and accepts the OK or BAD little-endian magic.

The hpt37x detector uses static magic entries at the documented offset and a probe that only enforces whole-disk/regular-file scope. Both idinfos report RAID usage. hpt45x records magic for wiping/reporting; hpt37x relies on the generic magic table.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/highpoint_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/hpfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/hpfs.c

HPFS detector. It matches the primary HPFS superblock magic at 0x2000, then reads the spare superblock at 0x2200 to verify its magic. It also reads the boot block to extract label and serial UUID when the boot signature, `HPFS` marker, and `0x28` serial-label signature are present.

On success it emits version from the HPFS superblock and fixed 512-byte block sizes. Detection depends on both primary and spare superblock validation, with optional boot-block identity fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/hpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/iso9660.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/iso9660.c

ISO9660, High Sierra, and Joliet detector. It honors a `session_offset` hint, scans up to 16 volume descriptors from 32 KiB, records boot, primary, and Joliet supplementary descriptors, and rejects non-sector-aligned session offsets.

It validates logical block size and then checks the root directory record by reading the root extent and requiring the first directory entry to be the `.` self-reference pointing back to the same LBA. This is a deliberate false-positive guard for `CD001` strings embedded inside other filesystems.

On success it emits block size, filesystem size, system/volume-set/publisher/data-preparer/application IDs, date-derived UUID, boot system ID, version (`Joliet Extension` or `High Sierra`), and label. Joliet fields are UTF-16BE and the code tries to reconstruct longer labels/IDs by merging Joliet prefixes with ASCII PVD suffixes.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/iso9660.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/isw_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/isw_raid.c

Intel Matrix Storage RAID member detector. It applies only to regular files or whole disks, reads metadata two logical sectors from the end using the probed sector size, and checks the `Intel Raid ISM Cfg Sig. ` prefix.

On match it formats the version from the signature suffix and records the signature as magic. It reports `isw_raid_member` with RAID usage and a 64 KiB minimum size. No checksum validation is performed in this detector.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/isw_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/jfs.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/jfs.c

JFS detector. It matches `JFS1` at 32 KiB, then validates block-size and physical-block-size logarithms, exact power-of-two relationships, and the logical-to-physical block factor.

On success it emits label, UUID, filesystem block size, and device block size. The geometry checks reduce false positives from the simple four-byte magic. The idinfo declares a 16 MiB minimum size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/jfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/jmicron_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/jmicron_raid.c

JMicron RAID member detector. It checks regular-file/whole-disk scope, reads metadata from the last sector, validates the `JM` signature, verifies a 16-bit additive checksum whose sum must be 0 or 1, and rejects RAID mode values above 5.

On success it reports version as major.minor from the packed version field and records the signature magic offset. It reports `jmicron_raid_member` with RAID usage and a 64 KiB minimum size.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/jmicron_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/linux_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/linux_raid.c

Linux MD RAID detector for legacy 0.90-style and version 1.x superblocks. The 0.90 path reads the reserved end-of-device area, accepts little- or big-endian magic, reconstructs the set UUID, validates that the component size fits before the superblock, and avoids whole-disk false positives when the superblock is covered by an existing partition table.

The 1.x path reads superblocks at v1.0, v1.1, and v1.2 locations, validates magic, major version, recorded superblock sector offset, and checksum over the variable `dev_roles` array. It emits set UUID, device UUID as `UUID_SUB`, and set name.

The top-level probe tries v0.90, v1.0, v1.1, and v1.2 in order, setting version for 1.x matches. Signature magic is recorded for wiping. Risk points are variable checksum length and offset calculations, both guarded by reads through the probe buffer API.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/linux_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/lsi_raid.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/lsi_raid.c

LSI MegaRAID member detector. It checks only regular files or whole disks, reads the last sector, and matches the six-byte `$XIDE$` signature.

On match it records the signature location through `blkid_probe_set_magic` and reports `lsi_mega_raid_member` with RAID usage and a 64 KiB minimum size. It does not expose UUID, label, version, or checksum validation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/lsi_raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/luks.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/luks.c

LUKS crypto-volume detector. It reads the primary header at offset zero, validates LUKS magic, and for LUKS2 also requires the header’s recorded offset to match the actual location. It emits magic, version, UUID, and for LUKS2 label plus `SUBSYSTEM`.

If no primary header is found and the probe is not in safeprobe mode, it scans known LUKS2 secondary header offsets using the reversed secondary magic. A separate OPAL probe detects LUKS2 headers whose subsystem is `HW-OPAL` only when the underlying drive reports itself locked through OPAL status; this allows reporting locked hardware-encrypted LUKS2 volumes despite later I/O errors.

The file deliberately does not verify LUKS2 header checksums or parse JSON metadata; it is focused on stable header identity and recovery-header discovery.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/luks.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/lvm.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/lvm.c

Detector collection for LVM1, LVM2 PVs, DM snapshot COW, DM-verity hash devices, and DM-integrity. LVM2 reads around 0 or 1 KiB, locates the `LABELONE` header, verifies the recorded sector, checks the LVM CRC over the label payload, formats the 32-character PV UUID with LVM dashes, sets version from the label type, and marks the first 8 KiB as a wiper region.

LVM1 verifies version 1 or 2 and formats its PV UUID. DM snapshot COW is magic-only. DM-verity validates version 1 and emits UUID/version. DM-integrity validates nonzero version and emits version.

This file is important for conflict resolution because LVM’s wiper hint tells safe probing that stale partition-table signatures inside the wiped start area should be ignored after an LVM match.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/minix.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/minix.c

Minix filesystem detector for versions 1, 2, and 3 in native or swapped endianness. It reads the superblock at 1024 bytes, classifies version from magic values, and records whether byte-swapping is needed.

The probe validates state bits for v1/v2, inode and zone bitmap capacity, first data zone bounds, zero zone-size shift, and nonzero sane inode counts. It also reads the ext-family magic location and rejects matches that are actually ext filesystems, because ext metadata can otherwise resemble Minix.

On success it emits version, filesystem/device block size, and endianness. Labels and UUIDs are not part of this detector.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/minix.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/mpool.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/mpool.c

mpool detector. It matches the ASCII `mpoolDev` magic, reads the superblock descriptor, and validates CRC32C over all descriptor fields preceding the checksum field.

On success it emits pool label and pool UUID. It reports filesystem usage under name `mpool`; the detector is compact and relies on magic plus checksum for false-positive resistance.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/mpool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/netware.c -->
# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/netware.c

NetWare NSS detector. It matches `SPB5` at 4 KiB, reads the NSS superblock, emits the pool UUID from `SBH_PoolID`, and formats the media version as major.two-digit-minor.

The idinfo reports filesystem usage under name `nss`. The probe does not validate the many other NSS structure fields or checksum; identity is based on magic and readable superblock fields.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libblkid/src/superblocks/netware.c -->