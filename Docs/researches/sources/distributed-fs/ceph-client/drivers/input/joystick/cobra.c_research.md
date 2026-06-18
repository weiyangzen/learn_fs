# sources/distributed-fs/ceph-client/drivers/input/joystick/cobra.c

Purpose: Gameport driver for Creative Labs Blaster GamePad Cobra devices, supporting up to two gamepads on one gameport.

Important APIs/types/functions: `struct cobra` stores the gameport, up to two input devices, read/failure counters, detected device bitmask, and phys names. `cobra_read_packet()` captures a 36-bit packet per device using raw gameport edge timing and aligns packets against magic bits. `cobra_poll()` validates current device presence against the detected bitmask and reports axes/buttons. `cobra_connect()` opens raw gameport mode, probes devices, rejects unsupported extension-bit devices, sets polling, and registers inputs.

Control flow: Connect reads initial packets to identify existing pads, filters unsupported devices, installs a 20 ms poll handler, and registers one input node per detected pad. Open/close start and stop gameport polling. Polling reads both packet streams, drops samples on presence mismatch, reports digital X/Y and 12 buttons, and syncs each input.

State and persistence: Per-port state tracks initial existence mask and counters. No persistent storage; all state is freed at disconnect.

Dependencies and integration points: Integrates with raw gameport API, input core, and Creative vendor ID constants.

Risks: Packet acquisition disables interrupts and assumes 45 us strobe timing. Device existence is fixed at connect, so hotplug-like changes on the port count as bad reads rather than dynamic registration. Unknown extension-bit devices are deliberately unsupported.

Test signals: One-pad and two-pad Cobra setups; unsupported extension bit warning; bad packet injection/failure counter changes; open/close polling; X/Y and every mapped button bit.
