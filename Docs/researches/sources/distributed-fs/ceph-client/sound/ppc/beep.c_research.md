# sources/distributed-fs/ceph-client/sound/ppc/beep.c

## Purpose

This file implements the optional PowerMac input-subsystem bell/tone device using the normal audio playback DBDMA path. It synthesizes a small stereo waveform into a coherent DMA buffer and exposes an ALSA mixer control for beep volume.

## Important APIs, types, and functions

`struct pmac_beep` stores running state, volume, cached tone parameters, waveform buffer, DMA address, and input device. `snd_pmac_attach_beep()` allocates state, coherent waveform memory, an input device, and `Beep Playback Volume`. `snd_pmac_beep_event()` handles `EV_SND` `SND_BELL` and `SND_TONE`. `snd_pmac_beep_stop()` and `snd_pmac_detach_beep()` are called from PCM start, suspend/free, and detach paths.

## Control flow

Attach registers an input device named `PowerMac Beep`. On a nonzero tone request, the handler validates frequency against the selected sample rate, refuses to run while playback/capture/beep are active, regenerates the waveform if frequency or volume changed, and starts looped DMA through `snd_pmac_beep_dma_start()`. A zero tone stops DMA under `reg_lock`.

## State and persistence behavior

Beep state persists under `chip->beep`. The waveform cache avoids recomputation for repeated same-frequency/same-volume tones. The beep shares playback DMA, so starting normal PCM calls `snd_pmac_beep_stop()` first.

## Dependencies and integration points

It depends on input core, ALSA controls, coherent DMA allocation, `snd_pmac_rate_index()`, and beep DMA helpers implemented in `pmac.c`. It is optionally attached by `powermac.c` via the `enable_beep` module parameter.

## Risks and test signals

Risks include playback/beep contention, invalid frequency fallback, DMA buffer lifetime during input unregister, and spinlock interactions around event callbacks. Test bell and tone events, volume changes, concurrent PCM playback/capture suppression, module removal, and suspend while a beep is active.
