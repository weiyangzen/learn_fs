# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic3x.h

## Purpose
Defines the private register map, model IDs, exported shared-core interface, and bit fields for the TLV320AIC3x family driver.

## Important APIs, Types, and Functions
Declares `aic3x_regmap`, `aic3x_probe()`, and `aic3x_remove()`. Defines model constants, 110 cached registers, reset/clock/PLL/interface/mixer/output/GPIO/headset registers, power and mute bits, default volume/gain helpers, micbias voltage enum, headset debounce enums, and GPIO function enums.

## Control Flow
The header has no executable code. Bus wrappers and the shared core include it to agree on model IDs, register addresses, and masks.

## State and Persistence
Constants describe persistent codec state in hardware registers: PLL programming, sample-rate selection, input/output routes, power bits, GPIO modes, headset detection, and micbias voltage.

## Dependencies and Integration Points
Integrated by both I2C/SPI wrappers and `tlv320aic3x.c`. Machine/platform code indirectly relies on these encodings through controls, DT properties, and DAI setup.

## Risks
Several comments preserve older datasheet spellings and broad compatibility assumptions. Register aliases such as `DAC_PWR` and `HPLCOM_CFG` sharing address 37 are intentional but easy to misuse. Model-specific reserved registers must be respected by the C file, especially AIC3104.

## Test Signals
Compile coverage for both transports, static validation of mask/shift pairs, and runtime checks for GPIO/headset/micbias register values on model-specific hardware.
