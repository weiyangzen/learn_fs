# sources/distributed-fs/ceph-client/include/linux/videodev2.h

## Purpose
This kernel header wraps the V4L2 userspace API and supplies kernel-side dependencies needed by code including `linux/videodev2.h`.

## Important APIs, types, and functions
It includes `linux/time.h`, `linux/kernel.h`, and `uapi/linux/videodev2.h`. The API surface is the V4L2 UAPI structures, controls, formats, buffer types, and ioctls.

## Control flow, state, and persistence
There is no control flow in this wrapper. Runtime video state is handled by V4L2 core and drivers using the UAPI definitions.

## Dependencies and integration points
It integrates media/V4L2 kernel drivers with the stable userspace videodev2 ABI.

## Risks and test signals
Risks are ABI drift or including this wrapper when a stricter internal header is needed. Test signals are V4L2 UAPI compile checks and userspace ioctl compatibility tests.
