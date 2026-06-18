# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn31/dcn31_dccg.h

Purpose: this header declares the DCN 3.1 DCCG register surface and exported helpers used by DCN 3.1 and later DCCG variants. It defines the register list macro, the shift/mask list macro, and the public function prototypes implemented in `dcn31_dccg.c`.

Important APIs and types: `DCCG_REG_LIST_DCN31()` enumerates DPP DTO, HDMI character clock, PHY symbol clock, DP stream clock, HPO `SYMCLK32`, OTG pixel rate, DTB DTO, audio DTO, dentist DISPCLK, DSC DTO, gate-disable, memory power, and time-base registers. `DCCG_MASK_SH_LIST_DCN31(mask_sh)` enumerates fields for those registers, including array-style fields for DPP and OTG instances. Public prototypes expose create/init, DPP DTO, DP stream, HPO SE/LE, PHY, DTB/audio DTO, OTG pixel add/drop, DISPCLK mode, DSC clock, and register-state callbacks.

Control flow: the header is declarative, but it drives control flow by determining which register addresses and fields are available to `REG_UPDATE`, `REG_SET`, `REG_WAIT`, and `REG_READ` calls in the C file. Later headers include it and reuse many of its function declarations and callbacks.

State and persistence: the header owns no runtime state. Its macros populate constant `dccg_registers`, `dccg_shift`, and `dccg_mask` tables elsewhere in the display driver; those tables are then referenced by live `struct dcn_dccg` objects.

Dependencies and integration: it includes `dcn30/dcn30_dccg.h`, so it builds on common DCCG structures and enums such as `streamclk_source`, `phyd32clk_clock_source`, `physymclk_clock_source`, `dtbclk_dto_params`, and `dcn_dccg_reg_state`. It is a compatibility layer for `dcn314`, `dcn32`, `dcn35`, `dcn401`, and `dcn42` code that imports DCN 3.1 helpers.

Risks: register and field macro names must match generated ASIC headers exactly; small naming drift breaks compilation or, worse, wires a field to the wrong bit. The register list omits DCN 3.5/4.x additions, so later variants must extend rather than blindly reuse it. Several prototypes are reused across ASIC generations, so signature changes have broad blast radius.

Test signals: compile coverage should instantiate `DCCG_REG_LIST_DCN31()` and `DCCG_MASK_SH_LIST_DCN31()` in a real resource table, link all declared functions, and boot a DCN 3.1 path that exercises DPP, DP stream, HPO, PHY, DTB/audio, DSC, and diagnostic callbacks.
