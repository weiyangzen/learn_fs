# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-dma.c

## Purpose
ASoC platform/PCM DMA support for Socionext UniPhier AIO. It exposes the memory-ring side of the AIO engine to ALSA PCM and compressed-audio streams, maps the AIO register resource, requests the shared DMA interrupt, and registers a component with PCM and compress callbacks.

## Important APIs, Types, and Functions
The exported entry point is `uniphier_aiodma_soc_register_platform()`. Runtime callbacks are `uniphier_aiodma_open()`, `uniphier_aiodma_prepare()`, `uniphier_aiodma_trigger()`, `uniphier_aiodma_pointer()`, `uniphier_aiodma_mmap()`, and `uniphier_aiodma_new()`. IRQ flow is handled by `aiodma_irq()`, `aiodma_pcm_irq()`, and `aiodma_compr_irq()`. The component uses the `uniphier_aio_sub` state and helper APIs declared in `aio.h`, especially `aiodma_ch_set_param()`, `aiodma_rb_set_buffer()`, `aiodma_rb_sync()`, `aiodma_rb_set_threshold()`, and interrupt clear/test helpers.

## Control Flow, State, and Persistence
Registration maps the AIO DMA register block through a 32-bit MMIO regmap, obtains IRQ 0, registers a shared interrupt handler, and then registers the ASoC component. `open()` installs static hardware limits and a 256-byte buffer-step constraint. `prepare()` programs channel parameters and ring-buffer bounds under the substream lock. `trigger(START)` syncs ring pointers, enables the DMA channel, and marks `sub->running`; `STOP` clears `running` before disabling the channel. IRQ scanning walks every `chip->aios[i].sub[j]`, checks `running` plus hardware IRQ status, advances the threshold by one ALSA period/fragment, syncs read/write offsets, clears the IRQ, and notifies ALSA with `snd_pcm_period_elapsed()` or `snd_compr_fragment_elapsed()`. State persists in `sub->threshold`, `rd_offs`, `wr_offs`, PCM/compress stream pointers, and the hardware ring registers until stop/prepare rewrites them.

## Dependencies and Integration Points
Depends on ALSA SoC component APIs, ALSA compressed ops from `uniphier_aio_compress_ops`, Linux DMA mask/buffer APIs, platform resources, IRQs, and UniPhier AIO helper routines implemented in sibling files. DAI drivers in `aio-ld11.c` and `aio-pxs2.c` use the CPU DAI identity to reach the matching `uniphier_aio` instance via `uniphier_priv()`.

## Risks and Test Signals
Risks include threshold drift if `aiodma_rb_set_threshold()` fails repeatedly, shared IRQ scans across inactive substreams, hard-coded 33-bit DMA addressing, mmap write-combine assumptions, and pointer correctness depending on `aiodma_rb_sync()` maintaining coherent offsets. Test signals are PCM playback/capture period interrupts, compressed S/PDIF fragment interrupts, pointer monotonicity/wrap behavior, mmap playback, prepare/start/stop cycles without stale IRQs, and DMA mask success on target UniPhier systems.
