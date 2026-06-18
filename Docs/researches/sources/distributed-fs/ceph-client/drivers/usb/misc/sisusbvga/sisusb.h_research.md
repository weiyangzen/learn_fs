# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb.h

Purpose: Main private/public definitions for the sisusb USB2VGA driver, covering versioning, buffers, USB endpoints, packet format, pseudo PCI address layout, VGA register offsets, device state, and ioctl ABI.

Important APIs and types: `struct sisusb_usb_data`, `struct sisusb_urb_context`, `struct sisusb_packet`, `struct sisusb_info`, `struct sisusb_command`, endpoint constants, buffer sizes, kref helper, endian correction macro, and ioctl numbers `SISUSB_COMMAND`, `SISUSB_GET_CONFIG_SIZE`, and `SISUSB_GET_CONFIG`.

Control flow: this header is consumed by the implementation and userspace ABI consumers. The implementation uses `sisusb_usb_data` to track USB interface/device, kref lifetime, URBs and buffers, readiness flags, framebuffer/MMIO/I/O bases, and chip identity. Command structures define register get/set/mask operations, clear-screen, text-mode handling, and mode setting.

State and persistence: no executable state, but it defines the runtime state layout and stable ioctl ABI. Risks include packed 10-byte USB command packets with endian-sensitive fields, fixed minor 133, fixed large output buffer sizes, legacy pseudo-PCI address assumptions, and ABI compatibility obligations for `struct sisusb_info` and commands. Test signals include ioctl structure size checks, big-endian packet conversion, endpoint mapping, open/disconnect kref paths in implementation, and userspace tool compatibility.
