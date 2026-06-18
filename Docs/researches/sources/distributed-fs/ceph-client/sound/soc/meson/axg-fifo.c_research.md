# sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.c

Purpose: Provides the shared PCM/component implementation for AXG/G12A playback and capture FIFOs. It manages DMA address registers, FIFO thresholds, interrupts, memory-arbiter reset, pclk, pointer reporting, trigger enable, managed buffers, and platform resource probing.

Important APIs and functions: Exported helpers include `axg_fifo_pcm_open()`, `axg_fifo_pcm_close()`, `axg_fifo_pcm_hw_params()`, `g12a_fifo_pcm_hw_params()`, `axg_fifo_pcm_hw_free()`, `axg_fifo_pcm_pointer()`, `axg_fifo_pcm_trigger()`, `axg_fifo_pcm_new()`, and `axg_fifo_probe()`. Internal helpers include `__dma_enable()`, `axg_fifo_ack_irq()`, and `axg_fifo_pcm_irq_block()`.

Control flow: Open applies broad PCM hardware limits, enforces burst alignment, requests a threaded IRQ, enables pclk, selects DDR-read status reporting, disables DMA and IRQs, clears pending interrupts, and deasserts the memory arbiter reset. `hw_params` programs start/finish addresses, interrupt period count, threshold as half of the smaller of period and FIFO depth, and repeat-count IRQ enable unless no-period-wakeup is requested. Trigger toggles DMA enable. IRQ handler acknowledges status and calls `snd_pcm_period_elapsed()` on repeat-count interrupts. Close asserts the arbiter reset, disables pclk, and frees IRQ. Probe maps registers, gets pclk/reset/irq, allocates the threshold regmap field, reads FIFO depth with a 256-byte fallback, and registers the SoC component/DAI from match data.

State and persistence: `struct axg_fifo` stores regmap, pclk, reset, threshold field, depth, and IRQ per platform device. PCM runtime DMA addresses persist in FIFO registers while a stream is configured. IRQ enable and DMA enable bits persist until hw_free/trigger/open reset.

Dependencies and integration points: Used by FRDDR and TODDR drivers through match data and component callbacks. Depends on regmap MMIO, OF IRQ, reset controller, clock controller, ALSA PCM, and ASoC component APIs.

Risks: Pointer reporting subtracts a 32-bit-cast DMA address from the status register; managed buffers should remain addressable by the hardware. Missing `amlogic,fifo-depth` falls back to the smallest known depth, which is safe but may reduce performance. IRQ status other than repeat-count is logged but not otherwise handled. The threshold calculation assumes period and depth are byte counts aligned to the burst size.

Test signals: FRDDR/TODDR playback/capture open-close, period wakeups and no-period-wakeup mode, underrun/stop/pause triggers, FIFO depth property present/missing, reset controller behavior, and regmap traces for FIFO start/finish/int/status registers.
