# sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.h

Purpose: defines the shared Cadence USBSS/CDNSP core data model and exported core lifecycle APIs used by DRD, host, gadget, and platform glue code.

Important APIs/types/functions: declares `struct cdns_role_driver`, `struct cdns3_platform_data`, `struct cdns`, controller version constants, platform quirk bits, `CDNS_XHCI_RESOURCES_NUM`, and prototypes for `cdns_hw_role_switch`, `cdns_init`, `cdns_remove`, and PM helpers.

Control flow: no executable flow beyond PM stubs when `CONFIG_PM_SLEEP` is disabled. The header defines the callback contract that `core.c` invokes for each role: `start`, `stop`, `suspend`, and `resume`.

State and persistence: `struct cdns` is the persistent controller object. It stores MMIO mappings for xHCI/device/OTG variants, IRQs, role driver table, current role, child devices, PHYs, role switch, low-power/wakeup flags, platform data, spinlock/mutex, xHCI private data, APB timeout override, and gadget init callback.

Dependencies and integration: depends on USB OTG and USB role headers and is included across cdns3 DRD/host/gadget code. Glue drivers fill resources and platform data before calling `cdns_init`.

Risks: the struct mixes fields for three controller generations; code must select the right register pointer according to `version`. Role-array indexing assumes Linux `enum usb_role` values up to `USB_ROLE_DEVICE`.

Test signals: compile coverage across host-only, gadget-only, OTG, and PM-disabled builds confirms callback stubs and struct users remain consistent.
