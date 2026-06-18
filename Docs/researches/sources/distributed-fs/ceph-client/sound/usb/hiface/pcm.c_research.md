# sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.c

## Purpose
Implements playback-only ALSA PCM support for hiFace-compatible USB-SPDIF devices using bulk OUT URBs and vendor sample-rate requests.

## Important APIs, Types, and Functions
`hiface_pcm_init()` allocates runtime state, creates eight bulk OUT URBs, creates an ALSA playback PCM, installs callbacks, and attaches runtime to `chip->pcm`. `hiface_pcm_abort()` sets a panic flag and stops streaming. Internal types `pcm_runtime`, `pcm_substream`, and `pcm_urb` track stream state, URB buffers, active playback substream, DMA offsets, and period offsets. PCM callbacks are `hiface_pcm_open()`, `close()`, `prepare()`, `trigger()`, and `pointer()`.

## Control Flow
Open installs hardware constraints; `extra_freq` devices add KNOT rate constraints up to 384 kHz. Prepare stops any previous stream, resets offsets, sends a vendor control request for the selected rate, and starts the URB ring. Startup submits zeroed URBs and waits up to one second for the first completion to prove the stream is running. Completion copies ALSA ring-buffer data into the URB with half-word-swapped 32-bit samples when active, sends silence when inactive, reports period elapsed outside the spinlocked copy region, and resubmits. Trigger only toggles `sub->active`; streaming remains primed from prepare. Close stops stream and clears the substream.

## State and Persistence
State is volatile: `stream_state`, `panic`, `active`, DMA/period offsets, anchored URBs, and `extra_freq`. The selected sample rate is device-visible after a vendor request but not persisted by the driver.

## Dependencies and Integration
Depends on ALSA PCM APIs, Linux USB bulk URBs/control messages, and `hiface_chip`. It is independent from the generic USB-audio endpoint engine.

## Risks and Test Signals
Risks include panic state becoming sticky after one URB failure until stream restart, period comparison using bytes against `runtime->period_size` frames, no capture support, rate request without ACK, URB buffer cleanup after partial init, and disconnect races with completion callbacks. Tests should play all supported rates, validate 352.8/384 kHz only on extra-frequency devices, inspect sample word order, run pause/start/stop cycles, disconnect during playback, and run USB error injection.
