# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409-tables.c

## Purpose

This file contains static data for the CS8409 HDA bridge driver: ALSA mixer templates, fixed-rate PCM descriptors, HDA init verb arrays, pin configuration tables, CS42L42 I2C initialization sequences, CS8409 coefficient programming sequences, sub-codec descriptors, Dell platform quirk tables, model names, and HDA fixup chains.

## Important APIs, types, and functions

Exported data includes `cs42l42_dac_volume_mixer`, `cs42l42_adc_volume_mixer`, `cs42l42_48k_pcm_analog_playback`, `cs42l42_48k_pcm_analog_capture`, `cs8409_cs42l42_init_verbs`, `cs8409_cs42l42_hw_cfg`, `cs8409_cs42l42_bullseye_atn`, `cs8409_cs42l42_codec`, `dolphin_init_verbs`, `dolphin_hw_cfg`, `dolphin_cs42l42_0`, `dolphin_cs42l42_1`, `cs8409_cdb35l56_four_init_verbs`, `cs8409_cdb35l56_four_hw_cfg`, `cs8409_fixup_tbl`, `cs8409_models`, and `cs8409_fixups`. The static pin and I2C arrays are consumed through exported descriptors and fixups.

## Control flow

The file is declarative. Runtime code in `cs8409.c` selects an entry from `cs8409_fixup_tbl` or `cs8409_models`, applies a pin-table fixup, then chains to a function fixup such as `cs8409_cs42l42_fixups()`, `dolphin_fixups()`, or `cs8409_cdb35l56_four_autodet_fixup()`. Hardware init functions iterate the `struct cs8409_cir_param` arrays until the zero terminator. CS42L42 resume/init code bulk-writes the `struct cs8409_i2c_param` sequences.

## State and persistence behavior

Most objects are immutable tables. The exported `struct sub_codec` objects are mutable templates: `cs8409.c` assigns their `codec` pointer and updates fields such as `hp_jack_in`, `mic_jack_in`, `suspended`, `last_page`, and volume caches at runtime. Because those objects are global, correct single-device assumptions and initialization ordering matter.

## Dependencies and integration points

The data depends on constants and structs from `cs8409.h`, CS42L42 register definitions, HDA generic parser APIs, and the HDA fixup framework. Quirk entries primarily target Dell subsystem IDs for Bullseye, Warlock, Cyborg, Dolphin, Odin, and related MLK variants, plus CDB35L56-four-HD model support.

## Risks and test signals

Risks include incorrect Dell subsystem-to-fixup mapping, stale CS42L42 register sequences, shared mutable `sub_codec` state across multiple codec instances, wrong pin defaults causing generic parser misclassification, and coefficient recipes that break ASP slot timing or DMIC routing. Test signals include fixup selection logs for known subsystem IDs, 48 kHz-only PCM constraints, jack detection for single and dual CS42L42 designs, speaker/DMIC routing on Bullseye/Warlock/Cyborg/Odin, and component binding for CDB35L56 systems.
