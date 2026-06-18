<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c

## Purpose
Parses virtio channel-map configuration and exposes it as ALSA PCM channel-map controls.

## APIs, Types, and Functions
Exports `virtsnd_chmap_parse_cfg()` and `virtsnd_chmap_build_devs()`. Internal data includes `g_v2a_position_map` converting virtio channel positions to ALSA `SNDRV_CHMAP_*`, and helper `virtsnd_chmap_add_ctls()`.

## Control Flow, State, and Persistence
Parse reads the device `chmaps` count, allocates `snd->chmaps`, queries `VIRTIO_SND_R_CHMAP_INFO`, finds or creates the owning `virtio_pcm` by HDA function node ID, and increments per-stream channel-map counts by direction. Build allocates per-stream `snd_pcm_chmap_elem` arrays, repopulates them from raw virtio map info, clamps channel count to ALSA map capacity, translates positions, then adds ALSA channel-map controls to built PCMs.

## Dependencies and Integration
Depends on virtio config reads, control queries, PCM registry helpers `virtsnd_pcm_find_or_create()`/`virtsnd_pcm_find()`, and ALSA `snd_pcm_add_chmap_ctls()`.

## Risks and Test Signals
Risks include invalid directions, out-of-range position IDs, channel count truncation, channel-map info referencing PCM NIDs that were not otherwise configured, and build ordering requiring PCMs to exist before controls are added. Test signals are playback/capture chmaps for different channel counts, malformed position IDs, devices with no PCM for a chmap, and `alsactl`/`amixer` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_chmap.c -->
