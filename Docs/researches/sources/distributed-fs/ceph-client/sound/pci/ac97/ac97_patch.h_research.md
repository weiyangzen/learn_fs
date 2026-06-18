# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_patch.h

## Purpose
`ac97_patch.h` is a private helper header for AC97 codec patch code. It defines compact macros for building ALSA mixer controls that read and write AC97 registers, an enum-control descriptor, and private prototypes for generic AC97 helpers implemented in `ac97_codec.c`.

## Important APIs, Types, And Macros
- `AC97_SINGLE_VALUE()` and `AC97_PAGE_SINGLE_VALUE()` encode register, bit shift, mask, invert flag, and optional page into `private_value`.
- `AC97_SINGLE()`, `AC97_PAGE_SINGLE()`, and `AC97_DOUBLE()` build `struct snd_kcontrol_new` entries using `snd_ac97_info_volsw`, `snd_ac97_get_volsw`, and `snd_ac97_put_volsw`.
- `struct ac97_enum` stores register, left/right shifts, mask, and text labels for enum controls.
- `AC97_ENUM_DOUBLE()`, `AC97_ENUM_SINGLE()`, and `AC97_ENUM()` build enum descriptors and ALSA controls using `snd_ac97_info_enum_double`, `snd_ac97_get_enum_double`, and `snd_ac97_put_enum_double`.
- Prototypes expose `snd_ac97_cnew()`, control remove/rename/swap helpers, `snd_ac97_try_bit()`, and PM restore helpers to patch implementation files.

## Control Flow
There is no executable control flow in this header. Runtime behavior is created when patch files instantiate macros into `struct snd_kcontrol_new` arrays. The control core later calls the referenced generic info/get/put functions and decodes `private_value`.

## State And Persistence
The header does not own state. It defines encoding conventions that become persistent ABI inside each created control's `private_value`. Those values determine which AC97 register bits are read, updated, inverted, or page-switched.

## Dependencies And Integration Points
It assumes ALSA control types and `struct snd_ac97` are already visible via the including source's AC97 headers. It is tightly coupled to `ac97_codec.c` helper functions and to patch files such as `ac97_patch.c`.

## Risks
- The bit packing in `private_value` is positional; masks wider than expected or wrong shift values silently target incorrect bits.
- `AC97_PAGE_SINGLE_VALUE()` reserves high bits for page metadata, so helper decoding must stay consistent.
- Function prototypes are `static` because this header is included in the implementation unit that also includes or has visibility into generic AC97 code; moving it across compilation boundaries would require rework.

## Test Signals
- Controls built with these macros should expose correct boolean/integer/enum ranges.
- Get/put tests should verify inverted and non-inverted controls update only the intended AC97 bits.
- Paged controls should restore `AC97_INT_PAGING` after access.
