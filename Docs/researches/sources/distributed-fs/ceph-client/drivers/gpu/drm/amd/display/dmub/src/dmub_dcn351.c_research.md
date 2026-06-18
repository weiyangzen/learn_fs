# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c

Purpose: supplies the DCN 3.5.1 register-offset initializer for the otherwise shared DCN35 DMUB hardware implementation.

Important APIs and control flow: `dmub_srv_dcn351_regs_init()` fills `dmub->regs_dcn35` by expanding `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN35_FIELDS()` with `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`. It uses dynamic `ctx->dcn_reg_offsets` segment bases.

State and persistence behavior: no independent state. It mutates the service-owned DCN35 register descriptor during initialization.

Dependencies and integration points: depends on `dmub_dcn351.h`, `dmub_reg.h`, and DCN351 generated headers. `dmub_srv_hw_setup()` selects this init function for `DMUB_ASIC_DCN351` while using the DCN35 callback set.

Risks and test signals: risks include missing fields in DCN351 generated headers and use before `init_reg_offsets` runs. Test signals include successful DCN351 build, initialized offsets differing from DCN35 where expected, and normal DCN35 boot/mailbox/pre-OS behavior on DCN351.
