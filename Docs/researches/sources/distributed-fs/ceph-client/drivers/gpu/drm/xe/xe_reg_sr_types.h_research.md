<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h

Purpose: defines compact storage for register save/restore entries and tables.

Important types: `struct xe_reg_sr_entry` stores register descriptor, `clr_bits`, `set_bits`, and `read_mask`; `struct xe_reg_sr` stores an xarray keyed by register address plus a human-readable name and optional KUnit error counter.

State and integration: entries are built by RTP/whitelist code and consumed by MMIO apply/readback and LRC validation paths. The bit masks encode both RMW behavior and readback expectations.

Risks and test signals: table authors must keep `set_bits` within intended clear/read masks, especially for masked registers. KUnit should assert conflict handling and error counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h -->
