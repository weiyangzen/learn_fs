# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.h

Purpose: Declares the OMAP4 HDMI core register map, audio/video packet constants, core video configuration types, and public HDMI4 core entry points used by the OMAP HDMI4 implementation.

Important APIs/types: The file defines system, DDC, audio-video, packet, and infoframe register offsets such as `HDMI_CORE_SYS_*`, `HDMI_CORE_DDC_*`, and `HDMI_CORE_AV_*`. It declares enums for input bus width, output truncation/dither, deep-color packet enable, packet mode, clock multiplier, packet enable/repeat, and I2S audio setup. `struct hdmi_core_video_config` captures bus width, dither/truncation, deep color, packet mode, DVI/HDMI selection, and clock multiplier. `struct hdmi_core_packet_enable_repeat` controls audio, AVI, generic, and control packet repetition. Public functions cover DDC init/read, core configure/dump/init, core enable/disable/powerdown, and HDMI4 audio start/stop/config.

Control flow: This header is consumed by HDMI4 core and top-level HDMI4 code. Runtime flow is implemented elsewhere: probe maps the core, enable powers it, configure programs video, DDC read fetches EDID, and audio_config/start/stop program and gate audio packets.

State and persistence: No storage is allocated here. The declared APIs operate on `struct hdmi_core_data`, `struct hdmi_wp_data`, `struct hdmi_config`, and `struct omap_dss_audio`, which are volatile driver state.

Dependencies/integration: Includes `hdmi.h` for common HDMI structs, register helpers, and shared enums. Integrates with HDMI wrapper programming, DRM EDID callbacks, DSS output bridge enable paths, and OMAP HDMI audio.

Risks and test signals: Header-level risk is register offset or bitfield mismatch with OMAP4 TRM. Audio and DDC APIs depend on callers keeping runtime PM and regulators active. Validate with OMAP4 HDMI probe, EDID read, DVI/HDMI mode programming, infoframe emission, audio startup, and suspend/resume.
