# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.h

Purpose: declares the GT throttling sysfs setup and reason-mask read API.

Important APIs: `xe_gt_throttle_init` creates throttling sysfs attributes, and `xe_gt_throttle_get_limit_reasons` returns the current masked throttle reason bits from hardware.

Control flow: GT frequency sysfs setup calls init; power/frequency reporting code can call the reason getter directly.

State and persistence: no state in the header; implementation reads MMIO on demand.

Dependencies and integration: forward-declares `struct xe_gt` and includes Linux types.

Risks: callers of `get_limit_reasons` may trigger runtime PM and MMIO reads, so it should not be used from atomic contexts.

Test signals: compile integration with GT frequency and GuC power code, plus sysfs group creation tests.
