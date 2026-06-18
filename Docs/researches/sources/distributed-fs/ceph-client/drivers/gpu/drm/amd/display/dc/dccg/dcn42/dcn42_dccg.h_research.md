# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h

Purpose: this header defines the DCN 4.2 DCCG field contract and public DCN 4.2 helpers. It builds on DCN 4.0.1 while adding DCN 4.2-specific OTG add/drop and FIFO resync fields and preserving five-PHY/four-LE support.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN42_COMMON(mask_sh)` maps common DCN 4.2 fields for DPP, DISPCLK frequency change and FIFO error detection, HDMI/PHY/DP stream, `SYMCLK32`, pipe DTO source, OTG add/drop pixel control, TMDS and DP DTO fields, DTBCLK_P, audio DTO, dentist, gate-disable, `SYMCLK[A-D]`, and root gates. `DCCG_MASK_SH_LIST_DCN42(mask_sh)` extends the common list with PHYE, DSC3, `SYMCLKE`, and `RESYNC_FIFO_LEVEL_ADJUST_EN`. Prototypes declare DCN 4.2 OTG add/drop, global FCG, PHY symbol clock, pixel divider, FIFO resync, and create functions.

Control flow: resource files expand the mask macros to supply the fields used by `dcn42_dccg.c` and inherited DCN35/DCN401 callbacks. The C file then chooses a mixed callback table that relies on these fields being present.

State and persistence: the header owns no mutable state. It defines static register-field metadata.

Dependencies and integration: it includes `dcn401/dcn401_dccg.h`, inheriting DCN4 signatures and common DCCG types. It must stay synchronized with generated DCN 4.2 register headers and with inherited callback field requirements.

Risks: the common and extended field lists are long and partially overlapping; duplicate fields such as PHYE root gate are easy to introduce. The header exposes four `SYMCLK32_LE` fields, while one inherited root-gating callback in the C table only handles two instances. Any mismatch between `OTG_ADD_DROP_PIXEL_CNTL` field names and generated headers breaks the DCN42-specific add/drop callbacks.

Test signals: compile a DCN 4.2 resource table, link `dccg42_create()`, and runtime-test OTG add/drop, FIFO resync, PHYE/DSC3/SYMCLKE fields, DP DTO/TMDS divider fields, and inherited DCN35/DCN401 root-gate paths.
