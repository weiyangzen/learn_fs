# sources/distributed-fs/ceph-client/drivers/input/joystick/gf2k.c

Purpose: Gameport driver for Genius Flight 2000 family digital joysticks, with support tables for several Genius device IDs.

Important APIs/types/functions: `struct gf2k` stores gameport, input device, counters, detected ID/packet length, and phys string. `gf2k_trigger_seq()` sends reset/digital trigger timing sequences. `gf2k_read_packet()` captures triplet-coded packet bits. `gf2k_get_bits()` extracts fields from the triplet buffer. `gf2k_read()` maps decoded axes, hats, and buttons to input events. `gf2k_connect()` probes, initializes, identifies, calibrates ranges, and registers the input device.

Control flow: Connect opens raw gameport mode, sends reset and digital sequences, reads an initial packet, decodes ID, checks support tables, installs 20 ms polling, performs an initial read to set ABS ranges, and registers input. Polling reads a packet of the expected length and either increments bads or reports decoded state.

State and persistence: Per-device state includes detected ID and counters. Axis ranges are calibrated from initial sampled values. No persistence.

Dependencies and integration points: Uses raw gameport timing, input core, static device tables, and Genius gameport vendor ID.

Risks: The visible tree forces `gf2k->id = 6` when `RESET_WORKS` is not defined, which can misidentify other devices. Timing sequences disable interrupts and rely on microsecond behavior. Supported-device tables contain zeros for unimplemented IDs, so detection may intentionally reject hardware.

Test signals: Known F-23/Flight2000 device path; packet read lengths; hat direction conversion; forced-ID behavior with other hardware; initial calibration; disconnect cleanup and failure counter behavior.
