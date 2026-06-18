# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-serio.c

Purpose: RS232/serio transport for I-Force devices. It frames outbound packets with serial start/checksum bytes, parses inbound serial packets, and bridges the shared I-Force core to the serio subsystem.

Important APIs/types/functions: `struct iforce_serio` embeds `struct iforce` and stores serio pointer plus receive parser state, command-response buffer, and data buffer. `iforce_serio_xmit()` drains the shared transmit ring to `serio_write()` with framing/checksum. `iforce_serio_get_id()` sends query packets and waits for a matching response. `iforce_serio_irq()` is the byte-wise receive parser. `iforce_serio_connect()` opens serio and calls `iforce_init_device()`.

Control flow: Connect allocates state, assigns transport ops, opens serio, and initializes the core input device. Outbound xmit starts when the core queue transitions from empty. Inbound IRQ waits for 0x2b start, packet ID, length, data, then either completes an expected command response or passes the packet to `iforce_process_packet()`.

State and persistence: Receive parser fields (`pkt`, `id`, `len`, `idx`, checksum accumulator, expected packet) persist across bytes. Core state is embedded. No persistent storage.

Dependencies and integration points: Serio RS232 protocol `SERIO_IFORCE`, input core via shared I-Force, wait queues for command response, and `module_serio_driver`.

Risks: The receive parser accumulates `csum` but does not visibly validate an incoming checksum byte in this snapshot. `iforce_serio_stop_io()` is a TODO and does not wait for final packets. Query response timeout is one second per command. Synchronous `serio_write()` under spinlock/IRQ-save context should be evaluated with serio backend behavior.

Test signals: Byte framing with valid/invalid start, ID, length, and checksum-like bytes; query timeout and wrong-ID response; write wakeup reentry; disconnect during transmit; core packet delivery after type is initialized.
