# sources/distributed-fs/ceph-client/sound/hda/common/hda_jack.h

## Purpose
Declares the common HD-audio jack-detection API and data structures. It supports pin presence detection, unsolicited-event callbacks, ALSA jack controls, phantom jacks, gating relationships, DP MST device entries, and headset button key mapping.

## Important APIs, Types, And Functions
Defines `struct hda_jack_callback`, `struct hda_jack_tbl`, and `struct hda_jack_keymap`. Public functions include jack table lookup/clear/disconnect, dirty marking, detection enable, callback registration, gating/keymap/button helpers, pin sense and state queries, ALSA jack kctl creation, auto-pin jack kctl creation, unsolicited event handling, and polling.

## Control Flow
Codec parsers create table entries and ALSA jack controls, enable detection through unsolicited events or polling, and then route hardware events to callbacks and `snd_jack_report()` through the implementation in `jack.c`.

## State And Persistence Behavior
The jack table is per-codec in-memory state. Entries cache pin sense, tag, detect capability, dirty status, phantom/report blocking flags, gating/key-routing NIDs, button state, and the associated `snd_jack`.

## Dependencies And Integration Points
Depends on ALSA jack APIs, HDA codec types, auto parser output, and codec power/resume paths that mark jack state dirty. It is consumed by generic and codec-specific parser code plus HDMI/DP MST support.

## Risks And Test Signals
Risks include stale cached pin sense, duplicate unsolicited tags, gated jack ordering errors, DP MST `dev_id` mismatches, button state not being released, and lifetime bugs around `snd_jack` private data. Test signals are jack kcontrol enumeration, hotplug events, phantom jack reporting, headset button events, polling mode, DP MST monitor changes, and suspend/resume jack resync.
