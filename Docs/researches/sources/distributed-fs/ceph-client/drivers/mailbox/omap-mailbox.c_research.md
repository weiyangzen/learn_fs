# sources/distributed-fs/ceph-client/drivers/mailbox/omap-mailbox.c

Purpose: implements the TI OMAP/K3 mailbox controller, mapping DT child mailbox descriptions to FIFO pairs with interrupt-driven RX and TX-ready completion.

Important APIs/types/functions: `struct omap_mbox_device` stores shared MMIO, IRQ context, user/fifo counts, and SoC interrupt layout. `struct omap_mbox` stores one logical channel's TX/RX FIFO register offsets, IRQ, and `send_no_irq` mode. Core functions read/write FIFOs, enable/disable/ack IRQ bits, handle startup/shutdown, send, suspend/resume, and OF xlate by child phandle.

Control flow: probe reads `ti,mbox-num-users` and `ti,mbox-num-fifos`, parses each child `ti,mbox-tx`/`ti,mbox-rx` tuple into FIFO/IRQ registers, registers a txdone-IRQ controller, and prints the hardware revision under runtime PM. Startup powers the device, requests a threaded shared IRQ, optionally switches the channel to client-ACK txdone for `ti,mbox-send-noirq`, and enables RX IRQ. Normal send writes one 32-bit word if the TX FIFO is not full and enables TX IRQ; TX interrupt disables TX IRQ, acks, and reports txdone. RX interrupt drains all messages and delivers each word to the client.

State and persistence: per-channel FIFO register mapping is built from DT and remains for device lifetime. Runtime PM gates the shared block. System sleep saves IRQ enable registers and can reject suspend if exclusive hardware has unread messages.

Dependencies and integration: depends on OMAP/K3 mailbox DT bindings, runtime PM, generic mailbox framework, and shared IRQ behavior. Supports OMAP2/3/4 and AM64/AM654 interrupt layouts.

Risks: `send_no_irq` path writes then locally reads/acks RX state and changes txdone semantics, so clients must be designed for that mode. Child DT tuple mistakes can route messages to wrong FIFOs.

Test signals: child xlate by phandle, RX FIFO draining, TX FIFO full retry, runtime/system suspend restore, and both interrupt config types.
