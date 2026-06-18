## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_printer.h

Purpose: declares configfs option state for the USB printer gadget function.

Important APIs and types:
- `struct f_printer_opts` embeds `usb_function_instance`, stores printer minor, PNP string pointer and ownership flag, request queue length `q_len`, and configfs `lock`/`refcnt`.

Control flow and integration:
- Configfs sets PNP identification and queue depth before bind.
- The printer function uses `minor` to create a printer character device and `q_len` to size USB request queues.

State and persistence:
- Per-instance in-memory options. `pnp_string_allocated` controls ownership cleanup for the PNP string.

Dependencies:
- USB composite framework and printer function implementation.

Risks:
- PNP string lifetime/ownership must be tracked exactly to avoid leaks or freeing static strings.
- Queue depth affects memory and throughput.
- Live changes must respect `refcnt`.

Test signals:
- Create printer gadget with custom PNP string, verify host class detection and bidirectional data path through the character device.
- Repeated bind/unbind should release minors and allocated PNP strings.
