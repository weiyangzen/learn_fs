# sources/distributed-fs/ceph-client/drivers/hwmon/via686a.c

## Purpose
Legacy hwmon driver for VIA VT82C686A/VT82C686B southbridge integrated sensors. It reports five voltage inputs, two fans, three temperatures, limits, fan dividers, alarms, and name through manually defined sysfs attributes.

## Important APIs, Types, and Functions
`struct via686a_data` caches ISA I/O base, hwmon device, update mutex, register snapshots, fan dividers, and alarm bits. Conversion helpers implement board-specific voltage factors, fan RPM conversion, and LUT-based temperature conversion. `via686a_update_device()` refreshes all measurements every 1.5 seconds. `via686a_pci_probe()` discovers the ISA base from PCI config, optionally forces/enables it, then registers a platform driver/device for the I/O region.

## Control Flow
The PCI driver probes the VIA southbridge function, determines the monitoring I/O base, enables sensors if forced, registers the platform driver, and adds a platform device. Platform probe reserves the ISA region, allocates state, starts monitoring, configures temperature interrupt mode, creates a single sysfs group, and registers hwmon. Sysfs reads use the cached update routine; writes update cached limits/dividers and immediately write ISA registers.

## State and Persistence
Measurements and limits are cached for 1.5 seconds under `update_lock`. User-written min/max/fan divider/temp thresholds persist in chip registers and cached fields. The module keeps global `pdev` and `s_bridge` because only a single device is supported and the PCI probe deliberately returns failure after holding a reference so other drivers can bind the same PCI device.

## Dependencies and Integration Points
Depends on PCI ID `PCI_DEVICE_ID_VIA_82C686_4`, ISA port I/O, ACPI resource conflict checks, platform device wrappers, legacy hwmon sysfs helpers, and module parameter `force_addr`.

## Risks
Legacy manual sysfs and ISA access have many scaling edge cases. Temperature conversion relies on historical LUTs rather than a datasheet formula. PCI probe intentionally returns `-ENODEV` after creating side effects, so init/exit lifecycle depends on the global bridge reference. Only one device is supported. Fan divider writes do not preserve fan minimum RPM semantics beyond raw register recalculation at the current divider.

## Test Signals
Verify PCI config base/enable handling, `force_addr` path, ACPI conflict rejection, sysfs group unwind, cache refresh timing, voltage conversion round trips, temperature LUT boundaries, fan RPM zero/saturation behavior, alarm bit mapping, and module exit unregistering platform resources only when `s_bridge` was acquired.
