<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h

Purpose: Declares the Cobalt ALSA PCM creation entry point.

Important APIs/types: `snd_cobalt_pcm_create(struct snd_cobalt_card *cobsc)` is called by `cobalt_alsa_init()` after the ALSA card and private card state exist.

Control flow: Header-only declaration; implementation creates capture or playback PCM devices depending on the associated stream direction.

State/persistence: No state; the function consumes and initializes fields in `struct snd_cobalt_card`.

Dependencies/integration: Depends on `struct snd_cobalt_card` from `cobalt-alsa.h` and ALSA PCM core in the implementation.

Risks: The header intentionally exposes only one creation API, so future PCM helper exports require explicit declaration here.

Test signals: Compile/link checks between ALSA main and PCM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-pcm.h -->
