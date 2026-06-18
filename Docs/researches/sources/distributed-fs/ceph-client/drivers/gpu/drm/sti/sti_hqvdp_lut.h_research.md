# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp_lut.h

Purpose: Supplies static legacy HVSRC scaling coefficient lookup tables for HQVDP luma/chroma horizontal and vertical scaling.

Important APIs/types: Defines `NB_COEF` as 128, shift constants for LUT classes A through F, and arrays such as `coef_lut_a_legacy`, `coef_lut_b`, `coef_lut_c_y_legacy`, `coef_lut_c_c_legacy`, through F variants. These arrays are copied into `struct sti_hqvdp_hvsrc` command fields by `sti_hqvdp_update_hvsrc()`.

Control/state: The header is data-only. HQVDP chooses tables by scale factor thresholds: stronger downscale picks later legacy LUT classes, unity uses LUT B, and upscale falls back to LUT A. Shift values are packed into horizontal/vertical shift registers alongside copied coefficients.

Dependencies/integration: Included only by `sti_hqvdp.c`. It assumes `u32` is available from prior includes in that compilation unit.

Risks/test signals: Since tables are compile-time constants, errors show as visual artifacts rather than runtime failures. Table size must match `NB_COEF` and command array fields. Test by exercising scale ratios around each threshold and comparing HQVDP debugfs LUT names and visual output.
