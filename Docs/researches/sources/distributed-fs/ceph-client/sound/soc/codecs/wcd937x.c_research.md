# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.c

## Purpose
`wcd937x.c` is the aggregate ASoC platform codec driver for Qualcomm WCD9370/WCD9375. It binds the RX and TX SoundWire slave components, obtains the TX-side CSR regmap, powers supplies and reset GPIOs, registers DAI and component drivers, defines ALSA controls, builds DAPM widgets/routes, initializes MBHC headset detection, and sequences analog/digital power for headphone, earpiece, AUX, ADC, DMIC, and micbias paths.

## Important APIs, Types, and Functions
- `struct wcd937x_priv` is the central state holder: SoundWire devices, per-DAI `wcd937x_sdw_priv`, regmap, MBHC config/state, Class-H controller, IRQ data, GPIOs, micbias refcounts, compander flags, headphone mode, and clock counters.
- `wcd937x_regmap_irq_chip`, `wcd937x_irqs`, `wcd937x_irq_init()`, and `wcd937x_handle_post_irq()` map the codec's three interrupt status/mask/clear registers into Linux IRQs used by MBHC and PDM watchdog handlers.
- DAPM event handlers such as `wcd937x_codec_hphl_dac_event()`, `wcd937x_codec_enable_hphl_pa()`, `wcd937x_codec_enable_aux_pa()`, `wcd937x_codec_enable_adc()`, `wcd937x_enable_req()`, and micbias helpers perform register sequencing, delays, Class-H state changes, and watchdog IRQ enable/disable.
- `wcd937x_micbias_control()` serializes micbias and pull-up refcounting with `micb_lock`, updates micbias mode bits, and notifies MBHC for MIC_BIAS_2 lifecycle events.
- MBHC callbacks (`mbhc_cb`) implement clock/bias control, button threshold programming, micbias voltage adjustment, impedance measurement, ground detection, pull-down control, and moisture detection for the shared `wcd-mbhc-v2` engine.
- `wcd937x_connect_port()`, `wcd937x_get_swr_port()`, `wcd937x_set_swr_port()`, and compander controls mutate SoundWire port/channel masks consumed by `wcd937x_sdw_hw_params()`.
- `wcd937x_bind()`/`wcd937x_unbind()` implement the component master, link platform/RX/TX device PM dependencies, initialize IRQs, and register/unregister the ASoC component and DAIs.

## Control Flow
Platform probe allocates `wcd937x_priv`, initializes micbias and MBHC defaults, gets reset and optional US/EU swap GPIOs, enables four regulators, parses micbias/MBHC device-tree data, adds RX/TX component matches, pulses reset, registers as component master, and enables autosuspended runtime PM. Component bind waits briefly, binds both SoundWire child components, finds the RX/TX SoundWire devices by phandle, stores their private data in playback/capture DAI slots, creates runtime PM device links, takes the TX regmap, initializes the IRQ domain/regmap-irq chip, writes micbias default voltages, and registers the codec component with two SoundWire DAIs.

Component probe waits for TX SoundWire initialization, attaches the regmap to ASoC, resumes the device, validates the chip ID as WCD9370 or WCD9375, allocates Class-H control, runs `wcd937x_io_init()` efuse-dependent analog setup, programs interrupt levels as edge-triggered, requests and disables watchdog IRQs, conditionally adds WCD9375-only DAPM widgets/routes, then initializes MBHC. Runtime audio paths flow through ASoC DAPM: widgets call event handlers before and after power transitions to enable clocks, route DAC/ADC/DMIC data, arm/disarm PDM watchdogs, delay around PA and compander transitions, and notify MBHC before/after headphone PA shutdown.

DAI operations are thin wrappers over the SoundWire private state. `set_stream` stores `sruntime`; `hw_params` calls `wcd937x_sdw_hw_params()`; `hw_free` removes the slave from the SoundWire stream; `get_channel_map` returns the per-master channel masks built by control changes.

## State and Persistence Behavior
The driver has several state lanes: hardware register cache in the TX SoundWire regmap, power sequencing state in DAPM, software controls in `hph_mode`/`comp1_enable`/`comp2_enable`, SoundWire port enables and master channel maps in the child `wcd937x_sdw_priv`, IRQ mappings in `irq_chip` and `virq`, and reference counts in `micb_ref`, `pullup_ref`, `rx_clk_cnt`, and `ana_clk_count`. The regmap cache is owned by the TX SoundWire driver and survives runtime suspend through cache-only mode. MBHC persists headset type, impedance, jack state, and moisture configuration through `wcd_mbhc`.

## Dependencies and Integration Points
The file integrates ASoC component/DAI/DAPM APIs, SoundWire stream callbacks, Linux component framework, regmap-irq, runtime PM, GPIO, regulator bulk enable, device tree helpers, and Qualcomm codec libraries `wcd-common`, `wcd-mbhc-v2`, and `wcd-clsh-v2`. It depends on `wcd937x-sdw.c` for SoundWire slave registration and the TX regmap. Board integration requires compatible strings `qcom,wcd9370-codec` or `qcom,wcd9375-codec`, RX/TX phandles, reset GPIO, regulators, and micbias/MBHC properties.

## Risks and Edge Cases
- In `wcd937x_micbias_control()`, the `MICB_PULLUP_DISABLE` branch increments `pullup_ref[micb_index]` when it is greater than zero. That appears to leak the pull-up reference count and can prevent micbias shutdown.
- Watchdog IRQ request failures are logged but do not abort component probe; later DAPM paths call `enable_irq()`/`disable_irq_nosync()` on the stored IRQ numbers regardless.
- `wcd9375_audio_map` contains a duplicated `ADC3_OUTPUT` to `ADC3_MIXER` route.
- SoundWire control changes directly alter port masks without an explicit lock; verify ALSA control access cannot race active stream setup on target kernels.
- Several power sequences rely on fixed microsecond sleeps, efuse values, and Class-H/MBHC side effects. Reordering or missing events can produce pops, OCP trips, or bad impedance results.
- `wcd937x_get_channel_map()` writes `SDW_MAX_PORTS` entries and reports `*rx_num`/`*tx_num` as the loop bound, not the number of active ports; machine drivers must interpret sparse masks correctly.

## Test Signals
Strong signals include platform probe/bind logs, correct chip ID detection, successful codec registration with two DAIs, WCD9375-only ADC3/DMIC widgets appearing only on WCD9375, jack insert/remove and button events from MBHC, impedance controls returning plausible left/right values, playback over HPHL/HPHR/EAR/AUX with Class-H modes and compander toggles, capture over AMIC/DMIC paths, SoundWire channel maps matching board data, PDM watchdog IRQ behavior, and runtime suspend/resume preserving register programming.
