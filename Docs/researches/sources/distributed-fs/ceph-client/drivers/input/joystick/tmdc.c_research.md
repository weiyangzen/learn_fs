# sources/distributed-fs/ceph-client/drivers/input/joystick/tmdc.c

Purpose: implements the ThrustMaster DirectConnect/BSP gameport driver for several joystick/gamepad models, including two logical ports on one gameport.

Important APIs/types/functions: `struct tmdc` tracks the gameport, up to two `tmdc_port` instances, existence bitmask, and read/error counters. `struct tmdc_port` stores per-port input device, mode, axis/button tables, and names. Key functions are `tmdc_read_packet`, `tmdc_parse_packet`, `tmdc_poll`, `tmdc_setup_port`, `tmdc_connect`, and `tmdc_disconnect`.

Control flow: connect opens the gameport in raw mode, reads a 13-byte packet from one or both ports, records which ports exist, installs a 20 ms poll handler, and creates an input device for each present port. Packet reading disables interrupts, triggers the gameport, then samples two serial streams in parallel from upper status bits, honoring start/data/stop bits. Polling rereads both ports and compares the presence bitmask with the probed one. Per-port parsing verifies the mode byte, reports configured axes, handles model-specific hats, reports button groups, and syncs.

State and persistence: per-port model configuration is derived at probe from the packet ID/default byte and held in memory. `reads` and `bads` accumulate until disconnect. There is no persistent storage.

Dependencies and integration: depends on gameport raw polling, Linux input, delay/timing helpers, and model tables for ThrustMaster hardware. It exposes `BUS_GAMEPORT` devices and vendor `GAMEPORT_ID_VENDOR_THRUSTMASTER`.

Risks: raw timing and serial decode are sensitive to CPU/gameport timing. Unknown devices fall back to a generic model based on packet definition bits, which can overdeclare buttons. `tmdc_setup_port` formats phys with the loop variable after prior loops, which is worth checking in maintenance. Polling flags any transient packet read mismatch as bad.

Test signals: real hardware tests should cover one-port and two-port adapters, known model IDs, unknown device fallback, hat translation for M3DI/Attack Throttle, open/close polling start/stop, and bad packet counters under unplug/noise.
