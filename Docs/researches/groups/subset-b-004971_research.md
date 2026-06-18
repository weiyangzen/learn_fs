# subset-b-004971 research

Grouped research for wlcore command, configuration, debug, event, init, and IO sources. Each section is delimited for reconciliation into the matching source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.c

## Purpose
`cmd.c` is the wlcore firmware command execution layer. It turns mac80211 and wlcore state into packed firmware command mailboxes, manages role and host-link allocation, programs templates and keys, starts and stops STA/AP/IBSS/device roles, controls remain-on-channel, configures firmware logging, and sends regulatory/DFS and generic feature commands.

## Important APIs and functions
The core API is `wl1271_cmd_send()`, backed by `__wlcore_cmd_send()` and `wlcore_cmd_send_failsafe()`. It writes a DMA-safe command buffer to `wl->cmd_box_addr`, triggers the chip-specific command doorbell through `wl->ops->trigger_cmd()`, polls `REG_INTERRUPT_NO_CLEAR` for `WL1271_ACX_INTR_CMD_COMPLETE`, reads command status back from the mailbox, ACKs the command interrupt, and queues recovery on transport or unexpected firmware status failures.

Role lifecycle functions include `wl12xx_cmd_role_enable()`, `wl12xx_cmd_role_disable()`, `wl12xx_cmd_role_start_sta()`, `wl12xx_cmd_role_stop_sta()`, `wl12xx_cmd_role_start_ap()`, `wl12xx_cmd_role_stop_ap()`, `wl12xx_cmd_role_start_ibss()`, `wl12xx_start_dev()`, and `wl12xx_stop_dev()`. Link allocation is owned by `wl12xx_allocate_link()` and `wl12xx_free_link()`, which update `wl->links_map`, per-vif link maps, session IDs, TX accounting, AP broadcast/global links, and recovery sequence padding.

Configuration helpers include `wl1271_cmd_interrogate()`, `wlcore_cmd_configure_failsafe()`, `wl1271_cmd_configure()`, `wl1271_cmd_data_path()`, `wl1271_cmd_ps_mode()`, `wlcore_cmd_regdomain_config_locked()`, `wl12xx_cmd_config_fwlog()`, `wl12xx_cmd_stop_fwlog()`, `wlcore_cmd_generic_cfg()`, and `wlcore_cmd_wait_for_event_or_timeout()`. Template/key helpers include `wl1271_cmd_template_set()`, null/QoS/PS-poll/probe/ARP template builders, `wl12xx_cmd_set_default_wep_key()`, `wl1271_cmd_set_sta_key()`, and `wl1271_cmd_set_ap_key()`.

## Control flow
Command control flow is synchronous: allocate and fill a packed command, call `wl1271_cmd_send()`, and unwind state if command submission fails. Role start paths allocate HLIDs before sending `CMD_ROLE_START`; error labels free partially allocated links. AP start allocates both global and broadcast HLIDs and preserves broadcast sequence accounting across recovery/resume. Peer removal sends `CMD_REMOVE_PEER` and then waits for `WLCORE_EVENT_PEER_REMOVE_COMPLETE`, but tolerates timeout because firmware may omit the event. Regulatory configuration builds a channel bitmap from pending channels plus current wiphy channel flags, sends `CMD_DFS_CHANNEL_CONFIG`, waits for `WLCORE_EVENT_DFS_CONFIG_COMPLETE`, then persists the last-applied bitmap.

## State and persistence behavior
The file mutates driver runtime state: `roles_map`, `links_map`, `roc_map`, `session_ids`, `active_link_count`, per-link TX counters, per-vif role IDs, per-vif HLIDs, `reg_ch_conf_pending`, `reg_ch_conf_last`, and AP/STA recovery counters. It also consumes persistent configuration from `wl->conf` for TX retries, AP aging, firmware logger settings, and power-save timing. Most allocations are transient command buffers, but link/session state persists until stop, recovery, or role teardown.

## Dependencies and integration points
`cmd.c` depends on IO wrappers in `io.h`, ACX configuration, `event.h` wait events, `tx.h` queue/watchdog helpers, mac80211 frame constructors, cfg80211 band/channel definitions, and chip-specific callbacks in `wl->ops`/`hw_ops.h`. It is called by wlcore main, scan, AP/STA setup, key management, regulatory updates, and debugfs firmware logger controls.

## Risks
The command ABI requires exact packed layouts and little-endian fields; buffer length, alignment, or status handling mistakes can lock the firmware or corrupt command interpretation. Link allocation and free paths are shared with TX under `wl_lock`; missing locking or bad unwind can leave stale HLID maps. Several paths accept firmware timeouts as recoverable, so regressions may appear as delayed recovery rather than immediate failure. Template builders must account for encryption padding and mac80211 skb ownership. Regulatory bitmap mapping is hand-coded and sensitive to band/channel tables.

## Test signals
Useful signals include successful interface bring-up in STA/AP/IBSS/P2P roles, association and disassociation without leaked HLIDs, scan and scheduled-scan probe templates, AP peer add/remove, encryption for WEP/TKIP/AES/GEM, remain-on-channel completion, DFS/regdomain update completion, firmware logger reconfiguration, command timeout recovery, and debug traces under `DEBUG_CMD`, `DEBUG_SCAN`, `DEBUG_CRYPT`, and `DEBUG_ACX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.h

## Purpose
`cmd.h` declares the public wlcore command API and defines the packed firmware command ABI used by `cmd.c` and adjacent wlcore modules. It is the contract between host driver code and wl12xx/wl18xx firmware command mailboxes.

## Important APIs and types
The header exports command functions for command send/configure/interrogate, role start/stop/enable/disable, device role ROC, link allocation/free, template building, key programming, peer state, AP peer add/remove, firmware logging, channel switch stop, regulatory configuration, generic feature configuration, and event waits.

The central ABI types are `struct wl1271_cmd_header`, `struct wl1271_command`, `enum wl1271_commands`, command status constants, `enum cmd_templ`, role structures (`wl12xx_cmd_role_enable`, `wl12xx_cmd_role_disable`, `wl12xx_cmd_role_start`, `wl12xx_cmd_role_stop`), `struct wl1271_cmd_template_set`, `struct wl1271_cmd_ps_params`, `struct wl1271_cmd_set_keys`, peer/ROC structures, firmware logger structures, DFS regulatory config, generic config, and calibration test structures.

## Control flow and integration
Consumers allocate one of these packed structures, fill host-side fields using little-endian conversions where required, and pass it to `wl1271_cmd_send()` or the configure/interrogate wrappers. The firmware command IDs in `enum wl1271_commands` select mailbox behavior, while command status codes returned in `wl1271_cmd_header.status` are validated by `cmd.c`.

## State and persistence behavior
The header does not mutate state directly, but it defines persistent command-visible state: role IDs, HLIDs, sessions, rates, key material, logger mode, channel bitmaps, and feature toggles. These structures are packed, so layout is persistent across host/firmware boundaries and must remain synchronized with firmware expectations.

## Dependencies and risks
It depends on `wlcore.h` and kernel/mac80211 scalar types. The main risks are ABI drift, incorrect enum values, missing `__packed`, wrong endian annotations, and command structures exceeding firmware mailbox limits such as `WL1271_CMD_MAX_PARAMS` or `WL1271_CMD_TEMPL_MAX_SIZE`.

## Test signals
Compile-time structure use, role lifecycle smoke tests, firmware command status validation, key install/remove, AP peer management, and template programming are the primary signals. Firmware rejecting a command with `CMD_STATUS_INVALID_PARAM`, `CMD_STATUS_TEMPLATE_TOO_LARGE`, or `CMD_STATUS_UNKNOWN_CMD` often points back to this ABI layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/conf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/conf.h

## Purpose
`conf.h` defines the wlcore configuration file ABI and the in-memory `struct wlcore_conf` consumed by initialization, command, ACX, debugfs, TX, RX, scan, power-save, firmware logging, recovery, and rate-control code.

## Important APIs and types
The header provides rate bitmasks and indices, SoftGemini settings, RX interrupt/queue thresholds, TX rate class/access-category/TID settings, beacon filtering and wake conditions, connection monitoring, power management, roaming trigger weights, foreground and scheduled scan dwell policies, HT block-ack settings, memory pool sizing, FM coexistence, RX streaming, firmware logger configuration, rate management, hangover behavior, and recovery policy.

The top-level persisted layout is `struct wlcore_conf_file`, composed of `struct wlcore_conf_header`, `struct wlcore_conf`, and chip-private trailing data. `WLCORE_CONF_VERSION`, `WLCORE_CONF_MASK`, and `WLCORE_CONF_SIZE` define versioning and expected core size.

## Control flow and integration
Runtime code reads values from `wl->conf` and sends them to firmware through ACX commands and command helpers. `init.c` consumes TX/RX/PM/scan/rate/hangover/memory settings during hardware and vif initialization. `cmd.c` uses TX retry limits, AP aging, and firmware logger fields. `debugfs.c` exposes selected fields as writable runtime controls and may reprogram firmware immediately after writes.

## State and persistence behavior
This is a persistent firmware configuration contract. Values can originate from external wlconf/NVS configuration, are stored in `wl->conf`, and may survive until driver reload or be changed through debugfs. Because many structures are `__packed`, padding and field ordering are part of the ABI. Some values have documented ranges but are not all validated at compile time.

## Dependencies and risks
The file depends on kernel bit helpers and shared scalar types. Risks include version mismatch with configuration blobs, invalid range values causing firmware rejection, confusion between rate bitmasks and rate indices, and subtle behavior changes when debugfs writes alter fields without immediately reapplying all dependent ACX state.

## Test signals
Signals include successful parsing of the wlcore configuration file, hardware initialization completing all ACX stages, stable power-save behavior, correct scan dwell timing, AP WMM/TID setup, RX interrupt pacing, firmware logger operation, and recovery policy behavior when firmware faults occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debug.h

## Purpose
`debug.h` centralizes wlcore logging names, debug-level bitmasks, and logging/dump macros. It provides a uniform driver prefix and gates verbose debug output through the global `wl12xx_debug_level`.

## Important APIs and types
The debug categories include IRQ, SPI, boot, mailbox, testmode, event, TX, RX, scan, crypto, PSM, mac80211, command, ACX, SDIO, filters, ad-hoc, AP, probe, IO, master, and all. Macros include `wl1271_error()`, `wl1271_warning()`, `wl1271_notice()`, `wl1271_info()`, `wl1271_debug()`, `wl1271_dump()`, and `wl1271_dump_ascii()`.

## Control flow and integration
All wlcore modules call these macros inline. With `CONFIG_DYNAMIC_DEBUG`, `wl1271_debug()` emits through `dynamic_pr_debug()` when the category is enabled. Otherwise it uses `printk(KERN_DEBUG)`. Hex dump helpers cap dumps with `DEBUG_DUMP_LIMIT`.

## State and persistence behavior
The only shared state is external `u32 wl12xx_debug_level`, generally controlled through module/debug mechanisms. The header itself has no persistence, but enabled categories can materially affect diagnostics and log volume.

## Dependencies and risks
It depends on kernel `bitops`, `printk`, dynamic debug, and hex dump helpers. Risks are mainly operational: logging sensitive key material through `DEBUG_CRYPT`, excessive debug volume, and losing diagnostics when category masks are not enabled.

## Test signals
Compile-time macro expansion across modules, dynamic debug behavior, category-gated command/event/IO logs, and bounded hex dump lengths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.c

## Purpose
`debugfs.c` exposes wlcore diagnostics and live tuning controls under the wiphy debugfs directory. It provides state snapshots, firmware statistics, selected configuration knobs, forced recovery/power controls, direct device-memory access, RX streaming controls, and firmware logger output selection.

## Important APIs and functions
`wl1271_format_buffer()` formats small debugfs reads. `wl1271_debugfs_update_stats()` refreshes firmware statistics at most once per second while the device is on and not in PLT mode. `wl1271_debugfs_init()` creates the root directory, allocates `wl->stats.fw_stats`, adds files, and delegates chip-specific debugfs setup through `wlcore_debugfs_init()`. `wl1271_debugfs_exit()` frees stats memory, and `wl1271_debugfs_reset()` clears counters.

File operations cover retry counters, total TX queue length, GPIO power, recovery trigger, dynamic PS timeout, forced PS, split scan timeout, driver and vif state dumps, DTIM/beacon intervals, RX streaming interval/always, beacon filtering, raw firmware stats, sleep authorization, device memory read/write/seek, firmware logger output, and RX interrupt thresholds generated by `WL12XX_CONF_DEBUGFS`.

## Control flow
Read paths usually format cached driver state or refresh firmware stats. Write paths parse userspace input with `kstrtoul_from_user()`, validate ranges, lock `wl->mutex`, mutate `wl->conf` or driver flags, and for live settings resume the device with runtime PM before issuing ACX/command updates. Device-memory access saves the current partition, installs a temporary partition for the requested address range, performs raw bus IO, restores the partition, and copies data to or from userspace.

## State and persistence behavior
Debugfs writes mutate runtime configuration fields such as RX interrupt thresholds, dynamic PS timeout, forced PS, scan split timeout, wake intervals, RX streaming, sleep authorization, and firmware logger output. These changes are not file-backed persistence but affect the active driver until reset/reload or replacement by configuration. Stats memory persists from debugfs init to exit and is refreshed lazily.

## Dependencies and integration points
The file integrates Linux debugfs, runtime PM, wlcore mutex discipline, ACX configuration routines, PS management, TX queue counting, IO partitioning, firmware logger commands, and chip-specific debugfs hooks. It depends on `conf.h` values indirectly through `wl->conf`.

## Risks
Writable debugfs files can change live firmware behavior and bypass normal mac80211 flows. Device memory access is powerful and only dword-aligned, capped to `4 * PAGE_SIZE`, but can still perturb a live device. Some write paths return `count` even after internal command failure unless count is overwritten, so userspace may need logs to detect partial failure. Range validation differs between knobs, and some values take effect only when entering PSM later.

## Test signals
Mount/debugfs presence, readable counters and state dumps, firmware stats refresh, valid and invalid writes returning expected errors, runtime PM reference balance, partition restoration after `dev/mem`, forced recovery scheduling, RX streaming recalculation, and firmware logger reconfiguration are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.h

## Purpose
`debugfs.h` declares wlcore debugfs lifecycle functions and provides macro templates for creating formatted read-only files and firmware-stat files.

## Important APIs and macros
It declares `wl1271_format_buffer()`, `wl1271_debugfs_init()`, `wl1271_debugfs_exit()`, `wl1271_debugfs_reset()`, and `wl1271_debugfs_update_stats()`. `DEBUGFS_READONLY_FILE` generates a read function and file operations for scalar values. `DEBUGFS_ADD` and `DEBUGFS_ADD_PREFIX` create files. `DEBUGFS_FWSTATS_FILE` and `DEBUGFS_FWSTATS_FILE_ARRAY` generate stats readers that refresh firmware stats before formatting a scalar or array.

## Control flow and integration
`debugfs.c` uses these helpers to reduce repetitive file-operation boilerplate. Chip-specific modules can use the firmware-stat macros to expose fields in their own firmware statistics structures while sharing the common `wl->stats.fw_stats` refresh path.

## State and persistence behavior
The header does not own state. Generated readers access `file->private_data` as `struct wl1271 *` and read live driver/statistics memory. The fixed buffer size limits formatted output for generated array readers.

## Dependencies and risks
It depends on `wlcore.h`, debugfs APIs through consuming C files, and correct type names passed to the macros. Macro-generated code can obscure bounds behavior; array output truncates once `DEBUGFS_FORMAT_BUFFER_SIZE` is reached.

## Test signals
Build coverage from generated operations, debugfs files showing expected scalar/array values, stats refresh calls before firmware-stat reads, and no truncation surprises for arrays near the buffer cap are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.c

## Purpose
`event.c` translates firmware mailbox events into driver state changes and mac80211/cfg80211 notifications. It handles firmware logger data, RSSI threshold notifications, SoftGemini state, scheduled-scan completion, block-ack constraints, channel switch completion, dummy-packet requests, AP station disconnect hints, remain-on-channel completion, beacon loss, event mask programming, and mailbox processing.

## Important APIs and functions
`wl1271_event_handle()` reads an event mailbox into `wl->mbox`, calls the chip-specific `process_mailbox_events()` callback, then ACKs the event through `wl->ops->ack_event()`. `wl1271_event_unmask()` programs the inverse event mask with `wl1271_acx_event_mbox_mask()`.

Exported handlers include `wlcore_event_fw_logger()`, `wlcore_event_rssi_trigger()`, `wlcore_event_soft_gemini_sense()`, `wlcore_event_sched_scan_completed()`, `wlcore_event_ba_rx_constraint()`, `wlcore_event_channel_switch()`, `wlcore_event_dummy_packet()`, `wlcore_event_max_tx_failure()`, `wlcore_event_inactive_sta()`, `wlcore_event_roc_complete()`, and `wlcore_event_beacon_loss()`.

## Control flow
The interrupt path chooses mailbox 0 or 1, reads the descriptor, lets chip-specific code decode event bits, and ACKs the mailbox. Individual decoded events walk active wlcore vifs/links, update flags, and call mac80211 APIs such as `ieee80211_cqm_rssi_notify()`, `ieee80211_sched_scan_stopped()`, `ieee80211_stop_rx_ba_session()`, `ieee80211_chswitch_done()`, `ieee80211_csa_finish()`, `ieee80211_report_low_ack()`, `ieee80211_ready_on_channel()`, `ieee80211_connection_loss()`, and `ieee80211_cqm_beacon_loss_notify()`.

## State and persistence behavior
The handlers update `wl->flags`, `wlvif->last_rssi_event`, `wlvif->ba_allowed`, channel-switch flags, `wl->sched_vif`, and deferred connection-loss work. Firmware logger handling copies ring-buffer data to the driver logger path and writes the updated read pointer back to device memory. Event mask state lives in `wl->event_mask`.

## Dependencies and integration points
This file depends on mailbox addresses initialized elsewhere, IO wrappers, ACX event-mask commands, PS/RX streaming recalculation, scan state, TX dummy packet support, mac80211 station/vif APIs, and chip-specific mailbox decoding. It is tightly coupled to `event.h` event IDs and wait-event names used by command paths.

## Risks
Mailbox ACK ordering is critical; missed ACKs can stall event delivery. Firmware logger pointer validation protects against out-of-bounds reads, but constants are wl18xx-specific. Event handlers assume locks and runtime context are provided by callers. Beacon-loss delayed work and channel-switch completion can race with interface teardown, so role IDs and flags are checked defensively.

## Test signals
Signals include event interrupt handling on both mailboxes, firmware logger output with ring wraparound, RSSI CQM notifications, scheduled-scan completion, BA session stop on constraints, CSA completion for STA/AP roles, dummy packet TX, low-ack station reports, ROC ready notification, beacon loss reporting, and successful command waits for role stop, peer removal, and DFS config completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.h

## Purpose
`event.h` documents the dual-mailbox firmware event mechanism and declares event IDs, wait-event identifiers, firmware logger metadata, and event handling functions.

## Important APIs and types
It defines RSSI/SNR trigger bit IDs, `EVENT_MBOX_ALL_EVENT_ID`, `enum wlcore_wait_event` values for role stop, peer removal, and DFS config completion, power-save entry result constants, `NUM_OF_RSSI_SNR_TRIGGERS`, and packed `struct fw_logger_information` containing ring-buffer size and read/write pointers.

## Control flow and integration
Firmware fills one of two event buffers while the host processes the other. `wl1271_event_handle()` consumes one mailbox and ACKs it. Command code uses `wlcore_wait_event` names through `wl->ops->wait_for_event()` when synchronous command flows need firmware completion events.

## State and persistence behavior
The header defines no host state directly, but the firmware logger structure maps persistent device memory for logger ring-buffer accounting. Event masks and mailbox buffers are maintained in `struct wl1271`.

## Dependencies and risks
It depends on bit definitions and packed endian fields. Risks include mismatch between chip-specific event decoding and common exported handler prototypes, and wait-event enum changes that break command paths expecting specific completions.

## Test signals
Mailbox event handling, wait-event completion for role stop/peer removal/DFS config, firmware logger pointer parsing, and RSSI trigger delivery validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/hw_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/hw_ops.h

## Purpose
`hw_ops.h` is the common inline dispatch layer from wlcore core code to chip-specific operations stored in `wl->ops`. It hides wl12xx/wl18xx differences for TX/RX descriptors, firmware status, rate masks, keys, debugfs, address conversion, priority decisions, smart config, DFS/CAC, and AP sleep.

## Important APIs and wrappers
Mandatory wrappers call `BUG_ON(1)` when missing: TX block calculation, TX descriptor block/data length setup, RX buffer alignment, RX packet length, firmware status conversion, STA AP rate mask, TX checksum setup, spare block calculation, key setup, firmware address conversion, and link priority decisions.

Optional wrappers return success/defaults or `-EINVAL`: read preparation, delayed/immediate TX completion, vif init, firmware identify, RX checksum setup, AP MIMO/wide rate mask, chip debugfs init, static data handling, pre-packet-send adjustment, STA rate-control update, interrupt notify, RX BA filter, AP sleep, peer capability setup, smart config, CAC, and DFS master restart.

## Control flow and integration
Core files call these wrappers instead of branching on chip type. The wrappers either delegate to `wl->ops` or provide a conservative default. This keeps common code in `cmd.c`, `event.c`, `debugfs.c`, `init.c`, TX, and RX independent of hardware family details.

## State and persistence behavior
The header mutates no state directly, but delegated operations can update descriptors, firmware status structures, per-vif chip-private data, keys, debugfs trees, and DFS/smart-config firmware state.

## Dependencies and risks
It depends on `wlcore.h`, `rx.h`, and the completeness of each chip family's operations table. The main risk is a missing mandatory callback causing a kernel BUG instead of a recoverable failure. Optional default returns can also hide unsupported hardware features if callers assume the operation took effect.

## Test signals
Build coverage across wl12xx and wl18xx, probe-time operations table validation, TX/RX descriptor correctness, key installation, firmware status decoding, debugfs chip extensions, AP rate masks, DFS/CAC calls, and smart-config unsupported-path errors exercise this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/hw_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ini.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ini.h

## Purpose
`ini.h` defines the wl1271/wl128x NVS/INI binary layouts for platform and RF calibration data. These structures describe clocks, SmartReflex, 2.4 GHz and 5 GHz static radio parameters, FEM-specific dynamic power tables, RSSI compensation, trace loss, and NVS section sizes.

## Important APIs and types
Key types include `wl1271_ini_general_params`, `wl128x_ini_general_params`, band parameter structures for 2.4 GHz and 5 GHz, FEM parameter structures for wl1271 and wl128x, `wl1271_nvs_file`, and `wl128x_nvs_file`. Constants define channel/sub-band/rate-group counts, FEM module mapping, the NVS section size, and the legacy NVS file size.

## Control flow and integration
The header has no executable flow. Loader/calibration code interprets firmware/NVS blobs using these packed structures and may map four logical FEM module types into two stored NVS entries via `WL12XX_FEM_TO_NVS_ENTRY()`.

## State and persistence behavior
This is persistent board calibration data. The NVS section must be first in both top-level file structures, followed by the INI section. Layout, count constants, and padding bytes are part of the on-disk/on-flash ABI.

## Dependencies and risks
The structures depend on exact packing and little-endian fields for voltage values. Risks include using a wl1271 layout for wl128x data, wrong FEM mapping, malformed calibration blobs, and array-size/count drift corrupting subsequent fields.

## Test signals
Signals include successful NVS loading, clock/ref-clock configuration, sane per-band power limits, valid FEM selection, calibration test command results, and RF behavior across channels and temperature/power states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.c

## Purpose
`init.c` sequences wlcore firmware/hardware initialization and per-vif initialization. It reserves firmware template memory, configures core ACX settings, initializes AP/STA role behavior, installs rate policies, sets BA policy, and enables the data path.

## Important APIs and functions
Top-level functions are `wl1271_hw_init()`, `wl1271_init_vif_specific()`, `wl1271_init_templates_config()`, `wl1271_init_pta()`, `wl1271_init_energy_detection()`, `wl1271_init_ap_rates()`, `wl1271_ap_init_templates()`, and `wl1271_sta_hw_init()`.

Static helpers build AP deauth/null/QoS-null templates, configure RX lifetime, slot/service-period/RTS settings, STA beacon filtering, beacon/DTIM broadcast options, firmware logging, AP hardware sleep, STA keep-alive behavior, BA policies, STA role ACX settings, and AP role ACX settings.

## Control flow
`wl1271_hw_init()` first delegates chip-specific hardware init, reserves all common firmware templates with empty placeholders, configures memory and firmware logging, applies regulatory/DFS config, sets PTA/SoftGemini, initializes target memory config, RX behavior, DCO itrim, TX completion options, RX interrupt pacing, energy detection, fragmentation threshold, data path, PM config, rate management, and hangover settings. On failures after memory-map allocation, it frees `wl->target_mem_map`.

`wl1271_init_vif_specific()` chooses AP or STA initialization based on `wlvif->bss_type`, configures sleep authorization and AP event masks for first roles, applies mode-specific ACX settings, programs PHY defaults, iterates configured AC/TID arrays, configures encryption features, runs post-memory template setup, sets BA policies, and calls chip-specific vif init.

## State and persistence behavior
Initialization consumes persistent `wl->conf` fields and writes live firmware state through ACX and command calls. It mutates event masks, BA counters, `wlvif->ba_support`, `wlvif->ba_allowed`, template reservations, rate-policy indexes, and target memory map ownership. Template memory reservations persist in firmware and are later overwritten with live frame templates.

## Dependencies and integration points
It depends on command/template APIs, ACX configuration functions, TX rate helpers, event unmasking, IO/data path commands, hw_ops chip callbacks, mac80211 vif state, and configuration structures from `conf.h`. It is invoked from wlcore bring-up and interface creation paths.

## Risks
Initialization is order-sensitive. Data path enablement before PM/rate/hangover completion, missing template reservations, mismatched AC/TID counts, or wrong first-AP/first-STA sleep authorization can cause firmware errors or power issues. `BUG_ON(wl->conf.tx.tid_conf_count != wl->conf.tx.ac_conf_count)` makes invalid configuration fatal.

## Test signals
Signals include complete firmware boot, all ACX init stages succeeding, STA association after vif init, AP beacon/probe/deauth/null templates, AP rate policies across ACs, BA session setup, event masks for AP events, data path enablement, recovery from init failures without memory leaks, and debug logs under `DEBUG_BOOT`, `DEBUG_AP`, and `DEBUG_ACX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.h

## Purpose
`init.h` declares the wlcore initialization entry points shared between core bring-up, AP/STA setup, and chip-specific code.

## Important APIs
Declarations include `wl1271_hw_init_power_auth()`, `wl1271_init_templates_config()`, `wl1271_init_pta()`, `wl1271_init_energy_detection()`, `wl1271_chip_specific_init()`, `wl1271_hw_init()`, `wl1271_init_vif_specific()`, `wl1271_init_ap_rates()`, `wl1271_ap_init_templates()`, and `wl1271_sta_hw_init()`.

## Control flow and integration
`wl1271_hw_init()` is the common full-hardware init sequence. `wl1271_init_vif_specific()` is called when a mac80211 vif needs firmware configuration. AP and STA helper declarations allow other modules to reuse mode-specific setup. Some declarations are implemented outside `init.c`, preserving a common init interface across wlcore components.

## State and persistence behavior
The header itself does not manage state. Implementations configure firmware state, templates, ACX settings, and per-vif runtime fields.

## Dependencies and risks
It depends on `wlcore.h` and mac80211 `ieee80211_vif` visibility through included wlcore definitions. Risks are stale declarations or missing implementations during chip split changes.

## Test signals
Compile/link coverage, successful probe-time hardware init, and successful STA/AP vif initialization validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.c

## Purpose
`io.c` implements common wlcore bus and address-partition helpers: bus block-size setup, IRQ enable/disable/synchronize wrappers, virtual-to-physical target address translation, partition programming, and optional bus reset/init callbacks.

## Important APIs and functions
`wl1271_set_block_size()` configures the bus block size through `wl->if_ops`. `wlcore_disable_interrupts()`, `wlcore_disable_interrupts_nosync()`, `wlcore_enable_interrupts()`, and `wlcore_synchronize_interrupts()` wrap Linux IRQ APIs. `wlcore_translate_addr()` maps wlcore virtual target addresses into the current physical partition layout. `wlcore_set_partition()` writes the four partition start/size registers through raw IO and updates `wl->curr_part`. `wl1271_io_reset()` and `wl1271_io_init()` call optional bus-level callbacks.

## Control flow
Address translation checks whether an address falls in memory, register, memory2, or memory3 windows and returns a contiguous physical offset. Partition programming copies the requested partition set into `wl->curr_part`, logs each window, then writes hardware partition registers in order. Errors abort remaining writes and return upward.

## State and persistence behavior
The persistent state is `wl->curr_part`, which all translated IO wrappers use until the next partition change. Hardware partition registers persist in the target until reprogrammed or reset. IRQ state is managed by Linux IRQ core, not stored here.

## Dependencies and integration points
This file depends on bus `if_ops`, register constants from `io.h`, debug logging, and Linux IRQ APIs. `cmd.c`, `event.c`, `debugfs.c`, `init.c`, TX/RX paths, and chip-specific code all rely on the partition and raw/translated IO model.

## Risks
Bad partition state can redirect every translated read/write. `wlcore_translate_addr()` warns and returns zero for out-of-range addresses, so callers may accidentally access physical zero after a bad address. Partition programming comments describe wl12xx/wl18xx register conflicts around partition 3, making changes especially risky. IRQ disable variants must be used in the right context to avoid deadlocks or races.

## Test signals
Signals include successful block-size setup, correct register/memory reads after partition changes, no out-of-range warnings during normal command/event/debugfs access, working suspend/resume IO reset/init, and correct IRQ masking behavior during recovery and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.h

## Purpose
`io.h` declares wlcore IO APIs and implements inline raw, translated, register, data, hardware-address, power, and 32-bit bus access helpers. It is the main abstraction boundary between wlcore core code and the lower SDIO/SPI bus operations.

## Important APIs and helpers
Constants define hardware access ranges and partition register offsets. Declarations cover IRQ wrappers, IO reset/init, address translation, partition setup, block-size setup, and dummy packet TX.

Inline helpers include `wlcore_raw_read()`, `wlcore_raw_write()`, `wlcore_raw_read_data()`, `wlcore_raw_write_data()`, `wlcore_raw_read32()`, `wlcore_raw_write32()`, `wlcore_read()`, `wlcore_write()`, `wlcore_write_data()`, `wlcore_read_data()`, `wlcore_read_hwaddr()`, `wlcore_read32()`, `wlcore_write32()`, `wlcore_read_reg()`, `wlcore_write_reg()`, `wl1271_power_off()`, and `wl1271_power_on()`.

## Control flow
Raw access checks `WL1271_FLAG_IO_FAILED` and rejects most IO while in ELP except the ELP control register. It calls `wl->if_ops->read()` or `write()` and marks IO failed on errors while the device is not off. Translated helpers convert wlcore virtual addresses using `wlcore_translate_addr()`. Register/data helpers index `wl->rtable`. Power helpers call optional bus power callbacks and maintain `WL1271_FLAG_GPIO_POWER`.

## State and persistence behavior
The helpers update `WL1271_FLAG_IO_FAILED` after transport errors and `WL1271_FLAG_GPIO_POWER` after power transitions. They depend on persistent `wl->curr_part`, `wl->rtable`, `wl->buffer_32`, device state, and ELP flags. The IO failed flag persists until higher-level recovery clears or reinitializes state.

## Dependencies and integration points
This header depends on lower bus `if_ops`, partition state from `io.c`, chip address conversion callbacks, and shared wlcore flags. It is included throughout command, event, init, debugfs, TX/RX, and chip-specific code.

## Risks
Because many functions are inline and widely used, error semantics must remain stable. Marking IO failed suppresses later accesses and drives recovery behavior. Returning `-EIO` when in ELP catches illegal sleep-state access but can expose callers that forgot runtime PM wakeup. `wl->buffer_32` is shared scratch storage and must be used under appropriate serialization.

## Test signals
Transport fault injection, ELP access checks, raw and translated 32-bit register reads/writes, power-on/off state transitions, command mailbox IO, debugfs device-memory access, and recovery after IO failure are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/io.h -->
