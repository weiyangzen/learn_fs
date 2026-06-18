# sources/distributed-fs/ceph-client/sound/core/oss/pcm_oss.c

## Purpose

`pcm_oss.c` implements ALSA PCM OSS emulation: the `/dev/dsp`-style character device, OSS ioctl surface, OSS-specific runtime parameter negotiation, read/write buffering, mmap behavior, procfs setup overrides, and registration hooks that attach OSS minors to ALSA PCM devices. It bridges legacy OSS applications onto ALSA `struct snd_pcm_substream` operations.

## Important APIs, Types, and Functions

The module exposes parameters `dsp_map`, `adsp_map`, and `nonblock_open`, registers `snd_pcm_oss_f_reg`, and installs `snd_pcm_oss_notify` with `snd_pcm_notify()`. `snd_pcm_oss_open()`, `snd_pcm_oss_release()`, `snd_pcm_oss_read()`, `snd_pcm_oss_write()`, `snd_pcm_oss_ioctl()`, `snd_pcm_oss_poll()`, and `snd_pcm_oss_mmap()` are the file operation entry points. Parameter helpers refine ALSA `snd_pcm_hw_params` to match OSS format/rate/channel/fragment requests. `snd_pcm_oss_change_params_locked()` is the main translation point from OSS runtime settings to ALSA `HW_PARAMS` and `SW_PARAMS`.

Data movement is split into byte-oriented OSS wrappers and frame-oriented ALSA helpers. `snd_pcm_oss_write1()` and `snd_pcm_oss_read1()` handle user buffers, partial fragments, signal interruption, nonblocking returns, and `runtime->oss.rw_ref`. `snd_pcm_oss_write2()` and `snd_pcm_oss_read2()` optionally pass through the OSS plugin chain. `snd_pcm_oss_write3()` and `snd_pcm_oss_read3()` call ALSA transfer helpers and recover from XRUN/suspend states.

## Control Flow

Open resolves the OSS minor to an ALSA PCM, applies per-task procfs setup overrides, waits for substreams unless nonblocking open is active, then opens playback and/or capture substreams. Initialization seeds OSS defaults such as 8 kHz mono, initial format by minor type, trigger enabled, and pending parameter setup. Reads, writes, ioctls, poll, and mmap force deferred parameter changes through `snd_pcm_oss_make_ready*()` before touching hardware state.

Ioctl dispatch implements classic OSS commands: reset/sync/post, speed, channels, format, fragment sizing, buffer-space queries, capabilities, trigger control, input/output pointer reporting, nonblocking mode, duplex checks, and mixer forwarding. Release syncs playback, drops capture, closes substreams, wakes open waiters, and releases module/card references.

## State and Persistence Behavior

Persistent state lives mostly in `runtime->oss`: pending params, selected rate/channels/format, period and buffer byte counts, trigger state, fragment/subdivision preferences, mmap size, software byte counters, partial-fragment buffer state, plugin list, and `params_lock`. Per-stream OSS setup lists persist under `pcm->streams[stream].oss.setup_list` and are edited through procfs when verbose procfs is enabled. Device registration state persists in `pcm->oss.reg` and `reg_mask`.

## Dependencies and Integration Points

This file depends on ALSA PCM core ioctls, `pcm_plugin.h`, OSS UAPI definitions from `linux/soundcard.h`, mixer OSS forwarding, ALSA proc/info APIs, card minor lookup, and the PCM notifier list in `pcm.c`. It integrates with plugin builders for format/rate/channel conversion when `CONFIG_SND_PCM_OSS_PLUGINS` is enabled.

## Risks and Edge Cases

The main risks are lock ordering around `params_lock`, mmap locks, and user copies; partial-fragment accounting; conversion between OSS bytes and ALSA frames when plugin sizes differ; nonblocking open/write behavior; and legacy apps that ignore errors. The mmap path intentionally uses trylock for parameter changes to avoid deadlock. Pointer and delay calculations include compatibility hacks such as `buggyptr`, capture overrun forwarding, and zeroing errors for broken `GETODELAY` consumers.

## Test Signals

Useful signals include opening `/dev/dsp` and `/dev/adsp` mappings, exercising `SNDCTL_DSP_*` ioctls, full-duplex and half-duplex open behavior, OSS mmap playback/capture, procfs setup overrides, nonblocking partial-fragment writes, XRUN recovery, and builds with and without `CONFIG_SND_PCM_OSS_PLUGINS`, `CONFIG_COMPAT`, `CONFIG_SND_VERBOSE_PROCFS`, and `CONFIG_SND_MIXER_OSS`.
