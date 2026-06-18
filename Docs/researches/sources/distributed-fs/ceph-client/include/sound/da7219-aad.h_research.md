# sources/distributed-fs/ceph-client/include/sound/da7219-aad.h

## Purpose
This header defines DA7219 accessory-detection platform data for headset insert/remove, mic detection, and button detection.

## Important APIs, Types, and Constants
Enums define micbias pulse level, button configuration, mic detect threshold, jack insertion debounce and polarity, jack detect rate, removal debounce, button averaging, and ADC 1-bit repeat count. `struct da7219_aad_pdata` stores all these settings plus four button threshold values.

## Control Flow
The DA7219 accessory-detect driver reads this pdata during initialization and programs AAD hardware. Runtime interrupt handlers then use the programmed thresholds/debounce to classify jack presence, microphone presence, and button presses.

## State and Persistence
The structure is persistent board policy; event state and ADC/button status live in codec hardware and driver runtime state. On reset/resume the AAD registers must be reprogrammed from this data.

## Dependencies and Integration Points
It is included by DA7219 codec/accessory-detect code and referenced from `da7219.h` via a forward declaration. It integrates with ALSA jack/button reporting and platform firmware property parsing.

## Risks and Edge Cases
Button thresholds must be monotonic and calibrated to headset resistor ladders. Debounce and polarity choices are board-specific. Bad micbias pulse settings can prevent microphone classification or waste power.

## Test Signals
Insertion/removal, CTIA/OMTP or mic-present classification where supported, button press thresholds for all configured buttons, long debounce/noise scenarios, and resume after jack insertion should be tested.
