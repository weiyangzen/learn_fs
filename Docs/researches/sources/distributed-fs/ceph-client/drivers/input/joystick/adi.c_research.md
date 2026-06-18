# sources/distributed-fs/ceph-client/drivers/input/joystick/adi.c

Purpose: Gameport driver for Logitech ADI digital joystick and gamepad family, including WingMan, ThunderPad, CyberMan, Formula, and related devices. It probes one or two device halves on a gameport and reports decoded axes, buttons, hats, and pads through input.

Important APIs/types/functions: `struct adi_port` represents one gameport and contains two `struct adi` streams. `struct adi` stores decoded device identity, packet length, axis/button counts, cached raw packet bytes, and input metadata. `adi_read_packet()` captures edge-timed serial data under IRQ-off timing. `adi_move_bits()` merges a two-stream packet mode. `adi_id_decode()` parses the identification packet. `adi_decode()` emits ABS/key events. `adi_init_digital()` sends the reset/init trigger sequence. `adi_connect()` owns probe, input allocation, calibration, poll setup, and registration.

Control flow: Connect opens raw gameport mode, initializes digital mode, reads an ID packet, optionally merges dual streams, decodes each half, creates input devices, performs a first data read, initializes ABS center/ranges, and registers devices. Once an input node is opened, the gameport poll handler repeatedly reads and decodes packets every 20 ms.

State and persistence: State is in `struct adi_port` and the two `struct adi` instances. It tracks packet decode failures with `bad` and `reads`, stores discovered device packet layout, and records center/range calibration from initial values. There is no persistence beyond module lifetime.

Dependencies and integration points: Uses gameport raw mode, input core, module gameport driver registration, and vendor/product IDs from the parsed ADI ID. Device-specific axis/button maps are static arrays selected by ID.

Risks: Timing is fragile and depends on low-latency gameport reads with interrupts disabled. The ID parser rejects unsupported POV layouts and packet lengths, so uncommon devices may fail. Axis/button table selection is hard-coded; malformed IDs could produce incomplete capabilities. Failure counters are not exported except indirectly by behavior.

Test signals: Attach known ADI devices in single and dual-stream modes; verify ID packet length validation, hat conversion, pad handling, and 8-bit versus 10-bit axes; exercise open/close polling; inspect warnings for short or unsupported packets; compare initial calibration against input ABS ranges.
