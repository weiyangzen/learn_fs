# sources/distributed-fs/ceph-client/drivers/staging/iio/Kconfig

## Purpose
Defines the top-level staging Industrial I/O menu. The menu is visible only when core `IIO` support is enabled.

## Important Entries and Integration
The file sources subordinate Kconfig files for accelerometers, ADCs, ADDAC devices, DDS frequency devices, and impedance analyzers. It does not define symbols itself beyond the menu wrapper.

## Risks and Test Signals
Risk is mostly build-menu coverage: omitted sources make driver symbols unreachable. Test by running Kconfig menu or `olddefconfig` with `IIO=y/m` and verifying each sourced submenu is reachable.
