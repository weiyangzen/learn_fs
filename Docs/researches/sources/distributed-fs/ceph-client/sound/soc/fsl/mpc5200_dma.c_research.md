# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.c

## Purpose
ASoC PCM/DMA backend for Freescale MPC5200 PSC audio using BestComm DMA tasks. It handles fixed ALSA buffers, BestComm buffer descriptor cycling, period notifications, PSC error accounting, and component registration for PSC-based I2S/AC97 drivers.

## APIs, Types, and Functions
Exports `mpc5200_audio_dma_create()` and `mpc5200_audio_dma_destroy()`. Important internals include `psc_dma_status_irq()`, `psc_dma_bcom_enqueue_next_buffer()`, `psc_dma_bcom_irq()`, `psc_dma_trigger()`, `psc_dma_open()`, `psc_dma_close()`, `psc_dma_pointer()`, and `psc_dma_new()`. It registers `mpc5200_audio_dma_component`.

## Control Flow, State, and Persistence
Create maps PSC registers, reads `cell-index`, allocates `struct psc_dma`, initializes locks, BestComm RX/TX tasks, resets PSC state, programs FIFO alarms, requests PSC status and BestComm IRQs, stores drvdata, and registers the component. START initializes period indexes, resets the relevant task, queues period buffers until the BestComm queue is full, enables DMA, and clears PSC errors. BestComm IRQs dequeue completed buffers, enqueue replacements, advance `period_current`, and call `snd_pcm_period_elapsed()` when active. STOP disables and resets the task. Pointer reports `period_current * period_bytes`.

## Dependencies and Integration
Depends on OF address/IRQ parsing, MPC52xx PSC register definitions, BestComm APIs, ALSA SoC component callbacks, and `mpc5200_dma.h`. Used by `mpc5200_psc_ac97.c` and `mpc5200_psc_i2s.c`.

## Risks and Test Signals
Risks include manual `kzalloc` lifetime combined with devm component registration, OR-combined `request_irq` return values obscuring which IRQ failed, queue depth assumptions versus ALSA period count, pointer granularity only at completed periods, and shared PSC status IRQ handling. Test signals are create/destroy without leaks, BestComm IRQ cadence, underrun/overrun counters, correct pointer movement, fixed buffer allocation, and playback/capture on MPC5200 PSC hardware.
