# sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifout.c

Purpose: Implements the AXG SPDIF output DAI and component. It configures SPDIF framing, sample extraction from FIFO words, IEC958 channel-status words, mute via validity bit, input source DAPM routing, playback mixer controls, and mclk/pclk sequencing.

Important APIs and functions: Runtime ops are `axg_spdifout_startup()`, `axg_spdifout_shutdown()`, `axg_spdifout_hw_params()`, `axg_spdifout_trigger()`, and `axg_spdifout_mute()`. Helpers include `axg_spdifout_enable()`, `axg_spdifout_disable()`, `axg_spdifout_sample_fmt()`, and `axg_spdifout_set_chsts()`. Component bias callback `axg_spdifout_set_bias_level()` enables mclk in PREPARE and disables it on return to STANDBY.

Control flow: Startup enables pclk, disables the block, sets baseline data ordering, selects manual control for V/C/U bits, and writes a static swap configuration. `hw_params` sets mclk to `rate * 128`, configures channel mask and sample packing based on channel count and physical width, positions the MSB from actual sample width, and writes consumer IEC958 status into A and B channel registers while clearing the remaining status words. Trigger applies reset sequencing and enables/disables the block. Mute sets the SPDIF validity bit.

State and persistence: `struct axg_spdifout` stores regmap, mclk, and pclk. Routing, gain, mute, channel-status, and sample-format bits persist in SPDIFOUT registers. Bias level controls mclk lifetime independent of stream pclk startup.

Dependencies and integration points: Uses ALSA IEC958 helpers, regmap MMIO, clocks named `pclk` and `mclk`, DAPM source mux from IN0-IN2, and AXG sound-card routes from FRDDR/TDM outputs.

Risks: Comments note documentation has inverted meaning for V/U/C select bits; future changes must preserve the empirically correct manual-control semantics. Only 1 or 2 channels and 8/16/32 physical width modes are supported. Channel-status generation writes only the first 32 bits and clears the rest. MCLK and pclk are controlled by different lifecycle callbacks, so bias transitions matter.

Test signals: SPDIF playback at supported rates, S8/S16/S20/S24 samples, 1- and 2-channel streams, receiver IEC958 status verification, mute/unmute via validity bit, DAPM input-source switching, and bias-level clock enable traces.
