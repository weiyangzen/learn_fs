<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c

Purpose: manages register save/restore tables, including merging compatible register bit updates, applying them to MMIO, dumping them, and checking hardware or LRC readback.

Important APIs and control flow: `xe_reg_sr_init()` initializes an xarray and registers managed cleanup. `xe_reg_sr_add()` stores entries by register address, merging only compatible non-overlapping clear/set masks for the same raw register. `xe_reg_sr_apply_mmio()` forcewakes the GT, rejects VF processing by assertion, and writes each entry with `apply_one_mmio()`. Masked registers are written via upper mask bits; unmasked registers use RMW unless clearing all bits. MCR registers are accessed through `xe_gt_mcr_*`.

State and dependencies: `struct xe_reg_sr` owns an xarray of heap-allocated `xe_reg_sr_entry`. KUnit builds track `errors` on rejected entries. Integration points include RTP action processing, whitelist programming, GT reset/apply paths, default LRC lookup, and DRM printers.

Risks and test signals: conflicting entries are discarded, so table authors need tests for duplicate register actions. Readback checks should cover masked, unmasked, and MCR registers. Forcewake failure currently logs and returns without applying, which should be visible in GT logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c -->
