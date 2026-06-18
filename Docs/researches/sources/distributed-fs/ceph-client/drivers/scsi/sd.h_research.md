# sources/distributed-fs/ceph-client/drivers/scsi/sd.h

## Purpose

`sd.h` is the private header shared by the SCSI disk implementation files. It defines disk constants, `struct scsi_disk`, zoned metadata, conversion helpers, medium-access command classification, logging macros, and DIF/ZBC helper prototypes or stubs.

## Important APIs, Types, and Functions

Constants define major counts, timeouts, retry limits, buffer sizes, transfer limits, provisioning modes, and zeroing modes. `struct zoned_disk_info` stores zone count and zone size. `struct scsi_disk` stores the SCSI device, gendisk, class device, capacity, queue-limit inputs, discard/unmap/write-same/atomic fields, zoned fields, media/cache/protection/security/provisioning flags, retry policy, and suspend state.

Inline helpers include `scsi_disk()`, `sd_printk()`, `sd_first_printk()`, `scsi_medium_access_command()`, `logical_to_sectors()`, `logical_to_bytes()`, `bytes_to_logical()`, and `sectors_to_logical()`.

## Control Flow

The header has no module flow, but its helpers participate in hot paths. `scsi_medium_access_command()` is used by SCSI disk error handling. Conversion helpers are used in request setup, capacity publishing, queue limits, and ZBC parsing. When zoned block support is disabled, inline stubs make zone probing a no-op, zone commands fail with target status, completion pass through, and `.report_zones` is `NULL`.

## State and Persistence Behavior

`struct scsi_disk` is mutable runtime state updated by probe, revalidation, sysfs stores, request completion, error handling, and power management. Many bitfields mirror device capabilities or selected policy and must remain synchronized with committed block queue limits. Conversion helpers assume a validated power-of-two logical block size of at least 512 bytes.

## Dependencies and Integration Points

The header connects `sd.c`, `sd_dif.c`, and `sd_zbc.c` to SCSI and block-layer types. It is the shared contract for optional block integrity and zoned support.

## Risks and Edge Cases

The compact bitfield state is easy to confuse between device capability, active mode, and user override. Any change to `struct scsi_disk` semantics can affect sysfs, revalidation, queue-limit setup, request setup, completion, and PM paths. Sector-size validation in `sd.c` is critical because conversion helpers use shifts based on `ilog2(sector_size)`.

## Test Signals

Compile with zoned support enabled and disabled, block integrity enabled and disabled, and OPAL enabled and disabled. Check logical/sector/byte conversions for 512, 4096, and larger power-of-two block sizes and verify `scsi_medium_access_command()` coverage for read/write/verify/sync/unmap and variable-length CDBs.
