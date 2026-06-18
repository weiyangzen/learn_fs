# sources/distributed-fs/ceph-client/drivers/input/joystick/stinger.c

Purpose: supports the Gravis Stinger RS-232 gamepad by decoding fixed four-byte packets into two axes and ten buttons.

Important APIs/types/functions: `struct stinger` stores the input device, packet index, four-byte data buffer, and phys path. `stinger_interrupt` buffers incoming bytes. `stinger_process_packet` reports buttons and ABS_X/ABS_Y. `stinger_connect` and `stinger_disconnect` manage serio and input lifecycle.

Control flow: connect allocates state/input, assigns `BUS_RS232` IDs, declares `EV_KEY` and `EV_ABS`, sets key bits for A/B/C/X/Y/Z/TL/TR/START/SELECT, sets -64..64 axis ranges, opens serio, and registers input. The interrupt handler appends bytes until four are received, then decodes and resets the index. Decode pulls button bits from bytes 0 and 3 and combines high sign bits with bytes 1 and 2 for axes.

State and persistence: only the current four-byte packet index and data buffer persist between interrupts. No hardware configuration is written and no data persists beyond device removal.

Dependencies and integration: uses `SERIO_STINGER`, `module_serio_driver`, and standard Linux input key/axis reporting.

Risks: there is no explicit framing or checksum, so a dropped byte can desynchronize all following four-byte windows until external serio framing recovers. The driver assumes every four bytes are a complete packet. Allocation uses plain `kmalloc_obj`, so all fields initialized before use matter.

Test signals: validate packet-to-event mapping using synthetic four-byte streams, test lost-byte behavior, check axis bounds and flat value with `evtest`, and verify serio open/register failure unwinds cleanly.
