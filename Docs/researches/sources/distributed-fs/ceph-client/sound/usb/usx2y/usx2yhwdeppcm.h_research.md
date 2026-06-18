<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h

## Purpose
Shared-memory layout and creation prototype for US-X2Y hwdep mmap PCM mode.

## APIs, Types, and Functions
Defines `MAXPACK`, `MAXBUFFERMS`, `MAXSTRIDE`, derived shared-section size `SSS`, `struct snd_usx2y_hwdep_pcm_shm`, and `usx2y_hwdep_pcm_new()`.

## Control Flow, State, and Persistence
No executable logic. The shared memory persists three audio buffers (`playback`, `capture0x8`, `capture0xA`), playback/capture isochronous cursor state, an array of 128 captured iso descriptors with frame/offset/length, and counters used by kernel and userspace to synchronize raw USB PCM movement.

## Dependencies and Integration
Included by `usbusx2y.h` and implemented/used by `usx2yhwdeppcm.c`. The layout is exposed through ALSA hwdep mmap and is therefore an ABI with userspace drivers.

## Risks and Test Signals
Risks include volatile fields used as synchronization, no explicit versioning in the shared layout, fixed buffer sizing, and offset arithmetic matching URB descriptor advancement. Test signals are mmap clients reading/writing expected buffers, wraparound of captured iso descriptors, and low-latency JACK workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2yhwdeppcm.h -->
