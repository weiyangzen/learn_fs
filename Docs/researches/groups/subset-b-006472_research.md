<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta529.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta529.c

## Purpose

This file is an ASoC I2C codec driver for the ST STA529 audio codec used on SPEAr-era platforms. It exposes one full-duplex stereo DAI, playback/capture format setup, digital/master volume controls, PWM mode selection, stream mute, and coarse power/bias handling through the codec's FFX and serial-port registers.

## Important APIs, types, and functions

The driver-local register map defines STA529 FFX, S2P/P2S, PLL, ADC, clock, misc, status, and power registers. `struct sta529` stores only the `regmap`. `sta529_readable()` constrains regmap cache-visible registers. ALSA controls are `Digital Playback Volume`, `Master Playback Volume`, and `PWM Select`. The DAI callbacks are `sta529_hw_params()`, `sta529_set_dai_fmt()`, and `sta529_mute()`. `sta529_set_bias_level()` drives standby/on transitions and cache sync. `sta529_i2c_probe()` allocates state, initializes an 8-bit regmap, and registers the component plus `sta529-audio` DAI.

## Control flow

Probe creates the regmap with MAPLE cache defaults and registers the component for I2C/OF matches `sta529` and `st,sta529`. During PCM setup, `sta529_hw_params()` maps 16/24/32-bit widths to codec data length and BCLK-to-FS ratios, then maps supported sample-rate bands to playback and capture frequency range fields. Playback updates `STA529_S2PCFG1` and `STA529_MISC`; capture updates `STA529_P2SCFG1` and capture range bits. `sta529_set_dai_fmt()` accepts left-justified, I2S, and right-justified formats and programs `STA529_S2PCFG0`. `sta529_mute()` toggles `AUDIO_MUTE_MSK`. Bias ON/PREPARE powers up FFX and enables the FFX clock; STANDBY syncs regcache after OFF, puts the device in standby, forces FFX output off, and disables the FFX clock.

## State and persistence behavior

Persistent software state is almost entirely regmap cache state. No runtime PM or private clock/regulator objects are tracked. `suspend_bias_off`, `idle_bias_on`, and `use_pmdown_time` delegate lifecycle behavior to ASoC bias management. Hardware settings survive in the regcache across bias-off suspend and are restored by `regcache_sync()` when returning from OFF to STANDBY.

## Dependencies and integration points

The driver depends on I2C, regmap, ALSA SoC component/DAI/control APIs, DAPM bias states, and OF/I2C modalias matching. Machine drivers must configure a compatible CPU DAI and one of the supported sample widths/rates. There is no DAPM route graph in this file; power control is handled at component bias and mute level rather than per-path widgets.

## Risks and test signals

Risks include the typoed `POWER_CNTLMSAK` macro name, limited DAI-format handling that ignores clock-provider and inversion bits, no validation for unsupported capture/playback asymmetry beyond `hw_params()`, and a readable-register list that excludes many defined status/PLL registers. Test signals are successful I2C probe, ALSA control enumeration, playback/capture at every advertised rate and 16/24/32-bit width, left/I2S/right-justified format programming, mute/unmute behavior, suspend/resume or bias OFF/STANDBY cache restoration, and absence of regmap access errors for cached controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta529.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/stac9766.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/stac9766.c

## Purpose

This file implements ASoC support for the STAC9766 AC97 codec, including analog AC97 playback/capture and IEC958/S/PDIF playback. It exposes classic AC97 mixer controls, record routing, mic/boost options, S/PDIF source selection, AC97 reset/resume handling, and rate programming through AC97 standard registers.

## Important APIs, types, and functions

The driver uses `struct snd_ac97` as component private data and a 16-bit AC97 regmap built with `regmap_init_ac97()`. `stac9766_snd_ac97_controls` defines speaker/headphone/mono/record/beep/phone/mic/line/CD/AUX/video/DAC/3D/S/PDIF/mux controls. `ac97_analog_prepare()` enables variable-rate audio and writes either `AC97_PCM_FRONT_DAC_RATE` or `AC97_PCM_LR_ADC_RATE`. `ac97_digital_prepare()` writes S/PDIF setup, enables VRA plus S/PDIF, and programs DAC rate. `stac9766_set_bias_level()` writes `AC97_POWERDOWN`. Probe/remove/resume are handled by `stac9766_component_probe()`, `stac9766_component_remove()`, and `stac9766_component_resume()`.

## Control flow

The platform driver `stac9766-codec` registers a component with two DAIs: `stac9766-hifi-analog` for 8 kHz to 48 kHz AC97 formats with playback/capture, and `stac9766-hifi-IEC958` for 32/44.1/48 kHz IEC958 subframe playback. Component probe calls `snd_soc_new_ac97_component()` with the expected vendor ID, creates the AC97 regmap, attaches it to the component, and stores the AC97 object. Analog prepare disables S/PDIF while enabling VRA; digital prepare configures the S/PDIF register and enables both VRA and S/PDIF. Bias OFF powers everything down including the AC link; other bias states clear powerdown.

## State and persistence behavior

State is held by the AC97 core object and MAPLE regcache defaults. Resume performs `snd_ac97_reset()` with the vendor ID/mask, so hardware identity and AC-link recovery are central. Remove tears down the component regmap and frees the AC97 component. The driver relies on ASoC suspend-bias-off and idle-bias-on behavior rather than maintaining its own runtime PM state.

## Dependencies and integration points

The file integrates with the ALSA AC97 codec core, regmap AC97 helpers, ASoC platform component registration, and machine drivers that instantiate `stac9766-codec`. It has no I2C/SPI/OF binding in this file. The analog DAI uses `SND_SOC_STD_AC97_FMTS`; the digital DAI requires IEC958 subframe samples.

## Risks and test signals

Risks include dependence on a working AC97 bus reset sequence, broad mixer control exposure with minimal policy, fixed S/PDIF register value `0x2002`, and no DAPM widgets/routes for path-level power modeling. Test signals include probe success with vendor ID `0x83847666`, readable/writable AC97 mixer controls, analog playback/capture at standard AC97 rates, IEC958 playback at 32/44.1/48 kHz, powerdown register changes across bias transitions, and successful resume reset after suspend.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/stac9766.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sti-sas.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sti-sas.c

## Purpose

This file is an ASoC codec-style driver for STMicroelectronics STi SAS audio glue hardware. It exposes an analog DAC output DAI and an S/PDIF output DAI backed by syscon registers, controlling DAC standby/softmute bits, S/PDIF biphase formatter enable, and validation of required MCLK-to-FS ratios.

## Important APIs, types, and functions

`struct sti_sas_data` holds device data plus DAC/SPDIF register and MCLK state. `sti_sas_read_reg()` and `sti_sas_write_reg()` adapt syscon regmap access to a virtual component regmap. `sti_sas_init_sas_registers()` idles S/PDIF and DAC hardware. DAC callbacks include `sti_sas_dac_set_fmt()` and `stih407_sas_dac_mute()`. S/PDIF callbacks include `sti_sas_spdif_set_fmt()` and `sti_sas_spdif_trigger()`. Shared callbacks are `sti_sas_set_sysclk()` and `sti_sas_prepare()`. Probe is `sti_sas_driver_probe()`.

## Control flow

Platform probe matches `st,stih407-sas-codec`, allocates driver data, creates a virtual regmap that reads/writes the syscon-backed DAC register bank, looks up the `st,syscfg` syscon, assigns the analog DAI ops from match data, and registers the component with two DAIs. Component probe and PM resume call `sti_sas_init_sas_registers()` to disable the S/PDIF biphase formatter and put DAC analog/digital paths into standby with softmute set. `set_fmt()` for both DAIs only accepts codec bit/frame clock consumer mode (`CBC_CFC`). `set_sysclk()` records incoming MCLK per DAI. `prepare()` enforces S/PDIF MCLK/rate ratio 128 and analog DAC ratio 256. S/PDIF trigger enables biphase on START/PAUSE_RELEASE and disables it before STOP/SUSPEND/PAUSE_PUSH to avoid formatter stalls.

## State and persistence behavior

State consists of `dac.mclk`, `spdif.mclk`, syscon/virtual regmaps, and static DAI ops selection. Register defaults use MAPLE cache, with `STIH407_AUDIO_GLUE_CTRL` marked volatile. Resume reinitializes hardware to idle rather than restoring arbitrary stream state. The shared syscon map is the persistent hardware backing for both DAC and S/PDIF controls.

## Dependencies and integration points

The driver depends on platform/OF matching, `syscon_regmap_lookup_by_phandle()`, regmap, reset/syscon infrastructure, and ASoC DAI/component/DAPM APIs. The device tree must provide `st,syscfg`. Machine drivers must set sysclk before prepare and use MCLK values with the exact required ratios.

## Risks and test signals

Risks include strict integer MCLK/rate ratio checks, global mutation of `sti_sas_dai[STI_SAS_DAI_ANALOG_OUT].ops`, no explicit reset-control use despite including reset headers, and dependency on syscon offsets matching the SoC. Test signals include OF probe with syscon, component probe register writes, analog playback with 256x MCLK, S/PDIF playback with 128x MCLK, biphase enable/disable at trigger boundaries, DAC softmute behavior, and resume reinitialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sti-sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.c

## Purpose

This file implements an I2C ASoC driver for the TI TAS2552 mono smart amplifier. It provides digital/analog input selection, Class-D/PLL DAPM modeling, playback and capture DAIs, PLL and PDM clock programming, TDM slot delay support, runtime PM, regulator/GPIO sequencing, and basic volume/source controls.

## Important APIs, types, and functions

`struct tas2552_data` stores component, regmap, I2C client, three supplies, optional enable GPIO, PLL/PDM clock IDs and rates, DAI format, and TDM delay. Core callbacks are `tas2552_setup_pll()`, `tas2552_hw_params()`, `tas2552_prepare()`, `tas2552_set_dai_fmt()`, `tas2552_set_dai_sysclk()`, `tas2552_set_dai_tdm_slot()`, `tas2552_mute()`, `tas2552_runtime_suspend()`, and `tas2552_runtime_resume()`. Component lifecycle is handled by `tas2552_component_probe()`/`remove()` plus system suspend/resume regulator callbacks. Probe is `tas2552_probe()`.

## Control flow

I2C probe allocates state, gets optional `enable` GPIO, creates an 8-bit RBTREE regmap, obtains `vbat`, `iovdd`, and `avdd` regulators, enables runtime PM/autosuspend, and registers the component. Component probe enables supplies, asserts enable GPIO, runtime-resumes the device, mutes it, programs default input/output/boost/APT/limiter settings, and leaves the codec ready. `hw_params()` maps sample width to serial word length and clocks-per-frame, maps PCM rate to `CFG_3` WCLK frequency, then calls `tas2552_setup_pll()`. PLL setup derives a 512xFS PLL clock, uses the selected sysclk or BCLK, bypasses when possible, otherwise calculates J/D divisors, and falls back to BCLK or fixed 1.8 MHz when PLL input is out of range. `prepare()` writes DSP_A/DSP_B data delay from the TDM slot. DAPM post events write reserved/limiter/shutdown sequencing around power-up and power-down.

## State and persistence behavior

The driver persists PLL/PDM clock choices, DAI format, TDM delay, and regmap cache. Runtime suspend sets software shutdown, marks cache-only/dirty, and deasserts enable GPIO. Runtime resume asserts enable GPIO, clears software shutdown, exits cache-only, and syncs regcache. System suspend/resume only disables/enables regulators. Component remove releases runtime PM and lowers the GPIO but does not explicitly disable regulators outside suspend flow.

## Dependencies and integration points

Dependencies include I2C, regmap, runtime PM, regulator bulk APIs, GPIO descriptors, ASoC controls/DAPM/DAI ops, platform data constants in `<sound/tas2552-plat.h>`, and DT bindings in `<dt-bindings/sound/tas2552.h>`. It matches `ti,tas2552` and I2C ID `tas2552`. Machine drivers may call `set_sysclk()` for PLL/PDM sources and `set_tdm_slot()` for DSP/TDM operation.

## Risks and test signals

Risks include complex PLL fallback math, possible divide-by-zero paths if BCLK-derived inputs are invalid, TDM adjacency requirements, capture support that only routes DMIC/ASI monitor data, and lifecycle coupling between component probe, runtime PM, regulators, and enable GPIO. Test signals include probe with all supplies, runtime autosuspend/resume cache sync, playback at 8 kHz through 192 kHz with 16/20/24/32-bit formats, DSP_A/DSP_B TDM delay, PLL bypass and non-bypass cases, sysclk fallback warnings, mute and DAPM power events, and ALSA controls for volume and DIN source.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.h

## Purpose

This header defines the TAS2552 register address map and bitfield macros used by the TAS2552 ASoC amplifier driver. It centralizes register offsets for configuration, serial audio, PLL, PDM, limiter, boost/APT, status, and telemetry registers.

## Important APIs, types, and functions

There are no functions or types. Important macro groups include `TAS2552_CFG_1/2/3`, `TAS2552_DOUT`, `TAS2552_SER_CTRL_1/2`, `TAS2552_OUTPUT_DATA`, `TAS2552_PLL_CTRL_1/2/3`, `TAS2552_PDM_CFG`, and `TAS2552_PGA_GAIN`. Bitfields define software reset/shutdown/mute, PLL source selection, Class-D/boost/APT/limiter/IV sense enables, WCLK rate encoding, DIN source selection, I2S output/analog/PDM selection, serial word length/data format/clocks-per-frame/provider bits, output telemetry muxing, PDM clock selection, APT threshold/delay, and PLL J/D/bypass helpers.

## Control flow

The header has no runtime control flow. Its macros are consumed by `tas2552.c` to translate ALSA DAI operations, DAPM events, sysclk requests, and controls into register writes.

## State and persistence behavior

No state is stored here. The register addresses and masks define the hardware state persisted by the TAS2552 device and regmap cache in the implementation file.

## Dependencies and integration points

The header depends only on kernel bit operations already available through includers. It is private to the codec implementation and must remain aligned with the TAS2552 datasheet and `<dt-bindings/sound/tas2552.h>` clock IDs used by the driver.

## Risks and test signals

Risks are incorrect masks/shifts causing silent misprogramming, especially `TAS2552_PLL_SRC_MASK`, serial-format encodings, and PLL D upper/lower helpers. Test signals are compile success of `tas2552.c`, register traces matching expected bit values for sysclk/format/rate changes, and hardware validation for each macro-controlled path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2552.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.c

## Purpose

This file implements an I2C ASoC driver for TI TAS2562-family smart amplifiers, including TAS2562, TAS2564, and TAS2110 variants. It handles paged register access, playback/capture DAI setup, TDM slot configuration, sample-rate/bit-width programming, DAPM power transitions, shutdown GPIO suspend/resume, IV sense routing for non-TAS2110 models, and volume controls.

## Important APIs, types, and functions

`struct tas2562_data` tracks component, shutdown GPIO, regmap, device/client, V/I sense slots, software volume level, model ID, and DAC/unmuted state. `tas2562_set_samplerate()`, `tas2562_set_dai_tdm_slot()`, `tas2562_set_bitwidth()`, `tas2562_hw_params()`, `tas2562_set_dai_fmt()`, `tas2562_update_pwr_ctrl()`, `tas2562_mute()`, and `tas2562_dac_event()` implement audio setup and power state. `tas2562_volume_control_get/put()` implements a custom DVC control using `float_vol_db_lookup`. `tas2562_parse_dt()` reads GPIO and sense slots. `tas2562_probe()` chooses either the TAS2110 or TAS2562 component driver.

## Control flow

Probe uses I2C/OF match data as model ID, parses optional `shutdown` or deprecated `shut-down` GPIO, reads `ti,imon-slot-no` and `ti,vmon-slot-no` for TAS2562/TAS2564, creates a regmap with a page selector range, and registers the appropriate component. Component probe stores the component pointer and deasserts SDZ. `hw_params()` programs RX word length, enables/disables VSENSE/ISENSE transmit bits based on power-control sense bits, and writes rate family/ramp-rate bits. `set_fmt()` validates normal/inverted bit clock with normal frame, maps I2S/DSP_A start slot to one BCLK and LEFT_J/DSP_B to zero, and writes RX edge/start offset. `set_tdm_slot()` selects left/right slots, slot width, and V/I sense slots. DAPM DAC events set `dac_powered`; mute sets `unmuted`; both converge through `tas2562_update_pwr_ctrl()` to ACTIVE/MUTE/SHUTDOWN.

## State and persistence behavior

State includes cached current volume, model ID, sense slots, and booleans controlling power-state derivation. Suspend sets regcache cache-only/dirty and asserts shutdown GPIO low; resume deasserts GPIO, exits cache-only, and syncs the regcache. The RBTREE regmap spans five 128-byte pages with explicit defaults. Current program/config firmware state is not involved; this is a standalone codec driver.

## Dependencies and integration points

The driver depends on I2C, GPIO descriptors, regmap range paging, ASoC DAPM/control/DAI APIs, firmware-node properties, and I2C/OF matching for `ti,tas2562`, `ti,tas2564`, and `ti,tas2110`. Machine drivers configure DAI format, optional TDM slots, and can expose capture for sense data. TAS2110 intentionally omits ISENSE/VSENSE DAPM widgets.

## Risks and test signals

Risks include an apparent `SNDRV_PCM_FORMAT_S32_LE` token in `TAS2562_FORMATS` rather than the usual fmtbit macro, `tas2562_parse_dt()` return value ignored in probe, volume lookup indexed by `value/2` despite a 1 dB TLV range, and typoed log text. Test signals include probe for all three model IDs, suspend/resume with SDZ GPIO and regcache sync, DAI format coverage for I2S/DSP_A/DSP_B/LEFT_J and inversion limits, TDM slot validation, VMON/IMON capture routing, DVC writes, and power-control transitions across DAPM and mute changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.h

## Purpose

This header defines the TAS2562-family paged register map and bitfields used by `tas2562.c`. It covers page control, software reset, power state, playback configuration, TDM configuration, DVC registers, revision ID, slot masks, sample-rate encodings, word/slot width encodings, and V/I sense transmit bits.

## Important APIs, types, and functions

No functions or C types are declared. `TAS2562_REG(page, reg)` linearizes paged addresses for regmap range access. Key register macros include `TAS2562_PAGE_CTRL`, `TAS2562_PWR_CTRL`, `TAS2562_TDM_CFG0` through `TAS2562_TDM_CFG10`, `TAS2562_TDM_DET`, `TAS2562_REV_ID`, and `TAS2562_DVC_CFG1` through `DVC_CFG4`. Important masks include `TAS2562_MODE_MASK`, `TAS2562_TDM_CFG0_SAMPRATE_MASK`, `TAS2562_TDM_CFG2_RX*`, `TAS2562_TDM_CFG5_VSNS_EN`, and `TAS2562_TDM_CFG6_ISNS_EN`.

## Control flow

There is no runtime control flow. The implementation uses these constants in DAI callbacks, DAPM events, regmap defaults, and volume programming.

## State and persistence behavior

No software state is kept in the header. Its definitions describe hardware register state cached and synchronized by `tas2562.c`.

## Dependencies and integration points

The macros assume kernel `BIT()`/`GENMASK()` definitions are available through includers. They are private to the TAS2562 codec implementation and must stay in sync with model variants TAS2562, TAS2564, and TAS2110 where registers overlap.

## Risks and test signals

Risks include off-by-one or wrong-bit masks for slot offsets and sense enables, especially because the driver composes values directly from these macros. Test signals are compile coverage, regmap traces for DAI operations, and hardware confirmation of RX slot, sample-rate, power, and sense-output behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2562.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h

## Purpose

This private header contains TAS2764/SN012776 quirk sequences, primarily for Apple-derived behavior. It supplements `tas2764.c` with undocumented or board-specific register writes for noise gate, VBAT/PVDD conversion, DAC modulator reset, thermal threshold handling, hidden-page writes, and a special shutdown sequence.

## Important APIs, types, and functions

The header defines quirk bit flags such as `TAS2764_NOISE_GATE_DISABLE`, `TAS2764_CONV_VBAT_PVDD_MODE`, `TAS2764_DMOD_RST`, `TAS2764_UNK_SEQ0`, `TAS2764_APPLE_UNK_SEQ1`, `TAS2764_APPLE_UNK_SEQ2`, `TAS2764_THERMAL_TH1_DISABLE`, and `TAS2764_SHUTDOWN_DANCE`. Each maps to `struct reg_sequence` arrays consumed by `regmap_multi_reg_write()`. `tas2764_do_quirky_pwr_ctrl_change()` wraps transitions to shutdown with pre/post hidden-page writes. `tas2764_quirk_init_sequences[]` indexes initialization sequences by bit position.

## Control flow

At compile time `ENABLED_APPLE_QUIRKS` enables the lower six quirk bits, while the shutdown dance bit is defined but not included by that mask. `tas2764_apply_init_quirks()` in `tas2764.c` iterates the sequence table and applies entries whose bit is enabled. Power-control updates call `tas2764_do_quirky_pwr_ctrl_change()` only when `TAS2764_SHUTDOWN_DANCE` is enabled.

## State and persistence behavior

The header itself stores no runtime state, but its sequences write persistent hardware registers, including undocumented hidden pages. The power-control helper reads current power state from the component before deciding whether to perform the shutdown dance.

## Dependencies and integration points

It depends on `linux/regmap.h` and `tas2764.h`, and it is included inside `tas2764.c` after `struct tas2764_priv` is defined. The helper uses `tas2764->component` and `tas2764->regmap`, so it is tightly coupled to that implementation.

## Risks and test signals

Risks are high because several writes are explicitly undocumented or unknown, the enabled mask is compile-time rather than DT-configured, and bit/table ordering must remain consistent. Test signals include SN012776 probe success, no regmap errors while applying init sequences, clean power-down/up without pops or hangs, thermal/fault behavior matching target hardware, and regression checks with plain `ti,tas2764` devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.c

## Purpose

This file implements an I2C ASoC driver for TI TAS2764 and compatible SN012776 smart amplifiers. It handles paged register access, reset/shutdown GPIOs, DAI format/rate/slot configuration, mute and power sequencing, V/I sense routing, SDOUT idle behavior, IRQ fault reporting, optional hwmon temperature reporting, and SN012776/Apple quirk initialization.

## Important APIs, types, and functions

`struct tas2764_priv` stores component, reset/shutdown GPIOs, regmap, IRQ, device ID, V/I sense slots, DAC/unmute state, and idle slot config. Key functions are `tas2764_irq()`, `tas2764_reset()`, `tas2764_update_pwr_ctrl()`, suspend/resume callbacks, `tas2764_mute()`, `tas2764_set_bitwidth()`, `tas2764_set_samplerate()`, `tas2764_hw_params()`, `tas2764_set_fmt()`, `tas2764_set_dai_tdm_slot()`, `tas2764_set_dai_tdm_idle()`, `tas2764_set_bclk_ratio()`, `tas2764_apply_init_quirks()`, hwmon read helpers, `tas2764_codec_probe()`, `tas2764_parse_dt()`, and `tas2764_i2c_probe()`.

## Control flow

Probe allocates state, records match data (`ti,tas2764` or `ti,sn012776`), initializes an RBTREE paged regmap up to `0xffff`, parses reset/shutdown GPIOs and `ti,imon-slot-no`/`ti,vmon-slot-no`, optionally registers hwmon, and registers the component/DAI. Component probe asserts shutdown GPIO, performs hardware and software reset, reinitializes regcache, unmasks selected IRQs and requests a threaded IRQ when present, disables sense transmit by default, applies SN012776 BOP presets, and then applies enabled quirk sequences. DAI setup programs sample widths, limited rate families (44.1/48/88.2/96 kHz), frame polarity/start slot, TDM slot positions, sense slots, and idle SDOUT behavior. Mute performs explicit ramp-down delays and transitions through ACTIVE/MUTE/SHUTDOWN based on `dac_powered` and `unmuted`.

## State and persistence behavior

State is split between regmap cache and booleans that derive the current power-control target. Suspend forces shutdown, optionally lowers SDZ, marks regcache dirty/cache-only, and delays for shutdown settling. Resume raises SDZ, reapplies derived power state, exits cache-only, and syncs regcache. IRQ handling reads latched fault registers and clears IRQ status through `TAS2764_INT_CLK_CFG`. hwmon temperature reports last sampled die temperature and treats zero/invalid ADC data as a fault.

## Dependencies and integration points

The driver integrates with I2C, OF match data, regmap range paging, GPIO descriptors, threaded IRQs, ASoC DAI/DAPM/control APIs, and optional hwmon. Machine drivers must set supported DAI formats, TDM slots, BCLK ratio for idle-mask cropping, and route VMON/IMON capture if needed. The SN012776 path depends on `tas2764-quirks.h`.

## Risks and test signals

Risks include compile-time enabled undocumented quirks, timing-sensitive mute/shutdown delays, limited accepted sample rates, absence of validation that sense slots are within TDM slot count, volatile hidden-page ranges for quirk writes, and IRQ fault handling that only decodes the first latch byte. Test signals include probe for both compatible strings, reset and regcache reinit, playback at supported rates/widths, TDM idle modes and BCLK-ratio cropping, V/I sense capture, IRQ fault logging/clear, hwmon temp/fault reads, suspend/resume restoration, and SN012776 BOP/quirk behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.h

## Purpose

This header defines TAS2764 register addresses and bitfields for the TAS2764/SN012776 ASoC driver. It covers paged address construction, power control, DVC/gain, TDM configuration, interrupt/fault registers, temperature readout, BOP configuration, and SDOUT idle-mask registers.

## Important APIs, types, and functions

There are no functions or types. `TAS2764_REG(page, reg)` linearizes paged register addresses. Important constants include `TAS2764_SW_RST`, `TAS2764_PWR_CTRL`, `TAS2764_DVC`, `TAS2764_CHNL_0`, `TAS2764_TDM_CFG0` through `TDM_CFG6`, interrupt mask/latch registers, `TAS2764_TEMP`, `TAS2764_INT_CLK_CFG`, `TAS2764_BOP_CFG0`, and `TAS2764_SDOUT_HIZ_*`. Bitfields define ACTIVE/MUTE/SHUTDOWN, BOP source, V/I sense power bits, rate/frame/slot/edge encodings, sense transmit enables, and SDOUT force-zero enable.

## Control flow

The header has no runtime control flow. `tas2764.c` uses these definitions for regmap defaults, DAI ops, mute/power sequencing, IRQ handling, hwmon reads, BOP presets, and quirk sequences.

## State and persistence behavior

No state is stored here. The macros describe hardware state cached by regmap and manipulated by `tas2764.c`.

## Dependencies and integration points

The header expects kernel `BIT()` and `GENMASK()` definitions from includers. It is shared with `tas2764-quirks.h`, so any address or bitfield change affects both normal and quirk paths.

## Risks and test signals

Risks include incorrect paged address construction or bit masks causing writes to wrong hidden/normal pages. Test signals are build coverage of `tas2764.c` and `tas2764-quirks.h`, register traces for DAI setup and power changes, IRQ latch reads, temperature reads, and SDOUT idle-mask writes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.c

## Purpose

This file implements an I2C ASoC driver for the TI TAS2770 smart amplifier. It provides reset/shutdown sequencing, paged regmap access, AIF input routing, DAI format/rate/slot setup, mute/power-state handling, V/I/PDM transmit-slot support, TDM idle behavior, playback/gain controls, and optional hwmon temperature reporting.

## Important APIs, types, and functions

The driver uses `struct tas2770_priv` from `tas2770.h`. Key functions include `tas2770_reset()`, `tas2770_update_pwr_ctrl()`, suspend/resume callbacks, `tas2770_dac_event()`, `sense_event()`, `tas2770_mute()`, `tas2770_set_ivsense_transmit()`, `tas2770_set_pdm_transmit()`, `tas2770_set_bitwidth()`, `tas2770_set_samplerate()`, `tas2770_hw_params()`, `tas2770_set_fmt()`, `tas2770_set_dai_tdm_slot()`, `tas2770_set_dai_tdm_idle()`, hwmon helpers, `tas2770_codec_probe()`, `tas2770_parse_dt()`, and `tas2770_i2c_probe()`.

## Control flow

I2C probe allocates state, creates a one-page RBTREE regmap with volatile/writeable callbacks, parses `ti,imon-slot-no`, `ti,vmon-slot-no`, `ti,pdm-slot-no`, `shutdown` GPIO, and `reset` GPIO, optionally registers hwmon, then registers the component. Component probe raises SDZ, resets the device, reinitializes regcache, and configures IV sense/PDM transmit slots when DT provided them. DAPM DAC events set `dac_powered`, mute sets `unmuted`, and both update power control. `sense_event()` forces a shutdown and restores power around ISENSE/VSENSE switch changes so hardware latches the sense-power configuration. DAI setup handles width, 44.1/48/88.2/96/176.4/192 kHz sample-rate families, clock/frame inversion, I2S/DSP/left-justified timing, two RX slots, and TX idle pulldown/zero/HiZ/off modes.

## State and persistence behavior

Software state tracks sense/PDM slots, DAC power, mute state, and current idle TX mode. Suspend puts regcache into cache-only mode and either lowers SDZ or writes shutdown; resume raises SDZ or restores derived power state before syncing cache. hwmon reads combine temp MSB/LSB and report `-ENODATA` as a fault for unsampled reset/shutdown values.

## Dependencies and integration points

The file depends on I2C, OF, GPIO descriptors, regmap range paging, ASoC controls/DAPM/DAI APIs, and optional hwmon. It matches `ti,tas2770` and exposes one symmetric-rate `tas2770 ASI1` DAI. Machine drivers should provide supported DAI format/slots and route VMON/IMON capture when using speaker protection.

## Risks and test signals

Risks include limited rate set despite 176.4 kHz handling not advertised in `TAS2770_RATES`, no IRQ request despite interrupt register definitions, sensitivity to sense switch shutdown cycles, and no validation of DT sense/PDM slots against actual TDM slots. Test signals include probe/reset, DAI setup for each supported rate/format/slot width, TDM idle modes, V/I/PDM slot transmission, DAPM sense switch operation during active playback, mute/power transitions, suspend/resume, and hwmon temperature/fault readings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.h

## Purpose

This header defines TAS2770 register addresses, bitfields, error flags, and the private driver state structure used by `tas2770.c`. It covers paged register addressing, power control, playback/gain, TDM configuration, brownout/interrupt/telemetry registers, temperature/VBAT registers, and idle/clock settings.

## Important APIs, types, and functions

`TAS2770_REG(page, reg)` linearizes paged addresses. Important macros define `TAS2770_PWR_CTRL`, playback config registers, TDM config registers 0-7, interrupt mask/live/latched registers, VBAT and TEMP MSB/LSB, `TAS2770_DIN_PD`, `TAS2770_TDM_CLK_DETC`, and revision ID. `struct tas2770_priv` stores component, reset/shutdown GPIOs, regmap, device pointer, V/I/PDM slots, DAC/unmute flags, and idle TX mode. Error bit macros identify overcurrent, overtemperature, voltage, brownout, and Class-D power faults.

## Control flow

The header has no independent control flow. The implementation uses these constants in regmap defaults, writeability/volatility callbacks, DAI operations, DAPM power events, hwmon reads, and DT-configured telemetry routing.

## State and persistence behavior

Only the `tas2770_priv` definition describes software state. Hardware state is represented by macros and persisted through the implementation's regmap cache and GPIO/power sequencing.

## Dependencies and integration points

The header requires kernel bit macros and is private to the TAS2770 codec driver. Its private state structure is the integration boundary between probe, DAI callbacks, DAPM events, suspend/resume, and hwmon callbacks.

## Risks and test signals

Risks include mismatched bit values for TDM frame polarity and RX word/slot widths, and divergence between defined error flags and implemented fault handling. Test signals are compile coverage, register traces for `tas2770.c` operations, and hardware checks for power, rate, slot, telemetry, and temperature behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2770.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.c

## Purpose

This file implements an I2C ASoC driver for the TI TAS2780 mono smart amplifier. It exposes one ASI1 DAI with playback/capture, input muxing, V/I sense DAPM switches, reset and power control, format/rate/slot programming, and basic speaker/gain volume controls.

## Important APIs, types, and functions

`struct tas2780_priv` stores component, reset GPIO, regmap, device pointer, and V/I sense slots. Key functions are `tas2780_reset()`, suspend/resume callbacks, `tas2780_mute()`, `tas2780_set_bitwidth()`, `tas2780_set_samplerate()`, `tas2780_hw_params()`, `tas2780_set_fmt()`, `tas2780_set_dai_tdm_slot()`, `tas2780_codec_probe()`, `tas2780_parse_dt()`, and `tas2780_i2c_probe()`. Controls expose `Speaker Volume` and `Amp Gain Volume`; DAPM exposes `ASI1`, `ASI1 Sel`, `ISENSE`, `VSENSE`, `OUT`, `VMON`, and `IMON`.

## Control flow

Probe allocates state, creates a one-page paged RBTREE regmap, parses optional reset GPIO and `ti,imon-slot-no`/`ti,vmon-slot-no`, then registers the component. Component probe sets the component pointer, performs GPIO/software reset, and enables IC configuration bits in `TAS2780_IC_CFG`. `hw_params()` writes RX word/slot widths, sense transmit enables based on power-control sense bits, and sample-rate family bits for 44.1/48/88.2/96 kHz. `set_fmt()` supports normal or inverted bit clock with normal frame, maps I2S/DSP_A to I2S interface/start slot 1 and LEFT_J/DSP_B to left-justified/start slot 0, and writes RX edge/start/interface fields. `set_tdm_slot()` accepts one or two TX slots, rejects RX masks, writes slot positions, slot width, and V/I sense slots. Mute directly writes MUTE or ACTIVE to power control.

## State and persistence behavior

State is minimal: V/I sense slots and reset GPIO are parsed at probe; no booleans are kept for DAPM-derived power state. Suspend writes shutdown and marks regcache cache-only/dirty; resume writes ACTIVE, exits cache-only, and syncs cache. There is no runtime PM, IRQ handling, hwmon, or firmware state in this driver.

## Dependencies and integration points

The driver depends on I2C, OF, GPIO descriptors, regmap range paging, and ASoC DAI/DAPM/control APIs. It matches `ti,tas2780` and expects machine drivers to supply supported DAI formats and TDM slot settings. Capture channels are available for VMON/IMON style telemetry when routed.

## Risks and test signals

Risks include simple mute logic that never writes shutdown except suspend, limited rate support, no slot validation for sense slots beyond DT defaults, no volatile/writeable callbacks for status-like registers, and error logging paths that continue through `goto err` for many write failures. Test signals include probe/reset, `TAS2780_IC_CFG` enable, playback/capture at supported rates and 16/20/24/32-bit formats, TDM slot programming, V/I sense capture, mute/unmute, and suspend/resume cache restoration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.h

## Purpose

This header defines the TAS2780 paged register map and bitfields used by `tas2780.c`. It covers page/software reset, power control, DVC/gain, TDM configuration, V/I sense transmit, and IC configuration registers.

## Important APIs, types, and functions

There are no functions or data types. `TAS2780_REG(page, reg)` linearizes addresses. Important register macros are `TAS2780_PAGE`, `TAS2780_SW_RST`, `TAS2780_PWR_CTRL`, `TAS2780_DVC`, `TAS2780_CHNL_0`, `TAS2780_TDM_CFG0` through `TAS2780_TDM_CFG6`, and `TAS2780_IC_CFG`. Bitfields describe ACTIVE/MUTE/SHUTDOWN, V/I sense power bits, DVC max, sample-rate families, RX edge/start, RX word/slot widths, input source format, slot positions, sense enable/slot masks, and IC enable bits.

## Control flow

The header has no runtime control flow. The implementation uses these macros for regmap defaults, DAI operations, mute/suspend/resume, DAPM switches, and codec probe initialization.

## State and persistence behavior

No software state is stored here. The macros define hardware state that is cached by the regmap in `tas2780.c`.

## Dependencies and integration points

The header assumes kernel `BIT()`/`GENMASK()` availability through includers. It is private to the TAS2780 codec driver and should track the hardware datasheet exactly.

## Risks and test signals

Risks include wrong interface source encodings or bit masks causing silent audio routing errors. Test signals are compile coverage of `tas2780.c`, register traces for each DAI format and slot width, and hardware validation for sense capture and IC configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2780.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c

## Purpose

This file provides I2C-specific common support for TAS2563/TAS2781-style multi-amplifier drivers used by both HDA and ASoC front ends. It creates the shared paged regmap, switches the active I2C address/book per channel, implements multi-device volume helpers, resets devices, and starts asynchronous RCA firmware loading.

## Important APIs, types, and functions

Important exported APIs are `tasdev_chn_switch()`, `tasdevice_dev_update_bits()`, `tasdevice_kzalloc()`, `tasdevice_init()`, `tasdevice_amp_putvol()`, `tasdevice_amp_getvol()`, `tasdevice_digital_getvol()`, `tasdevice_digital_putvol()`, `tasdevice_reset()`, and `tascodec_init()`. Internal helpers include `tasdevice_change_chn_book()` and `tasdevice_clamp()`. The regmap uses `TASDEVICE_PAGE_SELECT` as selector, spans 256 pages, and disables caching (`REGCACHE_NONE`).

## Control flow

`tasdevice_kzalloc()` allocates shared private state and records device/client pointers. `tasdevice_init()` initializes the shared I2C regmap, resets current program/config/book trackers to -1, wires function pointers for update/read/bulk-read/book switching, and initializes `codec_lock`. Channel switching mutates the live `i2c_client->addr` to the target amplifier address, resets page selection when crossing devices, and writes the book-control register when needed. Volume put helpers clamp/invert one control value and apply it to every device; get helpers read device 0. `tasdevice_reset()` either toggles reset GPIO or writes per-device software reset. `tascodec_init()` builds the RCA binary name from optional prefix, device name, and `ndev`, populates the CRC8 table, stores the codec pointer, and calls `request_firmware_nowait()`.

## State and persistence behavior

Persistent state lives in `tasdevice_priv`: shared regmap, current program/config, per-device current book/program/config, CRC table, firmware filenames, codec pointer, and mutex. Because all devices share one regmap and the I2C client address is mutated, `cur_book` and page reset behavior are essential. No regcache is used, so reads/writes go directly to hardware.

## Dependencies and integration points

The file depends on I2C, regmap, firmware loading, GPIOs, CRC8, ALSA SoC mixer controls, and public TAS2781 headers `<sound/tas2781.h>` and `<sound/tas2781-comlib-i2c.h>`. Higher-level ASoC/HDA drivers supply `tasdevice_priv` fields such as `ndev`, device addresses, `dev_name`, reset GPIO, and firmware callbacks.

## Risks and test signals

Risks include mutable `client->addr` races if callers do not hold `codec_lock`, surprising success return semantics in volume puts (`0` when all devices fail, `1` otherwise), lack of regcache, and book/page state corruption if external code accesses the same client. Test signals include multi-amplifier register reads/writes on each I2C address, page/book transitions, reset via GPIO and software reset, mixer get/put across all devices, asynchronous RCA firmware request naming, and lock coverage during codec probe/firmware loading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib.c

## Purpose

This file provides transport-neutral common helpers for TAS2563/TAS2781-style drivers. It wraps per-channel register read/write/bulk operations through the active book/page selection callback and frees parsed DSP/config firmware data during driver teardown.

## Important APIs, types, and functions

Exported APIs are `tasdevice_dev_read()`, `tasdevice_dev_bulk_read()`, `tasdevice_dev_write()`, `tasdevice_dev_bulk_write()`, `tasdevice_dsp_remove()`, and `tasdevice_remove()`. Internal cleanup helpers are `tasdev_dsp_prog_blk_remove()`, `tasdev_dsp_prog_remove()`, `tasdev_dsp_cfg_blk_remove()`, and `tasdev_dsp_cfg_remove()`.

## Control flow

Each register accessor validates `chn < ndev`, calls `tas_priv->change_chn_book()` with `TASDEVICE_BOOK_ID(reg)`, then performs the regmap operation on `TASDEVICE_PGRG(reg)`. Errors are logged and returned. DSP remove walks parsed firmware programs and configurations, freeing every block's `data`, each `dev_blks` array, the top-level programs/configs arrays, and the firmware object, then clears `tas_dev->fmw`. `tasdevice_remove()` destroys `codec_lock`.

## State and persistence behavior

The accessors modify current book/channel state through callbacks supplied by the transport layer. Cleanup clears heap-owned firmware state but does not touch RCA config info or calibration firmware; those are handled in the firmware library. Register state persists in hardware/regmap, not this file.

## Dependencies and integration points

The file depends on regmap, firmware data structures and macros from `<sound/tas2781.h>`, and a fully initialized `tasdevice_priv` with `regmap` and `change_chn_book` callbacks. It is exported for use by both I2C common code and higher-level codec/HDA drivers.

## Risks and test signals

Risks include bulk-read invalid-channel path logging but preserving the initial zero return, cleanup paths that assume parser allocation shapes, and dependence on callers to serialize shared regmap/channel switching. Test signals include register accessor error handling for valid/invalid channels, bulk I/O through page/book boundaries, leak checks after failed and successful firmware parsing, and lock destruction only after no worker path can use the private state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c

## Purpose

This file implements firmware support for TASDEVICE/TAS2781-family amplifiers. It parses RCA binaries, DSP coefficient/program/config binaries, and calibration binaries; maps firmware block types to target amplifier channels; executes register command streams; performs optional PRAM/YRAM checksum verification; loads tuning/program/config selections; applies calibrated speaker data; and frees parsed RCA/calibration state.

## Important APIs, types, and functions

Exported APIs include `tasdevice_rca_parser()`, `tasdevice_select_cfg_blk()`, `tas2781_load_calibration()`, `tasdevice_dsp_parser()`, `tasdevice_calbin_remove()`, `tasdevice_config_info_remove()`, `tasdevice_select_tuningprm_cfg()`, `tasdevice_prmg_load()`, and `tasdevice_tuning_switch()`. Important internal helpers include `tasdevice_add_config()`, `map_dev_idx()`, the `fw_parse_*` family for kernel/git/TAS5825 layouts, `fct_param_address_parser()`, `tasdevice_process_block()`, `tasdevice_load_block_kernel()`, CRC/YRAM helpers, `tasdev_load_blk()`, `tasdevice_load_block()`, `dspfw_default_callback()`, `fw_parse_header()`, calibration conversion/preprocessing helpers, and `tasdevice_dspfw_ready()`.

## Control flow

RCA parsing validates image size, minimum version, `ndev` match, config sizes, optional profile names, and block boundaries before storing `tasdevice_config_info` arrays. DSP parsing requests the coefficient binary, validates magic/size/fixed header, selects parser/load callbacks based on driver and PPC versions, parses variable headers, program data, configuration data, and optional calibration parameter address tables. Command execution has two paths: RCA/kernel-style subblocks (`SING_W`, `BURST`, `DELAY`, `FIELD_W`) through `tasdevice_process_block()`, and legacy 4-byte command arrays through `tasdev_load_blk()`. Program/config selection marks active devices from RCA config masks, loads programs when current program differs or force load is set, then loads configurations and calibrated data for devices that successfully loaded. `tasdevice_tuning_switch()` loads pre-power-up or pre-shutdown RCA blocks around playback/tuning state.

## State and persistence behavior

The library mutates `tasdevice_priv` firmware state: `rcabin`, `fmw`, parser/load function pointers, `dspbin_typ`, current program/config, force-load state, per-device `cur_prog`, `cur_conf`, `is_loading`, `is_loaderr`, `err_code`, and calibration-specific data. Parsed firmware and calibration blocks are heap-owned until explicit remove functions free them. Calibration data can rewrite R0, inverse R0, power, and thermal limit registers, and TAS2781-specific preprocessing may adjust sine gain based on default versus calibrated impedance.

## Dependencies and integration points

The file depends on Linux firmware loading, CRC8, unaligned big-endian helpers, regmap-backed `tasdevice_dev_*` callbacks, public TAS2781 data structures/macros, and caller-populated private state such as `ndev`, `chip_id`, firmware names, CRC lookup table, and device address/channel state. It exports symbols in namespace `SND_SOC_TAS2781_FMWLIB` for higher-level TAS2781/TAS2563 drivers.

## Risks and test signals

Risks include large binary parser attack surface, many manual offset/boundary calculations, parser variants selected by firmware version, mutable per-device load state after partial failures, checksum retry semantics that can invalidate current program/config, YRAM checksum logic with excluded swap-command regions, calibration assumptions about exactly one calibration and 15 commands, and potential mismatch between RCA active-device masks and DSP program/config device counts. Test signals include malformed firmware boundary tests, valid RCA/DSP/calibration load for 1/2/4 devices, all supported drv/PPC version parser paths, single/burst/field/delay command execution, checksum pass/fail retry behavior, program/config reload avoidance, calibrated data writes including TAS2781 sine-gain adjustment, cleanup leak checks, and playback tuning switch pre-power/pre-shutdown block loading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-fmwlib.c -->
