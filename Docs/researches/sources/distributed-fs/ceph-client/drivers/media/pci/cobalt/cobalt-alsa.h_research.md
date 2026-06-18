<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h

Purpose: Defines Cobalt ALSA private card state and the stream-level ALSA lifecycle API.

Important APIs/types: `struct snd_cobalt_card` stores the owning `cobalt_stream`, ALSA `snd_card`, capture counters, capture substream, playback buffer sizing/position, playback active flag, playback open count, and playback substream. It declares `cobalt_alsa_init()` and `cobalt_alsa_exit()`.

Control flow: The struct fields are initialized by ALSA card creation, then updated by PCM open/close/prepare/trigger/pointer and vb2 thread callbacks.

State/persistence: All fields are runtime-only and tied to one audio stream. `alsa_record_cnt` and `alsa_playback_cnt` protect vb2 thread start/stop. `hwptr_done_capture` and `pb_pos` are ALSA hardware pointer sources.

Dependencies/integration: Bridges `cobalt_stream` from the Cobalt core to ALSA `snd_card`/`snd_pcm_substream` state. Included by node registration, ALSA main, and PCM implementation.

Risks: There is no explicit lock in this struct; the PCM code relies on ALSA stream locks and vb2 thread serialization. Any new shared fields need a clear locking model.

Test signals: Compile coverage, concurrent ALSA open/close, pointer accuracy, and teardown with active substreams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa.h -->
