# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_perfmon.c

Purpose: Implements VC4 V3D performance monitor objects for gen4-era hardware. It exposes ioctl-backed creation, destruction, lookup, and value retrieval for hardware performance counters, and programs the active V3D counter registers while jobs run.

Important APIs/types/functions: `vc4_perfmon_get()`/`put()` refcount `struct vc4_perfmon`. `vc4_perfmon_start()` writes event selectors to `V3D_PCTRS(i)`, clears counters through `V3D_PCTRC`, enables them with `V3D_PCTRE`, and records `vc4->active_perfmon`. `vc4_perfmon_stop()` optionally accumulates `V3D_PCTR(i)` into 64-bit software counters and disables hardware counting. File lifetime is managed by `vc4_perfmon_open_file()`/`close_file()` and the file-local `xarray`. Ioctls are `vc4_perfmon_create_ioctl()`, `vc4_perfmon_destroy_ioctl()`, and `vc4_perfmon_get_values_ioctl()`.

Control flow: Open initializes an allocating xarray. Create validates V3D presence, counter count, and event IDs, allocates a flexible `vc4_perfmon`, initializes event selectors/refcount, inserts it with `xa_alloc()`, and returns an ID. Lookups lock the xarray, load by ID, and take a ref. Destroy erases by ID, stops it if active, and drops the ref. Close walks and deletes all remaining perfmons.

State and persistence: Per-file monitor state is held in `vc4_file->perfmons`; device-global active state is `vc4->active_perfmon`. Counter values persist in the perfmon object until destroy/close and are accumulated across stop calls when capture is true. No state persists beyond file/device lifetime.

Dependencies and integration points: Depends on `vc4_drv.h` definitions, V3D register helpers, DRM UAPI perfmon structs, xarray, refcounting, `copy_to_user()`, and V3D job code that starts/stops perfmons. All entry points reject `vc4->gen > VC4_GEN_4`.

Risks: Active perfmon ownership is protected mainly by call ordering and WARNs; misuse could program counters while another monitor is active. Destroy of an active monitor stops without capture, losing in-flight values. Event validation relies on `VC4_PERFCNT_NUM_EVENTS`. User pointer copy failures are handled, but callers must always balance `vc4_perfmon_put()`.

Test signals: Ioctl tests should cover invalid counts, invalid events, missing V3D, create/find/destroy/get-values, close cleanup, active destroy, and gen>4 rejection. Hardware tests should confirm counter accumulation after render workloads and no counter leakage between file descriptors.
