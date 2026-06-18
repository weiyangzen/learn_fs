# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-keystone.c

Purpose: TI Keystone and AM654 DWC3 wrapper driver. It powers the optional USB3 PHY, enables wrapper IRQ forwarding where required, and populates the child `snps,dwc3` core.

Important APIs, types, and functions: `struct dwc3_keystone` stores the parent device, USBSS MMIO base, and optional `usb3_phy`. `kdwc3_readl()` and `kdwc3_writel()` wrap register access. `kdwc3_enable_irqs()` and `_disable_irqs()` program `USBSS_IRQENABLE_SET_0`. `dwc3_keystone_interrupt()` clears, re-enables, and EOIs core IRQ status. `kdwc3_probe()` and `kdwc3_remove()` own resource lifecycle.

Control flow: probe allocates private data, maps USBSS registers, gets the optional `usb3-phy`, runtime-resumes the PHY, resets/initializes/powers it, enables runtime PM on the wrapper, optionally skips IRQ setup for `ti,am654-dwc3`, requests the shared IRQ for older Keystone, enables wrapper IRQs, and populates children. Removal disables IRQs for non-AM654, unregisters children, drops runtime PM, powers off/exits the PHY, and releases PHY runtime PM.

State and persistence: no software state beyond private pointers is durable. Hardware state consists of the PHY power/init state and wrapper IRQ enable/status registers. The interrupt handler always acknowledges and re-arms the wrapper interrupt rather than inspecting child DWC3 event content.

Dependencies and integration: depends on platform MMIO, OF population, the generic PHY framework, and runtime PM. It integrates with the DWC3 core by creating the OF child device and with TI wrapper interrupt routing through USBSS registers.

Risks: error paths after `phy_pm_runtime_get_sync()` must unwind PHY power/init state correctly. AM654 skips IRQ processing entirely, so compatible matching must reflect hardware behavior. The IRQ handler writes enable/status/EOI registers unconditionally, so incorrect resource mapping or sharing could mask interrupts.

Test signals: boot logs should show successful PHY reset/init/power-on and child creation. Regression tests should exercise non-AM654 interrupt handling, AM654 no-IRQ probe path, PHY probe defer, and removal/unbind cleanup without dangling child devices.
