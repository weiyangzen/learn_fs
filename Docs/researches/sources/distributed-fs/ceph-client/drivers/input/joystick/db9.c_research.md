# sources/distributed-fs/ceph-client/drivers/input/joystick/db9.c

Purpose: Parallel-port driver for DB9-era controllers including Atari/Amiga/Commodore/Amstrad multisystem sticks, Sega Genesis pads, Saturn pads/DPP, and Amiga CD32 pads. Device type and parport number are configured through module parameters.

Important APIs/types/functions: `struct db9_config` holds module parameter args for up to three parports. `struct db9_mode_data` describes each mode: name, button map, pad count, axis count, bidirectional requirement, and data direction. `struct db9` stores input devices, timer, parport device, mode, open count, mutex, and phys strings. `db9_timer()` contains the per-mode polling/decoding state machine. Saturn helpers (`db9_saturn_write_sub()`, `db9_saturn_read_packet()`, `db9_saturn_report()`) implement multi-device Saturn protocols.

Control flow: Module init validates that at least one configured device exists, then registers a parport driver. Attach matches configured parport number, validates mode and bidirectional requirements, claims an exclusive pardevice model, allocates up to two input devices, sets capabilities, and registers them. Open claims the parport and starts the 100 Hz timer. The timer reads or clocks the selected protocol and reschedules itself. Close stops the timer and releases the port.

State and persistence: State is global per configured port in `db9_base[]`, with open count and timer state until detach. No persistent storage. Module parameters are the only configuration source.

Dependencies and integration points: Depends on parport, input core, timer API, and module params `dev`, `dev2`, and `dev3`. Some modes require tristate/bidirectional parport support.

Risks: Protocol timing and parport electrical behavior are hardware-sensitive. Module parameter mistakes can prevent load or bind the wrong port. Several modes multiplex power/control bits and can affect attached hardware if misconfigured. Saturn multitap reporting is capped by `DB9_MAX_DEVICES`.

Test signals: Parameter validation for missing type and invalid mode; parport without tristate in bidirectional modes; Genesis 3/5/6 button sequences; Saturn digital/analog/multitap packets; CD32 clocked buttons; open/close claim/release behavior.
