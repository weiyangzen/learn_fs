# sources/distributed-fs/ceph-client/drivers/of/platform.c

## Purpose
Creates and destroys Linux platform or AMBA devices from device-tree nodes, including boot-time default population, managed population, and dynamic OF reconfiguration handling.

## Important APIs, types, and functions
Key APIs include `of_find_device_by_node()`, `of_device_add()`, `of_device_register()`, `of_device_unregister()`, `of_device_alloc()`, `of_platform_device_create()`, `of_platform_bus_probe()`, `of_platform_populate()`, `of_platform_default_populate()`, `of_platform_depopulate()`, `devm_of_platform_populate()`, and `devm_of_platform_depopulate()`.

## Control flow
`of_platform_bus_create()` validates compatible properties when strict, skips special nodes, honors auxdata, creates AMBA or platform devices, and recurses into bus-matching children. Default boot population handles reserved memory, firmware, simple-framebuffer, PPC displays, and then the default simple bus table.

## State and persistence behavior
`OF_POPULATED` and `OF_POPULATED_BUS` node flags prevent duplicate creation and guide destruction. Devices hold OF node references through device fwnodes. Managed helpers store devres cleanup state.

## Dependencies and integration points
Depends on OF address/IRQ/MSI helpers, DMA masks, platform bus, optional AMBA, sysfb, device-link sync-state controls, and OF dynamic notifiers.

## Risks and edge cases
Creation failures often collapse to `NULL`; flags must be cleared after failures; dynamic add must clear `FWNODE_FLAG_NOT_DEVICE`; destroy must avoid non-OF-populated devices; reserved-memory handling is intentionally selective.

## Test signals
`unittest.c` validates population, depopulation, IRQ error handling, overlay-triggered devices, and PCI child platform-device address translation. `overlay_test.c` adds KUnit platform-device checks.
