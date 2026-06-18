# sources/distributed-fs/ceph-client/drivers/usb/dwc3/host.c

Purpose: creates and tears down the child `xhci-hcd` platform device used when a DWC3 controller operates in host mode.

Important APIs/functions: `dwc3_host_init` and `dwc3_host_exit` are exported. Helpers include `dwc3_power_off_all_roothub_ports`, `dwc3_xhci_plat_start`, `dwc3_host_fill_xhci_irq_res`, and `dwc3_host_get_irq`. A small `xhci_plat_priv` hook enables SUSPHY when the primary HCD starts.

Control flow: host init first temporarily maps the xHCI MMIO range and clears `PORT_POWER` for every root-hub port to avoid VBUS glitches. It resolves the IRQ by named resources (`host`, `dwc_usb3`) or index 0, allocates an `xhci-hcd` platform device, attaches DWC3 xHCI resources, adds software-node quirks and capability properties, passes platform private data, registers the child, and propagates wakeup settings. Exit disables child wakeup, enables SUSPHY, unregisters xHCI, and clears `dwc->xhci`.

State and persistence: persistent state is `dwc->xhci`, populated xHCI resource entries, wakeup configuration, and transient root-hub port power state. Software-node properties persist with the child device.

Dependencies and integration: depends on Linux platform devices, IRQ helpers, OF naming, USB HCD APIs, xHCI platform private data, xHCI register definitions, and DWC3 core resources. The child xHCI driver owns actual host operation after registration.

Risks: temporary MMIO mapping must match resource flags, and blindly powering off ports can surprise platforms if called at the wrong point. IRQ lookup fallback must not mask probe deferral. Property array size must match optional property count. Host exit assumes `dwc->xhci` is valid. Wakeup propagation matters when switching from gadget mode.

Test signals: successful xHCI child probe, root-hub enumeration, role switch from gadget to host, wakeup enable propagation, and absence of VBUS glitches on affected boards. Failures include IRQ probe deferral, xHCI registration errors, powered-off ports not recovering, or suspend/resume regressions.
