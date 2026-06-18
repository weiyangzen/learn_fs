<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h

## Purpose
This header defines the generic SCSI transport template used by FC, SAS, iSCSI, SPI, SRP, and other transports to add host/target/device attributes, private data, user scan hooks, workqueues, and optional EH strategy overrides.

## Important APIs, Types, And Functions
`struct scsi_transport_template` contains host/target/device `transport_container`s, `user_scan`, size/private-offset fields for device/target/host data, `create_work_queue`, and `eh_strategy_handler`. Helpers reserve target or device private space, retrieve transport target/device private data from `scsi_target`/`scsi_device`, map transport classes to `Scsi_Host`, and initialize queue limits through `scsi_init_limits()`.

## Control Flow
Transport attach code sizes attribute/private areas before hosts/devices/targets are allocated. Reservation helpers may be called only once per target or device private offset and use `BUG_ON()` to enforce that. Later, drivers use the offset helpers to access their private area behind transport-managed data.

## State And Persistence
The template stores allocation sizing and class containers. Per-object state lives in `Scsi_Host::shost_data`, `scsi_target::starget_data`, or `scsi_device::sdev_data` based on these sizes and offsets.

## Dependencies And Integration Points
It depends on Linux transport class, block queues, bug checks, SCSI host, and SCSI device headers. It is the base template embedded/returned by transport-specific attach functions.

## Risks
Private offsets must be reserved before object allocation and only once. Mis-sized areas corrupt adjacent transport or driver data. `BUG_ON()` makes misuse fatal. Queue-limit initialization must remain consistent with host template limits.

## Test Signals
Validate private-data offsets and alignment, duplicate reservation failure, target/device data retrieval with multiple transports, user-scan callbacks, transport workqueue creation, EH strategy override invocation, and queue-limit initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport.h -->
