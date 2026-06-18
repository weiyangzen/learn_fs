# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dfp.c

## Purpose
`dfp.c` implements digital flat-panel encoder support for legacy Nouveau hardware, covering TMDS and LVDS outputs, flat-panel timing generator control, head binding, scaling, dithering, LVDS power scripts, external TMDS transmitters, and encoder creation.

## Important APIs, Types, And Functions
Important helpers are `nv04_dfp_get_bound_head`, `nv04_dfp_bind_head`, `nv04_dfp_disable`, `nv04_dfp_update_fp_control`, `get_tmds_slave`, `nv04_dfp_mode_fixup`, `nv04_dfp_prepare_sel_clk`, `nv04_dfp_prepare`, `nv04_dfp_mode_set`, `nv04_dfp_commit`, `nv04_lvds_dpms`, `nv04_tmds_dpms`, save/restore/destroy, `nv04_tmds_slave_init`, and `nv04_dfp_create`. It defines `FP_TG_CONTROL_ON/OFF` masks and `is_fpc_off()`.

## Control Flow, State, And Integration
Mode fixup chooses native panel timing when scaling is enabled and the requested mode fits inside the native mode. Prepare powers the encoder down, updates `SEL_CLK`, and routes the digital output to the intended CRTC/head. Mode set fills flat-panel horizontal/vertical register arrays, computes FP control flags for sync polarity, scaling mode, interface width, dual-link, and panel timing; it computes aspect scaling using fixed-point arithmetic and programs dither state based on connector properties and framebuffer depth. Commit runs TMDS or LVDS BIOS scripts, refreshes FP control state, programs DAC test control, initializes external I2C transmitters if needed, then DPMSes on. LVDS DPMS may run panel on/off scripts and update platform-specific backlight bits.

## State, Dependencies, Risks, And Tests
State includes `mode_reg` flat-panel registers, saved FP control/dither/SEL_CLK, CRTC `fp_users`, encoder `last_dpms`, DCB output metadata, connector native mode/scaling/dithering, and external I2C encoder state. Dependencies include BIOS TMDS/LVDS scripts, DCB tables, NVKM I2C, optional sil164 helper, low-level RAMDAC/VGA helpers, and connector properties. Risks include many undocumented chipset-specific bits, dual-link detection from EDID or BIOS tables, external transmitter ambiguity on shared I2C addresses, scaling math edge cases, and LVDS power sequencing. Test signals are LVDS/TMDS modesets, native/center/aspect/full scaling, dithering properties, dual-link high-clock panels, DPMS/backlight behavior, external sil164 output, and suspend/restore.
