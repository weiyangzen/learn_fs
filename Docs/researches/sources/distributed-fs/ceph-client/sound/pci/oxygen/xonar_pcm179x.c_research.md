
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_pcm179x.c

Purpose: largest Xonar board provider, covering PCM1796/PCM1792A-based D2/D2X/HDAV1.3/ST/STX/STX II/Xense boards, optional H6 daughterboards, CS2000 clocking, HDMI, GPIO output routing, and AC97 input routing.

Important types/functions: `struct xonar_pcm179x` embeds `xonar_generic`, DAC count, PCM1796 register cache, current rate, H6/headphone/CS2000 flags, HP gain offset, CS2000 cache, and broken-I2C flag. `struct xonar_hdav` adds HDMI state. PCM1796 write paths select SPI or I2C by model function flags; caches suppress redundant writes. Init functions configure per-board I2C/SPI, external power, CS53x1, CS2000, GPIOs, DAC count, H6 detection, HDMI, and output enable. Runtime callbacks update oversampling/de-emphasis by rate, CS2000 rate/MCLK, volume/mute, headphone routing/gain, HDMI params, rolloff/de-emphasis controls, and proc dumps.

Control flow: `get_xonar_pcm179x_model` matches subsystem IDs and may read GPIO daughterboard bits to mutate model channel counts, clocks, control filters, and shortnames. Shared probe then allocates model data and calls selected init. PCM hw_params calls model `set_dac_params`; mixers modify cached DAC/GPIO state.

State/persistence: codec caches, `current_rate`, H6/headphone flags, CS2000 cache, and HDMI params survive for resume replay. Shared DAC volume/mute state is combined with HP gain offset.

Dependencies: Oxygen SPI/I2C/GPIO/AC97/UART helpers, `xonar_lib`, `xonar_hdmi`, CM9780, PCM1796, CS2000, ALSA controls. Risks include board-variant branching, H6 detection, broken ST I2C filtering, CS2000 PLL timing, output GPIO safety, and HP gain offsets affecting only first DAC. Test signals: all supported subsystem IDs, H6 and non-H6 variants, playback rates, HDMI constraints, SPDIF, AC97 input switch, rolloff/deemphasis, headphone impedance/output controls, external power events, suspend/resume, and proc dumps.
