# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-main.c

Purpose: Core I-Force input device initialization and Linux force-feedback callbacks shared by USB and RS232 transports.

Important APIs/types/functions: Static tables map known vendor/product IDs to button, ABS, and FF capability arrays. `iforce_init_device()` allocates an input device, initializes wait queues/spinlocks/mutexes, queries the device, configures capabilities, creates the input FF device, and registers input. FF callbacks include `iforce_playback()`, `iforce_set_gain()`, `iforce_set_autocenter()`, `iforce_upload_effect()`, and `iforce_erase_effect()`. Open/close call transport `start_io()`/`stop_io()` and enable/disable FF.

Control flow: A transport allocates an enclosing transport struct, assigns `xport_ops`, and calls `iforce_init_device()`. Core initialization waits for query response, reads vendor/product/memory/effect counts, disables autocenter, matches a device table entry, sets input ranges, and registers callbacks. Uploads set an update bit until a status packet marks the relevant modifier memory ready.

State and persistence: `struct iforce` owns transmit ring state, effect memory resource tree, per-effect flags/resources, and synchronization primitives. This state lasts for the device lifetime. No persistent storage.

Dependencies and integration points: Exports `iforce_init_device()` for transport modules. Depends on input FF core, packet helper functions, unaligned access helpers, and transport operations from `iforce_xport_ops`.

Risks: Probe waits up to about five seconds for an ID response. Unknown devices fall back to generic joystick maps. `iforce_close()` waits for transmit completion after disabling FF; transport bugs can hang close. Duplicate or questionable device table entries should be tested against real hardware.

Test signals: USB and RS232 transport initialization; device query timeout; known and unknown VID/PID matching; FF effect upload/play/erase/status; open/close sequencing; memory size reported by packet B limiting effect resource allocation.
