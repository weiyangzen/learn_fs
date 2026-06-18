# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox.c

Purpose: implements the low-level AMD XDNA mailbox transport over firmware-provided ring buffers and mailbox registers. It sends host-to-firmware messages, receives firmware responses through IRQ/workqueue, matches responses by message ID, and handles ring wrap with tombstones.

Important APIs/functions: `xdnam_mailbox_create()` records mailbox/ring resource bases. `xdna_mailbox_alloc_channel()` creates a channel and RX workqueue. `xdna_mailbox_start_channel()` validates power-of-two rings, records X2I/I2X resources, initializes xarray message tracking, reads initial pointers, requests IRQ, and clears interrupt state. `xdna_mailbox_send_msg()` validates size/alignment/tombstone, builds a protocol header, allocates a magic-tagged message ID, copies payload, and writes the package to the ring. RX flow uses `mailbox_irq_handler()`, `mailbox_rx_worker()`, `mailbox_get_msg()`, and `mailbox_get_resp()` to consume responses and call callbacks.

Control flow: AIE2 startup creates the mailbox and management channel. Message helper calls send and waits on a completion. Stop frees IRQ, drains RX work, completes pending messages with NULL data, and destroys the xarray.

State and persistence: `mailbox_channel` stores ring resources, IRQ, interrupt register, message ID xarray, cached tail/head, workqueue, RX work, and bad-state flag. Pending requests persist until response, timeout cleanup, or channel stop.

Dependencies: DRM managed allocation, Linux xarray with IRQ locking, request_irq, workqueues, IO memcpy, bitfields, tracepoints, and `amdxdna_mailbox.h`.

Risks: ring pointer validation is safety-critical; invalid firmware tail/head marks channel bad and disables further RX. Send-side timeout parameter is currently not used by `mailbox_send_msg()` beyond helper wait. Large-message splitting is explicitly not supported despite header fields.

Test signals: ring wrap/tombstone, full-ring polling, invalid alignment/size/data, bad message ID, IRQ storms, response callback errors, stop with pending messages, and firmware malformed tail/size values.
