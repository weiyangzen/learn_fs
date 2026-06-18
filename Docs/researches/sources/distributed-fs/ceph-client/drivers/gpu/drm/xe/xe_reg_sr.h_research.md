<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h

Purpose: declares register save/restore lifecycle, mutation, apply, dump, and validation APIs.

Important APIs: `xe_reg_sr_init()`, `xe_reg_sr_add()`, `xe_reg_sr_apply_mmio()`, `xe_reg_sr_apply_whitelist()`, `xe_reg_sr_dump()`, `xe_reg_sr_readback_check()`, and `xe_reg_sr_lrc_check()`.

Dependencies and risks: forward declares GT, device, hardware engine, printer, and SR types. Callers must initialize `struct xe_reg_sr` before passing it to RTP or whitelist processing and must not assume rejected conflicting entries are retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h -->
