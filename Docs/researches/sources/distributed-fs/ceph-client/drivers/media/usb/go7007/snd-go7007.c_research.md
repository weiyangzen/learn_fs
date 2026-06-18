# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/snd-go7007.c

Purpose: ALSA capture sidecar for GO7007 boards with audio. It exposes one stereo 48 kHz S16_LE capture PCM and receives audio bytes through `go->audio_deliver`.

Important APIs and functions: `go7007_snd_init()` allocates `struct go7007_snd`, creates an ALSA card/device/PCM, installs capture ops, registers the card, stores `go->snd_context`, and takes a V4L2 device reference. `parse_audio_stream_data()` copies incoming USB audio data into the PCM ring and triggers period elapsed notifications. `go7007_snd_remove()` disconnects and frees the card when closed.

Control flow: PCM open allows only one active substream. `hw_params` installs the audio delivery callback; `hw_free` removes it. Trigger start only marks `capturing`; trigger stop resets pointers and counters. USB audio callbacks call `audio_deliver`, which advances `hw_ptr`, wraps writes in the DMA area, accumulates available frames, and signals ALSA when a period is reached.

State and persistence: `struct go7007_snd` stores card/PCM/substream pointers, spinlock, write byte index, hardware frame pointer, available frame count, and capture flag. Module arrays `index`, `id`, and `enable` provide ALSA card selection parameters.

Dependencies and integration points: depends on ALSA core/PCM APIs, GO7007 USB audio URB delivery, and V4L2 refcounting to keep the parent device alive while ALSA owns the card.

Risks and test signals: risks include races between close/remove/audio callback, reliance on callback removal during `hw_free`, period accounting when incoming chunks are larger than one period, fixed 48 kHz stereo assumptions, and static card index allocation. Test single-open exclusivity, start/stop/reset pointer behavior, ring wrap, disconnect during capture, disabled module slots, and audio-enabled stream start/stop.
