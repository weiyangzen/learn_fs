# sources/distributed-fs/ceph-client/drivers/eisa/virtual_root.c

## Purpose
`virtual_root.c` registers a fallback platform-device EISA root for systems without a discoverable PCI/EISA bridge, mainly x86 EISA-only systems.

## Important APIs, types, and functions
The file defines `eisa_root_dev`, `eisa_bus_root`, the `force_probe` module parameter, `virtual_eisa_release()`, and `virtual_eisa_root_init()`. It calls `platform_device_register()` and `eisa_root_register()`.

## Control flow
At `device_initcall`, the virtual platform device is registered, the root's `force_probe` flag is copied from the module parameter, driver data is set, and `eisa_root_register()` probes the default IO port resource from base 0 across `EISA_MAX_SLOTS`. If a real bridge already registered the same root resource, registration fails and the virtual platform device is quietly removed.

## State and persistence behavior
State is static runtime root/platform-device data and the `force_probe` parameter. There is no durable persistence.

## Dependencies and integration points
It depends on platform devices, the global `ioport_resource`, EISA core root registration, and Kconfig limiting this path to x86 EISA builds. `EISA_VLB_PRIMING` changes the default force-probe value.

## Risks and edge cases
Forced probing can touch IO ports on systems that do not actually have EISA. The driver intentionally loses to real root devices through resource conflict. Because the release callback is empty, all data must remain static.

## Test signals
Boot with and without a real PCI/EISA bridge, `force_probe=0/1`, resource conflict handling, VLB priming default behavior, and slot enumeration on EISA-only x86 hardware.
