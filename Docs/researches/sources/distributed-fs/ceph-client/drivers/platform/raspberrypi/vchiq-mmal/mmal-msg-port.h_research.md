# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-port.h

Purpose: MMAL port type, capability flags, and remote port descriptor structure.

Important APIs, types, and functions: `enum mmal_port_type` identifies unknown, control, input, output, and clock ports. Capability flags describe pass-through ports, ports preferring payload allocation, and ports supporting event-based format changes. `struct mmal_port` mirrors firmware port metadata: private/name pointers, type, index, enabled state, format pointer, minimum/recommended buffer counts and sizes, alignment, selected buffer count/size, component pointer, userdata, and capabilities.

Control flow: no executable flow; this is a protocol structure exchanged with or interpreted from MMAL firmware.

State and persistence: no global state. Port descriptors become runtime component/port configuration state in MMAL consumers.

Dependencies and integration points: expects Linux fixed-width integer types from surrounding includes. Integrates with MMAL format structures and component/port enable/configuration messages.

Risks: most fields are informational/read-only, while comments state only `buffer_num`, `buffer_size`, and `userdata` are writable when setting values. Writing other fields may be ignored or rejected by firmware. Pointer-like fields are 32-bit remote references, not kernel pointers. Capability flags control buffer allocation strategy and format-change handling; misinterpreting them can cause buffer underruns or failed reconfiguration.

Test signals: port query/set round trips with firmware, layout checks, tests that only writable fields are changed during set operations, and format-change event handling on ports advertising the capability.
