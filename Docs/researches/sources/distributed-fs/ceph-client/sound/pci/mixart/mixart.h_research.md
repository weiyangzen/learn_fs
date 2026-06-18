# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.h

## Purpose
This header defines the main miXart driver data model shared by the PCI/PCM, mailbox, firmware, and mixer files. It captures board-manager state, per-card state, firmware-visible buffer descriptors, stream/pipe status values, notification bit layout, and exported cross-file functions.

## Important APIs, types, and functions
`struct mixart_uid` is the firmware object identifier used by most mailbox requests. `struct mem_area` represents mapped PCI BARs. `struct mixart_mgr` is the physical-board manager: it owns the PCI device, IRQ, BAR mappings, mailbox wait/fifo state, locks, firmware status, board type, flow/buffer DMA allocations, console-manager UID, global sample rate, and mixer lock. `struct snd_mixart` is one logical ALSA card and stores PCM objects, analog/digital pipes, stream arrays, physical I/O UIDs, and cached mixer settings.

`struct mixart_pipe` models a firmware streaming group with connector UIDs, status, reference count, and monitoring flag. `struct mixart_stream` models one ALSA runtime stream and stores status, channel count, period-notification accounting, PCM number, and pipe reference. `struct mixart_bufferinfo` and `struct mixart_flowinfo` define DMA structures shared with firmware. Exported functions are `snd_mixart_create_pcm`, `snd_mixart_add_ref_pipe`, and `snd_mixart_kill_ref_pipe`.

## Control flow
The header itself has no executable control flow, but its types determine the driver lifecycle. `mixart_mgr` is allocated during PCI probe, `snd_mixart` objects are allocated per logical card, pipes are created lazily when PCM or monitoring paths request them, and streams are attached to ALSA substreams during open. Timer notifications use the bit masks defined here to decode firmware `buffer_id` values into card, PCM, capture/playback, and substream selectors.

## State and persistence behavior
The status macros define stream and pipe state machines. `mgr->dsp_loaded` records which firmware stages have completed. `mgr->sample_rate` and `mgr->ref_count_rate` persist while streams are open. Mixer arrays in `snd_mixart` cache analog, digital, and monitoring control values and are replayed to firmware by mixer update functions. This is all in-memory kernel state for the lifetime of the PCI device.

## Dependencies and integration points
The header depends on Linux interrupt/mutex types and ALSA PCM declarations. It is included by all miXart implementation files and is the contract between ALSA-facing code, firmware setup, IRQ/mailbox processing, and mixer controls.

## Risks and edge cases
Array sizes and notification masks must stay aligned with firmware expectations and descriptor indexing in `mixart.c` and `mixart_core.c`. The fixed `MIXART_MAX_CARDS` value drives card creation, physical connector counts, descriptor allocation, and notification decoding. Changing stream counts or PCM totals requires auditing all index arithmetic.

## Test signals
Compile coverage is the main direct signal for this header. Runtime signals include correct logical-card count, correct notification-to-stream mapping, no out-of-bounds stream selection under timer notifications, and stable mixer defaults across all cards.
