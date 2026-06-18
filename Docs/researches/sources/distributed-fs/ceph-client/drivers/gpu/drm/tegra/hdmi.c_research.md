# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hdmi.c

Purpose: full Tegra HDMI output driver: platform probe, host1x client lifecycle, DRM connector/encoder integration, mode programming, TMDS electrical setup, audio/ELD/infoframe handling, debugfs register dump, and HDA/SPDIF codec interoperability.

Important APIs/functions: `tegra_hdmi_probe()` gets clocks, reset, regulators, DDC/HPD output resources, MMIO, IRQ, OPP data, and registers the host1x client. `tegra_hdmi_init()/exit()` create encoder/connector or bridge connector, initialize common output state, enable regulators, and register the HDMI codec for non-HDA SoCs. Encoder helpers validate clocking, enable/disable SOR/TMDS/video/audio, and program display-controller HDMI output bits. Audio helpers compute N/CTS/AVAL, program audio FS tables, ELD, AVI/audio/vendor infoframes, and reconfigure live audio. `tegra_hdmi_irq()` handles HDA codec scratch0 format changes.

Control flow and state: `struct tegra_hdmi` persists connector/output, MMIO, regulators, clocks/reset, SoC config, audio source/format, pixel clock, DVI/HDMI mode, stereo flag, audio device, and mutex. Runtime resume powers PM, clock, and reset; encoder enable resumes host1x client, configures hardware, then enables packets/audio. Disable reverses visible output and suspends.

Dependencies/integration: depends on DRM connector/encoder helpers, bridge connector, EDID/ELD/infoframe APIs, HDMI codec, runtime PM/OPP, regulators, reset/clock APIs, `tegra_output`, `tegra_dc`, and register definitions from `hdmi.h`.

Risks: mode enable sequence is hardware-sensitive and includes a `BUG_ON()` retry exhaustion while waiting for SOR power state. Audio lock disables the HDMI IRQ, so lock/IRQ ordering matters. `dvi` fallback is used when audio setup fails. TMDS tables are SoC-specific and pixel-clock-threshold based. Debugfs reads require active CRTC.

Test signals: HDMI hotplug/mode-set, DVI sink fallback, audio playback via SPDIF/HDA, ELD correctness, suspend/resume with active display, debugfs register reads, and invalid mode clock tests are central.
