<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.c -->
# sources/distributed-fs/ceph-client/block/partitions/efi.c

## Purpose
`efi.c` implements GUID Partition Table detection and parsing. It validates protective or hybrid MBRs, primary and alternate GPT headers, partition-entry CRCs, and emits Linux partition records with PARTUUID/PARTNAME metadata.

## Important APIs, Types, and Functions
- Entry point: `efi_partition()`.
- Validation helpers: `efi_crc32()`, `is_pmbr_valid()`, `pmbr_part_valid()`, `is_gpt_valid()`, `is_pte_valid()`, `compare_gpts()`, and `find_valid_gpt()`.
- Reading helpers: `last_lba()`, `read_lba()`, `alloc_read_gpt_header()`, `alloc_read_gpt_entries()`.
- Metadata conversion: `utf16_le_to_7bit()`.
- Boot override: `__setup("gpt", force_gpt_fn)` sets `force_gpt`.

## Control Flow
`efi_partition()` calls `find_valid_gpt()`. Unless `force_gpt` is set, `find_valid_gpt()` first reads LBA 0, validates MBR signature and a protective 0xEE record at LBA 1, and distinguishes hybrid MBRs. It validates the primary GPT at LBA 1 and, if good, validates the alternate GPT at the primary header’s `alternate_lba`. With `force_gpt`, it can also try the last LBA or driver-provided `alternative_gpt_sector()`.

`is_gpt_valid()` reads a logical-block-sized header, checks signature, header size range, header CRC with the CRC field zeroed, `my_lba`, usable-LBA bounds, entry size, table allocation size, reads the entry array, and verifies entry-array CRC. `compare_gpts()` warns on mismatches between primary and alternate headers.

After a valid GPT is selected, `efi_partition()` iterates entries up to the kernel partition limit. Non-null type GUIDs with in-range start/end LBAs become partitions after scaling logical blocks to 512-byte sectors. Linux RAID type GUID sets `ADDPART_FLAG_RAID`; unique partition GUID becomes `info.uuid`; UTF-16LE partition name is converted to printable 7-bit `info.volname`.

## State and Persistence Behavior
No on-disk GPT metadata is changed. Runtime state includes the global `force_gpt` flag and allocated header/entry buffers. Parsed metadata becomes partition device ranges, RAID flags, PARTUUID, and PARTNAME.

## Dependencies and Integration Points
It depends on CRC32, EFI GUID helpers, logical block size from the request queue, generic sector reads, optional driver `alternative_gpt_sector`, MD autodetect via RAID flag in core, and Kconfig `EFI_PARTITION` selecting `CRC32`.

## Risks and Edge Cases
GPT validation is intentionally strict for header CRC, entry CRC, entry size, and usable LBA bounds. Protective MBR size mismatches are only debug warnings to support cloned images. `read_lba()` reads in 512-byte sectors after multiplying by logical-block sectors, so logical block size handling must be correct. `force_gpt` bypasses PMBR protection and can expose stale or unintended GPTs.

## Test Signals
Use GPT images with valid primary/alternate headers, corrupt primary fallback to alternate, corrupt CRCs, hybrid MBRs, missing PMBR with and without `gpt`, non-512 logical block devices, RAID GUID entries, long/nonprintable UTF-16 names, oversized entry arrays, alternate GPT sector callbacks, and fuzzed GPT headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.c -->
