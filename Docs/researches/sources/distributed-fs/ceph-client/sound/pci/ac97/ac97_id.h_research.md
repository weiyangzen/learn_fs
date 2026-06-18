# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_id.h

## Purpose

`ac97_id.h` defines selected AC97 codec vendor/device ID constants used by the AC97 codec core and patch logic.

## Important APIs, Types, and Functions

The file is a macro-only header. It defines IDs for Asahi Kasei (`AK4540`, `AK4542`), Analog Devices (`AD1819`, `AD1881`, `AD1885`, `AD1980`, etc.), TriTech, SigmaTel/STAC, Cirrus Logic, Realtek ALC, Yamaha, VIA/ICEnsemble, C-Media, and STMicroelectronics codecs. It also defines `AC97_ID_CS_MASK` for Cirrus revision masking.

## Control Flow

There is no executable flow. Constants are consumed by conditionals and codec match tables in `ac97_codec.c` and included patch code to validate registers, select patch functions, and handle quirks.

## State and Persistence

No runtime state is stored. The constants become compile-time values in users of the header.

## Dependencies and Integration Points

It is included by `ac97_codec.c` and complements the larger `snd_ac97_codec_ids[]` table there. It must stay synchronized with codec IDs referenced in patch logic and register validation.

## Risks and Edge Cases

An incorrect ID or mask can route a codec to the wrong patch or register filter. The file contains only a subset of IDs from the larger table, so new logic should not assume every supported codec has a macro here. Some IDs encode revision bits, making masks important.

## Test Signals

Compile all AC97 code paths, verify ID macros used in switch/case statements match the table entries, and exercise hardware or emulated probes for representative AD, Realtek, Cirrus, SigmaTel, and C-Media codecs.
