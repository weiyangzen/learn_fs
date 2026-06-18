
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-audio.c

## Purpose
This file implements ALSA PCM capture support for TW686x devices. It initializes an ALSA card/PCM capture device, manages per-channel audio DMA buffers, applies global audio sample-rate and period-size settings, services audio DMA interrupts, and starts/stops hardware audio channels.

## Important APIs, Types, And Functions
Externally used functions are `tw686x_audio_init`, `tw686x_audio_free`, and `tw686x_audio_irq`. ALSA callbacks are `tw686x_pcm_open`, `tw686x_pcm_close`, `tw686x_pcm_prepare`, `tw686x_pcm_trigger`, and `tw686x_pcm_pointer`, collected in `tw686x_pcm_ops`. Helpers are `tw686x_snd_pcm_init`, `tw686x_audio_dma_alloc`, and `tw686x_audio_dma_free`. The hardware contract is described by `tw686x_capture_hw`.

## Control Flow
Audio init enables external audio, creates an ALSA card, initializes each `tw686x_audio_channel`, optionally allocates coherent ping-pong DMA buffers for memcpy mode, creates capture substreams for `max_channels(dev)`, assigns managed ALSA buffers, and registers the card. PCM open stores the substream and hardware caps. Prepare rejects changes to global rate/period while any audio channel is enabled, disables the channel, updates audio clock divider and DMA size registers when needed, builds a list of runtime periods, selects initial P/B buffers, and programs DMA addresses in non-memcpy modes. Trigger start enables the channel and arms the DMA delay timer; trigger stop disables it and clears current buffers. IRQ handling rotates completed/current buffers based on P/B status, copies from coherent staging buffers in memcpy mode or programs the next DMA address otherwise, updates the ALSA pointer, and calls `snd_pcm_period_elapsed`.

## State And Persistence
Device-level runtime state includes `audio_rate`, `period_size`, `audio_enabled`, DMA mode, sound card pointer, and timer. Each channel stores lock, substream, channel number, buffer list, current ping-pong buffers, pointer, and optional coherent DMA descriptors. No data is persisted beyond hardware registers and ALSA runtime buffers.

## Dependencies And Integration Points
The file depends on ALSA core/PCM APIs, `tw686x.h` structures and channel helpers, `tw686x-regs.h` register definitions, PCI DMA allocation, timers owned by core code, and interrupt dispatch from `tw686x-core.c`.

## Risks
`dev->audio_enabled` is a single boolean, so stopping one channel clears it even if other channels remain active; this can weaken the global-parameter guard. In `tw686x_audio_irq`, `next` is only assigned when `buf_list` is non-empty, but non-memcpy mode writes `next->dma` after a done buffer is selected, so empty-list handling depends on queue invariants. `tw686x_audio_free` disables all audio DMA bits and frees the card but does not call `tw686x_audio_dma_free` for normal teardown in the shown path unless ALSA card cleanup indirectly covers only managed buffers, leaving coherent memcpy descriptors as a point to audit.

## Test Signals
Use ALSA capture on every channel at 8 kHz through 48 kHz, period sizes from 512 to 4096 bytes, and all supported period counts. Test simultaneous channels, attempts to change rate/period while another channel captures, memcpy and direct DMA modes, IRQ period cadence, pointer monotonicity, and unload/reload under active and idle audio capture.
