<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c

## Purpose
Core virtio-snd device driver: validates the virtio device, creates virtqueues, builds ALSA devices from virtio configuration, dispatches async events, and handles remove/suspend/resume.

## APIs, Types, and Functions
Registers `virtsnd_driver` via `module_virtio_driver()`. Important functions are `virtsnd_validate()`, `virtsnd_probe()`, `virtsnd_remove()`, `virtsnd_find_vqs()`, `virtsnd_build_devs()`, event queue helpers, `virtsnd_event_dispatch()`, and PM callbacks `virtsnd_freeze()`/`virtsnd_restore()`.

## Control Flow, State, and Persistence
Probe allocates `struct virtio_snd`, initializes pending-message and PCM lists plus queue locks, finds four virtqueues, populates event buffers, marks the device ready, parses config for jacks, PCMs, channel maps, and optional controls, builds ALSA devices, registers the card, then enables the event queue. Events are recycled back to the event queue after dispatch to jack, PCM, or kcontrol handlers. Remove/freeze disable events, cancel control messages, delete vqs, reset the device, cancel period work, free PCM messages, and release event messages.

## Dependencies and Integration
Depends on virtio core/config APIs, ALSA card APIs, virtio-snd UAPI, and helper files for PCM, jack, channel-map, kcontrol, and control-message management.

## Risks and Test Signals
Risks include failure cleanup after partial parsing/building, event delivery during teardown, timeout module parameter validation, optional controls feature negotiation, and restore not rebuilding ALSA config. Test signals are virtio feature negotiation, card creation, event storms, suspend/resume, remove during pending control messages, and PCM/jack/control configuration permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_card.c -->
