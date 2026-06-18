# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out.c

Purpose: ASoC CPU DAI driver for SPEAr S/PDIF output/playback.

Important APIs/functions: probe maps MMIO, gets clock and platform data, initializes DMA parameters, registers component/DAI, and registers the shared SPEAr DMAEngine PCM platform. `spdif_out_configure()` resets the block, programs memory format, FIFO trigger, and hardware validity/user/channel/parity handling, then clears/disables interrupts. `spdif_out_hw_params()` chooses a core clock family based on sample rate and programs the divider. Trigger start selects audio-data or mute opmode, and stop selects off. `spdif_mute()` and DAI control callbacks expose an IEC958 playback switch. PM suspend/resume disables/enables the clock and restores configuration when running.

Control flow/state: `struct spdif_out_dev` stores clock, DMA params, saved rate/core frequency/mute, running flag, MMIO, and DMAEngine config. Saved params are used for resume and trigger/mute behavior.

Dependencies/integration: depends on legacy `spear_spdif_platform_data`, shared `spear_pcm`, platform clock, DMA filter data, and ASoC DAI controls.

Risks/test signals: probe dereferences platform data without a null check, unlike the input driver. `clk_set_rate()` return is ignored in `spdif_out_clock()`. Tests should cover all supported rate families, mute toggling while stopped/running, suspend/resume while running, missing platform data failure, DMA playback, and divider accuracy.
