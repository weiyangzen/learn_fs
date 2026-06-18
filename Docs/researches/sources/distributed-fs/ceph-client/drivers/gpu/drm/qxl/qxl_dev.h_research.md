# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dev.h

Purpose: This header embeds QXL/SPICE device protocol definitions used to communicate between the guest DRM driver and the virtual QXL host device.

Important APIs, types, and functions: It defines protocol enums for SPICE image/bitmap/surface/clip/brush/cursor types, QXL device revisions, PCI range indices, I/O command numbers, interrupt bits, ring sizes, ROM/RAM header layout, command and release structures, draw/cursor/surface/image/bitmap structures, monitor config structures, and packed protocol data types such as `QXLPHYSICAL`.

Control flow: There is no executable control flow; runtime files populate these packed structs in guest-visible VRAM or surface memory and notify the host via command rings or I/O ports. The append-only comments document ABI constraints for QXL revision compatibility.

State and persistence: Structures in this header describe persistent shared memory layout: `struct qxl_rom` is host-provided read-only configuration, `struct qxl_ram_header` is guest/host shared command and status memory, and command payloads persist until the host completes releases.

Dependencies and integration points: Included by `qxl_drv.h` and used across command, display, image, draw, ioctl, and release code. Values must match spice-protocol/QXL host implementations, especially packed layout and integer widths.

Risks: Numeric value or packing changes would break guest/host ABI. Many structs contain variable-length tails, so size calculations in callers must avoid overflow and account for packed layout. Endianness and alignment assumptions are protocol-sensitive.

Test signals: Compile-time structure size checks would be valuable; runtime validation includes successful QEMU/SPICE boot, command submission, cursor updates, monitor config exchange, and surface create/destroy across QXL revisions.
