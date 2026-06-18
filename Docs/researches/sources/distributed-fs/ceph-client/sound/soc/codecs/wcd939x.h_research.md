# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.h

## Purpose
Private WCD939X codec interface and register map. It provides the register addresses, bit masks, SoundWire port/channel identifiers, shared SoundWire child state, and transport helper prototypes used by the WCD939X platform codec and SoundWire slave driver.

## Important APIs, Types, and Functions
The header defines the WCD939X analog, digital, RX top, compander, and DSD register address space from `WCD939X_BASE` through `WCD939X_MAX_REGISTER`, with bitfield masks for bias, RX supplies, headphone/ear PA controls, TX ADC controls, micbias, MBHC mechanical/electrical/impedance/moisture blocks, class-H/flyback, interrupt status/mask/clear/level registers, DMIC, SoundWire clocking, PDM watchdogs, efuse, and RX path controls. It declares SoundWire TX port/channel enums, RX port/channel enums, `WCD939X_MAX_SWR_CH_IDS`, and `struct wcd939x_sdw_priv`.

`struct wcd939x_sdw_priv` is the key shared transport type: it stores the `sdw_slave`, stream config/runtime, per-port config array, channel metadata pointer, port enable flags, active port count, TX/RX role flag, back pointer to `struct wcd939x_priv`, nested IRQ domain, and regmap. When `CONFIG_SND_SOC_WCD939X_SDW` is enabled the header declares `wcd939x_sdw_free()`, `wcd939x_sdw_set_sdw_stream()`, and `wcd939x_sdw_hw_params()`; otherwise inline stubs return `-EOPNOTSUPP`.

## Control Flow
The header itself has no runtime control flow. It shapes compile-time flow by giving `wcd939x.c` concrete register and bitfield names for component controls and DAPM event sequencing, while allowing the SoundWire child driver to export stream setup/free helpers and the shared child state consumed by the master codec driver.

## State and Persistence
No state is allocated by the header, but the `struct wcd939x_sdw_priv` layout defines the persistent per-SoundWire-child state used for stream lifetime, port masks, regmap access, and nested IRQ routing. Register macros also encode persistent hardware state touched by the driver, including micbias levels, MBHC thresholds, efuse calibration, interrupt configuration, and RX/TX path settings.

## Dependencies and Integration Points
The file includes Linux SoundWire headers and relies on kernel bit macros such as `BIT()` and `GENMASK()`. It is included by the WCD939X master codec driver and SoundWire slave implementation. The fallback stubs let the codec build fail functionally rather than link-fail when the SoundWire helper implementation is disabled.

## Risks
Risks are mostly register-contract risks: incorrect addresses or masks can silently program the wrong analog block, duplicate or drifted bit definitions can mislead future edits, and the fixed array sizes must remain consistent with the SoundWire channel metadata in the companion implementation. Because the header exposes a large hardware surface, changes need cross-checking against datasheets and the event code that assumes specific masks.

## Test Signals
Build coverage with and without `CONFIG_SND_SOC_WCD939X_SDW` validates the prototype/stub contract. Runtime signals are successful SoundWire child probe, correct port mask programming for all RX/TX channels, valid nested IRQ propagation through `slave_irq`, and expected register writes for micbias, MBHC, PDM watchdog, DMIC, ADC, headphone, ear, compander, and Type-C related paths.
