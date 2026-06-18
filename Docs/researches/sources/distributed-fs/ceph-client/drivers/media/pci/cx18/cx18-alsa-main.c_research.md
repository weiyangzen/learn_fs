<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c

Purpose: Implements the optional ALSA module entry point for cx18 PCM capture, creating ALSA card instances for existing cx18 devices and cleaning them up on module unload.

Important APIs/functions: `cx18_alsa_init()` sets the global `cx18_ext_init` callback to `cx18_alsa_load()`. `cx18_alsa_load()` validates the cx18 V4L2 device, checks that the PCM stream is enabled, prevents duplicate ALSA cards, and calls `snd_cx18_init()`. `snd_cx18_init()` creates `snd_card`, allocates `struct snd_cx18_card`, sets names, creates PCM via `snd_cx18_pcm_create()`, stores `cx->alsa`, and registers the card. Exit finds the `cx18` PCI driver and iterates devices to free each ALSA card.

Control flow: Loading `cx18-alsa` installs a hook used by the main cx18 driver to create ALSA devices. Unloading clears the hook after walking devices and calling `snd_card_free()` on existing cards.

State/persistence: `struct snd_cx18_card` is attached to both `snd_card->private_data` and `cx->alsa`. It stores the V4L2 device pointer, ALSA card, PCM counters, substream pointer, and spinlock. No persistent storage.

Dependencies/integration: Depends on cx18 core symbols, V4L2 device embedding, ALSA core, cx18 versioning, and PCM implementation. Uses the existing cx18 PCM encoder stream rather than separate DMA ownership.

Risks: Module load ordering and global callback behavior are subtle. Exit uses `driver_find("cx18", &pci_bus_type)` and does not explicitly handle a missing driver pointer. Private cleanup must clear `cx->alsa` to avoid stale references. The code returns 0 for several error cases after logging, so load can appear successful even if an individual device skipped ALSA.

Test signals: Load `cx18-alsa` before/after `cx18`, ALSA card appears only when PCM stream exists, duplicate load prevention, module unload with devices present, and card name/longname correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-alsa-main.c -->
