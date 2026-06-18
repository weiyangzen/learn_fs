# Research Report: subset-b-006479

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.h

## Purpose

`wcd9335.h` is the local register and hardware-constant header for the Qualcomm WCD9335 ASoC codec driver. It does not implement executable logic; it defines the symbolic register addresses, bit masks, field values, interrupt indices, SLIMbus product IDs, and device limits consumed by the WCD9335 codec implementation and related helper tables.

The central addressing abstraction is `WCD9335_REG(pg, r)`, which encodes a page number and register offset into the 16-bit register namespace. `WCD9335_REG_OFFSET()` and `WCD9335_PAGE_OFFSET()` decode that namespace. The opening comment documents a key hardware integration detail: SLIMbus mode maps the register window from base `0x800`, while I2S/I2C mode uses base `0x0`; the header therefore keeps logical page/register values separate from transport-specific windowing.

## Important APIs, Types, And Constants

This header exports preprocessor constants only. Important groups are:

- Register-address helpers: `WCD9335_REG(pg, r)`, `WCD9335_REG_OFFSET(r)`, and `WCD9335_PAGE_OFFSET(r)`.
- Page 0 clock, reset, efuse, chip-ID, and interrupt registers: `WCD9335_CODEC_RPM_CLK_GATE`, `WCD9335_CODEC_RPM_CLK_MCLK_CFG`, `WCD9335_CODEC_RPM_RST_CTL`, `WCD9335_CHIP_TIER_CTRL_*`, `WCD9335_INTR_*`.
- Page 1 FLL programming blocks for CPE, I2S, and SLIMbus/SB FLLs. These define user controls, L values, DSM fractions, config, test, frequency, SSC, mode, and status registers.
- Page 2 CPE/DMIC and MAD-related registers such as `WCD9335_CPE_SS_DMIC0_CTL`, `WCD9335_CPE_SS_DMIC_CFG`, and `WCD9335_SOC_MAD_AUDIO_CTL_2`.
- Page 6 analog, bias, microphone, MBHC, SIDO, flyback, headphone, ear, and line-out registers. This is the densest section and includes masks and enumerated values for analog bias, MCLK routing, RCO, buck, RX bias, MBHC mechanical/electrical detection, micbias, SIDO, HPH PA, headphone gain, DAC LDO, and line-out compander controls.
- Page 10 TX/decimator registers, including repeated address macros like `WCD9335_CDC_TX_PATH_CTL(dec)` and selection bits for AMIC/DMIC input.
- Page 11 compander and RX/interpolator path registers, including repeated register macros such as `WCD9335_CDC_COMPANDER1_CTL(c)`, `WCD9335_CDC_RX_PATH_CTL(rx)`, `WCD9335_CDC_RX_PATH_MIX_CTL(rx)`, and `WCD9335_CDC_RX1_RX_PATH_CFG(c)`.
- Page 12 CLSH/boost registers for class-H and boost paths.
- Page 13 RX/TX input muxing, CDC interface router, and top-level clock/reset controls.
- SLIMbus slave register helpers for port interrupt status/clear/source, RX/TX port configuration, and multi-channel mapping.
- IRQ IDs: `WCD9335_IRQ_SLIMBUS`, MBHC insert/remove/button IRQs, and related interrupt slots.
- Hardware IDs and limits: `SLIM_MANF_ID_QCOM`, `SLIM_PROD_CODE_WCD9335`, `WCD9335_VERSION_2_0`, `WCD9335_MAX_SUPPLY`, `WCD9335_MAX_REGISTER`, and `WCD9335_SEL_REGISTER`.

There are no C types, function declarations, inline helpers, global objects, or module metadata in this header.

## Control Flow

There is no runtime control flow in this file. Its control-flow impact is indirect: register constants drive the implementation order in the codec driver. For example, the WCD9335 implementation can use the page 0 efuse/chip-ID constants to detect silicon revision, page 6 constants to sequence analog bias and MBHC detection, page 10/11 constants to configure TX and RX paths, and SLIMbus constants to configure interface ports and clear port interrupts.

The repeated address macros are important to control-flow correctness because loops in the corresponding C driver can calculate per-channel or per-path registers rather than hand-coding each address. Incorrect stride constants would misdirect writes across adjacent hardware blocks.

## State And Persistence Behavior

The header itself stores no state. It defines hardware state locations:

- Clock and reset state: RPM clock gate, MCLK config, MCLK enable/source, FS counter, and reset control registers.
- Efuse and version state: chip ID bytes, efuse control/status, and efuse value registers.
- Interrupt state: mask/status/clear/level registers for two interrupt pins.
- Analog power state: bias, precharge, buck, RX supplies, micbias, MBHC, flyback, headphone PA, and DAC LDO registers.
- Audio-routing state: TX decimator path registers, RX interpolator and mixer registers, compander registers, and page 13 mux/router registers.
- SLIMbus interface state: per-port enable, watermark, multi-channel mapping, interrupt source/status/clear registers.

Persistence is hardware-backed and volatile across reset/power cycles. The symbols here are the contract used by driver code to make state transitions explicit and repeatable.

## Dependencies And Integration Points

The header depends on kernel bit macros such as `BIT()` and `GENMASK()` being visible before or through its consumers. It is integrated with:

- The WCD9335 codec implementation in the same `sound/soc/codecs` directory.
- ASoC machine drivers such as Qualcomm APQ8096 paths that set codec MCLK and route DAI links.
- SLIMbus registration through the Qualcomm manufacturer/product constants.
- Regmap range/window configuration, where `WCD9335_SEL_REGISTER` and page-encoded register addresses must agree with the transport window.
- Shared Qualcomm codec helpers for MBHC and class-H behavior, which depend on MBHC, HPH, and CLSH register fields.

Build integration is through the codec Kconfig and Makefile entries for `SND_SOC_WCD9335` and `snd-soc-wcd9335.o`.

## Risks And Edge Cases

- The header uses raw numeric register values and bit masks. A single bad offset or stride can silently redirect driver writes to the wrong analog or digital block.
- Some constants encode the same bit value for different named MCLK frequencies (`WCD9335_CODEC_RPM_CLK_MCLK_CFG_9P6MHZ` and `_12P288MHZ` are both `BIT(0)` in this header). Consumers must verify whether additional fields or external clock programming distinguish those modes.
- The transport base distinction in the opening comment means regmap range configuration must remain aligned with the active transport. Mixing logical and windowed addresses can break register access.
- Repeated macros such as `WCD9335_CDC_TX_PATH_CTL(dec)` and `WCD9335_CDC_RX_PATH_CTL(rx)` assume fixed hardware strides. Any new silicon variant with changed layout would need separate constants.
- Page 6 analog/MBHC constants include many one-bit enable values and zero-valued disable values. Incorrect mask/value pairing can leave bias, pullups, or headphone PA safety bits enabled.
- SLIMbus port macros expose port arithmetic over RX/TX ranges. Callers must validate port numbers before using these macros.

## Test Signals

Useful validation signals are mostly compile-time and hardware-integration oriented:

- `make` or `COMPILE_TEST` coverage for `SND_SOC_WCD9335` should catch missing symbols, duplicate definitions, and consumers that rely on these constants.
- Boot probing on a WCD9335 platform should report a supported version and successfully configure regmap windows and SLIMbus IDs.
- Runtime audio playback/capture through WCD9335 should exercise page 10/11 TX/RX path constants.
- Headset insertion, button, and impedance tests should exercise MBHC register constants and IRQ IDs.
- SLIMbus stress tests should show correct port interrupt status/clear behavior without persistent overflow/underflow logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd934x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd934x.c

## Purpose

`wcd934x.c` is the ASoC component driver for Qualcomm WCD9340/WCD9341 audio codecs. It binds as the `wcd934x-codec` child created by the WCD934x MFD SLIMbus driver, registers playback and capture DAIs, exposes mixer/volume/filter/compander controls, builds the DAPM audio graph, manages MCLK and SoundWire clock gating, programs SLIMbus interface ports, and integrates headset detection through the shared `wcd_mbhc` framework.

The driver supports four playback AIF DAIs and three capture AIF DAIs over SLIMbus. It routes audio between SLIMbus ports, RX interpolators, headphone/ear/line/speaker outputs, ADC/DMIC inputs, TX decimators, IIR/sidetone blocks, and capture ports. It also registers an output clock named from device tree, backed by the external clock divided by two for SoundWire/MCLK use.

## Important APIs, Types, And Functions

Key data structures:

- `struct wcd934x_slim_ch`: stores a logical SLIMbus channel number, hardware port number, bit shift, and list node used to attach a port to a selected DAI.
- `struct wcd_slim_codec_dai_data`: per-DAI runtime state containing the selected channel list, `slim_stream_config`, and `slim_stream_runtime`.
- `struct wcd934x_codec`: private driver state. It holds device/regmap pointers, primary and interface SLIMbus devices, class-H controller, `wcd_common`, component pointer, RX/TX channel tables, per-DAI state, current MCLK rate, chip version, headphone mode, RX/TX mux state arrays, SIDO source, DMIC clock reference counters, selected DMIC sample rate, compander enable state, shared sysclk reference count and mutex, MBHC state/config/interrupt IDs, micbias mutex, and micbias/pullup reference counters.
- `struct wcd934x_mbhc_zdet_param`: per-range impedance-detection ramp parameters.
- `struct wcd_iir_filter_ctl`: extended ALSA bytes control metadata for IIR band coefficients.

Important runtime functions:

- Clock and silicon setup: `wcd934x_enable_ana_bias_and_sysclk()`, `wcd934x_disable_ana_bias_and_syclk()`, `__wcd934x_cdc_mclk_enable()`, `wcd934x_codec_enable_mclk()`, `wcd934x_enable_efuse_sensing()`, `wcd934x_get_version()`, `wcd934x_swrm_clock()`, and `wcd934x_register_mclk_output()`.
- DAI and SLIMbus runtime: `wcd934x_hw_params()`, `wcd934x_hw_free()`, `wcd934x_trigger()`, `wcd934x_set_channel_map()`, `wcd934x_get_channel_map()`, `wcd934x_slim_set_hw_params()`, `wcd934x_codec_enable_int_port()`, and `wcd934x_slim_irq_handler()`.
- Rate programming: `wcd934x_set_interpolator_rate()`, `wcd934x_set_prim_interpolator_rate()`, `wcd934x_set_mix_interpolator_rate()`, and `wcd934x_set_decimator_rate()`.
- MBHC and micbias: `wcd934x_micbias_control()`, `wcd934x_mbhc_request_micbias()`, `wcd934x_mbhc_micb_adjust_voltage()`, `wcd934x_mbhc_get_result_params()`, `wcd934x_mbhc_zdet_ramp()`, `wcd934x_wcd_mbhc_calc_impedance()`, `wcd934x_mbhc_init()`, `wcd934x_mbhc_deinit()`, and `wcd934x_codec_set_jack()`.
- ALSA controls: IIR coefficient get/put/info helpers, compander get/set, headphone mode get/put, SLIM RX mux get/put, TX mixer get/put, decimator enum put, and DEM input mux put.
- DAPM events: `wcd934x_codec_enable_interp_clk()`, `wcd934x_codec_enable_mix_path()`, `wcd934x_codec_enable_main_path()`, `wcd934x_codec_ear_dac_event()`, `wcd934x_codec_hphl_dac_event()`, `wcd934x_codec_hphr_dac_event()`, `wcd934x_codec_lineout_dac_event()`, `wcd934x_codec_enable_hphl_pa()`, `wcd934x_codec_enable_hphr_pa()`, `wcd934x_codec_enable_dmic()`, `wcd934x_codec_enable_dec()`, `wcd934x_codec_enable_adc()`, and `wcd934x_codec_enable_micbias()`.
- Driver lifecycle: `wcd934x_codec_parse_data()`, `wcd934x_codec_probe()`, `wcd934x_comp_probe()`, `wcd934x_comp_remove()`, and the `platform_driver`/`snd_soc_component_driver` registration objects.

Static tables define supported rates/formats, RX/TX channel defaults, regmap range windows, TLV scales, text labels, `soc_enum` controls, MBHC field mappings, DAI descriptors, mixer controls, DAPM widgets, and DAPM routes.

## Control Flow

Probe begins in `wcd934x_codec_probe()`. The function allocates private state, copies regmap/extclk/SLIMbus handles from the parent MFD data, initializes mutexes and common micbias metadata, parses the `slim-ifc-dev` phandle, builds an interface regmap for the secondary SLIMbus device, sets default MBHC configuration, installs a cleanup action for the interface device reference, sets default MCLK config to 9.6 MHz, copies static RX/TX channel templates, requests the SLIMbus IRQ, registers the optional MCLK output provider, stores private data, and finally registers the ASoC component and DAI array.

ASoC component probe (`wcd934x_comp_probe()`) initializes the component regmap, allocates the class-H controller, sets default headphone mode to `CLS_H_LOHIFI`, performs hardware init, enables efuse sensing, reads version information, initializes per-DAI SLIMbus channel lists, initializes micbias/DMIC settings from device tree, and starts MBHC support. Remove tears down MBHC and the class-H controller.

Playback `hw_params` validates rate and width, converts the sample rate into a codec rate code, then walks the selected SLIM RX channel list to update any primary or mix interpolator fed by those ports. Capture `hw_params` converts capture rates into TX decimator rate codes, resolves which decimator is connected to each selected SLIM TX port through the CDC IF router registers, and writes decimator PCM rates. Both directions fill `slim_stream_config` and call `wcd934x_slim_set_hw_params()` to build channel arrays, port masks, multi-channel maps, watermark/enable values, and a SLIM stream runtime.

The `trigger` path prepares/enables or disables/unprepares the SLIM stream runtime. DAPM AIF widgets enable SLIM port interrupts after power-up. The IRQ handler reads four RX/TX status bytes, maps bits 0-15 to RX and 16-31 to TX, reports overflow/underflow/closed-port events, masks overflowing/underflowing ports, and clears interrupt bits.

ALSA control changes update driver-side routing state before DAPM power recalculation. `slim_rx_mux_put()` adds/removes an RX channel list node for a playback DAI, while `slim_tx_mixer_put()` does the same for capture TX ports. These lists are then consumed by `hw_params` and channel-map queries.

DAPM events sequence hardware power. MCLK supply events use `__wcd934x_cdc_mclk_enable()`, which enables the external clock, analog bias, precharge, MCLK source, FS counter, CDC MCLK, RPM clock gate, and SIDO source. RX interpolator events enable clocks, HD2, headphone LUT bypass, and compander state before power-up, and reverse/reset them on power-down. Headphone DAC and PA events enforce class-H mode requirements, ripple frequency settings, mute/unmute, OCP detection, GM3 boost, autochop timing, MBHC notifications, and hardware-mandated sleeps. TX decimator and DMIC events derive ADC/DMIC source selection and set clock dividers, HPF gate changes, gain latching, and AMIC power levels.

MBHC initialization maps parent regmap IRQs into the shared MBHC layer, registers callback operations, and adds impedance and headphone-type controls. Jack setup starts or stops `wcd_mbhc`. Impedance calculation saves relevant MBHC registers, disables conflicting detection state, runs one or more left/right ZDET ramps depending on measured range, applies qfuse calibration, performs mono/stereo detection, restores all saved registers, and restores FSM/L-det state.

## State And Persistence Behavior

Persistent driver state is held in `struct wcd934x_codec` for the lifetime of the platform device:

- `rx_chs[]`, `tx_chs[]`, `rx_port_value[]`, `tx_port_value[]`, and per-DAI `slim_ch_list` persist user routing decisions between control writes and PCM `hw_params`.
- `dai[].sconfig` and `dai[].sruntime` persist PCM stream configuration between `hw_params`, `trigger`, and `hw_free`.
- `rate` tracks MCLK/sysclk rate and controls DMIC clock divisor defaults and MCLK config writes.
- `hph_mode` persists the selected headphone class-H/class-AB mode.
- `comp_enabled[]` persists compander ALSA switch state and controls later DAPM compander sequencing.
- `sysclk_users` reference-counts analog bias and CDC MCLK users under `sysclk_mutex`.
- `dmic_0_1_clk_cnt`, `dmic_2_3_clk_cnt`, and `dmic_4_5_clk_cnt` reference-count paired DMIC clocks.
- `micb_ref[]` and `pullup_ref[]` reference-count micbias and pullup requests under `micb_lock`.
- `mbhc_started`, `mbhc`, `mbhc_cfg`, and `intr_ids` persist headset detection state.

Hardware state is stored in regmap-backed registers and is generally volatile across chip reset. The driver reprograms important state on probe, sysclk changes, DAPM events, ALSA control writes, and stream startup. IIR coefficient controls directly persist filter bytes in codec registers until overwritten or reset.

## Dependencies And Integration Points

This driver depends on:

- Linux ASoC core: components, DAIs, DAPM widgets/routes, controls, TLV scales, PCM params, and jack callbacks.
- SLIMbus core: `slim_device`, `slim_stream_config`, stream allocation/prepare/enable/disable/unprepare, and logical interface device lookup.
- Regmap and regmap IRQs from the parent WCD934x MFD driver.
- Parent MFD data (`struct wcd934x_ddata`) for `regmap`, `extclk`, `irq_data`, and the primary SLIMbus device.
- Device tree properties: `slim-ifc-dev`, parent `clock-frequency`, parent `clock-output-names`, parent `qcom,dmic-sample-rate`, micbias data, and MBHC configuration.
- Shared Qualcomm codec helpers: `wcd-clsh-v2`, `wcd-common`, and `wcd-mbhc-v2`.
- DT binding DAI IDs from `dt-bindings/sound/qcom,wcd934x.h`.

Integration in this tree appears through `CONFIG_SND_SOC_WCD934X`, `snd-soc-wcd934x.o`, the WCD934x MFD driver that creates the `wcd934x-codec` child, the WCD934x GPIO and SoundWire child devices, and Qualcomm machine drivers such as `sdm845.c`, which set the codec sysclk to the default 9.6 MHz rate.

## Risks And Edge Cases

- `wcd934x_slim_set_hw_params()` allocates `cfg->chs` and assigns `dai_data->sruntime = slim_stream_allocate(...)` but does not check the returned runtime before later trigger use. If allocation fails or returns an error-like value, trigger paths can dereference invalid state.
- `wcd934x_hw_free()` frees `sconfig.chs` but does not set it to `NULL`; repeated cleanup paths would be easier to audit if the pointer were cleared.
- The sysclk reference count is manually maintained. Disable pre-decrements `sysclk_users` without an explicit underflow guard; unbalanced DAPM or MBHC clock requests can leave clocks enabled or drive the count negative.
- Register writes frequently ignore regmap return values. Hardware or bus failures during power sequencing, efuse sensing, SLIM port programming, MBHC measurement, or DAPM events may be logged incompletely or not propagated.
- `wcd934x_codec_set_jack()` starts MBHC only when `jack && !mbhc_started`; any later call while started falls into the stop branch, even if `jack` is non-NULL. That depends on ASoC calling conventions and is a regression risk if the callback is reinvoked with the same jack.
- `wcd934x_codec_enable_hphl_pa()` sends `WCD_EVENT_POST_HPHL_PA_OFF` during `SND_SOC_DAPM_PRE_PMD`, while the right channel uses `WCD_EVENT_PRE_HPHR_PA_OFF` in the analogous phase. The asymmetry may be intentional, but it looks like a likely event-order bug.
- DMIC clock counters are decremented on POST_PMD without an explicit lower-bound check. Unexpected DAPM event imbalance can underflow and keep clocks misprogrammed.
- Routing list updates are protected by DAPM/control serialization only; there is no local mutex around `slim_ch_list` mutation. Concurrent control and PCM setup assumptions depend on ASoC locking.
- Several routines parse widget names (`DMIC0`, `ADC MUX0`) to discover hardware indices. Renaming widgets without updating parser assumptions breaks runtime behavior.
- MBHC impedance measurement temporarily disables detection bits, manipulates headphone grounds, changes thresholds, and then restores saved registers. Any early return or missed restore in future edits could leave detection or audio safety state altered.
- The IRQ handler disables port interrupt bits on overflow/underflow but no local recovery path re-enables them except later port-enable flows. Persistent errors can therefore suppress future port notifications until a route or stream cycle reprograms the port.

## Test Signals

Compile-time coverage should include `CONFIG_SND_SOC_WCD934X`, `CONFIG_MFD_WCD934X`, and `COMPILE_TEST` builds. Useful runtime and integration signals are:

- Probe logs from the MFD and codec showing chip ID/version detection, successful interface SLIMbus phandle lookup, IRQ request, and component registration.
- Machine-driver sysclk calls at 9.6 MHz and, where supported, 12.288 MHz should update parent extclk rate and MCLK config registers.
- Playback over AIF1-AIF4 at 8/16/32/48/96/192 kHz plus fractional 44.1/88.2/176.4 kHz should exercise interpolator rate programming and class-H DEM input constraints.
- Capture over AIF1-AIF3 at 8/16/32/48/96/192 kHz should exercise TX router to decimator rate resolution.
- SLIMbus stress should show no repeated overflow/underflow/port-closed ratelimited errors after normal route setup.
- Mixer tests should verify that SLIM RX muxes and SLIM TX mixers reject busy ports and that `get_channel_map()` reflects selected channels.
- DAPM route tests should cover EAR, HPHL/HPHR, LINEOUT1/2, SPK1/2, AMIC1-5, DMIC0-5, IIR0/1, and sidetone paths.
- MBHC tests should cover jack insertion/removal, button thresholds, micbias2 ramp/voltage changes, OCP events, impedance controls, and mono/stereo classification.
- Filter tests should write and read back each IIR band bytes control and verify reserved high bits are masked as expected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd934x.c -->
