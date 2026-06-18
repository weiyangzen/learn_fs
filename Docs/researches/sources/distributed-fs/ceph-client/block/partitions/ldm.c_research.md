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
