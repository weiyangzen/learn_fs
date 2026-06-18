# sources/distributed-fs/ceph-client/drivers/video/hdmi.c

Purpose: generic HDMI infoframe helper library. It initializes, validates, packs, unpacks, checksums, and logs standard HDMI infoframes: AVI, SPD, Audio, HDMI Vendor, DRM, and a DisplayPort SDP representation of HDMI audio infoframes.

Important APIs, types, and functions: exported init/check/pack APIs include `hdmi_avi_infoframe_init/check/pack/pack_only`, `hdmi_spd_infoframe_init/check/pack/pack_only`, `hdmi_audio_infoframe_init/check/pack/pack_only/pack_for_dp`, `hdmi_vendor_infoframe_init/check/pack/pack_only`, `hdmi_drm_infoframe_init/check/pack/pack_only/unpack_only`, `hdmi_infoframe_pack`, `hdmi_infoframe_pack_only`, `hdmi_infoframe_unpack`, and `hdmi_infoframe_log`. Internal helpers compute checksums, derive vendor frame length, validate "any vendor" frames, unpack individual types, and map enum values to log strings.

Control flow: each frame type has an init function that zeroes and assigns type/version/length defaults, a check function that validates type/version/length and type-specific constraints, a pack-only function that validates the existing frame, writes header and payload bytes, zeroes the destination buffer, and stores checksum byte 3, and a pack function that first normalizes derived fields where needed. Generic pack/unpack switch on infoframe type. Unpack functions validate size, header, length, checksum, then fill typed structs. Logging dispatches by type and prints decoded enum names and fields.

State and persistence: stateless library code. It mutates caller-provided frame structs only in `check` paths that update derived length, and mutates caller-provided buffers during packing. No global state exists.

Dependencies and integration points: depends on `linux/hdmi.h` structure definitions and enums, `drm/display/drm_dp.h` for `struct dp_sdp`, device logging, exported symbols for DRM/HDMI bridge/display drivers, and kernel bit/errno/string helpers.

Risks: packing assumes callers provide semantically valid enum values beyond the explicit checks; many fields are masked rather than rejected. `pack_only` variants require pre-normalized fields, especially vendor length. Vendor handling only supports HDMI IEEE OUI. SPD string initialization copies fixed field sizes and may not NUL-terminate, which is acceptable for packed fields but relevant for logging. Checksum failures cause unpack rejection. A typo in the DRM init comment is harmless.

Test signals: unit/KUnit-style round-trip tests for every infoframe type; checksum validation; too-small buffer `-ENOSPC`; invalid type/version/length `-EINVAL`; vendor VIC versus 3D mutual exclusion; DRM unpack-only CTA bytes; DP audio SDP header fields; logging smoke tests with boundary enum values.
