# sources/distributed-fs/ceph-client/sound/soc/renesas/dma-sh7760.c

Purpose: implements the SH7760 “Camelot” DMABRG PCM platform component for ALSA, using fixed DMABRG audio DMA registers and IRQs for two audio units.

Important functions and types: `struct camelot_pcm` tracks MMIO base, IRQ base, current substreams, period sizes, and half-buffer period toggles. `camelot_pcm_open()` installs hardware constraints and requests two DMABRG IRQs per direction. `camelot_prepare()` writes DMA area/length to DMABRG registers. `camelot_trigger()` starts/stops playback or capture engines. `camelot_pos()` reports position by toggled period rather than hardware pointer. `camelot_pcm_new()` allocates continuous DMA buffers.

Control flow: open selects unit by CPU DAI ID and direction, assigns callback substream, and requests IRQs. hw_params records period size. prepare programs base/length. trigger flips DMABRG control bits. IRQ callbacks toggle period and call `snd_pcm_period_elapsed()`. close frees IRQs.

State and persistence: global `cam_pcm_data[2]` stores per-unit runtime state and fixed physical MMIO addresses. State survives between opens within module lifetime but is reset by open/hw_params.

Dependencies and integration: depends on SuperH `asm/dmabrg.h`, direct uncached register access through fixed addresses, ASoC component callbacks, and platform driver `sh7760-pcm-audio`.

Risks: little-endian-only FIXME, fixed physical addresses, direct `runtime->dma_area` register programming instead of DMA address, and no locking around global per-unit state. Position is approximate by design.

Test signals: two-period PCM playback/capture, DMABRG half/full IRQs, no fast-playback regression under load, correct IRQ free on close, and mmap playback using continuous buffers.
