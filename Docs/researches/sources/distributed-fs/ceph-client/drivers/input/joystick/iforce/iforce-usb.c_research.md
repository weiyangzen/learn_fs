# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-usb.c

Purpose: USB transport for I-Force devices. It manages interrupt-in and interrupt-out URBs, vendor control queries, and bridges USB devices to the shared I-Force core.

Important APIs/types/functions: `struct iforce_usb` embeds `struct iforce` and stores USB device/interface, IRQ/out URBs, and aligned input/output buffers. `iforce_usb_probe()` validates endpoints, allocates URBs/state, fills interrupt URBs, and calls `iforce_init_device()`. `iforce_usb_xmit()`/`__iforce_usb_xmit()` drain the shared transmit ring to the interrupt-out URB. `iforce_usb_irq()` forwards inbound reports to `iforce_process_packet()`. `iforce_usb_get_id()` performs vendor control reads.

Control flow: USB probe requires endpoint 0 interrupt-in and endpoint 1 interrupt-out, initializes URBs, and registers the input device via core. Input open calls `start_io()`, which submits the interrupt-in URB. Outbound packets are submitted one at a time; completion calls `__iforce_usb_xmit()` to send the next packet. Disconnect unregisters input, frees URBs, and releases state.

State and persistence: Per-interface state stores URBs and transfer buffers; shared core state holds FF and transmit ring state. No persistent storage.

Dependencies and integration points: USB core, interrupt endpoints, vendor control messages, input/FF shared I-Force core, and static USB ID table.

Risks: Endpoint order is assumed rather than searched by direction beyond indexes 0 and 1. Inbound URB actual length should be at least one before using `data_in[0]` and `actual_length - 1`; malformed zero-length reports would be risky. Disconnect does not explicitly call transport stop before freeing URBs after input unregister, so lifetime relies on input close/unregister behavior.

Test signals: All USB IDs; endpoint order variants; control query timeout or wrong ID; URB resubmit after transient status; transmit ring wrap and multiple queued packets; disconnect during active input and FF playback.
