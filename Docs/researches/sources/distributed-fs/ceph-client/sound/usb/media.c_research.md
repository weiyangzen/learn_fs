# sources/distributed-fs/ceph-client/sound/usb/media.c

## Purpose
`media.c` adds Linux Media Controller graph integration to selected ALSA USB-audio devices. It creates media devices, mixer entities, PCM stream entities, interface links to ALSA control/PCM device nodes, and pipeline start/stop hooks so tuner-like USB devices can be shared with DVB/V4L2 users.

## Important APIs, Types, And Functions
Public functions are `snd_media_device_create()`, `snd_media_device_delete()`, `snd_media_stream_init()`, `snd_media_stream_delete()`, `snd_media_start_pipeline()`, and `snd_media_stop_pipeline()`. Internal helpers are `snd_media_mixer_init()` and `snd_media_mixer_delete()`. The data structures are defined in `media.h`: `struct media_ctl` for PCM streams and `struct media_mixer_ctl` for mixer entities.

## Control Flow And State
`snd_media_device_create()` either reuses `chip->media_dev` or allocates one with `media_device_usb_allocate()`, then initializes mixer/control entities and registers the media device if needed. Mixer initialization creates a media devnode for the ALSA control device, then creates an `MEDIA_ENT_F_AUDIO_MIXER` entity per USB mixer interface, with sink/source pads and an enabled interface link.

`snd_media_stream_init()` creates one media entity per ALSA PCM stream. Playback streams are `MEDIA_ENT_F_AUDIO_PLAYBACK` with an ALSA playback interface type and a source pad; capture streams are `MEDIA_ENT_F_AUDIO_CAPTURE` with an ALSA capture interface type and a sink pad. It links the stream entity to mixer pad 1 for playback or pad 2 for capture. Start/stop pipeline functions lock `media_dev->graph_mutex` and call optional `enable_source`/`disable_source` callbacks.

Deletion walks PCM streams and mixers, removes devnodes/entities when the media devnode is registered, deletes the media device, and clears pointers in `snd_usb_audio` and mixer/substream objects.

## State And Persistence
There is no persistence. Runtime ownership is stored in `chip->media_dev`, `chip->ctl_intf_media_devnode`, `mixer->media_mixer_ctl`, and `subs->media_ctl`. `media_pipeline` state is held per stream entity.

## Dependencies And Integration Points
The file depends on the Media Controller core, ALSA USB card/mixer/substream structures, USB device allocation helpers, and PCM/control devnodes. It is gated by `CONFIG_SND_USB_AUDIO_USE_MEDIA_CONTROLLER` through `media.h`.

## Risks And Edge Cases
Partial failure cleanup is delicate because entity registration, devnode creation, interface links, and pad links happen in sequence. `snd_media_mixer_init()` can return after allocating the shared control devnode but before all mixers are initialized. `snd_media_stream_delete()` removes interface devnodes and entities but does not explicitly remove pad links; this relies on entity cleanup/unregister semantics. Pipeline callbacks are optional and must be called with graph locking.

## Test Signals
Test with devices that opt into media-controller quirks: creation idempotence across multiple USB interfaces, mixer and stream entity/pad/link topology, failure injection for each allocation/register step, pipeline enable/disable callback invocation, stream delete before/after media device registration, and full device delete after PCM/mixer creation.
