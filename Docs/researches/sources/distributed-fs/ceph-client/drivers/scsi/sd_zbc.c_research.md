# sources/distributed-fs/ceph-client/drivers/scsi/sd_zbc.c

## Purpose

`sd_zbc.c` implements SCSI Zoned Block Commands support for host-managed ZBC disks. It validates zoned characteristics, reads zone topology, publishes zoned queue limits, reports zones to the block layer, maps block zone-management operations to SCSI ZBC OUT commands, and handles ZBC-specific completion quirks.

## Important APIs, Types, and Functions

Public functions are `sd_zbc_read_zones()`, `sd_zbc_revalidate_zones()`, `sd_zbc_setup_zone_mgmt_cmnd()`, `sd_zbc_complete()`, and `sd_zbc_report_zones()`. Internal helpers parse REPORT ZONES descriptors, allocate bounded report buffers, issue REPORT ZONES, validate VPD B6 characteristics, check capacity and zone size, and print topology.

Key state fields are `early_zone_info`, `zone_info`, `zones_max_open`, `zone_starting_lba_gran`, `urswrz`, `capacity`, and `rc_basis` in `struct scsi_disk`.

## Control Flow

`sd_zbc_read_zones()` runs during disk revalidation before capacity is committed. It skips non-ZBC devices, enables zoned queue features, forces READ/WRITE/SYNC(16), sets zone write granularity, reads zoned characteristics, rejects constrained-read host-managed devices, validates alignment method, checks capacity and zone size using REPORT ZONES, computes zone count, and fills queue limits.

`sd_zbc_revalidate_zones()` runs after capacity publication. If topology changed, it copies early zone info to live zone info and calls `blk_revalidate_disk_zones()` under `memalloc_noio_save()`, clearing capacity on failure.

`sd_zbc_report_zones()` implements `.report_zones()`. It allocates a report buffer constrained by queue limits, loops over partial REPORT ZONES replies, validates descriptor continuity, handles gap zones only when constant starting-LBA granularity allows it, converts descriptors to `struct blk_zone`, and calls `disk_report_zone()`.

Zone management requests call `sd_zbc_setup_zone_mgmt_cmnd()`, which checks disk type, media-change state, and zone alignment before building RESET WRITE POINTER, OPEN, CLOSE, or FINISH ZBC OUT commands. `sd_zbc_complete()` quiets invalid-field errors for management commands aimed at conventional zones.

## State and Persistence Behavior

Zoned topology persists in `struct scsi_disk` and committed queue limits. `early_zone_info` stages data before capacity is known; `zone_info` mirrors topology accepted by the block layer. The file does not maintain a separate write-pointer cache in this snapshot; REPORT ZONES remains authoritative.

## Dependencies and Integration Points

The file depends on SCSI command execution, ZBC constants, block zoned APIs, queue limits, `blk_revalidate_disk_zones()`, `disk_report_zone()`, vmalloc-backed buffers, and `sd_trace.h`. `sd.c` calls it from revalidation, request setup, completion, and block operations.

## Risks and Edge Cases

The driver must reject unsupported topology: constrained reads, non-power-of-two zone sizes, invalid start granularity, short REPORT ZONES replies, discontinuous descriptors, invalid capacity, and gap zones without constant offsets. Report buffers cannot be split, so allocation must respect max hardware sectors and segment limits. Revalidation failure deliberately zeroes capacity to avoid exposing inconsistent zone information.

## Test Signals

Test ZBC probing, VPD B6 failures, constrained-read rejection, constant length versus constant start-offset devices, invalid granularity, non-power-of-two zone size, capacity correction, runt final zones, topology changes, report-zones iteration, gap-zone handling, zone reset/open/close/finish commands, unaligned request rejection, and queue-limit values.
