<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c

Purpose: Implements the ALSA PCM capture device for cx18, copying PCM packets announced by the cx18 core into ALSA runtime buffers and controlling the underlying cx18 PCM encoder stream.

Important APIs/functions: `snd_cx18_pcm_create()` creates one capture PCM and installs `snd_cx18_pcm_capture_ops`. `snd_cx18_pcm_capture_open()` locks cx18 serialization, claims the PCM stream, sets runtime hardware constraints, installs `cx->pcm_announce_callback`, marks streaming, and starts the V4L2 encode stream. `snd_cx18_pcm_capture_close()` stops the encode stream, clears streaming, releases the stream, and clears the callback. `cx18_alsa_announce_pcm_data()` copies incoming PCM bytes into the ALSA ring, updates hardware and period pointers, and signals period elapsed.

Control flow: ALSA open claims and starts the cx18 PCM stream. cx18 mailbox/stream code calls the announce callback as PCM packets arrive. The callback wraps writes at `runtime->buffer_size`, updates counters under ALSA stream lock, and triggers period notifications. Close stops and releases the cx18 stream.

State/persistence: `snd_cx18_card` tracks `hwptr_done_capture`, `capture_transfer_done`, and active capture substream. cx18 core holds the callback pointer while capture is open.

Dependencies/integration: Uses cx18 stream claiming/start/stop/release APIs, cx18 serialize lock through `snd_cx18_lock()`, ALSA PCM core, and vmalloc managed buffers.

Risks: In `snd_cx18_pcm_capture_open()`, if stream claim succeeds but an early streaming flag path returns 0, the local claim item is not obviously released in this function path; correctness depends on broader stream semantics. `snd_cx18_pcm_trigger()` accepts all commands and does nothing, so ALSA trigger semantics are minimal. Copying occurs before stream locking, similar to many simple drivers but worth race testing.

Test signals: ALSA capture at 48 kHz S16_LE stereo, period wraparound, open when stream already used by V4L2, callback clearing on close, repeated opens, and underrun/stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.c -->
