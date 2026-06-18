# sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-out.c

Purpose: ASoC CPU DAI driver for the Imagination I2S output controller, supporting multi-channel S32_LE playback through dmaengine PCM.

Important APIs/types/functions: `struct img_i2s_out` contains MMIO, sys/ref clocks, reset, DMA data, active/max channel count, force-clock flag, DAI driver, and suspend snapshots. Key functions are runtime PM callbacks, `img_i2s_out_reset()`, DAI trigger/hw_params/set_fmt/probe, DMA prepare callback, and platform probe/remove/suspend/resume.

Control flow: probe maps resources, gets channel count, reset and clocks, allocates suspend storage, resumes PM, initializes global/channel registers, resets hardware, sets DMA data, registers component and dmaengine PCM. `set_fmt()` programs master/slave, continuous/gated clock, inversion, and I2S/left-justified channel timing under PM. `hw_params()` accepts only S32_LE, chooses a ref clock near rate*256 or rate*384, programs clock selector and active channel count, and enables the requested channel lanes. Trigger start enables clock/data; stop resets the block while preserving selected config.

State and persistence: persistent driver state includes `force_clk_active`, `active_channels`, DMA FIFO info, and saved registers. Runtime PM enables/disables sys and ref clocks. Reset sequencing rewrites saved channel/global config.

Dependencies/integration: requires MMIO, `img,i2s-channels`, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, and DT compatible `img,i2s-out`.

Risks: only S32_LE is supported despite hardware format fields; machine drivers must constrain formats. `clk_set_rate()` return is ignored after selecting the rounded rate, relying on later `clk_get_rate()` to infer actual clock. Reset on stop can be disruptive if another stream/shared clock existed. Channel base calculation depends on power-of-two rounded max channel count.

Test signals: playback across supported rates/channel counts, continuous clock mode, master/slave and inversion combinations, stop/reset/restart cycles, suspend/resume restore, and DMA destination burst scaling.
