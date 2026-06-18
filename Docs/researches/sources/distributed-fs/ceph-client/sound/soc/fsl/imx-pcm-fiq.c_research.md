# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-pcm-fiq.c

## Purpose
Legacy i.MX SSI PCM backend using ARM FIQ code instead of DMA-engine PCM. It allocates fixed write-combined buffers, installs an SSI FIQ handler, tracks hardware position from FIQ registers, and reports periods through an hrtimer.

## APIs, Types, and Functions
`struct imx_pcm_runtime_data` stores period sizing, current offset, hrtimer, substream, and playback/capture atomics. Main component callbacks are `snd_imx_open()`, `snd_imx_close()`, `snd_imx_pcm_hw_params()`, `snd_imx_pcm_prepare()`, `snd_imx_pcm_trigger()`, `snd_imx_pcm_pointer()`, `snd_imx_pcm_new()`, and `snd_imx_pcm_free()`. Exports `imx_pcm_fiq_init()` and `imx_pcm_fiq_exit()`.

## Control Flow, State, and Persistence
Open allocates runtime data and initializes the hrtimer. `hw_params()` computes period bytes/count and timer polling interval. Prepare writes the ring-buffer end into ARM FIQ registers r8/r9. Trigger START sets active atomics, starts the hrtimer, and enables the FIQ; STOP clears atomics and disables FIQ when both directions are inactive. The hrtimer snapshots r8/r9 low bits into `offset` and calls `snd_pcm_period_elapsed()`. PCM creation sets fixed buffers and exposes their virtual addresses through global FIQ symbols.

## Dependencies and Integration
Depends on ARM FIQ APIs, `imx-ssi.h` FIQ symbols, `imx-pcm.h`, ALSA PCM component callbacks, and platform data containing SSI base/IRQ and DMA params. It integrates with SSI drivers that select FIQ mode.

## Risks and Test Signals
Risks include global FIQ ownership (`claim_fiq`) preventing coexistence, register-based pointer width limitations, timer period arithmetic overflow/rounding, no cleanup in `imx_pcm_fiq_exit()`, and architecture specificity. Test signals are successful FIQ claim, fixed buffer setup, playback/capture pointer movement, period elapsed cadence, start/stop without stuck FIQ, and underrun-free SSI audio on supported ARM i.MX systems.
