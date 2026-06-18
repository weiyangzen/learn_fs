# subset-b-006447 MediaTek codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.c

## Purpose

This file implements the ALSA SoC codec component for the MediaTek MT6358/MT6366 PMIC audio codec. It registers a single bidirectional DAI, exposes mixer controls, defines DAPM widgets and routes for playback, receiver, lineout, analog microphone, digital microphone, sine-generator, and wake-on-voice paths, and programs the PMIC register map through ordered analog and digital power sequences.

## Important APIs, types, and functions

`struct mt6358_priv` is the private runtime state: PMIC `regmap`, cached playback/capture rates, analog gain cache, mux selections, output device reference counters, selected MTKAIF protocol, AVDD regulator, wake-on-voice state, and DMIC one-wire mode. `mt6358_set_mtkaif_protocol()` is exported so the machine driver can choose MTKAIF protocol 1, protocol 2, or protocol 2 clock phase 2 during initialization. `mt6358_snd_controls` exposes headphone, lineout, handset, PGA, wake-on-voice, and DMIC mode controls. `mt6358_dapm_widgets` and `mt6358_dapm_routes` describe the complete ASoC power graph.

Key event and sequencing helpers are `playback_gpio_set/reset()`, `capture_gpio_set/reset()`, `mt6358_mtkaif_tx_enable/disable()`, `mt_aif_in_event()`, `mt_aif_out_event()`, `mt_adc_supply_event()`, `mt_hp_event()`, `mt_rcv_event()`, `mt_mic_type_event()`, `mt6358_amic_enable/disable()`, `mt6358_dmic_enable/disable()`, and wake-on-voice `mt6358_enable_wov_phase2()` / `mt6358_disable_wov_phase2()`. Probe flows through `mt6358_platform_driver_probe()`, `mt6358_codec_probe()`, and `mt6358_codec_init_reg()`.

## Control flow

Platform probe allocates `mt6358_priv`, obtains the parent MT6397 PMIC regmap, reads `mediatek,dmic-mode`, and registers the ASoC component and DAI. Component probe binds the regmap to ALSA, initializes codec registers, resets playback/capture GPIO pins to input/GPIO mode, obtains the `Avdd` regulator, and enables it.

Playback setup starts when DAPM powers `AIF_RX`: MOSI pins switch to audio mode and the SDM/scrambler FIFO is enabled. The headphone DAPM mux calls `mt_hp_event()`, which reference-counts the headphone output and dispatches to `mtk_hp_enable()` for normal headphone playback or `mtk_hp_spk_enable()` for loudspeaker-through-headphone path. These sequences deliberately ramp pull-downs, NCP, capless LDOs, NV regulator, DAC clocks, output stages, feedback loops, and volume to avoid pops. Disable paths reverse the sequence and ramp gain back to the minimum. Receiver playback uses `mt_rcv_event()` with a similar but handset-specific NCP/DAC/HS driver sequence.

Capture setup starts when `AIF1TX` is powered: MISO pins switch to audio mode. `ADC Supply` enables ADC clock generation and the encoder LDO. `Mic Type Mux` records the selected mic mode on `WILL_PMU`, then chooses analog mic or DMIC programming on `PRE_PMU`. Analog mic enable configures DCC clocking, micbias rails, preamp input selection, left/right ADC power, MTKAIF TX FIFO mode, and UL source enable. DMIC enable powers micbias and the DMIC block, selects one-wire or normal digital format using `dmic_one_wire_mode`, enables MTKAIF TX, and waits 100 ms to avoid DMIC pop noise. `POST_PMD` disables the selected path and resets the relevant analog/digital blocks.

## State and persistence behavior

The driver caches user-visible analog gains in `ana_gain[]` because power-up sequences temporarily write safe minimum gains and later restore the requested values. `mux_select[]` records DAPM mux choices that are needed by later power events, especially mic type and PGA source. `dev_counter[DEVICE_HP]` prevents duplicate headphone power sequencing when both HPL and HPR widgets traverse the same event function. `dl_rate` and `ul_rate` are stored from `hw_params()` for logging only; no rate-dependent register programming is done here. `wov_enabled`, `dmic_one_wire_mode`, and `mtkaif_protocol` persist runtime control or machine-driver configuration until changed.

Hardware state persists in PMIC registers, not in memory. Most operations use direct `regmap_write()` or masked `regmap_update_bits()` with sleeps between analog stages. There is no explicit remove or regulator-disable path in this file, so managed device teardown handles allocation lifetime while AVDD disable is not represented in a component remove callback.

## Dependencies and integration points

The file depends on ALSA SoC component, DAI, DAPM, and control APIs; the MT6397 MFD parent for `regmap`; Linux regulator APIs for `Avdd`; PMIC register definitions from `mt6358.h`; and a platform device with compatible `mediatek,mt6358-sound` or `mediatek,mt6366-sound`. Machine drivers integrate by binding the `mt6358-snd-codec-aif1` DAI and may call exported `mt6358_set_mtkaif_protocol()` before capture. Device tree supplies `mediatek,dmic-mode`.

The DAI advertises playback at 8 kHz to 48 kHz plus 96/192 kHz, capture at 8/16/32/48 kHz, one or two channels, and 16/24/32-bit signed or unsigned little-endian formats. DAPM route names such as `Headphone L`, `Receiver`, `AIN0`, and `AIF1 Capture` are the integration contract used by board audio routing.

## Risks and test signals

Risks center on ordered analog sequencing: incorrect register values, missing delays, or mismatched disable order can cause pops, leakage, muted audio, or PMIC current draw. The headphone counter is only a simple integer and relies on serialized DAPM event ordering. The driver enables AVDD without a matching explicit disable path. MTKAIF protocol mismatches can silently break capture. Volume cache correctness depends on mixer writes passing through `mt6358_put_volsw()`. DMIC one-wire mode is only read at probe or changed through the control, so board defaults must match hardware wiring.

Useful test signals are successful component probe with `Avdd`, DAPM route enumeration, playback on headphone/receiver/lineout paths without pops, capture from ACC/DCC/DMIC paths, no MISO leakage during playback-only idle, correct behavior for both MTKAIF protocol modes, wake-on-voice phase2 toggle register effects, suspend/resume playback and capture recovery, and no negative `dev_counter[DEVICE_HP]` warnings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.h

## Purpose

This header is the MT6358 codec register contract for `mt6358.c`. It defines PMIC audio register addresses, bit shifts, raw masks, shifted masks, MTKAIF protocol identifiers, and the exported protocol-selection function prototype. It is intentionally hardware-map heavy and contains no executable logic beyond the public declaration.

## Important APIs, types, and functions

The header defines bitfield triples with the common pattern `*_SFT`, `*_MASK`, and `*_MASK_SFT` for audio top clocks, resets, interrupts, NCP clock divider, AFE digital blocks, MTKAIF FIFOs and protocol controls, sine generator, ADC/DMIC/DCC, wake-on-voice, analog encoder, analog decoder, LDO/NV regulator, ZCD gain, GPIO mode, and ACCDET registers. Register address macros span PMIC GPIO/DCXO/OTP/AUXADC space and the audio ranges from `MT6358_AUD_TOP_ID` through `MT6358_ZCD_CON5`.

Important public symbols are `MT6358_MAX_REGISTER`, the enum values `MT6358_MTKAIF_PROTOCOL_1`, `MT6358_MTKAIF_PROTOCOL_2`, and `MT6358_MTKAIF_PROTOCOL_2_CLK_P2`, and the prototype `mt6358_set_mtkaif_protocol(struct snd_soc_component *cmpnt, int mtkaif_protocol)`.

## Control flow

There is no runtime control flow. The header controls how `mt6358.c` builds register update masks and how external machine-driver code names MTKAIF protocol choices. The grouping of macros mirrors hardware blocks: top clocks/resets and interrupts first, then audio digital AFE and MTKAIF blocks, VOW registers, encoder analog registers, decoder analog registers, ZCD gain registers, raw register addresses, and finally protocol exports.

## State and persistence behavior

No memory state is declared. The state represented by this header is persistent PMIC register state manipulated elsewhere through `regmap`. Register definitions such as clock power-down, reset, interrupt status, LDO, NCP, analog mux, PGA gain, and VOW fields are the symbolic view of the hardware state that survives between individual driver calls until overwritten or reset by hardware.

## Dependencies and integration points

The header is included by `mt6358.c` and requires the ALSA SoC `struct snd_soc_component` type for the exported function prototype. It also implicitly integrates with machine drivers that call `mt6358_set_mtkaif_protocol()` and with any regmap range validation using `MT6358_MAX_REGISTER`. Macro names are consumed directly by the codec driver's DAPM events, controls, and probe-time register initialization.

## Risks and test signals

Risks are definition drift against the PMIC datasheet or silicon variant, incorrectly shifted masks, overlapping register addresses, and the `MT6358_MAX_REGISTER` value excluding later defined registers such as `MT6358_ACCDET_CON13` if used for strict regmap range policy elsewhere. Because many driver writes use literal full-register constants, bitfield bugs may only appear in masked updates. Test signals are clean compilation, no undefined register or bitfield names, successful regmap writes to all referenced addresses, expected ALSA control bit behavior, correct MTKAIF protocol register programming, and hardware readback/debugfs checks matching datasheet bit locations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6358.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.c

## Purpose

This file implements the MT6359 PMIC accessory detector ASoC component. It detects headset/headphone plug state through PMIC EINT/ACCDET hardware, classifies headset buttons by calibrated voltage thresholds, reports jack and button state to ALSA jack core, and initializes ACCDET analog/digital debounce, micbias, EINT, and fast-discharge settings from device tree.

## Important APIs, types, and functions

`struct mt6359_accdet` is declared in the companion header and holds the ALSA jack pointer, device/regmap, parsed DTS data, capability flags, IRQ numbers, lock, plug/button state, calibration voltage, jack-detect status, and two single-thread workqueues. Capability bits in this C file describe PMIC EINT versus AP GPIO EINT, EINT0/EINT1/BI EINT routing, trigger type, key-count mode, and fast-discharge features.

Important functions include `mt6359_accdet_parse_dt()`, `mt6359_accdet_init()`, `config_eint_init_by_mode()`, `config_digital_init_by_mode()`, `accdet_set_debounce()`, `mt6359_accdet_irq()`, `mt6359_accdet_work()`, `mt6359_accdet_jd_work()`, `check_jack_btn_type()`, `check_button()`, `mt6359_accdet_jack_report()`, `mt6359_accdet_enable_jack_detect()`, and `mt6359_accdet_probe()`. EINT transition helpers are `adjust_eint_analog_setting()`, `adjust_eint_digital_setting()`, `mt6359_accdet_jd_setting()`, `recover_eint_analog_setting()`, `recover_eint_digital_setting()`, and `mt6359_accdet_recover_jd_setting()`.

## Control flow

Probe allocates private state, DTS data, and PWM/debounce storage, takes the parent MT6397 regmap, parses the `accdet` child node, initializes `res_lock`, requests the main ACCDET IRQ and the selected PMIC EINT IRQ, creates dedicated workqueues for ACCDET state and jack-detect state, registers an ASoC component, sets initial state to unplugged, then calls `mt6359_accdet_init()`.

Initialization toggles ACCDET sequence init and reset, programs ACCDET and EINT debounce values, configures PWM width/threshold/rise/fall delay, configures micbias voltage and headset mode, optionally enables analog fast discharge, and initializes PMIC EINT analog/digital detection when DTS selected PMIC EINT. Runtime IRQ handling reads `ACCDET_IRQ_ADDR`: an ACCDET interrupt is acknowledged and queues `accdet_work`; an EINT interrupt is acknowledged, EINT memory state is read into `jd_sts`, jack-detection settings are adjusted, and `jd_work` is queued.

`mt6359_accdet_work()` re-reads ACCDET state memory and classifies state 0 as headphone or pressed headset button, state 1 as headset or button release, and state 3/default as unplugged. It reports changes only while `jack_plugged` is true. `mt6359_accdet_jd_work()` handles plug-in by setting `jack_plugged`, pulsing sequence init, and enabling ACCDET; plug-out disables ACCDET, restores debounce/EINT settings, clears jack/button state, and reports unplug. `mt6359_accdet_enable_jack_detect()` maps ALSA button bits to input key codes and stores the jack pointer.

## State and persistence behavior

Runtime state is protected by `res_lock` across IRQ and workqueue operations. `jack_plugged`, `jack_type`, `btn_type`, `accdet_status`, `pre_accdet_status`, `cali_voltage`, and `jd_sts` are the in-memory state used to decide what to report. Parsed device-tree settings persist in `struct dts_data`, including mic voltage/mode, plugout debounce, EINT polarity/detection mode, key thresholds, EINT comparator settings, and PWM/debounce values. Hardware state persists in PMIC registers: IRQ clear/status bits, debounce registers, EINT analog switches/resistors/inverters, ACCDET enable, micbias, PWM, and fast-discharge configuration.

The code creates workqueues with `create_singlethread_workqueue()` but has no remove callback to destroy them on normal unbind after successful probe. Error paths destroy the first queue when the second creation fails.

## Dependencies and integration points

The driver depends on Linux OF parsing, regmap, IRQ, workqueue, mutex, input key codes, ASoC component registration, ALSA jack reporting, the MT6397 MFD parent, MT6359 register definitions from `mt6359.h`, and public types/macros from `mt6359-accdet.h`. It registers as platform driver `pmic-codec-accdet` and exposes exported `mt6359_accdet_enable_jack_detect()` for the main MT6359 codec or board integration to attach an `snd_soc_jack`.

The device-tree contract is the `accdet` child under the parent PMIC node with properties such as `mediatek,mic-vol`, `mediatek,plugout-debounce`, `mediatek,mic-mode`, `mediatek,pwm-deb-setting`, `mediatek,eint-level-pol`, `mediatek,eint-use-ap`, `mediatek,eint-detect-mode`, `mediatek,eint-num`, `mediatek,eint-trig-mode`, `mediatek,eint-use-ext-res`, `mediatek,eint-comp-vth`, `mediatek,key-mode`, and threshold arrays for three-key/four-key/tri-key modes.

## Risks and test signals

Risks include DTS array size/type assumptions, missing default threshold values when threshold properties are absent, incomplete support paths for AP GPIO EINT or bi-EINT capabilities, IRQ storms if clear/poll sequences fail, stale `cali_voltage` because this file classifies buttons from it but does not show an AUXADC update path, no successful-probe workqueue cleanup callback, and subtle races from queuing work while holding `res_lock` and then re-taking it in the worker. The interrupt handler returns `IRQ_NONE` on poll timeout after partially clearing hardware state, which can affect shared IRQ diagnostics.

Useful test signals are probe with all expected IRQs, correct parsed `caps` for EINT0 and EINT1 boards, plug-in and plug-out reports through `snd_soc_jack_report()`, headset versus headphone classification, button key events for all configured thresholds, no duplicate reports during debounce, EINT mode 1 through 4 behavior, interrupt clear poll success, repeated plug cycles without stuck ACCDET enable, and module unbind/load testing for workqueue lifetime issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.h

## Purpose

This header defines the public and private data contract for the MT6359 accessory detector. It provides jack/button masks, headset mode constants, state enums, device-tree configuration structures, private driver state, and the exported jack-detection enable API used when the ACCDET component is enabled.

## Important APIs, types, and functions

Constants include `ACCDET_DEVNAME`, headset modes `HEADSET_MODE_1`, `HEADSET_MODE_2`, `HEADSET_MODE_6`, `MT6359_ACCDET_NUM_BUTTONS`, `MT6359_ACCDET_JACK_MASK`, and `MT6359_ACCDET_BTN_MASK`. `enum eint_moisture_status` names EINT plug/moisture states such as `M_PLUG_IN`, `M_WATER_IN`, `M_HP_PLUG_IN`, `M_PLUG_OUT`, `M_NO_ACT`, and `M_UNKNOWN`. The anonymous state enum names ACCDET debounce states, EINT debounce states, auxadc debounce, and inverter debounce slots consumed by `accdet_set_debounce()`.

Configuration structures are `struct three_key_threshold`, `struct four_key_threshold`, `struct pwm_deb_settings`, and `struct dts_data`. `struct mt6359_accdet` is the main runtime object with ALSA jack/device/regmap pointers, parsed data, capability flags, IRQ ids, mutex, jack/button status fields, ACCDET calibration/status fields, and workqueue/work structs. The public function is `mt6359_accdet_enable_jack_detect()`, with an inline `-EOPNOTSUPP` stub when `CONFIG_SND_SOC_MT6359_ACCDET` is disabled.

## Control flow

There is no executable control flow in the header. It shapes C-file control flow by defining the state identifiers passed to debounce programming, the moisture/jack-detect status values interpreted by IRQ work, the threshold structures used by button classification, and the conditional API availability controlled by Kconfig.

## State and persistence behavior

The header declares the in-memory state layout used by `mt6359-accdet.c`. `struct dts_data` persists parsed board configuration for the lifetime of the platform device. `struct mt6359_accdet` persists current jack state, previous ACCDET state, button state, calibration voltage, jack-detect status, IRQ registrations, and deferred work objects. No storage is allocated here; allocation is done by the probe function.

## Dependencies and integration points

It includes Linux string/ctype headers and uses ALSA jack bit constants and ASoC component types through the C file's include context. The exported API is the integration point for codec or machine code that owns the `snd_soc_component` and creates the `snd_soc_jack`. The Kconfig guard lets callers compile even when ACCDET support is disabled, receiving `-EOPNOTSUPP` from the inline stub.

## Risks and test signals

Risks include the generic include guard `_ACCDET_H_` being collision-prone, hidden dependency on ALSA declarations because this header itself does not include `<sound/soc.h>` or `<sound/jack.h>`, structure layout coupling to `mt6359-accdet.c`, and threshold arrays whose first DTS element is skipped by the parser. Test signals are clean builds with `CONFIG_SND_SOC_MT6359_ACCDET=y/m/n`, callers correctly handling the disabled stub, all jack/button mask bits reaching ALSA jack reports, and DTS threshold data producing expected `three_key` or `four_key` fields.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.h -->
