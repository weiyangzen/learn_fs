# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn42/dcn42_hubp.h

Purpose: declares DCN 4.2 HUBP additions over the DCN 3.5 base, focused on 3D LUT fast-load fields with DCN4.2 naming and MPC-width support.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN42()` composes `HUBP_MASK_SH_LIST_DCN35()` and adds `_3DLUT_FL_CONFIG`, `_3DLUT_FL_BIAS_SCALE`, `HUBP_3DLUT_CONTROL`, address, and DLG fields. DCN4.2-specific fields include `HUBP_3DLUT_MPC_WIDTH` and `HUBP_3DLUT_CROSSBAR_SEL_R/G/B`. The header forward-declares `struct dml2_display_rq_regs` and declares construction, 3D LUT crossbar/config programming, state readback, requestor programming, and setup.

Control flow: no runtime control flow exists here. The definitions allow DCN4.2 resource code to build shift/mask tables and call DCN4.2 setup/requestor/readback paths while reusing DCN3.5 and DCN4.0.1 helpers.

State and persistence: the declared fields persist 3D LUT fast-load enable, done, addressing, width, MPC width, TMZ, crossbar, address, DLG cadence, bias, scale, format, and mode. Requestor and setup prototypes expose DML2-driven timing state programming.

Dependencies and integration points: includes `dcn35_hubp.h`, but the implementation also includes `dcn401_hubp.h` to reuse DCN4 helper implementations. This header is part of the DCN4.2 color management and DML2 integration surface.

Risks and test signals: relying on the DCN3.5 mask base while adding DCN4.2 fields can hide differences from DCN4.0.1. Field renames from `CROSSBAR_SELECT_*` to `CROSSBAR_SEL_*` require matching generated registers. Signals include DCN4.2 register table builds, 3D LUT fast-load readback, DML2 setup builds, and compiler diagnostics for prototype mismatches.
