# Group Research: group_358_exfatprogs_sources_local_fs_exfatprogs_fsck_Makefile_am_sources_loca_edd4ac70cad1

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/local-fs/exfatprogs`. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/fsck/Makefile.am -->
# File Research: sources/local-fs/exfatprogs/fsck/Makefile.am

This Automake file builds the `fsck.exfat` program.

It sets common C flags with warnings, generated `config.h`, the project `include` path, and `-fno-common`. The binary links against the internal static library `$(top_builddir)/lib/libexfat.a`.

The program source list is tightly scoped to the checker implementation and repair UI:
- `fsck.c`
- `repair.c`
- `fsck.h`
- `repair.h`

This file has no conditional build logic; `fsck.exfat` is always listed in `sbin_PROGRAMS`.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/fsck/fsck.c -->
# File Research: sources/local-fs/exfatprogs/fsck/fsck.c

`fsck.c` is the main implementation for `fsck.exfat`. It validates exFAT boot regions, root metadata, allocation bitmap, upcase table, directory entries, file cluster chains, optional orphan-cluster rescue, and optional recursive MBR state.

The file owns the program globals:
- `struct exfat_fsck exfat_fsck`, holding the mounted exFAT context, directory iterator buffers, repair options, MBR mode, dirty flags, per-directory name hash bitmap, and progress bar.
- `struct exfat_stat exfat_stat`, counting directories, files, errors, and fixes.
- `struct path_resolve_ctx path_resolve_ctx`, used to print path-aware diagnostics.

CLI handling supports `-r/-y/-n/-p/-a`, rescue with `-s`, bad filesystem-name bypass with `-b`, progress with `-P`, verbosity, version/help, and long-only `--put-mbr` / `--clear-mbr`. Write-capable modes are encoded by `FSCK_OPTS_REPAIR_WRITE`; read-only checking defaults to `FSCK_OPTS_REPAIR_NO`. Interactive repair and progress are rejected together.

Boot-region handling is layered:
- `boot_region_checksum()` recomputes the 11-sector boot checksum and compares all words in the checksum sector.
- `read_boot_region()` reads and validates OEM name, checksum, sector size, cluster size, exFAT version, FAT count, volume length, and cluster count.
- `exfat_boot_region_check()` first reads sector size from the main boot sector, optionally allows bad OEM names under `-b`, tries the main region, and can restore from the backup boot region through `restore_boot_region()`.
- `exfat_mark_volume_dirty()` sets or clears the VolumeDirty flag in the boot sector and fsyncs after write.

Cluster-chain checking is central to consistency:
- `check_clus_chain()` validates a file or vendor-allocation dentry stream against file size, first cluster, FAT chain, heap bounds, duplicate cluster usage, BAD clusters, free-on-disk clusters, and too-short/too-long chains. Repair truncates the stream, updates stream dentries, and may terminate FAT at the last valid cluster.
- `root_check_clus_chain()` performs similar traversal for the root directory and guards against cyclic or broken root chains.
- The in-memory `alloc_bitmap` is populated as reachable clusters are discovered, then later compared/written against the on-disk allocation bitmap.

Directory-entry validation flows through:
- `file_calc_checksum()` recomputes a file dentry set checksum.
- `read_file_dentry_set()` validates the primary file dentry, stream dentry, name dentries, secondary counts, vendor extension/allocation entries, stream valid size, unknown dentries, and deletion/skip behavior for unrecoverable dentry sets.
- `check_name_dentry_set()` validates UTF-16 name length, invalid characters, name hash, and per-directory duplicate-name hashes. Duplicate or invalid names can route to `exfat_repair_rename_ask()`.
- `handle_dot_dotdot_filename()` rejects all-dot names that are not allowed on exFAT.
- `check_inode()` validates cluster chain, file size against cluster heap, empty contiguous streams, directory size alignment, and dentry-set checksum repair.

Root metadata checks are in `exfat_root_dir_check()`: it initializes root cluster/size, reads the volume label, reads the allocation bitmap, reads or repairs the upcase table, and builds an in-memory root dentry set. `read_bitmap()` validates bitmap dentry size and start cluster, stores bitmap cluster/size in `struct exfat`, marks bitmap clusters allocated, and loads the disk bitmap.

Upcase handling includes:
- `decompress_upcase_table()`, which expands compressed 0xFFFF skip-runs into a full uppercase mapping.
- `read_upcase_table()`, which locates the root upcase dentry, validates cluster, size, contents, and checksum, marks its clusters allocated, and falls back to the built-in default table when invalid.
- `exfat_repair_upcase_table()`, which writes the default upcase table and root dentry if the table entry or data is missing/corrupt.

Filesystem traversal is breadth/list based:
- `read_children()` iterates dentries in a directory, processes file dentry sets, handles `EXFAT_LAST` with `check_unused_dentry()`, tolerates root-only metadata entries, and repairs unknown live dentries by deleting them when permitted.
- `exfat_filesystem_check()` seeds `exfat->dir_list` with root, walks queued subdirectories, frees file children and ancestors as traversal advances, and cleans up the directory list.

Allocation reconciliation:
- `write_bitmap()` writes only changed 512-byte-aligned bitmap segments, using `alloc_bitmap | disk_bitmap`; this preserves already-marked allocated clusters unless rescue or other repair changes state.
- `rescue_orphan_clusters()` computes clusters marked allocated on disk but not referenced by scanned files, creates `LOST+FOUND`, and creates contiguous `FILE%07d.CHK` entries for orphan ranges.

MBR-related code:
- `do_recursive_mbr()` checks for copy-protected MBR markers, recognizes already-recursive MBR partition state, selects whether a partition table is suitable for Windows, and asks to write a recursive MBR when needed.
- `do_put_mbr()` rewrites bootstrap/partition entries in both main and backup boot regions, recalculates boot checksums, and can either place a recursive partition entry or clear partition entries.

`main()` wires the complete workflow: parse options, open block device, validate/repair boot region, handle MBR mode, allocate root/exFAT/buffers, mark volume dirty for write repairs, check root, optionally initialize progress by used cluster count, traverse filesystem, optionally rescue orphan clusters, write bitmap, fsync, clear VolumeDirty, print summary, free resources, and return fsck-style exit bits.

Notable dependencies are `libexfat` for device I/O, FAT/bitmap operations, dentry iterators, name encoding/hash/checks, path resolution, progress bar, and boot checksum helpers; `repair.c` supplies all user/auto repair decisions.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/fsck/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/fsck/fsck.h -->
# File Research: sources/local-fs/exfatprogs/fsck/fsck.h

`fsck.h` declares the shared checker state and option bitmask used by `fsck.c` and `repair.c`.

`enum fsck_ui_options` defines repair behavior and auxiliary flags:
- ask, yes, no, auto repair modes.
- `FSCK_OPTS_REPAIR_WRITE` as the write-capable repair-mode mask.
- `FSCK_OPTS_REPAIR_ALL` as all repair policy bits.
- bad filesystem-name ignore, orphan-cluster rescue, and progress bar flags.

`struct exfat_fsck` holds:
- the active `struct exfat *`.
- a reusable directory iterator and cluster buffer descriptors.
- selected options.
- signed MBR operation state.
- dirty and dirty-FAT booleans.
- per-directory filename hash bitmap.
- progress bar state.

The header forward-declares `struct exfat` and `struct exfat_inode`, includes list/utils helpers, and exposes `off_t exfat_c2o(struct exfat *exfat, unsigned int clus)` for cluster-to-device-offset conversion implemented elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/fsck/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/fsck/repair.c -->
# File Research: sources/local-fs/exfatprogs/fsck/repair.c

`repair.c` implements the repair policy and prompting layer used by `fsck.c`. It maps problem codes from `repair.h` to prompt type, default behavior, preen eligibility, and rename menu defaults.

The core table `problems[]` classifies each repairable condition:
- boot checksum/boot region fixes.
- corrupt or unknown dentry deletion/fix cases.
- file dentry secondary count, stream/name/hash/length fixes.
- rename cases for dot names, duplicate names, and invalid names.
- file size/cluster-chain truncation cases.
- vendor GUID warning defaulting to no.
- recursive MBR required and MBR clear operations.

`ask_repair()` applies global fsck options:
- `-n` or problem default-no refuses repair.
- `-y` or default-yes accepts repair.
- interactive ask mode reads `stdin`.
- auto/preen mode accepts only problems flagged `ERF_PREEN_YES`.
- rename prompts return menu numbers rather than booleans.

`exfat_repair_ask()` prints the formatted problem description, obtains a decision, and marks `fsck->dirty` for accepted repairs. Truncation-style repairs additionally mark `fsck->dirty_fat`.

Rename repair support has two paths:
- `get_rename_from_user()` reads a new name, UTF-16 encodes it, validates exFAT filename rules, flushes pending iterator state, and rejects names already present in the parent directory.
- `generate_rename()` auto-generates `FILE%07d.CHK` names using `iter->invalid_name_num`, skipping collisions.

`exfat_repair_rename_ask()` decodes the old UTF-16 name for display, presents a three-choice menu, obtains or generates a UTF-16 replacement, updates the first name dentry, recalculates the name hash, and patches the stream dentry name length/hash. It returns `1` for repaired, `0` for declined, and negative on invalid/unrecoverable rename flow.

The file depends on directory iterator dirty access and lookup helpers from `libexfat`/`exfat_dir`, but it intentionally does not perform broader filesystem traversal itself.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/fsck/repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/fsck/repair.h -->
# File Research: sources/local-fs/exfatprogs/fsck/repair.h

`repair.h` defines the repair problem-code namespace and public repair functions for `fsck.exfat`.

Problem codes are grouped by broad area:
- `ER_BS_*` for boot-sector/checksum/boot-region issues.
- `ER_DE_*` for directory entry set issues, including checksum, unknown/unused entries, file/stream/name fields, duplicated/invalid/dot names, upcase, and bitmap entries.
- `ER_FILE_*` for valid size, invalid clusters, first cluster, smaller/larger size mismatches, duplicate clusters, and zero-size no-FAT cases.
- `ER_VENDOR_GUID` for vendor extension GUID anomalies.
- `ER_MBR_*` for recursive MBR requirements and clearing.

It typedefs `er_problem_code_t` to `unsigned int`, forward-declares `struct exfat_fsck`, and declares:
- `exfat_repair_ask()` for generic repair prompts.
- `exfat_repair_rename_ask()` for filename-specific repairs that need dentry iterator and UTF-16 name mutation.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/fsck/repair.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/Makefile.am -->
# File Research: sources/local-fs/exfatprogs/mkfs/Makefile.am

This Automake file builds the `mkfs.exfat` program.

It sets warnings, generated `config.h`, the project include path, `-fno-common`, and `$(BLKID_CFLAGS)`. The binary links against internal `libexfat.a` and `$(BLKID_LIBS)` for existing-signature detection and library version reporting.

The program source list is:
- `mkfs.c`
- `upcase.c`
- `mkfs.h`
- `crc.c`

There is no conditional source selection in this file; `mkfs.exfat` is always installed via `sbin_PROGRAMS`.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/crc.c -->
# File Research: sources/local-fs/exfatprogs/mkfs/crc.c

`crc.c` supplies EFI/GPT CRC32 support for `mkfs.exfat`.

It contains a static little-endian CRC32 table derived from Gary S. Brown’s public-domain table and implements:
- `crc32_le_base()`, a local table-driven little-endian CRC update helper.
- `exfat_efi_crc32()`, the exported wrapper used by GPT construction. It starts with all bits set, processes the buffer, then bitwise-inverts the result, matching common EFI CRC32 behavior.

`mkfs.c` uses this function to compute:
- GPT partition entry array CRC.
- GPT main header CRC.
- GPT backup header CRC.

The file is self-contained apart from project headers and does not allocate memory or perform I/O.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/mkfs.c -->
# File Research: sources/local-fs/exfatprogs/mkfs/mkfs.c

`mkfs.c` is the main implementation for `mkfs.exfat`. It parses formatting options, probes the target, optionally builds a GPT or MBR wrapper, computes exFAT layout geometry, discards/zeros target ranges, writes all filesystem metadata, verifies writes when requested, and rolls back GPT structures on failure.

Global state:
- `struct exfat_mkfs_info finfo` stores target offsets/lengths, FAT/cluster/bitmap/upcase/root layout, volume serial, and owned GPT buffers/regions.
- `fd_rnddev` caches `/dev/urandom` for GUID generation.

Option handling supports volume label/GUID, sector size, cluster size, boundary alignment, bitmap packing, custom upcase table, custom bootcode message, partition-table mode, full format, force overwrite, read-back verification, no-discard, quiet/verbose, version, and help. Existing filesystem/partition signatures are detected through libblkid; interactive terminals refuse overwrite unless `-F` is set.

Partition-table support:
- `build_gpt()` constructs protective MBR, main/backup GPT headers, and a 128-entry GPT partition-entry array. It enforces 1 MiB minimum alignment for GPT, checks device alignment offset, calculates usable/aligned bounds, assigns GUIDs, computes EFI CRC32 values, and transfers buffers into `finfo.gpt`.
- `exfat_setup_boot_sector()` embeds exFAT BPB/BSX fields and can place a recursive MBR partition entry when `PART_TABLE_MBR` is selected.
- GPT writes are performed before exFAT metadata, after endian conversion. On later failure, `exfat_zero_mkfs_data_regions()` and `exfat_write_mkfs_data_regions()` wipe the GPT regions.

Filesystem layout is computed by `exfat_build_mkfs_info()`. It sets target sector/byte region, validates cluster and boundary sizes, places the FAT after the 24-sector boot area rounded to boundary alignment, computes FAT length from maximum clusters, places the cluster heap, places allocation bitmap, optionally moves the bitmap with `exfat_pack_bitmap()`, then lays out upcase table and root directory clusters. It also computes the upcase checksum and generates a timestamp-derived volume serial.

Metadata writing sequence in `make_exfat()`:
1. Main volume boot record via `exfat_create_volume_boot_record()`.
2. Backup volume boot record.
3. FAT table via `exfat_create_fat_table()`.
4. Allocation bitmap via `exfat_create_bitmap()`.
5. Upcase table via `exfat_create_upcase_table()` from `upcase.c`.
6. Root directory entries via `exfat_create_root_dir()`.

Boot-record writing is split into:
- `exfat_write_boot_sector()` for the PBR and checksum update.
- `exfat_write_extended_boot_sectors()` for extended boot sectors with signatures.
- `exfat_write_oem_sector()` for OEM and reserved sectors.
- `exfat_create_volume_boot_record()` to write the checksum sector after the preceding sectors.

FAT and allocation data:
- `write_fat_entry()` writes individual FAT entries and mirrors them in a verification buffer when `-C` is used.
- `write_fat_entries()` creates linked cluster chains ending in `EXFAT_EOF_CLUSTER`.
- `exfat_create_fat_table()` writes reserved entries 0/1, then chains for bitmap, upcase table, and root directory, and records `finfo.used_clu_cnt`.
- `exfat_create_bitmap()` creates an allocation bitmap with bits set for the metadata clusters already consumed.

Root directory creation writes initial dentries:
- volume label dentry.
- volume GUID dentry if requested, otherwise a reserved invalid GUID slot.
- allocation bitmap dentry.
- upcase table dentry when upcase length is nonzero.

Upcase handling:
- `exfat_load_upcase()` defaults to the built-in default upcase table or loads a user-supplied binary file by `mmap()` or read fallback. It does not validate supplied table semantics, only size/empty conditions.
- `exfat_free_upcase()` dispatches to `munmap` or `free`.

Device preparation:
- `exfat_discard_dev()` issues block discard in 2 GiB chunks for block devices unless disabled.
- `exfat_zero_out_disk()` writes zeros to either the first `EXFAT_HEAD_ZERO_OUT` bytes for quick format or the full device for full format; optional verification rereads zeroed ranges.
- `check_existing_filesystem()` uses blkid to detect existing filesystem and partition table signatures.

Utility routines include `parse_size()` for K/M suffix parsing with overflow checks; random GUID helpers `exfat_open_rnddev()`, `exfat_close_rnddev()`, and `exfat_gen_guid()`; and GPT region write/verify helpers.

Notable implementation detail: the long option table declares `{"partition-table", no_argument, NULL, 'P'}` while the short option string uses `P:` and the handler expects `optarg`. The intended CLI documented by usage is `--partition-table=auto|none|mbr|gpt`; the table entry appears inconsistent with that intended behavior.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/mkfs.h -->
# File Research: sources/local-fs/exfatprogs/mkfs/mkfs.h

`mkfs.h` declares mkfs layout constants, GPT structures, global formatting state, and helper functions shared by `mkfs.c`, `upcase.c`, and `crc.c`.

Key constants:
- `MIN_NUM_SECTOR` minimum target size in sectors.
- `EXFAT_MAX_CLUSTER_SIZE` as 32 MiB.
- `EXFAT_HEAD_ZERO_OUT` quick-format zeroing length.
- GPT entry size/count/array size and 1 MiB minimum GPT partition alignment.

`struct exfat_mkfs_data_region` describes an offset, length, and backing buffer for GPT region writes/verification/wipe.

`struct exfat_mkfs_info` is the central geometry/result structure:
- target sector/byte offsets and lengths.
- cluster counts and used cluster count.
- FAT, cluster heap, bitmap, upcase table, and root directory offsets/lengths/start clusters.
- upcase checksum and volume serial.
- GPT-owned buffers for protective MBR, main/backup headers, entry array, and data regions.

The header defines packed GPT structs:
- `struct exfat_guid`.
- `struct exfat_gpt_header`.
- `struct exfat_gpt_entry_attrs`.
- `struct exfat_gpt_entry`.

It declares global `finfo`, `exfat_create_upcase_table()`, GPT print macro `exfat_print_gpt_header()`, GPT region helpers, `exfat_efi_crc32()`, and GUID entropy helpers.

The header has a minor guard oddity: it uses `#ifndef _MKFS_H` but does not visibly `#define _MKFS_H` before declarations, so repeated inclusion protection depends on external context or is incomplete in this file as read.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/mkfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/upcase.c -->
# File Research: sources/local-fs/exfatprogs/mkfs/upcase.c

`upcase.c` writes the exFAT upcase table during filesystem creation.

`exfat_create_upcase_table()` writes `ui->upcase.table` of length `ui->upcase.len` to `finfo.target.byte.ofs + finfo.ut_byte_off`. When write verification is enabled, it rereads and compares the upcase table.

After writing the table bytes, it zero-fills the gap from the end of the table to the root directory offset:
- `zero_ofs = target + upcase offset + upcase length`
- `zero_len = root offset - upcase offset - upcase length`

It also verifies that zero-fill region when requested. On verification failure, it prints a specific upcase table mismatch error and returns the underlying error code.

The function asserts that the root directory offset is at or after the upcase-table offset, depends on the global `finfo` layout from `mkfs.c`, and uses libexfat full-write, zero-write, and verification helpers.
<!-- END FILE RESEARCH: sources/local-fs/exfatprogs/mkfs/upcase.c -->