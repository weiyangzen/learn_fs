# sources/distributed-fs/ceph-client/sound/soc/samsung/aries_wm8994.c

## Purpose
Machine driver for Samsung Aries and Fascinate 4G WM8994-based audio. It defines HiFi, baseband voice, and Bluetooth links, DAPM widgets/routes, dock/headset detection, mic-bias regulators, codec FLL programming, and optional FM routing.

## Important APIs, Types, And Functions
- `struct aries_wm8994_variant` selects modem DAI format and FM availability.
- `struct aries_wm8994_data` stores extcon, regulators, GPIOs, ADC, and variant.
- `headset_det_irq_thread()` debounces headset detect GPIO, enables micbias, reads IIO ADC, classifies jack type, and toggles earpath selection.
- `aries_hw_params()` and `aries_hw_free()` start/stop WM8994 FLL1 for AIF1 audio.
- `aries_baseband_init()` configures WM8994 FLL2 for 8 kHz voice.
- `aries_late_probe()` registers dock and headset jacks, extcon notifier, GPIO IRQ, jack zones, and media-button GPIO.
- `aries_audio_probe()` parses DT, regulators, GPIOs, extcon, IIO channel, routing, CPU/codec phandles, registers an auxiliary component with a "Voice call" DAI, and registers the card.

## Control Flow
Probe validates DT-only operation, selects variant data, obtains supplies and GPIO/ADC/extcon resources, parses routing and child `cpu`/`codec` nodes, binds codec phandles for all links, binds CPU/platform for the main I2S link and Bluetooth SCO CPU, registers the modem component, then registers the card. Late probe creates jack objects and installs notifiers/IRQs. At stream parameter setup, the codec FLL rate is selected from sample width/rate; on free, the codec returns to MCLK1.

## State And Persistence
Device state is in `aries_wm8994_data`, while `aries_dock` and `aries_headset` are static jack objects. GPIO/extcon/ADC events update ALSA jack state. FLL and sysclk selections live in codec hardware state until changed. No disk persistence.

## Dependencies And Integration Points
Depends on WM8994 codec/MFD, Samsung I2S DAI names, BT SCO PCM, extcon, IIO voltage ADC, GPIO descriptors, regulators, and DT audio routing. Integrates with DAPM for speakers, microphones, modem, Bluetooth, line out, and optional FM.

## Risks And Edge Cases
- Static card and jack structures can make multiple simultaneous devices unsafe.
- ADC threshold zones are hard-coded, unlike Midas where thresholds come from DT.
- Headset IRQ assumes detect GPIO remains asserted for 300 ms before ADC classification.
- Error paths release only top-level CPU/codec child nodes; phandles assigned into DAI links are devm/card lifetime assumptions.
- Variant selection depends on matching DT compatible; missing match data would be fatal.

## Test Signals
DT probe for both compatible variants, jack insertion/removal and media button tests, dock extcon notifications, FLL rate tests for 8/11.025/24-bit cases, modem/Bluetooth link activation, and DAPM path checks for FM-present and FM-absent variants.
