# sources/distributed-fs/ceph-client/drivers/input/mouse/focaltech.h

`focaltech.h` exposes `focaltech_detect()` and, when `CONFIG_MOUSE_PS2_FOCALTECH` is enabled, `focaltech_init()` to psmouse. If full support is disabled, `focaltech_init()` is an inline `-ENOSYS` stub while detection remains available.

This split is important control-flow policy: `psmouse-base.c` can detect FocalTech early using safe PNP matching, restrict further probing, and fall back cleanly even without the full driver. The header defines no runtime state; all private state is in `focaltech.c`.

Integration is through Kconfig and `struct psmouse`. Risks are callers assuming detection implies initialization support. Test signals are build coverage with support enabled/disabled and clean fallback when the initializer is stubbed.
