# subset-b-006471 research

Grouped research report for ALSA SoC codec sources under `sources/distributed-fs/ceph-client/sound/soc/codecs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.c

## Purpose
This file implements the Iron Device SMA1307/SMA1307AQ ASoC amplifier codec as an I2C/regmap component. It registers a playback/capture DAI, DAPM routing for the speaker and optional SDO capture/monitor output, ALSA mixer controls for volume, mute, TDM slot placement, fault-monitor policy, reset, and binary tuning mode, and device probe/remove handling.

## Important APIs, Types, And Functions
The private state is `struct sma1307_priv`, which owns the regmap, component/device pointers, firmware setting data, DAPM selections, DAI format/clock state, TDM slot selections, fault-monitor state, OTP/revision fields, current/initial volume, and delayed work. `struct sma1307_pll_match` is the BCLK-to-PLL table, and `struct sma1307_data` carries per-compatible initialization such as `sma1307aq_init()`.

The component-facing pieces are `sma1307_component`, `sma1307_dai[]`, `sma1307_dai_ops_amp`, the DAPM widget/route arrays, and `sma_i2c_regmap`. Driver entry is `sma1307_i2c_probe()`, which allocates state, initializes regmap, matches OF data, validates `SMA1307_FF_DEVICE_INDEX`, initializes defaults, and registers the ASoC component. Removal cancels delayed fault work.

Important control callbacks include the force-mute, software OT1 protection, fault-check enable/period, reset, binary mode, and TDM-slot get/put functions. DAPM callbacks (`sma1307_aif_in_event()`, `sma1307_sdo_setting_event()`, `sma1307_aif_out_event()`, `sma1307_sdo_event()`, `sma1307_power_event()`) translate user-visible mux/switch state into register fields.

The DAI path is handled by `sma1307_dai_set_fmt_amp()`, `sma1307_dai_set_sysclk_amp()`, `sma1307_dai_set_tdm_slot()`, `sma1307_dai_hw_params_amp()`, and `sma1307_dai_mute_stream()`. PLL programming is centralized in `sma1307_setup_pll()`.

## Control Flow
Probe creates regmap, stores defaults (`I2S`, BCLK PLL input, 1 second fault period, fault monitor on, initial volume `0x32`, OT1 software protection on), initializes delayed work, reads the device ID, and registers the component. Component probe syncs DAPM, stores a global component pointer, adds the binary-mode control, and calls `sma1307_reset()`.

Reset reads revision and OTP status, loads optional `sma1307_setting.bin`, applies either firmware/default register settings, high-Zs interrupt output, and restores initial speaker volume. Firmware loading validates a header/checksum, allocates a default register image and up to five mode register/value lists, and sets `set.status`.

Playback/capture parameter setup computes BCLK from rate/width/channels or TDM frame size, updates the PLL when BCLK changes, validates rates/widths, and programs I2S/LJ/RJ/TDM format registers. TDM setup validates 4/8 slots and 16/32-bit slots, programs slot count/width and RX/TX slot positions. Mute changes speaker mute unless force mute is active.

DAPM power-on enables PLL/power, selects mono/stereo speaker mode, and queues the delayed fault monitor when enabled. Power-down cancels the monitor, mutes, waits for mute slope, disables speaker mode, PLL, and power.

## State And Persistence
Runtime state is in `sma1307_priv` and cached by regmap. The optional firmware setting file is requested on each reset and held in devm-allocated buffers inside `sma1307->set`. ALSA control changes persist in driver memory until reset/remove. `last_bclk` avoids redundant PLL writes. The delayed worker maintains `tsdw_cnt`, `cur_vol`, and `init_vol` to reduce volume during OT1 and restore it when the fault clears.

## Dependencies And Integration Points
The file depends on Linux I2C, regmap, firmware loading, delayed work, kobject uevents, and ASoC component/DAI/DAPM/control APIs. It integrates with DT compatibles `irondevice,sma1307a` and `irondevice,sma1307aq`, and the I2C IDs `sma1307a`/`sma1307aq`. It expects register and bit definitions from `sma1307.h` and optional firmware named `sma1307_setting.bin`.

## Risks And Edge Cases
`sma1307_binary_mode_put()` assigns `struct sma1307_priv *sma1307 = snd_kcontrol_chip(kcontrol)`, while other callbacks use `snd_soc_component_get_drvdata(component)`; this appears type-incorrect and could dereference a component as private data. `sma1307_setup_pll()` warns that MCLK is unsupported but then still uses table index 0, which may be unintended for MCLK clock IDs. Firmware parsing assumes enough mode slots for `num_mode` and uses integer copies from firmware bytes without explicit endian conversion. `sma1307_set_binary()` checks writability using loop index `i` for mode entries but writes register addresses from `mode_set`, so filtering may not match the actual target register. Fault worker overwrites `envp[0]` if multiple faults are present, losing earlier fault strings and leaking any previous `kasprintf()` allocation assigned to the same slot.

## Test Signals
Useful validation includes I2C probe with both compatibles, bad device-ID rejection, firmware present/missing/checksum failure paths, reset control behavior, DAPM power transitions, PLL selection for all table BCLKs, TDM slot validation, supported and unsupported PCM rates/widths/formats, force-mute behavior, delayed fault uevent emission, and OT1 volume reduction/restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.h

## Purpose
This header defines the SMA1307 register map, bit masks, control names, DAPM names, device names, clock IDs, mode enums, and firmware-setting structure used by `sma1307.c`.

## Important APIs, Types, And Definitions
The exported types are local to the driver: `enum sma1307_fault`, `enum sma1307_mode`, `enum sma1307_sdo_mode`, `enum sma1307_sdo_source`, and `struct sma1307_setting_file`. The setting structure stores firmware status, header/default/mode arrays, checksum, mode count, and sizes.

The header defines I2C address constants, device names `sma1307a` and `sma1307aq`, sysclk IDs for external clocks and PLL input sources, setting header/default sizes, ALSA control names, and DAPM widget names. Register addresses cover low control registers, brown-out/protection blocks, PLL/OTP/top-management registers, boost/RMS/DGC/MCBS registers, and read-only status/device-index registers. Bit definitions cover power, reset, SAI polarity/format, speaker mute/mode, mono mix, SDO output routing, interrupts, TDM slot placement, OTP status, fault/status bits, and device/revision ID fields.

## Control Flow
There is no executable control flow. The C driver uses these symbols to bound regmap access, construct ALSA controls, select DAPM routes, program DAI formats, parse status bits in the delayed worker, and validate device identity.

## State And Persistence
The header declares no storage. Persistent state in the companion C file depends on these constants matching hardware behavior, especially firmware image sizing, OTP/status fields, and register access ranges.

## Dependencies And Integration Points
It includes `<sound/soc.h>` for ASoC-facing types/macros and is consumed by `sma1307.c`. The control-name macros are part of the user-visible ALSA mixer ABI for this driver.

## Risks And Edge Cases
Any mismatch in address or bit definitions directly changes hardware programming. The setting file sizes and `mode_set[5]` bound must stay aligned with firmware-format expectations and the C driver's binary-mode enum. Several bit definitions are raw shifts/masks used directly by regmap updates, so tests should catch regressions in slot positions, fault bits, and PLL/control fields.

## Test Signals
Compile coverage of `sma1307.c`, mixer-control enumeration, TDM slot controls, fault-status decoding, firmware-mode selection, and device-ID validation are the main signals that these definitions remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1307.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_receiver.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_receiver.c

## Purpose
This file provides a dummy/stub ASoC codec for S/PDIF digital input receiver configurations where the controller handles the actual S/PDIF data path and no external codec register programming is needed.

## Important APIs, Types, And Functions
The component driver `soc_codec_spdif_dir` exposes one DAPM input widget `spdif-in` and a route to the capture stream. `dir_stub_dai` defines the `dir-hifi` capture DAI with 1 to 384 channels, broad sample-rate support including 8 kHz through 768 kHz and 128 kHz, and PCM plus IEC958 subframe format support. `spdif_dir_probe()` registers the component and DAI through `devm_snd_soc_register_component()`.

## Control Flow
Platform probe has no hardware initialization. It only registers the ASoC component/DAI. The module platform driver binds by platform name `spdif-dir` and optional OF compatible `linux,spdif-dir`.

## State And Persistence
The driver has no private state, no regmap, no cached data, and no power-management state beyond ASoC DAPM metadata.

## Dependencies And Integration Points
It depends on platform driver, OF matching, and ASoC DAPM/DAI APIs. It is intended for machine drivers or DT descriptions that need a codec endpoint for a S/PDIF receive controller.

## Risks And Edge Cases
The driver intentionally accepts a very broad channel/rate set, so machine/controller constraints must prevent unsupported hardware combinations. It has no status detection, lock detection, or channel-status handling; those must be supplied by the controller or board-specific stack.

## Test Signals
Probe binding by compatible/name, creation of the `dir-hifi` capture DAI, DAPM route visibility, and PCM constraint negotiation with the paired controller are the relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_receiver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_transmitter.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_transmitter.c

## Purpose
This file provides a dummy/stub ASoC codec for S/PDIF digital output transmitter configurations where no physical codec driver is required.

## Important APIs, Types, And Functions
`soc_codec_spdif_dit` defines a DAPM output widget `spdif-out` and a route from playback. `dit_stub_dai` defines the `dit-hifi` playback DAI with 1 to 384 channels, rates from 8 kHz to 768 kHz plus 128 kHz, and common PCM formats. `spdif_dit_probe()` registers the component and DAI.

## Control Flow
The platform driver named `spdif-dit` binds through platform name or OF compatible `linux,spdif-dit`. Probe performs a single ASoC registration and has no register or GPIO setup.

## State And Persistence
There is no private state or persistence. Power behavior is represented only through DAPM metadata and component flags such as idle bias and pmdown time use.

## Dependencies And Integration Points
The file integrates with machine drivers and controller drivers that need a codec endpoint for S/PDIF transmit paths. It depends on ASoC, PCM format constants, platform driver support, and OF matching.

## Risks And Edge Cases
As a stub, it cannot validate S/PDIF framing details, channel status, actual controller limits, or connector presence. Its permissive DAI capabilities require paired hardware drivers to impose real constraints.

## Test Signals
Probe/bind tests, playback DAI enumeration, DAPM route creation, and PCM-open negotiation with real S/PDIF controller constraints are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/spdif_transmitter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c

## Purpose
This is the I2C bus glue for the TI SRC4xxx/SRC4392 ASoC codec driver. It creates an I2C regmap and delegates all codec logic to the shared `src4xxx_probe()`.

## Important APIs, Types, And Functions
The central function is `src4xxx_i2c_probe()`, which calls `src4xxx_probe(&i2c->dev, devm_regmap_init_i2c(...), NULL)`. The file declares I2C ID `src4392`, OF compatible `ti,src4392`, and registers an `i2c_driver` named `src4xxx`.

## Control Flow
I2C core matches a device, probe initializes a devm regmap using `src4xxx_regmap_config`, and shared registration/configuration proceeds in `src4xxx.c`.

## State And Persistence
No private state is stored in this file. The shared driver stores state via `dev_set_drvdata()` after probe.

## Dependencies And Integration Points
It depends on Linux I2C, regmap, module device tables, and `src4xxx.h`. It is the transport-specific entry point for DT/I2C-described SRC4392 devices.

## Risks And Edge Cases
All probe errors are delegated through `src4xxx_probe()`. There is no explicit I2C match-data use, variant handling, or fallback if regmap creation fails beyond passing the error pointer to shared probe.

## Test Signals
I2C/DT binding, regmap creation failure handling, and successful shared component registration for a `ti,src4392` device cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.c

## Purpose
This file implements the shared ASoC codec support for TI SRC4xxx/SRC4392 devices. It exposes two serial audio ports, source/sample-rate-converter routing, digital receiver/transmitter routing, a volume control, regmap defaults/cache metadata, reset/power setup, and master-clock-driven divider/PLL programming.

## Important APIs, Types, And Functions
`struct src4xxx` stores the regmap, per-port master/slave flags, configured MCLK frequency, and device pointer. The exported `src4xxx_probe()` is called by bus glue and registers `src4xxx_driver` plus two DAIs. `src4xxx_regmap_config` is exported for bus-specific regmap creation.

The ASoC component defines `SRC Volume`, DAPM muxes for Port A/B output source, DIT source, SRC source, and DIR digital input source. `src4xxx_dai_driver[]` exposes `src4xxx-portA` and `src4xxx-portB`, each with stereo playback/capture and rates 44.1 kHz to 192 kHz. DAI ops are `src4xxx_set_dai_fmt()`, `src4xxx_set_mclk_hz()`, and `src4xxx_hw_params()`.

## Control Flow
Probe validates regmap, allocates state, stores drvdata, issues hardware reset through `SRC4XXX_PWR_RST_01`, powers the device, configures the receiver PLL reference to MCLK, enables recovered MCLK behavior, and registers the component/DAIs.

`set_fmt` records whether each DAI is clock master and writes I2S/LJ/RJ format bits. `set_sysclk` stores MCLK frequency. During `hw_params`, if the port is master, the driver computes `mclk_hz / sample_rate`, validates an integer ratio mapping to register values, writes transmitter divider bits, chooses known DIR PLL values for 24.576 MHz or 22.5792 MHz MCLK, writes receiver PLL registers, and updates the port clock divider. In slave mode it leaves MCLK setup alone.

## State And Persistence
`master[]` and `mclk_hz` are runtime state. Regmap uses RBTREE cache with defaults for power/reset, port controls, transmitter/receiver controls, GPIO, and SRC controls. Volatile registers include status/subcode/preamble/I/O ratio regions and reserved page ranges, preventing stale reads for live status.

## Dependencies And Integration Points
The driver depends on ASoC component/DAI/DAPM/control APIs, regmap, and definitions from `src4xxx.h`. It is transport-independent and expects bus wrappers such as `src4xxx-i2c.c` to supply a regmap.

## Risks And Edge Cases
The `switch_mode` callback parameter to `src4xxx_probe()` is unused. MCLK divider validation uses a limited formula and range, so unsupported ratios fail at runtime. Unknown MCLK frequencies do not fail PLL setup; dummy PLL values are written after an info message, which may leave DIR behavior unsuitable even though other functions continue. DAPM routes mention `"SRC mclk source"` without a widget/control in this file, suggesting incomplete routing or a stale route name.

## Test Signals
Probe/reset sequencing, both DAIs in master and slave mode, supported and unsupported MCLK/rate combinations, I2S/LJ/RJ format writes, DAPM mux route visibility, regmap cache/volatile behavior for status registers, and the I2C wrapper path should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h

## Purpose
This header contains the SRC4xxx register addresses, bit masks, register-address helper macros, read-only register definitions, and the shared probe/regmap declarations used by bus glue and the core driver.

## Important APIs, Types, And Definitions
It declares `src4xxx_probe(struct device *dev, struct regmap *regmap, void (*switch_mode)(struct device *dev))` and `extern const struct regmap_config src4xxx_regmap_config`. Register definitions cover reset/power, port A/B format and clock controls, transmitter controls, SRC/DIT IRQ fields, receiver controls and PLL, GPIO, SRC controls, page select, status/subcode/preamble, and I/O ratio registers. `SRC4XXX_BUS_FMT(id)` and `SRC4XXX_BUS_CLK(id)` compute per-port register addresses.

## Control Flow
No executable flow is defined. The core driver uses these symbols to set DAI format, clock dividers, power bits, DIR reference clocks, DAPM mux selectors, and regmap access metadata.

## State And Persistence
No state is allocated. The definitions govern how `src4xxx.c` stores cached defaults and which registers are treated as volatile.

## Dependencies And Integration Points
The declarations require `struct device` and `struct regmap` declarations from included kernel headers in users. The header is shared by `src4xxx.c` and `src4xxx-i2c.c`.

## Risks And Edge Cases
Incorrect register constants or bit masks can silently misroute the SRC/DIR/DIT datapaths. The public probe signature includes an unused `switch_mode` parameter, so future callers may assume a behavior not currently implemented.

## Test Signals
Compile coverage from core and I2C files, DAI format programming, power/reset writes, PLL register writes, and regmap volatile/default tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/src4xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2305.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2305.c

## Purpose
This file implements a minimal ASoC platform driver for the Analog Devices SSM2305 analog stereo amplifier. It models the analog input/output paths and toggles a shutdown GPIO from DAPM power events.

## Important APIs, Types, And Functions
`struct ssm2305` stores the `shutdown` GPIO descriptor. `ssm2305_power_event()` sets that GPIO according to whether the DAPM supply is powering on or down. `ssm2305_component_driver` provides DAPM inputs `L_IN`/`R_IN`, outputs `L_OUT`/`R_OUT`, and a `Power` supply. `ssm2305_probe()` allocates state, obtains the mandatory `shutdown` GPIO as initially low, and registers the component without a DAI.

## Control Flow
Platform probe obtains the GPIO and registers the component. When DAPM enables the input paths, the `Power` supply callback asserts/deasserts shutdown with `gpiod_set_value_cansleep()` based on event state.

## State And Persistence
Only the GPIO descriptor is stored. Hardware state is the shutdown GPIO output level. There is no register cache, DAI state, or persistent mixer state.

## Dependencies And Integration Points
The driver depends on platform devices, GPIO descriptors, OF compatible `adi,ssm2305`, and ASoC component/DAPM APIs. Machine drivers route audio to the analog DAPM endpoints.

## Risks And Edge Cases
The shutdown GPIO is mandatory; probe fails if it is absent. Correct polarity depends on GPIO descriptor flags in firmware. Since there is no DAI, this driver is strictly an analog amplifier endpoint, not a clock/data interface.

## Test Signals
DT binding with `shutdown-gpios`, probe failure without GPIO, DAPM route activation, and observed GPIO transitions on power-up/power-down are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.c

## Purpose
This file implements the Analog Devices SSM2518 digital amplifier as an I2C ASoC codec. It provides playback DAI operations, sysclk/rate constraints, serial format and TDM configuration, bias-level power management, optional enable GPIO handling, regmap caching, DAPM routes, and extensive DRC/mixer controls.

## Important APIs, Types, And Functions
`struct ssm2518` stores the regmap, right-justified mode flag, sysclk frequency, active PCM rate constraints, and optional enable GPIO. The file defines register addresses/masks, reg defaults, TLV tables, DRC enum strings, and `ssm2518_snd_controls[]`.

The main DAI callbacks are `ssm2518_startup()`, `ssm2518_hw_params()`, `ssm2518_mute()`, `ssm2518_set_dai_fmt()`, and `ssm2518_set_tdm_slot()`. Component sysclk configuration is `ssm2518_set_sysclk()`, and power transitions are handled by `ssm2518_set_bias_level()` plus `ssm2518_set_power()`. Probe is `ssm2518_i2c_probe()`.

## Control Flow
Probe allocates state, optionally asserts the enable GPIO, creates regmap, bypasses cache to issue reset, clears amplifier power-down, powers the device off into cache-only mode, and registers the component/DAI. Bias transition from OFF to STANDBY enables power/GPIO, clears software power-down/reset bits, and syncs regcache; transition to OFF sets software power-down, marks the cache dirty, toggles GPIO off, and switches regmap cache-only.

`set_sysclk` validates clock ID/source, chooses rate constraint lists based on sysclk families, stores sysclk, and optionally marks BCLK-as-system-clock mode. Startup applies the selected rate constraints to PCM runtime. `hw_params` looks up the master-clock selector for the requested rate/sysclk, programs sample-rate range, right-justified width if needed, disables auto sample-rate detection, and writes MCS bits. `set_dai_fmt` validates codec clock consumer mode, handles BCLK/LRCLK inversion, selects I2S/LJ/RJ/DSP_A/DSP_B formats, and writes SAI controls. `set_tdm_slot` validates transmit-only slots, extracts left/right slots from `tx_mask`, programs channel map, TDM slot count, and slot width.

## State And Persistence
Runtime format/sysclk decisions live in `right_j`, `sysclk`, and `constraints`. Regmap uses an RBTREE cache with defaults. Power-off makes the cache authoritative until the chip is powered again and synchronized. Mixer/DRC settings are cached through regmap.

## Dependencies And Integration Points
The driver depends on I2C, optional GPIO descriptors, regmap, ASoC component/DAI/DAPM/control APIs, PCM constraints, and `ssm2518.h` for public sysclk IDs. It binds to I2C ID and OF compatible `adi,ssm2518`.

## Risks And Edge Cases
Sysclk must be configured before `hw_params`; otherwise MCS lookup fails. Some formats use `SNDRV_PCM_FMTBIT_S32` rather than `S32_LE`, matching existing code but worth compile/API scrutiny. In TDM mode, only TX masks are accepted because the device is playback-only; machine drivers must pass slot masks accordingly. The enable GPIO is optional but gets consumer-name assignment even when absent, relying on GPIO helpers tolerating NULL.

## Test Signals
Probe/reset/cache transitions, enable GPIO behavior, sysclk families and PCM constraint enforcement, `hw_params` failure for unsupported rate/sysclk combinations, all DAI formats/inversions, TDM slot masks for mono/stereo/multi-slot modes, mute control, and suspend/off-to-standby cache sync are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.h

## Purpose
This header provides the public sysclk selector definitions for the SSM2518 codec driver.

## Important APIs, Types, And Definitions
It defines `SSM2518_SYSCLK` as clock ID 0 and `enum ssm2518_sysclk_src` with `SSM2518_SYSCLK_SRC_MCLK` and `SSM2518_SYSCLK_SRC_BCLK`.

## Control Flow
There is no control flow. `ssm2518.c` uses these constants in its component `.set_sysclk` callback to validate clock ID and source.

## State And Persistence
The header has no state. It defines ABI-style constants used by machine drivers when configuring the codec.

## Dependencies And Integration Points
Machine drivers and the codec implementation include this header to agree on sysclk IDs/sources.

## Risks And Edge Cases
Because only one clock ID is defined, callers using other IDs fail with `-EINVAL`. BCLK source mode has a hardware wiring caveat documented in the C file: BCLK must be connected to MCLK and the BCLK pin left unconnected.

## Test Signals
Compile-time inclusion and machine-driver calls to `snd_soc_component_set_sysclk()` with both source values validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2518.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-i2c.c

## Purpose
This is the I2C transport wrapper for the SSM2602/SSM2603/SSM2604 codec family. It creates an I2C regmap and delegates codec registration to the shared `ssm2602_probe()`.

## Important APIs, Types, And Functions
`ssm2602_i2c_probe()` calls `ssm2602_probe(&client->dev, (uintptr_t)i2c_get_match_data(client), devm_regmap_init_i2c(...))`. The I2C ID table maps `ssm2602` and `ssm2603` to `SSM2602`, and `ssm2604` to `SSM2604`. OF compatibles are declared for all three.

## Control Flow
I2C probe initializes a 7-bit-register/9-bit-value regmap with the shared config and hands type/regmap to the core driver. Module registration is via `module_i2c_driver()`.

## State And Persistence
No local state is stored. The core probe allocates and stores private codec state on the device.

## Dependencies And Integration Points
It depends on Linux I2C, regmap, ASoC headers, and `ssm2602.h`. It supports I2C devices whose address is selected externally by GPIO5 during power-up.

## Risks And Edge Cases
The OF match entries do not carry `.data`, so `i2c_get_match_data()` may not provide the intended type for OF-instantiated devices unless the I2C ID path supplies it. This can make variant selection worth testing carefully for `adi,ssm2604`.

## Test Signals
I2C ID binding for each chip name, OF binding for each compatible, regmap creation, correct variant selection, and successful shared component registration cover this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c

## Purpose
This is the SPI transport wrapper for the SSM2602 codec. It creates an SPI regmap and delegates all codec logic to the shared core.

## Important APIs, Types, And Functions
`ssm2602_spi_probe()` calls `ssm2602_probe(&spi->dev, SSM2602, devm_regmap_init_spi(...))`. The SPI driver matches OF compatible `adi,ssm2602` and registers as `ssm2602`.

## Control Flow
SPI core matches the device, probe creates the regmap, and the shared driver handles reset, controls, DAPM, DAI, and registration.

## State And Persistence
No local state exists. Core state is stored by `ssm2602_probe()`.

## Dependencies And Integration Points
It depends on SPI, regmap, ASoC declarations, and `ssm2602.h`. It only supports the `SSM2602` variant over SPI in this file.

## Risks And Edge Cases
SSM2603/SSM2604 are not exposed through this wrapper. SPI regmap failure is delegated to shared probe via error pointer handling.

## Test Signals
SPI/OF binding, regmap creation failure handling, and successful shared component registration for an SSM2602 SPI device are the useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.c

## Purpose
This file implements the shared ASoC codec driver for the Analog Devices SSM2602/SSM2603/SSM2604 family. It provides playback/capture DAI support, controls for capture/playback/analog path, DAPM topologies for 2602 and 2604 variants, clock/rate coefficient programming, bias-level power management, reset patching, and a shared regmap/probe API for I2C/SPI wrappers.

## Important APIs, Types, And Functions
`struct ssm2602_priv` stores sysclk, sysclk-derived PCM constraints, regmap, chip type, and clock-output power bits. Exported APIs are `ssm2602_probe()` and `ssm2602_regmap_config`.

The DAI callbacks are `ssm2602_startup()`, `ssm2602_hw_params()`, `ssm2602_mute()`, `ssm2602_set_dai_sysclk()`, and `ssm2602_set_dai_fmt()`. Component callbacks include `ssm260x_component_probe()`, type-specific `ssm2602_component_probe()`/`ssm2604_component_probe()`, `ssm2602_resume()`, and `ssm2602_set_bias_level()`. `ssm2602_get_coeff()` maps MCLK/rate pairs to sample-rate register fields.

## Control Flow
Shared probe validates regmap, allocates state, stores type/regmap, and registers the component/DAI. Component probe resets the codec, registers a patch that activates the digital core and powers output/DAC/chip in a safe sequence, sets linked update bits for left/right input volumes, selects line-in plus mic boost defaults, then adds variant-specific controls/routes.

Startup applies sysclk-derived rate constraints when set. `hw_params` chooses the sample-rate coefficient for current sysclk and requested rate, writes `SSM2602_SRATE`, and updates IFACE data length based on PCM width. `set_sysclk` either configures input sysclk constraints/frequency or manages output clock/oscillator power-down bits. `set_fmt` validates master/slave, I2S/RJ/LJ/DSP_A/DSP_B, and inversion flags, then writes IFACE.

Bias transitions set power-down bits for ON/STANDBY/OFF. Resume synchronizes regcache.

## State And Persistence
The codec cannot be read over two-wire control in some modes, so regmap cache is central. Defaults cover all cached registers except reset. `sysclk_constraints` persist until changed by machine driver. `clk_out_pwr` persists desired output clock and oscillator power-down state across bias transitions.

## Dependencies And Integration Points
The driver depends on regmap, ASoC controls/DAPM/DAI, PCM constraints, and variant definitions from `ssm2602.h`. I2C and SPI wrappers instantiate it. Machine drivers must set sysclk for reliable rate programming.

## Risks And Edge Cases
`hw_params` fails if no supported sysclk/rate coefficient exists. Variant selection from the I2C wrapper should be tested for OF devices. The mic switch intentionally sleeps 500 ms to avoid artifacts, which affects capture path activation latency. The reset patch and power sequencing are important for avoiding playback distortion after power-up.

## Test Signals
Shared probe through both I2C and SPI wrappers, reset/patch application, SSM2602 versus SSM2604 DAPM/control differences, sysclk constraint enforcement, supported/unsupported rates for 12.288/11.2896/12 MHz families, all DAI formats/inversions/widths, mute behavior, bias transitions, and resume regcache sync are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.h

## Purpose
This header defines the public shared interface and register/bit constants for the SSM2602/SSM2603/SSM2604 codec family.

## Important APIs, Types, And Definitions
It declares `enum ssm2602_type` with `SSM2602` and `SSM2604`, exported `ssm2602_regmap_config`, and `ssm2602_probe()`. Register definitions cover line/headphone volumes, analog/digital paths, power, interface, sampling, active, and reset registers. Field masks cover input/output volume update bits, analog path features, digital mute/de-emphasis/high-pass filter, power-down bits, interface format/length/master/inversion, sample-rate/core/clkout dividers, active control, and clock IDs `SSM2602_SYSCLK`, `SSM2602_CLK_CLKOUT`, and `SSM2602_CLK_XTO`.

## Control Flow
No executable flow is present. Core and wrapper files use these constants to create regmap, program audio format/rates, apply power sequencing, and expose controls.

## State And Persistence
No state is stored here. Constants define cached register count (`SSM2602_CACHEREGNUM`) and the shared ABI between wrappers and the core.

## Dependencies And Integration Points
It includes `<linux/regmap.h>` and forward declares `struct device`. It is included by `ssm2602.c`, `ssm2602-i2c.c`, and `ssm2602-spi.c`.

## Risks And Edge Cases
Register width assumptions in the core regmap config depend on these register constants being within the 7-bit address space and reset at `0x0f`. Variant coverage is limited to the enum values here.

## Test Signals
Compile coverage, regmap config creation, wrapper calls to `ssm2602_probe()`, and DAI/sysclk tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm2602.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm3515.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm3515.c

## Purpose
This file implements an I2C ASoC driver for the Analog Devices SSM3515 mono digital amplifier. It exposes playback DAI support, mute/volume/analog-gain controls, serial format/TDM setup, basic DAPM routes, regmap caching, software reset, and fault logging at stream teardown.

## Important APIs, Types, And Functions
`struct ssm3515_data` holds device and regmap pointers. `ssm3515_i2c_regmap` defines 8-bit registers/values, flat cache, defaults, and volatile status/VBAT registers. `ssm3515_asoc_component` registers controls, DAPM widgets/routes, and component probe. DAI ops are `ssm3515_mute()`, `ssm3515_hw_params()`, `ssm3515_set_fmt()`, `ssm3515_set_tdm_slot()`, and `ssm3515_hw_free()`.

## Control Flow
I2C probe allocates state, initializes regmap, performs software reset by setting `SSM3515_PWR_S_RST`, reinitializes regcache, and registers the component/DAI. Component probe starts muted and clears master software power-down.

`hw_params` accepts 16- or 24-bit samples, programs SAI data width, maps sample rate ranges to DAC FS values, and writes DAC FS bits. `set_fmt` supports I2S and left-justified formats, BCLK inversion, and frame inversion; it always configures the serial input in TDM-style mode and treats the FSYNC mode bit as practical polarity selection. `set_tdm_slot` accepts a single TX slot, validates slot width 16/24/32/48/64, and programs TDM BCLK count and slot number. `hw_free` reads status and logs any faults because there is no live notification path.

## State And Persistence
State is mostly in hardware/regmap; no explicit private DAI format fields are stored. Regmap cache preserves defaults and runtime controls, while status and VBAT are volatile. Component probe leaves the device unmuted only when stream mute clears later.

## Dependencies And Integration Points
The driver depends on I2C, OF compatible `adi,ssm3515`, regmap, bitfield helpers, ASoC, and PCM parameter APIs. It registers one mono playback DAI named `SSM3515 SAI`.

## Risks And Edge Cases
The DAI advertises `SNDRV_PCM_RATE_CONTINUOUS`, but `hw_params` only accepts specific rate ranges, so runtime validation is essential. The supported PCM formats use `SNDRV_PCM_FMTBIT_S16_LE | SNDRV_PCM_FMTBIT_S24_LE`, but `hw_params` checks `SNDRV_PCM_FORMAT_S16`/`S24`; depending on ALSA enum aliases, this should be scrutinized. Faults are only checked on `hw_free`, so transient faults during long playback are not reported immediately.

## Test Signals
I2C probe/reset/cache reinit, component probe mute/power bits, all supported rate buckets, 16/24-bit format handling, I2S/LJ polarity combinations, TDM slot validation, mute control, and fault status logging on stream close should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm3515.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm4567.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ssm4567.c

## Purpose
This file implements the Analog Devices SSM4567 amplifier as an I2C ASoC codec. It supports mono playback plus a sense capture path, DAPM-controlled amp/sense blocks, SAI/TDM/PDM format setup, mute/rate programming, bias-level power management with regcache-only off state, and OF/ACPI matching.

## Important APIs, Types, And Functions
`struct ssm4567` stores the regmap. Register access is constrained by `ssm4567_readable_reg()`, `ssm4567_writeable_reg()`, and `ssm4567_volatile_reg()`. `ssm4567_component_driver` exposes controls and DAPM routes. `ssm4567_dai_ops` includes `ssm4567_hw_params()`, `ssm4567_mute()`, `ssm4567_set_dai_fmt()`, and `ssm4567_set_tdm_slot()`. Power transitions use `ssm4567_set_bias_level()` and `ssm4567_set_power()`.

## Control Flow
I2C probe allocates state, creates regmap, writes the soft reset register, powers the device off into cache-only mode, and registers component/DAI. Bias transition from OFF to STANDBY writes soft reset, clears software power-down, and syncs regcache; transition to OFF sets software power-down, marks cache dirty, and switches cache-only mode.

`hw_params` maps requested sample rate to DAC FS buckets from 8 kHz to 192 kHz. `mute` toggles the DAC mute bit. `set_tdm_slot` validates a single TX slot, optional matching RX mask, and 32/48/64-bit slot widths before programming auto-slot off/slot and TDM BCLK count. `set_dai_fmt` only supports codec clock consumer mode, handles BCLK/FSYNC inversion, and supports I2S, LJ, DSP_A, DSP_B, and PDM.

## State And Persistence
Regmap RBTREE cache stores register defaults and runtime controls. Off state is represented by cache-only mode plus dirty cache; resume to standby resets hardware and syncs cached settings. DAPM routes control amplifier boost and current/voltage/VBAT sense paths.

## Dependencies And Integration Points
The driver depends on I2C, regmap, ASoC, PCM params, optional OF compatible `adi,ssm4567`, and ACPI ID `INT343B`. The DAI exposes playback stream `Playback` and capture stream `Capture Sense`.

## Risks And Edge Cases
`ssm4567_set_tdm_slot()` and `ssm4567_set_dai_fmt()` use `snd_soc_dai_get_drvdata(dai)` while probe stores data with `i2c_set_clientdata()` and component callbacks commonly use component drvdata; this should be verified because a NULL/private-data mismatch would break format/TDM setup. The driver does not surface status faults as controls or logs during normal flow. PDM mode shares the same DAI and may need board-level constraints.

## Test Signals
I2C/OF/ACPI binding, soft reset and cache-only power transitions, playback and capture DAI enumeration, sample-rate bucket programming, mute, I2S/LJ/DSP/PDM formats, TDM slot validation, DAPM amp/sense routing, and private-data availability in DAI callbacks are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ssm4567.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.c

## Purpose
This file implements the ST STA32x/STA326/STA328/STA329 2.1-channel digital amplifier ASoC codec. It provides playback DAI setup, a large mixer/control surface including DSP coefficients, DAPM output routing, regulator/clock/reset handling, platform/DT policy programming, regmap cache management, and an optional ESD watchdog that restores configuration after unexpected chip reset.

## Important APIs, Types, And Functions
`struct sta32x_priv` stores regmap, optional XTI clock, regulator bulk data, component pointer, platform data, MCLK/format, coefficient shadow RAM, delayed watchdog work, shutdown flag, reset GPIO, and coefficient mutex. The file defines reg defaults, regmap access tables, supply names, TLV/enums, byte controls for biquad/mixer/scaling coefficients, DAPM widgets/routes, DAI ops, and component/driver structures.

Coefficient APIs are `sta32x_coefficient_info()`, `sta32x_coefficient_get()`, `sta32x_coefficient_put()`, `sta32x_sync_coef_shadow()`, and `sta32x_cache_sync()`. DAI functions are `sta32x_set_dai_sysclk()`, `sta32x_set_dai_fmt()`, and `sta32x_hw_params()`. Power and lifecycle are `sta32x_startup_sequence()`, `sta32x_set_bias_level()`, `sta32x_probe()`, `sta32x_remove()`, `sta32x_i2c_probe()`, and optional DT parser `sta32x_probe_dt()`.

## Control Flow
I2C probe allocates state, initializes coefficient mutex, gets platform data or parses DT, obtains optional XTI clock and reset GPIO, requests supplies, initializes regmap, stores client data, and registers the component/DAI. Component probe enables XTI and regulators, toggles reset, programs thermal/fault/drop-compensation/power/output/channel-mapping options from platform data, initializes coefficient shadow defaults, optionally initializes the watchdog work, forces standby bias, and drops the extra regulator enable.

The DAI requires machine drivers to set MCLK before `hw_params`. `hw_params` computes MCLK/sample-rate ratio, finds interpolation ratio and MCS index, maps sample width plus I2S/LJ/RJ format to CONFB SAI bits, and updates CONFA/CONFB. Bias transitions enable regulators and restore cache/coefficient state when waking from OFF, toggle power-down/EAPD bits for prepare/standby/off, stop watchdog and disable reset/supplies on OFF.

The watchdog periodically bypasses cache to read CONFA from hardware and compares it to the cached value. If they differ, it marks the cache dirty and calls `sta32x_cache_sync()` to rewrite coefficients and registers while muted.

## State And Persistence
The regmap uses MAPLE cache and explicit access/volatile tables. Coefficients are persisted in `coef_shadow[]` because the coefficient load/read window is indirect and volatile. Platform data determines many one-time hardware-policy fields. Regulator/clock/GPIO state tracks ASoC bias levels. Optional watchdog state persists while active.

## Dependencies And Integration Points
The file depends on I2C, OF, regmap, regulators, optional clock, GPIO descriptors, delayed work, ASoC, and public platform data from `<sound/sta32x.h>` plus register definitions from `sta32x.h`. It binds I2C IDs `sta326`, `sta328`, and `sta329`, and OF compatible `st,sta32x`.

## Risks And Edge Cases
Machine drivers must call `set_sysclk`; otherwise `hw_params` fails with `-EIO`. Coefficient put lacks a mutex while get uses one, so concurrent coefficient updates/readback could interleave. The watchdog assumes CONFA mismatch indicates reset and can trigger a full cache sync during runtime. DT/platform data is dereferenced in component probe, so missing platform data on non-DT systems would be unsafe. Power sequencing is regulator/GPIO dependent and needs board-specific validation.

## Test Signals
Probe with DT and platform data, regulator/clock/reset error paths, MCLK/rate ratio validation, I2S/LJ/RJ and width combinations, coefficient byte controls including shadow restore, bias OFF/STANDBY/PREPARE transitions, watchdog recovery, platform property programming, DAPM outputs, and remove cleanup are essential tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h

## Purpose
This header defines the STA32x/STA326 register addresses, bit fields, coefficient indices, and count constants used by `sta32x.c`.

## Important APIs, Types, And Definitions
It defines `STA32X_REGISTER_COUNT`, `STA32X_COEF_COUNT`, core control registers from `CONFA` through `FDRC2`, coefficient access registers (`CFADDR2`, coefficient byte windows, `CFUD`), mute/volume/config registers, and field masks/shifts for clock selection, serial format, thermal/fault behavior, automodes, output mapping, limiter fields, and coefficient update commands. Coefficient offsets enumerate biquad bases, crossover bases, pre/postscales, thermal postscale, and mixer coefficients.

## Control Flow
No executable flow is defined. The C file uses these constants for regmap ranges, mixer controls, coefficient indirect addressing, DAI format/rate setup, platform-data programming, and power bits.

## State And Persistence
No storage is defined. `STA32X_COEF_COUNT` sizes the C driver's coefficient shadow array and must remain aligned with coefficient offset definitions.

## Dependencies And Integration Points
The header is private to the STA32x codec implementation and is included by `sta32x.c`. Public board policy comes from `<sound/sta32x.h>`, not this file.

## Risks And Edge Cases
Coefficient offsets and register bit masks must match the hardware data sheet because the driver writes indirect coefficient windows using these indices. Bad masks can break thermal/fault policy, output mapping, or mute behavior without compile-time symptoms.

## Test Signals
Compile coverage, coefficient control read/write tests, DAI hw_params register programming, platform property programming, and watchdog cache restore paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.c

## Purpose
This file implements the ST STA350 2.1-channel high-efficiency digital amplifier ASoC codec. It is structurally similar to STA32x support but targets the STA350 register map and platform options, with playback DAI setup, DSP coefficient controls, DAPM outputs, regulator/reset/power-down GPIO sequencing, regmap caching, DT/platform configuration, and bias-level power management.

## Important APIs, Types, And Functions
`struct sta350_priv` stores regmap, supplies, platform data, MCLK/format, coefficient shadow RAM, shutdown flag, reset and power-down GPIOs, and coefficient mutex. The file defines reg defaults, regmap access tables, supply names, TLV/enums, byte coefficient controls, DAPM widgets/routes, `sta350_dai_ops`, `sta350_component`, and the I2C driver.

Coefficient functions mirror STA32x: `sta350_coefficient_info()`, `sta350_coefficient_get()`, `sta350_coefficient_put()`, `sta350_sync_coef_shadow()`, and `sta350_cache_sync()`. DAI functions are `sta350_set_dai_sysclk()`, `sta350_set_dai_fmt()`, and `sta350_hw_params()`. Lifecycle/power functions are `sta350_startup_sequence()`, `sta350_set_bias_level()`, `sta350_probe()`, `sta350_remove()`, `sta350_probe_dt()`, and `sta350_i2c_probe()`.

## Control Flow
I2C probe allocates state, initializes the coefficient mutex, obtains platform data or parses DT, gets optional reset and power-down GPIOs, requests regulators, initializes regmap, stores client data, and registers the component. Component probe enables supplies, powers/toggles reset, programs thermal/fault/output/drop-compensation/overcurrent/power/distortion/misc settings from platform data, initializes coefficient shadow defaults, forces standby bias, and releases the extra supply enable.

`set_sysclk` stores MCLK. `set_fmt` supports codec clock consumer mode with I2S/LJ/RJ and limited inversion choices. `hw_params` requires MCLK, maps sample rate to interpolation ratio and MCLK/sample ratio to MCS, maps width/format to SAI fields, and updates CONFA/CONFB. Bias transitions enable supplies and sync cache from OFF to STANDBY, set full-power bits in PREPARE, and clear power/reset/GPIOs and disable supplies in OFF.

## State And Persistence
Regmap uses MAPLE cache with explicit read/write/volatile tables. `coef_shadow[]` persists indirect DSP coefficients across cache sync and power cycles. Platform data parsed from DT controls many hardware policy bits. GPIO states represent hardware reset and power-down pins.

## Dependencies And Integration Points
The driver depends on I2C, OF, regmap, regulators, GPIO descriptors, ASoC, public platform data from `<sound/sta350.h>`, and register constants from `sta350.h`. It binds OF compatible `st,sta350` and I2C ID `sta350`.

## Risks And Edge Cases
Machine drivers must set MCLK before stream setup. Coefficient put is not mutex-protected while get is, allowing possible concurrent indirect-register races. `sta350_cache_sync()` reads `STA350_CFUD` into `mute` and then writes it to `STA350_MMUTE`, which looks suspicious because mute state should come from `STA350_MMUTE`. DT parsing warns but continues on unsupported FFX mode or powerdown divider. Missing platform data on non-DT systems would make component probe unsafe.

## Test Signals
DT property parsing, regulator/GPIO sequencing, MCLK/rate ratio validation, format/width mappings, coefficient controls and shadow restore, cache sync correctness, bias transitions, DAPM routes, and invalid DT property warnings should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.h

## Purpose
This header defines STA350 register addresses, bit fields, mute/control shifts, miscellaneous bits, coefficient indices, and count constants used by `sta350.c`.

## Important APIs, Types, And Definitions
It defines `STA350_REGISTER_COUNT`, `STA350_COEF_COUNT`, core config/volume/automode/channel/limiter/coefficient/status/EQ/RMS/misc registers, field shifts/masks for CONFA through CONFF, mute bits, automode and channel configuration fields, limiter shifts, coefficient update bits, coefficient offsets, and miscellaneous register bits such as `CPWMEN`, `BRIDGOFF`, `NSHHPEN`, `RPDNEN`, and powerdown-delay divider masks.

## Control Flow
No executable logic is present. The C driver uses the definitions for regmap access tables, mixer controls, indirect coefficient operations, hw_params register writes, DT/platform policy programming, power control, and cache sync.

## State And Persistence
No state is allocated. The coefficient count and offsets define the layout of `sta350_priv.coef_shadow`.

## Dependencies And Integration Points
This private header is included by `sta350.c`; board-level platform definitions are supplied by `<sound/sta350.h>`.

## Risks And Edge Cases
The status register comments note reserved ranges around `0x2d`, while the constants expose `STA350_STATUS` at `0x2d`; regmap range definitions must remain consistent with the actual hardware map. Coefficient and bit-field errors can corrupt DSP programming or board power policy.

## Test Signals
Compile coverage, coefficient get/put, hw_params clock/format writes, DT policy writes, cache sync, and bias/power tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta350.h -->
