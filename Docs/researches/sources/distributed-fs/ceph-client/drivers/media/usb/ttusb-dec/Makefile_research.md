
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Makefile

## Purpose
The Makefile builds the TTUSB DEC transport and frontend support objects.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_DVB_TTUSB_DEC) += ttusb_dec.o ttusbdecfe.o`.

## Control Flow
Kbuild compiles and links both C files into the DEC driver when the Kconfig symbol is enabled.

## State and Persistence
No runtime state exists here.

## Dependencies and Integration Points
The mapping ensures `ttusb_dec.c` can call the attach functions exported from `ttusbdecfe.c` in the same build unit/module set.

## Risks and Edge Cases
Both objects are required; omitting `ttusbdecfe.o` leaves unresolved attach symbols or no frontend support.

## Test Signals
Build `CONFIG_DVB_TTUSB_DEC=m` and confirm both objects are linked into the produced module.
