# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.c

Purpose: manages split PCH display resources: PCH transcoders, FDI link enable/disable sequencing, PCH DPLL selection, PCH transcoder timings/M/N values, PCH DP transcoding bits, LPT iCLKIP path, PCH config readout, and IBX port sanitization.

Important functions: `intel_has_pch_trancoder()`, `intel_crtc_pch_transcoder()`, `ilk_pch_pre_enable()`, `ilk_pch_enable()`, `ilk_pch_disable()`, `ilk_pch_post_disable()`, `ilk_pch_get_config()`, `lpt_pch_enable()`, `lpt_pch_disable()`, `lpt_pch_get_config()`, M/N get/set helpers, and `intel_pch_sanitize()`.

Control flow: ILK/CPT enabling starts FDI PLL before CPU pipe enable, then trains FDI, selects PCH DPLL, enables DPLL, programs PCH M/N and timings copied from CPU transcoder, performs normal FDI train, optionally configures CPT `TRANS_DP_CTL`, and enables the PCH transcoder. Disable tears down FDI, disables PCH transcoder, clears DP/DPLL select bits, disables FDI PLL, and drops DPLL. LPT uses fixed PCH transcoder A, programs iCLKIP, copies timings, enables/disables LPT transcoder, and disables iCLKIP on teardown. Config readout detects active PCH transcoders, reads FDI lanes/M/N, DPLL state or iCLKIP clock, and sets `has_pch_encoder`.

State and persistence: programs PCH transcoder registers, FDI RX/TX dependencies, DPLL selection, DP transcoding control, timings, and `crtc_state` readout fields. Sanitization rewrites stale IBX disabled-port transcoder select bits to pipe A to avoid false asserts.

Dependencies/integration: depends on CRT/LVDS/SDVO/DP port helpers, FDI, DPLL, PPS unlock asserts, PCH refclk, register helpers, and atomic CRTC state.

Risks/test signals: sequencing is hardware-sensitive. Test PCH LVDS/HDMI/DP/CRT paths on IBX/CPT/LPT, FDI training failures, DPLL sharing, interlaced modes, DP M/N readback, LPT iCLKIP clock readback, and asserts for ports/transcoder disabled during teardown.
