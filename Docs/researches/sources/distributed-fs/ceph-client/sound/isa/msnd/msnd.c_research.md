# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.c

## Purpose
`msnd.c` provides common ALSA support routines for Turtle Beach MultiSound cards. It implements host-to-DSP command transfer, shared SRAM queue setup, IRQ reference management, DSP halt/flush helpers, and ALSA PCM playback/capture operations used by the board driver in `msnd_pinnacle.c` and the Classic wrapper build.

## Important APIs, Types, and Functions
- Exported hardware helpers: `snd_msnd_init_queue`, `snd_msnd_send_dsp_cmd`, `snd_msnd_send_word`, `snd_msnd_upload_host`, `snd_msnd_enable_irq`, `snd_msnd_disable_irq`, `snd_msnd_force_irq`, `snd_msnd_dsp_halt`, `snd_msnd_DAPQ`, `snd_msnd_DARQ`, and `snd_msnd_pcm`.
- Queue helpers program DSP-visible queue structures with `JQS_*` fields and address conversion macros from `msnd.h`.
- PCM operations are split into `snd_msnd_playback_ops` and `snd_msnd_capture_ops`, both using I/O memory mmap through `snd_pcm_lib_mmap_iomem`.
- `snd_msnd_DAPQ` submits playback banks to the DSP and sends `HDEX_PLAY_START`; `snd_msnd_DARQ` advances capture queue tails and adjusts two-period capture buffer offsets.

## Control Flow
Playback open sets `F_AUDIO_WRITE_INUSE`, enables IRQs, maps runtime DMA to `chip->mappedbase`, and installs hardware constraints. `hw_params` stores sample width/channels/rate into the three playback DAQ descriptors. `prepare` rewrites playback queue descriptors for the current buffer and period layout. `trigger(START)` marks `F_WRITING` and primes the DSP queue; later DSP interrupts call `snd_msnd_DAPQ` again through `msnd_pinnacle.c`. Stop clears `F_WRITING` and sends `HDEX_PLAY_STOP`.

Capture open similarly enables IRQs and maps runtime DMA to `mappedbase + 0x3000`; `prepare` rewrites capture descriptors, and `trigger(START)` sends `HDEX_RECORD_START`. Stop sends `HDEX_RECORD_STOP`.

Command flow is mostly polling-based: `snd_msnd_send_dsp_cmd` waits for host-command bit `HPCVR_HC` to clear before writing `HP_CVR`; `snd_msnd_send_word` waits for `HPISR_TXDE` then writes high/mid/low bytes to the transmit ports.

## State and Persistence
Runtime state is held in `struct snd_msnd`: flags such as `F_WRITING` and `F_READING`, IRQ reference count, current PCM format, queue pointers, last bank numbers, and DMA-position counters. No persistent disk state exists. Hardware state lives in ISA I/O ports and mapped SRAM queues and is rebuilt during prepare/reset paths.

## Dependencies and Integration Points
This file depends on ALSA core/PCM APIs, Linux I/O port helpers, `msnd.h` register definitions, and board-specific setup that initializes `mappedbase`, queue pointers, IRQs, and DSP firmware. It is consumed by `msnd_pinnacle.c` and mixer code via exported symbols.

## Risks and Test Signals
Risks include polling timeouts with no delays in `snd_msnd_wait_TXDE`/`snd_msnd_wait_HC0`, IRQ reference underflow only logged in `snd_msnd_disable_irq`, and careful reliance on two or three SRAM queue banks. PCM tests should check playback/capture open-close balance, start/stop/suspend triggers, mmap I/O memory behavior, IRQ enable/disable pairing, period elapsed progression, firmware upload failure behavior, and buffer wrap for two-period and three-period configurations.
