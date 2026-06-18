# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.c

## Purpose
Creates MSM DRM debugfs files for GPU snapshots, KMS snapshots, framebuffer/GEM/MM state, shrinker control, fault injection, and GPU devfreq/hangcheck knobs.

## Important APIs, types, and functions
- `msm_debugfs_init()` registers common, GPU, KMS, shrinker, and fault-injection files.
- `msm_debugfs_late_init()` registers rd/perf debugfs on primary/render minors after DRM registration.
- GPU snapshot path: `msm_gpu_open()`, `msm_gpu_show()`, `msm_gpu_release()`.
- KMS snapshot path: `msm_kms_open()`, `msm_kms_show()`, `msm_kms_release()`.
- Debug entries include `gem`, `mm`, `fb`, `gpu`, `kms`, `shrink`, `stall_reenable_time_us`, and devfreq knobs.

## Control flow
Opening `gpu` locks the GPU, runtime-resumes it, initializes hardware, captures GPU state through GPU callbacks, and later prints/releases that snapshot. Opening `kms` locks `kms->dump_mutex`, captures a display snapshot, and prints it. `gem` walks the global object list under `obj_lock`; `fb` walks fbdev and framebuffer lists; `shrink` invokes the GEM shrinker and stores the last freed count. Late init installs rd/perf files only when a GPU platform device exists.

## State and persistence
Persistent debug state includes `last_shrink_freed` and writable driver fields such as hangcheck period, error IRQ disable, devfreq thresholds, and idle clamp. Snapshot objects are allocated per open and freed at release.

## Dependencies and integration points
Depends on CONFIG_DEBUG_FS, DRM debugfs helpers, fb helper, GPU/KMS callback interfaces, display snapshot code, GEM shrinker, fault injection attributes, and rd/perf debugfs modules.

## Risks
Debugfs reads can resume and initialize GPU hardware, so they are not passive. Snapshot capture and release must hold GPU/KMS locks correctly. Writable debug knobs are test-oriented and can alter hang detection or devfreq behavior. `last_shrink_freed` is global rather than per-device.

## Test signals
Check debugfs file creation on primary/render nodes, GPU and KMS snapshot reads, `gem`/`mm`/`fb` output, shrink write/read behavior, fault injection files, and lockdep under concurrent debugfs access/removal.
