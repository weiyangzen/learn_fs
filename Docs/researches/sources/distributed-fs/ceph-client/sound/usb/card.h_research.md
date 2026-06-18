# sources/distributed-fs/ceph-client/sound/usb/card.h

## Purpose
Defines the central in-memory model for the generic ALSA USB-audio driver: parsed audio formats, streaming endpoints, PCM substreams, stream containers, and optional platform callbacks. It is the shared contract consumed by format parsing, clock setup, endpoint streaming, PCM callbacks, quirks, and platform integration.

## Important APIs, Types, and State
`struct audioformat` records one USB alternate setting: ALSA format bitmask, channel count, UAC type/protocol, endpoint/sync endpoint coordinates, packet interval, max packet size, supported rates, clock ID, channel map, and DSD flags. `struct snd_usb_endpoint` models an isochronous data or sync endpoint with open/running state, endpoint callbacks, sync links, URB contexts, packet scheduling FIFO, clock/packet accumulators, hardware-constraint cache, and a spinlock. `struct snd_usb_substream` stores playback/capture state including current format, ALSA substream, endpoint handles, buffer accounting, DoP state, and stream flags. `struct snd_usb_stream` groups playback and capture substreams for one ALSA PCM. `struct snd_usb_platform_ops` provides connect/disconnect/suspend/resume hooks for external platform integration. Constants such as `MAX_URBS`, `MAX_PACKS_HS`, `SYNC_URBS`, and `MAX_QUEUE` bound URB fanout and queue depth.

## Control Flow and Integration
This header is included by `format.c`, `clock.c`, `endpoint.c`, `implicit.c`, and PCM code. Parser code fills `audioformat`; PCM hw_params opens an endpoint and passes selected format/rate/channel parameters; endpoint logic uses cached `audioformat` fields to allocate URBs and set interfaces/rates. `snd_usb_find_suppported_substream`, platform-op registration, and rediscovery declarations link this internal model to broader card/platform code outside this subset.

## State and Persistence
State is kernel-resident only. `audioformat` instances live on format lists, endpoints live on `chip->ep_list`, and substreams/streams live on `chip->pcm_list`. No persistent storage is used; suspend/resume and disconnect depend on callers resetting flags and freeing lists.

## Dependencies
Depends on Linux USB descriptors, ALSA PCM types, list heads, spinlocks/atomics, and local `struct snd_usb_audio` from `usbaudio.h`. Endpoint fields are tightly coupled to `endpoint.c` and PCM prepare/retire callbacks.

## Risks and Test Signals
Important risks are stale endpoint/substream pointers during disconnect, mismatched format/rate compatibility for shared endpoints, packet-size limits that must match USB speed, and DSD/DoP frame-size differences. Useful tests are USB-audio playback/capture across UAC1/UAC2/UAC3 devices, implicit feedback full duplex, DSD formats, suspend/resume, and module unload while streams are open.
