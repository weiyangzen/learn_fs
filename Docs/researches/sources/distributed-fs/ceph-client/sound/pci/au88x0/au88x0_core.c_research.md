# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_core.c

## Purpose
Contains the low-level Aureal Vortex hardware engine: mixer, sample-rate converters, FIFO control, ADB and WT DMA setup, ADB route graph, codec access, SPDIF setup, interrupt handling, resource management, and top-level core init/shutdown. Most routines are reverse-engineered from Aureal binary drivers and are internal to the au88x0 driver.

## Important APIs, Types, And Functions
Mixer functions manage input/output gains and route tables: `vortex_mix_setvolumebyte`, `vortex_mix_setinputvolumebyte`, `vortex_mix_enableinput`, `vortex_mix_disableinput`, `vortex_mixer_addWTD`, `vortex_mixer_delWTD`, and `vortex_mixer_init`. SRC functions include `vortex_src_setupchannel`, `vortex_src_addWTD`, `vortex_src_delWTD`, and `vortex_adb_setsrc`. FIFO/DMA functions include `vortex_fifo_setadbctrl`, `vortex_fifo_setwtctrl`, `vortex_adbdma_setbuffers`, `vortex_adbdma_setmode`, `vortex_adbdma_bufshift`, `vortex_adbdma_getlinearpos`, and equivalent WT DMA helpers. Routing/resource functions include `vortex_adb_init`, `vortex_route`, `vortex_routeLRT`, `vortex_connection_*`, `vortex_adb_checkinout`, `vortex_connect_default`, and `vortex_adb_allocroute`. Device lifecycle functions are `vortex_core_init`, `vortex_core_shutdown`, `vortex_interrupt`, `vortex_codec_read`, `vortex_codec_write`, `vortex_spdif_init`, and `vortex_alsafmt_aspfmt`.

## Control Flow
Probe code outside this file calls `vortex_core_init()`, which resets the chip, initializes the AC97 codec bus, clears IRQ state, initializes ADB DMA/FIFO/mixer/SRC blocks, programs EQ/SPDIF/A3D/WT where supported, sets the timer period, and initializes the spinlock. Default playback/capture/SPDIF/WT/A3D routes are created later through `vortex_connect_default()`. PCM hw_params calls `vortex_adb_allocroute()` to allocate DMA/SRC/mixer/A3D resources and install routes. PCM prepare calls `vortex_adbdma_setmode()` and `vortex_adb_setsrc()`. PCM trigger uses the FIFO start/pause/resume/stop helpers. IRQ handling acknowledges Vortex IRQ source bits, reports hardware errors, advances active DMA windows with `vortex_adbdma_bufshift()`/`vortex_wtdma_bufshift()`, and calls `snd_pcm_period_elapsed()`.

## State And Persistence
Driver state lives in `vortex_t` stream arrays (`dma_adb`, `dma_wt`), fixed resource bitmaps, mixer IDs, period tracking fields, SPDIF rate, codec pointer, and spinlock. Static `mchannels` and `rampchs` track mixer input enables across the driver instance and are reset by `vortex_mixer_init()`. DMA routines maintain virtual/real period positions and page-table refresh state for buffers with more than four periods. All state is volatile and rebuilt after init; MMIO state is explicitly cleared during shutdown.

## Dependencies And Integration Points
This file depends on `au88x0.h` for register constants, macros, `vortex_t`, `stream_t`, resource IDs, chip feature macros, and `hwwrite`/`hwread`. It also calls EQ, A3D, WT, ALSA AC97, ALSA PCM, MPU401, and kernel IRQ APIs. PCM, mixer, gameport, MIDI, and synth files rely on its static helpers because the driver is built by including implementation fragments.

## Risks
The resource allocator has complex rollback paths; several failure branches clear resource bitmaps without undoing routes already installed. DMA page shifting assumes hardware subbuffer reporting and powers-of-two period sizes; off-by-one errors would surface as period skips or stale DMA addresses. `mchannels`/`rampchs` are static globals, so multiple cards may share mixer bookkeeping. Many magic constants and chip-specific `#ifdef`s are reverse-engineered. IRQ handling calls period callbacks while temporarily dropping the spinlock; stream teardown races must be controlled by ALSA lifecycle locks. Codec polling has finite lifeboat loops and returns `0xffff` on read failure.

## Test Signals
Core tests require real or emulated AU88x0 hardware: init/shutdown without IRQ storms, AC97 read/write success, playback/capture at supported rates, SPDIF rate changes, quad-output routing, A3D/WT route allocation, and MIDI interrupts. Stress useful signals include long playback with many periods, simultaneous capture/playback, open/close churn, and no `lifeboat overflow`, `Src cvr fail`, FIFO, DMA, or fatal IRQ errors in dmesg.
