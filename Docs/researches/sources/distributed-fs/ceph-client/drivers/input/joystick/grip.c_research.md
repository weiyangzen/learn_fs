# sources/distributed-fs/ceph-client/drivers/input/joystick/grip.c

Purpose: Gameport driver for Gravis/Kensington GrIP protocol devices, including GamePad Pro, Blackhawk Digital, Xterminator Digital, and Xterminator DualControl. It can manage two devices on one gameport.

Important APIs/types/functions: `struct grip` stores gameport, two input devices, detected mode per device, and counters. `grip_gpp_read_packet()` reads 24-bit GamePad Pro packets and rotates to sync pattern. `grip_xt_read_packet()` reads four CRC-protected chunks for Xterminator-style devices. `grip_poll()` decodes each supported mode into ABS/key events. `grip_connect()` probes both positions, selects mode, sets capabilities/ranges, and registers inputs.

Control flow: Connect opens raw gameport mode and probes each of two shifts for GPP or XT packets. It installs a 20 ms poll handler and creates one input per detected mode. Open/close start or stop polling. Each poll reads the packet type for each device and reports axes, hats, throttle/gas/brake, and buttons according to mode.

State and persistence: Per-port state records detected modes and read/failure counts only for module lifetime. No persistent data.

Dependencies and integration points: Raw gameport access, input core, Gravis vendor ID, mode-specific static ABS/button tables.

Risks: Packet timing and CRC sync are fragile. Device modes are fixed at connect; runtime device changes are not dynamically registered. Many magic constants map protocol bits to inputs, so regressions are likely without hardware-specific tests.

Test signals: Probe each supported mode; dual-device operation with shifts 4 and 6; CRC failure handling; ABS ranges for centered and analog axes; button table coverage; start/stop polling on open/close.
