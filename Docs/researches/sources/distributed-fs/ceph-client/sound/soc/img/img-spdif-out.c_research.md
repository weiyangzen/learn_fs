# sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-out.c

Purpose: ASoC CPU DAI driver for Imagination SPDIF output with dmaengine PCM and IEC958 playback channel-status controls.

Important APIs/types/functions: `struct img_spdif_out` stores MMIO, sys/ref clocks, reset, DMA data, spinlock, and suspend snapshots. Controls expose IEC958 playback mask/default. DAI ops implement trigger, hw_params, and DAI probe. `img_spdif_out_reset()` preserves control and channel status across hardware reset.

Control flow: probe maps registers, gets reset/clocks, enables runtime PM, initializes control register and reset state, initializes lock, sets DMA FIFO info, registers component and dmaengine PCM. `hw_params()` accepts stereo S32_LE, chooses ref clock close to rate*256 or rate*384, and sets the clock selector bit from actual clock. Trigger start sets SRT; stop resets under lock. IEC958 control get/set reads/writes CSL/CSH registers under spinlock. Suspend saves CTL/CSL/CSH and resume restores them.

State and persistence: software state is mostly lock and saved registers. Hardware holds IEC958 channel status and transmit control. Runtime PM gates sys/ref clocks.

Dependencies/integration: requires MMIO, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, ALSA controls, and compatible `img,spdif-out`.

Risks: `clk_set_rate()` return is ignored; actual clock is sampled afterward, but a failed set may leave poor-rate output. Trigger start is not locked while stop/reset and kcontrol writes are, so concurrent control and stream operations should be considered. Only S32_LE stereo is supported.

Test signals: playback rate tests, IEC958 status get/set persistence across reset and suspend/resume, trigger start/stop cycles, clock selector validation, and runtime PM error injection.
