# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.h

## Purpose
Defines the parsed XenStore configuration structures for the Xen sound frontend.

## Important APIs, Types, And Functions
- `struct xen_front_cfg_stream` stores global stream index, XenStore path, and ALSA hardware constraints.
- `struct xen_front_cfg_pcm_instance` stores PCM name/device id, inherited hardware constraints, and playback/capture stream arrays.
- `struct xen_front_cfg_card` stores card names, default hardware constraints, and PCM instances.
- `xen_snd_front_cfg_card()` fills the card config and returns stream count.

## Control Flow
No executable flow. The structures describe the output of XenStore parsing and the input to event-channel creation and ALSA PCM creation.

## State And Persistence
Config structures persist for the frontend device lifetime and are regenerated from XenStore after reconnect. `xenstore_path` points to devm-allocated strings from parsing.

## Dependencies And Integration Points
Includes ALSA core/PCM headers for `snd_pcm_hardware`. Used by core, event-channel, and ALSA Xen frontend files.

## Risks
The global stream index must match event-channel pair indices; misordered parsing would connect ALSA streams to the wrong backend stream.

## Test Signals
Compile plus runtime multi-device/multi-stream configuration tests validate structure ownership and indexing.
