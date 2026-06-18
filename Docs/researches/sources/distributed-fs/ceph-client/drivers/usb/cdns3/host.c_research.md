# sources/distributed-fs/ceph-client/drivers/usb/cdns3/host.c

Purpose: implements the Cadence host role by powering the DRD block into host mode and registering an `xhci-hcd` child platform device with Cadence-specific xHCI quirks.

Important APIs/types/functions: main role callbacks are `__cdns_host_init`, `cdns_host_exit`, and `cdns_host_resume`; public initializer is `cdns_host_init`. xHCI platform private data includes `xhci_cdns3_plat_start`, `xhci_cdns3_resume_quirk`, `xhci_plat_cdns3_xhci`, and `xhci_plat_cdnsp_xhci`.

Control flow: role start calls `cdns_drd_host_on`, allocates `xhci-hcd`, attaches xHCI MMIO/IRQ resources, chooses CDNS3 or CDNSP quirks, optionally allows default runtime PM, registers the child device, and caches xHCI regs from the resulting HCD. Stop unregisters the child, frees private data, clears `host_dev`, and powers host mode off.

State and persistence: stores host child device in `cdns->host_dev`, xHCI private data in `cdns->xhci_plat_data`, and xHCI register base in `cdns->xhci_regs`. Resume marks xHCI `power_lost`.

Dependencies and integration: depends on `drd.c` host on/off, Linux platform-device APIs, xHCI platform driver internals, and xHCI register definitions.

Risks: if `platform_device_add` fails, private data and child device cleanup must remain balanced. `cdns_drd_host_on` return is not checked in `__cdns_host_init`, so later xHCI setup may expose earlier mode-on failures indirectly.

Test signals: host role probe, xHCI child enumeration, runtime PM resume quirk, CDNSP-specific context quirk, host stop/restart during OTG switches, and failure injection around child registration.
