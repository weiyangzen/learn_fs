# sources/distributed-fs/ceph-client/sound/hda/codecs/senarytech.c

## Purpose
`senarytech.c` is the HD-audio codec driver for Senarytech SN6186. It is a generic-parser-based codec driver with vendor initialization verbs, default pin fixups, optional beep controls, EAPD management, GPIO LED support fields, and a communication-stability workaround.

## APIs, Types, and Functions
The private type is `struct senary_spec`, embedding `hda_gen_spec` and storing EAPD pins, dynamic EAPD mode, parse flags, and GPIO LED masks/polarity. Important functions include `senary_auto_parse_beep()`, `senary_auto_parse_eapd()`, `senary_init_verb()`, `senary_auto_turn_eapd()`, `senary_auto_vmaster_hook()`, `senary_init_gpio_led()`, `senary_init()`, `senary_shutdown()`, `senary_remove()`, `senary_suspend()`, and `senary_probe()`. Tables include default pin config, fixups, empty quirk table, and `snd_hda_id_senary[]`.

## Control Flow
Probe allocates `senary_spec`, initializes generic parser state, scans EAPD-capable pin widgets, sets `own_eapd_ctl`, chooses SN6186 defaults and mixer node `0x15`, applies default pin fixup when no quirk matches, runs vendor init verbs, installs a vmaster hook, parses pin defaults, optionally adds beep controls from the first beep widget with output amp support, runs generic auto-config parsing, enables synchronous bus writes and bus reset for resume stability, then runs `PROBE` fixups. Init runs generic init, GPIO LED setup, vendor verbs, static EAPD enable, and init fixups.

## State and Persistence Behavior
State persists in `senary_spec`: up to four EAPD pins, dynamic-EAPD policy, GPIO LED values, parse flags, and generated routes. Vendor verbs and pin-cap overrides are reissued during init. Shutdown/suspend always turn EAPD off to avoid speaker noise.

## Dependencies and Integration Points
Dependencies include ALSA HDA core, generic parser, auto parser, jack support, optional HDA beep, module infrastructure, and SN6186 codec ID `0x1fa86186`. It integrates with generic HDA controls/PCMs and vmaster mute hooks.

## Risks
Vendor-specific writes to NID `0x1b` and pin-cap override for `0x19` are opaque hardware sequences. Enabling `sync_write` and bus reset changes bus behavior globally for stability. The EAPD scan stops at four pins, so codecs with more EAPD pins would be partially controlled.

## Test Signals
Check SN6186 binding, default pin override, generic controls/PCMs, beep controls when configured, EAPD vmaster toggling, suspend/remove speaker silence, resume without single-command stalls, and no regressions from forced sync writes.
