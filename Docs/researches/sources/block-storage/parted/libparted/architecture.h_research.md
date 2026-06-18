# File Research: sources/block-storage/parted/libparted/architecture.h

This private internal header defines libparted’s architecture abstraction.

Contents:
- Includes `<parted/disk.h>` for `PedDiskArchOps` and `PedDeviceArchOps`.
- Defines `struct _PedArchitecture` with:
  - `PedDiskArchOps* disk_ops`
  - `PedDeviceArchOps* dev_ops`
- Declares global `ped_architecture`.
- Declares `ped_set_architecture()`.

Research notes:
- The warning comment says this should not be exported to the public API.
- Common libparted code reaches platform functionality only through this two-table abstraction.
