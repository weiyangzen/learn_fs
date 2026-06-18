# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.c

## Purpose

`link_validation.c` owns link-level timing and bandwidth validation against dongle limits, DP receiver/link capabilities, USB4 DP tunnel budgets, and DP audio hblank requirements. It also exposes reusable bandwidth formulas.

## Important APIs, Types, And Functions

- `link_validate_mode_timing()` checks passive dongle pixel-clock limits, active dongle timing support, and DP link bandwidth.
- `dp_link_bandwidth_kbps()` computes effective DP bandwidth for 8b/10b and 128b/132b link settings, including FEC efficiency for 8b/10b when FEC should be enabled.
- `link_validate_dp_tunnel_bandwidth()` aggregates stream timing bandwidth by DPIA link and asks `link_dpia_validate_dp_tunnel_bandwidth()` to validate USB4 tunnel budgets.
- `dp_required_hblank_size_bytes()` calculates worst-case hblank bytes needed for DP audio SDP and main-link overhead for 8b/10b MST and 128b/132b.
- Static helpers validate active dongle encoding, color depth, 3D format, FRL/TMDS bandwidth, downstream-facing-port caps, VSC SDP requirements for YCbCr420, and audio layout overhead.

## Control Flow

Mode validation first permits virtual remote sinks for EDID override. It checks passive dongle pixel clock using TMDS output pixel clock adjusted for encoding and color depth. Active dongle validation branches by dongle type: simple DP-VGA/DVI require RGB, DP-HDMI converter checks extended caps, FRL/TMDS max bandwidth, and DFP capability extension fields. DP/eDP timings then require VSC SDP support for YCbCr420 unless virtual, always allow 640x480 fail-safe, enforce max uncompressed pixel rate unless DSC is enabled, and compare timing bandwidth against verified link bandwidth.

Tunnel validation iterates new context streams, filters DP/MST USB4/DPIA streams with bandwidth allocation enabled, groups required timing bandwidth by link, and validates all groups together. Audio hblank calculation derives audio layouts per line, rounds SDP symbol needs to lane mapping granularity, adds EOC/main-link overhead, and converts symbols to bytes by link encoding.

## State And Persistence Behavior

The file is mostly pure validation. It reads link DPCD/dongle caps, verified link caps, tunnel settings, stream timings, and audio params. It does not persist state or program hardware. Outputs are return statuses and calculated bandwidth/byte values.

## Dependencies And Integration Points

It includes `link_validation.h`, DP capability helpers, DPIA bandwidth helpers, and `resource.h`. DPMS uses `dp_link_bandwidth_kbps()` and `dp_required_hblank_size_bytes()` indirectly for payload/hblank decisions. Mode validation callers use `link_validate_mode_timing()` before committing modes.

## Risks And Edge Cases

- `dp_link_bandwidth_kbps()` multiplies/divides in an order that can lose precision and assumes link rates/lane counts are valid.
- The DP fail-safe 640x480 mode bypasses normal bandwidth checks.
- Some dongle DFP extension checks appear to test `support_rgb` for non-RGB encodings, matching current code but worth scrutiny.
- `link_validate_dp_tunnel_bandwidth()` iterates while `i < MAX_PIPES && i < stream_count` over `new_ctx->streams[]`, so stream array/count consistency matters.
- Audio hblank calculation assumes L-PCM, max one layout per SDP, four logical lanes, sixteen DSC slices worst case, and no SDP split.

## Test Signals

Test passive and active DP dongles, DP-HDMI FRL and TMDS converters, YCbCr420 VSC SDP support, DSC and max uncompressed pixel-rate caps, DP 8b/10b with and without FEC, DP 128b/132b, fail-safe 640x480, USB4 tunnel aggregation across multiple streams, and audio hblank for 2/6/8 channel audio at common sample rates. Return statuses `DC_EXCEED_DONGLE_CAP`, `DC_NO_DP_LINK_BANDWIDTH`, and `DC_FAIL_DP_TUNNEL_BW_VALIDATE` are key signals.
