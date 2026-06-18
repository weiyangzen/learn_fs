# sources/distributed-fs/ceph-client/include/sound/hda_regmap.h

Source read summary: 225 lines, regmap encoding helpers for HD-audio verbs and amplifier controls.

Purpose: adapts HDA verb transactions to Linux regmap so codec drivers can cache, update, and sync selected verb/register state, including vendor verbs and amp gain/mute controls.

Important APIs, types, and functions: lifecycle and raw calls are `snd_hdac_regmap_init()`, `exit()`, `add_vendor_verb()`, `read_raw()`, `read_raw_uncached()`, `write_raw()`, `update_raw()`, `update_raw_once()`, and `sync()`. Encoding macros include `snd_hdac_regmap_encode_verb()`, `snd_hdac_regmap_encode_amp()`, and stereo variants. Inline helpers implement node/verb read/write/update and amp get/update for mono and stereo using `AC_AMP_FAKE_MUTE`, direction, channel, and index fields.

Control flow: codec setup initializes regmap, drivers use encoded verb helpers for cached writes or updates, raw uncached reads query hardware, and resume/sync pushes cached state back to the codec. Amp helpers split left/right channels when stereo control is requested.

State and persistence behavior: cache state is in `hdac_device->regmap`, protected by `regmap_lock`, with vendor verb definitions in `vendor_verbs`. It persists only across runtime operations within the device lifetime and is replayed after power transitions.

Dependencies and integration points: depends on `hdaudio.h`, HDA verb constants, regmap, and ALSA codec code. It integrates HD-audio widgets with generic kernel regmap caching and control update semantics.

Risks and edge cases: register encoding must avoid collisions between verbs, NIDs, amps, and vendor ranges; lazy cache mode can defer hardware writes while power is off; stereo helpers must preserve channel-specific bits.

Test signals: cache write/read/update-once behavior, resume sync after runtime suspend, amp mute/gain control updates, vendor verb registration, uncached reads, and collision tests for encoded register IDs.
