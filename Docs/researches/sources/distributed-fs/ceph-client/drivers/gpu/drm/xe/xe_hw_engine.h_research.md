# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.h

Purpose: public hardware-engine API and default scheduler property bounds.

Important APIs/constants: Kconfig-backed defaults for job timeout, timeslice, and preempt timeout min/max/defaults; engine init, IRQ, ring enable, per-class mask, snapshot, print, LRC state setup, reservation check, lookup, class-to-string, timestamp, forcewake-domain, and engine-relative MMIO helpers. `xe_hw_engine_is_valid` checks `hwe->name`.

Control flow/state: GT init calls early/full init; IRQ code calls `xe_hw_engine_handle_irq`; exec queue and diagnostics code call lookup and snapshots; register programming code uses MMIO helpers.

Dependencies/integration: includes engine types and uses `struct xe_gt`, `struct xe_device`, `struct xe_exec_queue`, DRM printer, and UAPI class-instance structs.

Risks/test signals: default range macros must align with sysfs validation. Tests should verify invalid engines have no name, lookups reject out-of-range UAPI classes, and forcewake assertions catch bad MMIO access in debug builds.
