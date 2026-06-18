# sources/distributed-fs/ceph-client/drivers/macintosh/macio_asic.c

Purpose: implements the MacIO bus type and device enumeration/resource management for devices inside Apple MacIO ASICs. It adapts Open Firmware child nodes and PCI-attached MacIO chips into `struct macio_dev` devices with driver-model support.

Important APIs and functions: `macio_bus_type` provides match, uevent, probe/remove/shutdown/suspend/resume, and sysfs groups. Exported APIs include `macio_register_driver()`, `macio_unregister_driver()`, `macio_dev_get()`, `macio_dev_put()`, `macio_request_resource(s)()`, `macio_release_resource(s)()`, and `macio_enable_devres()`. Internal enumeration flows through `macio_pci_probe()`, `macio_pci_add_devices()`, and `macio_add_one_device()`.

Control flow: postcore init registers the bus; module init registers a broad Apple PCI driver. Probe filters real MacIO chips with `macio_find()`, handles two-ASIC ordering via `macio_on_hold`, then creates a root MacIO device, first-level children, media-bay children, and ESCC serial children. Each `macio_dev` receives OF node, DMA parameters, resources, interrupts, quirks, and a driver-model name before `of_device_register()`.

State and persistence: global state is the bus registration and optional held chip. Device state persists in allocated `macio_dev` objects until device release. Managed resource state is tracked with devres bitmasks.

Dependencies and integration: depends on PCI, OF address/IRQ helpers, `asm/macio.h`, `pmac_feature`, Linux device core, and sysfs attributes from `macio_sysfs.c`.

Risks: many resource quirks encode old device-tree bugs and are easy to regress. MacIO removal panics rather than hot-unplugging. The Gatwick IRQ fixup helper appears to populate IRQ resources only when `irq_create_mapping()` returns zero, so that path warrants careful validation. Media-bay dynamic behavior is only partly modeled.

Test signals: MacIO bus appears under sysfs, modalias uevents match OF IDs, child devices bind expected drivers, resource reservation/unwind works, media-bay and ESCC children are present, and old machines with Grand Central/OHare/Heathrow/KeyLargo/Gatwick retain expected resource shapes.
