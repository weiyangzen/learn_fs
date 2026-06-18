# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Kconfig

## Purpose
Defines configuration for Technisat/B2C2 FlexCop USB DVB/ATSC devices and optional debug support.

## Important APIs, types, and functions
`DVB_B2C2_FLEXCOP_USB` is a tristate depending on `DVB_CORE` and `I2C`. `DVB_B2C2_FLEXCOP_USB_DEBUG` is a bool depending on the USB driver and selecting shared `DVB_B2C2_FLEXCOP_DEBUG`.

## Control flow and state
No runtime flow. The main symbol builds the USB bus glue module, while the debug symbol enables runtime debug module parameter support compiled into the FlexCop USB source.

## Dependencies and integration points
Integrates with the common B2C2 FlexCop media code via the Makefile include path and common debug option.

## Risks and test signals
Risks are missing dependencies on shared FlexCop common code or overexposed debug options. Test signals are successful module builds with debug on/off and visibility under DVB USB devices.
