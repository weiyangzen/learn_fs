# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.c

Purpose: manages DP-to-HDMI 2.0 LSPCON bridge chips on Intel digital ports, including probe, mode switching to PCON, vendor detection, HDR capability detection, AVI/HDR infoframe handling, infoframe readback, and resume recovery.

Important APIs/types/functions: `intel_lspcon_init()` probes and activates LSPCON. `intel_lspcon_resume()` restores PCON state after resume. `intel_lspcon_detect_hdr_capability()`, `intel_lspcon_active()`, `intel_lspcon_wait_pcon_mode()`, and `intel_lspcon_infoframes_enabled()` provide external state queries. Digital port hooks include `lspcon_write_infoframe()`, `lspcon_read_infoframe()`, `lspcon_set_infoframes()`, and `lspcon_infoframes_enabled()`. Internal helpers detect Parade/MegaChips OUIs, read/change LSPCON mode via dual-mode helpers, wake native AUX, and perform vendor-specific AVI infoframe writes.

Control flow: init wakes native AUX to infer expected mode, retries dual-mode adapter detection, waits for LS or PCON, forces PCON if needed, reads DPCD caps, detects vendor OUI, allows YCbCr420 on the connector, and marks the bridge active. AVI infoframe setup builds an HDMI AVI infoframe from the adjusted mode and connector state, adapts colorspace/quantization for RGB versus YCbCr444-to-420 conversion, packs it, and writes it through vendor-specific AUX sequences. MegaChips writes bytes to a DPCD window then kicks control bits; Parade writes four 8-byte blocks with firmware-ready polling. HDR/gamut metadata reuses HSW HDMI infoframe paths. Resume reinitializes inactive bridges, detects expected mode, applies a PCON resume workaround, waits for mode, and forces PCON if required.

State and persistence behavior: runtime state is in `dig_port->lspcon`: active flag, mode, vendor, and HDR support. Hardware state lives in the bridge's DPCD/I2C-controlled mode and infoframe registers and in i915 DIP registers for HDR metadata. No filesystem persistence exists.

Dependencies and integration points: depends on DRM DP dual-mode helpers, DP DPCD/AUX, HDMI infoframe helpers, EDID connector state, Intel DP and HDMI code, digital port hook tables, and HSW infoframe register helpers.

Risks: vendor-specific protocols have different timeouts and control bits; Parade firmware can be slow to accept blocks. Mode settling differs by vendor, with Parade using an 800 ms timeout. Native AUX wake behavior determines expected LS/PCON mode, so resume failures can leave descriptor mismatches. AVI readback is not implemented, so state verification is partial. Color-space handling assumes LSPCON may downsample YCbCr444 pipe output to YCbCr420.

Test signals: detection of Parade and MegaChips LSPCONs, PCON mode switch and settle timing, HDR capability DPCD reads, AVI infoframe writes on both vendors, HDR metadata enable/readback, YCbCr420 output modes, suspend/resume PCON recovery, native AUX down/up behavior, and failure logs for slow firmware or invalid OUI.
