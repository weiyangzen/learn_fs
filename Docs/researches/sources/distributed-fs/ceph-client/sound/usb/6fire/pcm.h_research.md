# sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.h

## Purpose
Declares 6Fire PCM URB, substream, and runtime structures.

## Important APIs, Types, and Functions
Defines `PCM_N_URBS = 16`, `PCM_N_PACKETS_PER_URB = 8`, and `PCM_MAX_PACKET_SIZE = 604`. `struct pcm_urb` embeds `struct urb` followed immediately by ISO descriptors, buffer pointer, and peer pointer. `struct pcm_substream` tracks lock, ALSA substream, active flag, DMA offset, and period offset. `struct pcm_runtime` holds full duplex state.

## Control Flow
No executable logic. The "do not separate" comment around `urb` and packet descriptors reflects the kernel URB allocation layout expectation for inline ISO descriptors.

## State and Persistence
Runtime state persists as `chip->pcm` and owns URB arrays and buffers until destroy.

## Dependencies and Integration Points
Includes ALSA PCM and mutex APIs plus `common.h`; used by `pcm.c` and `chip.c`.

## Risks
Changing `PCM_MAX_PACKET_SIZE` requires keeping firmware endpoint descriptors and rate packet tables in sync. Reordering `struct pcm_urb` fields could break ISO descriptor assumptions.

## Test Signals
Build tests plus runtime high-rate streaming are needed to validate max packet sizing and inline descriptor layout.
