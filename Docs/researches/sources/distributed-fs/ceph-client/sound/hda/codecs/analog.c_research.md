# sources/distributed-fs/ceph-client/sound/hda/codecs/analog.c

## Purpose
`analog.c` is the ALSA HD-audio codec driver for a family of Analog Devices/SoundMAX codecs: AD1882/AD1882A, AD1883, AD1884/AD1884A, AD1981/AD1981HD, AD1983, AD1984 variants, AD1986A, AD1988/AD1988B, and AD1989A/B. The file is not a complete hand-built mixer graph; it layers codec-specific defaults, quirks, and extra controls on top of the generic HD-audio parser in `generic.c`.

The driver allocates one `struct ad198x_spec` per codec, sets per-chip mixer, beep, DAC, SPDIF, EAPD, and GPIO policy, lets the generic parser build playback/capture routes from BIOS pin defaults, then registers itself through `module_hda_codec_driver()`.

## APIs, Types, and Functions
The central private type is `struct ad198x_spec`, which embeds `struct hda_gen_spec gen` and adds `model`, SPDIF mux path indexes (`smux_paths`, `cur_smux`, `num_smux_conns`), `eapd_nid`, `beep_amp`, and cached `gpio_data`.

Driver entry points are collected in `ad_codec_ops`: `ad_codec_probe()`, `snd_hda_gen_remove()`, `ad_codec_build_controls()`, `snd_hda_gen_build_pcms()`, `ad_codec_init()`, `snd_hda_jack_unsol_event()`, `ad_codec_suspend()`, `snd_hda_gen_check_power_status()`, and `snd_hda_gen_stream_pm()`. Device matching is via `snd_hda_id_analog[]`, which maps HDA vendor IDs to the internal model enum.

Shared setup helpers include `alloc_ad_spec()`, `ad198x_parse_auto_config()`, `ad_codec_build_controls()`, `create_beep_ctls()`, `ad_vmaster_eapd_hook()`, `ad198x_power_eapd_write()`, and `ad198x_power_eapd()`. `ad198x_parse_auto_config()` sets codec-wide behavior flags (`spdif_status_reset`, `no_trigger_sense`, `no_sticky_stream`), chooses independent-headphone policy, parses pin defaults with `snd_hda_parse_pin_defcfg()`, and delegates route/control generation to `snd_hda_gen_parse_auto_config()`.

Per-model probe functions are `ad1882_probe()`, `ad1884_probe()`, `ad1981_probe()`, `ad1983_probe()`, `ad1986a_probe()`, and `ad1988_probe()`. They set model-specific `gen` fields such as `mixer_nid`, `mixer_merge_nid`, `beep_nid`, `preferred_dacs`, `multiout.no_share_stream`, and `auto_mute_via_amp`, then apply fixups before and after generic auto-configuration.

The important fixup groups are `ad1986a_fixups[]`, `ad1981_fixups[]`, `ad1988_fixups[]`, and `ad1884_fixups[]`, selected by model strings and/or PCI subsystem quirks. They override pin defaults, EAPD polarity and routing, jack-detect polarity, amplifier caps, GPIO mute behavior, digital-mic initialization verbs, and ThinkPad analog beeper behavior.

Extra ALSA controls are created for beep playback and SPDIF source selection. AD1983/AD1981/AD1884 use `ad1983_add_spdif_mux_ctl()` with `ad1983_auto_smux_*()` callbacks that write `AC_VERB_SET_CONNECT_SEL` on the digital output node. AD1988/AD1882 use `ad1988_add_spdif_mux_ctl()` with fake `struct nid_path` routes and `ad1988_auto_smux_*()` callbacks that activate/deactivate paths under `codec->control_mutex`.

## Control Flow
Module registration binds `analog_driver` to matching HDA codec IDs. On probe, `ad_codec_probe()` allocates and initializes `ad198x_spec`, stores `id->driver_data` as the model, and dispatches to the model probe. A failing model probe tears down through `snd_hda_gen_remove()`.

The normal model probe sequence is: set static codec parameters, pick a fixup with `snd_hda_pick_fixup()`, run `HDA_FIXUP_ACT_PRE_PROBE`, parse BIOS pin configuration through the generic parser, add any model-specific SPDIF mux control, then run `HDA_FIXUP_ACT_PROBE`. Later, `ad_codec_build_controls()` asks the generic layer to build controls and then optionally adds beep controls using the composed amp value stored in `spec->beep_amp`.

Initialization calls `snd_hda_gen_init()` first. For AD1988-style codecs with digital output, `ad_codec_init()` replays the stored SPDIF fake paths so the chosen IEC958 source is reflected in hardware after init/resume. Suspend shuts up pins with `snd_hda_shutup_pins()` and writes EAPD-off values for known front/headphone pins, accounting for inverted EAPD implementations.

Runtime mixer control flow is mostly delegated to generic HDA controls. The vmaster mute hook can additionally drive EAPD (`ad_vmaster_eapd_hook()`) or GPIO1 plus EAPD (`ad1884_vmaster_hp_gpio_hook()`). SPDIF source controls update either a connect selector directly or the active state of fake source paths.

## State and Persistence Behavior
The persistent driver state is the codec-owned `struct ad198x_spec`. It records the selected model, generated generic-parser state, active SPDIF source, fake SPDIF path indexes, selected EAPD node, beep amplifier encoding, and last GPIO data value.

Hardware state is persisted and restored through the HD-audio codec cache for several writes. EAPD writes in `ad_vmaster_eapd_hook()` and AD1983 SPDIF connect-selector writes use `snd_hda_codec_write_cache()`, so cached values can be replayed by the HDA core. AD1988 fake SPDIF paths are reactivated in `ad_codec_init()` because the source mux is represented as synthesized paths rather than a simple parser-discovered route. AD1884 HP GPIO mute state is cached in `spec->gpio_data` and pushed during `HDA_FIXUP_ACT_INIT`.

Fixups mutate persistent codec policy before generic parsing: examples include `codec->inv_eapd`, `codec->inv_jack_detect`, `gen.keep_eapd_on`, `gen.own_eapd_ctl`, `gen.add_stereo_mix_input`, and `gen.beep_nid`. Those flags affect later parser output, init behavior, and user-visible controls.

## Dependencies and Integration Points
This file depends on the ALSA HDA core (`sound/hda_codec.h`, `hda_local.h`), the generic parser (`generic.h`, `hda_auto_parser.h`), jack support (`hda_jack.h`), optional input beep support (`hda_beep.h` under `CONFIG_SND_HDA_INPUT_BEEP`), module infrastructure, and slab allocation.

It integrates with the generic parser by embedding `hda_gen_spec` and calling `snd_hda_gen_spec_init()`, `snd_hda_gen_parse_auto_config()`, `snd_hda_gen_build_controls()`, `snd_hda_gen_build_pcms()`, `snd_hda_gen_init()`, `snd_hda_gen_remove()`, and generic power-management helpers. It integrates with ALSA control creation through `snd_hda_gen_add_kctl()`, `snd_ctl_new1()`, and `snd_hda_ctl_add()`.

Hardware integration is through HDA verbs and node IDs: EAPD verbs, GPIO verbs, connection selectors, amp capability overrides, coefficient verbs for digital mics, and BIOS pin default overrides. Platform integration is primarily PCI subsystem quirk matching (`SND_PCI_QUIRK*`) and model-name fixups exposed by the HDA fixup framework.

## Risks
The driver is highly dependent on hard-coded node IDs, vendor IDs, and subsystem quirks. A wrong quirk can expose nonexistent pins, lose internal speakers, invert jack-detect behavior, or drive EAPD/GPIO mute incorrectly. Because many fixes run before generic parsing, subtle ordering changes can alter generated controls and routes.

SPDIF source handling is especially fragile. AD1988 synthesizes fake paths for hardware whose SPDIF source topology does not match the parser model; those paths must be kept consistent with widget capabilities and reactivated at init. AD1983-style SPDIF muxing assumes two or three digital-output connections and writes raw selector values.

Power and mute behavior has platform-specific risk. Several codecs have inverted EAPD, some HP/Lenovo systems need EAPD tied to vmaster mute, AD1884 HP systems toggle GPIO1, and AD1986A avoids shared streams due to a hardware issue. Suspend/init regressions can manifest as silent speakers, pops, or unexpectedly powered amplifiers.

Mixer and beep behavior also has compatibility risk. Amp cap overrides intentionally cap gain to avoid overload, while ThinkPad handling swaps digital beep for analog PC beeper routing. `CONFIG_SND_HDA_INPUT_BEEP` changes whether beep controls are registered at all.

## Test Signals
Useful validation signals include successful codec binding for every ID in `snd_hda_id_analog[]`, clean generic parser completion, expected ALSA controls for playback/capture/beep/SPDIF, and expected PCM construction via `snd_hda_gen_build_pcms()`.

Hardware tests should cover speaker, headphone, line-out surround channels, independent headphone mode for AD1882/AD1884/AD1988, capture from all advertised inputs, jack unsolicited events and auto-mute, vmaster mute/EAPD behavior, suspend/resume audio recovery, and IEC958 source switching. Quirk regression tests should focus on named systems in the fixup tables: Lenovo N100/M55/A60/ThinkPad, HP B2800/nx6320/Touchsmart, Toshiba Satellite L40, Samsung/FSC/ASUS/PackardBell variants.

Static review signals include all model probes returning errors from parser/control creation paths, `snd_hda_gen_remove()` cleanup on probe failure, bounded SPDIF source indices, holding `codec->control_mutex` while activating AD1988 fake paths, and preserving the exact fixup action phases.
