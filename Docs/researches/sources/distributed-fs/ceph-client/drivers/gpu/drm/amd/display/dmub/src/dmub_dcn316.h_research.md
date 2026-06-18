# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.h

Purpose: declares the DCN316 register table while reusing the DCN31 DMUB hardware interface.

Important APIs and control flow: exports `dmub_srv_dcn316_regs` as a `struct dmub_srv_dcn31_regs`. No functions are declared beyond the inherited DCN31 API.

State and persistence behavior: no state; this is a link-time declaration layer.

Dependencies and integration points: includes `dmub_dcn31.h`; used by `dmub_srv.c` to bind `DMUB_ASIC_DCN316`.

Risks and test signals: risks are declaration/definition mismatch and accidental omission from ASIC setup. Test signals are successful link and DCN316 service initialization selecting the expected register table.
