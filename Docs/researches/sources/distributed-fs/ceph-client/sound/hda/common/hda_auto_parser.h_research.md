# sources/distributed-fs/ceph-client/sound/hda/common/hda_auto_parser.h

## Purpose
Declares the shared BIOS pin auto-parser interface for HD-audio codecs. It describes parsed analog/digital input and output pin layouts and helper accessors used by generic codec parsers and jack-control creation.

## Important APIs, Types, And Functions
Defines `struct auto_pin_cfg_item`, `struct auto_pin_cfg`, input/output type enums, pin attribute enums, parser flags such as `HDA_PINCFG_HEADSET_MIC`, and prototypes for label, attribute, and pin default parsing helpers. Inline helpers return effective headphone and speaker pins when line-out pins are repurposed.

## Control Flow
Codec patch drivers call `snd_hda_parse_pin_defcfg()` with optional ignored NIDs and behavior flags. The resulting `auto_pin_cfg` is then consumed by mixer, PCM, and jack setup code, including `snd_hda_jack_add_kctls()`.

## State And Persistence Behavior
The header owns no runtime state. `auto_pin_cfg` is an in-memory parse product containing sorted pin NIDs, input descriptors, digital pins, and PCM type metadata.

## Dependencies And Integration Points
Includes `hda_local.h` for HDA types, pin config macros, and codec helpers. It integrates with codec-specific auto parsers, jack handling, and default pin configuration read from `codec.c`.

## Risks And Test Signals
Risks are array bound mistakes (`AUTO_CFG_MAX_OUTS`, `AUTO_CFG_MAX_INS`), incorrect interpretation of BIOS pin defaults, and headset/headphone mic misclassification. Test signals include correct mixer names, jack controls, detected input/output routing, and parser behavior on systems with docks, internal mics, headset mics, HDMI/SPDIF, and multi-output layouts.
