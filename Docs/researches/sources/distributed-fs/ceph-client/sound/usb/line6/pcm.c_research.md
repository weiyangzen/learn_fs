# sources/distributed-fs/ceph-client/sound/usb/line6/pcm.c

## Purpose
Implements the shared Line 6 PCM control layer for playback/capture streams, stream ownership arbitration, buffer allocation, ALSA controls, PCM device creation, disconnect synchronization, and common ALSA PCM callbacks.

## Important APIs and Functions
Exports `line6_init_pcm()`, `line6_pcm_disconnect()`, `line6_pcm_acquire()`, `line6_pcm_release()`, `snd_line6_hw_params()`, `snd_line6_hw_free()`, `snd_line6_prepare()`, `snd_line6_trigger()`, and `snd_line6_pointer()`. Internal helpers manage URB unlink/wait, per-direction stream start/stop, and buffer acquire/release. ALSA controls include PCM playback volume and impulse response volume/period.

## Control Flow
Initialization creates a duplex PCM, allocates `snd_line6_pcm`, initializes locks/default volumes/impulse period, derives max isochronous packet sizes, creates playback and capture URBs, and registers mixer controls. `hw_params` allocates the per-stream shared buffer and records the period size; `hw_free` releases it when no other stream type owns it. `prepare` waits for outstanding URBs when not running and resets both directions once per prepare cycle. `trigger` operates on grouped substreams: start/resume may also start a playback helper for capture devices needing output, while stop/suspend clears running flags and unlinks URBs once no stream type remains. Monitor/impulse users call `line6_pcm_acquire()` to allocate both directions and optionally start them; release stops and frees both directions for that type. Disconnect unlinks and waits for both directions.

## State and Persistence
`snd_line6_pcm` stores per-direction stream state, shared buffers, active/unlink bitmasks, positions, periods, volume controls, impulse parameters, previous capture frame, packet sizes, and flags. State is volatile. ALSA mixer values persist only for the lifetime of the card instance.

## Dependencies and Integration
Depends on ALSA PCM/control APIs, Linux USB, `capture.c`, playback helpers from `playback.c`, and device properties from `driver.h`. Device-specific modules pass `line6_pcm_properties` with hardware constraints.

## Risks and Test Signals
Risks include stream ownership bitmask mistakes, freeing buffers while URBs are still active, grouped trigger ordering across playback/capture, capture-helper playback not stopping, active URB timeout, and interactions between impulse/monitor/PCM users. Tests should cover duplex playback/capture, capture on `LINE6_CAP_IN_NEEDS_OUT` devices, grouped ALSA triggers, hw_params/free cycles, impulse controls, monitor users, disconnect while running, and suspend/resume.
