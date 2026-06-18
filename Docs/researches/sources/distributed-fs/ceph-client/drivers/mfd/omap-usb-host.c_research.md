# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c

## Purpose
`omap-usb-host.c` is the parent USBHS host-controller driver for TI OMAP EHCI/OHCI blocks. It owns the common UHH register programming, revision-dependent port-mode setup, runtime clock handling, and creation of EHCI/OHCI child devices.

## Important APIs, Types, And Functions
`struct usbhs_hcd_omap` stores per-port clocks, OMAP revision, UHH base, and `usbhs_omap_platform_data`. `omap_usbhs_alloc_child()` and `omap_usbhs_alloc_children()` create legacy platform children. `usbhs_runtime_resume()` and `usbhs_runtime_suspend()` gate TLL and per-port clocks. `omap_usbhs_init()`, `omap_usbhs_rev1_hostconfig()`, and `omap_usbhs_rev2_hostconfig()` program `OMAP_UHH_HOSTCONFIG`. `usbhs_omap_get_dt_pdata()` maps DT `portN-mode` strings into platform-data enums.

## Control Flow
Probe builds platform data from DT when needed, maps the UHH resource, initializes TLL, enables runtime PM long enough to read `OMAP_UHH_REVISION`, derives the port count, acquires revision-specific clocks, selects UTMI clock parents for OMAP4+ PHY/TLL modes, writes HOSTCONFIG, and then either populates DT child nodes or allocates legacy `ehci-omap` and `ohci-omap3` children. Remove disables runtime PM and depopulates/unregisters children.

## State And Persistence
Driver state is in devm-managed memory and volatile hardware registers. Runtime PM transitions persist only while the device is active. Child devices receive copied platform data and a 32-bit DMA mask.

## Dependencies And Integration Points
It depends on platform resources named `ehci`, `ehci-irq`, `ohci`, and `ohci-irq`, OMAP USB platform data, the paired TLL exports in `omap-usb.h`, DT compatibles `ti,usbhs-host`, `ti,ehci-omap`, and `ti,ohci-omap3`, clock framework APIs, and EHCI/OHCI child drivers.

## Risks
Probe calls `omap_tll_init()` but does not check its return, so init ordering relies on `fs_initcall` sequencing. OMAP4+ clock lookup treats missing per-port clocks as fatal despite comments suggesting optional behavior. Port-mode and revision logic directly changes HOSTCONFIG bit fields, so DT mistakes can disable ports or select the wrong PHY/TLL/HSIC mode. Runtime PM clock enable errors are logged but not propagated.

## Test Signals
Useful tests include DT and legacy platform boots, OMAP3 and OMAP4+ revision paths, all PHY/TLL/HSIC port combinations, runtime suspend/resume balance, child-device creation and removal, USB enumeration through EHCI/OHCI, and failure injection for missing clocks/resources.
