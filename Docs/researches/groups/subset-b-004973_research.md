# subset-b-004973 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.c

## Purpose
`tx.c` implements the common wlcore transmit pipeline shared by TI WiLink wl12xx/wl18xx-family drivers. It bridges mac80211 skb submission to firmware transfer buffers, assigns firmware TX descriptor IDs, fills the packed `wl1271_tx_hw_descr` ABI, schedules packets across vifs/links/access categories, handles TX completion status from firmware, and provides reset/flush/queue-stop helpers used by suspend, recovery, interface teardown, and chipset-specific interrupt paths.

## Important APIs, Types, And Functions
- `wlcore_tx_work_locked()` drains driver TX queues into `wl->aggr_buf`, writes the aggregate to `REG_SLV_MEM_DATA`, optionally triggers older hardware end-of-transaction signaling, wakes watermark-stopped queues, and rearms RX streaming for active data links.
- `wl1271_tx_work()` is the workqueue wrapper that takes `wl->mutex`, resumes runtime PM, invokes the locked worker, and queues recovery on bus failure.
- `wlcore_tx_complete()` reads the firmware TX-result ring from `target_mem_map->tx_result`, acknowledges `tx_result_fw_counter`, and hands each result to `wl1271_tx_complete_packet()`.
- `wl1271_tx_complete_packet()` validates the descriptor ID, restores skb layout, updates mac80211 TX status, queues the skb on `deferred_tx_queue`, schedules `netstack_work`, and frees the descriptor ID.
- `wl1271_tx_flush()`, `wl12xx_tx_reset()`, `wl12xx_tx_reset_wlvif()`, and `wl1271_tx_reset_link_queues()` are cleanup paths that stop queues, force TX work, report failed skbs, and restore counters after timeout or recovery.
- `wlcore_stop_queue*()`, `wlcore_wake_queue*()`, and `wlcore_is_queue_stopped*()` maintain per-mac80211-queue stop reason bitmaps for watermark, firmware restart, flush, and spare-block throttling.
- Internal helpers include `wl1271_alloc_tx_id()`, `wl1271_free_tx_id()`, `wl12xx_tx_get_hlid()`, `wl1271_tx_allocate()`, `wl1271_tx_fill_hdr()`, `wl1271_prepare_tx_frame()`, `wl1271_skb_dequeue()`, and `wl1271_skb_queue_head()`.

## Control Flow
mac80211 enqueue happens in `main.c`: skb queue mapping is translated by `wl1271_tx_get_queue()`, `wl12xx_tx_get_hlid()` chooses a host link ID, the skb is appended to `wl->links[hlid].tx_queue[q]`, queue counters are incremented, high watermark may stop the mac80211 queue, and `tx_work` is queued unless firmware TX is busy. `wl1271_skb_dequeue()` chooses an AC with pending packets and the fewest firmware-allocated packets, then does round-robin selection across vifs and links while asking chip ops whether a link is high or low priority.

For each skb, `wl1271_prepare_tx_frame()` validates the HLID, determines TKIP/GEM extra space and WEP default-key updates, calls `wl1271_tx_allocate()` to reserve a descriptor ID and firmware memory blocks, and calls `wl1271_tx_fill_hdr()` to populate session, lifetime, rate policy, encryption, EAPOL, checksum, and data-length fields. The prepared skb bytes are copied into the aggregate buffer with alignment selected by `wlcore_calc_packet_alignment()`.

If the aggregate buffer fills, the skb is pushed back to the head, the partial aggregate is written to firmware, and the loop continues. If firmware blocks are exhausted, the skb is pushed back, `WL1271_FLAG_FW_TX_BUSY` is set, and the worker exits until completions/free-block accounting lets TX proceed. Bus write failures are the only errors propagated to the workqueue wrapper for recovery.

Completion flow is ring-counter based: firmware advances `tx_result_fw_counter`; the host acknowledges by writing the same counter back; each ring entry supplies descriptor ID, status, retry count, rate class, and timing data. Successful completions map firmware rate class to mac80211 rate index and set ACK status unless no-ACK was requested. Retry-exceeded completions update retry statistics. Dummy packets free their ID but are not reported to mac80211.

## State And Persistence Behavior
This file does not persist state outside kernel memory. Runtime state is kept in `struct wl1271`: `tx_frames_map`, `tx_frames[]`, `tx_frames_cnt`, `tx_queue_count[]`, `queue_stop_reasons[]`, `tx_blocks_available`, `tx_allocated_blocks`, `tx_allocated_pkts[]`, `tx_packets_count`, `tx_results_count`, `last_wlvif`, `dummy_packet`, `deferred_tx_queue`, and per-link `allocated_pkts`. Per-vif state in `struct wl12xx_vif` includes per-AC counters, `last_tx_hlid`, pending authentication ROC timing, default WEP key, rate policy indexes, and link maps.

Locking is split by responsibility: `wl->mutex` protects high-level device state and runtime PM transitions; `wl->wl_lock` protects queue counters and stop-reason bitmaps; `flush_mutex` serializes `wl1271_tx_flush()`. The code assumes callers hold `wl->mutex` for locked TX/reset paths and uses `assert_spin_locked()` in queue-state queries that require `wl_lock`.

## Dependencies And Integration Points
The file depends on mac80211/cfg80211 skb metadata, Linux skb queues, runtime PM, workqueues, timers, and bitmaps. It calls wlcore hardware abstraction helpers from `hw_ops.h` for block accounting, descriptor data length, checksum setup, pre-send padding, link priority, and spare blocks. It uses wlcore bus helpers (`wlcore_write_data`, `wlcore_write32`, `wlcore_read`), command helpers (`wl12xx_cmd_set_default_wep_key`, `wl1271_acx_set_inconnection_sta`), power-save helpers (`wl12xx_ps_link_start`), recovery helpers (`wl12xx_queue_recovery_work`), and main.c watchdog/RX-streaming work.

Chip integration differs by family. wl12xx uses `wlcore_tx_complete()` through its delayed completion hook, while wl18xx has a separate completion path but still uses common queueing/allocation helpers and common state fields. Firmware ABI integration is through `struct wl1271_tx_hw_descr` and `struct wl1271_tx_hw_res_if` from `tx.h`.

## Risks And Edge Cases
- Descriptor ID accounting is safety-critical. Lost completions or double frees can leave `WL1271_FLAG_FW_TX_BUSY` stuck or leak skbs in `tx_frames[]`.
- Queue counters are updated in enqueue, dequeue, push-back, reset, and dummy-packet paths. Any mismatch can break watermark throttling or trigger warnings.
- `wl1271_tx_complete()` warns on result-ring overflow but still processes `count` entries using a 16-entry masked offset, so large counter jumps risk duplicate/stale result processing after firmware or bus anomalies.
- skb layout mutation for TX descriptors and TKIP extra header space must be exactly reversed before mac80211 status; mistakes corrupt frame headers on completion or reset.
- `wl1271_prepare_tx_frame()` suppresses most non-bus errors from the workqueue caller by design; command failures may rely on lower-level recovery scheduling.
- Flush stops all queues and waits up to `WL1271_TX_FLUSH_TIMEOUT`; timeout falls back to link queue reset, but in-flight firmware frames are handled separately by full TX reset/recovery.
- AP pending-auth handling starts a remain-on-channel style timer when auth responses are transmitted; incorrect detection could keep ROC too short or too long.

## Test Signals
Useful signals include mac80211 TX status correctness, no queue-counter warnings under traffic, high/low watermark stop/wake transitions, descriptor count returning to zero after traffic and flush, recovery behavior when bus writes fail, TX watchdog recovery when firmware completions stop, AP-mode sleeping-station traffic, EAPOL/WEP/TKIP/GEM frames, dummy packet reuse, and suspend/remove paths that call `wl1271_tx_flush()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.h

## Purpose
`tx.h` defines the wlcore transmit firmware ABI, TX result ABI, queue-stop reason enum, queue mapping helpers, and exported prototypes used by common wlcore code and chip-family drivers. It is the contract between the common TX implementation, firmware descriptors, and mac80211 queue management.

## Important APIs, Types, And Constants
- `TX_HW_ATTR_*` and `TX_HW_ATTR_OFST_*` define descriptor bitfields for retries, header padding, session counter, rate policy, last-word padding, completion request, dummy packet, host encryption, and EAPOL marking.
- `struct wl1271_tx_hw_descr` is the packed descriptor prepended to every firmware TX packet. It carries length, chip-family memory accounting union, host/device timing, lifetime, attributes, descriptor ID, TID, HLID, and wl18xx checksum metadata.
- `struct wl1271_tx_hw_res_descr` and `struct wl1271_tx_hw_res_if` define the 16-entry TX result ring read by `wlcore_tx_complete()`.
- `enum wl1271_tx_hw_res_status` enumerates firmware completion results such as success, retry exceeded, timeout, missing key, invalid peer, session mismatch, and invalid link.
- `enum wlcore_queue_stop_reason` provides independent queue-stop bits for watermark pressure, firmware restart, flush, and wl18xx spare-block limits.
- Inline helpers `wl1271_tx_get_queue()`, `wlcore_tx_get_mac80211_queue()`, and `wl1271_tx_total_queue_count()` translate mac80211 queue indexes to wlcore ACs and summarize pending work.

## Control Flow And Integration
The header is included by `tx.c`, `main.c`, and chip-family code. mac80211 queue mappings 0..3 are converted to wlcore AC constants in priority order VO, VI, BE, BK. Per-vif hardware queue bases are used to address mac80211 queues for stop/wake operations. The descriptor and result structs are filled/read only after chip ops have calculated block counts and chip-specific memory fields.

## State And Persistence Behavior
The header itself holds no storage, but its structs define persistent in-memory state exchanged with firmware in DMA/bus-visible buffers. Because descriptors are packed and use little-endian fields, layout drift would be an ABI break. Queue-stop reasons are stored in `wl->queue_stop_reasons[]`, one bitmap per mac80211 hardware queue.

## Dependencies
The file depends on wlcore configuration constants such as `CONF_TX_AC_*`, `NUM_TX_QUEUES`, `WLCORE_NUM_MAC_ADDRESSES`, and `struct wl1271`/`struct wl12xx_vif` declarations from wlcore headers. It also relies on Linux bit macros and endian types.

## Risks And Test Signals
Primary risks are packed-struct layout mismatch with firmware, incorrect AC mapping, off-by-one handling of the 16-entry result ring mask, and stop-reason bits being added without updating queue-state logic. Tests should validate TX descriptor sizes, successful TX completion parsing, mac80211 queue stop/wake behavior per vif, and all chip-family implementations of memory-block descriptor fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.c

## Purpose
`vendor_cmd.c` registers TI vendor commands and events on the wlcore wiphy. The commands expose smart-config firmware features through cfg80211/nl80211 vendor command hooks: start smart config, stop smart config, and set a smart-config group key.

## Important APIs And Functions
- `wlcore_vendor_attr_policy[]` accepts `WLCORE_VENDOR_ATTR_FREQ`, `WLCORE_VENDOR_ATTR_GROUP_ID`, and binary `WLCORE_VENDOR_ATTR_GROUP_KEY` up to `WLAN_MAX_KEY_LEN`.
- `wlcore_vendor_cmd_smart_config_start()` parses a required group ID and calls `wlcore_smart_config_start()`.
- `wlcore_vendor_cmd_smart_config_stop()` calls `wlcore_smart_config_stop()` without attributes.
- `wlcore_vendor_cmd_smart_config_set_group_key()` parses required group ID and group key, then calls `wlcore_smart_config_set_group_key()`.
- `wlcore_set_vendor_commands()` assigns command and event arrays to `wiphy->vendor_commands`, `wiphy->n_vendor_commands`, `wiphy->vendor_events`, and `wiphy->n_vendor_events`.

## Control Flow
Each command handler converts `wiphy` to `ieee80211_hw`, then to `struct wl1271`. Attribute-bearing commands reject missing data, parse netlink attributes with the local policy, and require the needed attributes. All handlers lock `wl->mutex`, reject devices not in `WLCORE_STATE_ON`, resume runtime PM with `pm_runtime_resume_and_get()`, invoke the chip op wrapper, autosuspend the device, unlock, and return the chip-op status.

## State And Persistence Behavior
The file does not own long-lived state. It mutates only cfg80211 registration fields on the `wiphy`. Command effects are delegated to chip ops and firmware. The only runtime state checks are `wl->state` and runtime PM references.

## Dependencies And Integration Points
This file depends on cfg80211 vendor command infrastructure, netlink attribute parsing, mac80211 `wiphy_to_ieee80211_hw()`, runtime PM, and wlcore chip-op wrappers from `hw_ops.h`. Registration is called from wlcore setup in `main.c`. Smart-config implementation is optional per chip; wl18xx supplies these ops, while wrappers can report unsupported behavior if ops are absent.

## Risks And Test Signals
Risks include ABI compatibility with userspace vendor commands, accepting unused attributes from `vendor_cmd.h` without policy coverage, missing runtime-PM put paths, and chip ops being unavailable. Test by issuing valid and invalid nl80211 vendor commands, verifying `-EINVAL` for missing data/group/key or off-state devices, checking runtime PM balance, and observing smart-config vendor events (`SC_SYNC`, `SC_DECODE`) from firmware-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.h

## Purpose
`vendor_cmd.h` defines the public constants and declaration for wlcore TI vendor-command registration. It names the TI OUI, smart-config command IDs, smart-config attribute IDs, and smart-config event IDs used by cfg80211 userspace APIs.

## Important APIs And Types
- `TI_OUI` is `0x080028`, the vendor identifier stored in nl80211 vendor command/event metadata.
- `wlcore_set_vendor_commands(struct wiphy *wiphy)` is declared for kernel builds and implemented in `vendor_cmd.c`.
- `enum wlcore_vendor_commands` defines `SMART_CONFIG_START`, `SMART_CONFIG_STOP`, and `SMART_CONFIG_SET_GROUP_KEY`.
- `enum wlcore_vendor_attributes` defines attributes for frequency, PSK, SSID, group ID, and group key. The current C implementation uses group ID and group key, with a policy entry for frequency.
- `enum wlcore_vendor_events` defines smart-config sync and decode events.

## Control Flow And Integration
The header is included by `vendor_cmd.c` and by wlcore registration code. Userspace identifies commands by the TI OUI plus subcommand number; cfg80211 dispatches to handlers installed by `wlcore_set_vendor_commands()`.

## State And Persistence Behavior
There is no mutable state. The enum numeric order is ABI-significant for userspace and should be treated as stable.

## Dependencies
The function declaration uses `struct wiphy` from cfg80211 when `__KERNEL__` is defined. Attribute lengths and parsing policy live in `vendor_cmd.c`.

## Risks And Test Signals
Changing enum order or OUI breaks userspace ABI. Adding attributes requires matching netlink policy updates in `vendor_cmd.c`. Tests should confirm command IDs and event IDs match userspace tooling and that unsupported/unused attributes are either ignored intentionally or documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wl12xx_80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wl12xx_80211.h

## Purpose
`wl12xx_80211.h` provides local 802.11 rate constants and packed template/IE structs used by wlcore/wl12xx firmware template commands. It defines legacy CCK/OFDM rate values and masks, generic 802.11 headers, common information elements, and firmware templates for null data, PS-poll, ARP response, and disconnect frames.

## Important APIs And Types
- Rate constants such as `IEEE80211_CCK_RATE_1MB`, `IEEE80211_OFDM_RATE_54MB`, and `IEEE80211_BASIC_RATE_MASK` encode firmware/802.11 rate values.
- Rate masks group CCK, OFDM, basic, default, and combined defaults for rate-policy setup.
- `MAX_SUPPORTED_RATES` and `MAX_COUNTRY_TRIPLETS` size local arrays used in IE structs.
- Packed structs include `ieee80211_header`, `wl12xx_ie_header`, `wl12xx_ie_ssid`, `wl12xx_ie_rates`, `wl12xx_ie_ds_params`, `country_triplet`, `wl12xx_ie_country`, `wl12xx_null_data_template`, `wl12xx_ps_poll_template`, `wl12xx_arp_rsp_template`, and `wl12xx_disconn_template`.

## Control Flow And Integration
This header has no functions. Template-building code includes it to lay out management/control frames and IEs exactly as firmware expects. The ARP response template combines RFC1042 LLC data, ARP header fields, and sender/target addresses so firmware can autonomously respond while the host is asleep.

## State And Persistence Behavior
There is no owned runtime state. The packed structs are transient command/template payload layouts, but their binary shape is part of the driver-firmware contract.

## Dependencies
The file uses kernel Ethernet and ARP definitions from `linux/if_ether.h` and `linux/if_arp.h`, mac80211 constants such as `IEEE80211_MAX_SSID_LEN` and `IEEE80211_COUNTRY_STRING_LEN`, and `rfc1042_header`.

## Risks And Test Signals
Risks include divergence from standard mac80211 definitions, incorrect packed layout, overly large IE arrays relative to firmware limits, and rate mask misuse across bands. Tests should validate template byte layout, ARP offload behavior, disconnect/nullfunc/PS-poll template operation, and rate policy generation using these masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wl12xx_80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore.h

## Purpose
`wlcore.h` is the main common wlcore device header. It defines the chip operation vtable, partition/register enums, top-level `struct wl1271` runtime state, firmware/version helpers, quirk bits, hardware register constants, and public probe/remove/key/configuration APIs shared by TI WiLink wl12xx and wl18xx drivers.

## Important APIs, Types, And Fields
- `struct wlcore_ops` is the chip-family abstraction. It covers setup, chip/FW identification, boot, command/event transport, TX block calculation and descriptor filling, RX layout, completions, hardware init, scan/sched-scan, key installation, channel switch, pre-send aggregation padding, link priority, interrupts, RX BA filtering, smart config, CAC/DFS, and debugfs/static-data hooks.
- `struct wl1271` is the central device object stored as `ieee80211_hw->priv`. It holds hardware handles, runtime state, mutexes/spinlocks, firmware/NVS blobs, partition tables, roles/links/rate-policy maps, vif list, TX/RX queues, descriptor tracking, aggregate buffers, mailbox/status buffers, scan/ROC/sched-scan state, supported bands, AP power-save maps, quirks, watchdog work, chip ops, firmware names, capabilities, DFS state, RX filters, flush mutex, firmware-version minima, interface combinations, trace flags, and time-sync data.
- `struct wlcore_partition*` and `enum wlcore_registers` describe translated firmware/register windows used by bus helpers.
- Inline helpers `wlcore_set_ht_cap()` and `wlcore_set_min_fw_ver()` initialize capability/version arrays.
- Quirk bits alter bus transaction, TX/RX block alignment, firmware log availability, NVS layout, TX padding, TKIP header space, scheduled-scan behavior, probe templates, regulatory configuration, and AP session ID semantics.

## Control Flow And Integration
Lower drivers allocate and initialize `struct wl1271`, populate `wlcore_ops`, partition/register tables, firmware names, limits, rate tables, and quirks, then call `wlcore_probe()`. Common wlcore code calls ops through wrappers in `hw_ops.h`, allowing `tx.c`, `cmd.c`, `scan.c`, `event.c`, and `main.c` to share control flow while delegating chip-specific details.

TX integration is prominent: `tx.c` updates `tx_blocks_available`, `tx_allocated_blocks`, `tx_allocated_pkts[]`, `tx_frames_map`, `tx_frames[]`, `tx_queue_count[]`, `queue_stop_reasons[]`, `dummy_packet`, `aggr_buf`, `tx_res_if`, `fw_status`, and `links[]`. Runtime PM, watchdog, recovery, scan, and ROC paths are also coordinated through fields in this struct.

## State And Persistence Behavior
All state is in-memory kernel driver state. Some subregions are logically persistent across firmware reconfiguration, such as MAC addresses, firmware version requirements, vif private persistent tails, total freed packet counters used for PN tracking, and NVS/firmware blobs while the device is bound. No filesystem persistence is performed by this header.

## Dependencies
The header includes platform-device support plus wlcore internal headers `wlcore_i.h`, `event.h`, and `boot.h`. It depends heavily on mac80211/cfg80211 types, kernel workqueues, completions, mutexes, bitmaps, sk_buffs, debugfs, and endian-aware firmware structures.

## Risks And Test Signals
The main risk is shared-state coupling: many subsystems mutate `struct wl1271`, so invariants around locks, firmware state, TX/RX counters, role/link maps, and runtime PM must remain consistent. Chip ops must be fully populated for the selected family or wrappers must safely reject unsupported operations. Tests should cover probe/remove, firmware boot/version gating, suspend/resume, scan/ROC, TX/RX under load, AP/STA concurrency, recovery, debugfs state dumps, DFS/CAC where supported, and smart-config ops on wl18xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore_i.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore_i.h

## Purpose
`wlcore_i.h` contains internal wlcore definitions used across common driver modules: firmware state enums, platform data, link/vif/station private structures, power-save and queue constants, RX filter structures, iterator macros, and declarations for internal helpers. It is the shared private model behind `wlcore.h` and the TX path.

## Important APIs, Types, And Fields
- `enum wlcore_state`, `enum wl12xx_fw_type`, `struct wl1271_chip`, and `struct wl_fw_status` describe driver/FW status and counters read from firmware.
- `struct wl1271_if_operations` abstracts the bus child operations: read, write, reset, init, power, and block-size setup.
- `struct wlcore_platdev_data` carries bus ops, family data, clock configuration, and suspend-power policy from platform glue.
- `enum wl12xx_flags` and `enum wl12xx_vif_flags` define global and per-vif flag bits for power, TX pending/busy, IRQ, suspend, recovery, vif changes, association/AP state, RX streaming, channel switch, beacon state, and more.
- `struct wl1271_link` owns per-HLID TX queues for each AC, allocated/freed packet accounting, PN tracking, address, BA bitmap, last firmware rate, owning vif, and total freed packets.
- `struct wl1271_station` is mac80211 station private data with HLID, firmware-added state, in-connection state, and freed-packet PN tracking.
- `struct wl12xx_vif` is mac80211 vif private data. It stores role IDs, STA/AP-specific HLIDs and rate indexes, AP station maps and recorded keys, last TX HLID, per-AC TX queue counts, link map, SSID/channel/rate state, templates, default key, power/RSSI, encryption/IP data, BA/WMM/radar flags, RX streaming work/timer, channel switch/loss work, pending-auth ROC state, rate-control update state, total freed packet counter, and a persistent tail.

## Control Flow And Integration
`wl12xx_vif_to_data()` and `wl12xx_wlvif_to_vif()` convert between mac80211 objects and wlcore private structures. Iterator macros traverse all vifs or filter by STA/AP BSS type. TX enqueue/dequeue uses `wl1271_link.tx_queue[]`, `wl12xx_vif.tx_queue_count[]`, `wl12xx_vif.links_map`, `wl12xx_vif.last_tx_hlid`, and global flags such as `WL1271_FLAG_FW_TX_BUSY` and `WL1271_FLAG_DUMMY_PACKET_PENDING`. Firmware status conversion populates `struct wl_fw_status`, which then drives TX block release, link PS maps, rate feedback, RX counters, and event handling elsewhere.

## State And Persistence Behavior
This header defines state containers but does not allocate them. Per-station and per-vif counters such as `total_freed_pkts` are intentionally retained across recovery/reconfiguration to preserve encryption PN continuity. The `persistent[0]` tail marks the boundary for vif data that must survive reconfig flows.

## Dependencies
The file includes kernel synchronization/list/bit operations and mac80211, plus wlcore `conf.h` and `ini.h`. It relies on constants from cfg80211/mac80211 and kernel networking headers through included dependencies.

## Risks And Test Signals
Risks include incorrect assumptions about max roles/links/rate policies, stale flags after recovery, mismatch between `links_map` and actual link ownership, per-link queue leaks, PN tracking regressions across recovery, and persistent-tail misuse when adding fields. Tests should exercise STA/AP/P2P roles, multi-vif queueing, station add/remove, AP power-save transitions, recovery with encrypted traffic, RX filter allocation/free/flatten helpers, and platform bus operation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Kconfig

## Purpose
`virtual/Kconfig` declares build-time configuration symbols for virtual wireless drivers: `MAC80211_HWSIM` and `VIRT_WIFI`. These options make simulated or wrapper wireless devices available for testing and integration without real WLAN hardware.

## Important Options
- `MAC80211_HWSIM` is a tristate simulated radio testing tool for mac80211. It depends on `MAC80211`, builds the `mac80211_hwsim` module when selected as `M`, and is described as a developer testing tool rather than normal WLAN support.
- `VIRT_WIFI` is a tristate wrapper that makes ethernet connections appear as wifi connections through a special rtnetlink device. It depends on `CFG80211`.

## Control Flow And Integration
Kconfig controls whether the corresponding objects in `virtual/Makefile` are compiled. The dependency chain ensures hwsim only appears when mac80211 is enabled and virt_wifi only appears when cfg80211 is enabled. Users and test kernels select these symbols through kernel configuration.

## State And Persistence Behavior
This file has no runtime state. Selection persists only in the generated kernel `.config` and build artifacts.

## Dependencies
The symbols depend on the kernel wireless stack (`MAC80211` or `CFG80211`) and integrate with the parent wireless driver Kconfig menu.

## Risks And Test Signals
Risks are mostly configuration-level: missing dependencies, unclear help text, or Makefile mismatch. Test by running Kconfig dependency checks, building each option built-in and as a module, and loading `mac80211_hwsim`/creating `virt_wifi` devices in wireless-stack tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Makefile

## Purpose
`virtual/Makefile` maps the virtual wireless Kconfig symbols to kernel build objects. It is the build glue for mac80211_hwsim and virt_wifi.

## Important Rules
- `obj-$(CONFIG_MAC80211_HWSIM) += mac80211_hwsim.o` builds the simulated mac80211 radio driver when enabled.
- `obj-$(CONFIG_VIRT_WIFI) += virt_wifi.o` builds the ethernet-to-wifi wrapper driver when enabled.

## Control Flow And Integration
The kernel build system expands each `obj-$()` rule based on the final configuration value. Built-in selections are linked into the kernel image; module selections produce `.ko` modules. The rules must match the symbols defined in `virtual/Kconfig` and the source filenames in the same directory.

## State And Persistence Behavior
There is no runtime state. Build outputs depend only on `.config` and source availability.

## Dependencies
Dependencies are declared in Kconfig rather than the Makefile. This file relies on normal kbuild semantics.

## Risks And Test Signals
Risks include symbol/file-name drift and missing object entries for new virtual drivers. Test with `CONFIG_MAC80211_HWSIM=y/m` and `CONFIG_VIRT_WIFI=y/m`, confirm object/module creation, and run clean builds to catch stale or renamed sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Makefile -->
