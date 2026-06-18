# File Research: sources/block-storage/lvm2/lib/device/device_id.h

## Purpose
Declares the public interface for persistent device-ID and `system.devices` management implemented in `device_id.c`, plus WWID parsing and sysfs ID helpers used by other device modules.

## Main API Groups
- Memory cleanup for `dev_use`, `dev_id`, and whole lists.
- ID type conversion and metadata export helpers.
- Devices-file lifecycle: read, write, existence, touch, lock/unlock, init/exit, version check.
- Devices-file updates for PV removal, LV removal, VG UUID changes, add/update device entries, and validation/search flows.
- Lookup helpers for `dev_use` entries by devno, device pointer, PVID, devname, or typed device ID.
- System ID reads/find/list APIs for a specific device or ID.
- Sysfs block reads with partition-to-primary fallback.
- SCSI/NVMe WWID type conversion, WWID list cleanup/addition, VPD/NVMe/sysfs WWID reads, and stale PV metadata ID checking.

## Dependencies
Includes command context and `device.h`. Several declarations are implemented in this group (`device_id.c`) while NVMe read support is implemented in `nvme.c`.

## Risk Notes
This header exposes high-level policy functions used during scanning and writeback. Return values often distinguish "not found", "update needed", and "hard failure" through side effects and output parameters, so callers must follow the intended sequencing.
