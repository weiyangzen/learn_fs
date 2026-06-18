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
