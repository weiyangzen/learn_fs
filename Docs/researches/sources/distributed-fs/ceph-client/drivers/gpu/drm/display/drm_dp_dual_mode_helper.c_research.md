# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_dual_mode_helper.c

Purpose: provides helper functions for detecting and controlling DisplayPort dual-mode (DP++) adaptors, including Type 1/Type 2 HDMI/DVI adaptors and LSPCON mode switching.

Important APIs/functions: `drm_dp_dual_mode_read()` and `drm_dp_dual_mode_write()` access adaptor registers at I2C slave address `0x40`; reads always start at offset zero and discard leading bytes when needed to handle adaptors without sub-addressing. `drm_dp_dual_mode_detect()` reads HDMI ID and adaptor ID to classify unknown/native, Type 1 DVI/HDMI, Type 2 DVI/HDMI, or LSPCON. `drm_dp_dual_mode_max_tmds_clock()` returns native unlimited, Type 1 fixed 165 MHz, or Type 2 register-derived limits. `drm_dp_dual_mode_get_tmds_output()`/`set_tmds_output()` read or control Type 2 TMDS output buffers, with write-read verification retries for LSPCON low-power behavior. `drm_dp_get_dual_mode_type_name()` maps enums to strings. `drm_lspcon_get_mode()` reads current level-shifter/protocol-converter mode with retries, and `drm_lspcon_set_mode()` writes requested mode and polls until the mode changes or times out.

Control flow: Type 1 adaptors often lack registers; failures reading the HDMI ID return `UNKNOWN`, leaving native HDMI versus Type 1 DVI decisions to driver-specific detection. Type 2 and LSPCON behavior depends on register reads. LSPCON set loops in 10 ms increments until timeout.

State and persistence: no driver state is stored here. State is adaptor hardware registers accessed through the DDC/I2C adapter.

Dependencies and integration points: depends on Linux I2C, DRM device logging, and public DP dual-mode register definitions. GPU drivers call these helpers during HDMI/DP++ detection, mode validation, and output enable/disable.

Risks: adaptor register behavior is inconsistent; helper deliberately uses conservative fallbacks. `drm_dp_dual_mode_read()` may allocate `size + offset` bytes and asks I2C to read that whole span, so callers should keep sizes bounded. Type misdetection can lead to wrong TMDS limits or buffer control. LSPCON mode changes depend on adaptor firmware timing.

Test signals: native HDMI ports, Type 1 DVI/HDMI adaptors with no registers, Type 2 adaptors, LSPCON adapters, max TMDS register edge values 0/0xff, TMDS output set verification retries, and LSPCON mode-change timeout behavior.
