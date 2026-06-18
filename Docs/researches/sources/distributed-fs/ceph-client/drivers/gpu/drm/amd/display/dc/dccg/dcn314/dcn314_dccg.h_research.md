# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn314/dcn314_dccg.h

Purpose: this header defines the DCN 3.1.4 DCCG register and field macros and declares the DCN 3.1.4 creation and DP stream clock entry points.

Important APIs and types: `DCCG_REG_LIST_DCN314()` extends the DCN 3.1 register set with `DSCCLK3_DTO_PARAM`, `OTG_PIXEL_RATE_DIV`, and `DTBCLK_P_CNTL`. `DCCG_MASK_SH_LIST_DCN314_COMMON(mask_sh)` defines shared field mappings for DPP DTO DB enable, DP stream clock enable/source, `SYMCLK32`, OTG DTO, pixel dividers, DTBCLK_P, audio DTO source, dentist controls, DSC DTO parameters, and root-gating fields. `DCCG_MASK_SH_LIST_DCN314(mask_sh)` adds DPP DTO enable, PHY force fields, HDMI stream DTO force disable, DSC DTO enable, PHY gate-disable, and dentist read/write divider fields. It declares `dccg314_create()` and `dccg314_set_dpstreamclk()`.

Control flow: the macro tables are consumed by resource files to populate register/shift/mask structures used by `dcn314_dccg.c`. The C implementation then selects local or inherited callbacks based on the `dccg314_funcs` table.

State and persistence: no runtime state is owned here. The macros produce static register metadata; live state remains in hardware registers and `struct dccg`.

Dependencies and integration: the header includes `dcn31/dcn31_dccg.h` and redefines `DCCG_SFII` for instance field expansion. It is part of the resource-construction contract for DCN 3.1.4 display hardware and depends on generated register-field names matching the macro concatenations.

Risks: the mask list contains a duplicate `OTG3_PIXEL_RATE_DIVK2` entry; while likely harmless in generated initializer ordering, it is a maintenance hazard. Field-list omissions will surface as callback failures when the shared DCN 3.1 functions access registers that the DCN 3.1.4 tables did not define. Because this header pulls in DCN 3.1 declarations, incompatible enum or callback changes propagate here.

Test signals: compile a DCN 3.1.4 resource table using the register and mask macros, verify the resulting DCCG object can call `dccg314_set_dpstreamclk()`, and boot-test pixel divider, DTBCLK_P, DSC3, and dentist divider fields.
