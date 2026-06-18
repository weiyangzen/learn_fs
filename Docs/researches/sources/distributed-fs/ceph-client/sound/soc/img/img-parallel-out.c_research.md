# sources/distributed-fs/ceph-client/sound/soc/img/img-parallel-out.c

Purpose: ASoC CPU DAI driver for Imagination parallel audio output, using dmaengine PCM for stereo S24/S32 playback.

Important APIs/types/functions: `struct img_prl_out` stores MMIO, sys/ref clocks, reset, DMA FIFO data, and device pointer. DAI ops are trigger, hw_params, set_fmt, and DAI probe. Runtime PM callbacks control the ref clock while the sys clock is enabled for the device lifetime after probe.

Control flow: probe maps registers, gets reset and clocks, enables sys clock, initializes edge mode, resets hardware, enables runtime PM, sets DMA FIFO parameters, and registers component plus dmaengine PCM. `hw_params()` validates stereo S24/S32, sets ref clock to rate*256, and toggles high-packing for S32. `set_fmt()` allows normal bit clock with normal or inverted frame and writes edge selection under PM. Trigger start sets module enable; stop resets hardware while preserving non-enable bits.

State and persistence: minimal state; hardware control register holds format/edge/enable bits. Runtime PM only gates `clk_ref`; sys clock is explicitly disabled on remove or error.

Dependencies/integration: needs MMIO, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, and DT compatible `img,parallel-out`.

Risks: `clk_set_rate()` return is ignored. Only stereo is supported. Sys clock is not part of runtime PM suspend/resume and remains enabled while the device is bound. Reset must preserve control bits correctly across stop.

Test signals: stereo S24/S32 playback, frame inversion format tests, trigger stop/start reset behavior, runtime PM ref-clock gating, and error paths after sys clock enable.
