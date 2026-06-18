# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.h

## Purpose
Header support for the RT1308 SoundWire driver. It supplies SDW regmap defaults, register-window offset helpers, the SDW reset address, and the per-device private state used by `rt1308-sdw.c`.

## APIs, Types, and Functions
The main data object is `rt1308_reg_defaults[]`, a static register-default table for SDW control, paging, vendor, and SDCA-style translated RT1308 registers. Offset macros `RT1308_SDW_OFFSET`, `RT1308_SDW_OFFSET_BYTE0` through `BYTE3`, and `RT1308_SDW_RESET` encode the 0xc000 SDW window and byte lanes used by the C file. `struct rt1308_sdw_priv` stores the ASoC component, regmap, `sdw_slave`, last `sdw_bus_params`, init flags, optional TDM `rx_mask`/`slots`, hardware version, and optional BQ parameter buffer/count.

## Control Flow
The header has no executable flow. Its defaults are consumed by `rt1308_sdw_regmap`; its offsets are used for DAPM widgets, reset, power, DAC mute, data-path controls, and class-D status writes; and its private-state fields are populated during SDW probe, status updates, bus-config callbacks, component probe, and DAI configuration.

## State and Persistence
State is runtime-only through `struct rt1308_sdw_priv`. The default table seeds regcache expectations but does not persist data outside memory. `hw_init` and `first_hw_init` distinguish a cold unenumerated slave from a previously initialized or reattached slave, while `bq_params` is devm-managed memory populated from firmware properties.

## Dependencies and Integration
This header assumes `rt1308.h` has already defined logical register identifiers such as `RT1308_DATA_PATH`, `RT1308_DAC_SET`, `RT1308_POWER`, `RT1308_POWER_STATUS`, and `RT1308_RESET`. It also relies on Linux regmap, SoundWire, and ALSA SoC types being included by the C file before the header.

## Risks and Test Signals
Risks include the static default table living in a header, so including it from more than one translation unit would duplicate definitions, and defaults/offset formulas needing to match RT1308 byte-addressed SDW semantics exactly. Useful checks are compiler coverage of all field users, regmap-cache behavior against the default table, reset address correctness, and SDW playback after hibernate/resume.
