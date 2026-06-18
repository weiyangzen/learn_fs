# sources/distributed-fs/ceph-client/sound/drivers/aloop.c

## Purpose

This file implements the ALSA loopback PCM sound card. It creates two PCM devices whose playback side of one device feeds the capture side of the paired device, with optional jiffies timing or synchronization to an external ALSA sound timer.

## Important APIs, Types, and Functions

Important structures are `struct loopback`, `struct loopback_cable`, `struct loopback_pcm`, `struct loopback_setup`, and `struct loopback_ops`. PCM callbacks are `loopback_open()`, `loopback_close()`, `loopback_prepare()`, `loopback_trigger()`, `loopback_pointer()`, and `loopback_hw_free()`. Timer backends are represented by `loopback_jiffies_timer_ops` and `loopback_snd_timer_ops`. Mixer/proc helpers expose rate shift, notify mode, active state, captured format/rate/channels/access, cable state, and `timer_source`.

## Control Flow

Module init registers a platform driver and creates enabled platform devices. Probe allocates an ALSA card, initializes two PCM devices, creates per-substream mixer controls, creates procfs cable/timer-source entries, and registers the card. Opening a PCM substream allocates a `loopback_pcm`, creates or reuses its paired cable, selects the timer backend, installs dynamic hardware rules that mirror peer constraints, and records the stream in the cable. Prepare computes byte alignment, buffer size, period size, bytes per second, clears capture buffers, and marks stream validity. Trigger validates peer format, toggles running/pause bits, and starts or stops the backend timer. Timer callbacks update positions, copy playback data into capture buffers, fill silence when needed, and call `snd_pcm_period_elapsed()`.

## State and Persistence Behavior

Loopback state persists per card in `struct loopback`, per paired substream in `struct loopback_cable`, and per open stream in `struct loopback_pcm`. The cable tracks valid/running/pause bits, peer stream pointers, timer instance, external timer id, in-flight stop count, and shared hardware constraints. `loopback_setup` persists user-visible mixer state such as notify flag, rate shift, last playback format/rate/channels/access, and control ids for notifications. `timer_source` is devm-managed and can be changed through procfs while holding `cable_lock`.

## Dependencies and Integration Points

It depends on ALSA PCM, control, procfs, timer core, platform devices, jiffies timers, wait queues, and module parameters. It integrates directly with `sound/core/timer.c` when an external timer source is configured, and with userspace through ALSA PCM devices and mixer controls.

## Risks

The main risks are peer-stream lifetime and locking. Format changes can stop a running capture stream outside `cable->lock`, so `stop_count` and `stop_wait` must prevent cable teardown races. External sound-timer callbacks intentionally avoid taking locks in timer callback order and defer MSTOP handling to workqueue to avoid deadlocks. Non-interleaved copy logic depends on channel buffer math. Timer source parsing mutates temporary string separators and must restore them. Dynamic hardware rules must reflect peer constraints without using stale PCM midlevel cached rules.

## Test Signals

Test paired playback/capture with interleaved and non-interleaved formats, format/rate/channel mismatches, notify mode, rate-shift changes, start/stop/pause/resume/drain, capture silence when playback is absent, external `timer_source` parsing by card id/index/global id, procfs cable output, and concurrent close during forced capture stop. ALSA loopback integration tests should compare captured bytes with playback bytes across ring wrap boundaries.
