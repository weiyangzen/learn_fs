# sources/distributed-fs/ceph-client/include/uapi/linux/usbdevice_fs.h

Purpose: Defines the usbfs `/dev/bus/usb` userspace ABI for direct USB device access.

Important APIs/types/functions: Structs describe control/bulk transfers, interface setting, disconnect signals, driver query, connection info, extended connection info, URBs with iso packet descriptors, driver-private ioctls, hub port info, disconnect claim, and stream allocation. Flags define URB behavior, URB types, capabilities, and disconnect-claim modes. Ioctls support control/bulk transfer, reset/clear halt, set interface/configuration, get driver, submit/discard/reap URBs, disconnect signal, claim/release interface or port, connect/disconnect/reset, query capabilities/speed/connection info, allocate/free streams, drop privileges, and suspend control. 32-bit compat ioctl aliases are provided for pointer-sized structs.

Control flow: Userspace opens a usbfs device node, claims interfaces, performs synchronous control/bulk ioctls or asynchronous URB submit/reap cycles, optionally disconnects kernel drivers, allocates streams, and releases/reset devices as needed.

State and persistence behavior: Claimed interfaces, dropped privileges, submitted URBs, stream allocations, suspend forbids, and disconnect claims are runtime state tied to the file/device. Device configuration changes affect hardware until changed again or reset.

Dependencies and integration points: Includes `linux/types.h` and `linux/magic.h`; integrates with USB core, libusb, device firmware tools, scanners, programmers, and test harnesses.

Risks: Direct device access is security-sensitive. Pointer fields and compat ioctls require careful translation. URB lifetime, disconnect races, mmap capability, privilege dropping, and kernel-driver detachment are key hazards.

Test signals: libusb-style claim/transfer tests, sync control/bulk, async interrupt/iso/bulk URBs, disconnect during pending URBs, reset/clear halt, stream allocation, capability queries, drop privileges, suspend forbid/allow/wait, and 32-bit compat coverage.
