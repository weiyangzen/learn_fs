# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-common.h

## Purpose
Provides V4L2 definitions shared by full video nodes and sub-device nodes. It centralizes selection target/flag values and EDID exchange layout.

## Important APIs, Types, And Constants
Selection targets cover current/default/bounds crop rectangles, native frame size, current/default/bounds compose rectangles, and padded compose area. Selection flags express greater-or-equal, less-or-equal, and keep-existing-configuration constraints. `struct v4l2_edid` carries a pad, start block, block count, reserved words, and an EDID pointer. Userspace-only backward compatibility aliases map obsolete subdev names to the common selection constants.

## Control Flow, State, And Persistence
No code runs in the header. The constants steer ioctl handlers such as selection and EDID get/set operations. Active crop/compose/EDID state belongs to media drivers and hardware; try-state may be held transiently during format negotiation.

## Dependencies And Integration Points
Depends on `<linux/types.h>`. It is intended to be included indirectly through `videodev2.h` or `v4l2-subdev.h`, and it is consumed by V4L2 applications, bridge drivers, camera sensor drivers, and display receiver/transmitter drivers.

## Risks And Test Signals
Risks center on selection target mismatch between video-node and subdev paths and unsafe EDID pointer/length handling. Tests should query/set each selection target, verify `KEEP_CONFIG` behavior, exercise EDID block ranges, and compile userspace with deprecated aliases.
