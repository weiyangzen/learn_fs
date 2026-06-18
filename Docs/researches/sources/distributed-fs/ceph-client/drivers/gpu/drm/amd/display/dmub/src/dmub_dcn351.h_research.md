# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.h

Purpose: declares the DCN351 register initialization hook and reuses the DCN35 DMUB API.

Important APIs and control flow: exports `dmub_srv_dcn351_regs_init(struct dmub_srv *dmub, struct dc_context *ctx)`. No other behavior is declared.

State and persistence behavior: no state; it identifies the per-revision initializer used to populate service-owned register metadata.

Dependencies and integration points: includes `dmub_dcn35.h`; selected by `dmub_srv_hw_setup()` for DCN351.

Risks and test signals: risks are declaration drift and omission from ASIC setup. Test signals are clean link and `init_reg_offsets` dispatch for DCN351.
