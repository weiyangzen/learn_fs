# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c

Purpose: supplies the DCN 3.6 register-offset initializer for the shared DCN35 DMUB hardware implementation.

Important APIs and control flow: `dmub_srv_dcn36_regs_init()` fills `dmub->regs_dcn35` from `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN35_FIELDS()` using `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.

State and persistence behavior: no independent state. It mutates the service-owned DCN35 register metadata table before callbacks use `REG_*` macros.

Dependencies and integration points: depends on `dmub_dcn36.h`, `dmub_reg.h`, and DCN360 generated headers. `dmub_srv_hw_setup()` selects this initializer for `DMUB_ASIC_DCN36`.

Risks and test signals: risks include generated field mismatch and DCN36 behavioral divergence not represented by DCN35 callbacks. Test signals include compile/link success, correct offset initialization, DMUB boot and region/window/mailbox operation on DCN36, and powered-up predicate matching firmware status bits.
