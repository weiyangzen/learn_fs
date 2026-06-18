<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h

## Purpose
Kernel-private interface for the USB stream helper, defining stream URB counts, kernel-side state, and lifecycle functions.

## APIs, Types, and Functions
Defines `USB_STREAM_NURBS` and `USB_STREAM_URBDEPTH`, `struct usb_stream_kernel`, and prototypes for `usb_stream_new()`, `usb_stream_free()`, `usb_stream_start()`, and `usb_stream_stop()`.

## Control Flow, State, and Persistence
The header contains no logic, but `struct usb_stream_kernel` persists the bridge between shared `struct usb_stream` memory, USB device, read/write URBs, idle/completed URB pointers, synchronization balance, wait queue, output phase accumulator, and normalized frequency.

## Dependencies and Integration
Includes `<uapi/sound/usb_stream.h>` for the userspace-visible stream layout. Implemented by `usb_stream.c` and expected to be embedded by device-specific code that owns the USB device and endpoints.

## Risks and Test Signals
Risks include ABI coupling to UAPI structures, assumptions that four URBs and depth four are enough for all supported devices, and state fields being updated from interrupt context. Build coverage plus stress tests around stream start/stop, wait queue wakeups, and high/full-speed rates validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.h -->
