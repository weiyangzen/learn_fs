# sources/distributed-fs/ceph-client/drivers/net/can/usb/peak_usb/Makefile

Purpose: defines the Kbuild composition for the PEAK-System USB CAN driver module. It builds the aggregate `peak_usb.o` module when `CONFIG_CAN_PEAK_USB` is enabled.

Important APIs/types/functions: no runtime APIs are declared. The relevant Kbuild variables are `obj-$(CONFIG_CAN_PEAK_USB) += peak_usb.o` and `peak_usb-y = pcan_usb_core.o pcan_usb.o pcan_usb_pro.o pcan_usb_fd.o`.

Control flow: Kbuild links the PEAK common core and the protocol/device-family objects for classic PCAN-USB, PCAN-USB Pro, and PCAN-USB FD support into one module. Runtime device dispatch is handled by the C sources included here, not by this Makefile.

State and persistence behavior: no runtime state and no persistence. This file only controls object inclusion.

Dependencies/integration points: integrates with kernel configuration through `CONFIG_CAN_PEAK_USB`. The object list is the build-time integration point for all PEAK USB subdrivers.

Risks: stale object lists can create link failures or silently exclude support for a PEAK hardware family. Any new source added to the PEAK driver family must be reflected here.

Test signals: kernel build tests with `CONFIG_CAN_PEAK_USB` enabled are the primary signal; runtime smoke tests should verify devices from each included PEAK family bind to the aggregate module.
