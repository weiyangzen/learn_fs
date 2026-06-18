<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c

## Purpose
Virtio-snd jack detection support. It parses virtio jack configuration, builds ALSA jack controls, labels them from HDA pin default configuration, and handles connected/disconnected events.

## APIs, Types, and Functions
Exports `virtsnd_jack_parse_cfg()`, `virtsnd_jack_build_devs()`, and `virtsnd_jack_event()`. Internal `struct virtio_jack` persists ALSA jack pointer, HDA node ID, feature bits, pin defaults/caps, current connection state, and ALSA jack type. Helpers `virtsnd_jack_get_label()` and `virtsnd_jack_get_type()` map HDA device/location fields to strings and `SND_JACK_*` bits.

## Control Flow, State, and Persistence
Parse reads jack count, allocates `snd->jacks`, queries `VIRTIO_SND_R_JACK_INFO`, and copies endian-converted fields into persistent jack entries. Build creates one ALSA jack per entry and reports initial state. Events validate the jack ID, update the `connected` boolean for connect/disconnect event codes, and call `snd_jack_report()`.

## Dependencies and Integration
Depends on virtio config/control query APIs, ALSA jack layer, HDA verb/default-configuration constants, and event dispatch in `virtio_card.c`.

## Risks and Test Signals
Risks include simplified implementation with no jack remap support, generic labels for unknown HDA defaults, event IDs outside range being silently ignored, and `snd_jack_report()` from interrupt context assumptions. Test signals are initial jack state, connect/disconnect events, HDMI/SPDIF/headphone/mic label mapping, and devices with zero jacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_jack.c -->
