# sources/distributed-fs/ceph-client/sound/usb/line6/capture.c

## Purpose
Implements Line 6 isochronous capture URB allocation, submission, completion handling, ALSA capture copying, period accounting, and capture PCM callbacks.

## Important APIs and Functions
Exports `snd_line6_capture_ops`, `line6_create_audio_in_urbs()`, `line6_submit_audio_in_all_urbs()`, `line6_capture_copy()`, and `line6_capture_check_period()`. Private `submit_audio_in_urb()` finds a free URB slot and submits it. `audio_in_callback()` processes completed capture URBs.

## Control Flow
Open applies device-specific rational rate constraints, acquires capture helper buffers, and installs capture hardware. Triggering is handled by common `snd_line6_trigger()`. URB allocation creates `line6->iso_buffers` isochronous URBs on `ep_audio_r`. Submission fills one packet descriptor per URB from `max_packet_size_in`, points transfer buffer into the shared input buffer, submits, and marks the active bit. Completion records `last_frame`, finds the URB index, copies non-empty PCM packets into ALSA DMA unless impulse mode is active, stores the previous frame for monitoring/playback synchronization, clears active/unlink bits, resubmits unless shutting down, and reports periods.

## State and Persistence
State lives in `line6pcm->in`: URB arrays, shared buffer, active/unlink masks, `pos_done`, `bytes`, `period`, `running`, and `last_frame`. `prev_fbuf`/`prev_fsize` in the parent PCM object cache the latest capture frame. No persistent storage exists.

## Dependencies and Integration
Depends on `pcm.h` stream state, common PCM helpers in `pcm.c`, device properties from `driver.h`, and playback/monitor code through `prev_fbuf`. ALSA callbacks reuse common hw_params/free/prepare/trigger/pointer functions.

## Risks and Test Signals
Risks include assuming `LINE6_ISO_PACKETS == 1`, sync issues when `iso_buffers != 2`, packet-size overruns, active bit leaks if submission fails, copying while runtime is invalid, and disconnect during callbacks. Tests should record audio at supported rates, run capture-only on devices needing playback helper, exercise impulse mode, disconnect during capture, and validate period wakeups and ring wrap copying.
