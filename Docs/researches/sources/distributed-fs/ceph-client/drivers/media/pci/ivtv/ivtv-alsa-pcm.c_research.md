# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.c

## Purpose
`ivtv-alsa-pcm.c` implements the ALSA PCM capture device that receives PCM audio packets from the ivtv encoder stream and copies them into the ALSA runtime ring buffer.

## Important APIs, Types, And Functions
The file defines `snd_ivtv_hw_capture` with fixed S16_LE, 48 kHz, stereo capture constraints, module parameter `pcm_debug`, callback `ivtv_alsa_announce_pcm_data()`, ALSA ops for open/close/prepare/trigger/pointer, and exported `snd_ivtv_pcm_create()`.

## Control Flow
`snd_ivtv_pcm_create()` creates one capture-only PCM device, initializes the card spinlock, installs capture ops, uses a vmalloc managed buffer, and names the PCM after the ivtv card. Opening the PCM serializes against ivtv V4L2 file operations, initializes hardware on first open, claims the ivtv PCM stream, assigns hardware constraints, stores the substream, installs `itv->pcm_announce_callback`, marks the stream as streaming, and starts the ivtv V4L2 encode stream. Closing stops the encode stream, clears streaming state, releases the stream, and removes the announce callback.

`ivtv_alsa_announce_pcm_data()` is called by ivtv when PCM bytes arrive. It validates the substream/runtime/dma area, converts byte count to frames, copies data into the ALSA ring buffer with wrap handling, updates hardware pointer and period accounting under ALSA stream lock, and calls `snd_pcm_period_elapsed()` when a period completes.

## State And Persistence
`struct snd_ivtv_card` stores the active capture substream, hardware pointer, and period-progress counter. State resets on prepare/open and is not persistent beyond module/device lifetime.

## Dependencies And Integration Points
The file integrates ALSA PCM core with ivtv stream claiming, stream start/stop, and the ivtv PCM announce callback. It relies on `snd_ivtv_lock()` using ivtv's serialize mutex.

## Risks And Test Signals
`ivtv_alsa_announce_pcm_data()` updates `hwptr_done_capture` under `snd_pcm_stream_lock()`, while `snd_ivtv_pcm_pointer()` reads it under `itvsc->slock`; these are different locks, so pointer reads can race. The trigger op is a no-op, so ALSA start/stop semantics are mostly handled at open/close. Tests should cover ring wrap, period elapsed cadence, concurrent pointer callback, stream already busy, close during packet delivery, and ALSA hw_params near min/max period settings.
