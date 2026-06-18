# sources/distributed-fs/ceph-client/include/media/dvb-usb-ids.h

Purpose: Central catalog of USB vendor/product IDs and convenience macros for DVB USB drivers.

Important APIs/types/functions: `DVB_USB_DEV(pid, vid)` and `DVB_USB_DEV_VER(pid, vid, lo, hi)` expand tokenized vendor/product macro names into `USB_DEVICE` or `USB_DEVICE_VER` table entries. The remainder of the file defines `USB_VID_*` vendor IDs and `USB_PID_*` product IDs for many DVB USB devices, including cold/warm firmware states.

Control flow: Individual USB DVB drivers include this header to build `usb_device_id` tables. On USB probe, kernel matching uses these constants to select the appropriate driver and sometimes distinguish pre- and post-firmware device identities.

State and persistence: No runtime state. It is a compile-time ID registry.

Dependencies and integration: Depends on `<linux/usb.h>` and integrates many DVB USB frontend/bridge drivers with USB core matching.

Risks and test signals: Risks include duplicate or incorrect IDs, swapped vendor/product tokens, missing warm IDs after firmware upload, and stale device naming. Test by compiling all including drivers, checking generated modalias tables, probing representative cold/warm devices, and comparing IDs to hardware descriptors.
