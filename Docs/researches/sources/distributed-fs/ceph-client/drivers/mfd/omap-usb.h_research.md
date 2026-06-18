# sources/distributed-fs/ceph-client/drivers/mfd/omap-usb.h

## Purpose
`omap-usb.h` is the local bridge header between the OMAP USBHS host parent and the OMAP USB TLL driver.

## Important APIs, Types, And Functions
It declares `omap_tll_init(struct usbhs_omap_platform_data *pdata)`, `omap_tll_enable(struct usbhs_omap_platform_data *pdata)`, and `omap_tll_disable(struct usbhs_omap_platform_data *pdata)`.

## Control Flow
There is no executable flow. The declarations define the call sequence expected by the host driver: initialize channel registers during host probe, enable TLL clocks on host runtime resume, and disable them on runtime suspend.

## State And Persistence
No state is stored in the header. State lives in `omap-usb-tll.c` and in platform data supplied by `omap-usb-host.c`.

## Dependencies And Integration Points
The API depends on `struct usbhs_omap_platform_data` from the OMAP USB platform-data header. It is included by both OMAP USB MFD source files and is the only local compile-time contract between them.

## Risks
The header does not encode ownership, locking, or return-value requirements. Callers must know that TLL probe publishes global state and that helpers may fail with `-ENODEV`.

## Test Signals
Build coverage across both source files, successful symbol export/linking, and boot tests where TLL is initialized before USBHS host probe are the relevant signals.
