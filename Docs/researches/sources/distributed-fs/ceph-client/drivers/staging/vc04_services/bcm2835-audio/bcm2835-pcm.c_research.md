## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-pcm.c

Purpose: this file implements ALSA PCM playback callbacks for BCM2835 audio, including regular PCM and HDMI IEC958/SPDIF playback paths.

Important data and functions: hardware capability tables are `snd_bcm2835_playback_hw` and `snd_bcm2835_playback_spdif_hw`. Runtime callbacks are `snd_bcm2835_playback_open_generic()`, regular/SPDIF open wrappers, `snd_bcm2835_playback_close()`, `snd_bcm2835_pcm_prepare()`, `snd_bcm2835_pcm_transfer()`, `snd_bcm2835_pcm_ack()`, `snd_bcm2835_pcm_trigger()`, and `snd_bcm2835_pcm_pointer()`. `bcm2835_playback_fifo()` is called from VCHIQ completion callbacks to advance playback state. `snd_bcm2835_new_pcm()` creates PCM devices and installs ops.

Control flow: open serializes on `audio_mutex`, rejects duplicate opens, allocates a `bcm2835_alsa_stream`, opens a VCHIQ audio instance, assigns runtime hardware constraints, stores the stream, and marks the substream open. Prepare sends controls and audio parameters to firmware, initializes indirect playback bookkeeping, buffer/period sizes, atomic playback position, and interpolation time. ALSA ack transfers newly available bytes from the DMA buffer through `bcm2835_audio_write()`. Trigger starts, stops, or drains firmware playback. Pointer reports indirect playback position and adjusts runtime delay by interpolating time since the last firmware completion.

State and persistence: stream state lives in dynamically allocated `struct bcm2835_alsa_stream` and includes indirect PCM state, `draining`, atomic byte position, period offset, buffer/period size, interpolation timestamp, VCHIQ instance, and index. `chip->opened` is a bitmask for active substreams; SPDIF open rejects any already-open stream. PCM buffers are managed through `snd_pcm_set_managed_buffer_all()`.

Dependencies and integration points: depends on ALSA PCM and indirect PCM helpers, `bcm2835.h`, and transport functions from `bcm2835-vchiq.c`. `bcm2835.c` calls `snd_bcm2835_new_pcm()` for each ALSA card/route.

Risks: `chip->opened` uses substream numbers and SPDIF's exclusive handling may be too broad or too narrow depending on card layout. Completion callbacks can call `bcm2835_playback_fifo()` asynchronously, so correct ALSA locking is critical. `runtime->delay` interpolation writes a negative frame count based on elapsed time, which should be checked against ALSA delay expectations. Drain path is marked questionable in transport code. The source pointer in transfer uses `runtime->dma_area + rec->sw_data` and assumes managed buffer is valid and contiguous for VCHIQ transfer.

Test signals: playback across U8/S16, 1-8 channels, 8 kHz to 192 kHz, HDMI SPDIF at 44.1/48 kHz, period constraints/alignment, xrun handling when firmware reports too many bytes, drain/stop behavior, concurrent open rejection, and position/delay reporting under long playback are key.
