# sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.c

## Purpose
Implements low-level support for Hoontech/STAudio/Event ICE1712 boards: SoundTrack Audio DSP24, DSP24 Value, DSP24 Media 7.1, STAudio ADCIII, and Event EZ8. It primarily sequences GPIO-controlled external boxes and optional AK4524 codec support.

## Important APIs, Types, and Functions
The exported table is `snd_ice1712_hoontech_cards[]`. `struct hoontech_spec` stores four GPIO box bytes, a global config mask, and per-box channel/MIDI config. `hoontech_init()` is the shared initializer for DSP24-like and STAudio variants; wrappers are `snd_ice1712_hoontech_init()` and `snd_ice1712_staudio_init()`. GPIO sequencers include `snd_ice1712_stdsp24_gpio_write()`, `snd_ice1712_stdsp24_darear()`, `snd_ice1712_stdsp24_mute()`, `snd_ice1712_stdsp24_insel()`, `snd_ice1712_stdsp24_box_channel()`, `snd_ice1712_stdsp24_box_midi()`, and `snd_ice1712_stdsp24_midi2()`. `snd_ice1712_value_init()` configures modified DSP24 Value hardware with an AK4524 template, and `snd_ice1712_ez8_init()` simply applies EEPROM GPIO defaults.

## Control Flow
DSP24/STAudio initialization sets 8 DACs and 8 ADCs, allocates `hoontech_spec`, initializes the four addressable GPIO bytes with address, clock, channel, MIDI, mute, input-select, and rear-DAC defaults, then applies either normal or STAudio box defaults. It writes global DAREAR/mute/input-select state and loops over four boxes to enable MIDI2, channel routing, and MIDI1 as configured. DSP24 Value instead sets 2 DACs/ADCs, allocates AKM state, initializes AK4524 access through GPIO masks, and immediately builds AKM mixer controls. EZ8 copies EEPROM GPIO mask, direction, and state into hardware.

## State and Persistence Behavior
The driver keeps intended box state in `hoontech_spec->boxbits`, `config`, and `boxconfig`; hardware receives the state through clocked GPIO writes. There are no custom ALSA controls for changing the box config after initialization. AKM state for DSP24 Value is held in `ice->akm` and managed by common AK4xxx helpers. EZ8 state is sourced from EEPROM and not otherwise shadowed beyond `ice->gpio`.

## Dependencies and Integration Points
The file depends on `ice1712.h`, `hoontech.h`, ALSA core allocation/control support, AK4xxx helpers through declarations in `ice1712.h`, and the core card table scan. Core probe uses the card-info entries, then generic ICE1712 PCM, mixer, MIDI, and control setup run around these board hooks.

## Risks
GPIO sequencing has fixed microsecond/millisecond delays and no readback, so timing changes can silently break external box programming. Historical comments warn that box configuration flags and MIDI routing behave unexpectedly on ADAC2000-like boxes. The default config is conservative and mostly first-box oriented for non-STAudio. DSP24 Value builds AKM controls inside `chip_init`, unlike most board files, which can interact with later generic control creation ordering.

## Test Signals
Probe all listed Hoontech/Event/STAudio model paths, verify 8-channel or 2-channel counts as appropriate, observe GPIO writes during box setup, test MIDI routing on first and additional boxes, validate mute/input/rear-DAC defaults, run AKM mixer controls on DSP24 Value, and confirm EZ8 preserves EEPROM GPIO direction/mask/state.
