# Research: subset-b-004758

Grouped source research for the ath5k/ath6kl wireless driver subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reset.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reset.c

Purpose: Implements ath5k hardware reset, wake, hold, power-mode, core-clock, sleep-clock, initval-tweak, and EEPROM-commit handling for AR5210/AR5211/AR5212-era Atheros MAC/PHY/radio combinations.

Important APIs and functions: `ath5k_hw_register_timeout()` is the generic register polling helper. `ath5k_hw_htoclock()` and `ath5k_hw_clocktoh()` convert microseconds to the current hardware clock domain. `ath5k_hw_on_hold()` places PCI devices into warm reset for low-power hold. `ath5k_hw_nic_wakeup()` wakes and warm-resets MAC/PHY, programs PLL and PHY mode for a channel, and handles AHB reset through `ath5k_hw_wisoc_reset()`. `ath5k_hw_reset()` is the full reinitialization entry point used after channel changes and hardware trouble. Static helpers include `ath5k_hw_init_core_clock()`, `ath5k_hw_set_sleep_clock()`, `ath5k_hw_nic_reset()`, `ath5k_hw_set_power_mode()`, `ath5k_hw_tweak_initval_settings()`, and `ath5k_hw_commit_eeprom_settings()`.

Control flow: Full reset validates channel mode against MAC generation, optionally attempts fast channel switching for RF2413/RF5413, saves sequence counters, AR5211 TSF, LED state, and GPIO state, applies pending RF gain calibration, wakes and warm-resets the NIC, enables PHY access, writes initvals, initializes clock registers, applies chipset-specific tweaks, commits EEPROM-derived analog parameters, restores preserved state, initializes PCU, PHY, QCU/DCU queues, DMA, optional 32 kHz sleep clock, disables beacons, and resets TSF. Wakeup first forces `AR5K_PM_AWAKE`, performs MAC/baseband reset with PCIe-specific reset masking, clears reset state, then derives PHY mode/PLL/turbo bits from band, modulation, radio type, and bandwidth mode.

State and persistence: Mutates hardware registers extensively and updates runtime fields such as `common->clockrate`, transmit power CCK/OFDM deltas, `ah_current_channel`-dependent clock programming, sleep-clock state, and preserved/restored TSF, sequence, GPIO, and LED register values. EEPROM data is not changed, but EEPROM-derived calibration settings are copied into registers and driver TX power state. No durable host persistence exists.

Dependencies and integration points: Depends on `ath5k.h`, `reg.h`, `debug.h`, PCI helpers, platform-device AHB reset addresses, initvals, PHY, EEPROM, ANI, queue, DMA, PCU, GPIO, and RF gain helpers. It integrates with mac80211 channel/configuration changes, attach/start recovery paths, AHB and PCI bus variants, and the rest of ath5k's PHY/radio initialization pipeline.

Risks: Register sequences are chipset- and revision-sensitive; wrong reset flags can hang PCIe devices or leave AHB MAC/baseband in reset. Sleep-clock enablement is deliberately disabled by default because it can destabilize some hardware. Fast channel change fallback must not leave partial PHY state. TSF restore on AR5211 trades reset continuity against power-save behavior. EEPROM-derived writes assume valid mode indexes and revision gates.

Test signals: Exercise cold start, warm reset, recovery reset, fast channel change success/fallback, 2 GHz/5 GHz and 5/10/20/40 MHz modes, PCI and AHB devices, invalid channel modes, power-mode wake failures, TSF/sequence preservation, EEPROM calibration application, and 32 kHz sleep-clock opt-in behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfbuffer.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfbuffer.h

Purpose: Defines ath5k RF buffer data structures, RF analog-register field maps, register indexes, and static RF bank initialization tables for supported RF chips.

Important APIs and types: `struct ath5k_ini_rfbuffer` describes one RF bank/control-register tuple with mode-specific values for A/XR, B, and G. `struct ath5k_rfb_field` describes bit length, position, and column shift in the packed RF bank stream. `struct ath5k_rf_reg` maps a logical RF register index to a bank and packed field. `enum ath5k_rf_regs_idx` names logical RF fields such as turbo, OB/DB bias, XPD, PWD bits, gain, wait, and delay controls. Static tables include `rf_regs_5111`, `rf_regs_5112`, `rf_regs_5112a`, `rf_regs_2413`, `rf_regs_2316`, `rf_regs_5413`, `rf_regs_2425`, and RF buffer defaults `rfb_5111`, `rfb_5112`, `rfb_5112a`, `rfb_2413`, `rfb_2316`, `rfb_5413`, `rfb_2425`, `rfb_2317`, and `rfb_2417`.

Control flow: This header has no executable control flow. Runtime RF initialization code selects a table by radio revision, copies the mode-specific RF bank words, edits selected packed fields using the register maps, writes bank data through RF buffer registers, and triggers hardware apply through the corresponding control register.

State and persistence: Owns immutable static calibration defaults and packed-field metadata. It does not mutate state directly, but consumers use these values to populate `ah->ah_rf_banks` and hardware RF buffer registers. The constants encode a hardware ABI for analog front-end programming.

Dependencies and integration points: Consumed by ath5k PHY/RF register initialization code and tied to register definitions in `reg.h`, EEPROM calibration values, channel mode selection, RF gain optimization, and reset/PHY initialization. It bridges logical driver concepts to packed RF bank layouts that differ by RF5111, RF5112, RF2413, RF2316/2317, RF5413, RF2425/2417 families.

Risks: Bit positions and bank layouts are extremely hardware-specific; a one-bit error can corrupt radio analog programming. Several tables intentionally share defaults with comments noting TODOs for 2317/2417 differences, so later edits must preserve known variant quirks. Static header definitions increase compile-time coupling and can produce duplicate-data bloat if included outside intended C files.

Test signals: Verify RF bank programming on every supported radio family, band and mode transitions, turbo/half/quarter-rate behavior, EEPROM overrides of OB/DB/XPD/gain fields, RF gain calibration interaction, and regression tests for hardware that uses the 2317/2417 alternate tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfgain.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfgain.h

Purpose: Provides static RF gain initialization tables and gain-optimization ladders used by ath5k PHY/RF code to program analog gain behavior.

Important APIs and types: `struct ath5k_ini_rfgain` maps an RF gain register address to 5 GHz and 2 GHz values. Static tables `rfgain_5111`, `rfgain_5112`, `rfgain_2413`, `rfgain_2316`, `rfgain_5413`, and `rfgain_2425` provide mode-specific 64-entry gain defaults. `struct ath5k_gain_opt_step` stores adjustment parameters and resulting gain delta. `struct ath5k_gain_opt` stores a default step, count, and optimization ladder. `rfgain_opt_5111` and `rfgain_opt_5112` define dynamic gain adjustment steps for older RF chips. Macros define adjustment thresholds and `AR5K_GAIN_CHECK_ADJUST()`.

Control flow: The header itself is static data. Runtime code selects an initial gain table by RF chip and frequency band, writes gain registers, then uses the optimization ladder to move between gain steps when measured gain crosses low/high thresholds. The ladder parameters correspond to RF buffer fields such as PWD and mixgain controls plus PHY clip settings.

State and persistence: Owns immutable constants. Consumers maintain current gain measurements, low/high thresholds, selected step, and any pending RF bank edits. No durable persistence exists; values are re-applied during reset/PHY initialization.

Dependencies and integration points: Depends on RF gain register macros such as `AR5K_RF_GAIN()`, RF buffer field editing from `rfbuffer.h`, PHY calibration paths, channel band selection, and reset-time gain calibration in `reset.c`. It is most important for RF5111/RF5112 dynamic gain behavior and newer chips' initialization defaults.

Risks: Gain values are analog calibration constants; wrong table selection causes poor sensitivity, transmit quality, or unstable calibration. Optimization thresholds and step parameters are tuned for specific chip families and can regress fringe RF performance. Because tables are static and opaque, tests need hardware signal metrics rather than simple compile checks.

Test signals: Validate RX sensitivity, noise floor, transmit EVM/power, gain calibration convergence, 2 GHz versus 5 GHz table selection, reset-time reprogramming, dynamic gain step transitions under changing RSSI/noise, and no regressions on RF5111/RF5112 devices that use optimization ladders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfgain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfkill.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfkill.c

Purpose: Implements ath5k hardware rfkill GPIO setup, interrupt toggling, and mac80211/cfg80211 hardware-rfkill state reporting.

Important APIs and functions: `ath5k_rfkill_hw_start()` reads EEPROM rfkill GPIO and polarity, initializes a tasklet, drives the rfkill output to the unblocked state, and enables GPIO interrupt if the EEPROM header advertises rfkill. `ath5k_rfkill_hw_stop()` disables the interrupt, kills the tasklet, and drives the GPIO to the blocked state so the Wi-Fi LED turns off. Static helpers drive GPIO output high/low according to polarity, configure GPIO interrupt edge, read blocked state, and report changes through `wiphy_rfkill_set_hw_state()`.

Control flow: Start copies EEPROM config into `ah->rf_kill`, sets up `toggleq`, disables rfkill by writing the inverse polarity, then arms GPIO interrupt edge detection. On GPIO interrupt, the tasklet reads current GPIO state and reports blocked/unblocked state to the wiphy. Stop disables interrupt edge handling, synchronously kills the tasklet, and asserts rfkill.

State and persistence: Mutates `ah->rf_kill.gpio`, `ah->rf_kill.polarity`, and the tasklet lifecycle. It changes hardware GPIO direction, output value, and interrupt polarity. The EEPROM configuration is persistent but only read here; runtime rfkill state is reflected to cfg80211/rfkill core.

Dependencies and integration points: Depends on ath5k GPIO helpers, EEPROM capability macros, tasklet infrastructure, `struct ieee80211_hw`/wiphy rfkill integration, and driver interrupt handling that schedules `toggleq`.

Risks: The code comments that configuring GPIO input can disable rfkill on some hardware, so state reads avoid reconfiguring direction in `ath5k_is_rfkill_set()`. Wrong polarity can invert regulatory/user-visible block state. Interrupt edge selection uses current GPIO state and must be updated when enabling/disabling to catch toggles reliably.

Test signals: Toggle the physical rfkill switch, verify cfg80211/rfkill state changes, confirm no toggles after stop, test EEPROM absent/present rfkill headers, validate polarity on devices with active-high and active-low switches, and confirm LED/off behavior on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/sysfs.c

Purpose: Exposes selected ath5k ANI tuning and limit values through a device sysfs attribute group named `ani`.

Important APIs and functions: Macros `SIMPLE_SHOW_STORE()` and `SIMPLE_SHOW()` generate sysfs show/store handlers. Writable attributes include `ani_mode`, `noise_immunity_level`, `spur_level`, `firstep_level`, `ofdm_weak_signal_detection`, and `cck_weak_signal_detection`; read-only attributes include maximum noise immunity, spur, and firstep levels. `ath5k_sysfs_register()` creates the group and `ath5k_sysfs_unregister()` removes it.

Control flow: A show handler obtains `struct ieee80211_hw` via `dev_get_drvdata()`, resolves `struct ath5k_hw`, and emits the current ANI value. A store handler parses decimal input with `kstrtoint()` and calls the corresponding ANI setter, returning the input byte count on success. Registration creates the `ani` group under the device kobject and logs failure through `ATH5K_ERR`.

State and persistence: Mutates in-memory ANI state and hardware ANI settings through `ath5k_ani_*` setters. Sysfs changes are runtime-only and do not persist across reloads or reset unless higher-level ANI initialization reuses the state.

Dependencies and integration points: Depends on Linux device/sysfs APIs, mac80211 device private data, ANI state in `ah->ani_state`, ANI setters from ath5k, and constants such as `ATH5K_ANI_MAX_NOISE_IMM_LVL`. It is integrated during device registration/teardown.

Risks: Store handlers do not validate ranges themselves, relying on ANI setters to clamp or reject values. Concurrent sysfs writes and driver reset/ANI recalibration can race at the semantic level. Exposing low-level tuning can degrade RF performance if users write unsuitable values.

Test signals: Register/unregister group on probe/remove, read each attribute, write valid and invalid integers, verify setters are invoked and hardware behavior changes, confirm parse errors return negative status, and ensure group removal prevents use-after-free during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/trace.h

Purpose: Defines optional ath5k ftrace tracepoints for RX, TX enqueue, and TX completion events, with no-op inline fallbacks when tracing is disabled.

Important APIs and events: `TRACE_EVENT(ath5k_rx)` records driver private pointer, skb address, and a dynamic copy of the received frame. `TRACE_EVENT(ath5k_tx)` records private pointer, skb address, queue number, and a dynamic copy of the transmitted frame. `TRACE_EVENT(ath5k_tx_complete)` records private pointer, skb address, queue number, status, RSSI, and antenna. When `CONFIG_ATH5K_TRACER` is not enabled, `TRACE_EVENT` is redefined to static inline `trace_*` stubs.

Control flow: Including code calls generated `trace_ath5k_*()` helpers at datapath points. If tracing is enabled, tracepoint infrastructure captures metadata and optional frame bytes; otherwise calls compile away to no-op inline functions. The bottom include of `<trace/define_trace.h>` materializes tracepoints when the header is included by the trace definition translation unit.

State and persistence: No driver state is owned. Trace buffers are managed by the kernel tracing subsystem and are transient. The dynamic arrays copy skb payload bytes at trace time.

Dependencies and integration points: Depends on `<linux/tracepoint.h>`, `struct sk_buff`, ath5k TX queue/status types, `TRACE_SYSTEM ath5k`, and build configuration `CONFIG_ATH5K_TRACER`. It integrates with trace-cmd/perf/ftrace and ath5k RX/TX datapath instrumentation.

Risks: Capturing full frame bytes can expose packet contents and add overhead when tracepoints are enabled. The fallback macro must keep call signatures compatible with enabled tracepoints. `TRACE_INCLUDE_PATH .` assumes trace build include paths are set correctly.

Test signals: Build with and without `CONFIG_ATH5K_TRACER`, enable each tracepoint under ftrace, verify RX/TX/TX-complete records include expected queue/status metadata, confirm no unresolved trace symbols in disabled builds, and measure datapath overhead when tracepoints are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Kconfig

Purpose: Defines Kconfig options for the ath6kl core, SDIO bus driver, USB bus driver, debug support, event tracing, and optional regulatory-domain firmware control.

Important symbols: `ATH6KL` is the core tristate and depends on `CFG80211`. `ATH6KL_SDIO` depends on `ATH6KL` and `MMC`. `ATH6KL_USB` depends on `ATH6KL` and `USB`. `ATH6KL_DEBUG` enables debug messages/debugfs. `ATH6KL_TRACING` depends on `EVENT_TRACING`. `ATH6KL_REGDOMAIN` depends on `CFG80211_CERTIFICATION_ONUS` and allows firmware regdomain changes.

Control flow: Kconfig dependency selection determines which modules are built and which optional code paths are compiled. The core can be built without a bus driver, but real hardware requires SDIO or USB. Debug, tracing, and regulatory paths gate code in other ath6kl files.

State and persistence: No runtime state. The selected configuration persists in the kernel build configuration and module set.

Dependencies and integration points: Integrates with the kernel wireless menu, cfg80211, MMC, USB, event tracing, debugfs/debug message code, and regulatory certification policy. Module names advertised in help text align with Makefile outputs `ath6kl_core`, `ath6kl_sdio`, and `ath6kl_usb`.

Risks: Enabling `ATH6KL_REGDOMAIN` carries explicit regulatory responsibility. Building core without a transport driver produces no usable device support. Debug/tracing options increase diagnostic surface and may add overhead or expose sensitive packet/control data when enabled.

Test signals: Compile matrix for built-in/module combinations of core, SDIO, USB, debug, tracing, and regdomain; verify dependency enforcement; modprobe expected module names; and confirm unsupported AR6001/AR6002 expectations remain documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Makefile

Purpose: Lists ath6kl object composition for the core module and SDIO/USB transport modules.

Important build targets: `obj-$(CONFIG_ATH6KL) += ath6kl_core.o` builds the core from debug, HIF, HTC mailbox/pipe, BMI, cfg80211, init, main, txrx, WMI, core, and recovery objects. `ath6kl_core-$(CONFIG_NL80211_TESTMODE) += testmode.o` and `ath6kl_core-$(CONFIG_ATH6KL_TRACING) += trace.o` add optional objects. `obj-$(CONFIG_ATH6KL_SDIO) += ath6kl_sdio.o` builds `sdio.o`; `obj-$(CONFIG_ATH6KL_USB) += ath6kl_usb.o` builds `usb.o`. `CFLAGS_trace.o := -I$(src)` supports trace header discovery.

Control flow: Kernel kbuild expands objects according to Kconfig selections and links per-module object lists. Transport modules depend on the core module APIs but are built separately.

State and persistence: No runtime state. It defines build-time module composition and object ordering.

Dependencies and integration points: Integrates with Kbuild, Kconfig symbols, trace generation, nl80211 testmode, SDIO/USB transport implementations, and the shared ath6kl core exported symbols.

Risks: Omitting an object breaks link-time symbol resolution; changing optional object gates can accidentally expose testmode/tracing code in production builds. Trace include flags must stay aligned with `trace.h` include path assumptions.

Test signals: Build every Kconfig combination, verify module symbol linkage between core and transports, ensure testmode and trace objects appear only under their configs, and run modpost without unresolved exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.c

Purpose: Implements the ath6kl Bootloader Messaging Interface used before firmware start to query target info, read/write target memory and registers, execute target code, set application start, and download compressed firmware data.

Important APIs and functions: `ath6kl_bmi_init()` allocates the command buffer based on HIF-provided `max_data_size`; `ath6kl_bmi_cleanup()` frees it; `ath6kl_bmi_reset()` clears the done flag. Command APIs include `ath6kl_bmi_done()`, `ath6kl_bmi_get_target_info()`, `ath6kl_bmi_read()`, `ath6kl_bmi_write()`, `ath6kl_bmi_execute()`, `ath6kl_bmi_set_app_start()`, `ath6kl_bmi_reg_read()`, `ath6kl_bmi_reg_write()`, `ath6kl_bmi_lz_stream_start()`, `ath6kl_bmi_lz_data()`, and `ath6kl_bmi_fast_download()`.

Control flow: Every command checks `ar->bmi.done_sent` and refuses access after `BMI_DONE`. Requests are serialized into `ar->bmi.cmd_buf` with command ID, address/length/parameters, then sent through `ath6kl_hif_bmi_write()`; commands with responses read through `ath6kl_hif_bmi_read()`. Memory reads/writes split transfers by `max_data_size`. Writes pad short unaligned final chunks to 4 bytes. Fast download starts an LZ stream, sends aligned compressed data, sends a padded final word if needed, then starts a zero-address stream to flush target caches.

State and persistence: Mutates `ar->bmi.done_sent`, `cmd_buf`, `max_cmd_size`, and target memory/register/application-start state through BMI commands. Host buffer state is runtime-only; target-side changes persist until target reset or firmware takeover.

Dependencies and integration points: Depends on `core.h`, `hif-ops.h`, `target.h`, debug helpers, HIF transport BMI read/write operations, and target boot ROM protocol definitions from `bmi.h`. Called during `ath6kl_core_init()` and firmware loading before WMI/HTC operation.

Risks: The code uses host-endian command fields as expected by the target/HIF path; mismatch would break boot. Incorrect `max_data_size` can overflow the fixed local `aligned_buf` or violate command-size checks. After `BMI_DONE`, commands correctly return `-EACCES`; callers must order firmware setup before done. There is a subtle write-loop behavior where padding increases `len_remain`, so accounting depends on padded target write semantics.

Test signals: Boot AR6003/AR6004 over SDIO and USB, target-info old/new sentinel formats, memory read/write chunk boundaries, unaligned write and fast-download tails, register read/write, execute return parameter, command rejection after BMI done, allocation failure, and HIF error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.h

Purpose: Documents and declares the ath6kl Bootloader Messaging Interface protocol, command IDs, target-info structure, HI-item helpers, and BMI function prototypes.

Important APIs and definitions: Command IDs include `BMI_DONE`, `BMI_READ_MEMORY`, `BMI_WRITE_MEMORY`, `BMI_EXECUTE`, `BMI_SET_APP_START`, SOC register read/write, target info, ROM patch commands, and LZ stream/data. `TARGET_VERSION_SENTINAL`, `TARGET_TYPE_AR6003`, and `TARGET_TYPE_AR6004` identify target-info behavior. `struct ath6kl_bmi_target_info` is a packed little-endian byte-count/version/type response. Macros `ath6kl_bmi_write_hi32()` and `ath6kl_bmi_read_hi32()` resolve host-interest item addresses and perform little-endian 32-bit BMI access.

Control flow: The comments define request/response payload formats used by `bmi.c`. The HI helper macros call `ath6kl_get_hi_item_addr()`, then perform BMI memory reads/writes for firmware boot-time configuration.

State and persistence: No state is owned in the header. It defines the protocol that mutates target bootloader memory/register state before firmware starts. `BMI_DONE` marks the end of the bootloader access window.

Dependencies and integration points: Depends on `struct ath6kl`, target HI item address lookup, little-endian conversion helpers, and implementations in `bmi.c`. Integrated with firmware download, board/OTP/patch setup, and target bootstrapping.

Risks: Command IDs and struct layout are firmware ABI; changes must remain target-ROM compatible. The misspelled `TARGET_VERSION_SENTINAL` is part of local API spelling and should not be casually renamed. HI helper macros evaluate arguments in expression context and rely on pointer type checking tricks.

Test signals: Compile BMI users, validate packed struct size, read/write HI items on target boot, handle old and new target-info responses, and ensure every declared command prototype links to `bmi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.c

Purpose: Implements ath6kl's cfg80211/nl80211 integration: wiphy capabilities, virtual interface lifecycle, station/IBSS/AP/P2P operations, scanning and scheduled scanning, security keys, PMKSA, station statistics, management TX, remain-on-channel, WoW/deep-sleep/cut-power suspend, regulatory notification, and ethtool stats.

Important APIs and functions: The `ath6kl_cfg80211_ops` table wires cfg80211 callbacks to this file. Public event/API entry points include `ath6kl_interface_add()`, `ath6kl_cfg80211_connect_event()`, `ath6kl_cfg80211_disconnect_event()`, `ath6kl_cfg80211_scan_complete_event()`, `ath6kl_cfg80211_ch_switch_notify()`, `ath6kl_cfg80211_tkip_micerr_event()`, `ath6kl_cfg80211_suspend()`, `ath6kl_cfg80211_resume()`, `ath6kl_cfg80211_stop()`, `ath6kl_cfg80211_stop_all()`, `ath6kl_cfg80211_vif_cleanup()`, `ath6kl_cfg80211_init()`, `ath6kl_cfg80211_cleanup()`, `ath6kl_cfg80211_create()`, and `ath6kl_cfg80211_destroy()`. Static helpers translate WPA/auth/cipher/key management, app IEs, interface types, BSS entries, WOW patterns, HT caps, AP beacon/RSN settings, and station rates.

Control flow: User cfg80211 operations validate WMI/WLAN readiness, update per-vif driver state, and issue WMI commands to firmware. Connect disables scheduled scan, serializes through `ar->sem`, drains pending control commands, programs assoc IEs and crypto/auth state, handles reconnect or disconnect of same SSID, configures BSS filtering/listen interval/background scan, sends `ath6kl_wmi_connect_cmd()`, and starts a disconnect timer when WPA PSK offload is absent. Firmware connect/disconnect events are converted back to cfg80211 connect, roam, IBSS, and disconnect notifications. Scan configures probed SSIDs, app IEs, optional channel list, starts WMI scan, and completes through scan events. AP start builds a firmware profile from beacon settings, crypto, HT, inactivity timeout, hidden SSID, and optional RSN capability override before committing the profile. Suspend dispatches to WOW, deep sleep, or cut-power flows and aborts outstanding scans.

State and persistence: Mutates `struct ath6kl` state (`state`, `flag`, `connect_ctrl_flags`, `avail_idx_map`, `num_vif`, `ibss_if_active`, `tx_pwr`, firmware capabilities use, recovery state) and per-vif state (`sme_state`, `flags`, `ssid`, `req_bssid`, `bssid`, `ch_hint`, `nw_type`, `next_mode`, crypto fields, keys, WEP/AP broadcast key caches, scan request, timers, HT caps, target stats, management IDs, multicast filters, listen/bmiss/bg scan values). Firmware receives persistent runtime configuration until reset, suspend, disconnect, or interface teardown; host state is rebuilt at probe.

Dependencies and integration points: Depends on cfg80211/mac80211 wireless structures, netdevice and ethtool APIs, WMI command/event layer, HIF PM callbacks, recovery, testmode, aggregation, target statistics, firmware capability flags, timers, wait queues, RTNL/wiphy locking, and IPv4 address data for ARP offload. It is the main boundary between Linux wireless userspace and ath6kl firmware.

Risks: State transitions are complex and shared across firmware events, user requests, suspend/resume, and recovery. Some list traversals note missing `list_lock` because callees sleep. WOW resume can occur from RX path due to SDIO wake behavior, which is explicitly called out as needing rework. IE filtering must avoid malformed element overreads. AP power-save queues and management TX require correct locking and PVB updates. Firmware capability gates such as RSN-cap override, scheduled scan, multicast WOW filter, and regdomain support must match actual firmware.

Test signals: Cover station connect/reconnect/failure/roam/disconnect, WPA/WPA2/WEP/TKIP/CCMP/SMS4 keys, scan and scheduled scan with match sets/RSSI thresholds, IBSS join/leave, AP/P2P GO start/change/stop, station authorize/deauth, remain-on-channel and management TX status/queueing, WoW user/default patterns, deep sleep and cut power suspend/resume, regulatory cell hints, HT capability gating, ethtool stats, vif add/delete/change, and recovery stop paths with outstanding scans and connects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.h

Purpose: Declares ath6kl cfg80211 lifecycle, event notification, interface, and suspend/resume APIs shared between core, WMI event handling, and transport PM code.

Important APIs and types: `enum ath6kl_cfg_suspend_mode` defines `ATH6KL_CFG_SUSPEND_DEEPSLEEP`, `ATH6KL_CFG_SUSPEND_CUTPOWER`, and `ATH6KL_CFG_SUSPEND_WOW`. Prototypes cover interface creation, channel-switch notification, scan completion, connect/disconnect events, TKIP MIC failure notification, suspend/resume, vif cleanup/stop, cfg80211 init/cleanup, and wiphy-backed core create/destroy.

Control flow and integration: WMI event paths call the event notification functions to inform cfg80211. Core initialization calls create/init/interface-add and cleanup/destroy during teardown. HIF PM code calls suspend/resume with a selected suspend mode and optional WoWLAN configuration.

State and persistence: Header owns no state. Its functions mutate ath6kl core state, per-vif state, wiphy registration, and firmware PM/connect/scan state.

Dependencies: Requires ath6kl core types, cfg80211 types such as `wireless_dev` and `cfg80211_wowlan`, WMI network/PHY enums, and implementations in `cfg80211.c`.

Risks: Prototype drift breaks cross-file event and PM integration. Suspend mode enum values are part of internal policy decisions between HIF and cfg80211 code, so new modes need all call sites updated.

Test signals: Build all ath6kl objects, exercise WMI connect/disconnect/scan/MIC/channel events, interface add/remove, and each suspend mode through SDIO/USB PM hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/cfg80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/common.h

Purpose: Provides ath6kl shared constants, data-path sizing formulas, LLC/SNAP header layout, crypto enum, common forward declarations, and the buffer allocation prototype.

Important APIs and types: `ATH6KL_MAX_IE` caps IE storage. `ath6kl_printk()` is the printf-annotated logging helper. `ATH6KL_ABI_VERSION` documents host/firmware ABI version. Signal quality metric indexes identify SNR/RSSI/all metrics. `WMI_MAX_TX_DATA_FRAME_LENGTH` and `WMI_MAX_AMSDU_RX_DATA_FRAME_LENGTH` compute WMI data buffer sizes including WMI, Ethernet, and LLC/SNAP headers. `EPPING_ALIGNMENT_PAD` computes HTC frame alignment padding. `struct ath6kl_llc_snap_hdr` is packed DSAP/SSAP/control/OUI/ethertype layout. `enum ath6kl_crypto_type` maps NONE/WEP/TKIP/AES/WAPI bit values. `ath6kl_buf_alloc()` allocates skb buffers.

Control flow: No executable flow is defined. Macros are evaluated by TX/RX and WMI paths for buffer sizing and crypto selection.

State and persistence: No state. Constants form part of the host/firmware interface contract and data-path memory layout.

Dependencies and integration points: Includes `linux/netdevice.h` and references WMI data headers, Ethernet headers, HTC frame headers, HTC credit distribution types, ath6kl core types, and HT capability structures. Used widely by core, WMI, TX/RX, cfg80211, and HTC code.

Risks: Buffer length macros must match firmware frame format; underestimation can overflow or truncate frames, while ABI version mismatches can hide incompatible firmware changes. Crypto enum values are consumed by WMI firmware commands and must not be renumbered casually.

Test signals: Compile consumers, validate TX/RX maximum frame handling, AMSDU receive buffer sizing, WMI crypto command values, ABI compatibility checks, and skb allocation behavior at maximum sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.c

Purpose: Provides ath6kl module parameters, core object creation/destruction, hardware/firmware initialization, HTC/WMI/BMI setup, cfg80211 registration, initial netdev creation, recovery initialization, and core cleanup.

Important APIs and functions: Module parameters include `debug_mask`, `suspend_mode`, `wow_mode`, `uart_debug`, `uart_rate`, `ath6kl_p2p`, `testmode`, `recovery_enable`, and `heart_beat_poll`. Exported callbacks `ath6kl_core_tx_complete()` and `ath6kl_core_rx_complete()` bridge HIF completions into HTC. `ath6kl_core_create()` allocates the wiphy-backed `struct ath6kl` and initializes locks, queues, station aggregation state, defaults, and lists. `ath6kl_core_init()` attaches HTC transport, creates a workqueue, initializes BMI, powers on hardware, queries target info, loads firmware, starts WMI/HTC/hardware, registers cfg80211/debugfs, creates the initial station interface, and enables recovery. `ath6kl_core_cleanup()` and `ath6kl_core_destroy()` release resources.

Control flow: Creation allocates cfg80211/wiphy private state, sets defaults, and allocates per-station aggregation contexts. Initialization chooses mailbox or pipe HTC ops, allocates a single-thread workqueue, initializes BMI, powers on target, reads BMI target info, selects hardware params, creates HTC target, fetches firmware, applies backward-compatible firmware capability bits, initializes WMI and queues/buffers/cookies, applies module-parameter policy, starts hardware, refills control/data RX endpoints, registers wiphy, initializes debugfs, marks all vif indexes available, and creates `wlan%d` station interface under RTNL and wiphy locks. Error paths unwind in reverse through WMI, HTC, power, BMI, and workqueue cleanup.

State and persistence: Mutates module-global parameter variables and many `struct ath6kl` fields: target version/type, wiphy hw version, firmware capabilities, WMI flags, AC stream priorities, config flags, suspend modes, UART rate, first boot flag, vif index map, recovery settings, station aggregation contexts, power state, queues, waitqueue, semaphore, and list heads. Firmware blobs are retained in memory until cleanup. No durable persistence exists outside module parameters and loaded firmware files.

Dependencies and integration points: Depends on cfg80211 creation/init, BMI, HIF power and transport, HTC mailbox/pipe ops, WMI, firmware/init code, debug/debugfs, recovery, RX buffer management, cookie management, netdevice registration, and exported symbols consumed by SDIO/USB HIF modules.

Risks: Error handling has a noted FIXME that firmware blobs are not freed on some init failures below fetch. Initialization order is strict: BMI before firmware start, WMI after firmware capabilities, cfg80211 after hardware start. Recovery heartbeat depends on firmware capability. Partial netdev/wiphy registration failures need careful cleanup to avoid leaked registrations or powered hardware. Per-station aggregation allocation failure calls destroy on a partially initialized object.

Test signals: Probe success over SDIO and USB, invalid HTC type, workqueue/BMI/power/target-info/firmware/WMI/hardware/cfg80211/debugfs/interface allocation failures, module parameter combinations, initial interface creation, recovery enabled/disabled and heartbeat polling, cleanup after full and partial init, and HIF TX/RX completion routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.c -->
