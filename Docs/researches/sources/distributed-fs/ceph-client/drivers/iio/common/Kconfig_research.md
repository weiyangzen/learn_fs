# sources/distributed-fs/ceph-client/drivers/iio/common/Kconfig

Purpose: top-level Kconfig aggregation point for IIO common helper modules. It does not define symbols itself; it sources each common subdirectory so helper libraries and sensor-hub bridges become visible under the IIO configuration tree.

Important entries: sourced submenus are `cros_ec_sensors`, `hid-sensors`, `inv_sensors`, `ms_sensors`, `scmi_sensors`, `ssp_sensors`, and `st_sensors`.

Control flow: Kconfig processing includes this file from the wider IIO Kconfig. Each `source` line delegates dependency expressions, help text, and tristate symbols to the subdirectory.

State and persistence: there is no runtime state. Build configuration state is carried by the symbols declared in the sourced files.

Dependencies and integration: path names assume the Linux kernel source layout `drivers/iio/common/...`. Adding or removing a common helper family requires updating this file and the common Makefile together.

Risks and test signals: ordering is simple but missing a source line hides a whole helper family from configuration. Test signals are `scripts/kconfig/conf` parsing without missing files and menu visibility for each subdirectory symbol.
