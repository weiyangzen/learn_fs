# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.c

## Purpose
Initializes the Meson Video Post Processing block, including output muxing, postblend/preblend defaults, FIFO sizing, scaler disabling, and scaler filter coefficient programming.

## Important APIs, types, and functions
- `meson_vpp_setup_mux()` writes the VIU-to-VENC mux control register.
- Static OSD four-point B-spline and video bicubic coefficient tables provide 33 coefficient entries for horizontal and vertical scaler filters.
- `meson_vpp_write_scaling_filter_coefs()` and `meson_vpp_write_vd_scaling_filter_coefs()` program OSD and video scaler coefficient ports.
- `meson_vpp_init()` performs SoC-specific VPP initialization.

## Control flow
Initialization first programs dummy black data and Dolby-path settings by SoC compatibility: GXL, GXM, and G12A have different defaults. It sets output FIFO size and hold lines, disables preblend/postblend and all blend sources on non-G12A hardware, seeds default VD ranges, disables OSD scalers, enables video scale-out bank length defaults, enables VADJ minus black level, and writes both OSD and VD horizontal/vertical filter coefficients.

## State and persistence
No C-side state is kept in this file. VPP state persists in VPU MMIO registers until another init or modeset path updates it. The mux register determines which VENC block receives post-processed VIU output.

## Dependencies and integration points
Depends on Meson compatibility checks and register definitions. `meson_venc.c` calls `meson_vpp_setup_mux()` when selecting ENCI, ENCP, or ENCL. Plane and CRTC code rely on `meson_vpp_init()` defaults before enabling OSD scanout.

## Risks
SoC-specific defaults are compatibility-sensitive; incorrect dummy data, Dolby bypass, or blend setup can produce black screens or wrong color on one family while working on another. The header declares interlace scaler helpers that are not implemented in this file, so callers must link against another implementation or avoid those declarations in this tree revision.

## Test signals
Validate clean boot display on GXL/GXM/G12A, correct ENCI/ENCP/ENCL mux selection during mode changes, scaler-disabled baseline output, and absence of unexpected preblend/postblend video paths. Register dumps of `VPP_MISC`, `VPP_OFIFO_SIZE`, `VPU_VIU_VENC_MUX_CTRL`, and scaler coefficient ports are useful.
