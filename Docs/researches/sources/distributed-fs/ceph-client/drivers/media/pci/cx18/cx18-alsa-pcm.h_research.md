<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h

Purpose: Declares cx18 ALSA PCM creation and PCM data announcement helpers.

Important APIs/types: `snd_cx18_pcm_create(struct snd_cx18_card *cxsc)` creates the ALSA PCM device. `cx18_alsa_announce_pcm_data(struct snd_cx18_card *card, u8 *pcm_data, size_t num_bytes)` is the callback used by cx18 core/mailbox paths to deliver PCM data to ALSA.

Control flow: ALSA main calls PCM creation during card init; cx18 core invokes the announcement callback while capture is active.

State/persistence: No header state; functions mutate `snd_cx18_card` runtime counters and ALSA runtime buffer state.

Dependencies/integration: Bridges cx18 ALSA module and core PCM packet delivery.

Risks: The callback declaration exposes a raw byte buffer and size; callers must pass complete S16 stereo frames matching ALSA runtime assumptions.

Test signals: Compile/link checks and PCM capture data delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-pcm.h -->
