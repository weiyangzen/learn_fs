# subset-b-005354 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_srp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_srp.c

## Purpose

`scsi_transport_srp.c` implements the SCSI RDMA Protocol transport class. It gives SRP low-level drivers a common way to publish remote target ports under a SCSI host, expose SRP-specific sysfs attributes, drive transport-layer failure timers, and coordinate reconnect/fail-fast/device-loss behavior with the SCSI midlayer.

The file is not an SRP initiator implementation by itself. It is a transport support layer consumed through `struct srp_function_template`: an SRP HBA driver supplies callbacks such as `reconnect`, `terminate_rport_io`, and `rport_delete`, then calls `srp_attach_transport()` and `srp_rport_add()` to integrate its target ports into the driver core and SCSI error-handling model.

## Important APIs, Types, and Functions

The private transport wrapper is `struct srp_internal`, which embeds `struct scsi_transport_template`, points at the low-level `struct srp_function_template`, and owns host/rport attribute arrays plus the `srp_remote_ports` attribute container. `struct srp_host_attrs` stores the per-host `next_port_id` counter in `Scsi_Host.shost_data`.

Exported APIs are `srp_tmo_valid()`, `srp_parse_tmo()`, `srp_start_tl_fail_timers()`, `srp_reconnect_rport()`, `srp_timed_out()`, `srp_rport_get()`, `srp_rport_put()`, `srp_rport_add()`, `srp_rport_del()`, `srp_remove_host()`, `srp_stop_rport_timers()`, `srp_attach_transport()`, and `srp_release_transport()`.

The sysfs attribute surface includes `port_id`, `roles`, `state`, `reconnect_delay`, `failed_reconnects`, `fast_io_fail_tmo`, `dev_loss_tmo`, and optional write-only `delete`. Which attributes appear depends on callback and capability bits in the function template. Timeout strings use integer seconds or `off`, represented internally as `-1`.

The runtime state machine is `enum srp_rport_state`: `SRP_RPORT_RUNNING`, `SRP_RPORT_BLOCKED`, `SRP_RPORT_FAIL_FAST`, and `SRP_RPORT_LOST`. State transitions are centralized in `srp_rport_set_state()` and serialized by `rport->mutex`.

## Control Flow

Module initialization registers two transport classes: `srp_host` and `srp_remote_ports`. `srp_attach_transport()` allocates `struct srp_internal`, installs the host and rport attribute containers, selects attributes according to the function template, registers the containers, and returns the embedded transport template. `srp_release_transport()` unregisters those containers and frees the wrapper.

`srp_rport_add()` allocates and initializes an `srp_rport`, copies the target port ID and role bits, initializes delayed work for reconnect, fast-I/O-fail, and device-loss handling, seeds timeout defaults from the low-level template or built-ins, names the device `port-HOST:ID`, and publishes it through the transport and driver-core device model. `srp_rport_del()` reverses publication with `transport_remove_device()`, `device_del()`, `transport_destroy_device()`, and a final reference drop. `srp_remove_host()` deletes all SRP rport children below a host before the host is removed.

Transport failure handling starts with `srp_start_tl_fail_timers()`, which calls `__srp_start_tl_fail_timers()` under `rport->mutex`. If reconnect is enabled it schedules `reconnect_work`. If fail-fast or dev-loss timers are enabled it transitions the rport to `BLOCKED`, blocks SCSI targets, and schedules the relevant delayed work.

`srp_reconnect_work()` calls `srp_reconnect_rport()` and reschedules itself with an increasing backoff after failures. `srp_reconnect_rport()` blocks target command queueing before invoking the low-level `reconnect()` callback. On success it cancels fail timers, resets `failed_reconnects`, returns the rport to `RUNNING`, unblocks targets, and explicitly moves any devices left in `SDEV_OFFLINE` back to `SDEV_RUNNING`. On failure it either starts fail-fast plus timers for a formerly running rport, or unblocks with `SDEV_TRANSPORT_OFFLINE` when reconnect is no longer appropriate.

`rport_fast_io_fail_timedout()` moves a blocked rport to `FAIL_FAST`, unblocks targets as transport-offline, and invokes `terminate_rport_io()` when available. `rport_dev_loss_timedout()` moves the rport to `LOST`, unblocks targets as offline, and invokes `rport_delete()`. `srp_timed_out()` integrates with command timeout handling: if the port is blocked, both fail timers are disabled, the template asks for timer reset behavior, and the SCSI device is blocked, it returns `SCSI_EH_RESET_TIMER`; otherwise it leaves timeout processing to the SCSI core.

## State and Persistence Behavior

The persistent runtime objects are the transport template, SCSI host transport-private `shost_data`, and child `srp_rport` devices. `rport->state`, `failed_reconnects`, timeout fields, work items, and device references live until the rport release callback frees the object. Sysfs writes mutate the timeout fields immediately, and changing `reconnect_delay` can queue or cancel reconnect work depending on the old value and state.

Timeout validation intentionally prevents all recovery mechanisms from being disabled at once, rejects a zero reconnect delay, ensures fail-fast does not exceed `SCSI_DEVICE_BLOCK_MAX_TIMEOUT`, caps dev-loss against jiffies overflow, and requires fail-fast to be lower than dev-loss when both are active.

Device lifetime is reference-counted through the driver core. `srp_rport_release()` drops the parent host device reference and frees the rport. Timer stop is explicit: callers removing a host must call `srp_stop_rport_timers()` after `srp_remove_host()` and `scsi_remove_host()` while holding references to the rport and host.

## Dependencies and Integration Points

This file depends on the SCSI midlayer, SCSI transport attribute containers, `scsi_transport_srp.h`, delayed work on `system_long_wq`, driver-core devices, and SCSI target block/unblock helpers. Low-level SRP drivers integrate through `struct srp_function_template` and the exported SRP transport APIs. User-visible integration is via sysfs under SCSI transport devices.

The SCSI EH and blk timeout paths integrate through `srp_timed_out()`, `scsi_block_targets()`, `scsi_target_unblock()`, and low-level reconnect/terminate callbacks. The host removal path integrates through child device iteration below `shost_gendev`.

## Risks and Edge Cases

Timer/state races are the primary risk. The code relies on `rport->mutex` for state changes, but delayed work cancellation has to be sequenced by callers during teardown. `store_reconnect_delay()` contains duplicate `cancel_delayed_work(&rport->reconnect_work)` calls; this is harmless but suspicious and does not wait for an already running work item.

The state machine prohibits returning from `LOST` to `RUNNING` and only allows `BLOCKED` from `RUNNING`, but some paths ignore transition failures when they are expected no-ops. Low-level callbacks must honor the documented synchronization contract around `reconnect()` because this layer blocks new queueing but does not drain or abort outstanding commands itself.

Sysfs timeout changes are validated against the current values of the other timeouts. A user can make recovery more or less aggressive at runtime, but invalid combinations fail with `-EINVAL`. `srp_timed_out()` finds only one child rport under a host and warns if more are found, so this transport assumes the host/rport relationship used by current SRP drivers.

## Test Signals

Useful tests include loading and unloading an SRP transport user, verifying registration of `srp_host` and `srp_remote_ports`, adding and deleting rports, checking sysfs attribute visibility for different function templates, and validating timeout parsing for integers, `off`, invalid combinations, overflow-sized dev-loss values, and fail-fast greater than dev-loss.

Recovery tests should simulate blocked paths, reconnect success, repeated reconnect failure and backoff, fail-fast timeout, dev-loss timeout, `srp_timed_out()` with timers disabled, and host removal followed by `srp_stop_rport_timers()`. Reference tests should check that rport parent references and child devices are released after `srp_rport_del()` and `srp_remove_host()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_srp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsicam.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsicam.c

## Purpose

`scsicam.c` provides legacy SCSI-CAM geometry helpers used by disk drivers for `HDIO_GETGEO` and related BIOS-style cylinder/head/sector reporting. Modern block I/O does not depend on CHS geometry, but old partitioning tools and ioctl users still expect a plausible geometry. This file either infers that geometry from an MSDOS partition table or synthesizes one using the SCSI-CAM algorithm.

## Important APIs, Types, and Functions

The exported functions are `scsi_bios_ptable()`, `scsi_partsize()`, and `scsicam_bios_param()`.

`scsi_bios_ptable()` reads folio zero from the disk's partition-zero mapping and copies 66 bytes starting at MBR offset `0x1be`: the four 16-byte partition entries plus the two-byte signature. The caller owns the returned `kmemdup()` buffer.

`scsi_partsize()` parses the copied MSDOS partition table, picks the nonempty primary partition with the largest ending cylinder, decodes CHS end fields, compares the CHS-derived physical end against the LBA logical end, and, on consistency, returns heads, sectors, and cylinders in `geom`.

`setsize()` is the local SCSI-CAM fallback. It starts with 1024 cylinders and 62 sectors per track, derives the minimum head count and sector count that can address the capacity, and returns failure only if the resulting cylinder count is zero. `scsicam_bios_param()` is the public fallback wrapper used by `sd_getgeo()` when a host template does not provide `bios_param`.

## Control Flow

`scsicam_bios_param()` first tries `scsi_partsize()`. If a valid MSDOS partition table contains a CHS layout consistent with LBA capacity, that inferred geometry is returned. If inference fails and the capacity fits below 32 bits, `setsize()` tries to create a standard at-most-1024-cylinder mapping.

If the SCSI-CAM mapping fails or exceeds BIOS field limits, the function falls back to fixed mappings. Very large devices use 255 heads and 63 sectors; smaller devices use 64 heads and 32 sectors. Cylinders are capped at 65535 when the capacity cannot be represented by the selected heads/sectors values. The function returns `0` even for fallback geometry because the goal is best-effort compatibility rather than exact physical layout.

## State and Persistence Behavior

There is no persistent state. The only allocation is the temporary partition-table copy returned by `scsi_bios_ptable()` and freed by `scsi_partsize()`. Disk contents are read through the block mapping; no writes are issued. Output state is limited to the caller-provided integer array.

## Dependencies and Integration Points

The file depends on block-layer `struct gendisk`, partition-zero address-space access, folio reads, MSDOS partition table layout, unaligned little-endian helpers, and the exported SCSI-CAM header. `sd.c` integrates this file through `sd_getgeo()`: host drivers can override with `hostt->bios_param`, otherwise `scsicam_bios_param()` supplies geometry.

## Risks and Edge Cases

The helpers deliberately operate on legacy MBR/CHS data. GPT-only disks, malformed MBRs, protective MBRs, or disks with inconsistent CHS fields will fall back to synthetic geometry. `scsi_partsize()` checks for zero end-sector and wraparound-like `end_head + 1 == 0`, but the geometry remains a compatibility fiction.

`scsi_bios_ptable()` assumes the first folio can be read through `dev->part0->bd_mapping`. Read failure returns `NULL`; there is no retry or sense-level detail. The code compares an unaligned signature through an `unsigned short *` cast at `buf + 64`, which works on the target kernel architectures in practice but is less explicit than the unaligned helpers used for partition LBA fields.

For capacities at or above 2 TiB, CHS values are necessarily saturated or synthetic. Consumers must not infer true media size or topology from these values.

## Test Signals

Tests should cover MBRs with valid CHS/LBA agreement, 1023-cylinder extended CHS handling, empty partition tables, invalid signatures, zero sector fields, inconsistent CHS/LBA endings, capacities below and above 32 bits, and capacities requiring the 255/63 or 64/32 fallback. Integration tests should call `HDIO_GETGEO` through `sd_getgeo()` with and without a host-provided `bios_param`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsicam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sd.c

## Purpose

`sd.c` is the Linux SCSI disk driver. It binds SCSI direct-access disks, magneto-optical disks, RBC devices, and ZBC host-managed disks to the block layer, translates block requests into SCSI CDBs, probes media capacity and capabilities, exposes disk policy through sysfs, handles removable-media events, persistent reservations, cache flushes, DIF/DIX protection, discard/write-zeroes/write-same, atomic writes, power management, and SCSI disk lifecycle.

The driver is the central integration point between the SCSI midlayer and the generic block layer for `/dev/sd*` devices. It does not implement a low-level transport; all actual command execution goes through `scsi_execute_cmd()` or through SCSI commands initialized for the midlayer request path.

## Important APIs, Types, and Functions

The main per-disk object is `struct scsi_disk`, defined in `sd.h` and allocated by `sd_probe()`. It stores the backing `struct scsi_device`, `struct gendisk`, sysfs class device, capacity, retry limits, queue capability data, protection settings, provisioning/write-zeroes modes, zone data, cache bits, media state, and power-management flags.

Driver registration is through `sd_template`, a `struct scsi_driver` with `.probe`, `.remove`, `.shutdown`, `.rescan`, `.resume`, `.init_command`, `.uninit_command`, `.done`, `.eh_action`, and `.eh_reset`. Block operations are in `sd_fops`: `.open`, `.release`, `.ioctl`, `.getgeo`, `.check_events`, `.unlock_native_capacity`, `.report_zones`, `.get_unique_id`, `.free_disk`, and persistent reservation operations.

Request translation is centered on `sd_init_command()`. It dispatches block operations to `sd_setup_read_write_cmnd()`, `sd_setup_unmap_cmnd()`, `sd_setup_write_zeroes_cmnd()`, `sd_setup_flush_cmnd()`, and ZBC helpers. Read/write setup chooses READ/WRITE(6), (10), (16), (32), or WRITE ATOMIC(16), sets DPO/FUA/protection flags, validates online/media/capacity/alignment state, handles the last-sector bug quirk, and allocates scatter-gather tables.

Capability probing flows through `sd_revalidate_disk()`, `sd_spinup_disk()`, `sd_read_capacity()`, `read_capacity_10()`, `read_capacity_16()`, `sd_read_write_protect_flag()`, `sd_read_cache_type()`, `sd_read_block_limits()`, `sd_read_block_limits_ext()`, `sd_read_block_characteristics()`, `sd_read_block_provisioning()`, `sd_read_write_same()`, `sd_read_security()`, `sd_read_io_hints()`, `sd_read_app_tag_own()`, `sd_config_discard()`, `sd_config_write_same()`, `sd_config_atomic()`, and `sd_config_protection()`.

Sysfs attributes under `/sys/class/scsi_disk/...` expose and sometimes mutate cache mode, FUA support, start/stop management, shutdown/restart policy, protection type/mode, application tag ownership, thin provisioning, provisioning mode, zeroing mode, write-same limits, medium timeout policy, zoned capability, and retry count.

## Control Flow

`init_sd()` registers the historical SCSI disk block majors, registers the `scsi_disk` class, creates the small-page mempool used for special payloads, and registers the SCSI driver. `exit_sd()` unregisters the driver, mempools, class, and block majors.

`sd_probe()` filters device types, rejects host-managed ZBC disks when zoned block support is unavailable, allocates `struct scsi_disk`, allocates a `gendisk` for the SCSI request queue, allocates a stable disk index with `ida`, formats the `sd[a-z]+` disk name, creates the class device, initializes defaults, calls `sd_revalidate_disk()`, creates the large-sector mempool when needed, configures removable-media event flags, initializes runtime PM, publishes the disk with `device_add_disk()`, and initializes OPAL support if security protocols are supported. Error paths unwind the disk, class device, IDA index, mempool usage, and autopm reference.

Normal I/O enters via the SCSI midlayer calling `sd_init_command()`. For read/write, `sd_setup_read_write_cmnd()` translates block sectors to logical blocks, rejects offline/changed/out-of-range/unaligned requests, applies DIX/DIF metadata handling, encodes command duration limit hints, chooses the smallest safe CDB form, sets transfer size, underflow, retry count, and data length. Discard uses UNMAP or WRITE SAME with UNMAP depending on `sdkp->provisioning_mode`. Write zeroes can use WRITE SAME with zero payload or UNMAP semantics depending on `zeroing_mode` and `REQ_NOUNMAP`. Flush maps to SYNCHRONIZE CACHE(10/16). Zone operations are delegated to `sd_zbc_setup_zone_mgmt_cmnd()`.

Completion flows through `sd_done()`. It computes good bytes, aligns bogus residuals, normalizes sense data, resets the medium-access timeout counter on completion, handles medium/hardware/DIF/DIX errors by using the reported bad LBA when possible, disables discard/write-same paths when a device rejects UNMAP or WRITE SAME with illegal-request sense, and delegates ZBC post-processing for host-managed disks.

Open/release paths take and drop SCSI device references, wait for error processing, revalidate removable or write-protected media when needed, fail opens for no media or write-protected write opens, and prevent/allow medium removal on first open/last close. `sd_check_events()` uses TEST UNIT READY to detect media changes and absence for removable disks.

Power and shutdown paths call `sd_sync_cache()` when write caching is enabled and media is present, then optionally send START STOP UNIT according to system/runtime/shutdown/restart policy bits. Resume can start the disk and unlock OPAL state. Runtime resume may clear stale sense data for devices with `ignore_media_change`.

## State and Persistence Behavior

State persists in `struct scsi_disk` for the lifetime of the disk object and in block queue limits committed during revalidation. Capacity is stored in logical blocks in `sdkp->capacity` and published to the block layer in 512-byte sectors with `set_capacity_and_notify()`. Media state uses `media_present`, `device->changed`, and disk event flags. Cache state uses `WCE`, `RCD`, `DPOFUA`, and `cache_override`; sysfs can temporarily override queue flush/FUA features without changing device mode pages.

Queue limits are reconstructed during revalidation from READ CAPACITY, VPD pages, mode pages, and zoned data. These include logical/physical block sizes, discard granularity and maximums, write-zeroes maximums, atomic-write units, zoned limits, rotational/add-random flags, I/O minimum and optimum sizes, and independent access ranges.

Mempools provide special payload pages for UNMAP and WRITE SAME/zeroes commands. A global small-page pool exists while the module is loaded; a large-page pool is reference-counted only for disks whose sector size exceeds `PAGE_SIZE`.

## Dependencies and Integration Points

`sd.c` depends on the SCSI midlayer, block layer, blk-mq, runtime PM, sysfs class devices, SCSI VPD/mode-sense/report-opcode helpers, SCSI error handling, persistent reservation block APIs, optional OPAL support, optional block integrity support through `sd_dif_config_host()`, optional zoned support through `sd_zbc_*()`, and `scsicam_bios_param()` for legacy geometry.

Low-level SCSI drivers integrate by exposing `struct scsi_device` instances and request queues. Userspace sees `/dev/sd*`, `/sys/class/scsi_disk`, disk events, ioctls, persistent reservation operations, and block queue capabilities.

## Risks and Edge Cases

Device quirk handling is broad and easy to regress. The driver has fallbacks for broken READ CAPACITY values, unsupported or hanging mode pages, invalid sector size reports, devices that reject FUA, devices that misreport WRITE SAME/UNMAP support, USB/UAS devices requiring a read before mode sense, last-sector access bugs, and removable media that lies about presence.

Request setup must keep logical-block conversion, capacity checks, protection metadata, CDB limits, and queue limits consistent. A mismatch can produce out-of-range CDBs, underreported completion bytes, data-integrity failures, or writes split in ways that violate physical-block or ZBC alignment requirements.

Revalidation touches many fields and commits queue limits while the disk may already be visible. The code uses frozen queue-limit updates, but consumers can observe capability changes after media changes or sysfs writes. Power management must not fail system suspend for benign cache/start-stop errors while still reporting retryable runtime suspend failures.

Persistent reservations translate SCSI status and sense into block-layer PR errors; malformed responses or unsupported parameter combinations need precise error mapping. `sd_eh_action()` can offline a disk after repeated medium-access timeouts even when TEST UNIT READY succeeds, so timeout thresholds are operationally significant.

## Test Signals

Build coverage should include normal SCSI disks, removable devices, OPAL, block integrity, and zoned configurations. Request tests should verify READ/WRITE(6/10/16/32) selection, FUA, DIX/DIF, Type 2 protection using READ/WRITE(32), atomic writes, unaligned request rejection, beyond-end rejection, discard modes, write-zeroes modes, flush timeout, and special-payload cleanup.

Probe/revalidation tests should cover READ CAPACITY(10/16) fallbacks, capacity adjustment quirks, sector sizes including larger than `PAGE_SIZE`, VPD-derived block limits, provisioning, write-same, cache mode pages, write protect, rotational flags, concurrent positioning ranges, OPAL security protocol discovery, and queue-limit commits. Runtime tests should cover open/release media locking, media change events, sync-cache error handling, start/stop policy sysfs knobs, suspend/resume/shutdown, persistent reservations, and error handling that disables unsupported discard/write-same paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sd.h

## Purpose

`sd.h` is the private header shared by the SCSI disk implementation files. It defines SCSI disk constants, the `struct scsi_disk` runtime object, zoned-disk metadata, conversion helpers between logical blocks, bytes, and 512-byte sectors, medium-access command classification, logging macros, and prototypes or stubs for DIF and ZBC helpers.

## Important APIs, Types, and Functions

Constants include disk major count, default disk and magneto-optical timeouts, flush and WRITE SAME timeout policy, retry limits, probe buffer size, and the last-sector quirk window. Enumerations define extended CDB and mempool sizes, transfer/write-same block limits, logical block provisioning modes, and write-zeroes implementation modes.

`struct zoned_disk_info` stores `nr_zones` and `zone_blocks` for ZBC probing before and after capacity publication. `struct scsi_disk` is the key SCSI disk state object used by `sd.c`, `sd_dif.c`, and `sd_zbc.c`. It links to `struct scsi_device`, `struct gendisk`, optional `opal_dev`, class device state, capacity, queue-limit input values, discard/unmap parameters, atomic-write parameters, media/cache/protection/provisioning/zoned/security flags, retry policy, and runtime power state.

`scsi_disk()` maps a `gendisk` back to the private disk object. `sd_printk()` and `sd_first_printk()` wrap SCSI device logging with the disk name and first-scan filtering. `scsi_medium_access_command()` identifies commands that touch media for timeout/error policy. Conversion helpers are `logical_to_sectors()`, `logical_to_bytes()`, `bytes_to_logical()`, and `sectors_to_logical()`.

The header declares `sd_dif_config_host()`, the ZBC helper API when `CONFIG_BLK_DEV_ZONED` is enabled, fallback stubs when it is disabled, and logging helpers `sd_print_sense_hdr()` and `sd_print_result()`.

## Control Flow

There is no module control flow in the header. Its inline helpers participate in hot paths. `scsi_medium_access_command()` is used by SCSI disk error handling to decide whether a timed-out command should count as a medium-access timeout. Conversion helpers are used throughout request setup, queue-limit construction, capacity publication, and ZBC report parsing.

The ZBC stubs are an important compile-time control point: without zoned block support, zone probing is a no-op, zone management commands return `BLK_STS_TARGET`, completions pass through unchanged, and `.report_zones` is `NULL`.

## State and Persistence Behavior

`struct scsi_disk` is mutable runtime state rather than persistent storage. Its fields are updated by probe, revalidation, sysfs stores, request completion, error handling, and power management. Several bitfields mirror device or queue capabilities and must stay synchronized with committed block queue limits.

The conversion helpers assume `sdev->sector_size` is a power-of-two block size at least 512 bytes. That invariant is enforced during capacity probing in `sd.c`.

## Dependencies and Integration Points

The header depends on SCSI core types, block integrity/zoned types through included users, and the block layer's 512-byte sector model. It integrates the split implementation files: `sd.c` owns most disk behavior, `sd_dif.c` owns integrity queue-limit setup, and `sd_zbc.c` owns host-managed zoned command/report behavior.

## Risks and Edge Cases

`struct scsi_disk` is shared across multiple subsystems, so adding fields or changing semantics can require updates in sysfs, revalidation, queue-limit setup, suspend/resume, and completion paths. The many one-bit flags are compact but easy to misinterpret, especially the distinction between device capability, selected mode, and user override.

The conversion helpers use shifts based on `ilog2(sector_size) - 9`; unsupported sector sizes or sizes below 512 would be dangerous, so the validation path in `sd_read_capacity()` is critical. ZBC stubs must match the real function signatures so non-zoned builds preserve behavior.

## Test Signals

Compile tests should cover `CONFIG_BLK_DEV_ZONED` enabled and disabled, block integrity enabled and disabled, and OPAL enabled and disabled. Unit-style checks should verify block/sector/byte conversion for 512, 4096, and larger power-of-two logical block sizes, and `scsi_medium_access_command()` coverage for all read/write/verify/sync/unmap and variable-length command cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_dif.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sd_dif.c

## Purpose

`sd_dif.c` configures SCSI disk Data Integrity Field/Data Integrity Extensions support for the block layer. It translates SCSI host DIF/DIX capabilities and the disk's formatted protection type into `struct blk_integrity` queue limits so the block layer knows whether protection metadata can be exchanged with the host adapter and/or device.

## Important APIs, Types, and Functions

The only function is `sd_dif_config_host(struct scsi_disk *sdkp, struct queue_limits *lim)`. It reads `sdkp->protection_type`, checks `scsi_host_dif_capable()` and `scsi_host_dix_capable()`, clears and fills `lim->integrity`, sets checksum type from `scsi_host_get_guard()`, sets reference-tag handling for non-Type 3 protection, marks device-capable DIF when both host and disk can exchange protection information, and derives application-tag size when the disk grants application tag ownership.

It uses `struct blk_integrity`, `struct t10_pi_tuple`, `BLK_INTEGRITY_*` flags, `T10_PI_TYPE3_PROTECTION`, and SCSI host protection helpers.

## Control Flow

`sd_config_protection()` in `sd.c` calls this function during disk revalidation when block integrity support is enabled. The function starts by zeroing the integrity limits. If the host does not support DIX for the disk protection type, but supports Type 0 DIX, it falls back to host-only DIX by clearing DIF and enabling DIX. If DIX remains unavailable, it returns with integrity disabled.

When DIX is available, it selects IP or CRC guard checksum, sets metadata and tuple size to one T10 PI tuple, and sets `BLK_INTEGRITY_REF_TAG` for Type 1/2-style protection. If the disk is formatted with DIF and the host supports the matching type, it marks the queue as device-capable. Application-tag exposure is conditional on `sdkp->ATO`; without ATO, the function leaves tag size unset even though device-capable protection may be marked.

## State and Persistence Behavior

The function has no private state. It mutates only the queue-limit integrity structure passed by the revalidation caller. Those values become persistent block queue state after `queue_limits_commit_update_frozen()` succeeds in `sd_revalidate_disk()`.

## Dependencies and Integration Points

The function integrates SCSI host protection capability reporting with the block integrity layer and T10 PI tuple layout. `sd.c` handles protection type discovery from READ CAPACITY(16), command protection op setup in `sd_setup_protect_cmnd()`, and completion/error interpretation. This file handles only queue capability publication.

## Risks and Edge Cases

The fallback from unsupported DIX for a formatted protection type to Type 0 DIX is subtle: it enables host protection metadata handling without device DIF. Incorrect capability reporting by a host can cause the block layer to submit metadata the HBA cannot handle, or fail to expose protection that is actually supported.

Application-tag size depends on both protection type and ATO. Type 3 exposes application plus reference tag space, while Type 1/2 expose only the application tag. Queue-limit commits must stay synchronized with command setup in `sd.c`, which sets protection operations and flags per request.

## Test Signals

Tests should exercise hosts with no DIX, Type 0-only DIX, full DIX/DIF for Type 1/2/3, IP versus CRC guard support, disks with and without ATO, and queue limits after revalidation. I/O tests should pair this with protected read/write paths and verify guard/ref/application tag handling and correct disablement when host capabilities are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_dif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_trace.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sd_trace.h

## Purpose

`sd_trace.h` defines tracepoints for SCSI disk zoned-block behavior. It is included by `sd_zbc.c` with `CREATE_TRACE_POINTS`, producing trace events that help observe zone append preparation and write-pointer offset updates.

## Important APIs, Types, and Functions

The trace system name is `sd`, and the include file is `sd_trace`. Two `TRACE_EVENT()` definitions are present.

`scsi_prepare_zone_append` records SCSI device identity (`host_no`, `channel`, `id`, `lun`), the target LBA, and the write-pointer offset used when preparing a zone append.

`scsi_zone_wp_update` records the same SCSI identity plus the request sector, write-pointer offset, and number of good bytes completed. Both events use `struct scsi_cmnd` to derive device identity and expose formatted strings through `TP_printk`.

## Control Flow

Trace headers are declarative. When tracepoints are enabled at runtime through ftrace/perf/tracefs, callers compiled against these event definitions can emit records. The bottom of the file sets `TRACE_INCLUDE_PATH` to `../../drivers/scsi` and includes `trace/define_trace.h`, which is required outside the include guard for tracepoint generation.

## State and Persistence Behavior

There is no persistent driver state. Enabling a tracepoint causes event records to be written into the kernel tracing buffers. The schema is fixed by the fields in `TP_STRUCT__entry`.

## Dependencies and Integration Points

The header depends on Linux tracepoint infrastructure plus `scsi_cmnd` and `scsi_host` definitions. It is tied to `sd_zbc.c`, which defines `CREATE_TRACE_POINTS` before including it. Userspace tools consume the events from the `sd` trace system.

## Risks and Edge Cases

Tracepoint field types must match the values recorded by call sites. `sector_t` formatting uses `%llu`; this is normal in kernel trace definitions but should be checked on configurations where `sector_t` width changes. The include path is relative to the build location and must remain valid if files are moved.

The event names mention zone append/write pointer behavior, but this source snapshot's `sd_zbc.c` does not visibly call these tracepoints in the read regions, so the definitions may support code paths present in nearby versions or conditional code. A build will catch stale tracepoint declarations only if call sites still reference them correctly.

## Test Signals

Build tests should compile with tracepoints enabled and with `sd_zbc.c` as the defining translation unit. Runtime tests should enable `sd:scsi_prepare_zone_append` and `sd:scsi_zone_wp_update` through tracefs while issuing zoned writes/appends on a compatible SCSI ZBC device, verifying device identity and LBA/offset fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_zbc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sd_zbc.c

## Purpose

`sd_zbc.c` implements the SCSI disk driver's support for Zoned Block Commands on host-managed ZBC disks. It validates zoned device characteristics, reads zone size/count information, publishes zoned queue limits, services block-layer zone report callbacks, maps block zone-management operations to SCSI ZBC OUT commands, and performs ZBC-specific completion handling.

## Important APIs, Types, and Functions

Public functions declared in `sd.h` are `sd_zbc_read_zones()`, `sd_zbc_revalidate_zones()`, `sd_zbc_setup_zone_mgmt_cmnd()`, `sd_zbc_complete()`, and `sd_zbc_report_zones()`.

Internal helpers include `sd_zbc_is_gap_zone()`, `sd_zbc_parse_report()`, `sd_zbc_do_report_zones()`, `sd_zbc_alloc_report_buffer()`, `sd_zbc_zone_sectors()`, `sd_zbc_cmnd_checks()`, `sd_zbc_check_zoned_characteristics()`, `sd_zbc_check_capacity()`, and `sd_zbc_print_zones()`.

The file uses `struct scsi_disk` zoned fields: `early_zone_info`, `zone_info`, `zones_optimal_open`, `zones_optimal_nonseq`, `zones_max_open`, `zone_starting_lba_gran`, `urswrz`, `capacity`, `rc_basis`, and the disk's logical/physical block sizes.

## Control Flow

`sd_zbc_read_zones()` is called during `sd_revalidate_disk()` before the gendisk capacity is committed. It returns immediately for non-ZBC devices. For ZBC devices, it sets zoned queue features, forces READ/WRITE/SYNC(16), sets zone write granularity to the physical block size, reads VPD page B6, rejects unsupported constrained-read host-managed devices, validates zone alignment method, issues REPORT ZONES to verify capacity and zone size, requires a power-of-two zone size, computes the number of zones, fills `early_zone_info`, and sets max-open/max-active/chunk queue limits.

`sd_zbc_revalidate_zones()` runs after capacity has been set. It skips non-zoned queues and unchanged zone topology. Otherwise it copies early zone information into live `zone_info`, calls `blk_revalidate_disk_zones()` under `memalloc_noio_save()`, clears zone info and capacity on failure, and prints the zone topology on success.

`sd_zbc_report_zones()` is the block-layer `.report_zones()` callback. It rejects non-ZBC or invalid-capacity disks, allocates a REPORT ZONES buffer sized by requested zones and queue mapping limits, loops while the requested zone count and capacity are not exhausted, issues partial REPORT ZONES commands, validates descriptor continuity, skips gap zones only when constant starting-LBA granularity makes that valid, converts each descriptor to `struct blk_zone`, and calls `disk_report_zone()`.

Zone management requests enter from `sd_init_command()`. `sd_zbc_setup_zone_mgmt_cmnd()` validates the disk type, media-change state, and zone alignment, then builds a 16-byte ZBC OUT CDB for RESET WRITE POINTER, OPEN, CLOSE, or FINISH, optionally setting the all-zones bit. `sd_zbc_complete()` quiets INVALID FIELD IN CDB errors for zone-management commands attempted on conventional zones.

## State and Persistence Behavior

The persistent state lives in `struct scsi_disk` and the block queue limits. `early_zone_info` is a staging area before gendisk capacity is known; `zone_info` mirrors the topology accepted by the block layer. `zone_starting_lba_gran` records devices whose zones have constant start offsets rather than constant lengths. Queue zoned flags, chunk size, max open zones, and zone write granularity persist after queue-limit commit.

The file does not maintain an in-memory write-pointer cache in this snapshot. Zone state is fetched from the device through REPORT ZONES and exposed through block-layer callbacks.

## Dependencies and Integration Points

This file depends on SCSI command execution, SCSI ZBC constants, the block zoned API, queue limits, `blk_revalidate_disk_zones()`, `disk_report_zone()`, vmalloc-backed report buffers, and `sd_trace.h`. `sd.c` calls it from revalidation, request setup, completion, and block operations. Userspace observes behavior through block zoned ioctls/sysfs and ordinary zone management requests.

## Risks and Edge Cases

Zoned disks have strict topology constraints. The driver rejects constrained-read host-managed devices, non-power-of-two zone sizes, invalid constant-start granularity, REPORT ZONES replies with too-short lengths, discontinuous descriptors, and gap zones when the disk does not advertise constant LBA offsets. Incorrect validation can make the block layer accept a device it cannot safely address.

Buffer allocation must respect max hardware sectors and segment limits because REPORT ZONES commands cannot be split. Large zone counts are handled by bounded partial reports; allocation falls back by halving buffer size down to one sector.

Capacity may be adjusted from REPORT ZONES when READ CAPACITY uses `RC_BASIS == 0`. Revalidation failure deliberately sets capacity to zero, making the disk unusable rather than exposing inconsistent zone topology.

## Test Signals

Tests should cover host-managed ZBC probing, non-ZBC bypass, VPD B6 failures, constrained-read rejection, constant zone length versus constant start-offset devices, invalid granularity, non-power-of-two zone size, capacity mismatch correction, runt final zones, and zone topology changes across revalidation.

I/O tests should exercise `report_zones`, partial reports over many zones, gap-zone handling, zone reset/reset-all/open/close/finish commands, unaligned zone-management request rejection, media-change rejection, conventional-zone invalid-field quieting, and queue-limit values such as `BLK_FEAT_ZONED`, `chunk_sectors`, `zone_write_granularity`, and `max_open_zones`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sd_zbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sense_codes.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sense_codes.h

## Purpose

`sense_codes.h` is a macro-consumed data table of T10 SCSI Additional Sense Code and Additional Sense Code Qualifier pairs. It maps 16-bit ASC/ASCQ values to human-readable text used by SCSI sense decoding and logging code. The file intentionally contains no include guard or standalone declarations because it is meant to be included with `SENSE_CODE(code, text)` defined by the including translation unit.

## Important APIs, Types, and Functions

There are no functions or C types. The only interface is repeated invocations of `SENSE_CODE(0xAABB, "description")`, where the high byte is ASC and the low byte is ASCQ. The table starts with no-additional-sense and progresses through readiness, write/read errors, illegal request, medium changes, target condition changes, protocol errors, copy/offload errors, zoning errors, power conditions, prediction warnings, encryption/security errors, and many other T10-defined conditions.

Comments document wildcard-style ranges that cannot be represented directly by single `SENSE_CODE()` rows, such as `0x40NN`, `0x4DNN`, and `0x70NN`. The top comment identifies the T10 canonical list and the source date used for this snapshot.

## Control Flow

Control flow is provided by the including file. A typical including pattern defines `SENSE_CODE()` to generate switch cases, array initializers, or lookup entries, includes this header, then undefines the macro. This file's ordering is therefore data ordering only.

## State and Persistence Behavior

There is no runtime mutable state. The generated lookup representation in the including file becomes static kernel data. Updating this file changes sense-code decoding text after rebuild.

## Dependencies and Integration Points

The file depends on an external `SENSE_CODE` macro definition. It integrates with SCSI diagnostic/logging paths, especially code that prints sense key, ASC, and ASCQ meanings for command failures. `sd.c`, `ses.c`, SRP, and other SCSI drivers indirectly benefit when they call SCSI sense-printing helpers because those helpers can translate numeric ASC/ASCQ pairs into readable strings.

## Risks and Edge Cases

Because the table is macro-expanded, syntax errors or unescaped strings break every include site. Duplicate codes, stale text, or missing newer T10 values degrade diagnostics rather than core I/O behavior. Wildcard ranges in comments require special handling elsewhere; they are not actual lookup entries.

The table is snapshot-based. Device firmware may return vendor-specific or newer standard ASC/ASCQ values absent from this file, in which case decoders must fall back to numeric output. Changing descriptions can affect tests that assert exact log text.

## Test Signals

Build tests should include every translation unit that macro-includes the table. Lookup tests should verify representative codes such as `0x0000`, `0x0401`, `0x2000`, `0x2400`, `0x2800`, `0x2900`, `0x3A00`, `0x5000`, and `0x7400`, plus unknown/vendor-specific codes. Static checks can detect duplicate numeric keys, unsorted additions if ordering is expected, malformed strings, and accidental direct inclusion without a macro definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sense_codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ses.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ses.c

## Purpose

`ses.c` implements the SCSI Enclosure Services driver. It binds SCSI enclosure devices, reads SES diagnostic pages, registers enclosure components with the generic enclosure class, exposes controls such as fault, locate, active, power status, and component IDs, and matches ordinary SCSI devices to enclosure slots using SAS/FCP additional descriptor information when available.

The driver supports both explicit `TYPE_ENCLOSURE` devices and embedded enclosure services associated with another SCSI device. It is an integration layer between SCSI diagnostic commands, the enclosure class, and SAS transport identity.

## Important APIs, Types, and Functions

`struct ses_device` stores diagnostic page buffers and lengths for Configuration page 1, Enclosure Status/Control page 2, and Additional Element Status page 10. `struct ses_component` stores the parsed device address associated with an enclosure component. `struct ses_host_edev` is compiled out in this snapshot.

SCSI command helpers are `ses_recv_diag()` and `ses_send_diag()`, which issue RECEIVE DIAGNOSTIC RESULTS and SEND DIAGNOSTIC with retry definitions for unit attention and not-ready conditions. Component control helpers include `init_device_slot_control()`, `ses_get_page2_descriptor()`, `ses_set_page2_descriptor()`, `ses_get_fault()`, `ses_set_fault()`, `ses_get_status()`, `ses_get_locate()`, `ses_set_locate()`, `ses_set_active()`, `ses_show_id()`, `ses_get_power_status()`, and `ses_set_power_status()`.

Discovery and matching helpers are `ses_process_descriptor()`, `ses_enclosure_find_by_addr()`, `ses_enclosure_data_process()`, `ses_match_to_enclosure()`, `ses_intf_add()`, `ses_intf_remove_component()`, `ses_intf_remove_enclosure()`, and `ses_intf_remove()`. Registration uses `ses_interface` as a SCSI class interface and `ses_template` as a SCSI driver for enclosure devices.

## Control Flow

Module initialization registers the class interface first, then the SCSI enclosure driver. `ses_probe()` accepts only `TYPE_ENCLOSURE` and logs attachment. `ses_intf_add()` runs for SCSI devices visible to the class interface. If a device is not an enclosure, the driver searches existing enclosures on the same host and tries to match the device into a slot. If it is an enclosure or embedded enclosure, the driver allocates `struct ses_device`, reads page 1 to discover subenclosures and element type counts, counts device and array-device components, optionally reads page 2 for status/control and page 10 for address matching, registers an `enclosure_device`, assigns per-component scratch storage, processes descriptors, and matches any previously scanned non-enclosure devices.

`ses_enclosure_data_process()` optionally reads page 7 element descriptors and refreshes page 10. It walks the page-1 type table and each element instance. For device and array-device slots it allocates or reuses `struct enclosure_component`, assigns names from page 7 when present, parses SAS/FCP addresses from page 10, and registers components on creation. Additional descriptor pointer advancement is limited to element types for which SES additional descriptors are expected.

Runtime sysfs enclosure callbacks fetch or modify page 2 descriptors. Getters refresh page 2 before reading descriptor bits. Setters copy the current descriptor into a safe control descriptor with reserved/status bits cleared, set or clear the relevant request bit, mark select on the matching descriptor, and send page 2 back with SEND DIAGNOSTIC.

Removal distinguishes non-enclosure components from enclosure devices. Component removal finds the enclosure containing the SCSI device and removes the device association. Enclosure removal frees page buffers and scratch storage, drops the enclosure reference, and unregisters the enclosure.

## State and Persistence Behavior

Per-enclosure state is stored in `edev->scratch` as `struct ses_device`; per-component state is stored in `component[i].scratch` as `struct ses_component`. Page buffers persist so callbacks can reuse lengths and type tables. Page 2 is refreshed before descriptor reads and rewritten for control changes, so the authoritative state remains the enclosure hardware.

Device-to-slot association persists in the enclosure class until removed or refreshed. SAS addresses parsed from page 10 are stored in component scratch and used to link `scsi_device` objects to slots. Component controls such as locate, fault, active, and power are persisted by the enclosure device if SEND DIAGNOSTIC succeeds.

## Dependencies and Integration Points

The driver depends on SCSI command execution, SCSI device typing and enclosure detection, the generic enclosure class, SCSI diagnostic page formats, unaligned helpers, and SAS transport helpers (`scsi_is_sas_rphy()`, `sas_get_address()`). It exports no symbol; integration is through module registration, the SCSI driver core, class interfaces, and enclosure sysfs.

## Risks and Edge Cases

SES page parsing is length-sensitive. The code guards many descriptor bounds, but malformed page 1, 7, or 10 data can still reduce functionality to simple population or abort binding. Page 2 support is optional; without it, status/control callbacks return default values or `-EINVAL`.

Component numbering for page 2 descriptors counts only device and array-device elements while walking all type descriptors. If page 1 type counts and page 2 descriptor layout disagree, controls may target the wrong slot or fail. `ses_set_page2_descriptor()` clears the page-2 control area and selects only one descriptor before sending, which is correct for targeted control but depends on descriptor reconstruction preserving required status bits.

Address matching currently handles SAS thoroughly and only limited FCP slot extraction; other protocols are noted as future work. Devices scanned before their enclosure are matched after enclosure registration, and devices scanned later are matched by the class-interface add path, so refresh ordering matters.

## Test Signals

Tests should cover explicit and embedded enclosure devices, page 1 discovery with multiple subenclosures and element types, missing page 2, missing page 7 names, missing or malformed page 10 descriptors, SAS address matching, late device-to-slot matching, and removal of both enclosure and member devices.

Control tests should exercise fault, locate, active, and power setters/getters, verify correct SEND DIAGNOSTIC payload bits and select bit, handle invalid enclosure settings, and confirm that not-ready/unit-attention retry rules work. Robustness tests should feed short or inconsistent diagnostic pages and verify clean failure without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ses.c -->
