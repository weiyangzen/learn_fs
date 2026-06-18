# sources/distributed-fs/ceph-client/include/sound/jack.h

Source read summary: 116 lines, ALSA jack abstraction API.

Purpose: defines shared reporting for audio/video/USB jack presence and headset button events through ALSA controls and optional input devices.

Important APIs, types, and functions: `enum snd_jack_types` is a bitmask for headphone, microphone, headset, line/video/AV, line-in, USB, and six button bits. `struct snd_jack` stores kcontrol list, card, ID, optional input device state/key map, cached hardware status, private data/free. APIs include `snd_jack_new()`, `snd_jack_add_new_kctl()`, `snd_jack_set_key()`, and `snd_jack_report()`, with config stubs when jack/input support is disabled.

Control flow: a codec or machine driver creates a jack, optionally adds extra kcontrols and key mappings, then reports status changes from GPIO, codec unsolicited events, polling, or USB detection.

State and persistence behavior: jack state is card-lifetime in-memory state plus `hw_status_cache`; userspace-visible switch/key events are emitted but not persisted.

Dependencies and integration points: depends on ALSA core and optional Linux input devices. Integrates ASoC, HDA, USB, and machine drivers with mixer controls and input event reporting.

Risks and edge cases: enum bits must stay synced with `sound/core/jack.c`, disabled stubs can hide missing reports, input key setup must precede registration, and cached status must handle phantom jacks.

Test signals: jack creation with/without initial kctl, headphone/mic/headset reports, button key events, input-disabled builds, phantom jack behavior, and concurrent report/remove paths.
