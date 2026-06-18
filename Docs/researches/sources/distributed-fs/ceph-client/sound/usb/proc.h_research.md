# sources/distributed-fs/ceph-client/sound/usb/proc.h

Purpose: small internal header for usb-audio proc entry creation.

Important APIs, types, and functions: declares `snd_usb_audio_create_proc()` for card-level entries and `snd_usb_proc_pcm_format_add()` for per-stream diagnostics.

Control flow: card setup invokes the card-level function after `struct snd_usb_audio` exists, and stream creation invokes the PCM-format function once a `struct snd_usb_stream` and `pcm_index` are available.

State and persistence: no state is defined here. The declared functions create read-only ALSA proc entries that persist for the lifetime of the sound card.

Dependencies and integration points: depends on `struct snd_usb_audio` and `struct snd_usb_stream` definitions from usb-audio internals and on the implementation in `proc.c`.

Risks: the header exposes no cleanup API because ALSA card proc entries are lifetime-managed by the card. Callers must pass initialized card/stream objects.

Test signals: successful compilation and the presence of card-level and stream-level proc files during usb-audio device enumeration.
