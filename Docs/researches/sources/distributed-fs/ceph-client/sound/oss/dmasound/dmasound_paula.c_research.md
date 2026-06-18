# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_paula.c

## Purpose

`dmasound_paula.c` is the Amiga Paula low-level backend for the legacy dmasound OSS core. It maps the core's generic queue, mixer, and format requests onto Amiga chip RAM allocation, Paula audio DMA registers, Amiga audio interrupt handling, volume/low-pass-filter control, and sample-layout conversion for 8-bit and pseudo-14-bit playback.

## Important APIs, Types, and Functions

The file defines `machAmiga`, `def_hard`, and `def_soft`, then installs them in `amiga_audio_probe()` before calling `dmasound_init()`. The module is a platform driver named `amiga-audio` via `module_platform_driver_probe()`.

Key callbacks are `AmiAlloc()`, `AmiFree()`, `AmiIrqInit()`, `AmiIrqCleanUp()`, `AmiInit()`, `AmiSilence()`, `AmiSetFormat()`, `AmiSetVolume()`, `AmiSetTreble()`, `AmiPlay()`, `AmiWriteSqSetup()`, `AmiMixerInit()`, `AmiMixerIoctl()`, and `AmiStateInfo()`. Sample translation is represented by `transAmiga`, with direct signed-8 copy and generated converters for mu-law, A-law, unsigned 8-bit, and 16-bit big/little endian signed/unsigned input.

## Control Flow

Probe copies the machine descriptor into `dmasound.mach`, sets defaults, and enters the core init path. IRQ setup stops all Paula audio DMA through `StopDMA()` and requests `IRQ_AMIGA_AUD0`. Core writes call `AmiInit()` during queue setup, which silences DMA, computes an Amiga audio period from `amiga_colorclock / soft.speed - 1`, clamps it to `amiga_audio_min_period..65535`, copies soft settings to hard settings, installs `transAmiga`, writes Paula `audper` for all four channels, and updates `amiga_audio_period`.

`AmiPlay()` controls two-stage frame loading. It disables the Paula audio interrupt while inspecting queue state, refuses to queue a partial fragment unless syncing/posting, and calls `AmiPlayNextFrame()` when enough queued data exists. `AmiPlayNextFrame()` maps a queued buffer into Paula channel addresses and lengths. For 8-bit output it uses channels 0/1. For 16-bit pseudo-14-bit output it splits high and low six-bit data over four channels and only enables channels 2/3 when both volumes are at full scale. `AmiInterrupt()` advances active loaded/playing flags, decrements queue count after a frame completes, wakes writers, queues the next frame if available, stops DMA when drained, and wakes sync waiters.

## State and Persistence

Persistent state is module-global and hardware-register state: `write_sq_block_size_half`, `write_sq_block_size_quarter`, optional `saved_heartbeat`, Paula channel volumes/periods/locations/lengths, `amiga_audio_period`, and `dmasound.volume_left/right` plus `dmasound.treble`. Buffer allocation uses `amiga_chip_alloc()` because Paula DMA requires chip-addressable memory. There is no persistent storage outside hardware and process lifetime.

## Dependencies and Integration Points

This backend depends on Amiga architecture headers, `amiga_custom`, CIA register access for the low-pass filter, `amiga_chip_alloc/free`, `ZTWO_PADDR`, Amiga IRQ numbers, and the machine heartbeat callback when `CONFIG_HEARTBEAT` is enabled. It integrates with the core through `MACHINE` callbacks and consumes the exported mu-law/A-law conversion tables from `dmasound_core.c`.

## Risks and Edge Cases

Heartbeat and Paula low-pass/power LED use the same line, so playback disables heartbeat and restores it on DMA stop. Pseudo-14-bit output only works at maximum volume; lower volume silently disables low-bit channels. The translation functions deliberately operate on complete sample units and may leave trailing bytes for user space to retry. `AmiStateInfo()` guards only after using `sprintf()` and relies on the caller-provided space. Hardware period clamping means requested sample rates above Paula capability are reported through adjusted hard speed, while user-visible soft speed remains request-oriented until core state is refreshed.

## Test Signals

Build-test with Amiga dmasound enabled, platform probe/remove, chip-RAM allocation failure, IRQ request failure, 8-bit mono/stereo playback, 16-bit pseudo-14-bit playback at full and non-full volume, `/dev/mixer` volume/treble reads and writes, `/dev/sndstat` low-level volume output, sync drain wakeups, and heartbeat restore after playback stop.
