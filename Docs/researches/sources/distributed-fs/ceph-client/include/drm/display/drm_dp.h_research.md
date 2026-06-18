# sources/distributed-fs/ceph-client/include/drm/display/drm_dp.h

Purpose: core DisplayPort protocol registry header defining AUX codes, DPCD addresses/bit fields, eDP, MST, DSC, FEC, PSR, Panel Replay, PCON, CEC, HDCP, DP tunneling, LTTPR, and SDP wire structures.

Important APIs/types/functions: no functions. Important types are `enum drm_dp_phy`, `struct dp_sdp_header`, `struct dp_sdp`, `enum dp_pixelformat`, `enum dp_colorimetry`, `enum dp_dynamic_range`, `enum dp_content_type`, and `enum operation_mode`; macro groups cover link training, payload tables, eDP backlight/PSR, DSC/PCON, HDCP offsets, CEC tunneling, USB4 tunneling, LTTPR addressing, and MST sideband IDs.

Control flow: callers use constants to form AUX/DPCD transactions, train links, parse capabilities, configure eDP/DSC/FEC/MST/PCON/HDCP/CEC/tunneling features, and pack or parse secondary data packets.

State and persistence: no kernel state. Constants describe wire-visible sink/branch/repeater/protocol-converter registers; packed SDP structures are ABI-sensitive.

Dependencies and integration points: Linux integer/bit macros, DP helpers, MST helpers, DSC, HDCP, CEC-over-AUX, tunneling, and GPU DP drivers.

Risks and test signals: spec-version gating, overlapping register meanings, bit mask errors, endian/packing mistakes, and stale revision constants are risks. Test 8b/10b and 128b/132b link training, MST sideband, eDP PSR/backlight/Panel Replay, DSC/FEC, PCON FRL/DSC, CEC, HDCP, LTTPR, and USB4 tunnel events.
