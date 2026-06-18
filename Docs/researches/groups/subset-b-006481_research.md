# subset-b-006481 research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h

## Purpose

`wcd938x.h` is the shared register and SoundWire contract header for the WCD938x codec driver family. It defines the codec CSR address map, bit masks, SoundWire port/channel enumerations, the per-SoundWire-child state structure, and the exported SoundWire helper prototypes used by `wcd938x.c`.

The header is intentionally hardware-facing. Most definitions are one-to-one names for analog, MBHC, TX, RX, class-H, interrupt, digital, efuse, SoundWire, pad, GPIO, and debug registers in the WCD938x address range from `WCD938X_BASE_ADDRESS` through `WCD938X_MAX_REGISTER`.

## Important APIs, types, and constants

The register map starts at `WCD938X_BASE_ADDRESS` and declares analog registers such as `WCD938X_ANA_BIAS`, `WCD938X_ANA_RX_SUPPLIES`, `WCD938X_ANA_HPH`, `WCD938X_ANA_EAR`, ADC channel registers, MBHC mechanical/electrical/ZDET/result/button registers, micbias registers, class-H and flyback registers, headphone PA and RDAC registers, earpiece and AUX registers, sleep/watchdog registers, and digital CDC/SoundWire/interrupt/efuse/pad/debug registers. `WCD938X_MAX_REGISTER` is `WCD938X_DIGITAL_DEM_BYPASS_DATA3`, giving regmap users a bounded maximum.

Bit-mask definitions describe fields used throughout `wcd938x.c`: RX supply and regulator mode bits, headphone PA/reference enables, earpiece gain fields, TX HPF init bits, MBHC detection and result masks, micbias VOUT and enable modes, LDOH enable, clock enable masks, TX/RX digital clock bits, ADC mode fields, compander enables, digital gain enables, DMIC clock masks, PDM watchdog masks, interrupt status/mask/clear registers, efuse ID masks, and moisture detection controls.

The SoundWire TX port enum maps logical source paths to data port numbers: `WCD938X_ADC_1_2_PORT`, `WCD938X_ADC_3_4_PORT`, `WCD938X_DMIC_0_3_MBHC_PORT`, and `WCD938X_DMIC_4_7_PORT`, with `WCD938X_MAX_TX_SWR_PORTS` as the last port number. `enum wcd938x_tx_sdw_channels` names ADC1-4, DMIC0-7, and MBHC channel IDs. The RX port enum maps `WCD938X_HPH_PORT`, `WCD938X_CLSH_PORT`, `WCD938X_COMP_PORT`, `WCD938X_LO_PORT`, and `WCD938X_DSD_PORT`; `enum wcd938x_rx_sdw_channels` names HPH, CLSH, compander, LO, and DSD channels.

`struct wcd938x_sdw_priv` is the bridge object shared between the SoundWire child driver and the aggregate codec driver. It contains the SoundWire slave pointer, stream config, current stream runtime, per-port `sdw_port_config` array, logical channel info table, `port_enable` booleans indexed by channel/port IDs, active port count, TX/RX direction flag, parent `wcd938x_priv`, shared slave IRQ domain, and child regmap.

The exported functions are `wcd938x_sdw_free()`, `wcd938x_sdw_set_sdw_stream()`, and `wcd938x_sdw_hw_params()`. When `CONFIG_SND_SOC_WCD938X_SDW` is enabled they are implemented by the SoundWire support object; otherwise inline stubs return `-EOPNOTSUPP`, allowing the main codec code to compile while making DAI operations fail cleanly without SoundWire support.

## Control flow and integration

The header has no executable control flow beyond compile-time configuration, but it controls how the C files interact. `wcd938x.c` includes it to program named registers and fields, build DAPM event handlers, configure MBHC register descriptors, map regmap IRQs, and bridge ASoC DAI operations to SoundWire helper functions. The SoundWire child implementation includes it to allocate and populate `wcd938x_sdw_priv`, expose channel tables, and configure SoundWire ports using the same enum values.

The port and channel enums are part of an implicit ABI inside the driver. ALSA controls in `wcd938x.c` use enum constants as `private_value` register/channel identifiers; DAPM and SoundWire helpers then use those IDs to locate `wcd938x_sdw_priv->ch_info[]` entries and mutate `port_config[port_num - 1].ch_mask`.

## State and persistence behavior

The header defines state shape but does not allocate persistent state. State persistence is handled by users of `struct wcd938x_sdw_priv`: the SoundWire child persists stream runtime, port masks, direction, regmap cache and IRQ domain pointers for the lifetime of the device, while the main codec stores pointers to the RX and TX child objects in `wcd938x_priv`.

Register definitions are persistent only in the hardware/regmap sense. They are used as stable symbolic addresses for reads, writes, cache defaults, volatile-register policy, and DAPM/MBHC sequencing. The fallback inline stubs make absence of SoundWire support an explicit runtime error for DAI operations rather than silently pretending stream setup succeeded.

## Dependencies and integration points

The header depends on Linux SoundWire types from `<linux/soundwire/sdw.h>` and `<linux/soundwire/sdw_type.h>`, kernel bit helpers such as `BIT()` and `GENMASK()`, ALSA PCM and DAI types referenced in function prototypes, and `struct wcd_sdw_ch_info` from the common WCD codec support included by C users.

Its main integration points are `wcd938x.c`, the WCD938x SoundWire child implementation, regmap configuration code, MBHC field descriptors, and ASoC controls that use these enum values. Device-tree and ACPI do not include this header directly, but their SoundWire port mapping and codec compatible data must match the register and port layout represented here.

## Risks

Because the file is a dense hardware register map, incorrect address or mask edits can break unrelated codec paths. Many masks are reused by event handlers that assume one-bit fields can be written with logical `1` values through `snd_soc_component_write_field()`. Changing enum order is risky because channel IDs index channel-info arrays and are embedded in ALSA control private data.

`WCD938X_MAX_SWR_CH_IDS` bounds `port_enable`, but RX and TX channel enums plus port enums use different logical spaces. Code that indexes `port_enable` by port number in one path and by channel ID in another needs careful review to avoid off-by-one or cross-direction confusion. The `CONFIG_SND_SOC_WCD938X_SDW` stubs also mean builds without SoundWire support compile, but runtime stream operations will fail with `-EOPNOTSUPP`.

## Test signals

Compile coverage should include both `CONFIG_SND_SOC_WCD938X_SDW=y/m` and disabled configurations to verify prototypes and inline stubs stay compatible. Runtime signals include successful regmap access through all referenced register ranges, correct SoundWire port masks for ADC/DMIC/HPH/CLSH/COMP/LO/DSD controls, correct interrupt mask/status/clear register use, and no undefined register access beyond `WCD938X_MAX_REGISTER`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c

## Purpose

`wcd939x-sdw.c` is the SoundWire slave driver for Qualcomm WCD939x codec RX/TX child devices. It provides channel-to-port metadata, data-port properties, ALSA-to-SoundWire stream setup helpers exported to the main WCD939x codec driver, interrupt forwarding from SoundWire out-of-band events into the codec regmap IRQ domain, regmap defaults and access policy for the TX CSR interface, component-framework registration, and runtime PM cache handling.

This file is a transport and register-access layer rather than the full ASoC codec policy. The aggregate WCD939x codec driver owns the high-level controls and DAPM behavior; this SoundWire child driver gives that aggregate driver a regmap, SoundWire stream operations, and RX/TX child component instances.

## Important APIs, types, and functions

`wcd939x_sdw_rx_ch_info` and `wcd939x_sdw_tx_ch_info` define logical codec channels with `WCD_SDW_CH(channel_id, port_num, channel_mask)`. RX channels cover HPH L/R, class-H, compander L/R, line-out, DSD L/R, and HIFI PCM L/R. TX channels cover ADC1-4, DMIC0-7, and MBHC. The TX table maps both `WCD939X_MBHC` and `WCD939X_DMIC2` to `WCD939X_DMIC_0_3_MBHC_PORT` bit 2, which makes those logical functions mutually dependent on the same SoundWire channel bit.

`wcd939x_rx_dpn_prop` and `wcd939x_tx_dpn_prop` advertise SoundWire data-port capabilities to the SoundWire core. RX ports support simple data ports with 1-2 channels for HPH, compander, DSD, and HIFI PCM, and 1 channel for CLSH and LO. TX ports support simple 1-4 channel source ports for ADC, ADC/DMIC, DMIC/MBHC, and upper DMIC groups.

The exported stream helpers are `wcd939x_sdw_hw_params()`, `wcd939x_sdw_free()`, and `wcd939x_sdw_set_sdw_stream()`. The main codec DAI callbacks call these helpers with a `struct wcd939x_sdw_priv` child object. `hw_params()` builds an active `sdw_port_config` array from nonzero `wcd->port_config[i].ch_mask`, fills `sdw_stream_config` with frame rate, direction, and PCM type, and calls `sdw_stream_add_slave()`. `free()` removes the slave from the stream. `set_sdw_stream()` stores the `sdw_stream_runtime` pointer.

Interrupt handling is implemented by `wcd9390_interrupt_callback()`, which calls common `wcd_interrupt_callback()` with the child `slave_irq` domain and the three WCD939x digital interrupt status registers. This bridges SoundWire implementation-defined interrupts to the regmap IRQ machinery owned by the aggregate codec.

Regmap support is defined by `wcd939x_defaults`, `wcd939x_rdwr_register()`, `wcd939x_readable_register()`, `wcd939x_volatile_register()`, `wcd939x_writeable_register()`, and `wcd939x_regmap_config`. The defaults table covers analog, MBHC, TX, RX, class-H, flyback, digital CDC, interrupt, pad, dem, RX_TOP, compander, ear and DSD registers. The access callbacks split ordinary read/write registers from read-only status/efuse/result/debug registers and volatile status/result/interrupt/debug registers. The regmap uses 32-bit register addresses, 8-bit values, `REGCACHE_MAPLE`, and `WCD939X_MAX_REGISTER`.

Device lifecycle is handled by `wcd9390_probe()`, `wcd9390_remove()`, `wcd939x_sdw_runtime_suspend()`, and `wcd939x_sdw_runtime_resume()`. The SoundWire driver is registered by `module_sdw_driver(wcd9390_codec_driver)` with SoundWire device ID vendor `0x0217`, part `0x10e`.

## Control flow

At SoundWire probe, `wcd9390_probe()` allocates `struct wcd939x_sdw_priv`, detects whether this child is TX by checking for `qcom,tx-port-mapping`, and reads either TX or RX static port mapping into `pdev->m_port_map[1]` because WCD data ports start at index 1. Missing static mapping is informational rather than fatal. It then stores the SoundWire slave pointer, configures SCP interrupt masks, lane-control and simple clock-stop capability, assigns source or sink port bitmaps and DPN property arrays, and assigns the appropriate channel-info table.

Only TX children create a regmap with `devm_regmap_init_sdw()`, because the TX SoundWire device is the main CSR register interface. That regmap starts in cache-only mode until SoundWire enumeration and aggregate binding make hardware access safe. Both RX and TX children register with the component framework through `component_add(dev, &wcd_sdw_component_ops)`, allowing the aggregate codec platform driver to bind them.

When the aggregate ASoC DAI configures a PCM stream, `wcd939x_sdw_set_sdw_stream()` first stores the SoundWire stream runtime. `wcd939x_sdw_hw_params()` scans `wcd->port_config` for enabled channel masks, copies active ports into a local array, computes a channel count from set bits, fills `sconfig`, selects TX or RX direction from `wcd->is_tx`, and calls `sdw_stream_add_slave()`. Stream shutdown calls `wcd939x_sdw_free()`, which removes the slave from the SoundWire stream.

During SoundWire interrupt delivery, the core calls `wcd9390_interrupt_callback()`. The callback does not decode codec interrupts itself; it delegates to the common WCD helper so the regmap IRQ chip in the aggregate driver can read status, acknowledge, and fan out nested IRQs.

Runtime suspend and resume only operate on the TX regmap when present. Suspend sets cache-only mode and marks the cache dirty. Resume clears cache-only mode and synchronizes cached writes to hardware. RX-only children have no regmap in this file and therefore do no cache work.

## State and persistence behavior

Persistent in-memory state lives in `struct wcd939x_sdw_priv`, which is allocated per SoundWire child. It stores the SoundWire slave, stream configuration, current stream runtime, per-port channel masks, active port count, TX/RX direction, parent aggregate pointer, slave IRQ domain, and TX regmap. The active port masks are expected to be mutated by the aggregate codec controls before `hw_params()` consumes them.

Hardware register state is represented by the TX child regmap. The defaults table seeds regcache, readable/writeable/volatile callbacks control cacheability and access validation, and runtime PM moves the regmap between cache-only and synchronized states. Since only TX owns the regmap, aggregate drivers must respect device links and PM ordering so register accesses do not occur while TX is suspended or not enumerated.

SoundWire stream state is not persistent across stream free. `sruntime` is a borrowed pointer set by the main DAI `.set_stream` path and used by `sdw_stream_add_slave()` and `sdw_stream_remove_slave()`. `active_ports` and `sconfig` are recomputed for each `hw_params()` call from current `port_config` masks.

## Dependencies and integration points

The driver depends on Linux SoundWire core APIs (`sdw_slave`, `sdw_stream_add_slave()`, `sdw_stream_remove_slave()`, `sdw_driver`, DPN properties, SCP interrupt masks), regmap over SoundWire, runtime PM, component framework, OF properties, and ALSA SoC DAI types used by exported helpers.

Local dependencies are `wcd939x.h` for WCD939x register, enum, and private-structure definitions, and `wcd-common.h` for `WCD_SDW_CH`, common SoundWire component ops, update-status and bus-config callbacks, and interrupt forwarding. The aggregate WCD939x codec driver is expected to bind the RX/TX SoundWire components, set `slave_irq`, set parent pointers, and call the exported stream helpers from its DAIs.

External integration points are SoundWire device ID `SDW_SLAVE_ENTRY(0x0217, 0x10e, 0)`, device-tree properties `qcom,tx-port-mapping` and `qcom,rx-port-mapping`, SoundWire implementation-defined interrupts, and runtime PM. TX children advertise wake capability, while RX children only advertise sink ports.

## Risks

`wcd939x_sdw_hw_params()` initializes `wcd->sconfig.ch_count` to `1` and then increments once for each set channel bit. If SoundWire expects an exact enabled-channel count, this appears to overcount by one for every stream. That behavior should be compared with hardware expectations and related WCD drivers before changing it, because a silent off-by-one in SoundWire stream config can break channel preparation.

The TX channel table maps `WCD939X_MBHC` and `WCD939X_DMIC2` to the same port and channel mask. That may be intentional because MBHC data shares a DMIC lane, but it is a risk for controls that allow both paths to be enabled independently. Static port mapping is optional; if firmware omits it, operation depends on default SoundWire port mapping being valid for the board.

Only TX creates the regmap. Any aggregate-driver path that tries to use RX child regmap state would fail, and any PM dependency bug that lets TX suspend before register access can produce stale cache writes or I/O failures. The register access policy is large and manual; missing a volatile status register or marking a write-only register readable can cause stale status, failed cache sync, or regmap warnings.

`wcd939x_sdw_free()` unconditionally calls `sdw_stream_remove_slave()` with the stored runtime. It assumes `.set_stream` was called and `sruntime` remains valid. Error paths around failed `sdw_stream_add_slave()` should ensure later free does not remove an unadded or NULL stream.

## Test signals

Probe tests should cover TX and RX child enumeration, optional static port mapping, component bind with the aggregate codec, TX regmap creation in cache-only mode, and correct source/sink port properties visible to the SoundWire core. Stream tests should verify enabled channel masks produce the expected SoundWire port configs, active port counts, TX/RX directions, frame rates, and channel counts for mono, stereo, and four-channel capture.

Power-management tests should suspend/resume the TX child and confirm regcache dirty/sync behavior, no register I/O while cache-only is active, and stable playback/capture across runtime PM cycles. Interrupt tests should inject or observe MBHC/button/OCP/status interrupts and confirm SoundWire callbacks trigger the aggregate regmap IRQ domain. Regmap tests should read volatile status registers without stale cache effects and verify cache sync does not attempt unsupported read-only writes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c -->
