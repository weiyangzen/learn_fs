## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_serial.h

Purpose: declares the public interface for USB gadget serial/TTY utilities.

Important APIs and types:
- `MAX_U_SERIAL_PORTS` limits dynamic `ttyGS*` ports to 8.
- `struct f_serial_opts` is generic serial configfs option state with `usb_function_instance`, port number, protocol, lock, and instance count.
- `struct gserial` embeds `usb_function`, stores linked `gs_port`, IN/OUT endpoints, CDC line coding, and connect/disconnect/send_break callbacks.
- Exports request helpers `gs_alloc_req()` / `gs_free_req()`.
- Exports line allocation/free, optional console get/set, connect/disconnect, and suspend/resume APIs.

Control flow and integration:
- Serial-like functions allocate a line, bind descriptors/endpoints to a `gserial`, then call `gserial_connect()` on USB activation and `gserial_disconnect()` on deactivation.
- Function-specific control handlers can update or read `port_line_coding` through the `gserial` object.
- TTY devices are managed by `u_serial.c`, not by each individual function.

State and persistence:
- `gserial->ioport` is valid only while connected.
- `port_line_coding` persists across connect/disconnect by copyback in `u_serial.c`.

Dependencies:
- USB composite and CDC line coding definitions.

Risks:
- `MAX_U_SERIAL_PORTS` is fixed; configfs users must handle `-ENXIO`/allocation failure when exhausted.
- Callback execution context can be IRQ-like; callbacks must avoid sleeping unless implementation guarantees context.
- Endpoint pointers must be configured and enabled by speed before connect.

Test signals:
- Compile ACM/gserial/OBEX users.
- Validate line allocation exhaustion, disconnect without connect, and suspend/resume callback ordering.
