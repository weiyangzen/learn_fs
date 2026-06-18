# sources/distributed-fs/ceph-client/include/drm/display/drm_dsc.h

Purpose: VESA Display Stream Compression definitions for constants, encoder configuration, 128-byte Picture Parameter Set layout, and DP PPS infoframe container.

Important APIs/types/functions: no functions. Main definitions are DSC rate-control constants and PPS masks/shifts, `struct drm_dsc_rc_range_parameters`, `struct drm_dsc_config`, `struct drm_dsc_picture_parameter_set`, and `struct drm_dsc_pps_infoframe`; packed PPS fields use big-endian wire layout where required.

Control flow: drivers populate `drm_dsc_config`, helper code computes RC fields, packs a PPS, wraps it in a DP PPS infoframe, and programs/sends it before enabling compression.

State and persistence: caller-owned config and packed metadata only. PPS bytes are protocol-persistent for the active stream; encoder/decoder state is elsewhere.

Dependencies and integration points: `drm_dp.h` for SDP headers, DP/eDP DSC helpers, HDMI PCON DSC, encoder drivers, and sink capability parsing.

Risks and test signals: endian/packing errors, invalid RC params, slice mismatch, unsupported bpc/bpp/native modes, and PPS/capability mismatch are risks. Test PPS byte vectors, DSC 1.1/1.2, RGB/YCoCg/native formats, 8/10/12 bpc, slice limits, and compressed enable/disable.
