# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/ep0.c

Purpose: endpoint-zero control transfer engine for both the virtual hub itself and each downstream virtual gadget device.

Important APIs, types, and functions: `ast_vhub_init_ep0` initializes EP0 objects and maps their control/status, setup, buffer, and DMA addresses. `ast_vhub_ep0_handle_setup` reads setup packets, routes standard/class hub requests or standard device requests, forwards driver-owned requests to gadget `setup`, and stalls or completes as needed. `ast_vhub_reply` and `__ast_vhub_simple_reply` send internal replies. `ast_vhub_ep0_handle_ack`, `ast_vhub_ep0_do_send`, `ast_vhub_ep0_do_receive`, and `ast_vhub_ep0_rx_prime` implement data/status phase progression. EP ops `ast_vhub_ep0_queue` and `ast_vhub_ep0_dequeue` connect gadget requests to the EP0 state machine. `ast_vhub_reset_ep0` nukes queued work and returns to token state.

Control flow: a SETUP IRQ copies the setup packet, recovers from unexpected states by nuking queued requests, sets data direction, and dispatches to hub/device standard handlers or the gadget driver. Internal replies queue through the same EP0 ops after dropping the lock. IN transfers send maxpacket-sized chunks from request buffers or the EP buffer; OUT transfers prime RX, copy received data into the request, and complete on short packet or expected length. ACK IRQs advance data or status phases and return to token state unless a stall is needed.

State and persistence: EP0 state is in `ep->ep0.state`, `dir_in`, internal request object, queue, and per-EP coherent buffer. Only one EP0 request is allowed at a time. State is protected by `vhub->lock`; completion can drop the lock to call gadget callbacks. No persistent data exists.

Dependencies and integration points: depends on internal hub request handlers, device standard request handler, gadget driver `setup`, hardware EP0 control/status registers, DMA buffer workaround helper, and shared request completion from `core.c`.

Risks: control transfers are state-machine sensitive. Wrong ACK direction, missing requests, stale queued requests, or setup packets arriving during non-token states can cause stalls. The code includes a workaround for hardware returning wrong OUT lengths. `ast_vhub_ep0_queue` rejects requests without completion callbacks unless internal, and rejects queues in token/stall states.

Test signals: enumerate the root hub and downstream gadgets, exercise standard device and hub requests, class hub requests, IN/OUT control transfers with zero, short, exact, and multi-packet data, force stalls and dequeues, send setup during pending data, reset ports, and run with debug logs to verify state transitions token/data/status/stall.
