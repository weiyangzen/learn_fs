# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.c

## Purpose
Initializes and controls the Meson Video Input Unit OSD path, including OSD color-space conversion matrices, EOTF/OETF LUTs, OSD1 reset recovery, and AFBC path selection for GXM/G12A-class SoCs.

## Important APIs, types, and functions
- Internal enums `viu_matrix_sel_e` and `viu_lut_sel_e` select OSD matrix/LUT blocks.
- Static coefficient tables include RGB709-to-limited-YUV709 matrix, EOTF bypass matrix, linear EOTF 33-entry LUT, and linear OETF 41-entry LUT.
- Matrix/LUT writers: `meson_viu_set_g12a_osd1_matrix()`, `meson_viu_set_osd_matrix()`, `meson_viu_set_osd_lut()`, and `meson_viu_load_matrix()`.
- Public helpers: `meson_viu_osd1_reset()`, `meson_viu_g12a_enable_osd1_afbc()`, `meson_viu_g12a_disable_osd1_afbc()`, `meson_viu_gxm_enable_osd1_afbc()`, `meson_viu_gxm_disable_osd1_afbc()`, and `meson_viu_init()`.

## Control flow
Initialization disables OSD1 and OSD2, then loads the appropriate matrix path by SoC family. GXL/GXM use the older VIU OSD matrix/EOTF/OETF path; G12A uses the VPP wrapper OSD1 matrix and clears vendor bootloader HDR2 state that can cause color distortion. It then programs OSD FIFO priorities, burst lengths, hold lines, alpha replacement values, disables VD1 AFBC, initializes VD luma FIFO sizes, and for G12A sets blend routing, Dolby bypass, dummy blend data, and disables AFBCD.

The OSD1 reset helper saves two OSD control registers, toggles VIU software reset, restores the saved registers, and reloads color conversion state as a workaround for a GXL+ alpha OSD issue. AFBC enable on G12A enables Mali AFBC unpack, chooses ARGB or ABGR reorder based on `priv->afbcd.format`, and routes OSD1 through the AFBCD path. GXM AFBC control is a simpler write to `VIU_MISC_CTRL1`.

## State and persistence
The file initializes `priv->viu.osd1_enabled`, `osd1_commit`, and `osd1_interlace` to false. AFBC enable depends on `priv->afbcd.format`. Most state is persistent hardware register state in VIU, VPP wrapper, OSD blend, Dolby, FIFO, matrix, and LUT registers.

## Dependencies and integration points
Depends on Meson compatibility detection, register definitions, DRM fourcc formats, and Linux bitfield helpers. It is used by Meson driver initialization, plane/AFBCD paths, and reset workarounds needed by OSD scanout.

## Risks
Matrix and LUT programming is register-layout-sensitive, with different control bits for legacy VIU and G12A wrapper paths. The G12A color-distortion workaround clears vendor bootloader state and is easy to regress if compatibility checks change. AFBC reorder only switches for XBGR/ABGR; unsupported formats could display swapped channels. OSD reset preserves only two registers and then reloads matrices, so any additional volatile state lost across reset would need explicit restore.

## Test signals
Validate OSD scanout colors on GXL, GXM, and G12A, especially RGB-to-YUV limited range output and the green/pink distortion workaround. AFBC test signals include correct channel order for ARGB and ABGR/XBGR formats, clean enable/disable transitions, and no stale OSD blend routing after init or reset.
