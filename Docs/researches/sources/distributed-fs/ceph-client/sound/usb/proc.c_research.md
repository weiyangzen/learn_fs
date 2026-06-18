# sources/distributed-fs/ceph-client/sound/usb/proc.c

Purpose: `/proc/asound` diagnostic output for usb-audio cards and streams.

Important APIs, types, and functions: implements `snd_usb_audio_create_proc()` and `snd_usb_proc_pcm_format_add()`. Helpers print USB bus/device ID, vendor/product ID, supported PCM formats, channel counts, endpoints, sync type, rates, packet interval, bit depth, DSD flags, channel maps, sync endpoint details, running status, packet size, momentary feedback frequency, and feedback format.

Control flow: card creation calls `snd_usb_audio_create_proc()` to add `usbbus` and `usbid` read-only entries. Each PCM stream calls `snd_usb_proc_pcm_format_add()`, which creates `streamN`; reads print the card and PCM name, then playback and capture sections when those substreams have formats. Status output locks `chip->mutex` while checking running state and endpoint pointers.

State and persistence: this file creates read-only proc entries; it does not own stream state. Output reflects current `snd_usb_stream`, `snd_usb_substream`, `audioformat`, and endpoint state at read time. It suppresses bus and ID output after chip shutdown.

Dependencies and integration points: depends on ALSA info/proc APIs, usb-audio stream and endpoint structures, channel map constants, and endpoint frequency fields maintained by streaming code.

Risks: proc output is diagnostic but can still race with unusual teardown paths if callers violate locking expectations. Channel labels must stay aligned with ALSA channel-map enum values. The frequency conversion is approximate and depends on full-speed versus high-speed feedback units.

Test signals: `/proc/asound/card*/usbbus`, `usbid`, and `stream*` entries should exist; stream files should list all altsets and rates; running streams should show packet size and momentary frequency; channel maps should print labels or `--` for unknown positions.
