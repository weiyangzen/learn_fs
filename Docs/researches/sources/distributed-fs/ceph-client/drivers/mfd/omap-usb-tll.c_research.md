# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-tll.c

## Purpose
`omap-usb-tll.c` drives the OMAP USB TLL block used by OMAP EHCI/OHCI ports in TLL, OHCI FS/LS, and HSIC modes. It exposes helper functions consumed by the USBHS host parent to initialize, enable, and disable TLL channels.

## Important APIs, Types, And Functions
`struct usbtll_omap` holds the TLL MMIO base, channel count, and channel clocks. Exported APIs are `omap_tll_init()`, `omap_tll_enable()`, and `omap_tll_disable()`. Helpers include `ohci_omap3_fslsmode()` for OHCI port-mode conversion and `omap_usb_mode_needs_tll()` for per-port clock decisions.

## Control Flow
Probe maps the TLL register resource, enables runtime PM, reads `OMAP_USBTLL_REVISION` to choose two or three channels, allocates flexible clock storage, prepares `usb_tll_hs_usb_chN_clk` clocks, drops runtime PM, and publishes a global `tll_dev` under `tll_lock`. `omap_tll_init()` programs shared TLL configuration and per-channel mode bits based on USBHS platform data. Enable and disable gate per-channel clocks around host runtime PM.

## State And Persistence
The driver uses a global `tll_dev` pointer protected by a spinlock, devm-managed device state, prepared clocks, and volatile TLL channel registers. Register state is reprogrammed by `omap_tll_init()` and clock state follows runtime PM users.

## Dependencies And Integration Points
It integrates with `omap-usb-host.c` through `omap-usb.h`, with platform data from `<linux/platform_data/usb-omap.h>`, DT compatible `ti,usbhs-tll`, clock framework, MMIO accessors, and runtime PM.

## Risks
The exported helpers return `-ENODEV` when called before probe, but the host driver ignores the init return. The helpers use a spinlock while dereferencing device state and touching registers/clocks; changes must preserve sleepability constraints. Channel count is revision-derived and port-mode arrays must be large enough for all channels. The HSIC path relies on UTMI-style configuration bits.

## Test Signals
Exercise probe before host init, all known TLL revisions, TLL-free PHY-only setups, OHCI FS/LS modes, EHCI TLL and HSIC modes, runtime PM reference balance, channel clock failure handling, and remove while host children are gone.
