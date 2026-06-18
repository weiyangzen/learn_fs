# sources/distributed-fs/ceph-client/drivers/input/mouse/sentelic.h

`sentelic.h` defines Sentelic FSP register addresses, bit masks, packet type encodings, hardware revisions, private driver state, and psmouse entry points.

It provides constants for device/version/revision registers, system control, OPC tags, on-pad scroll, SWC absolute reporting, page/serial registers, packet classes, button bits, and revisions A4 through E0. `struct fsp_data` stores version, revision, button mode, flags, scroll state, last register readback, and last multitouch finger. It declares `fsp_detect()` and `fsp_init()`.

These definitions drive `sentelic.c` register programming, packet dispatch, and version-specific control flow. State is per-device only. Risks are incorrect bit definitions enabling incompatible modes, and contextual aliasing of middle-button/second-finger bits. Test signals are build coverage, register programming checks, packet type decoding, and sysfs-visible state updates.
