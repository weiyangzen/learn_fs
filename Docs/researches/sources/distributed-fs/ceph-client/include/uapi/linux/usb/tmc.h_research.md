# sources/distributed-fs/ceph-client/include/uapi/linux/usb/tmc.h

Purpose: Defines the USB Test and Measurement Class userspace ioctl ABI, including USBTMC-USB488 operations.

Important APIs/types/functions: Structs include terminal-character configuration, generic control requests, and message-based read/write requests. Ioctls cover indicator pulse, clear, abort bulk in/out, clear halt, vendor/control request, get/set timeout, EOM enable, termchar config, read/write and write-result retrieval, API version, USB488 capabilities, status byte reads, REN/local/lockout/trigger/SRQ controls, message-in attributes, auto-abort, cancel and cleanup I/O. Capability bits describe trigger, simple, REN, go-to-local, local lockout, 488.2, DT1, RL1, SR1, and full SCPI support.

Control flow: Userspace controls lab instruments by configuring timeouts/termchar/EOM, sending USBTMC messages, reading responses/status bytes, and using USB488 control operations for bus-management semantics.

State and persistence behavior: Timeout, EOM, termchar, auto-abort, and pending I/O are runtime per-device/file state. Instrument command state is external device state.

Dependencies and integration points: Integrates with USBTMC kernel driver, USB control/bulk transfers, VISA/SCPI stacks, and lab automation tooling.

Risks: Long-running I/O and abort/clear races must be handled. Timeouts and termchar config affect protocol framing. Capability bits overlap historically and require careful interpretation.

Test signals: Query API/caps, perform SCPI write/read, test timeouts, termchar and EOM handling, abort/clear paths, cancel/cleanup during blocking I/O, and USB488 status/trigger controls with real or emulated instruments.
