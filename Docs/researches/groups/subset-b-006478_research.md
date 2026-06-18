# subset-b-006478 Research

Grouped source research for Qualcomm WCD codec support files in `sources/distributed-fs/ceph-client/sound/soc/codecs`. Each source file has a marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.c

## Purpose

`wcd-clsh-v2.c` implements the exported Class-H/Class-AB supply and headphone mode controller shared by WCD93xx-family codecs. It owns a small `struct wcd_clsh_ctrl` state object and translates logical Class-H events from codec DAPM paths into register writes for buck, flyback, Class-H CRC/DSM routing, gain path selection, and headphone PA bias modes. The source was read as a complete 902-line file.

## Important APIs, Types, and Functions

`struct wcd_clsh_ctrl` stores the current Class-H state and mode, reference counts for `flyback_users`, `buck_users`, and `clsh_users`, the codec version selector, and the owning `snd_soc_component`.

Exported entry points are `wcd_clsh_ctrl_alloc()`, `wcd_clsh_ctrl_free()`, `wcd_clsh_ctrl_set_state()`, `wcd_clsh_ctrl_get_state()`, and `wcd_clsh_set_hph_mode()`. Internal helpers split into v2/WCD9335-style and v3/WCD937x+ style paths: `wcd_clsh_state_ear()`, `wcd_clsh_state_hph_l()`, `wcd_clsh_state_hph_r()`, `wcd_clsh_state_lo()`, `wcd_clsh_v3_state_ear()`, `wcd_clsh_v3_state_hph_l()`, `wcd_clsh_v3_state_hph_r()`, and `wcd_clsh_v3_state_aux()`. Lower-level helpers program buck/flyback enables and modes, Class-H K coefficients, headphone power levels, IQ forcing, and gain path selection.

## Control Flow

Codec drivers call `wcd_clsh_ctrl_set_state()` on `WCD_CLSH_EVENT_PRE_DAC` to enable the requested path and on `WCD_CLSH_EVENT_POST_PA` to disable it. The public function validates that `nstate` is one of the defined singleton states, dispatches to `_wcd_clsh_ctrl_set_state()`, and records `ctrl->state` and `ctrl->mode`.

The state dispatcher selects an output path by requested state, then selects v2 or v3 programming based on `codec_version >= WCD937X`. Enable flows generally configure regulator mode, set buck/flyback mode, enable flyback, set flyback current, enable buck, and program headphone/line/ear path state. Disable flows reverse the PA/headphone mode, disable per-path Class-H routing where relevant, decrement buck/flyback/Class-H reference counts, and restore normal/default modes. Hardware-mandated `usleep_range()` delays are embedded after supply transitions.

## State and Persistence Behavior

All persistent state is in `struct wcd_clsh_ctrl`; there is no file-backed persistence. `buck_users`, `flyback_users`, and `clsh_users` protect shared hardware resources across left/right headphone, ear, lineout, and aux users. The code clamps `clsh_users` back to zero if it underflows, but buck/flyback counters are not similarly clamped. Hardware state persists in codec registers until later DAPM events or driver teardown write new values.

## Dependencies and Integration Points

The implementation depends on ASoC `snd_soc_component_*` register access, delay helpers, `wcd9335.h` register definitions, and `wcd-clsh-v2.h` public enums. It is integrated by `wcd9335.c` headphone, ear, and lineout DAC DAPM events, and is designed to support newer codec register layouts through version checks.

## Risks and Edge Cases

`wcd_clsh_ctrl_set_state()` accepts only singleton bit values even though state macros are bitmasks; callers that try to pass combined HPHL|HPHR state will be rejected. Several internal state functions log invalid mode combinations but return through the public API as success because `_wcd_clsh_ctrl_set_state()` always returns zero. Supply reference counters rely on balanced PRE_DAC/POST_PA calls; unbalanced disable paths can underflow buck/flyback counters and potentially desynchronize hardware enables. v2 K1 values are hard-coded for an assumed 16-ohm headphone impedance. The controller has no internal locking, so caller-side serialization through DAPM/component sequencing is assumed.

## Test Signals

Useful signals are kernel build coverage for `CONFIG_SND_SOC_WCD9335`, DAPM playback path tests for EAR/HPHL/HPHR/lineout, register trace checks around PRE_DAC and POST_PA ordering, balanced reference count tests for concurrent HPHL/HPHR enablement, and audio validation for click/pop behavior around the documented 100 us, 500 us, 1 ms, 5 ms, and 7 ms waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.h

## Purpose

`wcd-clsh-v2.h` is the public interface for the WCD Class-H controller. It defines the logical Class-H events, output states, amplifier modes, supported codec version identifiers, and exported controller functions used by codec drivers. The source was read as a complete 66-line file.

## Important APIs, Types, and Functions

`enum wcd_clsh_event` exposes `WCD_CLSH_EVENT_PRE_DAC` and `WCD_CLSH_EVENT_POST_PA`, matching the enable/disable event sequence used by DAPM event handlers. State macros define `WCD_CLSH_STATE_IDLE`, `WCD_CLSH_STATE_EAR`, `WCD_CLSH_STATE_HPHL`, `WCD_CLSH_STATE_HPHR`, `WCD_CLSH_STATE_LO`, and `WCD_CLSH_STATE_AUX`. `enum wcd_clsh_mode` covers Class-H normal, HiFi, low-power, low-HiFi, ultra-low-power, Class-AB variants, and `CLS_NONE`. `enum wcd_codec_version` selects WCD9335/WCD934x versus WCD937x+ programming.

The header forward-declares `struct wcd_clsh_ctrl` and declares `wcd_clsh_ctrl_alloc()`, `wcd_clsh_ctrl_free()`, `wcd_clsh_ctrl_get_state()`, `wcd_clsh_ctrl_set_state()`, and `wcd_clsh_set_hph_mode()`.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by `wcd-clsh-v2.c`; codec drivers include this file and call the public functions during DAPM state transitions.

## State and Persistence Behavior

The header does not allocate or store data. It describes state values and an opaque controller pointer whose storage is owned by the implementation. State persists only inside the allocated controller and codec registers programmed through it.

## Dependencies and Integration Points

The header includes `<sound/soc.h>` because public APIs use `struct snd_soc_component`. It is consumed by codec implementations such as `wcd9335.c` and by the implementation file itself.

## Risks and Edge Cases

State values are bitmasks, but the implementation currently validates only individual state values. New codec versions must be reflected in both the enum and implementation dispatch. Mode names include overlapping Class-H and Class-AB variants, so caller-side mode selection must match the output path and codec generation.

## Test Signals

Compile coverage should include this header from both the controller implementation and at least one codec driver. API compatibility tests are mostly build-time: enum users, opaque pointer usage, and exported symbol prototypes should remain synchronized with `wcd-clsh-v2.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-clsh-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.c

## Purpose

`wcd-common.c` provides shared Qualcomm WCD codec helper code for micbias voltage parsing/conversion, SoundWire component runtime-PM setup, SoundWire status/bus callbacks, and interrupt draining. The source was read as a complete 144-line file.

## Important APIs, Types, and Functions

Exported helpers are `wcd_get_micb_vout_ctl_val()`, `wcd_dt_parse_micbias_info()`, `wcd_sdw_component_ops`, `wcd_update_status()`, `wcd_bus_config()`, and `wcd_interrupt_callback()`. Internal `wcd_get_micbias_val()` reads `qcom,micbiasN-microvolt` properties, falls back to 1800 mV, and stores both millivolt and register-control forms through the caller's `struct wcd_common`.

## Control Flow

Micbias parsing loops from 1 to `common->max_bias`, reads each DT property, converts microvolts to millivolts, validates the 1000 mV to 2850 mV range, and computes the register value as `(mV - 1000) / 50`. Component bind enables runtime PM with a 3000 ms autosuspend delay; unbind disables it. SoundWire attach handling disables regcache cache-only mode and synchronizes cached writes. Bus configuration writes bank-specific clock divider control. Interrupt handling repeatedly dispatches nested IRQ 0 and rereads three interrupt status registers until all are clear.

## State and Persistence Behavior

The only caller-visible state is populated in `struct wcd_common`: `micb_mv[]` and `micb_vout[]`. Runtime PM state is stored in the device core. Register cache state is held by regmap. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on device tree, component framework, runtime PM, SoundWire APIs, irqdomain nested IRQ mapping, and regmap. It is intended for codec SoundWire slave drivers that share micbias and bus callback patterns.

## Risks and Edge Cases

`wcd_get_micbias_val()` logs the converted invalid value after `wcd_get_micb_vout_ctl_val()` returns a negative error, so the error message may show the error code rather than the original millivolt value. `sprintf()` into a 64-byte buffer is safe for the fixed property pattern and small index, but not bounds-checked. `wcd_interrupt_callback()` assumes the regmap exists; `wcd_update_status()` checks for regmap but the IRQ callback does not. The nested interrupt loop relies on status registers eventually clearing.

## Test Signals

Useful tests are DT parsing with missing, minimum, maximum, and out-of-range micbias properties; SoundWire attach tests that verify regcache sync; bus config tests for `next_bank`; IRQ tests with synthetic status register sequences; and runtime-PM bind/unbind smoke coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.h

## Purpose

`wcd-common.h` declares shared data structures and helper APIs for Qualcomm WCD codec support, especially SoundWire channel metadata, micbias storage, SoundWire component operations, and common callback functions. The source was read as a complete 46-line file.

## Important APIs, Types, and Functions

`WCD_MAX_MICBIAS` sets the common micbias array size to four entries. `struct wcd_sdw_ch_info` stores SoundWire port number, channel mask, and master channel mask; `WCD_SDW_CH()` initializes all three fields with matching channel masks. `struct wcd_common` carries a device pointer, max-bias count, and per-bias millivolt/register-control arrays.

The header declares `wcd_sdw_component_ops`, `wcd_get_micb_vout_ctl_val()`, `wcd_dt_parse_micbias_info()`, `wcd_update_status()`, `wcd_bus_config()`, and `wcd_interrupt_callback()`.

## Control Flow

There is no executable control flow in this header. It provides compile-time contracts for helper users and for the implementation in `wcd-common.c`.

## State and Persistence Behavior

The only state layout defined here is `struct wcd_common`, caller-owned and normally embedded in a codec driver. Values are runtime configuration derived from firmware/DT and do not persist outside driver lifetime.

## Dependencies and Integration Points

The header forward-declares `struct device`, `struct sdw_slave`, `struct sdw_bus_params`, `struct irq_domain`, and `enum sdw_slave_status` to keep includes light. It integrates with SoundWire codec drivers and common component binding.

## Risks and Edge Cases

Callers must keep `max_bias <= WCD_MAX_MICBIAS`; the parsing implementation does not independently clamp it. `WCD_SDW_CH()` assumes the master channel mask initially matches the slave channel mask, which may need adjustment for unusual routing.

## Test Signals

Build coverage from several WCD codec drivers is the main signal. Runtime tests should exercise `struct wcd_common` with one to four micbiases and verify channel metadata is interpreted correctly by SoundWire DAI setup code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.c

## Purpose

`wcd-mbhc-v2.c` implements the Qualcomm WCD MBHC v2 headset/headphone detection engine. It handles mechanical plug interrupts, ADC-based accessory classification, button press/release reporting, micbias/current-source policy, Type-C analog mux reporting, extension cable/lineout detection, cross-connection checks, over-current interrupts, and impedance reporting. The source was read as a complete 1635-line file.

## Important APIs, Types, and Functions

`struct wcd_mbhc` is the private runtime state: device/component/jack/config pointers, callback and IRQ tables, register-field table, delayed button work, plug-detection work, correction work, mutex, current plug type, jack status, button mask, impedance, headset type, ADC/legacy detection mode, and flags for switch IRQ, recording, force-linein, and Type-C behavior.

Exported functions are `wcd_mbhc_init()`, `wcd_mbhc_deinit()`, `wcd_mbhc_start()`, `wcd_mbhc_stop()`, `wcd_dt_parse_mbhc_data()`, `wcd_mbhc_event_notify()`, `wcd_mbhc_get_impedance()`, `wcd_mbhc_set_hph_type()`, `wcd_mbhc_get_hph_type()`, `wcd_mbhc_typec_report_plug()`, and `wcd_mbhc_typec_report_unplug()`. Important internal paths include `mbhc_plug_detect_fn()`, `wcd_correct_swch_plug()`, `wcd_mbhc_adc_hs_ins_irq()`, `wcd_mbhc_adc_hs_rem_irq()`, `wcd_mbhc_btn_press_handler()`, `wcd_mbhc_btn_release_handler()`, `wcd_check_cross_conn()`, `wcd_measure_adc_once()`, `wcd_measure_adc_continuous()`, and `wcd_mbhc_report_plug()`.

## Control Flow

Initialization validates required callback and register-field tables, allocates `struct wcd_mbhc`, initializes work items and a mutex, and registers seven threaded IRQs: mechanical switch, button press, button release, electrical insert, electrical remove, left OCP, and right OCP. `wcd_mbhc_start()` attaches config/jack pointers and calls `wcd_mbhc_initialise()`, which gets runtime PM, programs pullups, jack switch polarity, debounce, bias/clock, HS_VREF, and button thresholds.

Mechanical switch IRQ schedules `mbhc_plug_detect_work`. The work function toggles mechanical detection type. On insertion it enables micbias ramp, master bias, and starts ADC plug-type correction. On removal it disables FSM/current source, disables insert/remove IRQs, resets electrical detection, and reports removal for the current plug type.

ADC correction runs in `wcd_correct_swch_plug()`: it runtime-resumes the component, disables insert IRQ while classifying, checks ground/mic cross-connection repeatedly, measures IN2P through continuous and one-shot ADC modes, maps voltage to headphone/headset/high-impedance lineout, handles special-headset micbias bumping, optionally swaps ground/mic through a platform callback, runs a three-second stabilization loop, updates BCS and FSM current-source policy, reports the final jack type, sets `DETECTION_DONE` for headset button IRQs, and restores pull-down/runtime PM.

Button press IRQ ignores early presses within 250 ms of headset reporting, ignores non-headset and switch-handler overlap, maps hardware button result to `SND_JACK_BTN_0..5`, and schedules delayed reporting for long press. Release IRQ either reports long-release or short press+release and clears the button mask. Electrical removal validates against fake removals by polling ADC for at least 100 ms before reporting unplug.

## State and Persistence Behavior

Runtime state is in `struct wcd_mbhc`; jack status is reported through ALSA jack APIs and hardware state is programmed through the codec callback/register-field abstraction. Workqueue state persists until canceled by removal/deinit. Impedance values `zl` and `zr` are cached after successful detection and cleared on removal. There is no storage outside memory and hardware registers.

## Dependencies and Integration Points

The module depends on ASoC jack reporting, Linux IRQ/workqueue/mutex/runtime-PM APIs, and codec-provided `struct wcd_mbhc_cb` callbacks. Register access is indirect through `struct wcd_mbhc_field`, allowing different WCD codecs to reuse the algorithm with different register maps. It integrates with codec DAPM/micbias/PA events through `wcd_mbhc_event_notify()` so button current source and micbias state track playback/recording and PA usage.

## Risks and Edge Cases

The code assumes callback tables are complete enough for the selected configuration; some callbacks are optional but others are dereferenced after only the initial `mbhc_bias`/`set_btn_thr` validation. Several paths perform sleeps inside IRQ threads or work while holding `mbhc->lock`, so latency and lock ordering need care. Counter/state changes in micbias, fake removal, Type-C plug reporting, and work cancellation are race-prone if plug events arrive rapidly. `wcd_mbhc_get_impedance()` returns `-EINVAL` until both channels are nonzero. DT parsing only fills button high thresholds and basic polarity/threshold values; missing button thresholds default to 500 mV.

## Test Signals

High-value tests include insertion/removal of headset, headphone, high-impedance lineout, extension cable, Type-C analog accessory, and ground/mic-swapped plug; button short and long press/release; fake insertion/removal rejection; ADC threshold scaling for non-1.8 V micbias; impedance detect success/failure; OCP IRQ recovery; suspend/runtime-PM behavior during delayed correction work; and jack report masks for `SND_JACK_HEADSET`, `SND_JACK_HEADPHONE`, `SND_JACK_LINEOUT`, `SND_JACK_MECHANICAL`, and button bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.h

## Purpose

`wcd-mbhc-v2.h` defines the public contract for Qualcomm WCD MBHC v2 headset detection. It contains register-field identifiers, configuration structures, callback tables, IRQ tables, plug/button/micbias enums, and exported APIs with stubs when `CONFIG_SND_SOC_WCD_MBHC` is disabled. The source was read as a complete 343-line file.

## Important APIs, Types, and Functions

`enum wcd_mbhc_field_function` enumerates every abstract register field the algorithm may read/write, including detection enables, plug type, FSM, debounce, button result/source, electrical result, micbias control, PA/OCP fields, ADC fields, and moisture fields. `struct wcd_mbhc_config` stores DT/platform policy: button thresholds, headset/headphone thresholds, micbias selections, Type-C mux flag, ground/mic swap callback, line-in threshold, moisture options, and switch polarity. `struct wcd_mbhc_intr` names all IRQ numbers required by the implementation. `struct wcd_mbhc_cb` is the codec callback surface for bias, clock, threshold, impedance, micbias, pullup/pulldown, ground detection, ANC, and moisture operations.

The public functions are `wcd_dt_parse_mbhc_data()`, `wcd_mbhc_init()`, `wcd_mbhc_deinit()`, `wcd_mbhc_start()`, `wcd_mbhc_stop()`, `wcd_mbhc_event_notify()`, `wcd_mbhc_get_impedance()`, `wcd_mbhc_set_hph_type()`, `wcd_mbhc_get_hph_type()`, `wcd_mbhc_typec_report_plug()`, and `wcd_mbhc_typec_report_unplug()`.

## Control Flow

This header has no executable control flow beyond inline disabled-configuration stubs. With MBHC enabled, the implementation owns init/start/IRQ/workqueue flow. With MBHC disabled, parsing and most operations return `-ENOTSUPP` or `-EINVAL`, while `wcd_mbhc_start()` is a no-op success stub.

## State and Persistence Behavior

The header defines caller-provided config, callback, field, and IRQ state. The opaque `struct wcd_mbhc` runtime object is allocated by `wcd_mbhc_init()` and freed by `wcd_mbhc_deinit()`. All persistence is in memory, ALSA jack state, and codec registers.

## Dependencies and Integration Points

The header includes `<sound/jack.h>` and relies on ASoC component types through callback signatures. It is meant for codec drivers that map their register addresses into `WCD_MBHC_FIELD()` entries and provide hardware-specific callbacks around the common MBHC state machine.

## Risks and Edge Cases

The callback surface is broad and partially optional, so codec integrations must document which callbacks are mandatory for each feature. Disabled stubs are not all strict failures, which can hide missing MBHC support if callers do not check feature availability carefully. Field IDs and callback expectations must stay synchronized with `wcd-mbhc-v2.c`; adding a field without updating codec field tables silently reads/writes zero because missing fields are treated as absent.

## Test Signals

Build tests should cover both `CONFIG_SND_SOC_WCD_MBHC=y/m` and disabled configurations. Integration tests should verify each codec field table, IRQ table, and callback set against the common implementation, including button thresholds, Type-C path, impedance detection, and optional moisture hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.c

## Purpose

`wcd9335.c` is the Qualcomm WCD9335 Slimbus ASoC codec driver. It registers the codec component and DAIs, configures Slimbus RX/TX ports, exposes ALSA controls, builds DAPM widgets/routes for playback and capture paths, manages MCLK/master bias/SIDO voltage, handles Class-H events through `wcd-clsh-v2`, manages micbias/DMIC/ADC/PA power sequencing, and handles codec/interface interrupts. The source was read as a complete 5168-line file.

## Important APIs, Types, and Functions

`struct wcd9335_codec` is the main persistent state: device, clocks, Slimbus devices, codec/interface regmaps, IRQ chip data, RX/TX channel arrays, DAI runtime data, component pointer, master-bias and clock reference counts, SIDO voltage, Class-H controller, interpolator users, compander state, port routing, cached HPH gains, RX bias count, micbias/pullup refs, and DMIC clock refs. `struct wcd_slim_codec_dai_data` stores each DAI's channel list, Slimbus stream config, and stream runtime. `struct wcd9335_slim_ch` maps logical channels to Slimbus ports.

Key functions include DAI operations `wcd9335_hw_params()`, `wcd9335_trigger()`, `wcd9335_set_channel_map()`, `wcd9335_get_channel_map()`; Slim routing controls `slim_rx_mux_put()` and `slim_tx_mixer_put()`; rate programming helpers `wcd9335_set_interpolator_rate()` and `wcd9335_set_decimator_rate()`; DAPM event handlers for micbias, ADC, decimators, DMIC, Slim ports, interpolators, DACs, headphone/lineout/ear PAs, RX bias, and MCLK; clock/bias helpers `wcd9335_cdc_req_mclk_enable()`, `wcd9335_enable_master_bias()`, `wcd9335_enable_mclk()`, `wcd9335_codec_apply_sido_voltage()`; IRQ helpers `wcd9335_slimbus_irq()`, `wcd9335_setup_irqs()`, `wcd9335_irq_init()`; and driver lifecycle functions `wcd9335_slim_probe()`, `wcd9335_slim_status()`, `wcd9335_codec_probe()`, and `wcd9335_codec_remove()`.

## Control Flow

Slimbus probe allocates `struct wcd9335_codec`, parses reset GPIO, `mclk`, `slimbus` clock, and regulators, then toggles reset. When Slimbus status reports the device available, the driver resolves the interface Slimbus device from `slim-ifc-dev`, initializes codec and interface regmaps, performs chip bring-up for supported v2.0 silicon, creates a regmap IRQ chip, and registers the ASoC component/DAIs.

Component probe initializes the regmap, allocates a WCD9335 Class-H controller, sets default headphone mode to `CLS_H_HIFI`, writes codec default register settings, enables efuse sensing, initializes DAI channel lists, and requests the Slimbus slave IRQ. DAI channel map and DAPM RX/TX mux controls populate per-DAI channel lists. `hw_params()` derives sample-rate register values, programs interpolator or decimator rates based on active routing, builds Slimbus stream config and channel arrays, and allocates a Slimbus stream runtime. `trigger()` prepares/enables or disables/unprepares that Slimbus stream.

DAPM controls most power sequencing. Playback paths enable MCLK and RX bias, configure interpolators/companders, validate headphone DEM input for Class-H modes, call `wcd_clsh_ctrl_set_state()` before DAC enable and after PA disable, wait for hardware settle times, and unmute RX paths after PAs come up. Capture paths manage micbias reference counts, AMIC TX hold, decimator power level/HPF/mute/APC sequencing, DMIC clock group reference counts, and Slimbus interrupt-port enables. Clock helpers enforce master-bias-before-MCLK ordering and apply SIDO voltage transitions with required delays.

## State and Persistence Behavior

Persistent driver state lives in `struct wcd9335_codec` for the device lifetime. Many fields are reference counts that gate hardware resources: `master_bias_users`, `clk_mclk_users`, `sido_ccl_cnt`, `prim_int_users[]`, `rx_bias_count`, `micb_ref[]`, `pullup_ref[]`, and DMIC clock counters. ALSA controls persist selected compander states, HPH mode, volume registers, HPF cutoffs, and route muxes. Slimbus channel lists persist until controls or channel maps change. Register state is cached by regmap and programmed into hardware; no file-backed persistence exists.

## Dependencies and Integration Points

The driver integrates with Linux Slimbus, regmap/regmap-irq, regulator bulk enable, GPIO reset, common clock framework, ASoC component/DAI/DAPM/control APIs, and WCD9335 register definitions. It directly uses `wcd-clsh-v2` for Class-H sequencing. Although this subset includes MBHC helpers, this particular file does not instantiate `wcd-mbhc-v2`; it handles only WCD9335 codec audio paths and Slimbus IRQs in the read source.

## Risks and Edge Cases

Several resource counters can underflow or desynchronize if DAPM events are unbalanced. `wcd9335_hw_params()` ignores the return value from `wcd9335_slim_set_hw_params()`, which can hide allocation or regmap-write failures. `wcd9335_slim_set_hw_params()` allocates `cfg->chs` every setup and frees it in the Slim DAPM POST_PMD path, so error and unusual trigger/order paths must be checked for leaks or stale pointers. Some parsing is based on widget names, making widget renames risky. Headphone Class-H modes require DEM input set to `CLSH_DSM_OUT`; misrouting returns `-EINVAL` during DAPM enable. Slimbus IRQ handling disables per-port interrupt bits after overflow/underflow until ports are re-enabled. `wcd9335_slim_status()` calls `wcd9335_probe(wcd)` but does not propagate its return value.

## Test Signals

Important signals are probe/status success on a real or emulated WCD9335 Slimbus device, register-map access and IRQ chip setup, playback and capture PCM open/hw_params/trigger/stop across all seven DAIs, route changes through RX muxes and TX mixers, sample-rate coverage for 8 kHz through 384 kHz and 44.1 kHz restrictions, DAPM power sequencing for EAR/HPHL/HPHR/LINEOUT/AMIC/DMIC, Class-H HPH mode switching, compander enable/disable, micbias reference behavior, Slimbus overflow/underflow IRQ logging and clearing, suspend/runtime clock behavior, and leak/error-path tests around `cfg->chs` and Slim stream allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd9335.c -->
