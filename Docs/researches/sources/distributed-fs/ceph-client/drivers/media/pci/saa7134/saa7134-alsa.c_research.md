# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-alsa.c

## Purpose
This file implements the optional ALSA PCM capture interface for Philips/NXP SAA713x PCI video-capture chips. It exposes the chip's DMA audio capture path as an ALSA capture-only PCM device, creates simple mixer controls for input selection and coarse volume/mute behavior, and wires the ALSA side into the main `saa7134` V4L2 driver through the global `saa7134_dmasound_init` and `saa7134_dmasound_exit` hooks.

The implementation is intentionally close to the older OSS DMA path in the same driver family. It allocates a vmalloc-backed audio buffer, maps it into a scatterlist and SAA7134 page table, programs the SAA7134 audio DMA register set, handles audio DMA interrupts, and reports period completion back to ALSA.

## Important APIs, Types, and Functions
The file's local ALSA card wrapper is `snd_card_saa7134_t`. It stores the ALSA `struct snd_card`, mixer lock and mixer state, active capture source, per-source capture controls, PCI/SAA7134 device pointers, I/O base, IRQ, and the `mute_was_on` restore flag. `snd_card_saa7134_pcm_t` is the per-open runtime object attached to `runtime->private_data`; it points back to the `saa7134_dev` and current substream.

DMA lifecycle helpers are `saa7134_dma_start()`, `saa7134_dma_stop()`, `saa7134_alsa_dma_init()`, `saa7134_alsa_dma_map()`, `saa7134_alsa_dma_unmap()`, `saa7134_alsa_dma_free()`, `dsp_buffer_init()`, and `dsp_buffer_free()`. These use `vmalloc_32()`, `vmalloc_to_page()`, `sg_init_table()`, `dma_map_sg()`, and the shared SAA7134 page-table helpers `saa7134_pgtable_alloc()`, `saa7134_pgtable_build()`, and `saa7134_pgtable_free()`.

The ALSA PCM callbacks are collected in `snd_card_saa7134_capture_ops`: `snd_card_saa7134_capture_open()`, `snd_card_saa7134_capture_close()`, `snd_card_saa7134_hw_params()`, `snd_card_saa7134_hw_free()`, `snd_card_saa7134_capture_prepare()`, `snd_card_saa7134_capture_trigger()`, `snd_card_saa7134_capture_pointer()`, and `snd_card_saa7134_page()`. The advertised hardware capabilities are in `snd_card_saa7134_capture`, which limits capture to 32 kHz, one or two channels, MMAP/interleaved/block-transfer formats, and 8/16-bit signed or unsigned PCM variants.

Mixer controls are defined by `SAA713x_VOLUME()` and `SAA713x_CAPSRC()` entries, implemented by `snd_saa7134_volume_info/get/put()` and `snd_saa7134_capsrc_info/get/put()`. `snd_saa7134_capsrc_set()` is the central control routine that updates the cached source state and programs SAA7134/SAA7133/SAA7135 audio input routing registers.

Interrupt handling is split between `saa7134_alsa_irq()` and `saa7134_irq_alsa_done()`. The IRQ handler filters shared interrupts for `SAA7134_IRQ_REPORT_DONE_RA3`, acknowledges the audio DMA done bit, and advances ring-buffer state. Card creation and teardown flow through `alsa_card_saa7134_create()`, `alsa_device_init()`, `alsa_device_exit()`, `saa7134_alsa_init()`, and `saa7134_alsa_exit()`.

## Control Flow
Module initialization is via `late_initcall(saa7134_alsa_init)`, deliberately after the sound core is available. Initialization installs `alsa_device_init` and `alsa_device_exit` into the main driver's `saa7134_dmasound_*` hooks, then walks `saa7134_devlist`. SAA7130 devices are skipped because they do not support digital audio; other present devices get an ALSA card through `alsa_card_saa7134_create()`.

Card creation checks the ALSA card index/enable arrays, allocates `struct snd_card` with `snd_card_new()`, initializes locks and chip pointers, requests the shared PCI IRQ using `devm_request_irq()`, creates mixer controls, creates one capture-only PCM device with `snd_pcm_new()`, fills card names, and calls `snd_card_register()`. On success, the card is stored in `snd_saa7134_cards[devnum]`.

Open initializes `dev->dmasound.read_count` and `read_offset`, derives the initial audio input from `dev->input->amux`, allocates the per-runtime PCM state, assigns ALSA hardware constraints, and temporarily unmutes TV audio if the V4L2 side had `ctl_mute` set. `hw_params` validates period size, period count, and total buffer size, tears down any prior runtime DMA area, allocates the vmalloc audio buffer, maps it for DMA, builds the SAA7134 DMA page table, and exposes that vmalloc buffer as ALSA's `runtime->dma_area`.

Prepare derives SAA7134 format bits from ALSA format, signedness, endian, channel count, and the selected input. It programs either SAA7134 audio registers or SAA7133/SAA7135 audio registers, writes DMA channel 6 base addresses, pitch, and control bits, stores the runtime rate, and forces the cached ALSA capture source control to match `dev->dmasound.input`. Trigger only starts or stops the audio DMA under `dev->slock`; actual hardware setup happened in prepare.

On each RA3 audio DMA interrupt, `saa7134_irq_alsa_done()` validates the expected odd/even block transition, logs lost IRQ status bits, detects ring overrun using `read_count`, schedules the next block address into `SAA7134_RS_BA1/BA2(6)`, advances `dma_blk`, increments `read_count`, records the active register, and calls `snd_pcm_period_elapsed()` once enough bytes have accumulated. The ALSA pointer callback subtracts one period from `read_count`, advances `read_offset`, wraps at `bufsize`, and returns the current frame position.

Close restores mute if open had cleared it. `hw_free` and `alsa_device_exit` tear down page tables, DMA mappings, vmalloc buffers, and ALSA card registration.

## State and Persistence
All persistent state is in kernel memory and device registers; nothing is saved across driver unload or reboot. Global module parameters `index[]` and `enable[]` control ALSA card allocation. `snd_saa7134_cards[]` tracks registered ALSA cards by SAA7134 device number.

Per-device audio state is mostly shared through `dev->dmasound`: block size/count, buffer size, vmalloc address, scatterlist, DMA sg length, SAA7134 page table, current DMA block, read offset/count, selected input, current ALSA substream, DMA running flag, and a mutex used around open-time state initialization. `dev->slock` protects IRQ and trigger DMA fields. Mixer state lives in `snd_card_saa7134_t` and is protected by `mixer_lock`; it caches per-source volume, active capture source address, and left/right boolean source state.

Hardware state programmed by this file includes audio format registers, SIF sample frequency, analog I/O selection, SAA7133 digital input/output crossbars, DMA channel 6 base/pitch/control registers, and the main driver's DMA enable bits via `saa7134_set_dmabits()`. The `mute_was_on` flag is a per-card transient used to restore V4L2 mute state after capture closes.

## Dependencies and Integration Points
This file depends on `saa7134.h` and `saa7134-reg.h` for device structures, register constants, `saa_readl/writel/writeb/andorb/andorl`, `saa_dsp_writel()`, `saa7134_set_dmabits()`, `saa7134_pgtable_*()`, `saa7134_tvaudio_setmute()`, `saa7134_boards[]`, and the global device list. It integrates with ALSA core through card, PCM, mixer-control, PCM-ops, period-elapsed, XRUN, and mmap page APIs.

It uses the Linux DMA mapping API for `DMA_FROM_DEVICE`, vmalloc helpers for audio buffer pages, PCI device IDs to distinguish SAA7134 from SAA7133/SAA7135 register programming, and shared PCI interrupts. It also relies on the V4L2-side SAA7134 input model because `dev->input->amux` seeds the ALSA capture source.

## Risks and Edge Cases
The DMA buffer is vmalloc-backed and exposed to ALSA by overriding `runtime->dma_area`, while the hardware uses a separately built SAA7134 page table. That is deliberate but fragile: buffer-size validation, scatterlist construction, DMA mapping, and page-table teardown must stay exactly paired or capture can corrupt memory or leak mappings.

The IRQ and pointer logic uses `read_count` as an overrun and period accounting counter. The IRQ side updates it under `dev->slock`, while `snd_card_saa7134_capture_pointer()` updates it without taking that lock, so races are possible if ALSA pointer callbacks interleave with audio interrupts. Overrun handling calls `snd_pcm_stop_xrun()` after dropping the spinlock and returns without the final unlock path, which is intentional but easy to break.

Source and volume controls are coarse hardware switches rather than true gain controls. TV tuner volume is forced to 20, line volume maps around a threshold into mute/enable bits, and capture-source controls prevent deactivating the active source. User-space mixer behavior may therefore look unlike a normal ALSA mixer.

Rate handling is constrained to 32 kHz even though some line-input register paths include 48 kHz comments and encodings. The fixed rate avoids silent source-switch resampling problems, but any change to advertised rates must re-audit SAA7133/35 DDEP mode, TV/radio paths, and source switching. The initial `amux` conversion clamps invalid or out-of-range values to line 1, which can hide bad board definitions.

`alsa_device_init()` always returns 1 and ignores the error from `alsa_card_saa7134_create()`, so initialization failures may only be visible through logs. Device numbers beyond `SNDRV_CARDS` are rejected, and `dev->nr` is used as an index into `snd_saa7134_cards[]`; any mismatch between SAA7134 numbering and ALSA card capacity is a functional limit.

## Test Signals
Build signals include compiling this file with ALSA enabled, SAA7134 core symbols available, and no missing references to the V4L2-side DMA/page-table helpers. Runtime registration should log the ALSA driver load message and one card registration per non-SAA7130 SAA7134/SAA7133/SAA7135 device, with `/proc/asound/cards` and ALSA control enumeration showing the SAA7134 PCM and mixer controls.

Functional tests should open the capture PCM at 32 kHz with supported 8/16-bit, signed/unsigned, little/big-endian, mono/stereo formats; mmap the buffer; vary period sizes/counts at boundary values; start/stop repeatedly; and verify period interrupts advance monotonically without XRUN under normal load. Source-switch tests should cover TV tuner, line 1, line 2, mute restore, and V4L2 input changes before ALSA open. Hardware tests should watch `SAA7134_IRQ_REPORT_DONE_RA3`, lost-interrupt logging, overrun handling, and audio route behavior separately on SAA7134 and SAA7133/SAA7135 chips.
