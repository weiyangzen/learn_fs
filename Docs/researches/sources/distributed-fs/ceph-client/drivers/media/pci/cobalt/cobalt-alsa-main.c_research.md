<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c

Purpose: Creates and tears down ALSA card objects for Cobalt audio-capable streams, binding each audio stream to a `struct snd_cobalt_card` and its PCM device.

Important APIs/functions: `cobalt_alsa_init()` creates an ALSA `snd_card`, allocates private `snd_cobalt_card` state, sets card names, creates the PCM device through `snd_cobalt_pcm_create()`, stores `s->alsa`, and registers the card. `cobalt_alsa_exit()` frees the ALSA card and clears the stream pointer. Private free callbacks clear back-pointers so stream state does not retain stale ALSA references.

Control flow: Called from Cobalt node registration for non-dummy audio streams. Init proceeds in ALSA-driver order but deliberately assigns `s->alsa` before `snd_card_register()` to avoid races with userspace opening the device. Error paths free `snd_card` and allocation state.

State/persistence: `struct snd_cobalt_card` persists while the ALSA card exists and points back to the owning `cobalt_stream`. It stores runtime counters and substream pointers defined in `cobalt-alsa.h`. No persistent configuration is written.

Dependencies/integration: Integrates kernel ALSA core with the Cobalt stream model and V4L2 device logging. PCM behavior is implemented in `cobalt-alsa-pcm.c`.

Risks: The error path calls both `snd_card_free(sc)` and `kfree(cobsc)` even though card private free may also free private data depending on initialization stage; any changes here need careful ownership review. Card names assume one ALSA card per audio stream and use Cobalt instance/video channel.

Test signals: ALSA card creation/removal for HDMI input and HSMA output audio streams, open/close after registration, error injection around `snd_card_new`, private-data cleanup, and module unload with active or recently closed PCM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-alsa-main.c -->
