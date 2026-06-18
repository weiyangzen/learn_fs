# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_print.h

## Purpose

This header provides HuC-prefixed logging macros layered on top of GT logging.

## APIs, Dependencies, Risks, And Test Signals

`huc_printk()` expands to `gt_<level>(huc_to_gt(_huc), "HuC: " ...)`, and convenience macros cover error, warning, notice, info, debug, and probe-error levels. It depends on `intel_gt.h` and `intel_gt_print.h`, especially `huc_to_gt()`. The main risk is macro argument side effects because `_huc` is evaluated inside another macro; existing usage passes simple pointers. Test signals are compile-time macro use and boot/auth logs consistently prefixed with `HuC:`.
