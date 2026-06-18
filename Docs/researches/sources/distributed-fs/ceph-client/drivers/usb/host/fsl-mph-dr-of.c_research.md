# sources/distributed-fs/ceph-client/drivers/usb/host/fsl-mph-dr-of.c

## Purpose
`fsl-mph-dr-of.c` is Freescale USB2 device-tree glue. It reads flat device-tree properties for multi-port host and dual-role USB controllers, creates child platform devices for the appropriate host/OTG/device drivers, fills `struct fsl_usb2_platform_data`, and supplies MPC512x-specific PHY/clock initialization hooks.

## Important APIs, Types, and Functions
- Mode data: `struct fsl_usb2_dev_data` and `dr_mode_data[]` map `dr_mode` to child driver names and operating modes.
- Parsing/helpers: `get_dr_mode_data()`, `determine_usb_phy()`, and `usb_get_ver_info()`.
- Child registration: `fsl_usb2_device_register()` allocates a platform device, copies resources/platform data, inherits DMA mask and OF node, and registers it.
- Driver lifecycle: `fsl_usb2_mph_dr_of_probe()`, `fsl_usb2_mph_dr_of_remove()`, and `__unregister_subdev()`.
- MPC512x support: `fsl_usb2_mpc5121_init()`, `fsl_usb2_mpc5121_exit()`, and `fsl_usb2_mpc5121_pd`.

## Control Flow
Probe verifies device availability and match data, copies compatible-specific platform data, selects host/otg/peripheral mode, applies MPH port-enable flags or DR polarity flags, parses PHY type and controller version, reads erratum booleans and `phy-clk-valid`, and rejects sysif-register configurations without a known controller version. It then iterates selected child driver names and registers each child using the parent resources. Remove unregisters all children.

For MPC512x, the init callback obtains/enables the `ipg` clock and, for UTMI-wide PHY mode, programs USBGENCTRL/ISIPHYCTRL bits for PHY enable, oscillator enable, and polarity settings. Exit disables the clock and clears `regs`.

## State and Persistence Behavior
The file stores no long-lived private object beyond static child index `idx` and platform data copied into child devices. Parsed flags persist as child platform data until device unregister. Hardware register effects from MPC512x init persist until child exit or reset.

## Dependencies and Integration Points
It depends on Linux OF/platform-device/DMA/clock APIs and Freescale USB platform definitions from `linux/fsl_devices.h`. It instantiates drivers named `fsl-ehci`, `fsl-usb2-otg`, and `fsl-usb2-udc`, passing parent resources and OF association to children.

## Risks and Test Signals
Risks include fallback to host mode on invalid/missing `dr_mode`, static `idx` reuse behavior across devices/probe cycles, resource sharing among multiple child devices, property spelling differences for errata (`usb-erratum` vs `usb_erratum`), and missing cleanup if registering later children fails after earlier ones succeeded. Test signals include DT matrices for MPH/DR/OTG/peripheral, controller version compatibles, PHY modes, erratum flags, MPC512x clock failure paths, child device counts, and remove-time child unregister.
