<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.c

## Purpose

`wcd938x.c` is the main ASoC platform codec driver for Qualcomm WCD9380/WCD9385 audio codecs. It binds the aggregate codec device to separate RX and TX SoundWire slave devices, exposes playback and capture DAIs, builds the DAPM graph for analog microphones, DMICs, headphone/earpiece/aux outputs, controls SoundWire channel enablement, manages codec power sequencing, and integrates the common WCD MBHC headset-detection engine.

The file is not a filesystem component despite the repository path; it is Linux kernel audio codec infrastructure. Its main responsibilities are register programming through the TX SoundWire regmap, ASoC control/widget registration, jack detection, impedance detection, runtime PM dependencies between aggregate and SoundWire children, and hardware-specific sequencing delays.

## Important APIs, types, and functions

The central private state is `struct wcd938x_priv`. It stores RX/TX SoundWire child pointers, `sdw_priv[AIF1_PB]` and `sdw_priv[AIF1_CAP]`, the shared TX `regmap`, MBHC configuration and interrupt IDs, class-H control state, micbias reference counters, cached headphone/ADC modes, watchdog IRQ numbers, GPIO or mux state for US/EU headset wiring, and feature flags such as `comp1_enable`, `comp2_enable`, `ldoh`, and `mux_setup_done`.

Probe and component lifecycle are handled by `wcd938x_probe()`, `wcd938x_remove()`, `wcd938x_bind()`, `wcd938x_unbind()`, `wcd938x_soc_codec_probe()`, and `wcd938x_soc_codec_remove()`. Platform probe allocates `wcd938x_priv`, parses reset GPIO, optional US/EU mux or GPIO, regulators, micbias and MBHC device-tree data, resets the codec, and registers a component master. Bind waits for RX/TX SoundWire child components, resolves their `struct device` instances from OF phandles, links device PM ordering, takes the TX child regmap as the codec CSR map, initializes IRQ plumbing, writes micbias defaults, and registers the ASoC component plus two DAIs.

DAI and SoundWire entry points are `wcd938x_codec_hw_params()`, `wcd938x_codec_free()`, `wcd938x_codec_set_sdw_stream()`, and `wcd938x_sdw_dai_ops`. These are thin wrappers that dispatch to `wcd938x_sdw_hw_params()`, `wcd938x_sdw_free()`, and `wcd938x_sdw_set_sdw_stream()` through the per-DAI `wcd938x_sdw_priv` objects defined in `wcd938x.h` and implemented by the companion SoundWire driver selected by `CONFIG_SND_SOC_WCD938X_SDW`.

Clock and port helpers include `wcd938x_get_clk_rate()`, `wcd938x_set_swr_clk_rate()`, `wcd938x_sdw_connect_port()`, `wcd938x_connect_port()`, `wcd938x_tx_swr_ctrl()`, `wcd938x_get_swr_port()`, and `wcd938x_set_swr_port()`. These map ADC operating modes to SoundWire TX clock rates, update both SoundWire register banks around DAPM transitions, and maintain channel masks in `sdw_priv->port_config`.

DAPM event functions implement most hardware sequencing: `wcd938x_codec_enable_rxclk()`, `wcd938x_codec_hphl_dac_event()`, `wcd938x_codec_hphr_dac_event()`, `wcd938x_codec_ear_dac_event()`, `wcd938x_codec_aux_dac_event()`, `wcd938x_codec_enable_hphr_pa()`, `wcd938x_codec_enable_hphl_pa()`, `wcd938x_codec_enable_aux_pa()`, `wcd938x_codec_enable_ear_pa()`, `wcd938x_codec_enable_dmic()`, `wcd938x_codec_enable_adc()`, and `wcd938x_adc_enable_req()`. They enable and disable analog/digital clocks, DAC/RDAC gain paths, class-H power states, flyback current detection, PDM watchdogs, companders, earpiece path routing, DMIC clocks, and ADC path modes.

MBHC integration is built from `wcd_mbhc_fields`, `wcd938x_irqs`, `wcd938x_regmap_irq_chip`, `mbhc_cb`, `wcd938x_mbhc_init()`, and `wcd938x_mbhc_deinit()`. Callback implementations cover MBHC clock and bias control, button threshold programming, micbias requests and ramping, threshold-mic voltage adjustment, impedance measurement, ground detection, headphone pulldowns, moisture detection, and polling control. `wcd938x_codec_set_jack()` starts or stops MBHC against an ALSA jack.

User-visible controls are declared in `wcd938x_snd_controls`, `wcd9380_snd_controls`, and `wcd9385_snd_controls`. They expose SoundWire channel switches, compander switches, line and ADC volumes, earpiece PA gain, LDOH enable, headphone class-H mode, and TX ADC mode enums. Variant-specific controls are installed after reading `WCD938X_DIGITAL_EFUSE_REG_0`.

## Control flow

The platform path starts in `wcd938x_probe()`. After device-tree parsing and reset, the component framework calls `wcd938x_bind()` when both SoundWire slaves are available. Bind stores child state, creates runtime PM dependency links so the TX CSR interface remains available when RX is active, initializes a synthetic IRQ domain plus regmap IRQ chip, points both RX and TX SoundWire children at the same slave IRQ domain, programs micbias voltages, and registers the ASoC component.

ASoC component probe waits up to two seconds for the TX SoundWire slave `initialization_complete`, initializes the component regmap, resumes runtime PM, reads the WCD9380/WCD9385 variant ID, allocates class-H control, runs the hardware IO initialization sequence in `wcd938x_io_init()`, programs interrupt level registers for edge-triggered handling, and releases runtime PM. It then maps PDM watchdog virtual IRQs, requests threaded IRQs with a no-op handler, disables them until DAPM enables relevant paths, adds variant-specific controls, and initializes MBHC.

Playback DAPM paths are built from RX widgets and routes. `RXCLK` powers analog RX clocks and bias. HPHL/HPHR DAC events enable RX digital paths and optional compander bits; PA events select class-H mode, enable LDOH if requested, wait the hardware-required 7 ms or 20 ms depending on compander state, enable watchdog interrupts, and notify MBHC before and after PA off. AUX and EAR paths share flyback current detector reference counting through `flyback_cur_det_disable`; EAR can route through either AUX/RX3 or HPHL/RX1 depending on `WCD938X_DIGITAL_CDC_EAR_PATH_CTL`.

Capture DAPM paths are built around ADC and DMIC mixers. ADC power-up enables analog TX clocks and marks a bit in `status_mask`. `wcd938x_adc_enable_req()` programs the chosen ADC mode in TX analog mode registers, toggles channel HPF init bits, enables the matching TX digital clock bit, and clears the mode on power-down. `wcd938x_tx_swr_ctrl()` observes active ADC status bits, selects the highest-priority active low-power mode via `tx_mode_bit`, and programs SoundWire TX clock rate into both current and alternate banks. DMIC power-up chooses the relevant clock-rate and clock-enable registers based on widget shift, selects DMIC input, sets 2.4 MHz DMIC rate, and enables digital clock scaling.

MBHC control starts from `wcd938x_mbhc_init()`, which maps regmap IRQs to the common `wcd_mbhc_intr` structure and passes `mbhc_cb` plus register field descriptors to `wcd_mbhc_init()`. Impedance detection in `wcd938x_wcd_mbhc_calc_impedance()` snapshots MBHC and ZDET registers, disables FSM and surge protection where needed, performs left and right ZDET ramps through `wcd938x_mbhc_zdet_ramp()` and `wcd938x_mbhc_get_result_params()`, applies efuse qfuse calibration, classifies mono versus stereo by measuring a left-channel value under right-channel pulldown, restores saved registers, and re-enables detection state.

Removal unwinds the same layers: component remove deinitializes MBHC, frees watchdog IRQs, and frees class-H state; unbind unregisters the ASoC component, removes device links, drops RX/TX child references, and unbinds child components; platform remove removes the component master, disables runtime PM, and deselects any mux control.

## State and persistence behavior

Runtime state is volatile kernel driver state, not persistent storage. Register values are persisted in hardware and the SoundWire child regmap cache while the device is runtime suspended. `wcd938x.c` itself caches policy and reference state in `wcd938x_priv`: micbias enable/pullup reference counts, active ADC bits in `status_mask`, current `hph_mode`, per-ADC `tx_mode`, compander and LDOH controls, flyback current-detector nesting, cached earpiece route, SoundWire port-enable booleans inside child `wcd938x_sdw_priv`, and US/EU mux state.

Micbias control is reference counted separately for true micbias enable and pull-up mode. `wcd938x_micbias_control()` keeps pull-up active when disable requests leave only pull-up users, disables the register only when both counters reach zero, and sends MBHC notifications around MIC_BIAS_2 transitions. Voltage changes are serialized by `micb_lock` and temporarily switch an enabled micbias to pull-up before writing a new VOUT code.

IRQ state is split between a local synthetic IRQ domain, regmap IRQ data, and requested PDM watchdog IRQs. Watchdog interrupts are requested during component probe but explicitly disabled until path-specific DAPM PMU events enable them; PMD events disable them again. MBHC IRQs are delivered through the regmap IRQ chip and common MBHC code.

Runtime PM ordering is explicit. Bind adds device links from RX to TX and from the aggregate codec to both SoundWire children. This matters because the TX SoundWire child owns the main CSR regmap used for both RX and TX codec register access.

## Dependencies and integration points

The driver depends on ALSA SoC component, DAI, DAPM, control and jack APIs; Linux SoundWire device lookup and stream APIs; regmap and regmap IRQ; component framework aggregate binding; GPIO descriptors; mux controls; regulator bulk enable; runtime PM; device-tree phandles and MBHC/micbias parsing helpers.

Local codec dependencies include `wcd938x.h` for register and SoundWire contracts, `wcd-common.h` for SoundWire channel info, DT parsing, interrupt callback helpers and micbias helpers, `wcd-mbhc-v2.h` for headset detection, and `wcd-clsh-v2.h` for class-H control. The SoundWire operations are delegated to the `wcd938x_sdw_*` functions declared in the header, so the main platform driver only bridges ASoC DAI callbacks to child SoundWire state.

External integration points are OF compatibles `qcom,wcd9380-codec` and `qcom,wcd9385-codec`, phandles `qcom,rx-device` and `qcom,tx-device`, optional `mux-controls` or `us-euro` GPIO, supplies `vdd-rxtx`, `vdd-io`, `vdd-buck`, and `vdd-mic-bias`, ALSA mixer controls, DAPM graph routes, and ALSA jack registration through `.set_jack`.

## Risks

The driver is highly sequencing-sensitive. Many power events rely on fixed `usleep_range()` delays documented as hardware requirements; shortening or reordering them can cause pops, missing audio, or watchdog interrupts. `flyback_cur_det_disable` is a plain nesting counter shared by AUX and EAR paths; unbalanced DAPM events could leave flyback current detection disabled or re-enabled too early.

SoundWire port enablement is split between ALSA controls and per-stream `hw_params()`. Wrong `port_enable` state or channel-to-port mapping can produce silent streams even when DAPM powers the analog path. TX clock-rate selection depends on `status_mask` bits and `tx_mode[]`; stale bits would choose an unexpected low-power or high-speed clock.

MBHC impedance detection temporarily disables FSM, L_DET, pulldowns, and surge protection while manipulating shared analog registers. Any early return or future edit that skips restoration could leave headset detection or surge protection in the wrong state. The ZDET loop polls up to 900 iterations without sleeping in the main completion loop, so hardware that never updates result bits can burn CPU briefly and return floating or error results.

Probe and bind have several partial-failure paths. Device links created before later failures must be removed in the correct order. `wcd938x_irq_init()` creates an IRQ domain with `irq_domain_create_linear()` that is not explicitly removed in unbind in this file, so lifetime depends on broader devm/regmap IRQ cleanup and process teardown assumptions.

## Test signals

Useful test signals include successful aggregate bind after both RX and TX SoundWire slaves enumerate, no `soundwire device init timeout`, valid variant-specific controls for WCD9380 versus WCD9385, functional playback on HPHL/HPHR/EAR/AUX paths, functional capture on ADC1-4 and DMIC1-8, expected SoundWire port masks during mixer control changes, and correct runtime suspend/resume with the TX CSR regmap available before RX use.

MBHC-specific tests should verify jack insertion/removal, button thresholds, US/EU ground-mic swap through mux or GPIO, MIC_BIAS_2 notifications, moisture detection behavior for NO-jack versus NC configurations, left/right impedance values, and mono/stereo classification. Power-path tests should monitor PDM watchdog IRQ enable/disable around DAPM transitions, absence of underruns or pops with companders on/off, and restoration of class-H/flyback/surge-protection bits after path shutdown.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.c -->
