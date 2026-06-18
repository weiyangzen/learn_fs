<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c

Purpose: Implements ALSA PCM capture and playback operations for Cobalt audio streams by running the stream's vb2 queue in a kernel thread and translating FPGA HDMI audio sample layout to/from ALSA ring buffers.

Important APIs/functions: `snd_cobalt_pcm_create()` creates either a capture or playback PCM based on `s->is_output`, resets the corresponding audio IP block, installs PCM ops, and uses managed vmalloc buffers. Capture flow uses `snd_cobalt_pcm_capture_open()`, `vb2_thread_start()`, `alsa_fnc()`, and `cobalt_alsa_announce_pcm_data()`. Playback flow uses `snd_cobalt_pcm_playback_open()`, `alsa_pb_fnc()`, trigger state `alsa_pb_channel`, and `cobalt_alsa_pb_pcm_data()`. `sample_cpy()` and `pb_sample_cpy()` remap channel order and 16/32-bit sample packing.

Control flow: On first open, a vb2 thread begins dequeuing queued video-style audio buffers. Capture copies each FPGA frame into the ALSA runtime DMA area, advances `hwptr_done_capture`, tracks period progress, and calls `snd_pcm_period_elapsed()` when needed. Playback copies from ALSA ring memory into outgoing FPGA buffer slots only while trigger state is active. Close stops the vb2 thread when the open count drops to zero.

State/persistence: State is in `struct snd_cobalt_card`: open counters, capture/playback substreams, hardware pointer, period counters, playback buffer size/period/position, and active trigger flag. No state persists across device removal.

Dependencies/integration: Depends on ALSA PCM core, vb2 queue/thread APIs, Cobalt stream reset bits, and the V4L2/vb2 DMA setup from `cobalt-v4l2.c`.

Risks: Capture copy updates most ALSA counters under `snd_pcm_stream_lock_irqsave()` but performs the memory copy before locking; playback uses `pb_count` for iteration and period signaling, so unusual runtime sizes need testing. Channel remapping is hard-coded to Cobalt HDMI ordering. Trigger start returns `-EBUSY` if already active. The queue is shared with V4L2-style setup, so format/queue changes could affect audio behavior.

Test signals: `arecord`/`aplay` at 48 kHz, S16_LE and S32_LE, 1-8 channels, period elapsed cadence, wraparound copying, repeated open/close, trigger start/stop, vb2 thread start failure, and audio IP reset observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.c -->
