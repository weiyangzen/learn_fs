# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-ioctl.h

## Purpose
This header declares ioctl helper functions shared by file operations, control callbacks, stream setup, and first-open initialization.

## Important APIs, Types, and Functions
It declares VBI helpers `cx18_service2vbi()`, `cx18_expand_service_set()`, and `cx18_get_service_set()`, video-device setup `cx18_set_funcs()`, and direct state-change helpers `cx18_do_s_std()`, `cx18_do_s_frequency()`, and `cx18_do_s_input()`.

## Control Flow
No executable flow is present. The declared helpers let non-ioctl paths reuse ioctl logic for initial input, standard, and frequency setup.

## State and Persistence
The implementation mutates `struct cx18` device state, VBI state, and subdevice state. The header stores no state.

## Dependencies and Integration Points
It requires V4L2 types such as `v4l2_std_id`, `v4l2_frequency`, `v4l2_sliced_vbi_format`, and `video_device`. It integrates driver initialization, file open/read, and control code with the ioctl implementation.

## Risks and Edge Cases
Because helpers bypass userspace ioctl dispatch, callers must hold the same serialization locks where required. Prototype changes affect several subsystems.

## Test Signals
Build coverage and first-open initialization are direct signals. Runtime should show initial standard/input/frequency setup producing the same state as userspace ioctls.
