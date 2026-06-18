# sources/distributed-fs/ceph-client/sound/usb/line6/playback.c

## Purpose
`playback.c` implements the Line 6 USB driver's ALSA playback side: it allocates isochronous output URBs, fills them from the ALSA ring buffer, applies optional software playback volume, mixes software monitor/capture feedback when hardware monitoring is unavailable, and resubmits URBs from completion callbacks. It is tightly coupled to `struct snd_line6_pcm` from the Line 6 PCM core.

## Important APIs, Types, And Functions
The externally used functions are `line6_create_audio_out_urbs()` and `line6_submit_audio_out_all_urbs()`, plus the exported `snd_line6_playback_ops` PCM callback table. Internal helpers include `submit_audio_out_urb()`, `audio_out_callback()`, `change_volume()`, `create_impulse_test_signal()`, and `add_monitor_signal()`. The code operates on `line6pcm->out` stream state, `line6pcm->volume_playback`, `line6pcm->volume_monitor`, `line6pcm->prev_fbuf`, and `line6pcm->prev_fsize`.

## Control Flow And State
`line6_create_audio_out_urbs()` allocates `line6->iso_buffers` URBs, binds them to the device audio-out endpoint, sets `URB_ISO_ASAP`, one or more iso packet descriptors, interval, and `audio_out_callback()`. `line6_submit_audio_out_all_urbs()` repeatedly calls `submit_audio_out_urb()` while holding the output lock in the caller.

`submit_audio_out_urb()` finds an inactive URB bit, computes packet sizes from the device rate numerator/denominator and `intervals_per_second`, copies playback frames from the ALSA DMA ring with wraparound handling, then advances `out.pos`. If PCM playback is not running or playback is paused, it sends silence. It then takes the input lock, consumes `prev_fbuf`/`prev_fsize` from the capture side, optionally creates an impulse-test stream or mixes the captured signal into playback for software monitoring, clears the previous capture buffer pointer, submits the URB, and marks the active bit on success.

`audio_out_callback()` maps the completed URB back to its array index, updates `out.pos_done`, clears the active bit, detects shutdown from iso `-EXDEV` or explicit unlink bits, and resubmits another URB unless shutdown is requested. When enough playback bytes accumulate to cross `out.period`, it calls `snd_pcm_period_elapsed()` outside the spinlock.

## State And Persistence
There is no persistent storage. Runtime state lives in bitmaps (`active_urbs`, `unlink_urbs`, `running`), ALSA ring positions (`out.pos`, `out.pos_done`), byte counters (`out.bytes`, `out.period`, `out.count`), and temporary capture feedback (`prev_fbuf`, `prev_fsize`). Impulse test state is maintained in `impulse_count`, `impulse_period`, and `impulse_volume`.

## Dependencies And Integration Points
This file depends on ALSA PCM callbacks, USB isochronous URBs, Line 6 PCM helpers (`snd_line6_hw_params()`, `snd_line6_prepare()`, `snd_line6_trigger()`, `snd_line6_pointer()`), capture helpers (`line6_capture_copy()`, `line6_capture_check_period()`), and Line 6 device properties such as endpoint numbers, capabilities, sample size, channel count, and supported rates.

## Risks And Edge Cases
URB size calculation assumes `LINE6_ISO_PACKETS == 1` despite looping over packets. Incorrect rate factors, zero URB size, or mismatched frame sizes can break scheduling. `submit_audio_out_urb()` logs submit failures but returns zero, so callers cannot always distinguish a failed USB submission. Software volume handles only 16-bit stereo and packed 24-bit stereo frames. Software monitoring is intentionally skipped for 6-byte frames because those devices are assumed to have hardware monitoring. The capture feedback pointer is consumed under the input lock, so misuse by capture-side code could drop monitor data.

## Test Signals
Useful tests include playback open constraint negotiation, URB allocation against valid/invalid endpoints, ring-buffer wrap copies, period elapsed cadence, pause/silence behavior, volume clamp behavior for 16-bit and 24-bit samples, monitor mixing when `LINE6_CAP_HWMON` is absent, impulse stream capture loopback, URB unlink/shutdown paths, and no-free-URB handling.
