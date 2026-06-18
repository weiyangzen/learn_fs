# Research: subset-b-006480

This grouped report covers four Qualcomm WCD codec files under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each file section is bounded by the reconciliation markers required by the research cron so the guard can split or verify the source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x-sdw.c

## Purpose
`wcd937x-sdw.c` is the SoundWire slave-side companion for the WCD9370/WCD9375 codec platform driver. It describes RX/TX SoundWire data ports, channel-to-port mappings, the CSR regmap reachable through the TX SoundWire device, interrupt forwarding from SoundWire out-of-band events into a Linux IRQ domain, and runtime PM cache behavior. The platform codec driver in `wcd937x.c` binds this RX/TX pair through the component framework and uses the TX instance as the main register interface.

## Important APIs, Types, and Functions
- `wcd937x_sdw_rx_ch_info` and `wcd937x_sdw_tx_ch_info` map logical codec channels such as `WCD937X_HPH_L`, `WCD937X_ADC1`, `WCD937X_MBHC`, and DMIC channels to SoundWire port numbers and channel masks.
- `wcd937x_dpn_prop` declares five simple SoundWire data ports with one to four/eight channels and simple channel prepare state machines.
- `wcd937x_sdw_hw_params()` builds an `sdw_stream_config` and active `sdw_port_config` array from the per-port masks selected by mixer controls in `wcd937x.c`, then calls `sdw_stream_add_slave()`.
- `wcd9370_interrupt_callback()` delegates SoundWire interrupt handling to `wcd_interrupt_callback()` over the shared slave IRQ domain and the three digital interrupt status registers.
- `wcd937x_defaults`, `wcd937x_rdwr_register()`, `wcd937x_readable_register()`, and `wcd937x_volatile_register()` define the regmap cache defaults and register accessibility policy for the codec CSR space.
- `wcd9370_probe()` initializes the per-slave private state, reads static port/channel mappings from device tree, configures SoundWire properties, creates the TX regmap, and registers the slave as a component.
- Runtime PM callbacks switch the TX regmap into cache-only mode on suspend and resync it on resume.

## Control Flow
Probe allocates `struct wcd937x_sdw_priv`, decides whether the SoundWire slave is TX by checking `qcom,tx-port-mapping`, reads TX or RX port maps into `pdev->m_port_map[1...]`, and optionally reads channel mapping arrays. TX instances configure `source_ports`, `src_dpn_prop`, wake capability, and the SoundWire regmap; RX instances configure `sink_ports` and do not own a regmap. Both attach `wcd_sdw_component_ops` through `component_add()` so the platform device can later call `component_bind_all()`.

Audio stream setup is driven from `wcd937x_codec_hw_params()` in `wcd937x.c`: mixer controls update `wcd->port_config[*].ch_mask`, then `wcd937x_sdw_hw_params()` copies only active ports into a compact array and adds the slave to the existing SoundWire stream runtime. Direction is selected from `wcd->is_tx`. Interrupts arrive via `sdw_slave_ops.interrupt_callback`, which triggers the codec IRQ domain consumed by regmap-irq and MBHC/watchdog logic in the platform driver.

## State and Persistence Behavior
The persistent runtime state is in `struct wcd937x_sdw_priv`: `sdev`, `sconfig`, `sruntime`, selected `port_config`, channel metadata, `master_channel_map`, `active_ports`, `is_tx`, backpointer to the aggregate codec, `slave_irq`, and optional `regmap`. Hardware register state is cached by REGCACHE_MAPLE and seeded from the large `wcd937x_defaults` table. Suspend marks the regcache dirty and cache-only; resume disables cache-only and calls `regcache_sync()`, so late register writes during suspend are replayed.

## Dependencies and Integration Points
This file depends on Linux SoundWire core (`sdw_slave`, `sdw_stream_add_slave`, `sdw_dpn_prop`), regmap, runtime PM, component framework, ASoC headers, and shared Qualcomm helpers from `wcd-common.h`/`wcd937x.h`. The key integration is with `wcd937x.c`, which provides the aggregate component, consumes the TX regmap, manages SoundWire stream callbacks, and fills port masks through user controls and DAPM decisions. Device tree must provide `qcom,rx-port-mapping`/`qcom,tx-port-mapping`, and may provide channel mapping arrays.

## Risks and Edge Cases
- `wcd937x_sdw_hw_params()` initializes `sconfig.ch_count` to `1` before counting set channel bits. Tests should confirm this matches SoundWire expectations for all mono/stereo/multichannel port selections.
- TX channel entries for `ADC2` and `ADC3` both use `BIT(0)` on `WCD937X_ADC_2_3_PORT`; correctness depends on static channel mapping or codec-specific port semantics and deserves hardware validation.
- The DSD RX enum order in `wcd937x.h` puts `WCD937X_DSD_R` before `WCD937X_DSD_L`, while this file lists the channel info as L then R. Since `wcd937x_connect_port()` indexes `ch_info[ch_id]`, this can invert DSD channel masks if not intentional.
- Missing device-tree port/channel mappings are logged with `dev_info()` and the driver continues, so broken board data may fail later as silent channel-map issues.
- Only TX instances own a regmap; platform bind must always find and link the TX device before codec registration.

## Test Signals
Useful validation signals include successful SoundWire enumeration of both RX and TX slaves, `component_bind_all()` reaching the platform codec, `regcache_sync()` succeeding after runtime resume, ALSA playback/capture hw_params exercising enabled port masks, `get_channel_map()` returning expected master channel masks, interrupt delivery through MBHC and PDM watchdog lines, and suspend/resume audio smoke tests with cached register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.h

## Purpose
`wcd937x.h` is the shared register and interface contract for the WCD937x codec driver pair. It defines the analog/digital register address map, bit masks, SoundWire port and channel enumerations, interrupt numbers, the `struct wcd937x_sdw_priv` bus-private state shared between the platform and SoundWire drivers, and conditional prototypes for SoundWire helper functions.

## Important APIs, Types, and Definitions
- Register constants span analog blocks at `0x3000` and digital blocks at `0x3400`, ending at `WCD937X_MAX_REGISTER`.
- Bit masks define MBHC detection, micbias modes and voltage fields, headphone PA ground overrides, PDM watchdog bits, interrupt status/mask/clear registers, and SoundWire channel mask helpers.
- `enum wcd937x_tx_sdw_ports` and `enum wcd937x_rx_sdw_ports` assign codec data-port numbers used by the SoundWire DPN property arrays.
- `struct wcd937x_sdw_priv` is the shared SoundWire state: slave device, stream config/runtime, port configs, channel info, enable flags, master channel map, TX/RX role, aggregate-codec backpointer, slave IRQ domain, and regmap.
- Conditional declarations for `wcd937x_sdw_free()`, `wcd937x_sdw_set_sdw_stream()`, and `wcd937x_sdw_hw_params()` return `-EOPNOTSUPP` when the SoundWire companion is not built.
- `enum` interrupt IDs must align with the `wcd937x_irqs` table in `wcd937x.c`.
- TX/RX channel enums are consumed by ALSA controls and `wcd937x_connect_port()` as indexes into `ch_info`.

## Control Flow and Integration
The header itself has no executable control flow, but it governs nearly all cross-file coupling. `wcd937x-sdw.c` uses the register constants for regmap defaults/access tables and uses the SoundWire port/channel enums for static channel metadata. `wcd937x.c` uses the same constants for DAPM event register programming, MBHC callbacks, IRQ setup, DAI stream operations, and control definitions. The Kconfig conditional around helper prototypes allows the platform driver to compile even when the SoundWire module is disabled, with calls failing explicitly.

## State and Persistence Behavior
`struct wcd937x_sdw_priv` captures the persistent bus-facing state that survives across ALSA callbacks while the device is bound. Hardware persistence is represented indirectly through register constants and the regmap cache configured in `wcd937x-sdw.c`. The `port_enable`, `port_config`, and `master_channel_map` members are the software record of user-selected SoundWire paths and are later translated into stream configuration.

## Dependencies and Integration Points
The header depends on SoundWire core types and `wcd-common.h` for shared channel-info helpers and micbias definitions. It is included by both the SoundWire slave driver and platform codec driver, so changes here can break register access policy, DAPM sequencing, MBHC fields, IRQ mapping, or channel-map interpretation.

## Risks and Edge Cases
- `WCD937X_MICB_DISABLE`, `WCD937X_MICB_ENABLE`, and `WCD937X_MICB_PULL_UP` are defined twice, once around MICB1/2 and again near MICB3. The duplicate values are identical, but it increases maintenance risk.
- `WCD937X_AUXPA_CLK_EN_MASK` is also defined twice.
- RX channel enum order lists `WCD937X_DSD_R` before `WCD937X_DSD_L`, while `wcd937x-sdw.c` initializes the channel-info array with DSD_L before DSD_R. Because the platform code indexes `ch_info[ch_id]`, this should be checked for channel inversion.
- Register address or interrupt enum changes must be synchronized with regmap defaults, readable/writeable/volatile policies, MBHC field maps, and regmap-irq tables.

## Test Signals
Header-level validation is mostly build and integration based: compile both enabled and disabled SoundWire configurations, confirm no duplicate macro warnings under stricter tooling, verify regmap accesses stay within `WCD937X_MAX_REGISTER`, check IRQ enum/table alignment, and run playback/capture channel-map tests that cover every TX/RX channel enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x-sdw.c

## Purpose
`wcd938x-sdw.c` is the SoundWire slave driver for WCD9380/WCD938x codecs. It performs the same bus-facing role as the WCD937x SoundWire file but for a wider codec: it defines TX/RX channel maps, port capabilities, stream setup/free/set-stream helpers exported to the platform codec, the large CSR regmap defaults/access policy, SoundWire interrupt forwarding, component registration, and runtime PM cache handling.

## Important APIs, Types, and Functions
- `wcd938x_sdw_rx_ch_info` covers HPH, CLSH, compander, line-out, and DSD playback channels.
- `wcd938x_sdw_tx_ch_info` covers four analog ADC channels, MBHC, and DMIC0-DMIC7 capture channels over the TX SoundWire ports.
- `wcd938x_sdw_hw_params()` compacts active port masks into `sdw_port_config` and calls `sdw_stream_add_slave()`.
- `wcd938x_sdw_free()` and `wcd938x_sdw_set_sdw_stream()` are exported helpers used by the matching platform codec driver.
- `wcd9380_interrupt_callback()` forwards SoundWire out-of-band interrupts to `wcd_interrupt_callback()` using the three WCD938x interrupt status registers.
- `wcd938x_defaults`, `wcd938x_rdwr_register()`, `wcd938x_readonly_register()`, `wcd938x_readable_register()`, `wcd938x_writeable_register()`, and `wcd938x_volatile_register()` define the CSR regmap cache model and hardware access rules.
- `wcd9380_probe()` initializes TX/RX SoundWire roles, reads static port mapping, creates the TX regmap, and registers the slave component.

## Control Flow
Probe allocates `struct wcd938x_sdw_priv`, checks for a TX port-mapping property, reads TX or RX static port mapping into the SoundWire master's port map, records `sdev`, sets bus properties such as SCP interrupt mask, lane control, and simple clock-stop support, then configures source or sink port capabilities. TX instances create the CSR regmap and start it in cache-only mode; RX instances only expose sink ports. Both register with the common WCD SoundWire component ops and are marked runtime-suspended until the aggregate codec binds them.

Stream control is exported: the platform DAI stores `sruntime`, calls `wcd938x_sdw_hw_params()` to add active ports to the stream, and calls `wcd938x_sdw_free()` to remove the slave. Interrupts are delivered through `sdw_slave_ops`, and the WCD938x driver also supplies `bus_config = wcd_bus_config`, unlike the WCD937x SoundWire driver.

## State and Persistence Behavior
State lives in the matching `wcd938x_sdw_priv` structure from `wcd938x.h`: role, stream runtime/configuration, selected port masks, channel maps, regmap, and IRQ domain pointer. Register state is cached with REGCACHE_MAPLE. Runtime suspend switches to cache-only and marks the cache dirty; runtime resume syncs cached writes and marks the device last busy.

## Dependencies and Integration Points
The driver depends on SoundWire core, regmap, runtime PM, component framework, ASoC, and shared Qualcomm helpers in `wcd-common.h` plus register/channel definitions from `wcd938x.h`. It integrates with the WCD938x platform codec driver through exported SoundWire helpers and `wcd_sdw_component_ops`. Device tree must provide appropriate static SoundWire port mappings for TX/RX board wiring.

## Risks and Edge Cases
- Like WCD937x, `sconfig.ch_count` starts at `1` before counting active channel bits, so stream setup should be validated against the SoundWire controller's expected channel count.
- Probe continues after missing static port mappings, which can defer board-data errors into stream startup or channel-map mismatches.
- Only TX owns the CSR regmap; aggregate binding must link and resume the TX device before any register access.
- `wcd938x_volatile_register()` treats all readonly registers as volatile, which is conservative but can reduce cache effectiveness for efuse/status reads.
- `wcd938x_sdw_free()` ignores the return value from `sdw_stream_remove_slave()`, so teardown errors are not surfaced to the DAI caller.

## Test Signals
Useful checks include TX/RX SoundWire enumeration, component binding with the platform codec, regmap cache sync after resume, DAI `set_stream`/`hw_params`/`hw_free` playback and capture cycles, all ADC/DMIC/HPH/DSD channel controls producing expected master channel maps, interrupt delivery through the shared IRQ domain, bus configuration callbacks on controller setup, and runtime PM autosuspend/resume while streams are closed and reopened.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x-sdw.c -->
