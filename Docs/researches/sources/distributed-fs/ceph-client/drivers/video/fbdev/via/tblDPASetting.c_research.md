<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c

Purpose: Static DPA/skew tuning tables for VIA graphics output pads on VT3324, VT3327, and VT3364 chipsets. These values are selected by pixel-clock range when programming VT1636 LVDS paths and graphics DVP/DFP driving strength.

Important APIs/types/functions: Defines `GFX_DPA_SETTING_TBL_VT3324[6]`, `GFX_DPA_SETTING_TBL_VT3327[]`, and `GFX_DPA_SETTING_TBL_VT3364[6]`. Each entry is a `struct GFX_DPA_SETTING` keyed by `DPA_CLK_RANGE_*` and stores DVP0 skew, DVP0 data/clock driving, DVP1 skew/driving, DFP-high, DFP-low, and reserved/extra fields matching `viafb_set_dpa_gfx()` expectations.

Control flow and state: No executable flow. `vt1636.c` computes a clock-range index and passes one selected table row to `viafb_set_dpa_gfx()` through the LCD skew patch path. The tables are persistent read-only data.

Dependencies and integration points: Includes `global.h` for `struct GFX_DPA_SETTING` and register constants. Integrated by `tblDPASetting.h` and `vt1636.c`. Risks are undocumented magic values, comments with apparent typos around 150 MHz ranges, no compile-time assertion that all tables have six entries, and per-chip values that can visibly break signal integrity if edited. Test signals are DVP0/DVP1/DFP display stability at pixel clocks below 30 MHz through above 150 MHz on affected chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.c -->
