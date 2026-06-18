# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/Makefile

## Purpose
Builds the B2C2 FlexCop USB module from its USB transport source.

## Important APIs, types, and functions
Defines `b2c2-flexcop-usb-objs := flexcop-usb.o` and adds `b2c2-flexcop-usb.o` when `CONFIG_DVB_B2C2_FLEXCOP_USB` is enabled.

## Control flow and state
No runtime flow. The object composition links only the USB glue file, relying on external/common FlexCop objects through kernel media build dependencies.

## Dependencies and integration points
Adds include path to `drivers/media/common/b2c2/`, which supplies `flexcop-common.h` and shared FlexCop APIs called by `flexcop-usb.c`.

## Risks and test signals
Risks are include path drift and unresolved common FlexCop symbols. Test signals are clean module link and successful inclusion of shared common headers.
