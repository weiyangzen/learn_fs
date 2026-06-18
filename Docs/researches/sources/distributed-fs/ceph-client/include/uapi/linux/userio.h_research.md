# sources/distributed-fs/ceph-client/include/uapi/linux/userio.h

## Purpose
Defines the userspace ABI for the `userio` virtual serio device. Applications write compact commands to `/dev/userio` to register a userspace-backed serio port, set the port type, and inject interrupt data.

## Important APIs, Types, And Constants
The exported command namespace is `enum userio_cmd_type`: `USERIO_CMD_REGISTER`, `USERIO_CMD_SET_PORT_TYPE`, and `USERIO_CMD_SEND_INTERRUPT`. `struct userio_cmd` is a two-byte packed command envelope with `type` and `data`; the header explicitly uses packed layout to keep the ABI identical across architectures. It depends only on `<linux/types.h>` for fixed-width `__u8`.

## Control Flow, State, And Persistence
The header has no executable flow, but it describes the control sequence expected by the driver: userspace sends `struct userio_cmd` records to the character device, the driver interprets `type`, and `data` carries the optional argument. Kernel-side state lives in the userio driver and serio subsystem, not in this header; persistence lasts for the device/session lifetime.

## Dependencies And Integration Points
Integrates with Linux input/serio plumbing through `/dev/userio`. Consumers must include this header when building tools that emulate serio devices or send synthetic input interrupts.

## Risks And Test Signals
ABI risk is high for struct packing and command values because userspace and kernel exchange raw bytes. Tests should cover command size (`sizeof(struct userio_cmd) == 2`), valid command dispatch, malformed command rejection, and end-to-end registration plus interrupt delivery through the serio/input stack.
