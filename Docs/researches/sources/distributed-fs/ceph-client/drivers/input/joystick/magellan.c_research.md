# sources/distributed-fs/ceph-client/drivers/input/joystick/magellan.c

Purpose: Serio RS232 driver for LogiCad3D Magellan and SpaceMouse six-degree-of-freedom controllers.

Important APIs/types/functions: `struct magellan` stores input device, current packet index, packet data buffer, and phys string. `magellan_interrupt()` accumulates bytes until carriage return. `magellan_process_packet()` decodes axis (`d`) and button (`k`) packets. `magellan_crunch_nibbles()` validates and strips encoded nibbles. `magellan_connect()` allocates input and opens serio.

Control flow: Connect creates an input device with six ABS axes and nine buttons, opens the serio port, and registers the input. The interrupt handler buffers serial bytes. On `\r`, it dispatches packet processing and resets the index. Axis packets must be 25 bytes and produce six signed 16-bit-ish values offset by 32768. Button packets must be 4 bytes and produce a 9-bit mask.

State and persistence: Packet assembly state persists across serial interrupts. No persistent storage.

Dependencies and integration points: Serio protocol `SERIO_MAGELLAN`, input core, RS232 devices configured externally.

Risks: Oversized packets are truncated by ignoring extra bytes until `\r`. Invalid nibble encoding silently drops packets. Axis range is configured as -360..360 but decoded values are much wider before input core filtering/clamping behavior, which should be verified.

Test signals: Valid `d` and `k` packets; malformed nibble bytes; packets without carriage return; disconnect during partial packet; ABS and key event ranges through evtest.
