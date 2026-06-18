# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-aud.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-aud.c

### Purpose
`clk-mt8516-aud.c` registers MT8516 audio subsystem gates for AFE, I2S, 22 MHz, 24 MHz, internal direction/SPDIF, APLL tuners, HDMI, ADC, DAC, DAC pre-distortion, and TML clocks.

### Important APIs, Types, And Functions
The file defines a no-setclr audio gate bank, `GATE_AUD`, `aud_clks`, `aud_desc`, and an OF match for `mediatek,mt8516-audsys`. It uses `mtk_clk_gate_ops_no_setclr` and common `mtk_clk_simple_probe()`/`remove()`.

### Control Flow, State, And Persistence
Probe registers the audio gates and publishes the provider. Gates are controlled through a direct register at offset 0x0 with no set/clear sideband. State is hardware-only and no runtime PM logic is implemented locally.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents from MT8516 topckgen such as `clk26m_ck`, `i2s_infra_bck`, `rg_aud_engen1/2`, `rg_aud_spdif_in`, and APLL dividers. Risks include no-setclr races, parent naming mismatches, and tuner clocks being required before audio stream start. Test signals include ALSA playback/capture, SPDIF/HDMI audio, APLL tuner enables, clk summary, and suspend/resume audio.
