## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.c

Purpose: optional hwmon registration for Atlantic PHY and MAC temperature reporting.

Important APIs/types: defines hwmon callbacks `aq_hwmon_read()`, `aq_hwmon_read_string()`, `aq_hwmon_is_visible()`, `aq_hwmon_ops`, channel info, and `aq_drvinfo_init()`. When `CONFIG_HWMON` is not reachable, `aq_drvinfo_init()` is a no-op.

Control flow: init registers a devm hwmon device using the netdev name and `aq_nic_s` as driver data. Visibility hides PHY or MAC temperature channels unless corresponding firmware/hardware callbacks exist. Reads dispatch channel 0 to `aq_fw_ops->get_phy_temp`, and channel 1 to firmware `get_mac_temp` or hardware `hw_get_mac_temp`.

State and persistence: no persistent state; hwmon device is devm-managed under the PCI device. Temperature values are read live from firmware/hardware.

Dependencies/integration: depends on `aq_nic` for ops and PCI device, Linux hwmon framework, and firmware/hardware callback availability.

Risks: callbacks are dereferenced through `aq_nic->aq_fw_ops`/`aq_hw_ops`, so init must occur after those are populated. Missing callbacks must remain hidden to avoid unsupported reads. Temperature units follow hwmon expectations and firmware semantics.

Test signals: builds with and without `CONFIG_HWMON`, sysfs hwmon labels and temp inputs, callback absence visibility, and error propagation from firmware/hardware temperature reads.
