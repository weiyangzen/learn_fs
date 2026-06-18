# sources/distributed-fs/ceph-client/drivers/scsi/scsi_priv.h

## Purpose

`scsi_priv.h` is the internal SCSI mid-layer header. It gathers private cross-file declarations for host initialization, command setup, device-info tables, error handling, queueing, procfs, scanning, sysctl, sysfs, netlink, power management, device handlers, and BSG registration. It is not a public driver API; it is the glue used by implementation files under `drivers/scsi`.

## Important APIs, types, and functions

The header defines `SCSI_CMD_RETRIES_NO_LIMIT`, internal `enum scsi_ml_status` values, `scsi_ml_byte()`, `SCSI_EH_ABORT_SCHEDULED`, `SCSI_SENSE_VALID()`, and `SCSI_DEVICE_BLOCK_MAX_TIMEOUT`. It declares major SCSI core entry points including `scsi_init_hosts()`, `scsi_init_command()`, `scsi_timeout()`, `scsi_error_handler()`, `scsi_decide_disposition()`, `scsi_queue_insert()`, `scsi_io_completion()`, `scsi_run_host_queues()`, `scsi_scan_host_selected()`, `scsi_forget_host()`, `scsi_sysfs_add_sdev()`, `scsi_sysfs_device_initialize()`, `__scsi_remove_device()`, `scsi_bus_type`, `scsi_shost_groups`, and `blank_transport_template`.

Feature-guarded sections provide real declarations or no-op stubs for procfs, sysctl, netlink, PM, and SCSI device handlers. This allows core initialization and teardown code to call subsystem hooks without scattering `#ifdef`s.

## Control flow

There is no runtime control flow except inline helpers and stubs. The important design is compile-time routing: when optional features are enabled, callers link to the implementing file; when disabled, the inline definitions return success or do nothing. The header therefore centralizes SCSI core feature boundaries and keeps the rest of the mid-layer source files simpler.

## State and persistence behavior

The header owns no state. It exposes stateful objects owned elsewhere, such as `scsi_nl_sock`, `scsi_bus_type`, `scsi_shost_groups`, and the PM operations table. The inline stubs deliberately avoid state changes when a subsystem is disabled.

## Dependencies and integration points

It depends on Linux device infrastructure, `scsi/scsi_device.h`, and `linux/sbitmap.h`, plus forward declarations for SCSI core structures. Nearly every file in this work item includes it: netlink uses socket declarations, PM uses scan declarations, procfs uses scan and host declarations, scanning uses sysfs and PM declarations, and sysfs uses PM and scan helpers. It also bridges to transport classes and upper-level driver registration through `blank_transport_template` and `scsi_bus_type`.

## Risks and edge cases

Because this header is private but broad, changing a declaration can break many SCSI core files at once. Stub semantics matter: returning zero for disabled procfs/sysctl or doing nothing for disabled PM/netlink must match caller assumptions. Internal status values must not leak to low-level drivers, as the comments warn. `SCSI_SENSE_VALID()` only recognizes fixed-format sense with `0x70` response code; callers must not treat it as a universal sense validator.

## Test signals

Build matrix coverage should toggle `CONFIG_SCSI_PROC_FS`, `CONFIG_SYSCTL`, `CONFIG_SCSI_NETLINK`, `CONFIG_PM`, `CONFIG_SCSI_DH`, and `CONFIG_SCSI_LOGGING` to validate both declarations and stubs. Static checks should ensure functions declared here still match their definitions and exports. Integration tests should exercise initialization/exit with optional features disabled to confirm callers tolerate stub behavior.
