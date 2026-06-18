# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.h

Purpose: declares the DCN36 register initialization hook while inheriting the DCN35 DMUB API.

Important APIs and control flow: exports `dmub_srv_dcn36_regs_init()`. The function is called by the service core during register-offset setup for DCN36.

State and persistence behavior: no state; it only exposes an initializer for service-owned register metadata.

Dependencies and integration points: includes `dmub_dcn35.h`; used by `dmub_srv.c` for `DMUB_ASIC_DCN36`.

Risks and test signals: risks are declaration drift and missed dispatch. Test signals include build/link coverage and observed `init_reg_offsets` call on DCN36.
