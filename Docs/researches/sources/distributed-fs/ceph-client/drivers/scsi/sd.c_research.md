# sources/distributed-fs/ceph-client/drivers/scsi/sd.c

## Purpose

`sd.c` is the Linux SCSI disk driver. It binds SCSI disk-like devices to the block layer, publishes `/dev/sd*`, translates block requests into SCSI CDBs, probes media capacity and capabilities, manages cache/provisioning/protection/zoned policy, handles removable media, persistent reservations, power management, and SCSI disk lifecycle.

## Important APIs, Types, and Functions

The central object is `struct scsi_disk` from `sd.h`. Driver registration is `sd_template`, whose callbacks include probe/remove/shutdown/rescan/resume, request init/uninit, completion, and error handling. Block operations are `sd_fops`, including open/release/ioctl/getgeo/check_events/report_zones/get_unique_id/free_disk and PR ops.

Request setup is centered on `sd_init_command()`, dispatching to read/write, discard, write-zeroes, flush, and ZBC helpers. `sd_setup_read_write_cmnd()` chooses READ/WRITE(6/10/16/32), WRITE ATOMIC(16), FUA, command-duration-limit bits, and DIF/DIX protection. `sd_done()` computes completed bytes, interprets sense data, disables unsupported discard/write-same paths, and invokes ZBC completion handling.

Capability discovery is in `sd_revalidate_disk()` and helpers: `sd_spinup_disk()`, `sd_read_capacity()`, `read_capacity_10()`, `read_capacity_16()`, `sd_read_write_protect_flag()`, `sd_read_cache_type()`, `sd_read_block_limits()`, `sd_read_block_limits_ext()`, `sd_read_block_characteristics()`, `sd_read_block_provisioning()`, `sd_read_write_same()`, `sd_read_security()`, `sd_read_io_hints()`, `sd_read_app_tag_own()`, `sd_config_discard()`, `sd_config_write_same()`, `sd_config_atomic()`, and `sd_config_protection()`.

## Control Flow

`init_sd()` registers historical SCSI disk majors, the `scsi_disk` class, mempools, and the SCSI driver. `sd_probe()` filters supported SCSI device types, allocates `struct scsi_disk` and a `gendisk`, assigns an IDA-backed `sd[a-z]+` name, creates the class device, initializes defaults, revalidates the disk, configures removable and runtime-PM behavior, publishes the disk, and initializes OPAL support when present.

Normal I/O enters through SCSI midlayer request initialization. Read/write setup validates device online/changed state, capacity bounds, logical-block alignment, protection metadata, and CDB limits. Discard maps to UNMAP or WRITE SAME with UNMAP depending on provisioning mode. Write-zeroes chooses WRITE SAME or UNMAP semantics according to zeroing mode and `REQ_NOUNMAP`. Flush maps to SYNCHRONIZE CACHE(10/16). Zone operations are delegated to `sd_zbc_setup_zone_mgmt_cmnd()`.

Open/release take SCSI device references, wait for error processing, revalidate removable/write-protected media, fail no-media or write-protected write opens, and prevent/allow medium removal on first open/last close. Shutdown and suspend synchronize cache when needed and optionally send START STOP UNIT; resume starts disks and handles OPAL unlock.

## State and Persistence Behavior

`struct scsi_disk` persists until disk removal and stores capacity, queue-limit inputs, cache bits, media state, protection/provisioning/zoned/security state, retry policy, and suspend state. Queue limits are rebuilt on revalidation and committed frozen to the block queue. Capacity is tracked in logical blocks and published to the block layer in 512-byte sectors. Mempools provide special payload pages for UNMAP and WRITE SAME/zeroes.

## Dependencies and Integration Points

The driver integrates the SCSI midlayer, block layer, blk-mq, runtime PM, sysfs class devices, VPD/mode-sense/report-opcode helpers, SCSI EH, persistent reservations, optional OPAL, optional block integrity through `sd_dif_config_host()`, optional zoned support through `sd_zbc_*()`, and legacy geometry through `scsicam_bios_param()`.

## Risks and Edge Cases

The file contains extensive quirk handling for broken capacity reports, mode pages, FUA, WRITE SAME/UNMAP, last-sector access, USB/UAS mode-page population, invalid sector sizes, and removable media. Request setup must keep logical-block conversions, protection metadata, CDB limits, and queue limits synchronized. Revalidation can change visible queue capabilities while the disk exists. Power paths must treat benign shutdown/suspend errors carefully without hiding real runtime failures.

## Test Signals

Test probe/revalidation for READ CAPACITY(10/16), sector-size variants, VPD block limits, provisioning, write protect, cache modes, write-same, OPAL, rotational flags, CPR ranges, and queue-limit commits. Request tests should cover READ/WRITE CDB selection, FUA, DIX/DIF, Type 2 protection, atomic writes, unaligned and beyond-end rejection, discard/write-zeroes modes, flush, special-payload cleanup, PR ops, media events, suspend/resume/shutdown, and EH offlining after repeated medium-access timeouts.
