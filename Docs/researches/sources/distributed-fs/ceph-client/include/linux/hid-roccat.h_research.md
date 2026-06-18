# sources/distributed-fs/ceph-client/include/linux/hid-roccat.h

## Purpose
`hid-roccat.h` is the small shared interface for legacy Roccat HID device support. It declares a Roccat-specific ioctl for report size and in-kernel helper functions used by Roccat HID drivers to expose device reports through a class/minor interface.

## Important APIs, Types, And Functions
`ROCCATIOCGREPSIZE` is an `_IOR('H', 0xf1, int)` ioctl that reports the device report size. Under `__KERNEL__`, the file declares `roccat_connect()`, `roccat_disconnect()`, and `roccat_report_event()`. The helpers connect a HID device to the Roccat class, release by minor, and forward raw report data.

## Control Flow And State
A Roccat-specific HID driver calls `roccat_connect()` during probe after HID setup, stores the returned minor, forwards reports through `roccat_report_event()`, and calls `roccat_disconnect()` during remove. State is owned by the Roccat class implementation, not this header, and keyed by the allocated minor plus report size.

## Dependencies And Integration Points
It includes `linux/hid.h` and `linux/types.h`, so it integrates directly with `struct hid_device` and HID raw event paths. It also exports a userspace ABI through the ioctl constant.

## Risks
The ioctl number and report-size behavior are ABI and must remain stable. Risks include minor lifetime mismatches, forwarding events after disconnect, wrong report size advertised to userspace, and hidden dependency on the Roccat class being initialized before device probe paths call `roccat_connect()`.

## Test Signals
Probe/remove a supported Roccat HID device, verify minor allocation and cleanup, issue `ROCCATIOCGREPSIZE`, stream reports to userspace, and test disconnect while readers are open.
