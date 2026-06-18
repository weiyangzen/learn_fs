# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.c

## Purpose

This file creates ALSA PCM devices for ctxfi and bridges PCM operations to ATC playback, capture, SPDIF passthrough, and timer resources.

## Important APIs, types, and functions

The public API is `ct_alsa_pcm_create()`. Static hardware descriptors define normal playback, SPDIF passthrough playback, and capture constraints. PCM callbacks include open/close, hw_params/hw_free, prepare, trigger, and pointer functions for playback and capture. `ct_atc_pcm_interrupt()` calls `snd_pcm_period_elapsed()` for timer callbacks, and `ct_atc_pcm_free_substream()` releases ATC resources plus the timer instance.

## Control flow

Open allocates `ct_atc_pcm`, selects the correct runtime hardware descriptor, applies period/buffer constraints, creates a timer instance, and stores private data. Prepare asks ATC to allocate/configure hardware resources. Trigger starts/stops ATC streams. Pointer queries ATC byte positions and converts to frames. `ct_alsa_pcm_create()` creates playback/capture counts per logical device, attaches ops, installs SG buffers, and adds channel maps.

## State and persistence behavior

Per-substream state lives in `struct ct_atc_pcm`, runtime private data, timer instance, and ATC-allocated hardware resources. IEC958 opens enable SPDIF passthrough and close disables it. PM stores PCM pointers in `atc->pcms[]` when enabled.

## Dependencies and integration points

It depends on `ctatc.h`, `cttimer.h`, ALSA PCM APIs, SG DMA allocation, and channel-map helpers. ATC implements all actual resource allocation, transport start/stop, and position reporting.

## Risks and test signals

Risks include accepting unsupported trigger commands as success, position wrap to zero when exceeding buffer size, resource leaks if prepare partially fails in ATC, SPDIF passthrough state stuck on close errors, and channel-map mismatches. Tests should open all logical PCM devices, validate constraints with `aplay`/`arecord`, exercise pause/resume/stop, verify period interrupts, and check SPDIF passthrough formats.
