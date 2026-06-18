# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_edid.h

## Purpose
Static EDID fixture header for DRM HDMI KUnit tests. It provides raw base and CTA extension blocks that model DVI, HDMI 1080p, HDR, YUV/deep-color, constrained TMDS, and 4K YUV420-only/also-capable displays.

## Important APIs, Types, And Functions
The file exports no functions; it declares `static const unsigned char` arrays named `test_edid_dvi_1080p`, `test_edid_hdmi_1080p_rgb_max_100mhz`, `test_edid_hdmi_1080p_rgb_max_200mhz`, `test_edid_hdmi_1080p_rgb_max_200mhz_hdr`, `test_edid_hdmi_1080p_rgb_max_340mhz`, `test_edid_hdmi_1080p_rgb_yuv_dc_max_200mhz`, `test_edid_hdmi_1080p_rgb_yuv_dc_max_340mhz`, `test_edid_hdmi_1080p_rgb_yuv_4k_yuv420_dc_max_200mhz`, and `test_edid_hdmi_4k_rgb_yuv420_dc_max_340mhz`. Each array is accompanied by an `edid-decode` transcript documenting the intended capabilities and conformance.

## Control Flow
There is no runtime control flow in this header. Consumers pass the raw byte arrays and `ARRAY_SIZE()` into DRM EDID allocation/parsing helpers. The fixtures are selected by tests to force HDMI helper branches such as DVI behavior, max-TMDS rejection, RGB-only display constraints, YUV422/YUV444 support, YUV420-only 4K modes, HDR static metadata, and HDMI Forum deep-color data.

## State And Persistence
The EDID arrays are immutable test data compiled into the KUnit object. Their contents become transient parsed connector state only when a test calls `drm_edid_alloc()` and updates a connector.

## Dependencies And Integration Points
The header is tightly coupled to DRM EDID/CTA parsing and `drm_hdmi_state_helper_test.c`. The decoded comments document external expectations from `edid-decode`, including checksums, VICs, max TMDS clocks, colorimetry, deep-color flags, SCDC presence, and HDR metadata.

## Risks And Maintenance Notes
The arrays are binary fixtures, so small byte edits can silently change many parsed properties. The 100 MHz fixture is intentionally nonconformant to exercise filtering; it should not be generalized as a valid monitor. If EDID parser behavior changes, tests may fail because preferred modes, 4:2:0 capability maps, HDR property exposure, or `is_hdmi` classification change. Regenerate comments with a matching `edid-decode` version when fixture bytes are modified.

## Test Signals
Signals are indirect: consumers expect exact parsed display capabilities, mode availability, and conformance/failure semantics. Important observable values include 1080p/4K preferred modes, 640x480 fallback modes after filtering, max TMDS clocks of 100/200/340 MHz, HDR metadata availability, and YUV420-only versus YUV420-also mode classification.
