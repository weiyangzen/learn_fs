# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/dce6_afmt.h

Purpose: declares the DCE6 AFMT/audio endpoint helper interface used by radeon display and audio code. It provides forward declarations for DRM/radeon types and prototypes for endpoint access, HDMI/DP speaker/SAD programming, latency programming, pin selection, and audio DTO setup.

Important APIs and types: the header forward-declares `struct cea_sad`, `struct drm_connector`, `struct drm_display_mode`, `struct drm_encoder`, `struct radeon_crtc`, and `struct radeon_device`. Prototypes include `dce6_endpoint_rreg`, `dce6_endpoint_wreg`, `dce6_afmt_write_sad_regs`, HDMI/DP speaker allocation writers, `dce6_afmt_write_latency_fields`, `dce6_afmt_select_pin`, `dce6_hdmi_audio_set_dto`, and `dce6_dp_audio_set_dto`.

Control flow: there is no implementation flow in the header. It defines the call surface used by modeset/audio code to program DCE6+ audio hardware in a staged sequence: choose/select a pin, program sink capability descriptors and speaker allocation, program latency fields, and set the DTO clock for HDMI or DP transport.

State and persistence: no state is stored in this header. The declared functions mutate radeon device state and hardware endpoint/AFMT/DCCG registers in `dce6_afmt.c`. The use of forward declarations keeps compile-time coupling low while preserving the ABI between radeon display code and AFMT implementation.

Dependencies and integration points: the header is private to the radeon driver and guarded by `__DCE6_AFMT_H__`. It is included by `dce6_afmt.c` and by other DCE6/DCE8 display paths that need audio programming helpers. Callers must provide valid encoder/connector/mode/CRTC/device objects whose private radeon fields are initialized.

Risks: the prototypes expose low-level register helpers and assume callers know the correct block offset and transport-specific sequencing. There is no type-level distinction between HDMI and DP clocks or between SAD count and speaker-allocation byte count. Missing declarations for non-header-local helpers such as pin acquisition or audio enable may be intentional internal linkage through other headers, but API drift should be reviewed when changing audio setup paths.

Test signals: compile coverage catches prototype drift. Runtime tests should exercise HDMI and DP audio setup through the public prototypes on DCE6/DCE8 hardware, including modesets, hotplug, EDID audio changes, and DTO programming.
