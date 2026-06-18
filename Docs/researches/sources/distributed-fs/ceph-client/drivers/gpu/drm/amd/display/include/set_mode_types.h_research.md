# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/set_mode_types.h

Purpose: Defines HDMI info-frame packet status constants and packed structures for AVI/raw HDMI info packets used during display mode setting.

Important APIs and types: `enum info_frame_flag` contains invalid/valid/reset/update-scan-type states. `struct hdmi_info_frame_header` contains type/version/length. `struct info_packet_raw_data` models HB0-HB2 plus 28 sideband bytes. `union hdmi_info_packet` overlays a bitfield `avi_info_frame` representation with raw packet bytes.

Control flow: Mode-setting code can fill AVI fields semantically, then transmit as raw packet bytes, or manipulate raw bytes directly. `#pragma pack(push, 1)` ensures byte-level layout for the union payload.

State and persistence: No dynamic state. The structures are transient packets, but their layout must match HDMI specification and hardware packet programming registers.

Dependencies and integration points: Includes `dc_types.h` and Linux HDMI definitions. Used by stream encoder/infoframe programming in DC mode-set paths.

Risks: Bitfield ordering is compiler/endian-sensitive; the packed union must be validated for target architectures. Checksum calculation is not in this file, so callers must populate it correctly. The raw sideband size is fixed at 28 bytes and must match hardware expectations.

Test signals: Golden-byte tests for AVI infoframe construction, scan-type update handling, checksum validation in callers, and cross-endian/packing compile checks.
