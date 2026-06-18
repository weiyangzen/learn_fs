# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_perfcnt.h

`panfrost_perfcnt.h` is the internal declaration point for the Panfrost performance-counter subsystem. It exposes lifecycle hooks, file cleanup, ioctl handlers, and interrupt callbacks while keeping the session state private to `panfrost_perfcnt.c`.

The declared API is `panfrost_perfcnt_sample_done()`, `panfrost_perfcnt_clean_cache_done()`, `panfrost_perfcnt_init()`, `panfrost_perfcnt_fini()`, `panfrost_perfcnt_close()`, `panfrost_ioctl_perfcnt_enable()`, and `panfrost_ioctl_perfcnt_dump()`. The header includes `panfrost_device.h`; DRM file/device types arrive through driver headers.

There is no runtime control flow in the header. Device setup calls init/fini, GPU IRQ code calls the completion callbacks, the DRM ioctl table calls enable and dump, and file close calls `panfrost_perfcnt_close()` so a file-owned counter session cannot survive after the file disappears.

The header owns no persistent state, but its API defines access to `pfdev->perfcnt`, the active per-device perfcnt object allocated by the implementation. Dependencies are Panfrost device state, DRM ioctl/file infrastructure, and GPU IRQ integration. Risks are mostly lifecycle omissions: missing close or fini calls can leave counters or mappings active. Test signals are build coverage across ioctl/device/IRQ files plus runtime close while counters are enabled.
