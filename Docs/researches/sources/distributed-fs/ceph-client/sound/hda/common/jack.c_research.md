# sources/distributed-fs/ceph-client/sound/hda/common/jack.c

## Purpose
Implements HD-audio jack detection, cached pin-sense management, unsolicited event routing, jack polling, ALSA jack control creation, gated jack semantics, DP MST jack entries, and headset button/key reporting.

## Important APIs, Types, And Functions
Exports `is_jack_detectable()`, jack table lookup functions, table clear/disconnect, `snd_hda_jack_set_dirty_all()`, `snd_hda_jack_pin_sense()`, `snd_hda_jack_detect_state_mst()`, detection enable/callback registration, gating/keymap/button helpers, `snd_hda_jack_report_sync()`, `snd_hda_jack_add_kctl_mst()`, `snd_hda_jack_add_kctls()`, `snd_hda_jack_unsol_event()`, and `snd_hda_jack_poll_all()`.

## Control Flow
Codec setup creates `hda_jack_tbl` entries for pins and optional DP MST device entries. Detection enable either writes `AC_VERB_SET_UNSOLICITED_ENABLE` with a per-jack tag or relies on codec polling. Pin-sense reads optionally trigger sense measurement, apply inverted-detect quirks, cache results, and account for gating jacks. Unsolicited events find the jack by tag and device entry, mark affected jacks dirty, call registered callbacks, and synchronize ALSA jack reports. Polling walks dirty detectable jacks, compares old/new presence, calls callbacks on changes, then reports.

## State And Persistence Behavior
Per-codec jack table entries cache NID, dev_id, unsolicited tag, callback list, pin sense, detect/dirty/phantom/block flags, gating/gated/key-report links, jack type, button state, and `snd_jack` object. Button reports are one-shot: after reporting, button bits are cleared and a release report is emitted.

## Dependencies And Integration Points
Depends on ALSA jack/control APIs, HDA codec verbs, `hda_local.h` pin config helpers, `hda_auto_parser.h` labels, and codec PM paths that mark jack state dirty after resume. It integrates with auto-parser output and codec-specific callbacks.

## Risks And Test Signals
Risks include stale dirty flags, recursive/gated update ordering, unsolicited tag reuse, DP MST device-entry mismatches, phantom jack naming/reporting, button key routing errors, and lifetime cleanup while userspace holds jack devices. Test signals include jack hotplug events, `snd_jack_report()` notifications, polling-mode behavior, gated jack scenarios, headset button presses, DP MST monitor plug/unplug, and no leaks or stale callbacks after reconfiguration.
