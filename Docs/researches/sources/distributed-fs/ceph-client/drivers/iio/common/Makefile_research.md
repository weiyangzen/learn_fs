# sources/distributed-fs/ceph-client/drivers/iio/common/Makefile

Purpose: top-level build dispatcher for IIO common helper modules. It includes subdirectories under `drivers/iio/common` so their own Makefiles can add objects based on Kconfig symbols.

Important entries: `obj-y` includes `cros_ec_sensors/`, `hid-sensors/`, `inv_sensors/`, `ms_sensors/`, `scmi_sensors/`, `ssp_sensors/`, and `st_sensors/`. A comment requires alphabetical order.

Control flow: kbuild descends into every listed directory because entries are unconditional `obj-y`; each subdirectory then gates actual object files with `CONFIG_*` symbols.

State and persistence: no runtime state. The file controls build graph inclusion only.

Dependencies and integration: must stay synchronized with `drivers/iio/common/Kconfig`. Since helper modules are shared by multiple sensor drivers, missing a directory prevents selected helper objects from building even if Kconfig enables them.

Risks and test signals: risks are stale ordering or missing directory entries when a helper family is added. Test signals are successful `make drivers/iio/common/` traversal, no kbuild unknown target errors, and all selected common objects appearing in build output.
