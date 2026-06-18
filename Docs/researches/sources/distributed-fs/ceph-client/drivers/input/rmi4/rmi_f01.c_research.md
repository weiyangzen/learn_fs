<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c

## Purpose
`rmi_f01.c` implements RMI4 Function 01, the mandatory device-control function. It reads product/manufacturing properties, configures global sensor control and power-management registers, creates informational sysfs attributes, handles reset attention events, and manages sleep/resume behavior.

## Important APIs, Types, and Functions
The file defines `struct f01_basic_properties`, `struct f01_device_control`, and `struct f01_data`. Property parsing is in `rmi_f01_read_properties()`, and the product string API is `rmi_f01_get_product_ID()`. Sysfs show functions expose manufacturer ID, date of manufacture, product ID, firmware ID, and package ID on the physical RMI device. Lifecycle callbacks are `rmi_f01_probe()`, `rmi_f01_remove()`, `rmi_f01_config()`, `rmi_f01_suspend()`, `rmi_f01_resume()`, and `rmi_f01_attention()`, collected in `rmi_f01_handler`.

## Control Flow
Probe optionally reads F01 OF power-management properties, allocates private data, reads control register 0, applies `nosleep` policy, clears unexpected sleep mode, sets the configured bit, writes control 0, clears pending IRQs by dummy reading interrupt status, reads query properties, logs product information, walks optional doze/wakeup/holdoff control registers after the IRQ mask registers, validates that the device did not reset during setup, stores drvdata, and creates the sysfs group. Config rewrites saved control/doze fields after a core reset. Attention reads device status, warns on bootloader mode, and invokes the physical driver's reset handler if the device is unconfigured.

## State and Persistence
`struct f01_data` persists for the F01 function device lifetime and caches properties, control register values, optional register addresses, old nosleep state, suspended flag, and IRQ-register count. Sysfs values are read-only and reflect cached query data. Power-management settings are restored after resume or reset using the cached values.

## Dependencies and Integration Points
The file depends on the RMI bus/driver helpers, `rmi_get_platform_data()`, OF property parsing, sysfs, unaligned little-endian helpers, and the physical driver's reset callback. F01 is always included in `rmi_core` and suppresses user unbinding because the core depends on it.

## Risks and Edge Cases
F01 query layouts are variable: sensor ID, query 42, DS4 query length, package ID, and build ID alter offsets. Miscomputing these offsets corrupts property parsing. `package_id` is declared `u32` but read from a little-endian 64-bit buffer, truncating higher bits. Suspend writes reserved sleep mode 3 for wake-capable devices by design; platform compatibility should be validated. A reset during probe returns `-EINVAL`, while a later unconfigured status triggers full reset/config callbacks.

## Test Signals
Validate sysfs attributes, F01 property parsing on devices with and without DS4 queries, configurable doze/wakeup/holdoff OF properties, reset attention recovery, suspend/resume sleep mode writes, bootloader warnings, and interaction with the shared input device name set from product ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f01.c -->
