# sources/distributed-fs/ceph-client/drivers/input/joystick/interact.c

Purpose: Gameport driver for InterAct digital joystick/gamepad devices, specifically HammerHead/FX and ProPad 8 Digital.

Important APIs/types/functions: `struct interact_type` defines ID, ABS/button maps, product name, packet length, and count of 8-bit axes. `struct interact` stores gameport, input, counters, selected type, packet length, and phys string. `interact_read_packet()` reads up to 32 bits across three data streams from raw gameport edges. `interact_poll()` maps packets by type into axes and buttons. `interact_connect()` probes a signature and ID, configures input, and registers.

Control flow: Connect opens raw mode, reads a 64-bit probe window, validates header bytes, finds type by `data[2] >> 16`, installs a 20 ms poll handler, and registers input. Polling reads the type-specific length and decodes either analog-like HammerHead/FX axes plus hat/buttons or ProPad digital axes/buttons.

State and persistence: Per-device type and counters exist for module lifetime. No persistence.

Dependencies and integration points: Raw gameport API, input core, InterAct vendor ID constants, static type table.

Risks: Only two device IDs are accepted. Probe and polling depend on tight IRQ-off timing. `interact_read_packet()` stores parallel bit streams in three u32s; changes to packet length or stream interpretation can silently remap controls.

Test signals: Known HHFX and PP8D devices; unknown ID warning; short read bad counter; ABS ranges for 8-bit and digital axes; all mapped buttons; open/close polling.
