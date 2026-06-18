# Research: subset-b-006446

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.c

## Purpose
`ml26124.c` is an ALSA SoC codec driver for the LAPIS/ROHM ML26124 audio codec on I2C. It exposes a single bidirectional DAI named `ml26124-hifi`, initializes an 8-bit I2C regmap with defaults, defines ALSA mixer controls for digital volume, EQ, ALC/limiter, companding, and filters, and describes the codec's DAPM power graph for microphone, DAC, ADC, speaker, and line-out paths.

## Important APIs, Types, And Functions
- `struct ml26124_priv` stores runtime codec state: `mclk`, selected sample `rate`, regmap pointer, clock input mode, and the most recent PCM substream pointer used by mute handling.
- `struct clk_coeff` and `coeff_div[]` encode supported PLL coefficients for 12.288 MHz MCLK at 16 kHz, 32 kHz, and 48 kHz.
- `ml26124_snd_controls[]` defines ALSA controls using `SOC_SINGLE_TLV`, `SOC_SINGLE`, and `SOC_ENUM` for capture/playback volume, EQ bands, ALC/limiter ranges, filters, mute, and ADC/DAC companding.
- `ml26124_dapm_widgets[]` and `ml26124_intercon[]` model supplies (`MCLKEN`, `PLLEN`, `PLLOE`, `MICBIAS`), signal endpoints (`MDIN`, `MIN`, `LIN`, `SPOUT`, `LOUT`), DAC/ADC/PGA widgets, input mux, and output mixer.
- `get_srate()` maps PCM rates to the codec's sampling-rate register codes; unsupported rates return `-EINVAL`.
- `get_coeff()` searches the PLL coefficient table by `mclk` and rate.
- `ml26124_hw_params()` validates `mclk`/rate, stores stream/rate state, configures MCLK input ratio when using MCLKI, writes the sampling-rate register, and programs PLL registers.
- `ml26124_mute()` starts capture or playback run bits based on the stored substream direction, then toggles digital mute in `ML26124_DVOL_CTL`.
- `ml26124_set_dai_fmt()` accepts only I2S, normal bit/frame clocks, and either codec clock provider or consumer mode.
- `ml26124_set_dai_sysclk()` records whether the machine driver uses PLL output or direct MCLK input and stores the frequency.
- `ml26124_set_bias_level()` sequences speaker/preamp bits in `BIAS_ON`, enables VMID and syncs regcache when moving from OFF to STANDBY, and disables VMID in OFF.
- `ml26124_i2c_probe()` allocates private state, creates the I2C regmap, and registers the ASoC component/DAI.

## Control Flow
Probe allocates `ml26124_priv`, binds it to the I2C client, initializes regmap with defaults, and registers the component. Component probe performs a software reset by asserting then clearing `ML26124_SW_RST`. Machine-driver setup calls `set_sysclk()` and `set_fmt()`, then PCM startup invokes `hw_params()` to select the PLL and sampling-rate configuration. DAPM then powers widgets according to active routes; bias transitions enable VMID and sync cached register state after standby. Muting is handled through `mute_stream`, where the run bit for the remembered capture/playback stream is enabled before digital mute is applied or removed.

## State And Persistence
Persistent software state is small and in-memory only: MCLK frequency, sample rate, clock-input selection, and the latest substream pointer. Hardware register persistence is handled through regmap with `REGCACHE_RBTREE`; `regcache_sync()` is explicitly called after VMID startup from `BIAS_OFF`. The driver does not store state across unload/reboot and has no firmware, NVM, or filesystem persistence.

## Dependencies And Integration Points
The driver integrates with Linux I2C, regmap, and ASoC component/DAI/DAPM APIs. Machine drivers must match the `"ml26124"` I2C ID, provide a supported 12.288 MHz `mclk`/rate combination, select `ML26124_USE_PLLOUT` or `ML26124_USE_MCLKI`, and route endpoints such as `MIN`, `LIN`, `SPOUT`, and `LOUT`. It relies on register constants from `ml26124.h`.

## Risks
- `ml26124_mute()` dereferences `priv->substream` without a NULL check; if mute is called before `hw_params()` establishes a substream, a crash is possible.
- Only three 12.288 MHz clock/rate combinations are accepted by `get_coeff()`, despite the DAI formats listing broad sample formats. Unsupported MCLK values fail in `hw_params()`.
- Unsupported direct MCLKI ratios only log `"Unsupported MCLKI"` but continue to program the rest of the path, which may leave hardware misclocked.
- Bias sequencing uses fixed `msleep(100)` and `msleep(500)` delays; regressions can present as pops, startup latency, or incomplete regcache synchronization.
- Register map uses 8-bit register addressing with `write_flag_mask = 0x01`; changes to register definitions must preserve this bus protocol.

## Test Signals
- Build coverage with the ASoC, I2C, and regmap APIs enabled.
- Probe test on an I2C system should show successful component registration and no regmap initialization error.
- PCM playback/capture at 16 kHz, 32 kHz, and 48 kHz with 12.288 MHz MCLK should complete `hw_params()` and program expected PLL registers.
- DAPM route tests should verify `MIN` through `ADC`, `LIN` loopback, DAC-to-speaker, and line-out enable paths.
- Suspend/resume or bias OFF/STANDBY transitions should confirm VMID and regcache behavior without lost control settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.h

## Purpose
`ml26124.h` is the register and bit-definition companion for the ML26124 codec driver. It provides symbolic addresses for clock, system, power, analog, DSP, ALC, limiter, and video-amplifier registers, plus masks and clock-source enums consumed by `ml26124.c`.

## Important APIs, Types, And Defines
- Register addresses cover the codec's major blocks: sampling/PLL (`ML26124_SMPLING_RATE`, `ML26124_PLL*`, `ML26124_CLK_EN`, `ML26124_CLK_CTL`), system reset/run (`ML26124_SW_RST`, `ML26124_REC_PLYBAK_RUN`), power management, analog I/O, SAI interface, DSP/filter/EQ/volume, ALC, playback limiter, and video amplifier.
- Register masks such as `ML26124_R0_MASK`, `ML26124_R26_MASK`, and `ML26124_R68_MASK` document valid writable fields for many registers. The C driver uses a subset directly, especially speaker power and VMID-related masks.
- Clock enable bits `ML26124_MCLKEN`, `ML26124_PLLEN`, `ML26124_PLLOE`, and `ML26124_MCLKOE` correspond to DAPM supplies and clock control.
- Speaker/bias helpers `ML26124_BLT_ALL_ON`, `ML26124_BLT_PREAMP_ON`, and `ML26124_MICBEN_ON` are used during bias-on sequencing.
- `enum ml26124_clk_in` defines the values the machine driver passes into `set_sysclk()`: `ML26124_USE_PLLOUT` and `ML26124_USE_MCLKI`.

## Control Flow And Usage
This header has no executable control flow. Its constants are used by the codec driver to construct regmap defaults, mixer controls, DAPM widgets/routes, PLL setup, mute/run state changes, and bias sequencing. Machine-driver-facing clock selection is represented by the `enum ml26124_clk_in` values; legacy-looking macros `ML26124_USE_PLL` and `ML26124_USE_MCLKI_*FS` are defined but not consumed by the current C implementation.

## State And Persistence
The header defines hardware register locations and bit encodings only. It owns no runtime state and performs no persistence. Any persisted state is in the codec hardware registers and the regmap cache maintained by `ml26124.c`.

## Dependencies And Integration Points
The header is tightly coupled to `ml26124.c` and the ML26124 datasheet register map. It assumes Linux `BIT()` is available through including source context. Constants define the ABI between the codec driver and ML26124 hardware, and `enum ml26124_clk_in` is an integration point for board/machine code selecting sysclk mode.

## Risks
- Several names contain historical typos (`SMPLING`, `PLYBAK`, `BOST`, `BRAND`, `Mnagement` comments). Renaming them without updating users would break compilation.
- Both legacy clock macros and the current `enum ml26124_clk_in` coexist; using the wrong macro family in machine code could be incompatible with `ml26124_set_dai_sysclk()`.
- Mask definitions are not comprehensively used for every register write in `ml26124.c`; future changes should verify masks against the datasheet rather than assuming the header enforces safety.

## Test Signals
- Compile tests should include `ml26124.c` to catch stale or renamed register definitions.
- Static checks can compare every `ML26124_*` address used by the C file with this header.
- Hardware smoke tests should validate that defined bit values for clock enables, VMID, speaker preamp/all-on, and mute/run registers match expected behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ml26124.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-analog.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-analog.c

## Purpose
`msm8916-wcd-analog.c` is the analog/PMIC side of the Qualcomm MSM8916 WCD codec. It controls PM8916 analog audio blocks over the parent PMIC regmap, exposes analog DAPM endpoints for PDM playback/capture, microphones, headphone, earpiece, and speaker paths, manages micbias and ADC/PA sequencing, and implements MBHC headset/button jack detection through threaded interrupts.

## Important APIs, Types, And Functions
- `struct pm8916_wcd_analog_priv` stores PMIC/codec revisions, MBHC state flags, optional jack pointer, regulators, micbias capabilities, headset polarity properties, button thresholds, and the component pointer used by IRQ handlers.
- `supply_names[]` declares required regulators: `vdd-cdc-io` and `vdd-cdc-tx-rx-cx`.
- Mixer controls expose analog ADC gains for ADC1/2/3 with a 0 dB to +24 dB TLV range.
- DAPM muxes select ADC2 input (`INP2`/`INP3`), RDAC2 source (`RX1`/`RX2`), and output switch paths for earpiece/headphone.
- `pm8916_wcd_analog_micbias_enable()` programs MICBIAS1 precharge, optional DT-provided voltage, and a 50 ms delay when the target is at least 2.7 V.
- `pm8916_mbhc_configure_bias()` programs MBHC current-source or micbias-based thresholds for five buttons.
- `pm8916_wcd_setup_mbhc()` configures mechanical headset detection, debounce, plug-type polarity, MBHC clock, button IRQ enablement, and initial detection state.
- `pm8916_wcd_analog_enable_adc()`, `pm8916_wcd_analog_enable_spk_pa()`, and `pm8916_wcd_analog_enable_ear_pa()` are DAPM event handlers that perform pop-safe ADC, speaker PA, and earpiece PA sequences.
- IRQ handlers `mbhc_btn_press_irq_handler()`, `mbhc_btn_release_irq_handler()`, and `pm8916_mbhc_switch_irq_handler()` translate MBHC status into `snd_soc_jack_report()` events.
- `pm8916_wcd_analog_parse_dt()` reads micbias cap mode, micbias voltage, jack polarity, and MBHC threshold arrays from device tree.
- `pm8916_wcd_analog_spmi_probe()` obtains regulators and IRQs, installs threaded handlers, and registers the ASoC component and two PDM DAIs.

## Control Flow
Platform probe allocates state, parses DT, acquires regulators, requests the MBHC switch IRQ and optional button press/release IRQs, stores driver data, and registers the component. Component probe enables regulators, initializes the component regmap from the parent PMIC, reads revision registers, applies reset/default writes, releases digital reset, and calls `pm8916_wcd_setup_mbhc()`. Runtime DAPM routes connect the digital PDM interface to analog ADC/DAC/PA widgets. Capture paths power micbias, ADC muxes, TX clocks, and ADC init/deinit sequences. Playback routes power PDM RX clocks, DACs, charge pump/NCP, RX bias, headphone/ear/speaker drivers, and output muxes. Headset insertion/removal and button presses are handled asynchronously through threaded IRQs and reported to the ASoC jack layer.

## State And Persistence
State is in-memory and hardware-register backed. `pmic_rev` and `codec_version` are read once at probe. MBHC flags (`detect_accessory_type`, `mbhc_btn0_released`, `mbhc_btn_enabled`) preserve detection context across interrupt events. DT-derived thresholds and polarity settings persist for the driver lifetime. Regulators stay enabled from component probe until component remove. No data is persisted outside hardware registers and kernel memory.

## Dependencies And Integration Points
The driver depends on the PM8916 parent regmap, regulator framework, platform IRQ resources named `mbhc_switch_int`, `mbhc_but_press_det`, and `mbhc_but_rel_det`, ASoC component/DAPM/DAI APIs, and the jack reporting API. It matches `qcom,pm8916-wcd-analog-codec` and pairs with the MSM8916 WCD digital codec through PDM routes (`PDM_RX1..3`, `PDM_TX`) and shared clock/control registers in the PMIC address space.

## Risks
- IRQ handlers call `snd_soc_jack_report(priv->jack, ...)` without checking whether `.set_jack` has provided a jack; platforms enabling IRQs before jack registration may crash.
- MBHC accessory type detection depends on ordering of BTN0 press/release and switch interrupts; races or missing IRQs can misclassify headphone vs headset.
- DT threshold arrays are all-or-nothing for button detection; missing one property disables MBHC buttons and logs an error.
- Probe enables regulators in component probe, not platform probe; failed later initialization paths need to preserve regulator cleanup through component remove semantics.
- Many analog sequences require precise delays and bit ordering to avoid pops; regressions may be audible rather than compile-visible.
- `pm8916_wcd_analog_enable_adc()` shares TX2 connection logic for ADC2/ADC3 and must preserve fallthrough semantics on power-down.

## Test Signals
- Probe should read PMIC/codec revision and register both PDM DAIs.
- DT tests should cover micbias cap modes, micbias voltage, normally-open polarity booleans, and missing MBHC threshold arrays.
- Jack tests should insert/remove three-pole and headset accessories and press all five supported buttons.
- Audio path tests should exercise ADC1/ADC2/ADC3 capture and RX1/RX2/RX3 playback to earpiece, headphones, and speaker.
- Regulator and remove tests should verify supplies are disabled and reset is asserted on component removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-digital.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-digital.c

## Purpose
`msm8916-wcd-digital.c` is the LPASS digital-codec side of the Qualcomm MSM8916 WCD audio subsystem. It maps MMIO codec registers through regmap, manages AHB and master clocks, exposes I2S playback/capture DAIs, configures sample format/rate, implements digital gains, mute, HPF/DC blocker, IIR filter coefficient controls, and models the digital DAPM graph between I2S, decimators/interpolators, DMICs, IIR blocks, and PDM links to the analog codec.

## Important APIs, Types, And Functions
- `struct msm8916_wcd_digital_priv` stores `ahbclk` and `mclk` handles.
- `struct wcd_iir_filter_ctl` backs custom byte controls generated by `WCD_IIR_FILTER_CTL()` for two IIR filters with five bands each.
- `rx_gain_reg[]` and `tx_gain_reg[]` map logical RX/TX volume controls to hardware registers.
- `msm8x16_wcd_get_iir_band_audio_mixer()` and `msm8x16_wcd_put_iir_band_audio_mixer()` read/write five 32-bit coefficients for an IIR band through indexed coefficient registers.
- `msm8916_wcd_digital_enable_interpolator()` applies RX gain after interpolator enable and resets interpolators after power-down.
- `msm8916_wcd_digital_enable_dec()` mutes TX, forces HPF cutoff/enables HPF during decimator startup, restores gain, unmutes, and resets decimator logic during shutdown.
- `msm8916_wcd_digital_enable_dmic()` parses the DAPM widget name (`DMIC1`/`DMIC2`) to select clock dividers for the shared DMIC clock and TXn DMIC control.
- `msm8916_wcd_digital_component_set_sysclk()` sets the MCLK rate requested by machine code.
- `msm8916_wcd_digital_hw_params()` maps 8/16/32/48 kHz and S16/S32 formats to TX/RX I2S control bits.
- `msm8916_wcd_digital_startup()` enables MCLK and PDM feedback-clock selection and validates whether MCLK is 12.288 MHz or 9.6 MHz for top control programming.
- `msm8916_wcd_digital_probe()` maps MMIO, creates regmap, obtains/enables clocks, stores private data, and registers the component/DAIs.

## Control Flow
Platform probe maps the register resource, creates a 32-bit stride MMIO regmap, gets `ahbix-clk` and `mclk`, enables both clocks, and registers the component with two DAIs: `msm8916_wcd_digital_i2s_rx1` for playback and `msm8916_wcd_digital_i2s_tx1` for capture. Component probe binds private state. Machine code may set MCLK through `.set_sysclk`. PCM startup enables digital MCLK/PDM settings and encodes the MCLK frequency. `hw_params()` writes rate and word-size bits. DAPM powers digital routes: I2S RX enters RX mixers/interpolators and exits as PDM RX1/2/3; capture enters through analog ADC or DMIC selections, decimators, CIC muxes, and I2S TX outputs. IIR blocks can be inserted into RX and sidetone routes.

## State And Persistence
Runtime state is limited to prepared clock handles and hardware registers. The regmap uses `REGCACHE_FLAT`, but there is no explicit suspend/resume or cache sync logic in this file. IIR coefficient state lives in hardware registers and can be read/written through ALSA byte controls. Clock enable state is managed across probe/remove, while per-stream MCLK/PDM control is toggled during startup/shutdown.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, clocks named `ahbix-clk` and `mclk`, regmap-mmio, ASoC component/DAI/DAPM, and a DT compatible of `qcom,msm8916-wcd-digital-codec`. It integrates with the analog PM8916 WCD driver via named DAPM endpoints (`PDM_RX1..3`, `LPASS_PDM_TX`) and with machine drivers through `AIF1 Playback`/`AIF1 Capture`, sysclk, and DAPM mux selections.

## Risks
- `startup()` logs invalid MCLK rates but returns success, allowing a misclocked stream to continue.
- Supported DAI rates macro includes only 8/16/32/48 kHz, and `hw_params()` rejects other rates; machine constraints should match this.
- IIR byte controls copy `params->max` bytes without semantic validation of coefficient stability or endianness beyond raw 32-bit packing.
- `msm8916_wcd_digital_enable_dmic()` derives DMIC number from widget-name text; renaming widgets would break the parser.
- Clock enable occurs at probe and remains active until remove; runtime PM is not implemented here.
- DAPM route table has repeated-looking IIR routes for RX2/RX3; route changes need careful audio-graph validation.

## Test Signals
- Probe tests should validate MMIO mapping, clock acquisition/enabling, and component registration.
- PCM tests should verify 8, 16, 32, and 48 kHz playback/capture in S16_LE and S32_LE.
- DAPM tests should route I2S RX through RX1/RX2/RX3, capture through ADC and DMIC paths, and exercise IIR sidetone insertion.
- ALSA control tests should read/write digital volume, mute, HPF/DC blocker controls, and all IIR band coefficient byte controls.
- Remove tests should confirm both clocks are disabled/unprepared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/msm8916-wcd-digital.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.c

## Purpose
`mt6351.c` is the MediaTek MT6351 PMIC codec driver. It registers one ASoC DAI for playback/capture, exposes analog playback/capture gains and muxes, and uses DAPM event handlers to sequence MT6351 audio clocks, DAC/ADC paths, headphone/lineout/receiver drivers, micbias supplies, NCP, sine generator, and uplink/downlink sample-rate programming.

## Important APIs, Types, And Functions
- `struct mt6351_priv` stores the parent regmap, device pointer, last playback/capture rates, analog gain snapshots, and `hp_en_counter` for shared HPL/HPR sequencing.
- `mt6351_codec_dai_hw_params()` records playback (`dl_rate`) or capture (`ul_rate`) rate for later DAPM event programming.
- `get_play_reg_val()` and `get_cap_reg_val()` map PCM rates to hardware register codes.
- `hp_gain_ramp_set()`, `hp_zcd_enable()`, `hp_zcd_disable()`, and `set_hp_gain_zero()` implement pop-reduction volume and zero-cross behavior around headphone power transitions.
- `mt_reg_set_clr_event()` abstracts PMIC SET/CLR companion-register writes for top clocks such as `TOP_CLKSQ` and `TOP_CKPDN_CON0`.
- `mt_ncp_event()`, `mt_sgen_event()`, `mt_aif_in_event()`, and `mt_aif_out_event()` configure NCP, sine generator, downlink digital path, and uplink digital path.
- `mt_hp_event()` is the main HPL/HPR power sequence, including counter-based shared-channel handling, gain saving/restoring, ZCD, de-oscillation, precharge, and pop-safe ramping.
- `mt_pga_left_event()`, `mt_pga_right_event()`, and `mt_mic_bias_*_event()` sequence analog capture preamplifiers and micbias voltages.
- `mt6351_dapm_widgets[]` and `mt6351_dapm_routes[]` describe full capture and playback power graphs.
- `mt6351_codec_init_reg()` applies initial low-power/default safety settings at component probe.

## Control Flow
Platform probe allocates `mt6351_priv`, obtains the regmap from the parent PMIC device, and registers the component plus `mt6351-snd-codec-aif1`. Component probe initializes the component regmap and applies baseline register programming. PCM `hw_params()` records rates but does not directly program sample-rate registers. DAPM later powers the graph: playback through `AIF_RX` configures digital downlink and PMIC interface rate, powers global/DL supplies, DACs, muxes, and output drivers; capture through `AIF1TX` configures DCCLK and UL sample rate, powers ADC/PGA/micbias supplies, and routes selected AIN inputs to ADCs. Headphone paths coordinate left/right widgets with `hp_en_counter` so common power sequencing runs once for stereo use.

## State And Persistence
Driver state is runtime-only. `dl_rate` and `ul_rate` persist between `hw_params()` and DAPM events. `ana_gain[]` temporarily stores target analog gain values during headphone transitions, and `hp_en_counter` tracks active headphone channels. Hardware registers and the parent PMIC regmap hold the actual codec state. No filesystem, firmware, or NVM persistence is used.

## Dependencies And Integration Points
The driver depends on the parent PMIC regmap, ASoC DAI/component/DAPM APIs, and register definitions from `mt6351.h`. It matches DT compatible `mediatek,mt6351-sound`. The machine driver consumes stream names `AIF1 Playback` and `AIF1 Capture` and DAPM pins such as `Receiver`, `Headphone L/R`, `LINEOUT L`, and `AIN0..AIN3`.

## Risks
- Sample-rate programming happens in DAPM event handlers using the last value captured in `hw_params()`; unexpected DAPM ordering or missing `hw_params()` could leave default/zero rates.
- `hp_en_counter` can go negative on unbalanced DAPM events; the code logs errors but continues.
- Many register writes use full `0xffff` masks, making regressions easy if adjacent bit semantics change.
- Pop/click avoidance depends on precise delays, ZCD settings, and gain ramping.
- The capture path has special handling for rates <= 48 kHz through HPANC registers; high-rate capture needs separate validation.
- There is no explicit runtime PM or suspend/resume handling in this file.

## Test Signals
- Build and probe with a parent MT6351 regmap should register one DAI and component controls.
- Playback tests should cover 8 kHz through 192 kHz, with 44.1/48 kHz families routed to headphones, receiver, and lineout.
- Capture tests should cover AIN0/AIN1/AIN2/AIN3 routes, both PGAs, micbias 0/1/2, and low/high sample rates.
- Headphone stereo enable/disable should verify `hp_en_counter` behavior, volume restoration, and absence of audible pops.
- Sine generator routes should confirm DAPM can use `DAC In Mux`/`AIF Out Mux` test paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.h

## Purpose
`mt6351.h` is the MT6351 codec register-address map used by `mt6351.c`. It names the PMIC audio register offsets for AFE digital controls, top clock controls, zero-cross detection, LDO controls, decoder analog controls, and encoder analog controls.

## Important APIs, Types, And Defines
- AFE digital registers include `MT6351_AFE_UL_DL_CON0`, downlink source/SDM controls, uplink source controls, audio top controls, PMIC new-interface configuration, sine generator registers, DCCLK registers, HPANC, and NCP configuration.
- Top-level clock and CLKSQ registers include `MT6351_TOP_CKPDN_CON0`, `_SET`, `_CLR`, `MT6351_TOP_CLKSQ`, `_SET`, and `_CLR`.
- ZCD volume/control registers `MT6351_ZCD_CON0..5` back headphone, lineout, and handset volume and zero-cross behavior.
- LDO register definitions cover VA18 and VUSB33 supplies.
- Decoder analog registers `MT6351_AUDDEC_ANA_CON0..10` back DAC, headphone, receiver, lineout, bias, LDO, and regulator control.
- Encoder analog registers `MT6351_AUDENC_ANA_CON0..16` back ADCs, preamps, micbiases, and ADC clocking.

## Control Flow And Usage
This header contains no code. `mt6351.c` combines these addresses with locally defined bit positions to build controls, DAPM widgets, DAPM routes, and event-handler register writes. The address layout uses 16-bit-style PMIC register spacing and includes grouped digital AFE registers starting at `0x2000`.

## State And Persistence
The header defines constants only. Register state exists in MT6351 hardware and the parent PMIC regmap. No runtime state is declared here.

## Dependencies And Integration Points
`mt6351.c` includes this header directly. The definitions are coupled to the parent MFD/regmap address space for MT6351 and to MediaTek machine drivers that instantiate `mediatek,mt6351-sound`.

## Risks
- The header provides addresses but not masks; most bit definitions live in `mt6351.c`, so changes must keep both files synchronized with the datasheet.
- Many register names are consumed directly by DAPM widgets and event handlers; renaming breaks build-time linkage.
- Because the address constants are raw PMIC offsets, an incorrect parent regmap or incompatible chip revision could write unrelated PMIC registers.

## Test Signals
- Compile `mt6351.c` to validate all register names.
- Probe on MT6351 hardware should verify that initial writes to clock, decoder, and PMIC-newif registers land at expected offsets.
- Register-dump based tests can compare `mt6351_codec_init_reg()` and major DAPM sequences against these symbolic addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6351.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.c

## Purpose
`mt6357.c` is the MediaTek MT6357 PMIC codec driver. It registers one high-rate ASoC DAI, exposes playback/capture gains and muxes, configures audio GPIO pin modes, parses micbias/pull-down device-tree options, and implements detailed DAPM event sequencing for analog/digital supplies, downlink DAC/headphone/handset/lineout paths, uplink analog/digital microphone paths, loopback, and sine-generator paths.

## Important APIs, Types, And Functions
- `struct mt6357_priv` comes from `mt6357.h` and stores device, parent regmap, headphone pull-down setting, and active headphone-channel count.
- `set_playback_gpio()` and `set_capture_gpio()` switch MOSI/MISO pins between audio mode and GPIO input mode to avoid leakage and strap conflicts.
- `hp_main_output_ramp()`, `hp_aux_feedback_loop_gain_ramp()`, `hp_pull_down()`, `volume_ramp()`, `lo_volume_ramp()`, `hp_volume_ramp()`, and `hs_volume_ramp()` implement pop-safe output transitions.
- `mt6357_controls[]` exposes headphone, lineout, handset, headphone input degain, and mic volume controls.
- `mt6357_set_dmic()`, `mt6357_set_amic()`, `mt6357_set_loopback()`, and `mt6357_set_ul_sine_gen()` program the selected uplink source type.
- `mt_mic_type_event()` dispatches DAPM mic-type mux power events to the correct uplink setup/teardown function.
- `mt_adc_supply_event()`, `mt_pga_left_event()`, `mt_pga_right_event()`, and `adc_enable_event()` sequence ADC supply, analog PGA, ADC, UL source, and TX FIFO state.
- `configure_downlinks()` powers downlink supplies, NCP, LDOs, short-circuit settings, bias, decoder clock, and DAC low-noise mode.
- `mt_audio_in_event()` enables playback GPIOs, prepares the digital downlink scrambler/FIFO path, calls `configure_downlinks()`, and reverses the sequence on shutdown.
- `lo_mux_event()`, `hs_mux_event()`, and `hp_main_mux_event()` are output-driver sequences with gain save/ramp/restore and shared headphone channel tracking.
- `left_dac_event()` and `right_dac_event()` power DACs and optional headphone pull-downs.
- `mt6357_parse_dt()` reads `mediatek,hp-pull-down`, `mediatek,micbias0-microvolt`, and `mediatek,micbias1-microvolt`.
- `mt6357_platform_driver_probe()` enables `vaud28`, obtains the parent `mt6397` regmap, parses DT, configures DMA mask, and registers the component.

## Control Flow
Platform probe enables the `vaud28` regulator, allocates private state, obtains the MFD parent regmap from `mt6397_chip`, applies DT micbias settings into hardware registers, sets DMA mask, and registers the component/DAI. Component probe briefly enables the audio clock, disables output short-circuit protection for initialization, forces playback/capture GPIOs to safe GPIO-input state, then disables the audio clock. Runtime DAPM powers capture by enabling GPIO MISO mode, clock/supply widgets, mic type mux, ADC supply, ADC/PGA widgets, and the selected AMIC/DMIC/loopback/sine source. Playback powers GPIO MOSI mode, digital FIFO/scrambler, downlink supplies, DACs, and selected lineout/handset/headphone output. Headphone left/right widgets share `hp_channel_number` so the complex main-output sequence runs once when stereo paths are both active.

## State And Persistence
Runtime state is limited to `pull_down_needed`, `hp_channel_number`, device/regmap pointers, and hardware register contents. Micbias voltage indices are written during probe from DT and then persist in hardware registers for driver lifetime. Gain values are read from registers, temporarily forced to -40 dB during output startup/shutdown, then restored. No filesystem or firmware persistence is used.

## Dependencies And Integration Points
The driver depends on the MT6397 MFD parent (`struct mt6397_chip`) for the regmap, the regulator named `vaud28`, ASoC component/DAPM APIs, and register definitions from `mt6357.h`. It binds through platform ID `mt6357-sound` and uses `PROBE_PREFER_ASYNCHRONOUS`. Machine drivers use stream names `MT6357 Playback` and `MT6357 Capture`, DAPM endpoints `Headphones`, `Hansdet` (typo in widget name), `Line out`, `AIN0..2`, `LPBK`, and `SGEN` paths.

## Risks
- `mt6357_platform_driver_probe()` assumes `dev_get_drvdata(pdev->dev.parent)` returns a valid `mt6397_chip`; missing parent data would dereference a NULL pointer before regmap validation.
- `mt_pga_right_event()` powers down the right ADC input selection using `MT6357_AUDENC_ANA_CON0` with right-channel masks, which is suspicious and should be reviewed against hardware behavior.
- `hs_mux_event()` disables HS driver bias by writing the enable value during PRE_PMD, which may be intentional retention or a bug; hardware tests should confirm.
- `hp_channel_number` can underflow if DAPM events are unbalanced; the code does not log negative counts.
- Output sequencing has many fixed delays and full-stage ramps; regressions may only appear as pops, leakage, or slow transitions.
- Widget/output name `"Hansdet"` appears misspelled and may require machine drivers to use that exact spelling.
- Capture rates are advertised as continuous 8 kHz to 192 kHz but this file does not program per-rate coefficients; external interface assumptions must be validated.

## Test Signals
- Probe should enable `vaud28`, parse parent DT micbias values, initialize GPIO modes, and register one DAI.
- Playback tests should route normal and sine-generator paths to headphones, lineout, and handset while monitoring pops and gain restoration.
- Capture tests should cover ACC, DCC, DCC ECM differential/single-ended, DMIC, loopback, and uplink sine-generator modes.
- DT tests should verify `mediatek,hp-pull-down` and all supported micbias voltages, including fallback to index 0 on invalid values.
- GPIO register checks should confirm MOSI/MISO pins return to GPIO input mode when streams stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.h

## Purpose
`mt6357.h` is the register, bitfield, format/rate, gain, and private-state definition header for the MT6357 codec driver. It supplies the symbolic hardware contract used by `mt6357.c` for GPIO audio pin muxing, audio clocks, AFE/ADDA controls, encoder/decoder analog blocks, ZCD gains, micbias settings, DAC/headphone/lineout/handset controls, and driver private data.

## Important APIs, Types, And Defines
- GPIO mode/direction constants define audio MOSI pins GPIO8-11 and audio MISO pins GPIO12-15, plus SET/CLR helpers used by playback/capture GPIO switching.
- Clock/top constants cover `MT6357_DCXO_CW14`, `MT6357_AUD_TOP_CKPDN_CON0`, `AUDNCP` clock divider registers, AFE on bits, and `MT6357_AUDIO_TOP_CON0` power-down bits.
- Digital AFE/ADDA constants cover uplink/downlink enable bits, sine generator bits, DCCLK configuration, loopback, TX FIFO normal/loopback paths, and scrambler/FIFO controls.
- Encoder analog constants cover ADC L/R input selection, preamp gain, precharge, DCC/ACC mode, DMIC enable/bias, MICBIAS0/1 voltage fields, and DC-coupling switches.
- Decoder analog constants cover DAC power, headphone/handset/lineout muxes, bias, short-circuit protection, output stages, feedback loops, CMFB, low-noise mode, decoder reset, LDOs, NV regulator, and HP trim.
- ZCD/gain constants define playback gain enum values and register masks/shifts for lineout, headphone, and handset gains.
- `MT6357_SND_SOC_ADV_MT_FMTS` advertises 16/24/32-bit signed and unsigned little/big endian PCM formats; `MT6357_SOC_HIGH_USE_RATE` advertises continuous 8 kHz to 192 kHz capture.
- `struct mt6357_priv` stores `dev`, `regmap`, `pull_down_needed`, and `hp_channel_number`.

## Control Flow And Usage
The header has no executable code. `mt6357.c` uses these definitions in every helper and DAPM event sequence. The constants are organized by hardware register block and then by register address list, allowing event handlers to combine masks, shifts, and values with `regmap_update_bits()` or `regmap_write()`.

## State And Persistence
Only `struct mt6357_priv` describes runtime software state; the rest of the header is symbolic register metadata. Hardware register values persist while the PMIC remains powered and are controlled by the regmap writes in `mt6357.c`. There is no standalone persisted data.

## Dependencies And Integration Points
The header includes `<linux/types.h>` and expects bit macros such as `BIT()`/`GENMASK()` from kernel include context. It is coupled to MT6357 PMIC audio hardware, the MT6397 parent regmap, and the ASoC codec implementation in `mt6357.c`. Its PCM format/rate macros are part of the DAI capabilities presented to machine drivers.

## Risks
- Because many masks and values encode analog power sequencing, incorrect bit definitions can produce audible pops, power leakage, or hardware stress rather than obvious software failures.
- `struct mt6357_priv` is shared between header and C file; adding fields affects all code that allocates or inspects codec private data.
- The broad PCM format/rate macros may overstate what a specific board or upstream digital interface can safely support.
- Typographical compatibility matters: constants and endpoint names used by the C file should not be renamed casually.

## Test Signals
- Compile `mt6357.c` to validate all register/bitfield references.
- Hardware register traces during playback/capture should match the masks and shifts in this header.
- ALSA capability tests should confirm advertised formats/rates against the SoC audio interface.
- DT/probe tests should verify micbias VREF fields are programmed with the expected index shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6357.h -->
