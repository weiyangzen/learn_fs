# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.c

Purpose: exposes GT hardware/firmware frequency throttling reasons under `freq0/throttle/` sysfs.

Important APIs and functions: `xe_gt_throttle_get_limit_reasons` reads platform-specific perf limit reason registers with runtime PM held. `xe_gt_throttle_init` creates the throttle sysfs group and registers cleanup. Internal sysfs show helpers expose boolean `status`, individual `reason_*` files, and aggregate `reasons`.

Control flow: register selection uses media vs non-media GT and Crescent Island vs default masks. `reason_show` checks a single mask; `reasons_show` reads the full reason mask once, iterates the active platform group, and emits names for all active reason attributes or `none`.

State and persistence: no cached state; every read samples MMIO. Sysfs group lifetime follows `gt->freq` and DRM device-managed cleanup.

Dependencies and integration: depends on GT regs, MMIO, platform types, runtime PM, GT sysfs/frequency kobjects, and callers such as GuC power/frequency reporting.

Risks: aggregate `reasons` depends on attribute names starting with `reason_`; `status` uses `U32_MAX` as a special mask but is excluded from aggregate names. Unknown bits trigger a one-time DRM warning and return `none`, which can hide new hardware reason bits until masks are updated.

Test signals: sysfs reads on Crescent Island and default platforms, media/non-media register selection, runtime PM behavior, unknown bit warning, and cleanup on GT removal.
