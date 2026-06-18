# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-omap.c

## Purpose
TI OMAP3/OMAP4 EHCI host glue. It binds the EHCI core to OMAP USBHOST platform data, manages per-port USB PHYs, enables runtime PM, writes an OMAP EHCI unsuspend workaround register, and registers the host controller.

## Important APIs, types, and functions
`struct omap_hcd` tracks up to `OMAP3_HS_USB_PORTS` PHY pointers and port count. `ehci_hcd_omap_probe()` and `ehci_hcd_omap_remove()` own lifecycle. `ehci_write()` writes raw OMAP EHCI insn registers. `EHCI_INSNREG04_DISABLE_UNSUSPEND` disables an undocumented behavior where clearing Run/Stop unsuspends ports. `ehci_omap_overrides` only adds private storage.

## Control flow
Probe requires a parent device and platform data, pulling parent platform data for DT children. It maps MMIO, coerces a 32-bit DMA mask, creates the HCD, sets resource metadata and caps, then gets PHYs by `phys` phandle for each configured port. PHY-mode ports are initialized and unsuspended before `usb_add_hcd()`. Runtime PM is enabled and synchronously acquired, the OMAP workaround bit is written, and then non-PHY modes such as HSIC bring their reset-modeled PHY out of suspend after the HCD is live. Remove unregisters the HCD, shuts down all PHYs, drops the HCD, and disables runtime PM.

## State and persistence behavior
Driver-private state is limited to `struct omap_hcd`. Persistent external state includes PHY init/suspend state, runtime-PM active usage count, and the EHCI insn register workaround bit. Port configuration comes from platform data and remains board-specific.

## Dependencies and integration points
Depends on OMAP USB platform data (`usbhs_omap_platform_data`), legacy USB PHY APIs, runtime PM, DT phandles, DMA mapping, and shared EHCI core. It matches `ti,ehci-omap`.

## Risks and edge cases
The DT path depends on parent platform data. PHY failures after some ports were initialized require full cleanup. Runtime PM `pm_runtime_get_sync()` return value is not checked, so PM errors could be hidden. The undocumented register write is essential for suspend stability and should not be removed casually.

## Test signals
OMAP3/4 host probe, multiple port modes, missing or deferred PHYs, HSIC reset PHY behavior, runtime suspend/resume, root-hub suspend with the unsuspend workaround, remove after partial probe failure, and DMA allocation coverage are high-value tests.
