# sources/distributed-fs/ceph-client/sound/hda/codecs/conexant.c

## Purpose

This driver supports a broad set of Conexant HDA codecs using the generic HDA parser plus many platform fixups. It handles EAPD control, optional beep controls, mute and mic-mute LEDs, headset/headphone mic modes, OLPC XO DC-input behavior, amp-cap corrections, pin overrides, GPIO quirks, and stability workarounds for resume communication.

## Important APIs, types, and functions

`struct conexant_spec` embeds `struct hda_gen_spec` and stores EAPD pins, parse flags, OLPC DC-mode state, LED GPIO/EAPD fields, and a CX11880/SN6140 headset-recognition flag. Probe and lifecycle functions are `cx_probe()`, `cx_init()`, `cx_suspend()`, `cx_remove()`, and `cx_auto_shutdown()`. EAPD helpers are `cx_auto_parse_eapd()`, `cx_auto_turn_eapd()`, and `cx_auto_vmaster_hook()`. Beep support is conditionally compiled through `cx_auto_parse_beep()`. Major fixup helpers include `cxt_fixup_headphone_mic()`, `cxt_fixup_headset_mic()`, `cxt_fixup_olpc_xo()`, `cxt_fixup_mute_led_eapd()`, GPIO LED helpers, amp-cap fixups, HP gate-mic setup, and CX11880/SN6140 headset VREF handling.

## Control flow

Probe allocates state, enables a jack callback for CX11880/SN6140 headset VREF handling, scans EAPD-capable pins, selects a fixup table based on vendor ID, optionally installs a vmaster EAPD hook, applies `PRE_PROBE` fixups, parses pin defaults with accumulated parse flags, creates beep controls, runs generic auto-config, enables `sync_write` and bus reset if needed, and applies `PROBE` fixups. Init runs generic init, enables static EAPDs, initializes GPIO LEDs, applies `INIT` fixups, and re-applies CX11880/SN6140 headset recognition. Suspend/remove turn off EAPD to avoid speaker noise.

## State and persistence behavior

Software state includes generic parser data, EAPD pin lists, dynamic EAPD mode, LED masks and polarity, OLPC recording/DC bias state, current capture mux paths, and parse flags. Hardware state persists in pin widget controls, EAPD bits, GPIO data, amp-cap overrides, vendor registers for headset mode and recognition, and OLPC mic/DC routing. Some fixups install hooks into generic callbacks, so state transitions happen through mixer, automute, capture PCM, and LED classdev paths.

## Dependencies and integration points

The driver depends on ALSA HDA core, generic parser, beep support when configured, jack support, LED classdev integration through HDA helpers, and included helper fixups for ThinkPad and Ideapad ACPI hotkey LEDs. It matches many Conexant codec IDs from CX11880/SN6140 through CX20952 and uses PCI/subsystem and codec quirks to select platform behavior.

## Risks and test signals

Risks include quirk overmatching, EAPD shutdown muting valid outputs, LED polarity mistakes, OLPC DC mode disabling normal microphones incorrectly, headset mic parse flags changing jack semantics, CX11880/SN6140 vendor writes breaking headset detection, sync-write bus reset side effects, and amp-cap overrides creating unsafe gain ranges. Test signals include per-codec probe and fixup selection logs, EAPD speaker/headphone output after mute toggles and suspend, mute/micmute LED behavior, headset CTIA/OMTP/headphone detection, OLPC DC-mode mixers and capture LED behavior, beep mixer creation when configured, and S3 resume stability on affected laptops.
