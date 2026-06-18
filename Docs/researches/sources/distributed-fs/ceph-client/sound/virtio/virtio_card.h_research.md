<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h

## Purpose
Central private header for virtio-snd, defining the card state, queue wrappers, dynamic control state, queue accessors, and helper prototypes.

## APIs, Types, and Functions
Defines card/PCM names, `struct virtio_snd_queue`, `struct virtio_kctl`, and `struct virtio_snd`. Inline helpers return control, event, TX, RX, and PCM-direction queues. Prototypes cover jack, channel-map, and kcontrol parse/build/event functions, and exposes `virtsnd_msg_timeout_ms`.

## Control Flow, State, and Persistence
No executable runtime flow except inline queue selection. `struct virtio_snd` persists the virtio device, four virtqueue wrappers, ALSA card, pending control-message list, event buffers, PCM list, jack array, substream array, channel maps, control metadata, and built controls.

## Dependencies and Integration
Includes virtio, ALSA core, virtio-snd UAPI, `virtio_ctl_msg.h`, and `virtio_pcm.h`. It is included by all virtio-snd helper files.

## Risks and Test Signals
Risks include shared state lifetime across devm-managed arrays and manual frees, queue-selection correctness for playback/capture, and helper prototype drift. Test signals are full-driver builds, probe/remove lifecycle tests, and exercising each helper through config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.h -->
