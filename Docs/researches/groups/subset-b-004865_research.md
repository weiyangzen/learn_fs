# subset-b-004865 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.c

Purpose: implements the qtnfmac QLINK command plane. It translates cfg80211/mac80211-style requests into firmware commands, sends them synchronously over `qtnf_trans_send_cmd_with_resp`, validates replies, parses firmware TLVs, and updates host-side capability/cache structures such as `qtnf_hw_info`, `qtnf_mac_info`, supported bands, station stats, survey stats, and interface MAC addresses.

Important APIs/functions: `qtnf_cmd_send_init_fw` negotiates `QLINK_PROTO_VER`; `qtnf_cmd_get_hw_info`, `qtnf_cmd_get_mac_info`, and `qtnf_cmd_band_info_get` populate bus/MAC/wiphy capabilities; `qtnf_cmd_send_add_intf`, `qtnf_cmd_send_change_intf_type`, and `qtnf_cmd_send_del_intf` manage firmware VIFs; AP/STA workflows are exposed via `qtnf_cmd_send_start_ap`, `qtnf_cmd_send_stop_ap`, `qtnf_cmd_send_scan`, `qtnf_cmd_send_connect`, `qtnf_cmd_send_disconnect`, `qtnf_cmd_send_external_auth`, and `qtnf_cmd_send_update_owe`; security/control helpers include key operations, station changes, management frame registration/transmit, PM/WoWLAN, CAC/channel switch/channel get, regulatory notify, ACL, TX power, and bridge-domain updates. Core helpers include `qtnf_cmd_alloc_new_cmdskb`, `qtnf_cmd_send_with_reply`, `qtnf_cmd_check_reply_header`, and `qtnf_cmd_resp_result_decode`.

Control flow: each command allocates a zeroed SKB containing a `struct qlink_cmd` header plus fixed command payload, appends aligned TLVs where needed, acquires `qtnf_bus_lock`, sends through the transport, checks command id/MAC/VIF/length on the response, decodes firmware result codes to Linux errors, then releases any response SKB. Complex responses perform a second TLV pass: hardware info extracts build strings/capability bitmap; MAC info extracts regulatory rules, interface combinations, extended capabilities, and WoWLAN; band info rebuilds channels, HT/VHT/HE iftype data; station and channel stats use bitmap TLVs to decide which struct members are valid. Some commands also update host state, for example start AP turns carrier on after firmware success and add/change interface copies the returned MAC address into `vif->mac_addr`.

State and persistence: no on-disk persistence. Runtime state is split between firmware and host caches. This file writes `bus->hw_info`, `mac->macinfo`, `mac->rd`, `wiphy->bands[*]`, `band->channels`, `band->iftype_data`, `vif->mac_addr`, and carrier state. Allocated interface combinations, extended capabilities, regulatory domains, channels, iftype data, and WoWLAN support are later freed by core detach helpers. All synchronous firmware control transactions are serialized by the bus lock, while scan state itself lives in `mac->scan_req` and is completed by events/timeouts in other files.

Dependencies and integration points: depends heavily on `qlink.h` wire structures, `qlink_util.c` conversion helpers, `bus.h` locking/state, and `trans.h` command transport. It is called by cfg80211 operation implementations, core attach, netdev operations, and event follow-up paths. It integrates cfg80211 data types (`cfg80211_ap_settings`, `cfg80211_connect_params`, `station_info`, `survey_info`, `regulatory_request`, `cfg80211_wowlan`, `cfg80211_csa_settings`) with firmware TLVs and little-endian QLINK fields.

Risks: most safety depends on correct size accounting before `skb_put`; AP setup has an explicit fit check, but many other TLV-building paths rely on caller/kernel bounds and `QTNF_MAX_CMD_BUF_SIZE`. Firmware replies are trusted after header/length checks, so malformed TLV lengths, mismatched counts, or unexpected enum values are primary failure modes. Error unwinding must free partially allocated macinfo/band structures; repeated MAC-info refresh can leak or leave stale state if parsing fails after allocating `mac->rd`. Bus-lock misuse would deadlock command/response paths. Firmware-state checks reject commands when firmware is not up except `FW_INIT`, so attach/detach sequencing is critical.

Test signals: useful tests include QLINK reply header mismatch coverage, malformed TLV buffers for MAC/band/station/channel stats, AP start with maximum beacon/IE/ACL sizes, scan with disabled channels and random MAC, interface type changes that force band refresh, regulatory notifications with all channel bands, firmware result-code mapping, and fault-injection for allocation failures and command timeouts. Integration validation should watch wiphy registration capabilities, cfg80211 AP/STA connect flows, survey/station stats, DFS/CAC, WoWLAN pattern setup, and bridge-domain commands on hardware-bridge capable firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.h

Purpose: declares the qtnfmac firmware command interface used by core, cfg80211 operations, and netdev paths. It is the public boundary for the QLINK command plane implemented in `commands.c`.

Important APIs/types/functions: prototypes cover firmware init/deinit, hardware/MAC/band capability discovery, VIF add/change/delete/up/down, AP start/stop, management frame registration/transmit/app IE setup, station info and station changes, key management, scan/connect/disconnect/external auth, regulatory notifications, channel stats/channel switch/channel get/CAC, MAC ACL, power-management and TX-power control, WoWLAN configuration, bridge upper-device notification, and OWE updates.

Control flow: callers include cfg80211 hooks and core attach/detach. Most functions synchronously build and send one firmware command and return Linux errno-style status. Some functions return data through caller-provided output structures such as `station_info`, `survey_info`, `cfg80211_chan_def`, `int *dbm`, or cached fields inside `qtnf_wmac`/`qtnf_bus`.

State and persistence: the header owns no state, but its API exposes operations that mutate firmware state and host runtime caches. It includes `core.h` and `bus.h`, making `struct qtnf_vif`, `struct qtnf_wmac`, and `struct qtnf_bus` part of the interface contract.

Dependencies and integration points: depends on Linux `nl80211.h` and cfg80211 data types from included headers. It is consumed by `core.c`, `cfg80211.c`, event responses, and transport bringup paths that need to initialize or tear down firmware.

Risks: this broad synchronous API couples cfg80211 semantics tightly to firmware QLINK support. Prototype changes have wide blast radius. Callers must pass initialized VIF/MAC/bus pointers and must respect command context constraints because implementations allocate memory and take the bus lock.

Test signals: compile coverage is important because this header is the shared contract. Runtime signals are successful core attach capability discovery, VIF creation/deletion, AP/STA workflows, scan completion, key programming, regulatory handling, and no lockdep warnings around command calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.c

Purpose: implements the qtnfmac core driver lifecycle and netdev integration above the transport. It attaches firmware to cfg80211/wiphy/netdev objects, manages MAC/VIF runtime state, handles data TX entry points, scan completion, queue recovery, bridge notifications, debugfs root creation, and module init/exit.

Important APIs/functions: exported entry points are `qtnf_core_attach`, `qtnf_core_detach`, `qtnf_classify_skb`, `qtnf_wake_all_queues`, and `qtnf_get_debugfs_dir`. Netdev operations are `qtnf_netdev_open`, `qtnf_netdev_close`, `qtnf_netdev_hard_start_xmit`, `qtnf_netdev_tx_timeout`, `qtnf_netdev_set_mac_address`, and parent-id reporting. MAC helpers include `qtnf_core_mac_alloc`, `qtnf_core_mac_attach`, `qtnf_core_mac_detach`, `qtnf_mac_get_free_vif`, `qtnf_mac_get_base_vif`, `qtnf_mac_iface_comb_free`, `qtnf_mac_ext_caps_free`, and band initialization.

Control flow: `qtnf_core_attach` initializes transport state, starts data RX, allocates ordered/high-priority workqueues, sends firmware init, checks QLINK major version, retrieves hardware info, optionally enables metadata TX for hardware bridging, attaches each active MAC from the firmware bitmap, and registers a netdevice notifier. Per-MAC attach allocates a wiphy/private `qtnf_wmac`, initializes VIF slots and primary station VIF, asks firmware to add the primary interface, fetches MAC info and band info, registers the wiphy, creates the primary netdev, and programs bridge-domain metadata when needed. Detach reverses these steps: unregister notifier, stop RX, delete VIFs/netdevs, unregister wiphy, free per-band/macinfo/regdomain allocations, send firmware deinit if up, destroy workqueues, and free transport state.

State and persistence: state is volatile. Module parameters `slave_radar` and `dfs_offload` persist only as runtime module settings. The global `qtnf_debugfs_dir` tracks the module debugfs root. `qtnf_wmac` stores scan request, regulatory domain, platform device, wiphy registration state, and VIF array. `qtnf_vif` stores netdev pointer, MAC/BSSID, station list, high-priority TX queue/work, reset work, and TX-timeout count. Netdev carrier and queue state are controlled based on firmware events and transmit status.

Dependencies and integration points: integrates Linux netdev, cfg80211, debugfs, workqueues, rtnl, platform devices, switchdev/bridge notifications, transport functions, and command APIs. Data TX goes through `qtnf_bus_data_tx`; high-priority EAPOL frames are sent via `qtnf_cmd_send_frame` on a high-priority workqueue. RX classification consumes firmware-added `qtnf_frame_meta_info` tail metadata and returns the destination netdev for the PCIe NAPI path.

Risks: attach/detach ordering is delicate because firmware, transport RX, workqueues, wiphy, netdev, and notifier state overlap. `qtnf_classify_skb` assumes enough tailroom for metadata and valid magic; bad firmware packets are dropped but malformed skb lengths could still be risky upstream. TX timeout recovery schedules VIF reset after repeated timeouts and can disrupt live interfaces. MAC address change aborts scans and asks firmware to change interface type; partial failure must restore the old address. Bridge-domain handling differs depending on hardware bridge capability and switchdev availability. Workqueue teardown must happen after pending reset/high-priority/event work is quiesced.

Test signals: validate module load/unload, firmware attach failure unwinds at each stage, multi-MAC active/inactive bitmap behavior, primary netdev creation, netdev open/close/updown commands, TX fast path and EAPOL high-priority path, repeated TX timeout reset behavior, scan timeout and event completion, metadata RX classification/drop paths, bridge add/remove notifications, and debugfs root cleanup. Lockdep/KASAN/fault-injection tests are valuable for detach races and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.h

Purpose: defines the main qtnfmac runtime data model shared by command, event, cfg80211, transport, and bus-specific code. It also declares core lifecycle, netdev, scan, and utility APIs.

Important APIs/types/functions: constants include `QTNF_MAX_VSIE_LEN`, `QTNF_MAX_INTF`, `QTNF_MAX_EVENT_QUEUE_LEN`, `QTNF_SCAN_TIMEOUT_SEC`, default BSS/watchdog settings, and TX-timeout threshold. Key structs are `qtnf_sta_node`, `qtnf_sta_list`, `qtnf_vif`, `qtnf_mac_info`, `qtnf_wmac`, and `qtnf_hw_info`. Prototypes expose VIF lookup, capability cleanup, module parameter getters, wiphy allocation, net attach, main/event work, MAC lookup, skb classification, queue wake, VIF cleanup, netdev up/down, scan completion, debugfs root access, and qtn netdev identification.

Control flow: bus drivers allocate `qtnf_bus` and call core attach; core allocates `qtnf_wmac` via wiphy private data and fills the `iflist`. cfg80211 and netdev code use inline `qtnf_netdev_get_priv` to recover the `qtnf_vif` from `netdev_priv`. Hardware capability checks use `qtnf_hwcap_is_set` over the firmware capability bitmap.

State and persistence: all structs describe in-memory runtime state. `qtnf_vif` holds per-interface cfg80211 wireless_dev, BSSID/MAC, status/priority, management frame mask, netdev, station list, reset/high-priority work, high-priority SKB queue, timeout count, and generation. `qtnf_wmac` holds per-radio MAC id, bus pointer, capabilities, VIF array, active scan request, lock, scan timeout work, regulatory domain, and optional platform device. `qtnf_hw_info` caches protocol/firmware/hardware versions, MAC bitmap, chain counts, and hardware capabilities.

Dependencies and integration points: includes Linux kernel, netdevice/skbuff, cfg80211, firmware, workqueue, platform-device, `qlink.h`, `trans.h`, and `qlink_util.h`. The header is central to almost every qtnfmac file, so it defines the coupling between upper cfg80211 logic and lower transport implementations.

Risks: structure layout and lifetime are critical because bus code, workqueues, and cfg80211 callbacks hold pointers into these objects. `qtnf_netdev_get_priv` assumes netdev private storage contains a valid `struct qtnf_vif *`. Any change to constants such as `QTNF_MAX_INTF` affects firmware addressing and array bounds. Capability cleanup APIs must stay paired with allocation paths in `commands.c` and `core.c`.

Test signals: compile coverage across all qtnfmac objects, KASAN for VIF/MAC lifetime, lockdep around `mac_lock` and RTNL, attach/detach with multiple radios, scan timeout completion, netdev private pointer access, and capability bitmap checks for hardware bridge/DFS/WoWLAN paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.c

Purpose: provides the debugfs implementation for per-bus qtnfmac diagnostic directories and seq_file entries when `CONFIG_DEBUG_FS` is enabled.

Important APIs/functions: `qtnf_debugfs_init` creates a child directory under the module debugfs root returned by `qtnf_get_debugfs_dir`; `qtnf_debugfs_remove` recursively removes a bus debugfs directory and clears `bus->dbg_dir`; `qtnf_debugfs_add_entry` adds a device-managed seq_file entry using the caller-provided show function.

Control flow: PCIe firmware boot completion creates the bus directory, then common/chip-specific PCIe code registers stats files such as MPS/MSI/shared-memory stats and packet/IRQ stats. Remove paths call `qtnf_debugfs_remove` after core/transport teardown.

State and persistence: only `bus->dbg_dir` is stored; debugfs entries are runtime-only and disappear on module unload/device removal.

Dependencies and integration points: depends on `debug.h`, `core.h`, `bus.h`, and Linux debugfs/devm seq_file helpers. It is intentionally thin so chip-specific modules can provide their own seq callbacks without duplicating directory management.

Risks: debugfs creation failures are not surfaced to callers, which is normal for debugfs but means diagnostic files may silently be absent. Show functions must tolerate partially torn-down bus private state during removal. Recursive removal must be paired with setting `bus->dbg_dir = NULL` to avoid stale pointers.

Test signals: build with and without `CONFIG_DEBUG_FS`, verify expected PCIe debugfs files after firmware boot, read files during traffic, and remove/unload while files are open to catch lifetime issues in seq callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.h

Purpose: declares qtnfmac debugfs helpers and supplies no-op inline stubs when debugfs is disabled.

Important APIs/functions: with `CONFIG_DEBUG_FS`, it declares `qtnf_debugfs_init`, `qtnf_debugfs_remove`, and `qtnf_debugfs_add_entry`. Without debugfs, the same names compile to empty inline functions.

Control flow: bus/chip code can unconditionally call debugfs helpers. The preprocessor selects real or stub behavior, keeping the rest of the driver free of debugfs conditionals.

State and persistence: no state in the header. Real implementations mutate `bus->dbg_dir`; stub implementations do nothing.

Dependencies and integration points: includes Linux `debugfs.h`, `core.h`, and `bus.h`. It is used by PCIe common and chip-specific code for diagnostic seq_file registration.

Risks: the stubbed API can hide debugfs-only compile issues if callbacks are not otherwise built. The header includes broad qtnfmac core/bus headers, so include-cycle changes should be made cautiously.

Test signals: allmodconfig/allyesconfig coverage for real debugfs prototypes, tiny/no-debugfs builds for stubs, and module load checks confirming debugfs files are optional diagnostics rather than functional dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.c

Purpose: consumes asynchronous QLINK events from firmware and reports them into cfg80211/netdev state. It covers station association/deauth, station connect/disconnect, management RX, scan results/completion, channel changes, DFS/radar/CAC, external authentication, MIC failures, and OWE update requests.

Important APIs/functions: `qtnf_event_work_handler` drains `bus->trans.event_queue`; `qtnf_event_process_skb` validates event SKBs, finds the target MAC, and takes RTNL; `qtnf_event_parse` dispatches by `event_id`. Handlers include `qtnf_event_handle_sta_assoc`, `qtnf_event_handle_sta_deauth`, `qtnf_event_handle_bss_join`, `qtnf_event_handle_bss_leave`, `qtnf_event_handle_mgmt_received`, `qtnf_event_handle_scan_results`, `qtnf_event_handle_scan_complete`, `qtnf_event_handle_freq_change`, `qtnf_event_handle_radar`, `qtnf_event_handle_external_auth`, `qtnf_event_handle_mic_failure`, and `qtnf_event_handle_update_owe`.

Control flow: transport code enqueues received event SKBs and schedules `bus->event_work`. The work handler dequeues one SKB at a time, validates minimum event header length, looks up `qtnf_wmac` by firmware MAC id, and dispatches under RTNL. Handlers check payload sizes and current VIF mode, parse event-specific TLVs when present, then call cfg80211 notification APIs such as `cfg80211_new_sta`, `cfg80211_del_sta`, `cfg80211_connect_result`, `cfg80211_disconnected`, `cfg80211_rx_mgmt`, `cfg80211_inform_bss`, `cfg80211_scan_done` through `qtnf_scan_done`, `cfg80211_ch_switch_notify`, `cfg80211_radar_event`, `cfg80211_cac_event`, `cfg80211_external_auth_request`, `cfg80211_michael_mic_failure`, and `cfg80211_update_owe_info_event`.

State and persistence: no persistent storage. Runtime mutations include station-list add/remove, `vif->bssid`, netdev carrier on/off, cfg80211 BSS cache updates, scan request completion, and cfg80211 connection/CAC/external-auth state. Event handlers generally tolerate unregistered wiphy or missing netdev by returning without reporting.

Dependencies and integration points: depends on `qlink.h` event formats, `qlink_util` channel conversion, core MAC lookup and scan completion, `trans` event queue, station-list helpers from `util.h`, and Linux cfg80211 APIs. It is the asynchronous counterpart to the synchronous commands in `commands.c`.

Risks: firmware controls event payloads, so length checks and TLV parsing are critical. Some handlers use `event_len` from the QLINK header rather than SKB length after the initial minimum check; malformed lengths must be rejected by TLV parsing and handler size checks. Mode mismatches return protocol errors and may indicate firmware/host state divergence. Connect success may synthesize a missing BSS from the client SSID, which can fail if SSID is unknown. Event processing under RTNL serializes with netdev changes but can still race with teardown if queued SKBs outlive MAC/VIF state.

Test signals: inject malformed/short events, unknown event ids, invalid MAC/VIF ids, AP-only events in STA mode and vice versa, scan result TLVs with invalid lengths, scan completion including aborted flag, BSS join success/failure/missing-BSS cases, radar event variants with and without DFS offload, external auth/OWE workflows, MIC failure notification, and device removal with pending event queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.h

Purpose: declares the firmware event workqueue entry point for qtnfmac.

Important APIs/functions: exposes `qtnf_event_work_handler(struct work_struct *work)`, which is initialized by core attach as `bus->event_work`.

Control flow: lower transport receives QLINK event packets into `bus->trans.event_queue` and schedules the work item. The implementation in `event.c` drains and dispatches those packets to cfg80211.

State and persistence: no state in the header; state lives in the bus event queue and MAC/VIF structures.

Dependencies and integration points: includes Linux kernel/module headers and `qlink.h` for event protocol context. It is included by `core.c` and event-related transport code.

Risks: minimal header-level risk. The single exported work handler assumes `work` is embedded in a valid `struct qtnf_bus` and that the bus/event queue remain alive while work runs.

Test signals: compile coverage plus runtime checks that core attach initializes the work item, transport schedules it, and detach cancels or drains event processing safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie.c

Purpose: implements the common PCIe bus driver for qtnfmac. It probes PCIe devices, maps BARs, selects Pearl or Topaz chip support, configures DMA/interrupts/workqueues, initializes shared-memory IPC for the control path, starts asynchronous firmware bringup, exposes common debugfs stats, and handles remove/suspend/resume dispatch.

Important APIs/functions: module parameters control MSI, TX/RX descriptor sizes, flashboot, and firmware block size. `qtnf_pcie_probe` is the PCI probe path; `qtnf_pcie_remove` tears down. Shared helpers include `qtnf_pcie_control_tx`, `qtnf_pcie_alloc_skb_array`, `qtnf_pcie_fw_boot_done`, `qtnf_pcie_init_shm_ipc`, BAR mapping, IRQ setup, MPS tuning, and the control RX callback. PCI IDs bind Quantenna QSR devices, and chip id dispatch calls `qtnf_pcie_pearl_alloc` or `qtnf_pcie_topaz_alloc`.

Control flow: probe verifies PCIe, tunes MPS, enables the device, sets bus mastering, maps SYSCTL/DMA/shared-memory BARs, reads chip id, allocates the chip-specific `qtnf_bus` plus private state, initializes common private fields and locks, creates a PCIe workqueue, sets DMA mask, allocates a dummy mux netdev for NAPI, configures MSI or INTx, stores BAR pointers, saves PCI state, calls the chip-specific probe callback, then schedules firmware work. Firmware work eventually calls `qtnf_pcie_fw_boot_done`, which marks boot done, calls `qtnf_core_attach`, creates bus debugfs, and registers common stats files. Remove cancels firmware work, detaches core if attached, removes NAPI/tasklet/workqueue/netdev/shared IPC/debugfs, and calls chip remove.

State and persistence: common runtime state is held in `struct qtnf_pcie_bus_priv`: PCI device, callback table, locks, workqueue/tasklet, BAR mappings, shared-memory IPC endpoints, descriptor counts, TX/RX SKB arrays, ring indices, firmware block size, diagnostic counters, MSI flag, TX stop flag, and flashboot flag. Firmware/device state is not persisted; module parameters affect runtime behavior.

Dependencies and integration points: depends on Linux PCI, MSI/INTx, DMA mask APIs, netdev/NAPI, workqueues, shared-memory IPC, qtnf core attach/detach, debugfs helpers, and chip-specific Pearl/Topaz implementations. `control_tx` routes QLINK commands through `qtnf_shm_ipc_send`; control RX callback copies MMIO data into SKBs and calls `qtnf_trans_handle_rx_ctl_packet`.

Risks: probe error unwinding spans devm-managed resources, manual workqueue/netdev allocation, MSI/INTx state, and chip-specific allocations. `qtnf_pcie_control_tx` marks firmware dead only on IPC timeout; other transport failures propagate without state transition. Remove must not race with asynchronous firmware work or pending IRQ/tasklet/NAPI activity. BAR index assumptions and chip-id detection must match hardware. Debugfs show callbacks dereference bus private state and need removal ordering protection.

Test signals: PCI probe/remove on supported and unsupported chip ids, MSI enabled/disabled fallback, BAR mapping failures, DMA mask failure, firmware boot success/failure, control IPC timeout causing `QTNF_FW_STATE_DEAD`, module parameter variations for descriptor sizes and block size, suspend/resume callback dispatch, debugfs stats reads, and repeated load/unload under lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie_priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie_priv.h

Purpose: defines the shared private state and helper declarations used by common PCIe, Pearl, and Topaz qtnfmac bus code.

Important APIs/types/functions: constants define SKB buffer size and firmware/reset timeouts. `struct qtnf_pcie_bus_priv` embeds PCI device pointer, chip callback table, TX/reclaim locks, workqueue/tasklet, BAR pointers, shared-memory IPC endpoints, descriptor sizes/ring indices/SKB arrays, firmware block size, diagnostics counters, MSI/TX-stopped flags, and flashboot mode. It declares common helpers such as `qtnf_pcie_control_tx`, `qtnf_pcie_alloc_skb_array`, `qtnf_pcie_fw_boot_done`, `qtnf_pcie_init_shm_ipc`, chip allocation functions, and `qtnf_non_posted_write`.

Control flow: common probe fills the base private struct and calls a chip-specific `probe_cb`; chip code stores this struct as its first member so `get_bus_priv(bus)` can be cast to the full chip state. Bus operations call the common control path and chip-specific data paths.

State and persistence: all fields are runtime-only. Ring indices and SKB arrays represent in-flight DMA descriptors; diagnostic counters are exposed through debugfs; firmware block size and flashboot mirror module parameter decisions.

Dependencies and integration points: includes PCI, spinlock, I/O, SKB, workqueue, interrupt, shared-memory IPC, and `bus.h`. It is the ABI between `pcie.c`, `pearl_pcie.c`, and `topaz_pcie.c`.

Risks: because chip-private structs embed `qtnf_pcie_bus_priv` as the first field, layout assumptions matter. Ring index updates are shared between hard IRQ, tasklet, NAPI, and TX contexts and rely on the declared locks. `qtnf_non_posted_write` flushes posted MMIO writes by reading back the same register; using ordinary `writel` where a flush is required can break device handshakes.

Test signals: compile both chip variants, exercise TX/RX rings under traffic, IRQ/reclaim races, firmware boot timeouts, 32-bit and 64-bit DMA mask paths, and debugfs counter consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie.c

Purpose: implements the Pearl-family PCIe transport for qtnfmac. It defines Pearl boot data, descriptor formats, HDP/HHBM register handling, firmware upload/flashboot handshake, TX/RX DMA rings, IRQ/NAPI/tasklet handling, debugfs diagnostics, and Pearl bus operations.

Important APIs/functions: allocation entry is `qtnf_pcie_pearl_alloc`; chip probe/remove callbacks are `qtnf_pcie_pearl_probe` and `qtnf_pcie_pearl_remove`. TX/RX core functions include `qtnf_pcie_skb_send`, `qtnf_pcie_data_tx`, metadata TX variant `qtnf_pcie_data_tx_meta`, `qtnf_pearl_data_tx_reclaim`, `qtnf_pcie_pearl_rx_poll`, and `qtnf_pcie_pearl_interrupt`. Firmware functions include `qtnf_pearl_fw_work_handler`, `qtnf_ep_fw_load`, and `qtnf_ep_fw_send`. Helpers manage HDP IRQ masks, EP reset, IPC interrupt generation, BDA state polling, BD table allocation, RX SKB attachment, and HHBM init.

Control flow: probe assigns Pearl bus ops, initializes IRQ lock and firmware work, maps BDA/register base, writes MSI flag into BDA, initializes descriptor counts/HHBM/SKB arrays/BD table/RX buffers, disables HDP IRQs, requests IRQ, sets up reclaim tasklet and NAPI, and initializes shared-memory IPC regions from BDA. Firmware work either requests the Pearl firmware file or selects flashboot, sets RC state bits, waits for EP load-ready, uploads firmware in CRC-tagged SKB blocks with periodic sync/retry handling, waits for firmware done and QLINK done bits, then calls common `qtnf_pcie_fw_boot_done` and adds debugfs entries. Data TX maps SKBs into TX BDs, writes descriptor physical addresses to HDP host write registers, advances ring indices, and reclaims completed descriptors. RX NAPI polls BDs with `QTN_TXDONE_MASK`, unmaps DMA, classifies SKBs using qtnf frame metadata, feeds GRO, replaces consumed RX buffers, and re-enables RX interrupts when budget remains.

State and persistence: `struct qtnf_pcie_pearl_state` extends common PCIe state with IRQ lock, BDA pointer, PCIe register base, coherent TX/RX BD table, physical addresses, IRQ mask and counters. Runtime ring state is in `base.tx_bd_*`, `base.rx_bd_*`, `base.tx_skb`, and `base.rx_skb`. Firmware boot state lives in MMIO BDA flags and is not persisted by the host.

Dependencies and integration points: depends on Pearl register and IPC headers, shared PCIe private state, qtnf core, bus ops, shared-memory IPC, debugfs, firmware loader, DMA API, NAPI, tasklets, and circular buffer helpers. Hardware bridge support uses metadata TX so RX classification in `core.c` can demultiplex packets.

Risks: DMA mapping failure in RX attach stores the skb before returning and must be cleaned correctly later. TX queue fullness and reclaim happen in TX and tasklet contexts, so ring arithmetic and locking are critical. Firmware upload retry logic rewinds block pointers and can timeout after too many retries; off-by-one errors would corrupt firmware upload. RX replacement loop and wrap/ring indexes can leak buffers or starve RX if `CIRC_SPACE` accounting is wrong. Interrupt masking/unmasking uses hardware workarounds that clear all bits, so regressions can lose IRQs. Metadata TX appends tail data and trims only on busy return; other TX failures free/drop the skb.

Test signals: Pearl hardware boot from flash and host firmware file, firmware retry/sync timeout injection, MSI and legacy INTx interrupt paths, TX queue saturation and wake after reclaim, NAPI RX with invalid descriptor, missing skb, overlength packet, untagged metadata drop, hardware bridge metadata TX/RX, debugfs hdp/irq stats under traffic, remove/reset while traffic is active, and 32-bit versus 64-bit DMA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_ipc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_ipc.h

Purpose: defines Pearl PCIe boot-data-area flags, firmware upload constants, descriptor field helpers, and address macros shared by Pearl host and endpoint code.

Important APIs/types/functions: EP state bits include firmware/uboot presence, load-ready/sync/retry/QLINK-done/done and error flags. RC state bits advertise PCIe/net link, flashboot, QLINK, load-ready, and sync. Interrupt bit masks group HDP RX/TX events. `QTN_HOST_HI32`, `QTN_HOST_LO32`, and `QTN_HOST_ADDR` abstract 32-bit versus 64-bit DMA addresses. Constants define BDA version, BDA name length, HHBM max size, firmware upload board flag, block mask, buffer size, descriptor length/port/TQE fields, and firmware load types.

Control flow: `pearl_pcie.c` uses these definitions during BDA state polling, firmware upload packet construction, descriptor programming, interrupt setup, and DMA address reconstruction during cleanup/reclaim.

State and persistence: header constants describe volatile MMIO/BDA state shared with firmware. No host state is stored here.

Dependencies and integration points: includes Linux types and `shm_ipc_defs.h`. It is Pearl-specific and intentionally separate from Topaz, whose BDA state machine differs.

Risks: host and endpoint firmware must agree exactly on bit positions, BDA version, descriptor field layout, and DMA address width. Incorrect `QTN_HOST_ADDR` behavior on 32-bit/64-bit configurations would break DMA unmapping or descriptor programming. Firmware upload constants must match `qtnf_pearl_fw_hdr` packet construction.

Test signals: compile on 32-bit and 64-bit DMA address configurations, Pearl boot handshakes for flashboot and host-upload modes, firmware upload CRC/block sequencing, and descriptor length/port field decoding under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_regs.h

Purpose: maps Pearl PCIe HDP, HHBM, interrupt, legacy INTx, and system-control register offsets and bit fields for the Pearl transport implementation.

Important APIs/types/functions: macros compute MMIO addresses for HDP control, host write descriptors, RX/TX interrupt control/status/enables, RX descriptor pointers/counts, TX host queue controls, DMA counters, HHBM queue/pool registers, MSI/INTx status/mask registers, and SYSCTL LHOST interrupt offset. Bit definitions include HHBM reset/read/write/done/64-bit flags, HDP interrupt causes such as EP RXDMA/TXDMA/TXEMPTY/HHBM underflow/IPC, PCIe MSI/INTx status bits, legacy INTx assertion bit, Pearl IPC IRQ word construction, LHOST IPC IRQ, and EP reset IRQ.

Control flow: `pearl_pcie.c` uses these macros for descriptor table setup, HHBM initialization, IRQ enable/disable/clear, TX descriptor doorbells, RX polling counters, INTx deassertion, and endpoint reset/IPC interrupts.

State and persistence: no host state; the macros address volatile device registers.

Dependencies and integration points: consumed only by Pearl PCIe code. Register offsets must match the Pearl hardware programming model.

Risks: any incorrect offset or bit definition can cause lost interrupts, corrupted DMA queues, failed reset, or host/endpoint deadlock. Several macros alias offsets for different register meanings, so call-site context matters.

Test signals: Pearl hardware smoke boot, IRQ counter changes in debugfs, TX/RX traffic with descriptor counter movement, HHBM underflow/error handling, legacy INTx deassertion, and endpoint reset on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pearl_pcie_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie.c

Purpose: implements the Topaz PCIe transport for qtnfmac. It handles the Topaz BDA boot state machine, optional bootloader/firmware upload, endian/DMA-offset setup, descriptor rings, TX/RX IRQ/NAPI/tasklet paths, suspend/resume power signaling, debugfs diagnostics, and Topaz bus operations.

Important APIs/functions: allocation entry is `qtnf_pcie_topaz_alloc`; chip callbacks are `qtnf_pcie_topaz_probe`, `qtnf_pcie_topaz_remove`, and PM suspend/resume callbacks. Data path functions include `qtnf_pcie_data_tx`, `qtnf_topaz_rx_poll`, `qtnf_topaz_data_tx_reclaim`, `qtnf_pcie_topaz_interrupt`, `qtnf_try_stop_xmit`, `qtnf_try_wake_xmit`, and RX IRQ enable/disable helpers. Firmware/bringup helpers include `qtnf_topaz_fw_work_handler`, `qtnf_pre_init_ep`, `qtnf_post_init_ep`, `qtnf_pcie_endian_detect`, `qtnf_reset_dma_offset`, `qtnf_topaz_fw_upload`, and `qtnf_ep_fw_load`.

Control flow: probe requests IRQ but disables it, performs pre-init endianness/flags/target-ready handshake, initializes TX/RX descriptor counts in BDA, allocates coherent BD/extra-param memory, attaches RX SKBs, sets up tasklet/NAPI/shared-memory IPC, and returns for async firmware work. Firmware work marks target boot, optionally uploads bootloader, repeats pre-init if needed, then either waits for flashboot or uploads firmware blocks through a coherent DMA buffer, drives BDA boot states through start/config/run/running, post-initializes RX MSI address masking and waits for QLINK done, enables IRQ, calls common boot-done/core attach, and adds debugfs stats. TX writes DMA address and valid-packet length into the BDA request ring and interrupts the endpoint. RX NAPI consumes non-empty RX BDs, applies packet offset/length, classifies metadata, passes packets to the network stack, periodically interrupts endpoint with RX done, and replaces RX buffers.

State and persistence: `struct qtnf_pcie_topaz_state` extends common PCIe state with BDA pointer, dummy MSI DMA address, saved RX MSI write address, TX/RX BD pointers, shared extra-parameter pointers (`ep_next_rx_pkt`, `txqueue_wake`, `ep_pmstate`), and RX packet count. Runtime state is volatile across probe/remove and driven by MMIO BDA fields.

Dependencies and integration points: depends on Topaz register/IPС headers, shared PCIe private state, qtnf core, bus ops, shared-memory IPC, firmware loader, DMA API, PCI PM, NAPI/tasklets, and debugfs. Unlike Pearl, Topaz uses a 32-bit DMA mask and does not expose a metadata TX bus-op switch.

Risks: boot state is equality-based rather than bitmask-based, so wrong state ordering can stall bringup. IRQ is requested early and disabled until post-init; failures must not leave interrupts enabled unexpectedly. RX IRQ masking swaps the DMA writeback MSI address with a dummy coherent address, which is subtle and hardware-specific. TX stop/wake uses a shared `txqueue_wake` flag plus endpoint interrupts and can leave queues stopped if signaling is missed. The RX path calls `netif_receive_skb` rather than GRO, so behavior differs from Pearl. Freeing TX DMA uses `SKB_BUF_SIZE` in cleanup for Topaz TX instead of the original skb length, which is a review-sensitive detail. Suspend/resume writes PCI power state to shared memory and interrupts endpoint; this assumes firmware is alive.

Test signals: Topaz flashboot and host firmware upload, bootloader-needed path, endian detection timeout, DMA-offset error reset, firmware block upload timeout, MSI and INTx interrupt handling, IRQ enable after post-init, TX queue full/stop/wake, RX overlength/missing skb/metadata drop, RX done interrupt cadence, PM suspend/resume handshake, debugfs pkt/irq stats under load, and remove/reset during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_ipc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_ipc.h

Purpose: defines Topaz PCIe BDA boot states, flags, descriptor constants, DMA address helpers, endian markers, and utility macros used by the Topaz transport.

Important APIs/types/functions: boot states include PCIe init/ready, firmware load ready/done/start/run/config/running, host/target ready, flash boot, QLINK done, block transfer states, and failure states. Flags advertise RC mode, MSI, calibration command, flash presence/boot, bootloader transfer, QLINK driver, target/host errors, and BDA version/error masks. Address macros handle 32-bit/64-bit host values based on `BITS_PER_LONG`. Descriptor constants define TX queue length, valid-packet bit, packet length mask, BD empty/wrap/len/offset fields, RX done interrupt cadence mask, DMA offset error markers, endian detection values, and `NBLOCKS`.

Control flow: `topaz_pcie.c` uses this header to drive the firmware upload state machine, BDA flag negotiation, descriptor parsing/building, RX completion notifications, DMA offset correction, and endian detection handshake.

State and persistence: no C state is stored here; constants describe volatile shared BDA/register state.

Dependencies and integration points: includes Linux types and `shm_ipc_defs.h`. It is Topaz-specific and must remain synchronized with firmware/BDA layout in `qtnf_topaz_bda`.

Risks: state values are used by equality polling, so overlapping or incorrect values cause boot hangs. Descriptor length/offset macros directly control RX packet extraction. `BITS_PER_LONG` address helpers must agree with the DMA mask used by Topaz code. Endian detection markers are part of a fragile pre-boot handshake.

Test signals: 32-bit and 64-bit compile coverage, Topaz boot handshakes for all upload/flashboot branches, descriptor wrap/offset extraction under RX traffic, endian detection success/failure, and `NBLOCKS` block count behavior for firmware sizes around block boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_regs.h

Purpose: defines Topaz PCIe DMA interrupt, LHost IPC/M2L interrupt, and legacy INTx register offsets and bit numbers.

Important APIs/types/functions: macros compute MMIO addresses for DMA write/read interrupt status/mask/clear/error and MSI write-address registers, LHost IPC4 interrupt/mask, LHost M2L interrupt/mask, PCIe config offset for legacy INTx, and interrupt word construction. IRQ numbers identify TX done, endpoint reset, TX stop, RX done, power-management endpoint interrupt, and control IPC interrupt.

Control flow: `topaz_pcie.c` uses these definitions to mask/unmask RX MSI delivery, signal endpoint TX/RX/control/reset/PM events, detect/deassert legacy INTx, and reset the endpoint.

State and persistence: no host state; all definitions target volatile MMIO registers.

Dependencies and integration points: consumed by Topaz PCIe transport. It must match Topaz hardware register layout and the firmware interrupt protocol.

Risks: wrong offsets or IRQ bit numbers break firmware handshakes, TX/RX completion, reset, or PM signaling. RX interrupt masking depends on the DMA write-done MSI address registers, so these offsets are especially sensitive.

Test signals: Topaz MSI RX interrupt enable/disable behavior, INTx asserted/deasserted path, endpoint reset on remove, TX done/TX stop/RX done/control IPC interrupts observed by firmware, and PM suspend/resume IRQ signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/topaz_pcie_regs.h -->
