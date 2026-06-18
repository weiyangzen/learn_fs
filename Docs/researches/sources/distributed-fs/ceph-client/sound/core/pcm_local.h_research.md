# sources/distributed-fs/ceph-client/sound/core/pcm_local.h

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_local.h` is the private header shared by the ALSA PCM core implementation files in this directory. It exposes internal interval arithmetic, hardware constraint, pointer update, timer, XRUN, linked-group, and DMA synchronization helpers that are not part of the public ALSA PCM UAPI. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

The header declares `snd_pcm_known_rates`, interval helpers (`snd_interval_mul`, `snd_interval_div`, `snd_interval_muldivk`, `snd_interval_mulkdiv`), the internal mask constraint helper `snd_pcm_hw_constraint_mask`, application and hardware pointer helpers (`pcm_lib_apply_appl_ptr`, `snd_pcm_update_state`, `snd_pcm_update_hw_ptr`), `snd_pcm_playback_silence`, optional timer hooks, `__snd_pcm_xrun`, `snd_pcm_group_init`, and `snd_pcm_sync_stop`. Inline helpers include `snd_pcm_avail()`, `snd_pcm_hw_avail()`, `snd_pcm_dma_buffer_sync()`, `PCM_RUNTIME_CHECK`, and `for_each_pcm_substream`.

## Control Flow

This header has no standalone runtime flow. It wires call sites across `pcm_lib.c`, `pcm_native.c`, `pcm_memory.c`, `pcm_misc.c`, and `pcm_timer.c`: native ioctl/action paths call pointer and silence helpers from `pcm_lib.c`; transfer and mmap paths use `snd_pcm_dma_buffer_sync()`; open/close and suspend flows use group and sync-stop helpers; timer calls compile to real functions only under `CONFIG_SND_PCM_TIMER`.

## State and Persistence Behavior

No storage is owned by the header. The inline availability helpers read `runtime->control->appl_ptr`, `runtime->status->hw_ptr`, and stream direction indirectly through public ALSA helpers. `snd_pcm_dma_buffer_sync()` conditionally synchronizes the current runtime DMA buffer when `runtime->info` advertises `SNDRV_PCM_INFO_EXPLICIT_SYNC`.

## Dependencies and Integration Points

The header depends on public ALSA PCM definitions being available before inclusion. Its main integration role is to avoid exporting internal PCM core symbols through public headers while keeping implementation files source-compatible across optional timer builds. It also centralizes the explicit DMA sync policy used by transfer and pointer-control code.

## Risks and Edge Cases

Because this header provides inline helpers, semantic changes affect many PCM paths at once. `PCM_RUNTIME_CHECK` is intentionally a bug-on style guard and is not a substitute for full state validation. `snd_pcm_dma_buffer_sync()` assumes a valid runtime and DMA buffer, so callers must avoid using it before hw params or after detach. Availability helpers depend on correct stream direction and boundary-aware runtime pointer state.

## Test Signals

Compile coverage across `CONFIG_SND_PCM_TIMER`, `CONFIG_SND_PCM_XRUN_DEBUG`, explicit-sync DMA buffer configurations, playback and capture streams, and nonatomic PCM drivers is the key signal. Runtime transfer tests that exercise explicit sync and timer-disabled builds indirectly validate the header's inline choices.
