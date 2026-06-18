# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emupcm.c

## Purpose
`emupcm.c` implements the ALSA PCM surfaces for EMU10K1/EMU10K2-family cards: standard voice playback plus AC97 ADC capture, multi-channel EFX playback/capture, mic capture, and legacy FX8010 TRAM playback. It bridges ALSA substream callbacks to the EMU voice allocator, page table memory mapper, FX routing mixer state, capture engines, and interrupt callbacks in `irq.c`.

## Important APIs, Types, and Functions
The exported entry points are `snd_emu10k1_pcm()`, `snd_emu10k1_pcm_multi()`, `snd_emu10k1_pcm_mic()`, and `snd_emu10k1_pcm_efx()`, each creating an ALSA `struct snd_pcm` device and installing `struct snd_pcm_ops`. Runtime-private state is `struct snd_emu10k1_pcm`, which tracks the owning `emu`, stream type, allocated voices, extra IRQ voice, mapped memory block, start address, capture registers, running flag, and resume position. Normal playback uses `snd_emu10k1_playback_*`; capture uses `snd_emu10k1_capture_*`; EFX playback has separate synchronized trigger logic; FX8010 playback uses `struct snd_emu10k1_fx8010_pcm` and ALSA indirect playback helpers.

## Control Flow
Open allocates `epcm`, assigns hardware capabilities, constrains rates/periods, and activates mixer controls. `hw_params` allocates EMU voices, ALSA SG pages, and an EMU PTB mapping through `snd_emu10k1_alloc_pages()`. `prepare` writes voice routing, loop bounds, interpolation, capture buffer base/size, and sample-rate fields. `trigger` starts or stops hardware by enabling voice/capture interrupts, writing pitch targets, unmuting or muting attenuation registers, and setting capture buffer-size registers. `pointer` reads hardware current-address registers and compensates for the 64-frame cache and interpolation lookahead. IRQ handlers installed in `emu` call `snd_pcm_period_elapsed()`.

## State and Persistence
No durable state is persisted. Active state lives in ALSA runtime private data, `emu->pcm_mixer[]`, `emu->efx_pcm_mixer[]`, `emu->efx_voices_mask[]`, callback pointers such as `emu->capture_interrupt`, voice dirty/use flags, and hardware registers. Close/open toggles control visibility via `snd_ctl_notify()`. `resume_pos` is retained across EFX stop/suspend trigger transitions to restart from the previous position.

## Dependencies and Integration Points
This file depends on core ALSA PCM helpers, `sound/emu10k1.h` register definitions, `voice.c` allocation, `memory.c` PTB mapping, `io.c` pointer-register writes and interrupt enables, mixer controls from `emumixer.c`, and `irq.c` callback dispatch. E-MU models use `emu->emu1010.word_clock` to constrain rates and adjust 44.1 kHz clocking. FX8010 playback integrates with `snd_emu10k1_fx8010_register_irq_handler()` and TRAM/GPR registers.

## Risks
The logic is timing-sensitive. Normal playback relies on an extra voice for period interrupts and compensates for cache behavior; changes to pitch, cache, or loop setup can create underruns or incorrect positions. EFX playback attempts an atomic multi-voice start using loop-stop bits and can fail with `-EAGAIN` under interruption. Capture has fixed two-period buffer-size constraints and a `udelay(50)` first-pointer workaround. Voice and mixer state must be torn down exactly once, or IRQ callbacks can observe stale substreams. EFX capture mask validation rejects unsupported channel counts; bypassing it can create broken ALSA hardware declarations.

## Test Signals
Exercise playback and capture open/hw_params/prepare/trigger/pointer paths with 8-bit, S16_LE, mono, stereo, and EFX multi-channel modes. Verify period interrupts advance with no missed callbacks, suspend/resume triggers preserve or reset position as intended, and mixer controls become inactive on close. For E-MU cards, test both 44.1 kHz and 48 kHz word-clock modes. Useful signals are `aplay`/`arecord` stability, ALSA PCM pointer monotonicity, `snd_pcm_period_elapsed()` cadence, and absence of stale IRQ callbacks after stream close.
