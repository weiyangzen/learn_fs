# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Kconfig

## Purpose
Defines AtomISP sensor-level I2C drivers.

## Important Entries and Integration
`VIDEO_ATOMISP_OV2722` enables an OVT OV2722 raw camera sensor and depends on ACPI plus I2C/VIDEO_DEV. `VIDEO_ATOMISP_GC2235` enables GalaxyCore GC2235 raw camera support with the same dependencies. Both help texts state they currently only work with atomisp.

## Risks and Test Signals
The GC2235 help text calls it OVT despite being GalaxyCore, indicating stale copy. Kconfig tests should ensure these symbols are visible only under AtomISP and compile only on ACPI/I2C camera configurations.
