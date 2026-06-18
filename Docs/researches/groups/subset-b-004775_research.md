<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c

Purpose: Implements the carl9170 receive side for firmware command traps, USB RX stream framing, 802.11 MPDU status decoding, power-save beacon observation, and BlockAck/BAR side effects.

Important APIs/types/functions: Exports `carl9170_rx()` and `carl9170_handle_command_response()`. Internal entry points include `carl9170_rx_stream()`, `__carl9170_rx()`, `carl9170_rx_untie_cmds()`, `carl9170_rx_untie_data()`, `carl9170_rx_mac_status()`, `carl9170_rx_phy_status()`, `carl9170_ps_beacon()`, and `carl9170_ba_check()`. It consumes `struct ar9170_rx_head`, `struct ar9170_rx_phystatus`, `struct ar9170_rx_macstatus`, and `struct carl9170_rsp`.

Control flow: USB completions pass buffers to `carl9170_rx()`. Stream-enabled firmware is split by `AR9170_RX_STREAM_TAG`; non-stream frames are classified by the repeated `0xffff` command marker. Command traps validate monotonic firmware sequence numbers, dispatch PRETBTT/TXCOMP/WATCHDOG/TEXT/GPIO/BOOT events, and complete synchronous command waiters. Data frames are decoded as single or A-MPDU first/middle/last MPDUs, with PLCP cached for aggregate members, then copied into a fresh skb and delivered through `ieee80211_rx()`.

State and persistence: Updates in-memory driver state only: `cmd_seq`, firmware error counters, power-save timestamps/overrides, `rx_plcp`, `rx_has_plcp`, `ampdu_ref`, RX drop counters, BAR tracking lists, and stream failover skb/missing-byte state. No durable persistence.

Dependencies and integration points: Integrates with mac80211 RX status fields, firmware command protocol, TX status processing, beacon update logic, WPS input reporting, RCU-protected vif/BA lists, and `ath_is_mybeacon()`.

Risks and test signals: Main risks are malformed USB stream repair, sequence loss causing restarts, A-MPDU ordering assumptions, copied skb allocation failures, and status/rate decoding mismatches. Useful signals include RX under load, firmware trap loss logs, FCS/PLCP filter behavior, suspend/restart recovery, PS beacon handling, and BlockAck acknowledgment of BAR frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c

Purpose: Provides carl9170 transmit preparation, queueing, firmware-memory accounting, USB submission scheduling, TX completion processing, A-MPDU aggregation, power-save filtering, BAR tracking, and beacon upload.

Important APIs/types/functions: Exports `carl9170_op_tx()`, `carl9170_tx_scheduler()`, `carl9170_tx_process_status()`, `carl9170_tx_status()`, `carl9170_tx_callback()`, `carl9170_tx_drop()`, `carl9170_tx_janitor()`, `carl9170_update_beacon()`, and skb kref helpers. Core internals include `carl9170_tx_prepare()`, `carl9170_tx_apply_rateset()`, `carl9170_tx_ampdu_queue()`, `carl9170_tx_ampdu()`, `carl9170_tx()`, `carl9170_alloc_dev_space()`, and `carl9170_release_dev_space()`.

Control flow: mac80211 calls `carl9170_op_tx()`, which prepends the firmware superframe, fills encryption, queue, VIF, rate, ERP, and A-MPDU metadata, accounts queue depth, and either enqueues an aggregate TID or direct pending frame. `carl9170_tx()` allocates a firmware memory cookie, moves the skb to the status queue, adds an extra skb reference for USB/status race handling, and submits via `carl9170_usb_tx()`. Firmware TXCOMP traps remove skbs by cookie and queue, fill rate retry counts, and report status to mac80211. USB callbacks drop the pending reference and reschedule if more work exists.

State and persistence: Maintains `tx_stats`, queue stop timestamps, `tx_total_queued`, `tx_total_pending`, firmware memory bitmap/free-block counters, per-TID BA windows and sequence bitmaps, BAR lists, current A-MPDU density/factor, pending beacon skb cache per vif, and delayed janitor state. State is volatile and reset on device restart.

Dependencies and integration points: Depends on mac80211 rate control/status APIs, USB TX callbacks, firmware status cookies, `wlan.h` descriptor layout, `hw.h` register writes for beacon upload, RCU-protected station/vif state, and power-save station blocking.

Risks and test signals: Risks include cookie double-free races, queue wake/stop imbalance, stuck TX requiring restart, strict sequence assumptions in A-MPDU queues, BAR status heuristics, and beacon memory overflow. Test signals are TX under queue pressure, aggregation setup/teardown, firmware TXCOMP correlation, filtered frames for sleeping stations, queue timeout recovery, and beacon generation in AP/IBSS/mesh modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c

Purpose: Implements the USB frontend for AR9170/carl9170 devices: device ID matching, firmware loading, URB pools, command transport, RX/TX completion paths, restart/reset handling, probe/disconnect, and PM resume.

Important APIs/types/functions: Registers `carl9170_driver` through `module_usb_driver()`. Exports driver-facing functions such as `carl9170_exec_cmd()`, `__carl9170_exec_cmd()`, `carl9170_usb_tx()`, `carl9170_usb_open()`, `carl9170_usb_stop()`, `carl9170_usb_restart()`, `carl9170_usb_reset()`, and `carl9170_usb_handle_tx_err()`. Probe/firmware callbacks include `carl9170_usb_probe()`, `carl9170_usb_firmware_step2()`, `carl9170_usb_firmware_finish()`, and `carl9170_usb_disconnect()`.

Control flow: Probe resets the device, allocates `struct ar9170`, validates endpoints, initializes anchors/completions/tasklet state, and asynchronously requests firmware. Firmware finish parses metadata, starts interrupt and bulk RX URBs, uploads firmware by control transfers, waits for boot completion, runs echo test, registers mac80211, then stops until opened. RX bulk completions move URBs to a work anchor and schedule the high-priority tasklet, which calls `carl9170_rx()` and the TX scheduler. TX submissions are anchored in wait/active/error lists; completions either call `carl9170_tx_callback()` or defer failures to tasklet cleanup. Commands use a single in-flight command URB path plus completion waiting in `carl9170_exec_cmd()`.

State and persistence: Maintains USB anchors, URB counters, command response buffers/lengths, boot/load completions, endpoint mode, firmware pointer/parsed metadata, and carl9170 state transitions. No persistent storage beyond firmware image ownership.

Dependencies and integration points: Uses Linux USB core, firmware loader, mac80211 registration, carl9170 firmware command/RX/TX layers, tasklets, completions, and PM callbacks.

Risks and test signals: Risks include command timeouts forcing restarts, RX URB starvation, tasklet/anchor lifetime during disconnect, endpoint shape differences between full/high speed, and reset/resume losing mac80211 state. Test signals are probe with supported IDs, firmware upload and boot response, command echo, RX/TX stress, disconnect during traffic, suspend/resume, and firmware restart recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h

Purpose: Defines the shared carl9170 firmware version constants expected by the driver/firmware build contract.

Important APIs/types/functions: Provides `CARL9170FW_VERSION_YEAR`, `CARL9170FW_VERSION_MONTH`, `CARL9170FW_VERSION_DAY`, and `CARL9170FW_VERSION_GIT`.

Control flow: No executable control flow; consumers include firmware parsing or compatibility checks that compare embedded firmware metadata with driver expectations.

State and persistence: Compile-time constants only. They become part of built objects but no runtime mutable state is held here.

Dependencies and integration points: Tied to `CARL9170FW_NAME` and firmware-loading logic in the carl9170 USB path. It is a shared header guarded by `__CARL9170_SHARED_VERSION_H`.

Risks and test signals: Risk is stale version metadata causing misleading firmware compatibility diagnostics. Test signals are successful firmware parse/upload and any version mismatch logging in carl9170 initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h

Purpose: Describes the shared AR9170 WLAN descriptor, rate, encryption, RX status, TX control, and hardware queue layout used by carl9170 host code and firmware.

Important APIs/types/functions: Defines RX/TX PHY rate constants, encryption algorithm constants, RX status/error bits, TX MAC/PHY control bits, `_carl9170_tx_superdesc`, `_ar9170_tx_hwdesc`, `_carl9170_tx_superframe`, `ar9170_rx_head`, `ar9170_rx_phystatus`, `ar9170_rx_macstatus`, RX frame shape structs, `ar9170_get_decrypt_type()`, and `enum ar9170_txq`.

Control flow: No runtime flow except inline decrypt-type extraction. The descriptors drive `rx.c` parsing and `tx.c` superframe construction.

State and persistence: Defines packed wire-format structures and constants. It carries no runtime state but changes are ABI-sensitive between driver and firmware.

Dependencies and integration points: Includes `fwcmd.h`, is consumed by carl9170 RX/TX paths, and mirrors firmware-side definitions under `__CARL9170FW__`.

Risks and test signals: Primary risks are packed layout drift, endian mistakes, mismatched bit definitions, and the documented hardware limitation where QoS and aggregation cannot safely use independent hardware queues. Test signals are compile-time `BUILD_BUG_ON()` checks, working RX rate/status decoding, TX encryption/rate control, and stable A-MPDU operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/wlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c

Purpose: Provides a shared helper to render `enum nl80211_iftype` operation modes as readable strings for ath-family diagnostics.

Important APIs/types/functions: Exports `ath_opmode_to_string()`, mapping UNSPEC, ADHOC, STATION, AP, AP-VLAN, WDS, MONITOR, MESH, P2P client/GO, OCB, and default UNKNOWN.

Control flow: A single switch translates an interface type to a static string.

State and persistence: Stateless.

Dependencies and integration points: Includes `ath.h` and Linux export support; used by ath drivers for logging/debug output.

Risks and test signals: Risk is new nl80211 interface types falling to UNKNOWN until updated. Test signals are compile coverage and expected names in debug logs for each supported interface mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c

Purpose: Implements the ath DFS radar pattern detector facade, selecting regulatory-domain radar specs and coordinating per-channel PRI detectors.

Important APIs/types/functions: Exports `dfs_pattern_detector_init()`. Internal types include `struct radar_types` and `struct channel_detector`. Key functions are `get_dfs_domain_radar_types()`, `channel_detector_create()`, `channel_detector_get()`, `dpd_set_domain()`, `dpd_add_pulse()`, `dpd_reset()`, and `dpd_exit()`.

Control flow: Initialization creates a `dfs_pattern_detector`, installs the default method table, and sets the requested DFS domain if certification-onus support is enabled. Domain selection points at ETSI, FCC, or JP pattern tables and clears old channel detectors. Each pulse finds or creates a channel detector for its frequency, resets all detectors on timestamp wrap, and runs every radar-type `pri_detector`. A successful sequence copies the matched spec to the caller, logs the detection, resets that detector, and returns true.

State and persistence: Keeps `region`, radar spec pointer/count, `last_pulse_ts`, `common`, and a list of channel detectors with detector arrays. State is in-memory and freed by `exit()`.

Dependencies and integration points: Depends on cfg80211 DFS region enums, `dfs_pri_detector`, `ath_dbg`, and caller-provided pulse events from hardware-specific ath drivers.

Risks and test signals: Risks include fail-safe radar detection for unset domains, allocation failure under GFP_ATOMIC, timestamp wrap reset effects, and false positives/negatives from static regulatory patterns. Test signals are DFS CAC/radar simulations per domain, pulse sequences at tolerance boundaries, multi-channel off-channel reports, and pool statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h

Purpose: Declares the public ath DFS pattern detector interface and the common radar pulse/spec/stat structures shared with PRI detector code and ath drivers.

Important APIs/types/functions: Defines `PRI_TOLERANCE`, `struct ath_dfs_pool_stats`, `struct pulse_event`, `struct radar_detector_specs`, `struct dfs_pattern_detector`, and `dfs_pattern_detector_init()`.

Control flow: No implementation flow, but the `dfs_pattern_detector` method table defines object-style operations: `exit`, `set_dfs_domain`, `add_pulse`, and `get_stats`.

State and persistence: Describes detector runtime state: DFS region, radar type count, last pulse timestamp, `ath_common` pointer for logging, radar spec pointer, and channel detector list.

Dependencies and integration points: Includes kernel list/types and nl80211 region definitions; used by ath DFS-capable drivers and `dfs_pri_detector`.

Risks and test signals: ABI/layout risks are low inside the kernel tree but method-pointer misuse or unset domain handling can affect radar behavior. Test signals include compile coverage, detector initialization by DFS-capable drivers, and stats reporting after pulse injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pattern_detector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c

Purpose: Implements pulse repetition interval detection for a single radar specification, including reusable singleton pools for pulse and sequence objects.

Important APIs/types/functions: Exports `pri_detector_init()`. Internal helpers include `pde_get_multiple()`, pool registration/get/put functions, `pulse_queue_enqueue()`, `pulse_queue_dequeue()`, `pulse_queue_check_window()`, `pseq_handler_create_sequences()`, `pseq_handler_add_to_existing_seqs()`, `pseq_handler_check_detection()`, `pri_detector_add_pulse()`, `pri_detector_reset()`, and `pri_detector_exit()`. Exposes `global_dfs_pool_stats`.

Control flow: New pulses are filtered by width, minimum timestamp spacing, and chirp requirement. Existing sequences are advanced or aged out, new candidate sequences are built by comparing the current timestamp to queued historical pulses, and detection fires when a sequence reaches the spec threshold with enough matching pulses relative to false pulses. Non-detecting pulses are queued within a sliding time window.

State and persistence: Each detector keeps last timestamp, pulse queue, candidate sequence list, count, max count, and window size. Singleton pools retain freed `pulse_elem` and `pri_sequence` objects while any detector exists, protected by `pool_lock`; pools are freed when the last detector deregisters.

Dependencies and integration points: Used by `dfs_pattern_detector.c`; consumes `struct radar_detector_specs` and `struct pulse_event`; logs and stats are shared at ath DFS level.

Risks and test signals: Risks include GFP_ATOMIC allocation failures, false sequence growth under noisy pulses, timestamp arithmetic assumptions, pool reference imbalance, and boundary tolerance errors. Test signals are synthetic radar bursts, random noise rejection, chirp-required patterns, detector reset/exit leak checks, and pool stats consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h

Purpose: Declares the private PRI detector structures used by the DFS pattern detector implementation.

Important APIs/types/functions: Declares `global_dfs_pool_stats`, `struct pri_sequence`, `struct pri_detector`, and `pri_detector_init()`. `struct pri_detector` exposes `exit`, `add_pulse`, and `reset` method pointers plus internal queues and counters.

Control flow: No executable flow; callers allocate a detector for one `radar_detector_specs`, feed pulses through `add_pulse`, and reset or destroy through the method table.

State and persistence: Describes sequence state (`pri`, duration, count, false count, first/last/deadline timestamps) and detector state (`last_ts`, sequence list, pulse list, queue count, max count, window size). All state is volatile.

Dependencies and integration points: Includes Linux list support and relies on `dfs_pattern_detector.h` definitions for radar specs and pulse events.

Risks and test signals: Risks are mostly lifecycle and method-pointer misuse. Test signals include construction/destruction by `dfs_pattern_detector`, pulse additions yielding expected `pri_sequence` pointers, and reset clearing private queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/dfs_pri_detector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c

Purpose: Provides shared ath hardware helpers for BSSID mask programming and cycle counter accounting.

Important APIs/types/functions: Exports `ath_hw_setbssidmask()`, `ath_hw_cycle_counters_update()`, and `ath_hw_get_listen_time()`. Uses `common->ops->read/write`, `AR_STA_ID*`, `AR_BSSMSK*`, `AR_MIBC`, and cycle counter registers from `reg.h`.

Control flow: `ath_hw_setbssidmask()` writes the current MAC and BSSID mask into PCU registers. `ath_hw_cycle_counters_update()` freezes MIB counters, reads cycle/busy/RX/TX counts, clears counters, unfreezes, and accumulates into ANI and survey counters. `ath_hw_get_listen_time()` computes listen time from ANI counters and clears that accumulator.

State and persistence: Updates hardware registers and in-memory `ath_common` counter accumulators. Counter state persists only in driver memory until consumed.

Dependencies and integration points: Shared by ath drivers that provide register ops and `ath_common`; results feed ANI and survey reporting.

Risks and test signals: Risks include missing `cc_lock` by callers, divide-by-zero if `clockrate` is invalid, and BSSID mask over-acceptance in multi-BSS modes. Test signals are survey statistics sanity, ANI behavior, multi-vif ACK filtering, and register read/write traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c

Purpose: Implements shared ath hardware key-cache programming, key slot reservation, TKIP MIC layout handling, and key deletion.

Important APIs/types/functions: Exports `ath_hw_keyreset()`, `ath_hw_keysetmac()`, `ath_key_config()`, and `ath_key_delete()`. Core internals are `ath_hw_set_keycache_entry()`, `ath_setkey_tkip()`, `ath_reserve_key_cache_slot_tkip()`, and `ath_reserve_key_cache_slot()`.

Control flow: `ath_key_config()` translates mac80211 cipher/key metadata into `ath_keyval`, chooses a MAC binding and key-cache index based on pairwise/group mode and vif type, programs WEP/TKIP/CCMP/clear entries, then marks key bitmaps. TKIP programming handles combined MIC hardware or split MIC layouts, writing an inverted partial key first and the real key last to avoid transient MIC errors. Deletion clears MAC binding for CCMP/TKIP keys that might still be referenced by queued frames, otherwise resets key registers, then clears key maps.

State and persistence: Writes hardware key-table registers and mutates `keymap`, `ccmp_keymap`, and `tkip_keymap`. State is hardware/driver runtime only.

Dependencies and integration points: Depends on mac80211 key flags, nl80211 cipher suites, ath register ops, key-table addresses from `reg.h`, and `ath_common` crypt capability flags.

Risks and test signals: Risks include index arithmetic for TKIP companion slots, allocation exhaustion, stale key entries for queued encrypted frames, multicast/unicast MAC matching mistakes, and unsupported cipher handling. Test signals are WEP/TKIP/CCMP association, AP group keys, IBSS per-station group keys, key rekey under traffic, and key-cache bitmap consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c

Purpose: Provides shared ath module metadata and common utility functions for RX buffer allocation, beacon ownership checks, logging, and bus type names.

Important APIs/types/functions: Exports `ath_rxbuf_alloc()`, `ath_is_mybeacon()`, `ath_printk()`, and `ath_bus_type_strings`.

Control flow: RX buffer allocation reserves cacheline alignment slack and adjusts skb data alignment. Beacon matching checks frame type, nonzero current BSSID, and address equality. `ath_printk()` formats logs either with wiphy name and tracepoint emission or as generic ath logs when no wiphy is available.

State and persistence: Stateless except for allocated skbs returned to callers and exported static bus string table.

Dependencies and integration points: Depends on mac80211 skb/header helpers, `ath_common`, and `trace_ath_log()` from `trace.h`.

Risks and test signals: Risks include oversized allocations on systems that round skb allocation size up and missing wiphy context in logs. Test signals are RX path buffer alignment, beacon filtering in station power-save paths, and trace/log output coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h

Purpose: Defines shared ath hardware register offsets and bit fields used by common BSSID, counter, and key-cache helpers.

Important APIs/types/functions: Provides `AR_MIBC` flags, station ID registers, BSSID mask registers, cycle counter registers, key table base/address macros, key cache size, reserved WEP entries, key type constants, valid bit, and key/MAC register address macros.

Control flow: No executable flow; macro expansion is used by `hw.c` and `key.c`.

State and persistence: Defines hardware register interface constants only.

Dependencies and integration points: Consumed by ath common hardware helpers and hardware-specific drivers that implement register read/write ops.

Risks and test signals: Risks are incorrect offsets or bit definitions causing hardware misprogramming. Test signals include successful key programming, BSSID mask behavior, and sane cycle counter reads across ath hardware families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c

Purpose: Implements shared ath regulatory-domain initialization, world regulatory rules, country/regpair lookup, dynamic country updates, channel flag adjustments, and CTL band lookup.

Important APIs/types/functions: Exports `ath_is_world_regd()`, `ath_is_49ghz_allowed()`, `ath_regd_find_country_by_name()`, `ath_reg_notifier_apply()`, `ath_regd_init()`, and `ath_regd_get_band_ctl()`. Internal helpers include `ath_world_regdomain()`, `ath_reg_apply_radar_flags()`, `ath_reg_apply_world_flags()`, `ath_reg_apply_beaconing_flags()`, `ath_reg_apply_ir_flags()`, `__ath_reg_dyn_country()`, `ath_regd_is_eeprom_valid()`, `ath_get_regpair()`, and `__ath_regd_init()`.

Control flow: Initialization sanitizes and validates EEPROM regulatory data, maps country or regdomain values to a `reg_dmn_pair_mapping`, sets alpha2, stores a world-roaming copy if needed, installs a wiphy notifier, applies a custom world regdomain, and forces radar/world flags. The notifier always reapplies radar flags, then reacts to core/driver/user/country-IE hints, optionally dynamically mapping alpha2 to EEPROM country/regdomain state and relaxing no-IR flags according to world-domain rules.

State and persistence: Mutates `struct ath_regulatory` fields (`current_rd`, `country_code`, `regpair`, `alpha2`, `region`) and wiphy channel/regulatory flags. State is runtime only but derived from EEPROM-provided regulatory data.

Dependencies and integration points: Uses cfg80211/mac80211 regulatory APIs, tables from `regd_common.h`, constants from `regd.h`, `ath_common`, kernel config gates for dynamic user hints, and wiphy channel structures.

Risks and test signals: Regulatory correctness is high risk: wrong no-IR/radar flags can violate domain rules. Edge cases include invalid EEPROM codes, India DFS range exception, world roaming restoration, and user hints denied for US/Japan. Test signals include regdomain changes by core/user/country IE, channel flag audits, CTL lookup per band, and EEPROM invalid/sanitized logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h

Purpose: Declares ath regulatory constants, country codes, CTL groups, EEPROM regulatory flags, helper structs, and exported regulatory APIs.

Important APIs/types/functions: Defines `enum ctl_group`, CTL constants, `CTRY_*` country code enum values, `COUNTRY_ERD_FLAG`, `WORLDWIDE_ROAMING_FLAG`, world SKU masks, `struct country_code_to_enum_rd`, and prototypes for `ath_regd_init()`, `ath_reg_notifier_apply()`, `ath_regd_get_band_ctl()`, `ath_is_world_regd()`, `ath_is_49ghz_allowed()`, and `ath_regd_find_country_by_name()`.

Control flow: No executable flow; it defines the contract implemented by `regd.c`.

State and persistence: Provides symbolic values that represent EEPROM regulatory state and cfg80211-facing regulatory state.

Dependencies and integration points: Includes nl80211/cfg80211 and `ath.h`; used by ath drivers during wiphy registration and regulatory notifications.

Risks and test signals: Risks include stale or missing country code definitions and typo-level API mismatch. Test signals are compile coverage and correct mapping behavior through `regd.c` tests or runtime regulatory logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h

Purpose: Supplies the shared regulatory mapping tables used by ath regulatory code: enum regdomain IDs, regdomain-to-CTL mappings, and country-to-regdomain mappings.

Important APIs/types/functions: Defines `enum EnumRd`, static `regDomainPairs[]`, and static `allCountries[]`.

Control flow: No executable control flow, but `regd.c` linearly searches these tables when validating EEPROM data, mapping alpha2/country codes, selecting regpairs, and deriving CTL values.

State and persistence: Static compile-time lookup data only. Runtime state in `ath_regulatory` references entries from these tables.

Dependencies and integration points: Included by `regd.c`; table value meanings are tied to constants in `regd.h` and cfg80211 regulatory behavior.

Risks and test signals: Regulatory table errors have compliance impact. Risks include duplicate/legacy country entries, missing new countries, and static table definitions in a header if included by more than one C file. Test signals are country alpha2 lookup, EEPROM regpair validation, CTL selection for 2 GHz/5 GHz, and regulatory selftests if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h

Purpose: Defines common userspace-facing FFT spectral sample formats for ath drivers.

Important APIs/types/functions: Provides bin-count constants, `enum ath_fft_sample_type`, `struct fft_sample_tlv`, `struct fft_sample_ht20`, `struct fft_sample_ht20_40`, `struct fft_sample_ath10k`, and `struct fft_sample_ath11k`.

Control flow: No executable flow; drivers fill packed TLV records and expose them through debugfs or similar spectral scan interfaces.

State and persistence: Defines packed binary layouts with fixed and flexible sample data. No runtime state.

Dependencies and integration points: Shared by ath spectral scan producers and userspace parsers; endian annotations indicate wire format.

Risks and test signals: Risk is ABI breakage if fields before type/length are changed or if flexible bin lengths are misreported. Test signals are userspace spectral capture parsing for HT20, HT20/40, ath10k, and ath11k samples, including endian and length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h

Purpose: Defines the shared ath nl80211 testmode interface version, maximum payload sizes, attributes, and command IDs.

Important APIs/types/functions: Defines `ATH_TESTMODE_VERSION_MAJOR`, `ATH_TESTMODE_VERSION_MINOR`, `ATH_TM_DATA_MAX_LEN`, `ATH_FTM_EVENT_MAX_BUF_LENGTH`, `enum ath_tm_attr`, and `enum ath_tm_cmd`.

Control flow: No executable flow; driver testmode handlers parse attributes and commands according to these enums.

State and persistence: Constants only; version numbers are the compatibility contract with userspace tools.

Dependencies and integration points: Used by ath drivers with nl80211 testmode support for GET_VERSION, WMI command passthrough, UTF firmware start, and FTM WMI traffic.

Risks and test signals: Risks include incompatible interface changes without version bump, payload size mismatches, and command/attribute drift with userspace tooling. Test signals are nl80211 testmode GET_VERSION and WMI/FTM command round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.c

Purpose: Instantiates ath tracepoints declared in `trace.h`.

Important APIs/types/functions: Defines `CREATE_TRACE_POINTS` before including `trace.h`.

Control flow: No runtime control flow in this file; compile-time tracepoint generation emits the tracepoint definitions.

State and persistence: Tracepoint registration is build/runtime kernel tracing state, not driver data state.

Dependencies and integration points: Includes Linux module support and `trace.h`; `ath_printk()` calls `trace_ath_log()` when a wiphy is available.

Risks and test signals: Risks are build failures from trace include path/name mismatches or missing tracepoint config stubs. Test signals include successful module build and observing `ath:ath_log` events when tracepoints are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.h

Purpose: Declares the ath tracepoint interface, currently the `ath_log` trace event used by shared ath logging.

Important APIs/types/functions: Defines `TRACE_SYSTEM ath`, provides a no-op `TRACE_EVENT` fallback when `CONFIG_ATH_TRACEPOINTS` is disabled, and declares `TRACE_EVENT(ath_log)` with wiphy/device, driver, and formatted message fields.

Control flow: Trace macros generate either real tracepoint call sites or static inline no-op functions. `trace/define_trace.h` is included outside the include guard as required by kernel tracepoint conventions.

State and persistence: Trace records are runtime tracing data. The header itself defines no persistent driver state.

Dependencies and integration points: Includes Linux tracepoint support and `ath.h`; consumed by `trace.c` and `main.c`.

Risks and test signals: Risks include format lifetime issues with `va_format`, disabled-config stub mismatch, and trace include path errors. Test signals are builds with and without `CONFIG_ATH_TRACEPOINTS` and trace output containing driver/device/message fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig

Purpose: Defines kernel configuration entries for the Qualcomm Atheros WCN3660/WCN3680 mac80211 driver and its debugfs support.

Important APIs/types/functions: Provides `config WCN36XX` as a tristate depending on `MAC80211`, `HAS_DMA`, optional `QCOM_WCNSS_CTRL`, and optional `RPMSG`; provides `config WCN36XX_DEBUGFS` depending on `WCN36XX`.

Control flow: Kconfig dependency resolution controls whether the driver and debugfs code are built.

State and persistence: Build-time configuration only.

Dependencies and integration points: Integrates with kernel wireless, DMA, Qualcomm WCNSS control, RPMSG, and debugfs configuration.

Risks and test signals: Risks include invalid dependency combinations hiding the driver or enabling it without platform messaging support. Test signals are allmodconfig/allyesconfig coverage and module build as `wcn36xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile

Purpose: Describes the object composition for the `wcn36xx` kernel module.

Important APIs/types/functions: Sets `obj-$(CONFIG_WCN36XX) := wcn36xx.o`, includes `main.o`, `dxe.o`, `txrx.o`, `smd.o`, `pmc.o`, `debug.o`, and `firmware.o`, and conditionally includes `testmode.o` for `CONFIG_NL80211_TESTMODE`.

Control flow: Kbuild uses these object lists to link the module.

State and persistence: Build metadata only.

Dependencies and integration points: Mirrors source-level module boundaries: DXE DMA, TX/RX, SMD firmware control, power management, debugfs, firmware, and optional testmode.

Risks and test signals: Risks are missing objects after source changes or optional testmode link failures. Test signals are module builds under `CONFIG_WCN36XX=m/y` and `CONFIG_NL80211_TESTMODE` toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c

Purpose: Implements optional debugfs controls for WCN36xx BMPS power-save switching, firmware dump commands, and firmware feature capability display.

Important APIs/types/functions: Under `CONFIG_WCN36XX_DEBUGFS`, defines debugfs file operations for `bmps_switcher`, `dump`, and `firmware_feat_caps`, and exports `wcn36xx_debugfs_init()` / `wcn36xx_debugfs_exit()`.

Control flow: Init creates a `wcn36xx` debugfs directory under the wiphy debugfs root and adds files. BMPS reads scan station vifs for `WCN36XX_BMPS`; writes parse the first user byte and enter/exit BMPS via keepalive/PMC helpers. Dump writes parse up to five integer arguments and send an SMD dump command. Firmware feature reads allocate a buffer, lock `hal_mutex`, enumerate supported feature bits, and copy names to userspace. Exit removes the debugfs tree.

State and persistence: Mutates firmware/driver power-save state through PMC calls and stores debugfs dentries in `wcn->dfs`. No durable persistence.

Dependencies and integration points: Depends on debugfs, usercopy, WCN36xx vif list, PMC, firmware feature helpers, SMD command path, and `wcn->hal_mutex`.

Risks and test signals: Risks include vif-list iteration without explicit locking context, silent ignore of invalid BMPS input, fixed feature buffer truncation, and debugfs creation failure. Test signals are debugfs file presence, BMPS enter/exit on station mode, dump command dispatch, and firmware capability listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h

Purpose: Declares WCN36xx debugfs data structures and init/exit hooks, with no-op stubs when debugfs support is disabled.

Important APIs/types/functions: Defines `WCN36xx_MAX_DUMP_ARGS`, `struct wcn36xx_dfs_file`, `struct wcn36xx_dfs_entry`, `wcn36xx_debugfs_init()`, and `wcn36xx_debugfs_exit()`.

Control flow: With `CONFIG_WCN36XX_DEBUGFS`, callers link to real implementations in `debug.c`; otherwise inline no-op functions preserve call sites.

State and persistence: Describes debugfs dentry state stored under `struct wcn36xx`. No standalone state.

Dependencies and integration points: Used by WCN36xx main driver lifecycle; depends on debugfs types when enabled.

Risks and test signals: Risks are structure drift with `debug.c` or call sites assuming debugfs files exist when stubs are compiled. Test signals are builds with debugfs enabled/disabled and clean init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c

Purpose: Implements WCN36xx DXE DMA engine setup and runtime handling for high/low priority TX and RX channels, including descriptor rings, IRQs, DMA memory pools, TX completion, RX refill, BMPS wake signaling, and flush/deinit.

Important APIs/types/functions: Exports `wcn36xx_dxe_alloc_ctl_blks()`, `wcn36xx_dxe_free_ctl_blks()`, `wcn36xx_dxe_allocate_mem_pools()`, `wcn36xx_dxe_free_mem_pools()`, `wcn36xx_dxe_init()`, `wcn36xx_dxe_deinit()`, `wcn36xx_dxe_tx_frame()`, `wcn36xx_dxe_tx_flush()`, `wcn36xx_dxe_rx_frame()`, and `wcn36xx_dxe_tx_ack_ind()`. Key internals include descriptor initialization/freeing, `wcn36xx_dxe_fill_skb()`, `reap_tx_dxes()`, IRQ handlers, and `wcn36xx_rx_handle_packets()`.

Control flow: Allocation builds circular control-block rings for TX low/high and RX low/high and initializes SMSM TX state. Init resets DXE, selects interrupt routing, allocates coherent descriptor rings, assigns TX BD pools, primes RX skbs, writes channel next/source/destination registers, requests TX/RX IRQs, creates a TX ACK timer, and enables channel interrupts. TX uses paired descriptors: one for the firmware buffer descriptor and one for skb data; it maps skb DMA, marks descriptors valid in order, advances the head, and either writes channel control or signals SMSM when in BMPS. TX IRQs clear per-channel status and reap completed descriptors, transferring requested-status frames to either immediate mac80211 status, an ACK-indication wait slot, or timeout. RX IRQs process invalidated descriptors, replace skb buffers, unmap and deliver old skbs, then re-enable the channel.

State and persistence: Maintains descriptor/control rings, coherent BD pools, DMA mappings, queued skb pointers, channel head/tail pointers, locks, TX ACK pending skb/timer, queue-stopped flag, IRQ registrations, and SMSM state bits. All state is runtime and freed on deinit.

Dependencies and integration points: Depends on MMIO DXE/CCU register bases, Qualcomm SMEM state, mac80211 TX status and queue control, WCN36xx TX/RX parsing (`wcn36xx_rx_skb()`), platform IRQs, DMA API, and power-save state in `wcn36xx_vif`.

Risks and test signals: Risks include descriptor ownership ordering, DMA mapping leaks on TX errors, RX refill allocation failure dropping packets, TX ACK timeout races, queue stop/wake imbalance, IRQ cleanup ordering, and BMPS wake signaling. Test signals are high/low priority TX/RX traffic, requested TX status with ACK indication and timeout, ring-full backpressure, RX allocation-failure resilience, suspend/remove deinit, DMA API debug, and BMPS data transmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.c -->
