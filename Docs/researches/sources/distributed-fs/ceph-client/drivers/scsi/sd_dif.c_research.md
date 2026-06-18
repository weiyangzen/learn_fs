# sources/distributed-fs/ceph-client/drivers/scsi/sd_dif.c

## Purpose

`sd_dif.c` configures SCSI disk Data Integrity Field/Data Integrity Extensions support for the block layer. It translates disk protection type and SCSI host DIF/DIX capabilities into `struct blk_integrity` queue limits.

## Important APIs, Types, and Functions

The only function is `sd_dif_config_host(struct scsi_disk *sdkp, struct queue_limits *lim)`. It uses `sdkp->protection_type`, `scsi_host_dif_capable()`, `scsi_host_dix_capable()`, `scsi_host_get_guard()`, `struct blk_integrity`, `struct t10_pi_tuple`, and `BLK_INTEGRITY_*` flags.

## Control Flow

The caller zeroes and rebuilds queue limits during disk revalidation. This function clears `lim->integrity`, checks DIF and DIX support, falls back to Type 0 DIX when the exact type lacks DIX but host-only DIX is available, and returns if DIX is not available. It selects IP or CRC guard checksum, sets metadata and tuple size, enables reference-tag handling for non-Type 3 protection, marks device-capable DIF when host and disk support it, and sets application-tag size only when the disk's ATO bit grants OS ownership.

## State and Persistence Behavior

There is no private state. The function mutates only `lim->integrity`; the values persist after `queue_limits_commit_update_frozen()` succeeds in `sd_revalidate_disk()`.

## Dependencies and Integration Points

This file integrates SCSI host protection capabilities with the block integrity layer. `sd.c` discovers protection type, invokes this helper during revalidation, sets protection operations per command, and interprets protected-I/O completion errors.

## Risks and Edge Cases

The Type 0 DIX fallback is subtle because it enables host-side metadata exchange without device DIF. Incorrect host capability reporting can expose unsupported integrity modes or hide working ones. Application-tag size depends on both protection type and ATO, and must remain consistent with command setup.

## Test Signals

Test no-DIX hosts, Type 0-only DIX, full DIX/DIF for Type 1/2/3, IP versus CRC guard support, disks with and without ATO, and protected read/write I/O that verifies guard, reference tag, and application tag handling.
