<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h

Purpose: extends serial port type identifiers beyond the historical values in `serial.h` for platform UART drivers and generic userspace reporting.

Important APIs, types, and functions: `PORT_*` constants assign stable numeric IDs for NS16550A, XScale, Tegra, Exar, ARM, SPARC, OMAP, Cadence, SiFive, STM32, Qualcomm, Broadcom, Freescale, and many other UART families. `PORT_GENERIC` is `-1` for ports whose exact type is not important to userspace.

Control flow: UART drivers report a type through serial-core data structures or legacy serial ioctls. Userspace tools can display or compare the type without knowing driver internals.

State and persistence behavior: no state is stored in this header. The selected type is runtime driver metadata for a registered serial port.

Dependencies and integration points: includes `linux/serial.h` and integrates with serial core, UART drivers, and setserial-style tooling.

Risks and edge cases: values 0-19 are reserved for historical busybox/setserial compatibility and must not be modified. Adding new types must avoid reusing existing numeric IDs. Userspace should not depend on type IDs for hardware programming.

Test signals: compile coverage for UART drivers, serial ioctl reporting for representative ports, stable numeric values in ABI tests, and generic type reporting for drivers using `PORT_GENERIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h -->
