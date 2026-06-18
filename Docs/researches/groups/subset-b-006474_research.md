# subset-b-006474 Research

Grouped source research for ASoC codec drivers under `sources/distributed-fs/ceph-client/sound/soc/codecs`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tda7419.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tda7419.c

## Purpose

`tda7419.c` is an ALSA SoC component driver for the ST TDA7419 car-audio processor. It exposes the device's input selectors, loudness, mute timing, tone controls, speaker attenuation, subwoofer, mixer, and spectrum-analyzer settings as ALSA controls and DAPM routes over an I2C-backed regmap.

## Important APIs, Types, and Functions

The driver defines register and bit-position constants for all 18 TDA7419 registers, `struct tda7419_data` for the regmap pointer, and `struct tda7419_vol_control` for custom signed/inverted volume controls. `tda7419_vol_info()`, `tda7419_vol_get()`, and `tda7419_vol_put()` implement custom ALSA control conversion around `TDA7419_SINGLE_TLV()` and `TDA7419_DOUBLE_R_TLV()`. The component surface is `tda7419_component_driver`, and hardware binding is through `tda7419_probe()` plus the `i2c_driver` with `st,tda7419` OF match.

## Control Flow

Probe allocates private state, initializes an 8-bit regmap, writes every default value to hardware, then registers an ASoC component with no DAI. Runtime flow is driven by mixer controls and DAPM: mux widgets choose main/second/rear sources, switches gate mix/subwoofer routes, and output widgets expose front/rear/subwoofer pins. Volume control writes update the corresponding hardware registers through `snd_soc_component_update_bits()`.

## State and Persistence Behavior

The device registers are not readable; `tda7419_readable_reg()` always returns false. State therefore lives in the regmap cache and in explicitly written hardware registers. Probe resets the chip state by writing documented defaults because there is no soft reset and previous boot-stage programming could leave hardware/cache mismatched.

## Dependencies and Integration Points

The driver depends on Linux I2C, regmap, and ASoC component/control/DAPM helpers. It integrates with board audio routing as a pure component with analog inputs `SE*`, `DIFF*`, `MIX` and outputs `OUTLF/OUTRF/OUTLR/OUTRR/OUTSW`; no PCM DAI is registered.

## Risks and Edge Cases

The unreadable register model makes cache coherency critical after any external reset or power loss. Custom signed volume mapping has thresholds and inversion semantics that can regress user-visible dB values. `soc_sub_enable_switch_controls` uses `TDA7419_MIX_ENABLE` rather than `TDA7419_SUB_ENABLE`, which is a suspicious coupling to verify against the datasheet. Because all defaults are `0xfe`, bad reset assumptions can affect many controls at once.

## Test Signals

Useful signals include I2C probe/register-write smoke tests, `amixer` round trips for signed master/tone/speaker controls, DAPM route validation for main/second/rear/subwoofer paths, suspend/reset cache-coherency tests on boards that power-cycle the chip, and static review of bit assignments against the TDA7419 datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tda7419.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.c

## Purpose

`tfa9879.c` is an ASoC I2C codec driver for the NXP TFA9879 amplifier. It exposes a playback-only DAI, output volume and tone controls, DAPM power sequencing, and serial-interface setup for I2S/left-justified/right-justified formats.

## Important APIs, Types, and Functions

`struct tfa9879_priv` stores the regmap and whether the active interface is LSB/right justified. `tfa9879_hw_params()` maps sample rate and sample width to `TFA9879_I2S_FS_*` and `TFA9879_I2S_SET_*` fields. `tfa9879_set_fmt()` validates codec clock-slave mode, BCLK polarity, and serial format. `tfa9879_mute_stream()` controls software mute. The component uses `tfa9879_component`, `tfa9879_dai_ops`, `tfa9879_dai`, and the I2C probe path that initializes a 16-bit regmap from `tfa9879_regs`.

## Control Flow

I2C probe allocates private data, creates the regmap, stores driver data, and registers the component and DAI. The machine driver calls `set_fmt()` before stream startup to establish serial mode. `hw_params()` then programs sample rate and, for right-justified operation, the exact LSB-justified width. DAPM powers `POWER`, then the DAC, then `LINEOUT`; mixer controls adjust PCM volume and bass/treble gain/corner frequency.

## State and Persistence Behavior

Register defaults are cached in an RBTREE regcache, with `TFA9879_MISC_STATUS` marked volatile. Runtime mutable state is limited to the cached register values and `lsb_justified`, which affects later `hw_params()` programming. There is no runtime PM or explicit reset sequence in this file.

## Dependencies and Integration Points

The driver depends on Linux I2C/regmap and ASoC DAI/component helpers. It includes `tfa9879.h` for register contracts. Integration is through an I2C device named `tfa9879`, a playback stream named `HiFi Playback`, and a line output endpoint.

## Risks and Edge Cases

Only 16-bit and 24-bit sample widths are accepted, and only rates listed up to 96 kHz map to hardware values. The driver only supports codec clock consumer mode (`SND_SOC_DAIFMT_CBC_CFC`). Right-justified width is deferred to `hw_params()`, so invalid sequencing or missing `set_fmt()` can leave stale width settings. Regmap writes in the DAI callbacks are not checked for errors.

## Test Signals

Test with each accepted rate, 16/24-bit width, and I2S/left/right-justified formats. Verify mute toggles `TFA9879_MISC_CONTROL`, DAPM power toggles `TFA9879_DEVICE_CONTROL`, volume/tone controls round trip, and unsupported formats/rates fail with `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.h

## Purpose

`tfa9879.h` is the private register definition header for the NXP TFA9879 ASoC driver. It names all device registers and bit masks/shifts used by `tfa9879.c` for device control, serial audio format, PCM/IOM2 framing, equalizer coefficients, bypass/DRC/tone controls, volume, mute, power limiting, and status flags.

## Important APIs, Types, and Functions

There are no functions or data structures. The API surface is macro-only: register addresses from `TFA9879_DEVICE_CONTROL` through `TFA9879_MISC_STATUS`, serial-interface values such as `TFA9879_I2S_FS_48000` and `TFA9879_I2S_SET_I2S_24`, and masks for mute, power-up, bypass, DRC, bass/treble, and status events.

## Control Flow

This header has no runtime control flow. Its constants are consumed by the driver during probe default setup, DAI format negotiation, `hw_params()` sample-rate/width programming, mute control, and ALSA mixer declarations.

## State and Persistence Behavior

The file owns no state. It defines the hardware state layout that the 16-bit regmap caches and writes to the amplifier. Any macro change affects how persistent register bits are interpreted by the driver.

## Dependencies and Integration Points

The header is included only by the TFA9879 codec implementation and intentionally avoids external includes. It is the binding between readable C names and the datasheet register map.

## Risks and Edge Cases

Mask/shift errors silently redirect controls to wrong bits. Several fields are defined but not currently exposed by the driver, such as equalizer coefficients, DRC, PCM/IOM2 slots, and fault/status bits, so future changes should reuse these definitions rather than duplicate them. Numeric sample-rate encodings must remain aligned with `tfa9879_hw_params()`.

## Test Signals

Compile coverage of `tfa9879.c`, register-write traces for format/rate/mute paths, and datasheet comparison of all mask/shift values are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa9879.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa989x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tfa989x.c

## Purpose

`tfa989x.c` supports NXP/Goodix TFA9890/TFA9895/TFA9897 smart speaker amplifiers in a simplified DSP-bypass mode. It verifies the hardware revision, applies revision-specific initialization, disables the undocumented CoolFlux DSP path, and registers a playback DAI with DAPM speaker/receiver routing.

## Important APIs, Types, and Functions

`struct tfa989x_rev` maps an expected revision ID to an init function. `struct tfa989x` stores revision data, the `vddd` regulator, and optional TFA9897 receiver-mode GPIO. Revision setup is split across `tfa9890_init()`, `tfa9895_init()`, and `tfa9897_init()`. `tfa989x_dsp_bypass()` programs the common bypass path. `tfa989x_hw_params()` maps rates with `tfa989x_find_sample_rate()`. `tfa989x_put_mode()` combines a TFA9897 ALSA enum write with GPIO receiver-mode control.

## Control Flow

I2C probe gets OF match data, enables the `vddd` regulator, creates a regmap, does a dummy revision read, verifies the revision ID, resets I2C registers, runs the revision init hook, enables DSP bypass, disables regcache bypass, and registers the component/DAI. DAPM powers `POWER`, then `AMPE`, then `OUT`. For TFA9897 only, component probe adds a `Mode` enum that selects speaker or receiver.

## State and Persistence Behavior

Hardware-visible state is written during probe while regcache bypass is active, then normal cached regmap operation resumes. The regulator is disabled by a managed cleanup action. There is no firmware profile persistence; the driver deliberately avoids proprietary DSP containers and accepts the reduced feature set.

## Dependencies and Integration Points

Dependencies are I2C, regmap, regulators, optional GPIO descriptors, and ASoC. Integration is OF-only via `nxp,tfa9890`, `nxp,tfa9895`, or `nxp,tfa9897`, with a `vddd` supply and optional `rcv` GPIO for TFA9897.

## Risks and Edge Cases

The driver bypasses the DSP, so speaker protection/optimization and volume profiles may be absent. Revision mismatch aborts probe, which is safer but sensitive to match data errors. Only S16_LE playback from 8 kHz to 48 kHz is exposed. Initialization writes include undocumented/hidden registers, so datasheet drift or incompatible silicon variants are risky.

## Test Signals

Validate revision detection on all compatible strings, regulator cleanup on failed probe paths, sample-rate programming, DAPM power-up to audible output, optional receiver GPIO behavior on TFA9897, and absence of I2C errors during hidden-register init sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tfa989x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adc3xxx.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adc3xxx.c

## Purpose

`tlv320adc3xxx.c` is an ASoC I2C capture codec driver for TI TLV320ADC3001/ADC3101 devices. It configures ADC clocks, PLL/dividers, serial audio format, analog/digital input routing, AGC, miniDSP IIR coefficients, micbias pins, and a small gpiolib surface for GPIO/MICBIAS outputs.

## Important APIs, Types, and Functions

`struct adc3xxx` stores device type, MCLK, regmap, reset GPIO, PLL mode, sysclk, DT pin config, master/PLL route state, and `gpio_chip`. `adc3xxx_divs[]` is the clock table. `adc3xxx_get_divs()`, `adc3xxx_setup_pll()`, and `adc3xxx_hw_params()` select and program PLL/NADC/MADC/AOSR/BDIV. `adc3xxx_set_dai_sysclk()` accepts PLL auto/enable/bypass through `clk_id`; `adc3xxx_set_dai_fmt()` programs master/slave and I2S/DSP/right/left-justified modes. `adc3xxx_coefficient_*()` exposes 16-bit coefficient arrays. GPIO behavior is implemented by `adc3xxx_gpio_request()`, `adc3xxx_gpio_direction_out()`, `adc3xxx_gpio_set()`, and `adc3xxx_gpio_get()`.

## Control Flow

Probe allocates state, obtains reset GPIO and MCLK, enables the clock, parses DT pin/micbias properties, initializes a paged regmap, toggles hardware reset, configures GPIO/MICBIAS pins, and registers the component/DAI. During stream setup, `set_sysclk()` records clock mode and frequency; `set_fmt()` updates interface format and dynamically adds/removes DAPM routes for master-generated BCLK; `hw_params()` selects a supported divider row and dynamically adds/removes the PLL route depending on whether that row uses the PLL.

## State and Persistence Behavior

Registers are cached with an RBTREE regcache over pages 0, 1, and 4. Runtime state includes selected PLL usage, master mode, sysclk, and GPIO/MICBIAS values. GPIO output state persists in hardware registers and is readable via `gpio_get()`. Remove disables MCLK, unregisters GPIOs, and unregisters the component.

## Dependencies and Integration Points

The driver depends on I2C, clocks, reset GPIO, OF properties from `dt-bindings/sound/tlv320adc3xxx.h`, regmap, gpiolib, and ASoC. It integrates as a capture-only DAI `tlv320adc3xxx-hifi` with up to two channels and board-specific analog/digital input routing through DAPM.

## Risks and Edge Cases

The driver requires MCLK even though the chip could theoretically use BCLK. Divider support is table-limited, and PLL mode constraints can reject otherwise valid MCLK/rate pairs. GPIO input mode is explicitly not implemented. Coefficient controls write raw 16-bit values into miniDSP memory, so userspace can create invalid filters. Dynamic DAPM route changes must stay synchronized with `master` and `use_pll` state.

## Test Signals

Exercise all listed MCLK/rate combinations, PLL auto/enable/bypass modes, master/slave DAI formats, GPIO and MICBIAS output requests, DT validation failures, coefficient get/put round trips, and capture smoke tests through analog and digital-mic routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adc3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.c

## Purpose

`tlv320adcx140.c` is an ASoC I2C capture driver for TI TLV320ADC3140/5140/6140 family ADCs. It manages regulators, reset, regcache-backed power transitions, capture DAI configuration, analog and PDM input routing, DRE/AGC/digital gain controls, phase calibration, GPI/GPO/GPIO setup, and mic-bias configuration.

## Important APIs, Types, and Functions

`struct adcx140_priv` holds regulators, optional reset GPIO, regmap, micbias/phase-calibration state, DAI format, and slot width. `adcx140_reset()`, `adcx140_pwr_ctrl()`, `adcx140_pwr_on()`, and `adcx140_pwr_off()` implement reset and power sequencing. `adcx140_hw_params()`, `adcx140_set_dai_fmt()`, and `adcx140_set_dai_tdm_slot()` program word length, format, polarity, master mode, and TDM constraints. `adcx140_codec_probe()` parses firmware properties and initializes device registers. `adcx140_phase_calib_*()` exposes cached phase-calibration state.

## Control Flow

I2C probe gets `avdd`/`iovdd`, optional reset, optional `areg`, initializes the regmap, marks it cache-only, and registers the component. Component probe runs when ASoC instantiates the codec: it parses mic-bias, VREF, PDM edge, GPI, GPIO, GPO, and ASI TX drive properties; resets and wakes the device; programs static configuration; then powers ADC/PLL/bias. Bias transitions from OFF to STANDBY call `adcx140_pwr_on()` to enable regulators, deassert reset, disable cache-only mode, and sync the cache. Transitions back to OFF mark the cache dirty, assert reset, and disable supplies.

## State and Persistence Behavior

The flat regcache is authoritative while the chip is powered off. Probe starts cache-only before hardware is accessible; power-on sync restores cached configuration. `phase_calib_on` is stored in private memory and written to `ADCX140_PHASE_CALIB` when enabling power. `micbias_vg`, `slot_width`, and `dai_fmt` also persist only in driver memory.

## Dependencies and Integration Points

Dependencies include I2C, regmap with a paged range, regulator bulk APIs, optional GPIO reset, generic device properties/OF/ACPI, and ASoC. The DAI exposes capture from two to eight channels at 44.1/48/96/192 kHz. Integration with board DT happens through TI-specific properties for mic bias, PDM edges, GPI/GPO/GPIO, and ASI TX behavior.

## Risks and Edge Cases

`set_tdm_slot()` only supports lower adjacent TX slots despite hardware supporting arbitrary masks. `slot_width` is validated but not otherwise used in current `hw_params()`. Several property arrays are accepted only within fixed sizes; malformed GPI arrays shorter than four values can be risky because indexed values are later accessed. Power sequencing relies on cache-only transitions being correct.

## Test Signals

Validate OFF/STANDBY/PREPARE/ON transitions with regulator tracing, reset GPIO timing, regcache sync after suspend/resume, DAI format and TDM error paths, capture on 2/4/8-channel PDM and analog routes, phase-calibration switch effects, and property validation for mic-bias/GPO/GPI/GPIO settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.h

## Purpose

`tlv320adcx140.h` is the private register and bit definition header for the TLV320ADCX140 family driver. It defines supported PCM rates/formats, register addresses, bit masks, channel limits, mic-bias encodings, power-control bits, TDM offset masks, and pin-configuration limits used by `tlv320adcx140.c`.

## Important APIs, Types, and Functions

There are no functions or structs. The important symbols are `ADCX140_RATES`, `ADCX140_FORMATS`, register addresses such as `ADCX140_ASI_CFG0`, `ADCX140_CH1_CFG*`, `ADCX140_DSP_CFG*`, `ADCX140_PWR_CFG`, and masks such as `ADCX140_WORD_LEN_MSK`, `ADCX140_INV_MSK`, `ADCX140_PWR_CTRL_MSK`, `ADCX140_TX_OFFSET_MASK`, `ADCX140_MIC_BIAS_*`, and GPIO/GPI/GPO bounds.

## Control Flow

This header has no direct control flow. Its definitions are consumed by the codec driver during regmap setup, DAI format negotiation, DAPM widget declarations, property validation, power sequencing, and ALSA mixer control declarations.

## State and Persistence Behavior

The file owns no runtime state. It defines how driver state maps onto persistent hardware registers and cached regmap entries. Changes to register constants affect resume, power-on cache sync, DAPM, and userspace control behavior.

## Dependencies and Integration Points

The header assumes ASoC PCM format/rate macros and Linux bit helpers are available through the including C file. It is tightly coupled to `tlv320adcx140.c` and the TLV320ADC3140/5140/6140 datasheet.

## Risks and Edge Cases

Incorrect masks for word length, inversion, mic-bias, or power bits can cause silent audio failure or unsafe bias/power states. The register set uses page-windowed addressing in the C file even though most definitions here are low page-zero offsets; future additions must respect the regmap range model.

## Test Signals

Compile coverage of `tlv320adcx140.c`, static comparison against datasheet register tables, and runtime register traces for DAI format, power, mic-bias, and GPIO/GPO property programming validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-i2c.c

## Purpose

`tlv320aic23-i2c.c` is the I2C transport wrapper for the shared TLV320AIC23 codec core. It checks adapter capability, creates an I2C regmap with the common AIC23 regmap configuration, and delegates all codec registration to `tlv320aic23_probe()`.

## Important APIs, Types, and Functions

The only executable entry point is `tlv320aic23_i2c_probe()`. The file also defines `tlv320aic23_id`, `tlv320aic23_of_match` with `ti,tlv320aic23`, and `tlv320aic23_i2c_driver`.

## Control Flow

I2C core calls probe, probe verifies `I2C_FUNC_SMBUS_BYTE_DATA`, initializes `devm_regmap_init_i2c()`, and passes the device plus regmap to the shared core. Driver registration is handled by `module_i2c_driver()`.

## State and Persistence Behavior

This wrapper owns no private state. The regmap and ASoC component state are owned by the common probe and devm-managed resources.

## Dependencies and Integration Points

It depends on Linux I2C, OF, regmap, and ASoC headers plus `tlv320aic23.h`. It integrates the common codec with board descriptions that instantiate an I2C `tlv320aic23` device.

## Risks and Edge Cases

The SMBus byte-data check may reject adapters that could support the raw regmap transfer format by other means. Error handling is intentionally delegated: `tlv320aic23_probe()` receives an ERR_PTR regmap and returns the failure.

## Test Signals

Probe with a supported I2C adapter, OF modalias matching, failure injection for missing adapter functionality, and common AIC23 playback/capture tests through an I2C-connected board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-spi.c

## Purpose

`tlv320aic23-spi.c` is the SPI transport wrapper for the shared TLV320AIC23 codec core. It configures SPI mode 0, creates an SPI regmap with the common AIC23 register format, and delegates all codec behavior to `tlv320aic23_probe()`.

## Important APIs, Types, and Functions

The executable entry point is `aic23_spi_probe()`. The file defines a `spi_driver` named `tlv320aic23`, registered through `module_spi_driver()`.

## Control Flow

SPI core calls probe, probe sets `spi->mode = SPI_MODE_0`, calls `spi_setup()`, initializes `devm_regmap_init_spi()`, and then calls the common codec probe. There are no local controls, DAPM widgets, or DAI definitions.

## State and Persistence Behavior

The wrapper owns no state beyond transient probe variables. The common core owns driver data, regcache, component registration, and all runtime audio state.

## Dependencies and Integration Points

It depends on Linux SPI, regmap, ASoC, and `tlv320aic23.h`. Its integration point is any board that wires TLV320AIC23 over SPI instead of I2C.

## Risks and Edge Cases

Forcing SPI mode 0 is required by the chip but can override board defaults; failures in `spi_setup()` stop probe. There is no OF match table in this wrapper, so matching depends on SPI modalias/board registration.

## Test Signals

Probe over SPI with mode inspection, failure injection for `spi_setup()`, register write/read traces through regmap, and common AIC23 stream tests on an SPI-connected board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.c

## Purpose

`tlv320aic23.c` is the shared ASoC codec core for the TI TLV320AIC23 stereo codec, used by both I2C and SPI wrappers. It provides the regmap contract, mixer controls, DAPM graph, DAI operations, sample-rate selection, bias-level power control, and common `tlv320aic23_probe()` export.

## Important APIs, Types, and Functions

`tlv320aic23_regmap` is exported for bus wrappers. `struct aic23` stores the regmap, MCLK, and requested ADC/DAC rates. Custom sidetone conversion is handled by `snd_soc_tlv320aic23_get_volsw()` and `snd_soc_tlv320aic23_put_volsw()`. Rate logic is implemented by `find_rate()` and `set_sample_rate_control()`. DAI operations include `tlv320aic23_hw_params()`, `tlv320aic23_pcm_prepare()`, `tlv320aic23_shutdown()`, `tlv320aic23_mute()`, `tlv320aic23_set_dai_fmt()`, and `tlv320aic23_set_dai_sysclk()`.

## Control Flow

The bus wrapper calls `tlv320aic23_probe()`, which allocates state, stores the regmap, and registers the component/DAI. Component probe resets the codec, sets default de-emphasis and volumes, unmutes inputs, and activates the device. Stream `hw_params()` records requested playback/capture rates, computes the closest valid sample-rate register value from MCLK and ADC/DAC needs, and programs word length. `prepare()` activates the digital interface; `shutdown()` deactivates when no streams remain and clears the relevant requested rate.

## State and Persistence Behavior

The RBTREE regcache stores 7-bit register/9-bit value defaults. `requested_adc` and `requested_dac` persist while one side of full-duplex audio is active so rate selection can satisfy both streams. Resume marks the regcache dirty and syncs it. Bias levels write the power and active registers for ON/STANDBY/OFF.

## Dependencies and Integration Points

The core depends on regmap and ASoC and is transport-agnostic. It integrates through the exported regmap config/probe, DAI `tlv320aic23-hifi`, stereo playback/capture streams, and DAPM pins for line, mic, headphone, and line outputs.

## Risks and Edge Cases

Rate selection is heuristic and accepts rates within a tolerance, so unusual MCLK values need validation. Full-duplex ADC/DAC rate tracking can be sensitive to stream start/stop ordering. The DAI format path does not handle all inversion flags. Sidetone volume uses a non-linear mapping that is easy to regress. `mclk` must be set by the machine driver before `hw_params()`.

## Test Signals

Test each common MCLK family with 8-96 kHz playback/capture, full-duplex start-order permutations, DAI format modes, bias transitions, suspend/resume regcache restoration, sidetone get/put conversion, and both I2C and SPI wrapper probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.h

## Purpose

`tlv320aic23.h` is the shared private header for the TLV320AIC23 codec core and its I2C/SPI wrappers. It declares the exported regmap configuration and common probe function, then defines the codec's register addresses, bit values, volume limits, and audio-path constants.

## Important APIs, Types, and Functions

The file declares `extern const struct regmap_config tlv320aic23_regmap` and `int tlv320aic23_probe(struct device *dev, struct regmap *regmap)`. It defines registers `TLV320AIC23_LINVOL` through `TLV320AIC23_RESET`, power bits such as `TLV320AIC23_DAC_OFF`, format bits such as `TLV320AIC23_FOR_I2S`, sample-rate bits such as `TLV320AIC23_USB_CLK_ON`, and volume/sidetone masks.

## Control Flow

The header has no runtime control flow. Its declarations allow bus wrappers to create a regmap and call the transport-neutral core. Its constants are used throughout the core for controls, DAPM, DAI setup, power, and sample-rate selection.

## State and Persistence Behavior

No state is owned here. The macros define the layout of persistent codec registers and cached values. Any change affects both bus transports because they share the common core.

## Dependencies and Integration Points

Forward declarations keep wrapper dependencies small. The header binds `tlv320aic23.c`, `tlv320aic23-i2c.c`, and `tlv320aic23-spi.c` together.

## Risks and Edge Cases

The AIC23 uses 9-bit register values and compact bitfields; wrong masks can corrupt adjacent controls. Constants such as default volume and min/max values drive user-visible ALSA ranges and need datasheet alignment.

## Test Signals

Compile both wrappers, validate register traces for volume/mute/power/format/rate paths, and compare macro values against the TLV320AIC23 datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.c

## Purpose

`tlv320aic26.c` is a self-contained SPI ASoC driver for the TI TLV320AIC26 low-power codec. It registers playback and capture DAIs, programs PLL/audio interface settings, exposes PCM and keyclick controls, creates a small DAPM graph, and provides a sysfs keyclick debug trigger.

## Important APIs, Types, and Functions

`struct aic26` stores the SPI device, regmap, component pointer, clock-provider flag, data format, MCLK, and keyclick parameters. DAI callbacks are `aic26_hw_params()`, `aic26_mute()`, `aic26_set_sysclk()`, and `aic26_set_fmt()`. Component probe is `aic26_probe()`. SPI binding is handled by `aic26_spi_probe()` with `aic26_regmap`. Sysfs support is `keyclick_show()` and `keyclick_store()`.

## Control Flow

SPI probe allocates state, initializes a 16-bit register/16-bit value regmap, stores defaults, and registers the component/DAI. Component probe resets the codec, powers it up, defaults Audio Control 3 to master mode, and creates the `keyclick` sysfs file. During stream setup, `set_sysclk()` records an MCLK in the 2-50 MHz range, `set_fmt()` records master/slave and serial data format, and `hw_params()` maps rate/width to PLL, fsref divisor, and audio-control values.

## State and Persistence Behavior

Runtime state is kept in `struct aic26`: MCLK, master/slave mode, data format, and component pointer. Register state is held by regmap and hardware; there is no explicit regcache default table. The sysfs file is devm-associated through component lifetime indirectly, but no remove callback removes it explicitly.

## Dependencies and Integration Points

Dependencies include SPI, regmap, ASoC, sysfs device attributes, and `tlv320aic26.h`. It integrates as an SPI driver named `tlv320aic26-codec`, DAI `tlv320aic26-hifi`, stereo playback/capture, DAPM pins `MICIN`, `AUX`, `HPL`, and `HPR`.

## Risks and Edge Cases

`aic26_hw_params()` can use uninitialized `reg` when neither clock-provider nor 48 kHz fsref branch assigns it, so this path deserves scrutiny. It maps S8 to 16-bit word length. MCLK must be configured before stream setup. Keyclick sysfs writes update bit `0x800` under mask `0x8000`, which appears inconsistent and should be verified.

## Test Signals

Run probe/reset/power-up tests over SPI, validate MCLK range rejection, all supported sample rates and formats, master/slave DAI formats, mute and keyclick controls, sysfs keyclick behavior, and static analysis for uninitialized register writes in `aic26_hw_params()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.h

## Purpose

`tlv320aic26.h` defines the TLV320AIC26 register address encoding and symbolic values used by the SPI codec driver. It covers auxiliary data/control pages, audio control registers, filter coefficient registers, PLL registers, fsref divisors, digital audio formats, and sample word lengths.

## Important APIs, Types, and Functions

There are no functions. `AIC26_PAGE_ADDR(page, offset)` builds the 16-bit register address used by regmap. Register constants include `AIC26_REG_AUDIO_CTRL1`, `AIC26_REG_DAC_GAIN`, `AIC26_REG_POWER_CTRL`, `AIC26_REG_PLL_PROG1`, and coefficient registers. Enums `aic26_divisors`, `aic26_datfm`, and `aic26_wlen` provide values consumed by DAI setup.

## Control Flow

The header has no flow of its own. `tlv320aic26.c` uses the register and enum constants during probe reset/power-up, sample-rate PLL programming, format selection, mute, ALSA controls, and keyclick sysfs operations.

## State and Persistence Behavior

No runtime state is defined. The file describes persistent hardware register addresses and values. Since the driver's regmap has 16-bit register addresses, `AIC26_PAGE_ADDR()` is central to all persistent hardware access.

## Dependencies and Integration Points

The header is private to `tlv320aic26.c` and mirrors the TLV320AIC26 datasheet's paged register map.

## Risks and Edge Cases

Address-shift mistakes in `AIC26_PAGE_ADDR()` or enum values would redirect every SPI register access. Word-length and data-format enums share fields in Audio Control 1, so future additions must preserve bit placement.

## Test Signals

Compile the codec driver, trace SPI register addresses for reset/audio-control/PLL paths, and compare generated addresses and bit values with the datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.c

## Purpose

`tlv320aic31xx.c` is the ASoC I2C driver for TI TLV320AIC31xx and DAC31xx codecs. It supports multiple codec variants, regulator/reset power sequencing, paged regmap caching, playback/capture DAI setup, PLL/divider programming, DAPM widgets/routes, jack detection IRQ handling, mic bias, output common-mode voltage selection, and optional DAC3100 coefficient firmware loading.

## Important APIs, Types, and Functions

`struct aic31xx_priv` stores component, regmap, codec type, reset GPIO, micbias, platform data, supplies, regulator notifiers, jack pointer, sysclk, P divider, rate-div table index, IRQ, and OCMV. `aic31xx_divs[]` is the PLL/divider table. Major functions include `aic31xx_setup_pll()`, `aic31xx_hw_params()`, `aic31xx_set_dai_fmt()`, `aic31xx_set_dai_sysclk()`, `aic31xx_clk_on/off()`, `aic31xx_power_on/off()`, `aic31xx_set_bias_level()`, `aic31xx_irq()`, `aic31xx_add_controls()`, `aic31xx_add_widgets()`, and `tlv320dac3100_fw_load()`.

## Control Flow

I2C probe initializes a paged regmap in cache-only mode, reads firmware/platform properties, gets reset GPIO and six supplies, configures OCMV, optionally configures GPIO1/INT1 and requests a threaded IRQ, optionally loads DAC3100 coefficients, then registers either DAC-only or full codec DAI(s). Component probe registers regulator-disable notifiers, marks the cache dirty, adds variant-specific controls/widgets/routes, and caches OCMV. Bias OFF-to-STANDBY powers regulators, resets hardware, syncs regcache, and restores jack detection. PREPARE turns clocks on; STANDBY from PREPARE turns clocks off; STANDBY-to-OFF disables supplies.

## State and Persistence Behavior

Regmap cache is authoritative while powered off and is synced after reset on power-on. Regulator disable notifiers assert reset and mark cache dirty if supplies disappear. Runtime persistent state includes selected sysclk source/frequency, P divider, rate-div line, codec variant, jack pointer, and dynamic clock-master DAPM route status. Jack-detection configuration is in a volatile status register and is restored separately after cache sync.

## Dependencies and Integration Points

Dependencies include I2C, regmap range pages, regulators, optional reset GPIO, firmware loading, ASoC, jack reporting, OF/ACPI matching, and DT bindings for mic-bias values. Integration varies by codec type: DAC31xx exposes playback only, AIC31xx exposes playback and capture, AIC311x variants add stereo Class-D routes, and AIC310x variants add mono speaker routes.

## Risks and Edge Cases

The PLL table is finite and exact frame-size/BCLK constraints can reject configurations or warn about inexact bitclocks. BCLK-as-PLL-input sysclk is derived in `hw_params()`, so params sequencing matters. IRQ handling reads volatile sticky flags and reports jack state only if a jack is registered. Firmware coefficient loading is strict about 153-byte size, magic, and version. `aic31xx_set_bias_level()` calls `BUG()` for unexpected bias transitions, which is harsh if framework sequencing changes.

## Test Signals

Validate each compatible variant, regulator failures and disable notifiers, reset GPIO polarity/timing, OFF/STANDBY/PREPARE/ON transitions, sysclk sources and sample rates from 8-192 kHz, DAI formats including DSP polarity inversion, master-clock DAPM route add/remove, jack/headset/button IRQ reports, overflow/short-circuit logs, DAC3100 firmware acceptance/rejection, and suspend/resume cache restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.h

## Purpose

`tlv320aic31xx.h` is the private definition header for the TLV320AIC31xx/DAC31xx ASoC driver. It defines supported rates/formats, codec variant flags, platform data, the paged register-address macro, register constants, and masks for clocking, interface format, power/status, interrupts, GPIO1, mute, headset detection, output common-mode voltage, and mic bias.

## Important APIs, Types, and Functions

Important types are `enum aic31xx_type`, encoding AIC3100/AIC3110/AIC3120/AIC3111/DAC3100/DAC3101 feature bits, and `struct aic31xx_pdata` for legacy platform data. Key macros include `AIC31XX_REG(page, reg)`, `AIC31XX_RATES`, `AIC31XX_FORMATS`, `AIC31XX_JACK_MASK`, register addresses from `AIC31XX_PAGECTL` through page-1 analog registers, and bit masks such as `AIC31XX_PLL_CLKIN_MASK`, `AIC31XX_IFACE1_*`, `AIC31XX_DACMUTE_MASK`, `AIC31XX_HSD_*`, and `AIC31XX_MICBIAS_MASK`.

## Control Flow

The header has no runtime flow. The C driver consumes these definitions during regmap setup, clock programming, DAI format negotiation, DAPM power-status polling, IRQ decoding, jack reporting, firmware coefficient writes, and variant-specific control/widget registration.

## State and Persistence Behavior

No state is allocated here. The definitions describe hardware register layout and variant capability bits that determine persistent register programming and runtime feature exposure.

## Dependencies and Integration Points

The header depends on ASoC rate/format and jack constants and Linux bit helpers through its including context. It integrates OF/ACPI/I2C match data with the variant-specific control and DAPM paths in `tlv320aic31xx.c`.

## Risks and Edge Cases

Variant bit definitions drive whether capture, DAC-only, mono/stereo speaker, and miniDSP behavior are exposed; wrong flags can register an invalid topology. Interrupt and volatile status masks must match hardware or jack/overflow/short-circuit reporting becomes misleading. Paged register addresses must remain consistent with regmap range configuration.

## Test Signals

Compile coverage, variant probe tests for every compatible string, register trace comparison for PLL/interface/jack/power paths, and datasheet review of masks and page offsets validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic31xx.h -->
