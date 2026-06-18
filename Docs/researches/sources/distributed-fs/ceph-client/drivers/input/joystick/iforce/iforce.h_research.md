# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce.h

Purpose: Shared definitions for I-Force core, FF effect memory tracking, transport operations, command IDs, transmit ring helpers, and exported function prototypes.

Important APIs/types/functions: `struct iforce_core_effect` tracks two modifier resource chunks and effect flags. `struct iforce_device` maps VID/PID to input capability arrays. `struct iforce_xport_ops` abstracts transport operations: `xmit`, `get_id`, `start_io`, and `stop_io`. `struct iforce` stores input device, device type, transport ops, transmit ring, wait queue, on-device memory resource, per-effect state, and memory mutex. Command macros define FF packet IDs and `XMIT_SIZE`/`XMIT_INC` manage the circular buffer.

Control flow: Transport modules embed `struct iforce`, assign `xport_ops`, and call `iforce_init_device()`. Core FF and packet code use the shared fields and macros to queue commands, parse responses, and manage effect resources.

State and persistence: Defines runtime state containers only. Effect flags persist for the lifetime of each uploaded input FF effect and device state. No disk persistence.

Dependencies and integration points: Linux input, module, spinlock, circular buffer, mutex, wait queue, and resource APIs. Exposes core functions to transport modules and references transport driver symbols.

Risks: The transmit buffer is fixed at 256 bytes; callers must manage backpressure. `XMIT_INC` macro mutates its argument and assumes power-of-two buffer size. The high-byte fixup macro and time scaling are protocol-specific and easy to misuse.

Test signals: Compile inclusion from all I-Force source files; ring wrap behavior with `XMIT_INC`; effect flag lifecycle; transport ops completeness for USB and serio.
