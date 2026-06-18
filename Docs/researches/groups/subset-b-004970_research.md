# subset-b-004970 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.c

## Purpose
Implements wl12xx-family hardware scan and scheduled-scan operations behind the common wlcore scan hooks. The file translates cfg80211 scan requests into wl1271 firmware command payloads, drives a multi-stage active/passive scan state machine, builds probe-request templates through wlcore command helpers, and starts/stops firmware periodic scans.

## Important APIs, types, and functions
- `wl12xx_scan_start()` starts the scan state machine through `wl1271_scan_stm()`; the cfg80211 request has already been recorded in `wl->scan.req` by common wlcore.
- `wl12xx_scan_stop()` sends `CMD_STOP_SCAN` and rejects calls while the common scan state is idle.
- `wl12xx_scan_completed()` advances the state machine after firmware scan-complete events.
- `wl12xx_sched_scan_start()` configures and starts periodic scanning; `wl12xx_scan_sched_scan_stop()` sends `CMD_STOP_PERIODIC_SCAN`.
- `wl1271_scan_send()` builds `struct wl1271_cmd_scan`, optional split-scan timeout command, probe template, and the final `CMD_SCAN`.
- `wl1271_get_scan_channels()` filters cfg80211 channels into firmware `basic_scan_channel_params` entries and marks each selected request index in `wl->scan.scanned_ch`.
- `wl1271_scan_sched_scan_config()` fills `struct wl1271_cmd_sched_scan_config`, uses wlcore shared SSID/channel helpers, and builds band-specific periodic probe templates.

## Control flow
The immediate scan flow is a four-phase state machine: 2.4 GHz active, 2.4 GHz passive, 5 GHz active, 5 GHz passive. Active phases are skipped when no SSIDs are supplied; passive phases scan remaining channels. Each phase calls `wl1271_scan_send()`, which selects a P2P device role when needed, validates the role id, computes the channel list, fills rate/band/SSID fields, builds a probe request template, sends `CMD_TRIGGER_SCAN_TO`, and then sends `CMD_SCAN`. A local sentinel `WL1271_NOTHING_TO_SCAN` causes recursive state advancement to the next phase without reporting failure.

Scheduled scan first programs an SSID filter list via `wlcore_scan_sched_scan_ssid_list()`, derives channel buckets through `wlcore_set_scan_chan_params()`, copies them into wl12xx firmware layout with `wl12xx_adjust_channels()`, builds 2.4/5 GHz periodic probe templates for active bands, then sends `CMD_CONNECTION_SCAN_CFG`. `wl1271_scan_sched_scan_start()` then sends `CMD_START_PERIODIC_SCAN`.

## State and persistence behavior
State lives in `wl->scan`: `state`, `req`, `ssid`, `ssid_len`, `failed`, `scanned_ch`, and `scan_complete_work`. The file updates `scanned_ch` as channels are consumed so later phases skip them, clears `failed` when reaching `WL1271_SCAN_STATE_DONE`, and queues common completion work immediately. No persistent storage is written; configuration values are read from `wl->conf.scan` and `wl->conf.sched_scan`.

## Dependencies and integration points
Depends on cfg80211/mac80211 scan request structures, common wlcore scan helpers, wlcore command/probe-template helpers, `wl1271_cmd_send()`, wlcore role helpers, wlcore debug/dump utilities, and wlcore TX rate selection. It is wired into the wl12xx lower-driver ops elsewhere and relies on common wlcore event handling to call `wl12xx_scan_completed()`.

## Risks and test signals
Risks include incorrect active/passive filtering for `IEEE80211_CHAN_NO_IR`, failure to clear or initialize `scanned_ch`, invalid role ids for P2P management scans, recursion through empty scan phases, and firmware ABI mismatches in packed command structures. Useful tests are active scan with and without SSIDs, passive-only regulatory channels, 5 GHz disabled/enabled NVS cases, P2P management scans using `dev_role_id`, scheduled scan with no SSIDs forcing passive behavior, split-scan timeout handling, and stop requests during active firmware scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.h

## Purpose
Defines the wl12xx firmware scan command ABI and exports the wl12xx scan/scheduled-scan entry points used by the chip-family operation table.

## Important APIs, types, and functions
- `struct basic_scan_params` and `struct basic_scan_channel_params` are packed firmware payload fragments for normal scans.
- `struct wl1271_cmd_scan` wraps the normal scan header, parameters, fixed-size channel array, and source MAC address.
- `struct wl1271_cmd_sched_scan_config`, `wl1271_cmd_sched_scan_start`, and `wl1271_cmd_sched_scan_stop` describe firmware periodic-scan commands.
- Exports `wl12xx_scan_start()`, `wl12xx_scan_stop()`, `wl12xx_scan_completed()`, `wl12xx_sched_scan_start()`, and `wl12xx_scan_sched_scan_stop()`.

## Control flow
The header itself has no executable flow. Its packed layouts constrain how `scan.c` fills fields before issuing `CMD_SCAN`, `CMD_CONNECTION_SCAN_CFG`, `CMD_START_PERIODIC_SCAN`, and `CMD_STOP_PERIODIC_SCAN`.

## State and persistence behavior
No local state. The structures carry role ids, dwell times, filter thresholds, SSIDs, channel lists, and scan tags to firmware. Endianness annotations identify multi-byte fields that callers must convert.

## Dependencies and integration points
Includes wlcore core, command, and scan headers for common types such as `wl1271_cmd_header`, `conn_scan_ch_params`, and band/channel constants. The wl12xx-specific `WL12XX_MAX_CHANNELS_5GHZ` limit shapes scheduled-scan channel arrays.

## Risks and test signals
Packed firmware ABI drift is the main risk: field order, size, padding, or endian mistakes can corrupt firmware commands. Compile-time size checks would be valuable around firmware API updates. Runtime signals are successful normal scans, periodic scans, and stop commands on wl12xx hardware across both bands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/wl12xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/wl12xx.h

## Purpose
Declares wl12xx chip-family constants, private state, clock enumerations, firmware-version requirements, and firmware-status layouts for WiLink 6/7 chips.

## Important APIs, types, and functions
- Chip ids cover wl127x and wl128x PG revisions.
- Minimum single-role and multi-role firmware version macros drive wlcore firmware validation.
- Resource limits define aggregation buffer size, TX/RX descriptors, MAC addresses, BA sessions, AP station count, and link count.
- `struct wl12xx_priv` stores wl12xx private configuration, reference/TCXO clock selections, and RX memory pool address data.
- Clock enums enumerate supported reference and TCXO clock encodings.
- `struct wl12xx_fw_packet_counters` and `struct wl12xx_fw_status` describe the common firmware status block consumed by wlcore.

## Control flow
No executable flow. These declarations are consumed by wl12xx setup, boot, TX/RX, and firmware-status conversion logic in companion files.

## State and persistence behavior
Defines in-memory runtime state only. `wl12xx_priv` is allocated with the common `wl1271` object and carries configuration/state for one device instance. Firmware status structures mirror volatile device mailboxes and are not persisted.

## Dependencies and integration points
Includes wl12xx `conf.h` and uses wlcore firmware-version sentinel macros, queue/link constants, and Linux integer types. The status layout integrates with common wlcore interrupt/TX/RX processing.

## Risks and test signals
Resource-limit mismatches can break array bounds or mac80211 advertised capabilities. Firmware status ABI changes can corrupt interrupt, RX descriptor, or TX completion handling. Test signals include wl127x/wl128x boot with SR/MR firmware, TX completion accounting, PS/fast link bitmap handling, and 5 GHz enablement through NVS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/wl12xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Kconfig

## Purpose
Adds the kernel configuration option for TI WiLink 8 support.

## Important APIs, types, and functions
- `config WL18XX` is a tristate option labeled "TI wl18xx support".
- It depends on `MAC80211` and selects the common `WLCORE` module.

## Control flow
No runtime control flow. Build-system selection causes the wl18xx lower-driver module to be compiled when enabled and ensures wlcore is present.

## State and persistence behavior
No runtime state. The selected Kconfig value persists in the kernel build configuration.

## Dependencies and integration points
Integrates with Linux Kconfig, mac80211, and the common TI `WLCORE` dependency. The corresponding Makefile builds `wl18xx.o` when `CONFIG_WL18XX` is enabled.

## Risks and test signals
The main risk is missing required dependencies or failing to select wlcore. Build tests should cover builtin and module builds with `CONFIG_WL18XX=m/y`, and disabled builds should omit wl18xx objects cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Makefile

## Purpose
Defines the object composition for the wl18xx chip-family module.

## Important APIs, types, and functions
- `wl18xx-objs` lists `main.o acx.o tx.o io.o debugfs.o scan.o cmd.o event.o`.
- `obj-$(CONFIG_WL18XX) += wl18xx.o` links those objects into the wl18xx module or builtin object.

## Control flow
No runtime flow. Build flow aggregates the listed implementation files into the lower-driver module selected by Kconfig.

## State and persistence behavior
No runtime state. Build output depends on `CONFIG_WL18XX`.

## Dependencies and integration points
Integrates with kbuild and the wlcore module selected by `wl18xx/Kconfig`. The object list is the implementation boundary for WiLink 8-specific overrides.

## Risks and test signals
Omitting a new implementation object would compile-link fail when symbols are referenced, while stale objects can keep dead code in the module. Test with `make M=drivers/net/wireless/ti/wl18xx` or full kernel builds for module and builtin variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.c

## Purpose
Implements WiLink 8-specific ACX firmware configuration helpers. Each helper allocates a packed wl18xx ACX payload, fills it from wlcore or wl18xx configuration, sends it through `wl1271_cmd_configure()`, logs failures, and frees the payload.

## Important APIs, types, and functions
- `wl18xx_acx_host_if_cfg_bitmap()` configures host interface behavior, SDIO block size, extra TX memory blocks, and length-field width.
- `wl18xx_acx_set_checksum_state()` enables firmware checksum offload.
- `wl18xx_acx_clear_statistics()` clears firmware statistics used by debugfs.
- `wl18xx_acx_peer_ht_operation_mode()` updates a peer link between 20 and 40 MHz operation.
- `wl18xx_acx_set_peer_cap()` sets HT capabilities plus supported rates for a link.
- `wl18xx_acx_interrupt_notify_config()` and `wl18xx_acx_rx_ba_filter()` tune notification behavior during suspend.
- `wl18xx_acx_ap_sleep()`, `wl18xx_acx_dynamic_fw_traces()`, and `wl18xx_acx_time_sync_cfg()` configure AP sleep, dynamic firmware trace mask, and time sync parameters.

## Control flow
The functions all follow a linear pattern: allocate with `kzalloc_obj()`, fill command fields, convert multi-byte fields with `cpu_to_le*()` where required, call `wl1271_cmd_configure()` with the appropriate ACX id, handle negative status, then free. They are invoked from wl18xx setup/init paths, debugfs writes, suspend/resume hooks, AP sleep handling, and peer capability/rate-control updates via `wl18xx_ops`.

## State and persistence behavior
No persistent storage is written. Firmware state is changed by successful ACX commands. Host-side inputs come from `wl->dynamic_fw_traces`, `wl->conf.sg`, `wl->zone_master_mac_addr`, and `priv->conf.ap_sleep`. The command payloads are transient heap allocations.

## Dependencies and integration points
Depends on common wlcore command/debug headers, wlcore ACX base definitions, and wl18xx ACX structures. Integrated through `wl18xx/main.c` operations such as `interrupt_notify`, `rx_ba_filter`, `ap_sleep`, `set_peer_cap`, `hw_init`, and debugfs callbacks.

## Risks and test signals
Risks are wrong ACX ids, missing endian conversions, toggling checksum offload without matching TX/RX descriptor handling, and AP sleep/time sync settings that do not match firmware expectations. Test signals include successful boot `hw_init`, debugfs dynamic trace updates while device is on, suspend/resume notification filtering, HT bandwidth changes, and AP sleep configuration on AP roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.h

## Purpose
Defines the WiLink 8-specific ACX command ids, interrupt masks, firmware statistics layout, and packed payload structures used by `wl18xx/acx.c`, debugfs, and wl18xx runtime operations.

## Important APIs, types, and functions
- ACX ids `ACX_NS_IPV6_FILTER` through `ACX_TIME_SYNC_CFG` extend the common wlcore ACX namespace.
- `WL18XX_ACX_EVENTS_VECTOR` and `WL18XX_INTR_MASK` declare interrupt/event bits enabled by wl18xx.
- `struct wl18xx_acx_host_config_bitmap`, checksum, peer-capability, notification, RX BA filter, AP sleep, dynamic trace, and time-sync structures are command payload ABIs.
- `struct wl18xx_acx_statistics` aggregates nested error, TX, RX, ISR, power, filter, rate, aggregation, pipeline, diversity, thermal, calibration, roaming, and DFS counters.
- Function prototypes expose the wl18xx ACX helper surface.

## Control flow
No executable flow. The structures constrain callers that build ACX commands and debugfs stat readers that interpret firmware statistics.

## State and persistence behavior
The header describes firmware-owned state snapshots and configuration payloads. Statistics are volatile firmware counters. Configuration structures become firmware state only when sent by `wl1271_cmd_configure()`.

## Dependencies and integration points
Includes wlcore core and common ACX definitions. The statistics layout is used by `wl18xx/debugfs.c`; command payloads are used by `wl18xx/acx.c`; event and interrupt masks are used by `wl18xx/main.c` boot/interrupt setup.

## Risks and test signals
Because all structures are packed firmware ABIs, field order, size, alignment, and endian annotations are high-risk. Debugfs counter reads, firmware statistics clear, interrupt delivery, checksum enablement, peer HT updates, and AP sleep/time sync commands are the main runtime test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.c

## Purpose
Implements WiLink 8-specific firmware commands that are not generic ACX configuration: channel switch, Smart Config, DFS CAC, radar debug, and DFS master restart.

## Important APIs, types, and functions
- `wl18xx_cmd_channel_switch()` converts mac80211 channel-switch data into `CMD_CHANNEL_SWITCH`, including band, switch time, TX stop flag, channel type, and supported-rate mask.
- `wl18xx_cmd_smart_config_start()`, `wl18xx_cmd_smart_config_stop()`, and `wl18xx_cmd_smart_config_set_group_key()` control vendor Smart Config behavior.
- `wl18xx_cmd_set_cac()` starts/stops DFS channel availability check with role/channel/bandwidth.
- `wl18xx_cmd_radar_detection_debug()` triggers firmware radar detection debug for a supplied channel.
- `wl18xx_cmd_dfs_master_restart()` restarts DFS master operation for an AP role.

## Control flow
Each command allocates the matching packed command structure, fills role/channel/rate/key fields, sends the correct `CMD_*` via `wl1271_cmd_send()`, handles negative errors, and frees. Channel switch selects 2.4/5 GHz band explicitly, derives rates from common wlcore hardware callbacks, and strips CCK rates for P2P. Smart Config key setting validates exact key length before allocation.

## State and persistence behavior
No host-side persistent state is changed, except firmware command effects. Commands depend on current `wlvif` state such as `role_id`, `channel`, `band`, `channel_type`, `bss_type`, and P2P flag.

## Dependencies and integration points
Depends on wlcore command, debug, and hardware-ops helpers. `wl18xx/main.c` exposes these through `wlcore_ops` for channel switch, Smart Config, CAC, and DFS master restart; `debugfs.c` calls radar debug.

## Risks and test signals
Risks include invalid band mapping, rate masks inconsistent with peer/AP capabilities, accepting wrong Smart Config key lengths, and DFS commands on invalid roles. Test with CSA in STA/AP/P2P modes, P2P channel switches without CCK, Smart Config vendor commands/events, DFS CAC start/stop on 5 GHz, and certification radar debug hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.h

## Purpose
Declares WiLink 8-specific firmware command payloads and prototypes for command helpers implemented in `cmd.c`.

## Important APIs, types, and functions
- `struct wl18xx_cmd_channel_switch` carries role, target channel, switch timing, local supported rates, channel type, and band.
- Smart Config payloads include group bitmap and 16-byte group key command structures.
- DFS payloads include radar debug channel and DFS master restart role id.
- Prototypes expose channel switch, Smart Config start/stop/key, CAC, radar debug, and DFS master restart.

## Control flow
No executable flow. Callers allocate/fill/send these structures through `wl1271_cmd_send()`.

## State and persistence behavior
No local state. Structures describe transient command payloads that mutate firmware state when sent.

## Dependencies and integration points
Includes wlcore core and ACX headers for base command header and driver types. Used by `wl18xx/cmd.c`, `wl18xx/debugfs.c`, and `wl18xx/main.c` operation-table setup.

## Risks and test signals
Firmware ABI accuracy is the main risk. Build tests catch prototype drift; runtime signals include successful CSA, Smart Config operation, DFS CAC, radar debug, and master restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/conf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/conf.h

## Purpose
Defines the WiLink 8 private configuration ABI layered on top of common `wlcore_conf`. It covers configuration file identity, PHY/MAC board parameters, HT mode, AP sleep, and SoftGemini coexistence parameter indexes.

## Important APIs, types, and functions
- `WL18XX_CONF_MAGIC`, `WL18XX_CONF_VERSION`, `WL18XX_CONF_SIZE`, and `WL18XX_CONF_MASK` validate binary configuration files.
- `struct wl18xx_mac_and_phy_params` is copied wholesale to firmware PHY init memory and includes FEM/antenna/clock/power-limit/trace-loss/board-type fields.
- `enum wl18xx_ht_mode` and `struct wl18xx_ht_settings` choose default, wide SISO40, or SISO20 HT capabilities.
- `struct conf_ap_sleep_settings` and `struct wl18xx_priv_conf` define wl18xx-private configuration blocks.
- `enum wl18xx_sg_params` maps WiLink 8 SoftGemini/BT coexistence parameter indexes.

## Control flow
No executable flow. `wl18xx/main.c` loads this layout from firmware configuration files or defaults, lets module parameters override select fields, and writes the PHY block to firmware.

## State and persistence behavior
Configuration is stored in `struct wl18xx_priv` for a device instance. A binary firmware config file persists outside the driver and is validated by magic/version/size. The PHY subset is copied into device memory during boot.

## Dependencies and integration points
Depends on common `WLCORE_CONF_VERSION`, `WLCORE_CONF_SIZE`, and wlcore SoftGemini parameter capacity. Integrated by `wl18xx_load_conf_file()`, `wl18xx_conf_init()`, `wl18xx_set_mac_and_phy()`, `wl18xx_acx_ap_sleep()`, and debugfs config dump.

## Risks and test signals
Risks include binary config size/version mismatch, invalid board/FEM/antenna parameters, wrong HT mode advertisement, and PHY payload exceeding `WL18XX_PHY_INIT_MEM_SIZE`. Test signals include boot with and without external config file, module parameter overrides, 2.4/5 GHz antenna enablement, AP sleep ACX programming, and debugfs `conf` output matching expected size/magic/version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.c

## Purpose
Adds wl18xx-specific debugfs files for firmware statistics, configuration export, DFS/radar test hooks, and dynamic firmware trace control.

## Important APIs, types, and functions
- `WL18XX_DEBUGFS_FWSTATS_FILE*` macros instantiate readers for fields in `struct wl18xx_acx_statistics`.
- `conf_read()` exports a binary configuration image containing wl18xx header, common wlcore config, and wl18xx private config.
- `clear_fw_stats_write()` sends `ACX_CLEAR_STATISTICS`.
- `radar_detection_write()` parses a channel and sends firmware radar debug command.
- `dynamic_fw_traces_write/read()` updates `wl->dynamic_fw_traces` and, when the device is on, sends `ACX_DYNAMIC_TRACES_CFG`.
- Optional `radar_debug_mode_write/read()` toggles certification radar debug mode and propagates it to AP roles.
- `wl18xx_debugfs_add_files()` creates the module directory, `fw_stats` tree, and control files.

## Control flow
Reader/writer callbacks acquire `wl->mutex` around shared driver state. Runtime firmware commands are skipped when `wl->state != WLCORE_STATE_ON`; commands that require active hardware resume the device with `pm_runtime_resume_and_get()` and release with `pm_runtime_put_autosuspend()`. The add-files function registers many statistic leaves then adds control files.

## State and persistence behavior
Debugfs is runtime-only. `dynamic_fw_traces_write()` persists the requested trace mask in `wl->dynamic_fw_traces` for later init/reconfiguration. `radar_debug_mode_write()` updates `wl->radar_debug_mode`. `conf_read()` snapshots current config but does not modify it.

## Dependencies and integration points
Depends on common wlcore debugfs macros, PM runtime, wlcore state/mutex, wlcore PS/debug helpers, wl18xx ACX and command helpers, and optional `CONFIG_CFG80211_CERTIFICATION_ONUS`. Called from `wl18xx_ops.debugfs_init`.

## Risks and test signals
Risks include exposing stale stats if firmware statistic layout changes, PM runtime imbalance on command failures, accepting invalid debug inputs, and certification-only radar behavior leaking into normal builds. Test signals are debugfs file creation, successful stats reads, `clear_fw_stats` while on/off, `dynamic_fw_traces` persistence across off/on states, radar debug command with valid/invalid channel text, and config dump size/magic/version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.h

## Purpose
Declares the wl18xx debugfs initialization hook.

## Important APIs, types, and functions
- `wl18xx_debugfs_add_files(struct wl1271 *wl, struct dentry *rootdir)` registers wl18xx debugfs files beneath the wlcore root.

## Control flow
No executable flow. The function is called through `wl18xx_ops.debugfs_init`.

## State and persistence behavior
No local state. The implementation creates runtime debugfs dentries and control callbacks.

## Dependencies and integration points
Uses `struct wl1271` and `struct dentry` from wlcore/Linux debugfs context. Integrated by `wl18xx/main.c`.

## Risks and test signals
Risk is prototype drift with the implementation or wlcore ops table. Build tests catch that; runtime test is presence of wl18xx debugfs directory and controls after device probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.c

## Purpose
Processes WiLink 8 firmware mailbox events and maps them to common wlcore/mac80211/cfg80211 behavior. Also implements wait-for-event mapping for a small set of wlcore wait events.

## Important APIs, types, and functions
- `wl18xx_wait_for_event()` maps wlcore wait events to local firmware event bits and calls `wlcore_cmd_wait_for_event_or_timeout()`.
- `wl18xx_process_mailbox_events()` decodes `wl18xx_event_mailbox.events_vector` and dispatches scan, DFS, RSSI, BA, beacon-loss, channel-switch, ROC, Smart Config, firmware logger, and RX BA window-size events.
- `wlcore_smart_config_sync_event()` and `wlcore_smart_config_decode_event()` emit cfg80211 vendor events.
- `wlcore_event_time_sync()` logs firmware TSF time-sync values.

## Control flow
On each mailbox interrupt, the common core points `wl->mbox` at a `struct wl18xx_event_mailbox`; this file reads the little-endian event vector and checks each bit. Some events call common wlcore handlers directly, scan-complete calls `wl18xx_scan_completed()` on `wl->scan_wlvif`, and radar events call `ieee80211_radar_detected()` unless debug mode is active. RX BA window change finds the affected station and stops RX BA sessions after updating `max_rx_aggregation_subframes`.

## State and persistence behavior
The event path mutates transient driver/mac80211 state: scan completion work, RSSI trigger events, BA constraints, channel switch completion, link aggregation window size, and radar state in mac80211. No persistent storage is written.

## Dependencies and integration points
Depends on cfg80211 vendor events, mac80211 radar/BA APIs, common wlcore event handlers, wl18xx scan/event structures, wlcore vendor command attribute ids, and `wl->links[]` link metadata. Wired into `wl18xx_ops.process_mailbox_events` and `wait_for_event`.

## Risks and test signals
Risks include missing event bits in masks, wrong endian conversion on bitmaps, NULL link/vif assumptions for RX BA window changes, vendor event allocation failures, and radar debug suppressing real DFS notifications. Test scan completion, periodic scan reports/completion, DFS radar detection, beacon loss, max TX failure in AP mode, ROC completion, Smart Config sync/decode vendor events, firmware logger indication, and RX BA window change with active station.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.h

## Purpose
Defines WiLink 8 mailbox event bits, radar type ids, the packed event mailbox ABI, and event function prototypes.

## Important APIs, types, and functions
- Event bit macros cover scan completion, DFS/radar, channel switch, BSS loss, TX failure, inactive STA, periodic scan, BA constraints, ROC, DFS config, Smart Config, RSSI/SNR, firmware logging, time sync, and RX BA window-size change.
- `enum wl18xx_radar_types` differentiates regular, chirp, and no-radar types.
- `struct wl18xx_event_mailbox` carries vector, counters, bitmaps, TSF parts, Smart Config payloads, channel/band fields, and radar data.
- Prototypes expose `wl18xx_wait_for_event()` and `wl18xx_process_mailbox_events()`.

## Control flow
No executable flow. `event.c` interprets this mailbox layout after firmware writes it.

## State and persistence behavior
The mailbox is volatile firmware-to-host state. It is read during event handling and not persisted.

## Dependencies and integration points
Includes wlcore core definitions. The mailbox size is passed to `wlcore_alloc_hw()` in wl18xx probe, and event masks are set during boot in `wl18xx/main.c`.

## Risks and test signals
ABI drift in the mailbox layout or event bit values can misroute events. Test signals are correct handling of each event type, especially little-endian bitmaps and Smart Config variable-length arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.c

## Purpose
Provides 16-bit top-register read/write helpers on top of wlcore 32-bit register access for WiLink 8 PRCM/top-register programming.

## Important APIs, types, and functions
- `wl18xx_top_reg_write()` validates 2-byte alignment, reads the containing 32-bit word, replaces the lower or upper halfword, and writes it back.
- `wl18xx_top_reg_read()` validates 2-byte alignment, reads the containing 32-bit word, and extracts the lower or upper halfword.

## Control flow
The helpers branch on `addr % 4`: 32-bit-aligned addresses use the low halfword; 2-byte-offset addresses access the previous word and use the high halfword. Odd addresses trigger `WARN_ON()` and `-EINVAL`.

## State and persistence behavior
No host persistent state. Successful writes mutate hardware top registers; reads populate the caller-provided output pointer when non-NULL.

## Dependencies and integration points
Depends on `wlcore_read32()` and `wlcore_write32()` after the caller has selected the correct partition. Used by wl18xx clock and interrupt polarity setup in `main.c`.

## Risks and test signals
Read-modify-write can clobber adjacent halfwords if concurrent access is not serialized by higher-level locking. Wrong partition selection by callers accesses the wrong register bank. Test signals include successful clock setup, IRQ inversion setup for low/falling IRQs, and warnings on invalid odd addresses in fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.h

## Purpose
Declares WiLink 8 top-register 16-bit access helpers.

## Important APIs, types, and functions
- `wl18xx_top_reg_write()` and `wl18xx_top_reg_read()` are marked `__must_check` so callers handle hardware I/O errors.

## Control flow
No executable flow.

## State and persistence behavior
No local state. Implementations mutate or read hardware top registers.

## Dependencies and integration points
Uses `struct wl1271` from wlcore context. Included by `wl18xx/main.c` and `wl18xx/io.c`.

## Risks and test signals
Risk is ignored return values or prototype drift. Build warnings enforce `__must_check`; boot clock setup is the primary runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/main.c

## Purpose
Main WiLink 8 lower-driver implementation. It supplies wl18xx defaults, hardware tables, boot sequencing, firmware-status conversion, TX/RX descriptor semantics, HT capability advertisement, module-parameter overrides, and the `wlcore_ops` table that lets common wlcore drive wl18xx hardware.

## Important APIs, types, and functions
- Defaults: `wl18xx_conf` and `wl18xx_default_priv_conf` seed common/private configuration when a binary config file is absent.
- Hardware tables: `wl18xx_ptable`, `wl18xx_rtable`, rate-index maps, and PLL clock tables describe address partitions, registers, rates, and clock setup.
- Boot/setup: `wl18xx_identify_chip()`, `wl18xx_set_clk()`, `wl18xx_pre_boot()`, `wl18xx_pre_upload()`, `wl18xx_set_mac_and_phy()`, `wl18xx_boot()`, `wl18xx_enable_interrupts()`.
- Runtime ops: command trigger/ack, TX block math, TX/RX descriptor helpers, checksum hooks, status conversion, link priority, key handling, rate-mask helpers, and scan/event/debugfs callbacks.
- Config and platform: `wl18xx_load_conf_file()`, `wl18xx_conf_init()`, `wl18xx_setup()`, `wl18xx_probe()`, `module_platform_driver()`, module parameters, and `MODULE_FIRMWARE()`.

## Control flow
Probe allocates common wlcore hardware with wl18xx private data and mailbox size, assigns `wl18xx_ops` and partition table, then calls `wlcore_probe()`. Setup fills wlcore limits/capabilities, loads config or defaults, applies module parameters, selects HT capabilities, and enables 5 GHz only when antennas are configured. Boot programs clocks and PRCM state, performs pre-upload workarounds, uploads firmware, writes PHY/MAC params to PHY init memory, sets event masks, runs firmware through common boot code, and enables interrupts.

At runtime wlcore calls this file through `wlcore_ops`: command mailbox writes are padded to `WL18XX_CMD_MAX_SIZE`, TX descriptors use 268-byte block math and optional last-frame SDIO padding, firmware status is converted according to firmware API major version, checksum offload annotates TX descriptors and RX skbs when enabled, and link priority thresholds are read from the firmware status private block.

## State and persistence behavior
Per-device state is in `struct wl1271` plus `struct wl18xx_priv`: private config, command buffer, `last_fw_rls_idx`, and extra spare-key count. Persistent inputs are firmware (`WL18XX_FW_NAME`) and optional binary configuration file named by platform data. Module parameters are read-only after load and override config values. Boot writes hardware registers, PHY init memory, and firmware state; no files are written by the driver.

## Dependencies and integration points
Integrates Linux platform driver, firmware loader, mac80211/cfg80211, wlcore core/boot/io/tx/rx/acx APIs, wl18xx ACX/command/scan/event/debugfs modules, and platform data family names. It is the registration point for all wl18xx callbacks consumed by wlcore.

## Risks and test signals
High-risk areas are firmware ABI version handling, config file size/magic/version validation, clock/partition/register programming, event mask coverage, checksum offload consistency, firmware status structure selection, HT capability choices from antenna/config/module params, and spare-block updates for TKIP/GEM keys. Test signals include probe/remove, boot with real firmware/config fallback, PG/fuse logging, random MAC fallback, 2.4/5 GHz capability advertisement, checksum on/off traffic, TKIP/GEM key add/remove, scan and scheduled scan, DFS CAC/radar, channel switch, suspend notification filtering, and recovery reinitializing private counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/reg.h

## Purpose
Defines WiLink 8 base addresses for register, code, data, double-buffer, MCU key-search, and related memory regions.

## Important APIs, types, and functions
- `WL18XX_REGISTERS_BASE`, `WL18XX_CODE_BASE`, `WL18XX_DATA_BASE`, `WL18XX_DOUBLE_BUFFER_BASE`, and `WL18XX_MCU_KEY_SEARCH_BASE` identify hardware address regions.

## Control flow
No executable flow.

## State and persistence behavior
No state. Constants are used to calculate hardware addresses.

## Dependencies and integration points
Included by wl18xx main/reg programming code alongside larger register definitions from surrounding headers. These constants contribute to partition and register access decisions.

## Risks and test signals
Wrong base addresses break all hardware access for affected regions. Boot register reads/writes, firmware upload, and data-path access are the practical test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.c

## Purpose
Implements WiLink 8 immediate and scheduled scanning using the wl18xx unified firmware `CMD_SCAN` layout, plus scan stop and completion hooks for wlcore.

## Important APIs, types, and functions
- `wl18xx_scan_start()` sends a normal search scan through `wl18xx_scan_send()`.
- `wl18xx_scan_stop()` and `wl18xx_scan_sched_scan_stop()` use `__wl18xx_scan_stop()` with search or periodic scan type.
- `wl18xx_scan_completed()` clears scan failure and queues common scan completion work.
- `wl18xx_sched_scan_start()` configures periodic scanning through `wl18xx_scan_sched_scan_config()`.
- `wl18xx_adjust_channels()` copies shared wlcore channel-bucket output into wl18xx command fields.

## Control flow
Normal scan allocates `struct wl18xx_cmd_scan_params`, selects device or role id, fills search-scan defaults, uses `wlcore_set_scan_chan_params()` to classify channels, sets total cycles to one, adjusts rate when `no_cck` is set, copies first SSID if present, builds active 2.4 GHz and active/DFS 5 GHz probe templates, then sends `CMD_SCAN`.

Scheduled scan builds the firmware SSID list, allocates the same command structure with `SCAN_TYPE_PERIODIC`, fills filter and threshold fields, computes short/long interval cycle fields from firmware config and cfg80211 scan plan, builds periodic probe templates, sets report threshold, and sends `CMD_SCAN`. Stopping sends `CMD_STOP_SCAN` with role and scan type.

## State and persistence behavior
Immediate completion mutates `wl->scan.failed` and queues `wl->scan_complete_work`. Scheduled scan configuration is held by firmware after `CMD_SCAN`; no host persistent state is written. Inputs come from `wl->conf.scan`, `wl->conf.sched_scan`, `wlvif` role ids, and cfg80211 requests.

## Dependencies and integration points
Depends on common wlcore scan helpers, probe template builder, wlcore command send path, mac80211 workqueue helpers, and wl18xx scan ABI. Exposed through `wl18xx_ops.scan_start`, `scan_stop`, `sched_scan_start`, and `sched_scan_stop`; completion is triggered by `event.c`.

## Risks and test signals
Risks include `WARN_ON(req->n_ssids > 1)` because only the first SSID is copied, no explicit empty-channel failure after `wlcore_set_scan_chan_params()`, active/DFS probe-template band handling, role id validity for P2P management, and interval truncation to 16-bit fields. Test normal scans with no SSID, one SSID, no-CCK, DFS channels, P2P device role, scheduled scan with short/long plan behavior, stop for both scan types, and firmware scan-complete events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.h

## Purpose
Defines the WiLink 8 unified scan command ABI and scan function prototypes.

## Important APIs, types, and functions
- `struct tracking_ch_params` extends common channel params with BSSID fields for tracking scans.
- Probe request rate enum defines 1, 5.5, and 6 Mbps firmware encodings.
- `WL18XX_MAX_CHANNELS_5GHZ` raises the 5 GHz channel array size to 32.
- `struct wl18xx_cmd_scan_params` contains role, scan type, thresholds, filter flags, channel buckets, cycle timing, SSID, rate, and report/termination controls.
- `struct wl18xx_cmd_scan_stop` carries role id and scan type for `CMD_STOP_SCAN`.
- Prototypes expose normal and scheduled scan operations.

## Control flow
No executable flow. `scan.c` fills these structures for search and periodic scan commands.

## State and persistence behavior
No local state. Packed structures describe transient firmware command payloads that install scan state in firmware.

## Dependencies and integration points
Includes wlcore core, command, and common scan headers. The anonymous union in `wl18xx_cmd_scan_params` lets callers use either per-band channel arrays or tracking-scan channels against the same firmware area.

## Risks and test signals
ABI size/packing and channel array bounds are primary risks. Runtime tests are successful immediate/scheduled scans across 2.4/5 GHz, DFS scans, and stop commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.c

## Purpose
Handles WiLink 8 immediate TX completion status: maps firmware release descriptors to host skbs, fills mac80211 TX status, returns completed frames to the netstack worker, and updates per-link last-rate data.

## Important APIs, types, and functions
- `wl18xx_tx_immediate_complete()` consumes the firmware release ring from `wl18xx_fw_status_priv`.
- `wl18xx_tx_complete_packet()` validates a TX descriptor id, determines success, fills `ieee80211_tx_info`, handles dummy packets, strips private/TKIP header space, queues the skb for common netstack completion, and frees the TX id.
- `wl18xx_get_last_tx_rate()` converts firmware rate indexes into mac80211 legacy or MCS rate status flags, including SGI and HT40.
- `wl18xx_next_tx_idx()` wraps the firmware TX-status descriptor ring.

## Control flow
On each immediate completion callback, the function compares `priv->last_fw_rls_idx` with firmware `fw_release_idx`. If changed, it updates the last-rate cache for the reported HLID, validates the release index, then iterates ring entries from the previous index to the new one, completing each packet and incrementing `wl->tx_results_count`. The completion helper returns dummy packets internally; normal packets are pulled back to the original frame, annotated, queued on `wl->deferred_tx_queue`, and completed asynchronously by `netstack_work`.

## State and persistence behavior
Mutates `priv->last_fw_rls_idx`, `wl->links[hlid].fw_rate_idx`, `fw_rate_mbps`, `wl->stats.retry_count`, `wl->tx_results_count`, `wl->tx_frames[]`, the deferred completion queue, and TX id allocation state. No persistent storage.

## Dependencies and integration points
Depends on common wlcore TX descriptor definitions, mac80211 `ieee80211_tx_info`, SKB helpers, workqueues, and wl18xx firmware status private layout. Called through `wl18xx_ops.tx_immediate_compl`.

## Risks and test signals
Risks include invalid firmware release indexes, stale/null `tx_frames` entries, rate-index conversion errors for SGI/HT40/MIMO, TKIP header restoration bugs, and completion ring wraparound. Test heavy TX traffic, failures/no-ACK, dummy packets, TKIP encrypted traffic, HT20/HT40 MCS rates, ring wrap, and firmware recovery after invalid status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.h

## Purpose
Defines WiLink 8 TX constants and the immediate TX completion prototype.

## Important APIs, types, and functions
- `WL18XX_TX_HW_BLOCK_SPARE`, `WL18XX_TX_HW_EXTRA_BLOCK_SPARE`, and `WL18XX_TX_HW_BLOCK_SIZE` shape TX memory-block accounting.
- TX status macros split descriptor id and success/failure bit from firmware status bytes.
- `WL18XX_TX_CTRL_NOT_PADDED` marks frames not padded to SDIO block size.
- `CONF_TX_RATE_USE_WIDE_CHAN` is a firmware rate-policy flag for wide channels.
- `wl18xx_tx_immediate_complete()` is exported to wl18xx ops.

## Control flow
No executable flow. Constants are consumed by `tx.c` and `main.c` TX descriptor setup.

## State and persistence behavior
No local state. Constants influence firmware TX descriptor and rate-policy state.

## Dependencies and integration points
Includes wlcore core definitions. Integrated by wl18xx TX completion and descriptor helpers.

## Risks and test signals
Wrong block size/spare counts can cause firmware memory accounting failures; wrong status masks corrupt TX completion. Test with normal traffic, TKIP/GEM extra spare blocks, SDIO padding, and HT40 rate policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/wl18xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/wl18xx.h

## Purpose
Declares WiLink 8 chip constants, private driver state, firmware-status ABI variants, PHY/static-data structures, and clock configuration types.

## Important APIs, types, and functions
- Minimum firmware macros require chip version 8, interface 9, major 0, minor 58, with subtype ignored.
- Resource constants define command size, aggregation buffer, descriptor counts, MAC addresses, BA sessions, AP stations, and links.
- `struct wl18xx_priv` stores command buffer, private config, TX release index, and extra spare-key count.
- `struct wl18xx_fw_status_priv`, packet counters, `wl18xx_fw_status`, and `wl18xx_fw_status_8_9_1` mirror firmware status layouts for different API versions.
- `struct wl18xx_static_data_priv` carries PHY firmware version from static data.
- `struct wl18xx_clk_cfg` and clock enum support PLL programming.

## Control flow
No executable flow. `main.c` fills/reads these structures during setup, boot, firmware-status conversion, and TX completion.

## State and persistence behavior
Defines per-device in-memory state and volatile firmware status snapshots. No persistent files. The command buffer is reused for firmware command writes; `extra_spare_key_count` persists until keys are removed or hardware is reinitialized.

## Dependencies and integration points
Includes wl18xx private `conf.h`. Used by almost every wl18xx implementation file and by common wlcore through allocated private data/status lengths.

## Risks and test signals
Firmware status ABI mismatches can break interrupt, RX, TX, and logger handling. Resource constants must remain consistent with firmware and wlcore array bounds. Test boot on firmware versions using both status layouts, TX completion, link suspend/priority thresholds, command size handling, and key add/remove spare-block accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/wl18xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Kconfig

## Purpose
Defines build-time options for the common TI wlcore module and its SPI/SDIO transport modules.

## Important APIs, types, and functions
- `config WLCORE` is the common mac80211-based TI WLAN core and selects `FW_LOADER`.
- `config WLCORE_SPI` depends on `WLCORE`, `SPI_MASTER`, and `OF`, and selects `CRC7`.
- `config WLCORE_SDIO` depends on `WLCORE` and `MMC`.

## Control flow
No runtime flow. Kconfig controls which common and transport modules are built.

## State and persistence behavior
No runtime state. Values persist in the kernel build configuration.

## Dependencies and integration points
Chip-family modules such as wl18xx select or depend on `WLCORE`. Transport modules provide bus-specific access under the common wlcore abstraction.

## Risks and test signals
Dependency mistakes cause broken build combinations or missing firmware loader/transport support. Test builtin/module/disabled combinations for wlcore, SPI, SDIO, OF, MMC, and mac80211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Makefile

## Purpose
Defines object composition for the common wlcore module and its SPI/SDIO transport modules.

## Important APIs, types, and functions
- `wlcore-objs` includes common main, command, I/O, event, TX/RX, power-save, ACX, boot, init, debugfs, scan, sysfs, and vendor command objects.
- `wlcore_spi-objs` and `wlcore_sdio-objs` build transport implementations.
- Testmode support is conditionally added when `CONFIG_NL80211_TESTMODE` is enabled.

## Control flow
No runtime flow. kbuild combines objects according to Kconfig symbols.

## State and persistence behavior
No runtime state. Build outputs depend on configuration.

## Dependencies and integration points
Integrates the common wlcore implementation used by wl12xx/wl18xx lower drivers and bus modules.

## Risks and test signals
Object-list drift can cause unresolved symbols or missing runtime features. Build tests should cover wlcore, wlcore_spi, wlcore_sdio, and NL80211 testmode configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.c

## Purpose
Implements the common wlcore ACX configuration/interrogation layer used by TI chip-family lower drivers. It translates wlcore/mac80211 state and `wl->conf` policy into packed firmware information elements for power management, RX/TX behavior, rate policies, beacon filtering, aggregation, coexistence, memory layout, statistics, and optional PM RX filters.

## Important APIs, types, and functions
- Power/save/connectivity helpers include wake-up conditions, sleep authorization, PM config, keep-alive mode/config, beacon/DTIM options, BET, ARP filtering, RSSI/SNR triggers, and connection monitor parameters.
- TX/RX/rate helpers include TX power, RX MSDU lifetime, RTS/fragment thresholds, CCA threshold, service period timeout, AC/TID config, TX options, STA/AP rate policies, rate-management params, hangover, PS RX streaming, and AP max retry.
- Association/HT helpers include AID, preamble, CTS protection, HT capabilities/information, BA initiator policy, BA receiver setup, TSF interrogation, in-connection STA list, and average RSSI interrogation.
- Initialization/statistics helpers include memory config, memory-map interrogation, RX interrupt config, event mailbox mask, firmware statistics interrogation, SoftGemini enable/config, FM coexistence, and feature config.
- Optional `CONFIG_PM` helpers configure default and per-pattern RX data filters.

## Control flow
Most helpers allocate a command-specific structure, fill role/config fields, convert little-endian fields, call `wl1271_cmd_configure()` or `wl1271_cmd_interrogate()`, handle firmware status, and free. Some functions loop over configuration arrays: beacon filter IE rules, SoftGemini parameters, PS RX streaming queues, and rate policy classes. BA receiver setup uses `wlcore_cmd_configure_failsafe()` to translate a firmware "no RX BA session" status into `-EBUSY`.

## State and persistence behavior
The file mutates firmware state extensively. Host-side persistent runtime changes are limited but important: `wl->sleep_auth` is cached after sleep authorization, `wl->target_mem_map` is allocated and populated by memory-map interrogation, `wl->tx_blocks_available` is seeded from firmware memory map, and `wlvif->last_rssi_event` is reset before RSSI trigger configuration. All heap command buffers are transient.

## Dependencies and integration points
Depends on common wlcore command transport, debug logging, wlcore hardware callbacks for rate masks, mac80211 constants, PM RX filter flattening helpers, and `wl->conf` structures from `conf.h`. Called by wlcore main/init/PS/RX/TX paths and lower-driver setup operations such as wl18xx.

## Risks and test signals
Risks include firmware ABI field mismatch, missing endian conversions, unchecked multicast list length relative to fixed table capacity, invalid configuration values flowing from `wl->conf`, memory-map allocation leaks on partial failures, BA failsafe status handling, and PM filter flexible-array sizing. Test signals include association and AP startup, power-save entry/exit, beacon filtering, multicast filtering, ARP offload, rate policy updates, HT/BA negotiation, TSF reads, firmware stats reads, memory-map initialization, RX interrupt threshold behavior, SoftGemini/FM coexistence config, and suspend RX filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.h

## Purpose
Defines the common wlcore ACX firmware ABI: interrupt bits, ACX header, packed payload structures, constants/enums, ACX numeric ids, and prototypes for the common ACX helper functions.

## Important APIs, types, and functions
- Interrupt masks include watchdog, init-complete, event mailboxes, command complete, hardware available, data, trace, and software watchdog bits.
- `struct acx_header` is the common command/information-element prefix with id and length.
- Payload structures cover sleep auth, roles, PSM, RX/TX lifetimes, slots, multicast groups, beacon filtering, event masks, feature config, TX power, wake-up conditions, AID, preamble/CTS, rate policy, AC/TID config, memory config/map, RX config, BET, ARP, PM, keep-alive, RSSI/SNR, HT, BA, TSF, streaming, AP retry, PS config, FM coexistence, rate management, hangover, RX filters, and roaming stats.
- ACX id enum maps symbolic names to firmware numeric ids.
- Function prototypes match `acx.c`, including optional PM filter helpers.

## Control flow
No executable flow. The header constrains every ACX command/interrogate transaction built by wlcore and lower drivers.

## State and persistence behavior
No local state. Packed structures describe transient command payloads or volatile firmware response snapshots. Some payload fields correspond to firmware state that persists until reconfigured or reset.

## Dependencies and integration points
Includes wlcore and command headers and is included by common wlcore modules and chip-family modules such as wl18xx. It is the central compatibility contract between host driver and TI firmware for configuration.

## Risks and test signals
Highest risk is ABI drift: packing, flexible-array sizing, endian annotations, enum/id values, and fixed table lengths. Compile tests catch only syntax; runtime tests must cover boot/init, association, AP mode, scans, power save, BA, RX filters, statistics, event masks, and all lower-driver ACX extensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.c

## Purpose
Implements the common wlcore firmware boot pipeline: firmware image upload, NVS upload, firmware start/handshake, firmware-version parsing/validation, static-data handling, mailbox discovery, event unmasking, and partition transition to running mode.

## Important APIs, types, and functions
- `wlcore_boot_upload_firmware()` parses a big-endian chunked firmware image and writes chunks to target memory.
- `wl1271_boot_upload_firmware_chunk()` sets download partitions and streams fixed-size chunks with partition-window updates.
- `wlcore_boot_upload_nvs()` validates legacy or wl128x NVS layout, patches the active MAC address into NVS bytes, bursts register writes, aligns and uploads NVS tables.
- `wlcore_boot_run_firmware()` halts/runs firmware, verifies chip id, polls init-complete interrupt, reads command/event mailbox pointers, reads static data, unmasks events, and switches to work partition.
- `wlcore_boot_parse_fw_ver()` and `wlcore_validate_fw_ver()` parse firmware version strings and enforce chip-family minimums.
- `wlcore_boot_static_data()` reads static data and delegates lower-driver private handling.

## Control flow
Firmware upload reads the first word as chunk count, then loops over address/length/data records, rejecting oversized chunks and requiring 4-byte-aligned lengths. NVS upload chooses legacy or non-legacy layout based on quirks and size, updates the primary MAC address, interprets burst-write records until a zero-length marker, aligns to the NVS table area, switches to work partition, and writes the table to the command mailbox data address. Run-firmware selects boot partition, verifies the chip id after starting firmware, polls `REG_INTERRUPT_NO_CLEAR` for `WL1271_ACX_INTR_INIT_COMPLETE`, acknowledges it, reads mailbox pointers, validates firmware static data, calls lower-driver static-data handler, unmasks events, and sets the work partition.

## State and persistence behavior
Mutates runtime device state: `wl->enable_11a` from NVS, patched in-memory `wl->nvs`, `wl->cmd_box_addr`, `wl->mbox_ptr[]`, `wl->chip.fw_ver_str`, `wl->chip.fw_ver[]`, and lower-driver static-data state. It may free and NULL malformed NVS buffers. Hardware memory/register state is heavily changed; no filesystem persistence.

## Dependencies and integration points
Depends on wlcore I/O, partitioning, event unmasking, RX/event headers, lower-driver callbacks `wlcore_identify_fw()` and `wlcore_handle_static_data()`, platform family NVS names, and firmware/NVS formats. Exported functions are used by chip-family boot implementations such as wl18xx.

## Risks and test signals
Risks include malformed firmware/NVS bounds, incorrect partition-window updates, MAC byte-order patching errors, legacy NVS compatibility, timeout polling init-complete, firmware version parsing assumptions, and mailbox pointer errors. Test with valid/invalid firmware chunks, valid/invalid legacy and wl128x NVS sizes, 5 GHz enablement from NVS, chip-id mismatch, firmware version below minimum, init timeout, mailbox read failures, and recovery boot loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.h

## Purpose
Declares common wlcore boot entry points and firmware static-data constants/layout.

## Important APIs, types, and functions
- `wlcore_boot_upload_firmware()`, `wlcore_boot_upload_nvs()`, and `wlcore_boot_run_firmware()` are exported boot-stage helpers used by lower drivers.
- `struct wl1271_static_data` mirrors firmware static data: MAC address, firmware version string, hardware version, TX power table, and lower-driver private tail.
- Constants define power-table dimensions, firmware-version string length, init polling loop/delay, and ELP/wake command values.

## Control flow
No executable flow. Lower-driver boot implementations call the three boot helpers in chip-specific order.

## State and persistence behavior
No local state. The static-data structure describes volatile firmware-provided data read during boot.

## Dependencies and integration points
Includes wlcore core definitions. Implemented by `boot.c` and called from chip-family `main.c` files such as wl18xx.

## Risks and test signals
ABI mismatch in `wl1271_static_data` breaks firmware-version validation and lower-driver private static data parsing. Boot tests should verify firmware upload, NVS upload, firmware run, static-data parsing, and init-complete timing on supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.h -->
