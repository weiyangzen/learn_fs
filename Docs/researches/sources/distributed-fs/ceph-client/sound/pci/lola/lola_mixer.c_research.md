# sources/distributed-fs/ceph-client/sound/pci/lola/lola_mixer.c

## Purpose
This file discovers Lola pin and mixer widgets, initializes firmware-visible mixer matrices, manages analog gains and digital SRC controls, and creates ALSA mixer controls for analog and digital volume/SRC.

## Important APIs, Types, and Functions
`lola_init_pin()` validates pin widget caps and fills analog gain capabilities. `lola_init_pins()` walks input/output pin NIDs. `lola_init_mixer_widget()` validates the vendor mixer widget, maps the BAR1 mixer array, computes source/destination offsets and masks, and allocates a saved mixer shadow. `lola_mixer_set_src_gain()` and `lola_mixer_set_mapping_gain()` update MMIO gain arrays and notify firmware with mixer verbs. `lola_setup_all_analog_gains()` and `set_analog_volume()` manage pin amp verbs. `lola_set_src_config()` toggles input sample-rate converters by stereo pairs. `lola_create_mixer()` adds ALSA controls and calls `init_mixer_values()`.

## Control Flow
Probe parses pins before the mixer widget. Mixer creation adds analog playback/capture volume controls if all pins in that direction are analog, an optional digital SRC capture switch, digital capture/playback source-gain controls, and initializes default routing: SRC on, matrix cleared, physical inputs mapped to capture, playback streams mapped to physical outputs, and digital source gains at 0 dB.

## State and Persistence
Pin state persists in `chip->pin[dir].pins[]` including current gain step. Mixer state exists both in BAR1 MMIO arrays and driver metadata masks/offsets; `array_saved` is reserved for sleep/reset-style preservation but this file primarily replays current pin/SRC values. `input_src_mask` shadows active SRC channels.

## Dependencies and Integration Points
It depends on codec verbs from `lola.c`, BAR1 mixer register definitions from `lola.h`, ALSA control/TLV APIs, and stream/pin counts discovered by `lola_parse_tree()` and `lola_pcm.c`.

## Risks
The mixer matrix is 32x32 and heavily offset-dependent; invalid hardware caps could cause wrong source/destination writes, so mask validation is critical. Destination gain controls are disabled with a FIXME for buggy matrix handling, indicating unresolved risk in exposing full matrix control. `lola_analog_vol_put()` always returns 0 even after successful changes, so userspace may not get change notifications. SRC is stereo-pair based; odd channel expectations can surprise callers.

## Test Signals
Mixer creation should expose analog controls only on all-analog directions, expose SRC only when digital capture pins advertise SRC, and expose digital capture/playback volumes. Default loopback should route physical inputs to capture and playback to outputs. ALSA mixer writes should update BAR1 gain enable/value registers and produce successful codec flushes. Regression tests should verify change notification behavior and no out-of-mask MMIO writes for Lola280/Lola881/Lola16161-style layouts.
