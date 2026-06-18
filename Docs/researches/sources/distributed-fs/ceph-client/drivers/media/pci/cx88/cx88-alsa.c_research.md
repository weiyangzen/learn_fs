# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-alsa.c

## Purpose
Implements ALSA PCM capture for the cx2388x audio PCI function (`14f1:8801` and `14f1:8811`). It exposes the cx88 digital/analog-TV audio stream as an ALSA capture device, programs the downstream audio SRAM/RISC DMA path, handles audio interrupts, and provides mixer controls for volume, mute, DAC output, and optional WM8775 ALC.

## Important APIs, Types, And Data
`struct cx88_audio_dev` owns the ALSA card, shared `cx88_core`, PCI device, IRQ, register lock, period counter, DMA sizing, active `cx88_audio_buffer`, and current PCM substream. `struct cx88_audio_buffer` stores bytes-per-line, RISC memory, vmalloc capture buffer, scatterlist, SG length, and page count. The ALSA callback table `snd_cx88_pcm_ops` implements open, close, hw_params, hw_free, prepare, trigger, pointer, and mmap page translation. PCI binding is through `cx88_audio_pci_driver`.

Important functions include `_cx88_start_audio_dma()`, `_cx88_stop_audio_dma()`, `cx8801_irq()`, `cx8801_aud_irq()`, `cx88_alsa_dma_init/map/unmap/free()`, `snd_cx88_hw_params()`, `snd_cx88_card_trigger()`, `snd_cx88_pointer()`, `snd_cx88_pcm()`, mixer get/put helpers, `snd_cx88_create()`, and `cx88_audio_initdev()`.

## Control Flow
Probe creates an ALSA card, enables the PCI function, obtains the shared `cx88_core` with `cx88_core_get()`, sets a 32-bit DMA mask, requests the shared IRQ, creates one capture PCM, adds mixer controls, and registers the card. Opening a substream constrains periods to powers of two and fixes the hardware format to 48 kHz stereo S16_LE. `hw_params` frees any old buffer, computes period and total DMA sizes, allocates a vmalloc_32 buffer, builds a page scatterlist, maps it for DMA, creates a RISC data-buffer program, and patches the final jump to loop with `RISC_IRQ1 | RISC_CNT_INC`.

On `SNDRV_PCM_TRIGGER_START`, `_cx88_start_audio_dma()` disables audio DMA, programs SRAM channel `SRAM_CH25`, sets `MO_AUDD_LNGTH`, resets the GP counter, enables audio interrupt bits, clears stale status, enables PCI audio interrupts, enables the RISC controller, and starts downstream FIFO/RISC DMA. The IRQ handler loops until relevant PCI status is clear or `MAX_IRQ_LOOP` is reached, routes shared core IRQs to `cx88_core_irq()`, and routes audio IRQs to `cx8801_aud_irq()`. Audio IRQ handling acknowledges status, stops DMA on RISC opcode errors, resets the counter on sync errors, and on downstream RISC1 updates `chip->count` from `MO_AUDD_GPCNT` before calling `snd_pcm_period_elapsed()`. Stop disables downstream FIFO/RISC and audio IRQ masks.

## State And Persistence
Runtime state is held in ALSA core objects, `cx88_audio_dev`, the shared `cx88_core`, DMA mappings, coherent RISC memory, and audio control registers. `atomic_t count` is the ALSA position source and depends on the hardware GP counter and period count being a power of two. `substream->runtime->dma_area` points at vmalloc memory, not PCI coherent memory; scatterlist mapping supplies the hardware addresses. Mixer state is mirrored in hardware registers `AUD_VOL_CTL` and `AUD_BAL_CTL`, with shadow writes through `cx_swrite`; optional WM8775 controls are propagated through V4L2 control calls.

## Dependencies And Integration Points
The driver integrates Linux PCI, ALSA PCM/control APIs, vmalloc/scatterlist DMA mapping, V4L2 cx88 shared core helpers, cx88 SRAM/RISC helpers, and optional `wm8775` subdevice controls. It depends on the base cx88 core already describing the board and MMIO region. It deliberately checks `MO_AUD_DMACNTRL` interactions with the common audio DMA path in `cx88-core.c`, because ALSA owns downstream RISC DMA while analog TV audio setup may enable other audio FIFOs.

## Risks And Test Signals
Risks include IRQ storms, stale DMA mappings after failed `hw_params`, period-size assumptions tied to FIFO geometry, race windows between ALSA trigger and shared IRQ handling, and mismatched WM8775/control state. The code has a FIXME asking whether volume put is always called with IRQs enabled. Test signals are ALSA card creation, successful 48 kHz stereo capture, period interrupts advancing monotonically, clean start/stop/reopen cycles, mmap capture, mixer control readback, no DMA API warnings, and no `IRQ loop detected`, sync, or RISC opcode errors under load.
