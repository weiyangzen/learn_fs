# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i3c.c

Purpose: I3C transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_i3c_probe()` creates an 8-bit I3C regmap, reads WHOAMI directly, matches it against the exported chip-info array, and calls `inv_icm45600_core_probe(regmap, matched_info, false, NULL)`. Static I3C IDs use vendor/extra-info matching.

Control flow and state: no private persistent state. It performs chip selection by WHOAMI rather than firmware-compatible data and tells the core not to soft-reset, which avoids disrupting I3C bus state during attach.

Dependencies and integration: Linux I3C device/master APIs, regmap-I3C, module I3C tables, shared PM ops via `pm_sleep_ptr`, and `IIO_ICM45600` namespace.

Risks and tests: the chip-info scan must stay synchronized with exported variants. WHOAMI read failures or unrecognized IDs abort probe. Core reset is disabled on I3C, so tests should verify default-state assumptions after hotjoin/enumeration. Test signals include I3C autoload, WHOAMI matching for each variant, no-reset probe success, FIFO IRQ operation, and system sleep callbacks.
