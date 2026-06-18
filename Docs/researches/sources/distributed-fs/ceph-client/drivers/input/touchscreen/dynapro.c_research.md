# sources/distributed-fs/ceph-client/drivers/input/touchscreen/dynapro.c

Purpose: `dynapro.c` is a serio driver for Dynapro RS-232 touchscreen packets, typically attached through `inputattach`. It decodes a three-byte packet into single-touch X/Y and touch state.

Important APIs, types, and functions: `struct dynapro` contains the input device, serio port, packet index, three-byte data buffer, and physical path. `dynapro_interrupt()` buffers bytes from serio, accepts frames whose first byte has the `0x80` response-begin bit, and calls `dynapro_process_data()`. `dynapro_process_data()` waits for three bytes, decodes 10-bit X/Y from packed high bits in byte 0 and low bytes in bytes 1/2, reports `BTN_TOUCH`, and syncs. `dynapro_connect()`/`dynapro_disconnect()` manage input and serio lifecycle.

Control flow: the serio ID table matches `SERIO_RS232` plus `SERIO_DYNAPRO`. Connect allocates state and input, sets ABS_X/ABS_Y ranges 0..0x3ff, opens the serio port, and registers input. Each interrupt stores a byte at `idx`, verifies the first buffered byte has the start bit, and resets `idx` after a complete report.

State and persistence: all state is transient packet assembly and input device registration. No hardware configuration, persistent storage, or PM behavior exists.

Dependencies and integration points: it depends on the serio subsystem, input single-touch ABS/key APIs, and external line-discipline or inputattach configuration to create a matching serio device.

Risks: synchronization is minimal: a bad first byte is logged but `idx` is not reset unless `dynapro_process_data()` completes, so repeated garbage could keep overwriting the same first byte path. The touch bit is reported as the raw masked value rather than normalized boolean, which input handles as nonzero but is less explicit. There is no checksum.

Test signals: feed aligned and misaligned three-byte packets, verify coordinate extraction, touch/release reports, serio open/register failure unwinds, and disconnect lifetime with `input_get_device()`/`input_put_device()`.
