# `sources/distributed-fs/ceph-client/include/linux/usb/renesas_usbhs.h`

## Purpose

`renesas_usbhs.h` defines platform callbacks and driver parameters for Renesas USBHS controllers. It describes host/gadget ID detection, VBUS/power/PHY hooks, pipe configuration, DMA alignment, polling delays, SoC feature flags, and platform info passed to the USBHS driver.

## Important APIs, Types, and Constants

- Module IDs distinguish `USBHS_HOST` and `USBHS_GADGET`.
- `struct renesas_usbhs_platform_callback` supplies hardware init/exit, power control, PHY reset, ID detection, VBUS detection/control, and extcon notifier callbacks.
- `struct renesas_usbhs_driver_pipe_config` and `RENESAS_USBHS_PIPE()` describe endpoint type, buffer size/number, and double buffering.
- `struct renesas_usbhs_driver_param` carries pipe arrays, bus wait, detection delays, DMA channel names, D0/D1/D2 callbacks, pio/dma tuning, multi-clk flags, and hardware feature flags.
- `USBHS_USB_DMAC_XFER_SIZE` fixes a DMA transfer granularity used by the driver.
- `struct renesas_usbhs_platform_info` groups callbacks and parameters for platform registration.

## Control Flow and Lifetimes

Platform code provides callbacks and parameters. During probe, the driver initializes hardware, powers clocks, resets PHY, builds pipe resources from the config array, determines host/gadget mode from ID/VBUS callbacks or extcon notifications, and starts the appropriate role. Runtime role changes call notifier/ID/VBUS hooks and may start/stop host or gadget paths.

## State and Persistence Behavior

The platform info is static configuration. Runtime state includes selected role, pipe allocation, DMA channel use, VBUS state, and power/clock state in the driver and hardware.

## Dependencies and Integration Points

It depends on notifier blocks, platform devices, and USB Chapter 9 endpoint types. It integrates Renesas SoC board code, extcon, host/gadget controllers, DMA engines, and PHY/power management.

## Risks and Edge Cases

Pipe configuration must match hardware buffer RAM. Incorrect ID/VBUS callbacks cause wrong role selection. DMA transfer-size and alignment assumptions can corrupt data. Platform power callbacks must be safe across probe failure and suspend/resume. Extcon notifier paths must not race role teardown.

## Test Signals

Probe USBHS in host and gadget modes, validate pipe allocation, VBUS and ID transitions, extcon notifications, DMA and PIO transfers, suspend/resume, probe failure unwinds, and boards with multiple clocks or SoC feature flags.
