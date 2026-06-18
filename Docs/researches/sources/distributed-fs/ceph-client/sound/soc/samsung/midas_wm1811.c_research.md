# sources/distributed-fs/ceph-client/sound/soc/samsung/midas_wm1811.c

## Purpose
Machine driver for Samsung Midas WM1811/WM8994-family audio. It supports HiFi, voice, Bluetooth links, DAPM routing and pins, codec FLL1 management, GPIO/ADC headset detection and button classification, optional FM/lineout GPIO selection, and DT-driven thresholds.

## Important APIs, Types, And Functions
- `struct midas_priv` stores optional routing GPIOs, headset detect/key GPIOs, ADC channel, current FLL1 rate, and headset jack.
- `headset_jack_check()` enables headset mic bias via DAPM, reads ADC, and classifies jack type.
- `headset_key_check()` reads ADC and maps thresholds to media/volume buttons.
- `midas_start_fll1()` and `midas_stop_fll1()` manage WM8994 FLL1 and SYSCLK.
- `midas_aif1_hw_params()` chooses FLL1 rate for HiFi stream parameters.
- DAPM event handlers `midas_ext_spkmode()`, `midas_fm_set()`, and `midas_line_set()` adjust codec mixer/GPIO routes.
- `midas_late_probe()` sets initial MCLK2 sysclk and registers either codec-native or GPIO/ADC jack detection.
- `midas_probe()` parses DT GPIOs, ADC, threshold arrays, card name/routing, CPU/codec phandles, registers external voice/Bluetooth DAIs, and registers the card.

## Control Flow
Probe allocates private state, acquires optional FM/lineout/headset resources, validates IIO voltage channel and threshold arrays when GPIO headset detection is used, parses card metadata/routing, binds all DAI links to the CPU and codec nodes, registers extra voice/Bluetooth DAIs, and registers the card. Late probe initializes codec sysclk and jack detection path. During HiFi `hw_params`, FLL1 rate is selected from PCM parameters. DAPM bias transitions start FLL1 in prepare and stop it in standby.

## State And Persistence
Private state tracks the active FLL1 rate and jack object. Static threshold arrays are filled from DT at probe. GPIO outputs reflect DAPM route state. Codec FLL/sysclk persists in hardware state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S IDs, WM8994/WM1811 codec APIs, GPIO descriptors, IIO voltage ADC, DAPM, DT card/routing/phandle parsing, and external DAIs for voice/Bluetooth registered by this file.

## Risks And Edge Cases
- Static card and threshold arrays are mutated from DT and not multi-instance safe.
- There are non-ASCII spaces in two error strings, which is harmless but inconsistent with kernel ASCII style.
- FLL switching must avoid active-clock glitches; `midas_start_fll1()` temporarily switches to MCLK2 only when reconfiguring an existing FLL.
- ADC thresholds are treated as microvolt values but stored in fields named `min_mv`/`max_mv`.

## Test Signals
DT threshold validation, GPIO/ADC headset and button detection, codec-native jack detection fallback, HiFi playback across rates, DAPM bias FLL transitions, FM/lineout GPIO toggling, and voice/Bluetooth link registration.
