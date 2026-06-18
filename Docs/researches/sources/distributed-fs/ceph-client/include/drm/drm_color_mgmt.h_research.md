# sources/distributed-fs/ceph-client/include/drm/drm_color_mgmt.h

## Purpose
This header declares DRM color management helpers for CRTC gamma/degamma/CTM properties, plane YCbCr encoding/range properties, LUT size and validation helpers, fixed-point conversion, and legacy palette/gamma loading utilities.

## Important APIs, types, and functions
Inline helpers `drm_color_lut_extract` and `drm_color_lut32_extract` round userspace LUT values to hardware precision. Other APIs include `drm_color_ctm_s31_32_to_qm_n`, `drm_crtc_enable_color_mgmt`, `drm_mode_crtc_set_gamma_size`, LUT size helpers, `drm_plane_create_color_properties`, `drm_color_lut_check`, gamma/palette load and fill helpers, and `drm_color_lut32_check`. Enums define YCbCr encodings, ranges, and LUT validation tests.

## Control Flow
Drivers expose color properties during initialization, atomic property setting installs blobs or enum values into state, check paths validate LUT blobs for channel equality or monotonicity as needed, and commit paths convert/load LUT entries into hardware-specific precision.

## State and Persistence
CRTC and plane color properties are persistent KMS properties. LUT blobs are refcounted DRM property blobs referenced by atomic state. Hardware tables are updated during commit from validated blob contents.

## Dependencies and Integration Points
It depends on DRM property blobs, UAPI LUT structures, math64 helpers, CRTC and plane objects, and legacy palette/gamma code. It integrates with atomic color management, legacy gamma IOCTLs, and plane YCbCr conversion controls.

## Risks and Test Signals
Risks include precision overflow for large bit depths, accepting malformed blob lengths, non-monotonic LUTs on hardware that requires monotonic tables, CTM fixed-point conversion mistakes, and mismatched default encoding/range. Tests should cover 16-bit and >16-bit LUT extraction, 32-bit LUT extraction at high precision, invalid blob sizes, equal-channel and non-decreasing checks, gamma size setup, and legacy 888/565/555/palette loading.
