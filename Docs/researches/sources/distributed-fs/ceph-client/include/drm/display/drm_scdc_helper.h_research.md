# sources/distributed-fs/ceph-client/include/drm/display/drm_scdc_helper.h

Purpose: helper declarations for reading/writing HDMI SCDC registers and toggling scrambling and high TMDS clock ratio through a DRM connector.

Important APIs/types/functions: `drm_scdc_read`, `drm_scdc_write`, inline `drm_scdc_readb`, inline `drm_scdc_writeb`, `drm_scdc_get_scrambling_status`, `drm_scdc_set_scrambling`, and `drm_scdc_set_high_tmds_clock_ratio`.

Control flow: drivers perform arbitrary SCDC register access or call connector helpers during modeset to program scrambling and the TMDS 1/40 clock ratio.

State and persistence: no local state. Sink SCDC registers and connector/DDC context hold runtime state.

Dependencies and integration points: Linux types, SCDC constants, DRM connectors, I2C adapters, and HDMI mode-setting.

Risks and test signals: short I2C transfers, missing DDC, boolean helpers hiding detail, scrambling status failures, and wrong ordering relative to TMDS enable are risks. Test read/write errors, high TMDS modes, non-SCDC sinks, and hotplug after programming.
