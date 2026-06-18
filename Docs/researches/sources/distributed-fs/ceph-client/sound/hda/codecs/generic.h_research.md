# sources/distributed-fs/ceph-client/sound/hda/codecs/generic.h

## Purpose
Defines the public contract and state layout for the HD-audio generic parser implemented by `generic.c`. Codec drivers include this header to allocate/configure `struct hda_gen_spec`, describe preferred routing behavior, install hooks, and call the generic parse/build/init helpers.

## Important APIs, Types, and Functions
Key types are `struct hda_multi_io`, `struct nid_path`, `struct automic_entry`, `struct badness_table`, and `struct hda_gen_spec`. `struct nid_path` stores a route in DAC-to-pin order for output or pin-to-ADC order for input, including per-hop selector indices, multi-selector flags, assigned volume/mute/boost amp controls, and activation/power flags. `struct hda_gen_spec` is the large per-codec state object: it stores PCM stream templates and names, active stream bits and mutex, analog/digital routing data, ADC/DAC lists, auto-pin config, path index tables, automute state, parser behavior flags, loopback data, multi-I/O pins, preferred DAC pairs, virtual master/LED state, and hook callbacks.

The header declares generic lifecycle and parser functions: spec initialization/removal helpers, path lookup and creation, path activation, dynamic kcontrol creation, auto-config parsing, build controls, build PCMs, jack callbacks, output update, power management helpers, LED helpers, and speaker shutdown muting. It also exports the default output routing badness tables.

## Control Flow
Codec-specific drivers typically allocate `struct hda_gen_spec`, call `snd_hda_gen_spec_init()`, set parser flags or hooks, parse pin defaults, call `snd_hda_gen_parse_auto_config()`, then wire `snd_hda_gen_build_controls()`, `snd_hda_gen_build_pcms()`, and `snd_hda_gen_init()` into `hda_codec_ops`. During runtime, jack unsolicited callbacks can be routed to the standard HP, line-out, and mic autoswitch helpers declared here.

## State and Persistence Behavior
The header describes persistent per-device runtime state. Path arrays and kcontrol arrays are dynamic `snd_array` instances owned by the spec. Cached pin targets, current mux selections, current ADC stream metadata, automute booleans, mute bit masks, EAPD policy, channel count, independent HP enablement, and LED classdev pointers are all kept in the spec for the life of the codec. The state is not serialized to disk; it is reconstructed from codec defaults, hints, and driver flags on probe and restored to hardware during init/resume.

## Dependencies and Integration Points
It depends on Linux LED APIs and the HDA auto parser. It also references HDA core types, ALSA PCM/control types, `hda_multi_out`, `hda_input_mux`, `hda_vmaster_mute_hook`, and `hda_loopback_check` from included HDA headers. The integration contract is intentionally broad: vendor codec drivers can use the same parser while selectively overriding route preference, PCM stream templates, automute hooks, capture sync hooks, and LED behavior.

## Risks
Because `struct hda_gen_spec` is shared across many codec drivers, field ordering and semantics are an ABI-like internal kernel contract. Incorrect use of parser flags before parse time can silently change mixer topology. Path index arrays use one-based indices where zero means invalid, which is easy to misuse. Several arrays are bounded by auto-parser constants, so new hardware layouts with more pins, DACs, ADCs, or LEDs must respect those bounds or update them coherently.

## Test Signals
Compile coverage from multiple codec drivers is the first signal. Runtime signals include successful generic parser probe, correct allocation/freeing under probe failure and remove, expected mixer controls and PCMs for drivers using custom hooks, correct LED access flags when LED helpers are enabled, and no out-of-bounds path/mux references under unusual pin configurations.
