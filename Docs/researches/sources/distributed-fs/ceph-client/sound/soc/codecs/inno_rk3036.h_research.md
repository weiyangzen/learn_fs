# sources/distributed-fs/ceph-client/sound/soc/codecs/inno_rk3036.h

## Purpose
This header is the register map and bit-field contract for the RK3036 Inno codec driver. It defines the symbolic register offsets and bit values consumed by `inno_rk3036.c` for reset, interface format, word length, DAC/headphone power, mute, anti-pop, gain, and charge/discharge current programming.

## Important APIs, types, and functions
There are no functions or types. The exported symbols are preprocessor definitions for registers `INNO_R00` through `INNO_R10`, masks such as `INNO_R01_I2SMODE_MSK`, `INNO_R02_DACM_MSK`, `INNO_R02_VWL_MSK`, `INNO_R03_FWL_MSK`, and fields/shifts such as headphone enable/work bits, DAC clock/VREF bits, zero-cross bits, mute bits, DAC switch bits, and anti-pop bits. `INNO_R10_MAX_CUR` composes the maximum charge/discharge current setting used during bias transitions.

## Control flow
The header has no executable control flow. It drives control flow indirectly by allowing the codec driver to map ASoC events to concrete register masks and values.

## State and persistence behavior
The header carries no runtime state. Its constants describe hardware state fields in the RK3036 codec MMIO region. Any mismatch between these definitions and hardware behavior will affect all state programmed by the driver.

## Dependencies and integration points
It is included only by `inno_rk3036.c` in this subset. It is tightly coupled to that file's regmap writes in DAI format setup, `hw_params`, DAPM controls, reset, anti-pop handling, headphone volume, and bias charging/discharging.

## Risks and edge cases
Several definitions encode both masks and raw field values; callers must use the matching mask when updating bits. The anti-pop shift names contain `ANITPOP`, so grep-based maintenance can miss them if searching for the correctly spelled word. `INNO_R06_DAC_PRECHARGE` and `INNO_R06_DAC_DISCHARGE` are raw values in bit 4 rather than masks, so whole-register writes can affect adjacent fields.

## Test signals
Compile coverage is the primary direct signal. Runtime evidence comes from successful register updates in the RK3036 driver: correct reset, DAI mode/word-length selection, headphone mute and switch behavior, anti-pop left/right toggles, DAPM power bits, and bias charge/discharge writes using `INNO_R10_MAX_CUR`.
