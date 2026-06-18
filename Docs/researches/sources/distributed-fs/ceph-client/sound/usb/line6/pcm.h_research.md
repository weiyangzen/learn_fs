# sources/distributed-fs/ceph-client/sound/usb/line6/pcm.h

## Purpose
Defines Line 6 PCM stream constants, state structures, properties, and common PCM APIs shared by capture, playback, and device-specific modules.

## Important Types and APIs
`LINE6_ISO_PACKETS`, `LINE6_ISO_INTERVAL`, and `LINE6_IMPULSE_DEFAULT_PERIOD` define transfer cadence and default impulse behavior. Stream type bits distinguish ALSA PCM, monitor, impulse, and capture-helper ownership. `struct line6_pcm_properties` holds ALSA hardware constraints and bytes per channel. `struct line6_pcm_stream` tracks URBs, shared buffer, positions, period accounting, active/unlink masks, locks, opened/running bitmasks, and last frame. `struct snd_line6_pcm` owns duplex streams, packet sizes, volumes, impulse state, flags, and backpointer to `usb_line6`. Declared APIs cover initialization, acquire/release, disconnect, common PCM callbacks, and stream pointer/trigger handling.

## State and Integration
The header is the contract between `pcm.c`, `capture.c`, playback code, and device modules. Device modules supply properties; common PCM code creates runtime state; capture/playback URB callbacks update positions and active masks under spinlocks.

## Risks and Test Signals
Risks include assumptions that ALSA stream enum values match direction loop indexes, bitmask state becoming inconsistent across multiple stream users, and fixed `LINE6_ISO_PACKETS == 1` assumptions in capture. Tests should validate all stream-owner combinations, duplex operation, period accounting, and high-speed vs full-speed iso buffer counts.
