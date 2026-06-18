# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.h

## Purpose
Defines shared constants, timing calculations, state, and cross-file prototypes for the PC speaker ALSA driver.

## Important APIs, Types, And Functions
Macros derive PIT dividers, sample rates, hrtimer periods, buffer limits, and pointer increments: `DIV_18KHZ`, `PCSP_DEFAULT_SRATE`, `PCSP_RATE()`, `PCSP_PERIOD_NS()`, `PCSP_BUFFER_SIZE`, and related limits. `struct snd_pcsp` stores ALSA card/PCM/input pointers, hrtimer, port metadata, playback substream, sample format state, playback/period pointers, timer-active flag, PIT port latch state, and mixer flags. It declares `pcsp_chip`, `pcsp_do_timer()`, `pcsp_sync_stop()`, `snd_pcsp_new_pcm()`, and `snd_pcsp_new_mixer()`.

## Control Flow
The header has no executable flow but its macros determine runtime hrtimer cadence and PCM hardware constraints used by `pcsp.c` and `pcsp_lib.c`.

## State And Persistence
No state is stored in the header, but it defines the global runtime object layout. The driver persists nothing to disk.

## Dependencies And Integration
Includes hrtimer, i8253, and timex kernel headers and is included by platform, PCM, mixer, and input implementation files.

## Risks And Test Signals
Timing macros depend on integer arithmetic and PIT constants; mistakes affect sample rate, hrtimer period, and buffer pointer advancement. Build-time tests catch prototype drift; runtime tests should verify reported PCM rate, period constraints, and pointer movement at default treble settings.
