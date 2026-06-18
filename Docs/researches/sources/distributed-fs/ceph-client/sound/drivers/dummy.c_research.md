# sources/distributed-fs/ceph-client/sound/drivers/dummy.c

## Purpose

This file implements the ALSA dummy sound card, a virtual `/dev/null`-style card for testing ALSA PCM and mixer behavior. It exposes configurable PCM devices/substreams, optional hardware-profile constraints, fake or real buffers, timer-driven PCM position advancement, and dummy mixer controls.

## Important APIs, Types, and Functions

Important structures are `struct snd_dummy`, `struct dummy_model`, `struct dummy_timer_ops`, `struct dummy_systimer_pcm`, and, when high-resolution timers are enabled, `struct dummy_hrtimer_pcm`. PCM callbacks are `dummy_pcm_open()`, `dummy_pcm_close()`, `dummy_pcm_prepare()`, `dummy_pcm_trigger()`, `dummy_pcm_pointer()`, `dummy_pcm_hw_params()`, and optional fake-buffer copy/silence/page callbacks. Mixer callbacks implement volume, capture-source, and external I/O box controls. Probe/init functions are `snd_dummy_probe()`, `snd_card_dummy_pcm()`, `snd_card_dummy_new_mixer()`, and `alsa_card_dummy_init()`.

## Control Flow

Module init registers a platform driver, allocates fake pages when requested, and creates enabled platform devices. Probe creates an ALSA card, applies a named dummy hardware model if configured, creates requested PCM devices, adjusts hardware constraints, creates mixer controls, optionally exposes debug procfs hardware fields, and registers the card. PCM open chooses hrtimer or system timer ops, allocates per-substream timer state, applies model constraints, and adjusts interleaved/mmap capabilities by PCM device number. Trigger starts or stops the selected timer; prepare initializes period timing; pointer calculates current frame position from jiffies or monotonic hrtimer time.

## State and Persistence Behavior

Card state persists in `struct snd_dummy`, including current PCM hardware template, model pointer, mixer volumes, capture source bits, external I/O state, and references to CD controls. Per-substream timer state persists in `runtime->private_data`. Fake-buffer mode uses two global zero pages, one per stream, and reports `runtime->dma_bytes` manually for mmap. Debug procfs can mutate fields of `dummy->pcm_hw` at runtime when enabled.

## Dependencies and Integration Points

It depends on ALSA core, PCM, rawmidi headers, controls, TLV, procfs, platform devices, jiffies timers, hrtimers, and module parameters. Kconfig builds it through `CONFIG_SND_DUMMY`, and userspace sees standard ALSA PCM/mixer devices.

## Risks

Timer correctness affects PCM period wakeups and pointer monotonicity. The hrtimer start path sets running after starting the timer, so callback ordering is subtle. Fake buffer mmap maps the same page repeatedly, intentionally discarding all data; users must not infer real buffering. Mixer capture-source change detection uses logical AND between channel changes, so single-channel changes may report unchanged even though state changes. Debug procfs can create invalid hardware constraints if written incorrectly.

## Test Signals

Run PCM playback/capture with hrtimer and jiffies modes, fake and real buffers, mmap and non-mmap device variants, all built-in model presets, suspend/resume, period elapsed timing, XRUN/drain behavior, mixer volume and capture controls, external I/O inactive notifications, debug procfs reads/writes, and multi-card module-parameter combinations.
