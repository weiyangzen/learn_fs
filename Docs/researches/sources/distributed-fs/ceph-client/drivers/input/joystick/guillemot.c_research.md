# sources/distributed-fs/ceph-client/drivers/input/joystick/guillemot.c

Purpose: Gameport driver for Guillemot digital interface protocol joysticks, currently table-driven for a Guillemot Pad.

Important APIs/types/functions: `struct guillemot_type` describes supported ID, ABS map, button map, hat presence, and name. `struct guillemot` stores gameport, input device, counters, selected type, packet length, and phys string. `guillemot_read_packet()` reads a 17-byte bitstream with start/strobe timeouts. `guillemot_poll()` validates packet delimiters `0x55` and `0xaa`, reports axes, hat, buttons, and syncs. `guillemot_connect()` probes ID bytes and registers the input.

Control flow: Connect opens raw gameport mode, reads one full packet, validates framing, matches `data[11]` against supported type table, installs a 20 ms poll handler, sets capabilities, and registers input. Polling repeats the packet read and reports events on valid frames.

State and persistence: Per-device state stores selected type and counters only. No persistent storage.

Dependencies and integration points: Raw gameport API, input core, Guillemot vendor ID, static type table.

Risks: Only one ID is supported. Timing is IRQ-off and sensitive to gameport speed. Disconnect log appears to print `reads`/`bads` in a misleading order in the message text. Invalid frames still call `input_sync()` without new events.

Test signals: Valid pad packet including delimiter bytes and ID; unknown ID warning; packet timeout path and bad counter; ABS range 0..255 and hat -1..1; open/close polling.
