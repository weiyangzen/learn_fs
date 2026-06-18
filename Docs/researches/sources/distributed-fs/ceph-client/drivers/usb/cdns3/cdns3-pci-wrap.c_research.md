# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-pci-wrap.c

Purpose: Wraps a Cadence PCI USBSS device exposing separate PCI functions/BARs into a single `cdns-usb3` platform device with named host, peripheral, and OTG resources.

Important APIs, types, and functions: `struct cdns3_wrap` stores the synthesized platform device, six resources, and the devfn that registered the platform child. `cdns3_get_second_fun` finds the peer PCI function. `cdns3_pci_probe` enables PCI, fills resources from BARs and IRQs, and registers the platform device when both functions are available. `cdns3_pci_remove` unregisters the platform child and frees shared wrapper memory.

Control flow: The wrapper accepts only devfn 0 (host/device) and devfn 1 (OTG). Each function probe records its piece of the resource array. When the peer function is already enabled, the second probe creates `PLAT_DRIVER_NAME` (`cdns-usb3`) with resources named `host`, `peripheral`, `otg`, `xhci`, `dev`, and `otg` memory as appropriate.

State and persistence behavior: Shared state is `struct cdns3_wrap` referenced from PCI drvdata of both functions. It persists only while the PCI functions are bound. The platform child owns no permanent storage.

Dependencies and integration points: Uses Linux PCI, platform-device registration, DMA mask propagation, and Cadence PCI IDs. The generated platform device is consumed by `cdns3-plat.c`.

Risks: Peer-function discovery with `pci_get_device` is delicate and may mishandle multiple identical devices if not constrained by bus/device context. Lifetime depends on `pci_is_enabled(func)` and shared `wrap` ownership. Both device and host IRQ resources may use the same IRQ for function 0, so downstream IRQ sharing must work.

Test signals: Probe order with function 0 first and function 1 first, remove order in both directions, multiple identical PCI cards, platform resource names/ranges, shared IRQ operation, and module unload/reload.
