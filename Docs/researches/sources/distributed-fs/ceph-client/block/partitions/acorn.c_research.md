<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/acorn.c -->
# sources/distributed-fs/ceph-client/block/partitions/acorn.c

## Purpose
`acorn.c` implements partition detection for multiple Acorn/RISC OS disk-label variants: Cumana, native ADFS, ICS, PowerTec, EESOX, and optional RISCiX/Linux subformats. It reflects the lack of a single Acorn partition standard.

## Important APIs, Types, and Functions
- Shared helpers: `adfs_partition()`, `linux_partition()`, optional `riscix_partition()`.
- Parser entry points: `adfspart_check_CUMANA()`, `adfspart_check_ADFS()`, `adfspart_check_ICS()`, `adfspart_check_POWERTEC()`, and `adfspart_check_EESOX()`.
- On-disk structs: `riscix_record`, `riscix_part`, `linux_part`, `ics_part`, `ptec_part`, and `eesox_part`.
- Validation helpers: `valid_ics_sector()`, `valid_ptec_sector()`, and `adfspart_check_ICSLinux()`.

## Control Flow
Each parser reads fixed sectors with `read_part_sector()`, validates magic/checksum/ADFS boot block data, emits parser tags to `pp_buf`, and calls `put_partition()` for discovered ranges. ADFS and Cumana use sector 6 boot-block data and may delegate non-ADFS regions to RISCiX or Linux parsers. ICS reads sector 0, validates a checksum seeded with `0x50617274`, interprets signed sizes, and can hide a Linux marker sector by advancing start/size. PowerTec reads sector 0, rejects PC MBR signatures, validates a checksum, and scans twelve entries. EESOX reads sector 7, XOR-decodes a 256-byte table with a fixed name key, derives partition sizes from successive starts, and makes the final partition extend to disk capacity.

## State and Persistence Behavior
There is no runtime state beyond `parsed_partitions`. The parser translates vendor-specific on-disk metadata into kernel partition records and informational printk text. It does not write disk metadata.

## Dependencies and Integration Points
It depends on ADFS filesystem disk-record helpers, `check.h`, partition core probe ordering, and Kconfig suboptions. It must run before more generic parsers when stale PC tables may coexist with Acorn metadata.

## Risks and Edge Cases
Several formats have uncertain or historically incomplete semantics. Cumana code explicitly notes untested behavior and unclear next-partition sizing. EESOX stores starts but not sizes, making derived sizes fragile. Signed ICS sizes are overloaded as ignore markers. All parsers must avoid sector leaks on early breaks; this file has complex `put_dev_sector()` paths.

## Test Signals
Use disk images for each Acorn variant, malformed checksum/magic cases, negative ICS sizes with Linux marker sectors, EESOX final-size behavior, partition-limit truncation, stale MBR coexistence, and memory/folio leak checks around early exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/acorn.c -->
