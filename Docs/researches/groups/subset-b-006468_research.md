# Research: subset-b-006468

This grouped report covers the Realtek RT711/RT712/RT715 SoundWire and SDCA codec files assigned to `subset-b-006468`. Each section is source-path aligned and bounded by reconciliation markers for deterministic splitting into per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.c

Purpose: Implements the RT711 SDCA ASoC codec core. It exposes the jack codec and mic-array SDCA functions, ALSA controls, DAPM widgets/routes, SoundWire DAI operations, headset/button detection, calibration, and attach-time hardware initialization. It is called by the SoundWire bus wrapper after regmap creation.

Important APIs and functions: `rt711_sdca_init()` allocates `struct rt711_sdca_priv`, installs component/DAI drivers, initializes mutexes and delayed work, and enables runtime PM. `rt711_sdca_io_init()` is the attach-time initializer and sets `hw_init`/`first_hw_init`. `rt711_sdca_set_jack_detect()`, `rt711_sdca_jack_init()`, `rt711_sdca_jack_detect_handler()`, and `rt711_sdca_btn_check_handler()` implement the jack callback and deferred reporting. `rt711_sdca_pcm_hw_params()` maps AIF1/AIF2 to SoundWire ports DP3/DP2/DP4 and writes SDCA sample-frequency controls. Indexed vendor access is centralized in `rt711_sdca_index_read/write/update_bits()`.

Control flow: probe registers the component while hardware stays cache-only until the slave attaches. On attach, `io_init` disables cache-only, optionally bypasses cache on reattach, resets vendor/HDA blocks, reads the product version, applies VD0 or VD1 programming, calibrates, enables HP output, initializes jack detection if the machine driver already supplied a jack, marks the device initialized, and autosuspends. Runtime controls update MBQ volume registers, SDCA FU mute controls, selected GE mode override, and DAPM power-state controls. Jack IRQ status is staged by the SoundWire wrapper in `scp_sdca_stat1/2`, then the delayed work reads SDCA GE/HID controls and reports `SND_JACK_*`.

State and persistence: Persistent state lives in `rt711_sdca_priv`: normal and MBQ regmaps, SoundWire slave, component, jack pointer, cached interrupt bits, calibration/IRQ locks, hardware version, `hw_init`, `first_hw_init`, JD source, forced GE mode, and mixer/DAPM mute mirrors. Regcache is cache-only before enumeration and dirty-marked after reinitialization so resume can replay selected registers.

Dependencies and integration: Depends on Linux ASoC, DAPM, jack, SoundWire stream helpers, SDCA register macros, runtime PM, regmap, and workqueues. The wrapper file supplies regmaps and calls `rt711_sdca_init()`/`rt711_sdca_io_init()`. Machine drivers interact through the component controls, DAI names `rt711-sdca-aif1`/`aif2`, and `.set_jack`.

Risks and test signals: Hardware risk is concentrated in magic vendor sequences, version-specific init, calibration timeouts, GE/HID owner handling, and delayed-work/IRQ races around suspend. Functional tests should check card registration, jack insertion/removal, button press/release, JD source property variants, supported rates 44.1/48/96/192 kHz, SoundWire port assignment, DAPM mute transitions, suspend/resume cache sync, and logs for calibration or IO errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.h

Purpose: Defines the private state and register vocabulary for the RT711 SDCA codec core and its SoundWire wrapper. The header provides SDCA entity/control IDs, vendor index IDs, jack-detect constants, channel IDs, supported sample-rate encodings, DAI IDs, and exported init/detect entry points.

Important APIs/types: `struct rt711_sdca_priv` carries both regmaps, component/slave pointers, SoundWire bus params, runtime init flags, jack and delayed work state, calibration and IRQ mutexes, cached SDCA interrupt status, hardware version, JD source, GE override, and DAPM/mixer mute mirrors. Exported declarations are `rt711_sdca_init()`, `rt711_sdca_io_init()`, and `rt711_sdca_jack_detect()`. Enums identify AIF1/AIF2, JD routing (`JD1`, `JD2`, `JD2_100K`), and hardware versions `VD0`/`VD1`.

Control/data model: Most definitions are not simple offsets but contract values consumed by the C implementation: vendor NIDs select MBQ index spaces, SDCA entity IDs select functions such as jack codec, mic array, HID, FUs, PDEs, clock selectors, and line entities, and control IDs select SDCA mute/volume/sample-rate/current-owner/power-state fields.

State and persistence: The header encodes which state is software-owned versus hardware-owned. Software mirrors mute state, jack state, interrupt disable state, and first-init state because regmap cache and SoundWire attach/resume can outlive a single hardware enumeration.

Dependencies and integration: Includes PM, regmap, SoundWire, ASoC, and workqueue headers because the private structure is shared across core and bus glue. The SoundWire bus file depends on this header for function prototypes and state layout; the core file depends on it for all magic register constants.

Risks and test signals: Renumbering entity/control constants or changing `rt711_sdca_priv` semantics can silently break register writes. Test signals include successful compile coverage across both core and bus wrapper, valid ACPI/property JD source handling, and runtime traces showing expected SDCA addresses for mute, volume, sample-rate, GE, and HID accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.c

Purpose: Provides the SoundWire bus driver for the non-SDCA RT711 codec. It builds two regmaps, translates HDA-style register operations over SoundWire, declares port properties, handles attach status and interrupts, and manages runtime/system PM.

Important APIs and functions: `rt711_sdw_probe()` creates a raw SoundWire 8-bit regmap plus a logical 24/32-bit codec regmap with custom `rt711_sdw_read()`/`rt711_sdw_write()` callbacks, then calls `rt711_init()`. `rt711_read_prop()` advertises source ports 2 and 4 and sink port 3. `rt711_update_status()` calls `rt711_io_init()` on attach and clears `hw_init` on unattach. `rt711_bus_config()` stores bus params and calls `rt711_clock_config()`. `rt711_interrupt_callback()` schedules jack detection on implementation-defined control-port interrupts.

Control flow: Logical regmap reads/writes decide whether the target is an index register, HDA verb, gain register, or plain SoundWire register and emit the required low-level byte transactions. Interrupts are guarded by `disable_irq_lock` so system suspend can disable new scheduling while existing delayed work drains. Suspend cancels jack/button/calibration work and switches the logical regmap cache-only. Resume waits for SoundWire initialization if the slave was unattached, reenables interrupts if needed, clears `unattach_request`, and syncs selected regcache regions.

State and persistence: This file owns bus-visible properties and PM behavior while `rt711.c` owns codec semantics. Persistent state includes `params` copied from the bus, `disable_irq`, `hw_init`, `first_hw_init`, and regcache dirty/cache-only status.

Dependencies and integration: Integrates with `module_sdw_driver`, SoundWire slave ops, regmap, runtime PM, and `rt711.h`/`rt711-sdw.h`. It exposes SDW ID `0x025d:0x711` and the driver name `rt711`.

Risks and test signals: The custom HDA-over-SDW translation is fragile; bad register classification can corrupt codec state. Tests should exercise readable/volatile ranges, bus frequency changes, attach/unattach cycles, jack interrupts, system suspend with pending work, runtime resume cache sync, and probe failure paths for both regmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.h

Purpose: Supplies the non-SDCA RT711 logical regmap defaults used by the SoundWire wrapper. The table seeds register cache values for HDA verb windows, decoded vendor/index registers, gain controls, SDCA-like address ranges, and private vendor settings.

Important APIs/types: The primary artifact is `rt711_reg_defaults[]`, a `struct reg_default` array referenced by `rt711_regmap` in `rt711-sdw.c`. It covers normal byte registers, HDA readback windows (`0x2012` etc.), data-port/BRA/debug ranges, amplifier gain defaults, and private-index values such as jack auto-detect and mux controls.

Control flow: There is no executable logic in this header. At probe, regmap uses the table to initialize `REGCACHE_MAPLE`; the bus driver later switches cache-only/cache-bypass modes during attach, suspend, and resume. The defaults determine what values are replayed or compared when the codec is not immediately accessible.

State and persistence: This header is effectively the persisted default-state contract for the RT711 logical regmap. It influences suspend/resume behavior, first attach before hardware init, and ALSA controls that read cached values.

Dependencies and integration: Included only by `rt711-sdw.c`; depends on `struct reg_default` being available from regmap includes in the C file. It is paired with readable/volatile filters in the wrapper, so new defaults must remain inside allowed register ranges.

Risks and test signals: Stale defaults can cause regcache sync to program wrong jack, gain, or mux values after resume. Tests should compare hardware reset values against this table, verify no default falls outside readable ranges, and run suspend/resume plus mixer-control readback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.c

Purpose: Implements the non-SDCA RT711 ASoC codec core using HDA verb style register access over the logical SoundWire regmap. It provides mixer controls, DAPM routes, DAI operations, headset/button detection, calibration, bus clock configuration, and attach-time codec initialization.

Important APIs and functions: `rt711_init()` allocates state, registers component/DAIs, initializes delayed work and calibration work, and enables runtime PM. `rt711_io_init()` performs reset, pin/gain/default setup, mux arrangement, calibration, and deferred jack setup at SoundWire attach. `rt711_clock_config()` programs clock selectors from current bus rate. `rt711_set_jack_detect()` and `rt711_jack_init()` connect the machine jack to unsolicited response configuration. `rt711_pcm_hw_params()` maps playback/capture to SoundWire ports and writes HDA format registers.

Control flow: The driver starts cache-only, becomes active on SoundWire attach, resets codec state, powers audio to D0, programs pins and muted gains, writes configuration defaults and vendor indexes, then powers back to D3. First initialization schedules calibration asynchronously; later reinitialization calibrates synchronously with cache bypass. DAPM events write stream IDs and output/input power/gain state. Jack work reads pin sense, optionally waits for combo-jack auto-detection, decodes button IRQ tables, reports the ALSA jack state, and schedules release polling.

State and persistence: `struct rt711_priv` stores regmaps, component/slave, bus params, `hw_init`, `first_hw_init`, jack pointer, delayed works, calibration work, calibration/IRQ locks, current jack type, JD source, and interrupt-disable state. Bias-level management and calibration mutex prevent power-state changes while headset calibration or gain updates are running.

Dependencies and integration: Depends on ASoC, DAPM, SoundWire stream helpers, HDA verb constants, runtime PM, regmap, and the SoundWire wrapper. Machine drivers consume component controls, DAI names `rt711-aif1`/`rt711-aif2`, and the jack callback.

Risks and test signals: Risks include long calibration polling, asynchronous first calibration racing with suspend/remove, HDA verb translation correctness, JD source property handling, and hard-coded port differences from the SDCA version. Test jack detect/button tables, DAPM stream ID transitions, 44.1/48 kHz stream setup, supported sample widths, bus clock configurations, suspend/resume with pending work, and calibration timeout logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.h

Purpose: Defines the state, HDA verb/register constants, private vendor-index constants, DAI IDs, jack-detect options, and exported entry points for the non-SDCA RT711 codec and its SoundWire wrapper.

Important APIs/types: `struct rt711_priv` is the shared core/bus state: logical codec regmap, raw SoundWire regmap, component/slave pointers, bus params, init flags, jack work, calibration work, calibration and IRQ locks, current jack type/source, and disable-IRQ flag. Exports include `rt711_init()`, `rt711_io_init()`, `rt711_jack_detect()`, and `rt711_clock_config()`.

Control/data model: The header maps RT711 nodes (`DAC_OUT2`, `ADC_IN1`, `HP_OUT`, mixers, vendor blocks), HDA verbs for power, pin control, unsolicited events, stream IDs, amplifier gain/mute, and private index read/write windows. Compound macros form complete verb addresses used directly by ALSA controls and DAPM events.

State and persistence: Constants define how software reconstructs codec state after attach or resume. The private struct mirrors values that cannot be safely inferred from hardware while suspended, including first initialization, jack type, JD routing, and whether IRQ handling is temporarily disabled.

Dependencies and integration: Included by both `rt711.c` and `rt711-sdw.c`. It assumes regmap, SoundWire, ASoC, and PM types are visible through the including C files and declares `rt711_runtime_pm` for external PM integration.

Risks and test signals: Any change to verb macros can break regmap translation in `rt711-sdw.c` and control writes in `rt711.c`. Test signals include build coverage, correct HDA command bytes in regmap debug, expected ALSA mixer names, JD source variants, and stream-ID/gain register writes during DAPM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt711.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.c

Purpose: Implements a standalone RT712 SDCA digital microphone SoundWire codec function. Unlike `rt712-sdca.c`, this file registers only the mic-array component and a single capture DAI, with its own regmaps, controls, DAPM graph, attach initialization, and PM handling.

Important APIs and functions: `rt712_sdca_dmic_sdw_probe()` initializes 8-bit SDCA and 16-bit MBQ regmaps and calls `rt712_sdca_dmic_init()`. `rt712_sdca_dmic_io_init()` programs DMIC/ADC/HDA floating entity maps, enables the input terminal, ultrasound detector, RC calibration value, and marks `hw_init`. `rt712_sdca_dmic_hw_params()` configures SoundWire TX port 2 and writes mic-array sample-frequency controls. Control helpers manage four-channel FU1E mute/volume and FU15 boost.

Control flow: Probe creates regmaps cache-only and registers the ASoC component/DAI. On SoundWire attach, `update_status` calls `io_init`, which disables cache-only, optionally bypasses cache on reattach, performs vendor index programming, toggles first-init state, and autosuspends. ALSA mixer controls convert user gain values to SDCA fixed-point MBQ values. DAPM events combine software mixer mutes with DAPM mute state before writing per-channel FU1E mute controls, and PDE 11 power events request PS0/PS3.

State and persistence: `struct rt712_sdca_dmic_priv` stores regmaps, component, slave, bus params, init flags, `fu1e_dapm_mute`, and four per-channel mixer mute bits. Regcache is synchronized on resume and made dirty after cache-bypassed reinitialization.

Dependencies and integration: Uses common RT712 SDCA constants from `rt712-sdca.h`, standalone defaults from `rt712-sdca-dmic.h`, SoundWire slave ops, regmap, runtime PM, and ASoC DAPM/control APIs. It matches SDW part IDs `0x1712`, `0x1713`, `0x1716`, and `0x1717`.

Risks and test signals: The source uses some casts to `struct rt712_sdca_priv *` in gain helpers even though component drvdata is the DMIC private type; the accessed leading fields currently align but this is a maintenance hazard. Test four-channel capture, rates 16/32/44.1/48/96/192 kHz, port-2 SoundWire setup, mux selection, per-channel mute/volume, suspend/resume regcache sync, and attach/unattach reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.h

Purpose: Defines private state, per-control metadata, channel constants, and regmap defaults for the standalone RT712 SDCA DMIC SoundWire function.

Important APIs/types: `struct rt712_sdca_dmic_priv` holds the normal and MBQ regmaps, component, SoundWire slave, bus params, `hw_init`, `first_hw_init`, DAPM mute state, and four-channel mixer mute array. `struct rt712_sdca_dmic_kctrl_priv` describes dynamic ALSA controls with a base register, channel count, max value, and invert flag. The default arrays `rt712_sdca_dmic_reg_defaults[]` and `rt712_sdca_dmic_mbq_defaults[]` seed `REGCACHE_MAPLE` for SDCA and MBQ spaces.

Control/data model: Defaults cover HDA/vendor windows, RC calibration, mic-array sample-frequency controls, FU1E mutes/volumes, platform FU15 channel gain, and entity mapping values needed for DMIC capture. Channel constants `CH_01` through `CH_04` are used for contiguous SDCA controls.

State and persistence: The default arrays define cached power-on state before physical attach and after resume. The private structure mirrors mutable mute state so DAPM and ALSA mixer switches can be combined deterministically when hardware is temporarily inaccessible.

Dependencies and integration: Included by `rt712-sdca-dmic.c`; it relies on shared RT712 constants from `rt712-sdca.h` being included first in the C file and on SoundWire SDCA control macros.

Risks and test signals: Defaults must stay consistent with readable/volatile filters in the C file. Test signals include successful regmap registration, no out-of-range defaults, correct initial mute/readback state for four channels, and cache sync after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-dmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.c

Purpose: Provides the SoundWire bus glue for the multi-function RT712 SDCA codec. It declares regmaps, readable/volatile register ranges, port properties, SDCA interrupt handling, attach-time initialization, and PM cache synchronization.

Important APIs and functions: `rt712_sdca_sdw_probe()` creates the SDCA and MBQ regmaps and calls `rt712_sdca_init()`. `rt712_sdca_read_prop()` advertises source ports 4/8 and sink ports 1/3 with paging, wake capability, and clock-stop timeout. `rt712_sdca_update_status()` restores SDCA interrupt masks after attach and calls `rt712_sdca_io_init()`. `rt712_sdca_interrupt_callback()` reads and clears SDCA interrupt status, merges pending button status if work was canceled, and schedules jack delayed work.

Control flow: Probe registers the bus driver with SDW IDs for RT712/713/716/717. On attach, interrupt masks may be restored before initialization to avoid missing jack events. Interrupt processing cancels pending jack work, snapshots `SCP_SDCA_INT1/2`, loops up to three times clearing SDCA cascade flags, and schedules jack work after 30 ms unless system suspend disabled IRQ handling. Suspend cancels jack work, disables SDCA interrupt masks for system sleep, and switches both regmaps cache-only. Resume waits for enumeration if needed, reenables masks, clears `unattach_request`, and syncs both regmaps.

State and persistence: Uses the shared `rt712_sdca_priv` state from the core file, especially `scp_sdca_stat1/2`, `disable_irq`, `hw_init`, and `first_hw_init`. Regcache covers both 8-bit SDCA controls and 16-bit MBQ vendor/index values.

Dependencies and integration: Depends on SoundWire slave ops, regmap SoundWire helpers including MBQ, runtime PM, `rt712-sdca.h`, and the defaults in `rt712-sdca-sdw.h`. It imports `SND_SOC_SDCA`.

Risks and test signals: Interrupt clearing and canceled-work status merging are race-prone. Tests should cover jack/button events under repeated interrupts, attach after reset, suspend during pending jack work, unattach/resume timeout paths, source/sink port discovery, and cache sync of both regmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.h

Purpose: Provides RT712 SDCA regmap default tables for the main multi-function SoundWire codec instance.

Important APIs/types: `rt712_sdca_reg_defaults[]` seeds 8-bit SDCA controls for sample-frequency indexes, FU mutes, PDE power states, jack/mic/amp function defaults, and amp output vendor control. `rt712_sdca_mbq_defaults[]` seeds 16-bit MBQ/vendor values for analog, calibration, HID, jack, mixer, EAPD, FU volumes, platform gains, and amp volume controls.

Control flow: The header is data-only. `rt712-sdca-sdw.c` references these arrays in `regmap_config` so regcache has known values before attach and while suspended. `rt712-sdca.c` later mutates the same addresses during VA/VB initialization, DAPM events, and mixer-control writes.

State and persistence: These defaults define the baseline restored by regcache. They represent muted FUs, power-down PDEs, 48 kHz default sample-frequency indexes, and zero volume/gain defaults for user controls.

Dependencies and integration: Included by the SoundWire wrapper after `rt712-sdca.h`, because the arrays use shared SDCA function/entity/control IDs and `CH_01`/`CH_02`/etc. The readable/volatile filters in the wrapper must cover all addresses listed here.

Risks and test signals: Incorrect defaults can produce audible pops, muted paths, wrong amp state, or broken resume. Test signals include regmap cache validation, mixer default readback, DAPM power-up from a muted baseline, speaker-present and RT713 no-speaker variants, and resume after autosuspend/system sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.c

Purpose: Implements the main RT712 SDCA codec core. It supports jack/headphone codec paths, optional class-D speaker/amp paths, and optional smart-mic/DMIC component registration for RT712 VB systems, with controls, DAPM graphs, DAI ops, jack/button handling, calibration, and attach-time version-specific initialization.

Important APIs and functions: `rt712_sdca_init()` registers the main component and, when SDCA quirks expose SMART_MIC, a second DMIC component. `rt712_sdca_io_init()` reads product/version IDs, selects VA or VB initialization, enables jack setup, and marks first init. `rt712_sdca_va_io_init()` programs legacy VA analog/jack/speaker registers; `rt712_sdca_vb_io_init()` initializes mic, jack, and amp function blocks based on SDCA `FUNCTION_NEEDS_INITIALIZATION`. `rt712_sdca_pcm_hw_params()` maps AIF1/AIF2/AIF3 to ports 1/3/4/8 and writes function-specific sample-frequency indexes.

Control flow: Probe registers controls/routes, adding speaker widgets dynamically when the hardware is not RT713. Jack setup enables HID and GE events and SDCA interrupt masks. The SoundWire wrapper stores interrupt bits, then delayed work reads GE detected mode and HID UMP messages, reports jack/buttons, and schedules button-release polling. Mixer controls convert user values into 16-bit SDCA/MBQ dB encodings and maintain software mute mirrors so DAPM and user switches combine correctly. DAPM events drive FU mutes and PDE PS0/PS3 transitions.

State and persistence: `rt712_sdca_priv` tracks regmaps, two possible components, hardware/version IDs, DMIC-function presence, init flags, jack state, delayed work, calibration/IRQ locks, cached SDCA status, and mute mirrors for jack capture, playback, DMIC, and amp paths. VA/VB init paths persist hibernation or function-status information by clearing status bits and writing `SW_CONFIG1`.

Dependencies and integration: Uses ASoC, SoundWire, SDCA helpers, runtime PM, regmap, workqueues, `sdca_device_quirk_match()`, and the bus wrapper. DAI names are `rt712-sdca-aif1`, `aif2`, and optionally `aif3`; component controls expose FU05/FU0F/FU44 and optional FU06/FU1E paths.

Risks and test signals: Key risks are hardware-version branching, ACPI smart-mic mismatch handling, RT713 speaker exclusion, function-status clearing, GE/HID button owner differences between VA/VB, and unsupported AIF3 on VA. Tests should cover RT712/713/716/717 IDs, VA/VB init, smart-mic quirk present/absent, jack and button interrupts, speaker routes, DAPM mute combinations, all supported rates, suspend/resume, and logs for calibration or version mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.h

Purpose: Defines the main RT712 SDCA private state, control metadata, vendor/register constants, SDCA function/entity/control IDs, hardware IDs, version IDs, sample-rate encodings, and exported core APIs.

Important APIs/types: `struct rt712_sdca_priv` holds normal and MBQ regmaps, main and DMIC components, slave, bus params, init flags, jack work/state, calibration and IRQ locks, cached SDCA interrupt bits, hardware/version IDs, smart-mic presence, and mute mirrors for FU0F, FU1E, and FU05. `struct rt712_dmic_kctrl_priv` supports variable-count DMIC controls. Exported APIs are `rt712_sdca_init()`, `rt712_sdca_io_init()`, and `rt712_sdca_jack_detect()`.

Control/data model: The header defines vendor index spaces for analog, calibration, ultrasound, IMS/DRE, HDA legacy, and amp control. SDCA definitions cover jack codec, mic array, HID, amp functions, FUs, PDEs, clock selectors, terminals, function-status fields, and sample-frequency indices. Hardware enums distinguish RT712/713/716/717 and VA/VB behavior.

State and persistence: The private state captures software-owned mute and initialization data that must survive runtime PM, delayed work, and SoundWire reattachment. `FUNCTION_NEEDS_INITIALIZATION`, `FUNCTION_HAS_BEEN_RESET`, and `FUNCTION_BUSY` define how VB init decides which function blocks require reprogramming.

Dependencies and integration: Included by both the main RT712 SDCA core and standalone DMIC driver. It pulls in PM, regmap, SoundWire, ASoC, and workqueue types, and its constants are consumed by regmap defaults in the SDW/DMIC headers.

Risks and test signals: The header is a central ABI between multiple C files; changing structure layout or constants can break both integrated and standalone DMIC drivers. Test signals include build coverage of all RT712 variants, correct device ID/version decoding, valid SDCA addresses in regmap logs, smart-mic quirk behavior, and ALSA control readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.c

Purpose: Provides the SoundWire bus driver for RT715/RT714 SDCA microphone-array codecs. It defines regmaps and defaults, SoundWire source-port properties, attach-time initialization, and PM cache handling for the RT715 SDCA core implemented in neighboring files outside this subset.

Important APIs and functions: `rt715_sdca_sdw_probe()` initializes MBQ and SDCA regmaps and calls `rt715_sdca_init()`. `rt715_sdca_read_prop()` advertises source ports 4 and 6, no sink ports, paging support, and clock-stop timeout. `rt715_sdca_update_status()` calls `rt715_sdca_io_init()` on first attached status. `rt715_dev_suspend()` and `rt715_dev_resume()` control regcache cache-only/dirty state and synchronize selected SDCA/MBQ ranges after resume.

Control flow: Probe binds SDW IDs for parts `0x715` and `0x714`. On attach, the core initialization is run unless `hw_init` is already true. Suspend marks both regmaps cache-only and dirty. Resume exits early before first hardware init, otherwise waits for SoundWire enumeration when `unattach_request` is set, clears that flag, and syncs the SDCA control range plus MBQ vendor/control ranges.

State and persistence: The bus file depends on `struct rt715_sdca_priv` fields `regmap`, `mbq_regmap`, `hw_init`, and `first_hw_init` from `rt715-sdca.h`. Register defaults and regcache synchronization preserve mic-array mute/volume/VAD control state over runtime and system PM.

Dependencies and integration: Uses SoundWire slave ops, regmap SoundWire/MBQ helpers, runtime PM, ASoC, and `rt715-sdca.h`/`rt715-sdca-sdw.h`. Driver name is `rt715-sdca`; license metadata says GPL v2.

Risks and test signals: There is no interrupt callback in this wrapper, so behavior depends on polling/control paths in the core. Risks include incomplete cache sync ranges, source port property mismatches, and resume timeout after unattach. Tests should verify port discovery, capture path registration, RT714/RT715 matching, autosuspend/resume, unattach/reattach initialization, and regcache replay of VAD/mic controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.h

Purpose: Provides RT715 SDCA regmap default tables used by the SoundWire bus driver for RT714/RT715 microphone-array codecs.

Important APIs/types: `rt715_reg_defaults_sdca[]` seeds 8-bit SDCA/control defaults for HDA-like windows, vendor registers, clock selection, ADC FU mute controls, SMPU trigger status, and VAD-related controls. `rt715_mbq_reg_defaults_sdca[]` seeds 16-bit MBQ defaults for vendor blocks and mic-array volume/gain controls across ADC and DMIC channels.

Control flow: Data-only header consumed by `rt715-sdca-sdw.c` regmap configs. The defaults become the cached baseline used before attach and during suspend; resume synchronizes selected portions of these maps back to hardware.

State and persistence: Defaults establish muted ADC/DMIC FUs, zeroed volumes/gains, and initial VAD/SMPU control values. They are critical for preserving known-safe mic capture state through SoundWire enumeration and PM transitions.

Dependencies and integration: Includes SoundWire register macros and relies on function/entity/channel constants from `rt715-sdca.h`, which the C file includes before this header. The address sets must match readable and volatile filters in the bus wrapper.

Risks and test signals: Duplicate or stale defaults can make cache sync replay unexpected mute/volume settings. Test signals include regmap registration without range warnings, capture mixer default readback, VAD status reads, suspend/resume cache replay, and comparison with hardware reset defaults for RT714 and RT715.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt715-sdca-sdw.h -->
