# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_ata.c

## Purpose

`sas_ata.c` bridges libsas domain devices to libata so SATA/STP devices behind SAS controllers can be discovered, reset, power-managed, issued ATA commands, and represented as SCSI devices. It translates libata queued commands into `struct sas_task`, translates SAS completion status back into ATA error masks/result taskfiles, coordinates ATA EH with libsas revalidation, and adds SATA-specific SCSI device sysfs attributes.

## Important APIs, Types, and Functions

Command execution and completion are centered on `sas_ata_qc_issue()`, `sas_ata_task_done()`, `sas_to_ata_err()`, and `sas_ata_qc_fill_rtf()`. Reset/readiness functions include `smp_ata_check_ready_type()`, `smp_ata_check_ready()`, `local_ata_check_ready()`, `sas_ata_wait_after_reset()`, `sas_ata_hard_reset()`, `sas_ata_prereset()`, `sas_ata_schedule_reset()`, and `sas_try_ata_reset()` integration through other files. Device setup and discovery functions include `sas_ata_init()`, `sas_ata_add_dev()`, `sas_discover_sata()`, and `sas_probe_sata()`.

EH and lifecycle helpers include `sas_ata_internal_abort()`, `sas_ata_post_internal()`, `sas_ata_sched_eh()`, `sas_ata_end_eh()`, `sas_ata_task_abort()`, `sas_ata_strategy_handler()`, `sas_ata_eh()`, `sas_ata_wait_eh()`, `sas_ata_device_link_abort()`, `sas_suspend_sata()`, `sas_resume_sata()`, and `sas_execute_ata_cmd()`. The libata port operations table is `sas_sata_ops`. The exported SCSI device attribute group is `sas_ata_sdev_attr_group`.

## Control Flow

Libsas discovery calls `sas_ata_init()` to allocate an `ata_host` and one `ata_port` for a SATA domain device, set SAS/SATA/NCQ flags, wire the port to the SAS host, and add the libata transport port. For expander-attached SATA, `sas_ata_add_dev()` may first lower link rate via SMP PHY control if the device exceeds the parent pathway rate, then reads REPORT PHY SATA data, initializes the domain device, allocates an end-device rphy, queues it for discovery, and calls `sas_discover_sata()`.

Libata command issue calls `sas_ata_qc_issue()` with the ATA port lock held. The function temporarily drops the lock, allocates a SAS task, fills STP ATA FIS and optional ATAPI packet, computes transfer length/scatterlist metadata, sets `qc->lldd_task`, links SCSI commands to the SAS task when present, and submits through the low-level driver's `lldd_execute_task()`. Completion arrives at `sas_ata_task_done()`, which races against libsas EH and libata freezing by checking `done_lock`, `SAS_HA_FROZEN`, `ata_port_is_frozen()`, and `qc` state. It copies ending FIS data for protocol responses or good status, maps SAS transport errors to ATA error masks, completes the queued command, and frees the SAS task.

Reset flow uses libata hardreset callbacks. `sas_ata_hard_reset()` invokes the low-level `lldd_I_T_nexus_reset()`, waits for readiness either through a local low-level `lldd_ata_check_ready()` callback or SMP rediscovery polling behind an expander, records the classified ATA device class, and marks the cable SATA. EH scheduling marks `SAS_DEV_EH_PENDING` and increments `ha->eh_active`; `sas_ata_end_eh()` clears it. `sas_ata_strategy_handler()` runs ATA port EH asynchronously for all SATA devices while revalidation is disabled, then reenables revalidation to process deferred topology changes.

Power management iterates SATA devices under the discovery mutex, calls `ata_sas_port_suspend()` or `ata_sas_port_resume()`, waits for EH, and fails probes whose devices are disabled. `sas_ata_eh()` extracts SATA commands from the SCSI EH work queue per device, hands them to libata command EH, and cleans any leftover stack-local list entries. Sysfs attributes proxy NCQ priority supported/enabled state to libata only for SATA-backed SCSI devices.

## State and Persistence Behavior

Runtime state lives in `domain_device.sata_dev`, the libata `ata_host`, `ata_port`, `ata_link`, queued command fields, `sas_task` fields, and SAS HA EH counters. The last device-to-host FIS is kept in `dev->sata_dev.fis` and is used to fill ATA result taskfiles. `SAS_DEV_EH_PENDING`, `SAS_DEV_GONE`, and `SAS_HA_ATA_EH_ACTIVE` coordinate removal, reset, and discovery deferral. No state is persisted outside kernel objects.

## Dependencies and Integration Points

The file depends on libata, SCSI EH, SAS transport classes, libsas internal structures, low-level libsas driver callbacks, SMP expander helpers, and block request aborts. It is compiled only when `CONFIG_SCSI_SAS_ATA` is selected. It is the main integration layer between SAS topology discovery and the ATA device model.

## Risks and Edge Cases

The highest-risk areas are ownership races for `sas_task` and `ata_queued_cmd` during completion, libata port freeze, SCSI EH abort, and internal ATA command abort. `sas_ata_internal_abort()` warns that failed low-level aborts may leak tasks because libsas is not prepared to recover if a driver keeps owning the task. Readiness polling differs for local versus expander-attached devices and must tolerate SATA pending states. Wide-port/link-rate adjustments behind expanders can fail and abort discovery. Revalidation is intentionally deferred during ATA EH; missing reenabling would suppress hotplug processing.

## Test Signals

Useful tests include SATA device discovery both direct-attached and behind expanders, ATAPI and NCQ command issue/completion, ending-FIS error propagation, SAS transport error translation, libata hardreset through local and SMP readiness paths, port freeze races with command completion, SCSI EH command extraction for SATA devices, internal command timeout/abort, suspend/resume with failed devices, link-rate lowering behind expanders, NCQ priority sysfs visibility and toggling, and hot-remove aborting in-flight commands quickly.
