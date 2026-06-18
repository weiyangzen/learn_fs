# sources/distributed-fs/ceph-client/sound/sh/aica.c

## Purpose
`aica.c` is the ALSA PCM driver for the Sega Dreamcast Yamaha AICA sound processor. It creates a simple platform device, loads `aica_firmware.bin` into SPU memory, manages the ARM7/SPU control area, feeds playback data through the SH DMA API, and exposes basic PCM playback controls.

## Important APIs, Types, And Functions
Important functions include `spu_write_wait()`, `spu_memset()`, `spu_memload()`, `spu_disable()`, `spu_enable()`, `spu_reset()`, `aica_chn_start()`, `aica_chn_halt()`, `aica_dma_transfer()`, `run_spu_dma()`, `aica_period_elapsed()`, `snd_aicapcm_pcm_open()`, `snd_aicapcm_pcm_prepare()`, `snd_aicapcm_pcm_trigger()`, `snd_aicapcm_pcm_pointer()`, `snd_aicapcmchip()`, `load_aica_firmware()`, `snd_aica_probe()`, `aica_init()`, and `aica_exit()`. State comes from `struct snd_card_aica` and `struct aica_channel` in `aica.h`.

## Control Flow
Module init registers a platform driver, creates a matching platform device with ARM control and sound RAM resources, resets the SPU, requests firmware, copies it into SPU memory, and enables the ARM7. Probe allocates the ALSA card, initializes work and timer, creates a playback-only PCM, adds mixer controls, and registers the card. PCM open allocates an AICA channel descriptor and enables the SPU. Start schedules DMA work and a timer. The first work run copies the full buffer, uploads channel control, starts playback, then later timer callbacks compare the SPU sample counter with `current_period`, schedule period DMA, call `snd_pcm_period_elapsed()`, and rearm while running.

## State And Persistence
Persistent runtime state includes the global platform device pointer, module parameters, firmware-loaded SPU memory, `snd_card_aica`, the active channel descriptor, `substream`, DMA click counters, period timer, work item, `master_volume`, and `dma_check`. Playback data is staged in ALSA continuous DMA memory then copied into AICA sound RAM per period.

## Dependencies And Integration Points
The driver depends on Dreamcast memory-mapped constants, `mach/sysasic.h`, SH DMA functions `dma_xfer()` and `dma_wait_for_completion()`, the firmware loader, ALSA PCM/control APIs, timers, workqueues, and module firmware packaging for `aica_firmware.bin`.

## Risks And Edge Cases
The code uses fixed physical addresses and local IRQ masking around SPU writes. FIFO waits have a timeout warning but continue. The timer/work path assumes `substream` remains valid while synchronized by `.sync_stop`; incorrect ordering can race close. Mixer volume cannot be used before channel allocation and returns `-ETXTBSY`. `aica_init()` returns firmware-load errors after registering the platform device, so init unwinding deserves attention.

## Test Signals
High-value signals include firmware missing/present boot paths, PCM open/prepare/start/stop/close, period elapsed cadence at supported rates/formats/channels, DMA error injection, `.sync_stop` race testing, volume control before and during playback, and module unload confirming playback halt and SPU reset.
