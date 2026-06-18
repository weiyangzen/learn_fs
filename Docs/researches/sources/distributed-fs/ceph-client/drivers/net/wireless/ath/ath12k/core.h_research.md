# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.h

## Purpose
Defines the central ath12k object model and public core interface. Nearly every subsystem consumes this header for per-device, per-radio, per-vif, per-station, firmware stats, MLO, regulatory, recovery, debug, and datapath state.

## Important APIs, Types, And Functions
Important enums cover BDF search mode, WME AC, crypto mode, skb flags, hardware revisions, firmware modes, SMBIOS country-code mode, scan and 11d states, group and device flags, RX error buckets, stats categories, hardware state, and device family. Major structures include `ath12k_skb_cb`, `ath12k_skb_rxcb`, `ath12k_link_vif`, `ath12k_vif`, `ath12k_link_sta`, `ath12k_sta`, `ath12k`, `ath12k_hw`, `ath12k_pdev_cap`, `ath12k_pdev`, `ath12k_hw_group`, `ath12k_base`, and firmware stats records. Inline helpers convert between mac80211 private objects and ath12k objects, map bus names, build firmware paths, access DP/core pointers, and stringify scan state.

## Control Flow
The header does not implement full flows, but it defines the state machines used by `core.c`, `mac.c`, DP, WMI, and debugfs: scan transitions, hardware restart states, device flags for crash/recovery/registration, MLO group membership, and completion objects for WMI commands.

## State And Persistence
Persistent driver state is rooted at `ath12k_base`; per-radio runtime state is in `ath12k`; registered mac80211 aggregate state is in `ath12k_hw`; multi-device grouping is in `ath12k_hw_group`. It also stores long-lived firmware handles, regulatory domains, pdev capability tables, ACPI data, coredump buffers, workqueues, completions, IDRs, RCU pdev pointers, and rhashtables.

## Dependencies And Integration Points
Includes Linux IRQ, DMI, firmware, OF, panic notifier, average, rhashtable, and many ath12k subsystem headers. It is the integration boundary between bus drivers, mac80211, WMI/QMI/HTC/HAL/DP, debugfs, coredump, thermal, regulatory, and WOW.

## Risks
Because this is the shared state contract, field lifetime and locking comments are critical. Several members are protected by `data_lock`, `base_lock`, `core_lock`, `hw_mutex`, group mutex, RCU, or wiphy mutex; incorrect access can race with recovery or interface teardown. Flexible-array and private-data casts must remain compatible with mac80211 storage sizes.

## Test Signals
Builds with debugfs/coredump/ACPI combinations, sparse/lockdep, and all bus variants are important. Runtime signals include station/vif MLO creation, recovery state transitions, scan timeout/completion behavior, debug stats reads, and firmware path selection.
