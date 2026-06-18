# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.h

## Purpose
Declares the VirtIO PCM data model and cross-file PCM APIs used by the VirtIO sound driver. It is the contract between PCM discovery, PCM ALSA ops, and PCM message transport.

## Important APIs, Types, And Functions
- `struct virtio_pcm_substream` stores device identity, ALSA substream linkage, hardware constraints, indirect PCM state, transfer flags, message arrays, pending count, and synchronization objects.
- `struct virtio_pcm_stream` groups playback or capture substreams plus channel maps.
- `struct virtio_pcm` represents one ALSA PCM device keyed by VirtIO node id.
- Exports `virtsnd_pcm_validate()`, `virtsnd_pcm_parse_cfg()`, `virtsnd_pcm_build_devs()`, `virtsnd_pcm_event()`, notify callbacks, lookup helpers, control-message allocation, and I/O message lifecycle helpers.

## Control Flow
The header has no runtime flow, but it defines how the driver flows: parse config into `virtio_pcm_substream`, build `virtio_pcm` devices, use ALSA callbacks from `virtsnd_pcm_ops`, then send/complete transport messages through the queue notify callbacks.

## State And Persistence
The key mutable state is per-substream. `lock` protects IRQ/operator shared fields, `msg_empty` synchronizes stop/release draining, `elapsed_period` defers ALSA period notification to process context, and `msg_count` tracks device-owned messages. Nothing is persisted outside kernel memory.

## Dependencies And Integration Points
Includes Linux atomic and VirtIO config headers plus ALSA PCM and indirect PCM headers. It references `virtio_snd` from `virtio_card.h` indirectly through source inclusions and exposes function signatures consumed by `virtio_card.c`, `virtio_pcm.c`, `virtio_pcm_msg.c`, and `virtio_pcm_ops.c`.

## Risks
The structure fields encode concurrency assumptions. Misusing `msg_count`, `xfer_enabled`, or `stopped` without the documented lock/wait discipline can lead to use-after-free or stale device-owned messages.

## Test Signals
Compile coverage is important because this header couples multiple translation units. Runtime tests should exercise open/close, hw_params/hw_free, start/stop, suspend/resume, and interrupt completion paths that mutate the declared state.
