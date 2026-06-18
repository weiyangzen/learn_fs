# sources/distributed-fs/ceph-client/sound/hda/common/auto_parser.c

## Purpose
This file provides the common BIOS pin-default parser and fixup selector for ALSA HDA codecs. Codec drivers call it to turn raw HDA pin default configuration into `struct auto_pin_cfg`, generate user-facing pin labels, store init verbs and pin fixups, and select/apply model, subsystem, or pin-layout quirks.

## Important APIs, Types, And Functions
Exported APIs are `snd_hda_parse_pin_defcfg()`, `snd_hda_get_input_pin_attr()`, `hda_get_autocfg_input_label()`, `snd_hda_get_pin_label()`, `snd_hda_add_verbs()`, `snd_hda_apply_verbs()`, `snd_hda_apply_pincfgs()`, `__snd_hda_apply_fixup()`, `snd_hda_apply_fixup()`, `snd_hda_pick_pin_fixup()`, and `snd_hda_pick_fixup()`. Internal helpers include `is_in_nid_list()`, `sort_pins_by_sequence()`, `add_auto_cfg_input_pin()`, `compare_input_type()`, `reorder_outputs()`, `check_pincap_validity()`, `can_be_headset_mic()`, `hda_get_input_pin_label()`, `check_mic_location_need()`, `fill_audio_out_name()`, `pin_config_match()`, and `hda_quirk_lookup_id()`.

`struct auto_out_pin` is a temporary parser type pairing output pin NIDs with sequence values. The file operates on shared HDA types: `struct hda_codec`, `struct auto_pin_cfg`, `struct auto_pin_cfg_item`, `struct hda_pintbl`, `struct hda_fixup`, `struct hda_model_fixup`, `struct hda_quirk`, and `struct snd_hda_pin_quirk`.

## Control Flow
`snd_hda_parse_pin_defcfg()` optionally overrides caller flags with the `parser_flags` hint, clears the output config, scans every HDA node, filters non-pin widgets, ignored NIDs, disconnected pins, and pins with invalid input/output capabilities, then classifies pins by default device. Line-out, speaker, and headphone pins are accumulated with sequence ordering. Analog inputs are stored in `cfg->inputs`; digital inputs/outputs populate SPDIF/HDMI fields.

After scanning, headset/headphone mic flags mark suitable external mic pins by preferred sequence numbers and then by fallback candidate. The parser then fixes up common BIOS mistakes: multiple headphone pins may be promoted to line-out if no line-out exists, and speakers or headphones may become primary line-out when no real line-out is present. Output pins are sorted and reordered from HDA sequence to ALSA channel order. Inputs are sorted by logical type, headset/headphone mic preference, boost capability, and original order. The function emits autoconfig diagnostics and returns zero or a negative error.

Label functions derive stable mixer names from pin defaults, location, auto config, and output channel position. Verb helpers append zero-terminated verb tables to `codec->verbs` and replay them through `snd_hda_sequence_write()`. Fixup application walks a chain up to depth 10, supports before/after chaining, and performs pins, verbs, function callbacks, or pin-control changes depending on action phase. Fixup selection first honors `model=nofixup`, then model names, model SSID aliases, PCI SSID, codec SSID, and pin-layout quirks.

## State And Persistence
Parser output persists in the caller-provided `struct auto_pin_cfg`, usually inside a codec's `hda_gen_spec`. Fixups persist by mutating codec fields: `fixup_id`, `fixup_list`, `fixup_name`, cached pin configs, init verb arrays, and sometimes codec-private fields through callback functions. `snd_hda_add_verbs()` stores verb table pointers in `codec->verbs`, so table lifetime must exceed codec lifetime, which is why callers generally pass static arrays. Pin config changes update the codec's cached/default pin state and influence later generic parsing and label generation.

## Dependencies And Integration Points
The file depends on HDA codec core helpers for node iteration, widget capability reads, pin default reads/writes, amp capability detection, connection metadata, array allocation, and diagnostic logging. Codec drivers in `sound/hda/codecs` call these APIs before invoking `snd_hda_gen_parse_auto_config()`. Build integration comes from `snd-hda-codec-y += auto_parser.o` in the Makefile. Kconfig options indirectly influence debug verbosity and which codec drivers consume the exported symbols.

## Risks
The parser encodes many heuristics for broken BIOS pin defaults. Changes can alter mixer naming, channel order, jack routing, and automute behavior across many unrelated codecs. `snd_hda_pick_fixup()` must handle absent PCI devices, codec SSID fallback, and user-specified aliases without selecting too broad a quirk. Fixup chains can recurse; depth is capped but bad chains can skip needed work or apply it in the wrong phase. `pin_config_match()` ignores sequence/association bits and treats disabled pins specially, which is useful for matching but can overmatch. Label generation uses static strings and indexes; duplicate controls can appear if index/prefix logic changes.

## Test Signals
Useful tests include parser logs for known pin layouts, stable ALSA control names for line-out/speaker/headphone/mic/SPDIF/HDMI pins, correct channel order for 4/6/8-channel outputs, headset/headphone mic recognition with and without sequence markers, successful model/SSID/pin quirk selection, fixup chain ordering for pins/verbs/functions/pinctls, and no regressions in codec drivers that depend on `snd_hda_parse_pin_defcfg()` before generic parsing.
