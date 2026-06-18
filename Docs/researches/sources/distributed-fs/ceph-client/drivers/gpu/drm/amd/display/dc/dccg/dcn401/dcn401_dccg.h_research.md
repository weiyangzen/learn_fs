# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn401/dcn401_dccg.h

Purpose: this header defines the DCN 4.0.1 DCCG field map and public functions. It adapts the DCN 3.2/3.5 register contract to DCN4 pixel clock handling, including DP DTO integer fields, TMDS divider fields, four `SYMCLK32_LE` instances, and DCN4 gate-disable fields.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN401(mask_sh)` maps DPP clock enables, HDMI/PHY/DP stream fields, `SYMCLK32` SE/LE controls, OTG pipe DTO source/add pixel fields, `OTG#_TMDS_PIXEL_RATE_DIV`, `DPDTO#_INT`, DTBCLK_P source/enables, audio DTO fields, dentist change done, DP DTO enable fields, DSC enables and DTO params, root-gating fields, and `SYMCLK[A-D]` frontend/backend fields. Prototypes declare create/init, DPP DTO, ref frequency, DP stream clock, LE clock enable/disable, DP stream disable, DSC DTO/ref, pixel-rate divider get/set, DP DTO, `SYMCLK` SE control, DTBCLK_P source, and PHY symbol clock control.

Control flow: the C file's callback table consumes this header's fields to drive register updates. DCN4 DP pixel clocks use `set_dp_dto` rather than the older `set_dtbclk_dto`, and the header reflects that by including `DP_DTO_ENABLE` and `DPDTO#_INT` fields.

State and persistence: no state is stored in the header. It defines compile-time metadata used by live DCCG objects.

Dependencies and integration: it includes `dcn32/dcn32_dccg.h` and reuses shared enums and function signatures. DCN4 resource files must instantiate this field list and pass it into `dccg401_create()`.

Risks: `dccg401_set_src_sel()` is declared but absent from the researched implementation, so callers would fail to link unless another file provides it. The mask list includes many inherited fields that may not be used by the active DCN4 callback table, and any mismatch between field names and generated ASIC headers breaks resource construction. Four LE fields are required here where older headers define only two.

Test signals: build a DCN 4.0.1 resource table, link all prototypes, validate DP DTO and TMDS divider fields, four `SYMCLK32_LE` fields, DPP/DSC/PHY root gates, and `SYMCLK[A-D]` frontend/backend fields on real or register-simulated hardware.
