# sources/distributed-fs/ceph-client/include/linux/usbdevice_fs.h

## Purpose
This kernel header wraps the usbdevfs UAPI and defines 32-bit compatibility structures for usbfs ioctls.

## Important APIs, types, and functions
Under `CONFIG_COMPAT`, it defines `usbdevfs_ctrltransfer32`, `usbdevfs_bulktransfer32`, `usbdevfs_disconnectsignal32`, `usbdevfs_urb32`, and `usbdevfs_ioctl32`, mirroring pointer-bearing UAPI structs with `compat_caddr_t` and fixed-width fields.

## Control flow, state, and persistence
The usbfs ioctl layer copies compat user structures, translates pointers and sizes to native kernel forms, and dispatches to normal usbdevfs handling. The header describes ABI layout only; ioctl state and URB tracking live in usbfs implementation code.

## Dependencies and integration points
It depends on `uapi/linux/usbdevice_fs.h` and `linux/compat.h`. It integrates 32-bit userspace with 64-bit kernels for USB control, bulk, URB, disconnect-signal, and nested ioctl calls.

## Risks and test signals
Risks include ABI layout mismatch, pointer truncation, wrong padding, and unchecked user lengths. Tests should run 32-bit usbfs ioctl exercisers on 64-bit kernels and compare native versus compat behavior.
