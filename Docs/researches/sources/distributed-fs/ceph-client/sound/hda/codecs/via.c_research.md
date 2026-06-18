# sources/distributed-fs/ceph-client/sound/hda/codecs/via.c

## Purpose
This file is the ALSA HDA codec driver for VIA VT17xx, VT18xx, VT20xx, and related codec families. It maps VIA codec IDs to probe routines, applies small platform fixups, enables VIA vendor backdoors for mixer/boost paths, handles low-current analog mode, and delegates most control/PCM generation to the generic HDA parser.

## Important APIs, Types, And Functions
`enum VIA_HDA_CODEC` classifies supported chip families. `struct via_spec` embeds `struct hda_gen_spec gen` and stores VIA-specific runtime state: `dmic_enabled`, normalized `codec_type`, `alc_mode`, `hp_work_active`, and `vt1708_jack_detect`. `via_codec_ops` exports probe/remove/build/init/suspend/resume/check-power hooks to the HDA bus.

The central helpers are `via_new_spec()`, `get_codec_type()`, `via_parse_auto_config()`, `via_init()`, `via_build_controls()`, `via_build_pcms()`, `via_playback_pcm_hook()`, `via_check_power_status()`, `__analog_low_current_mode()`, `is_aa_path_mute()`, `vt1708_update_hp_work()`, `vt1708_stop_hp_work()`, `override_mic_boost()`, and `add_secret_dac_path()`. Family probes are `probe_vt1708()`, `probe_vt1709()`, `probe_vt1708B()`, `probe_vt1708S()`, `probe_vt1702()`, `probe_vt1718S()`, `probe_vt1716S()`, `probe_vt2002P()`, `probe_vt1812()`, and `probe_vt3476()`.

## Control Flow
`via_probe()` allocates `via_spec` with `via_new_spec()`, then dispatches by `id->driver_data`. The allocator initializes generic defaults: independent headphone, keep EAPD on, DAC min mute, playback hook, automatic stereo mix, `codec->power_save_node = 1`, and `gen.power_down_unused = 1`; it also normalizes VT1708BCE to VT1708S behavior.

Each probe sets a mixer NID and family-specific workarounds before `via_parse_auto_config()`. Examples include VT1708 jack polling and broken speaker mute handling, VT1708S/VT1716S mic boost override backdoors, VT1702 mixer/GPIO verbs and AA path volume cap, VT1718S/VT2002P/VT1812 secret DAC path injection, VT1802 connection-list correction, VT1716S digital mic and mono controls, and VT3476 DMIC/AOW path verbs. `via_parse_auto_config()` sets custom badness tables, parses BIOS pin config with `snd_hda_parse_pin_defcfg()`, adds optional beep controls, runs `snd_hda_gen_parse_auto_config()`, adds the "Dynamic Power-Control" control, and disables widget PM by default for compatibility.

Runtime power flow is driven by `analog_low_current_mode()`. It enables low-current mode only when node power save is allowed, analog loopback amps are muted, and no active streams exist. The actual vendor verb and parameter vary by codec family. Playback hooks and `check_power_status` both refresh this state and update VT1708 jack polling. VT1708 uses scheduled jack polling when the "Jack Detect" control is enabled or when analog-loopback headphone detection is requested.

## State And Persistence
`via_spec` holds codec-family state and current low-current mode. The dynamic power control toggles `spec->gen.power_down_unused` and re-evaluates analog low-current mode, but the code deliberately leaves `codec->power_save_node` disabled after parsing for compatibility unless a path re-enables it. VT1708 jack polling state is stored in `hp_work_active` and `vt1708_jack_detect`; remove and suspend cancel delayed work and stop polling. DMIC selection for VT1716S is written to connect select on NID `0x26` and cached in `dmic_enabled`. Vendor init verbs are stored in codec verb arrays via `snd_hda_add_verbs()` and are replayed by common init paths.

## Dependencies And Integration Points
The file uses the HDA generic parser and jack layer (`hda_auto_parser.h`, `hda_jack.h`, `generic.h`), ALSA mixer control callbacks, optional beep support under `CONFIG_SND_HDA_INPUT_BEEP`, and common fixup helpers from `auto_parser.c`. It integrates with the HDA bus by exporting `snd_hda_id_via[]`, `via_codec_ops`, and `module_hda_codec_driver(via_driver)`. It depends on HDA widget capabilities, pin defaults, connection-list overrides, amp capability overrides, and vendor verbs such as `0xf70`, `0xf73`, `0xf82`, `0xf88`, `0xf90`, `0xf93`, `0xf98`, `0xfb8`, and `0xfb9`.

## Risks
Low-current mode is hardware-sensitive and depends on analog-loopback amp state; errors can produce silence, power regressions, or jack-detect instability. VT1708 uses polling rather than unsolicited input-jack switching, so race conditions around work scheduling/removal and build-control temporary polling are important. `add_secret_dac_path()` injects a primary DAC into mixer connection lists based on heuristics; a wrong insertion can change routing. Power-save fixups intentionally disable node power saving on some systems, showing that generic PM can be unsafe. Format limiting for VT1708 forces playback to S16_LE to avoid noisy 24-bit output, a compatibility tradeoff that should not leak to other codecs.

## Test Signals
Expected signals include successful probe for all IDs in `snd_hda_id_via[]`, codec names corrected for VT1708BCE and VT1705, generic controls plus "Dynamic Power-Control", VT1708 "Jack Detect", VT1716S digital mic and mono controls, beep controls when configured, stable headphone polling start/stop, no phantom jack controls during build, correct S16-only playback on VT1708, valid capture boost controls on overridden pins, and suspend/resume without lost register cache or headphone pops on VT1802. Tests should inspect routing after secret-DAC and VT1802 connection overrides.
