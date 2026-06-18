# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.h

Purpose: This header exposes SDP header parity/packing helpers and the bit masks used to pack four DP SDP header bytes plus parity into two hardware words.

Important APIs and types: It defines header/parity bit positions and GENMASK fields for HB0-HB3 and parity bytes, then declares `msm_dp_utils_get_g0_value()`, `msm_dp_utils_get_g1_value()`, `msm_dp_utils_calculate_parity()`, and `msm_dp_utils_pack_sdp_header()`.

Control flow and integration: The header is included by `dp_panel.c` to pack VSC SDP headers before MMIO writes. It includes Linux bitfield helpers and DRM DP helper definitions for `struct dp_sdp_header`.

State and risks: No state is owned here. The risk is that mask definitions must match the hardware word layout expected by the DP link block. Compile testing and runtime VSC SDP/YUV420 validation are the key signals.
