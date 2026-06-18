<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h

## Purpose
Central private header for the Intel iwlwifi MVM op-mode. It defines the main driver state objects, per-vif/per-link state, feature probes, command helper prototypes, mac80211 callbacks, firmware notification entry points, and cross-file contracts used by the rest of `drivers/net/wireless/intel/iwlwifi/mvm`.

## Important APIs, Types, And Functions
Core types are `struct iwl_mvm`, `struct iwl_mvm_vif`, `struct iwl_mvm_vif_link_info`, `struct iwl_mvm_phy_ctxt`, `struct iwl_mvm_time_event_data`, `struct iwl_mvm_tcm`, `struct iwl_mvm_baid_data`, `struct iwl_mvm_txq`, `struct iwl_mvm_dqa_txq_info`, `struct iwl_mvm_tvqm_txq_info`, `struct ptp_data`, and `struct iwl_mei_scan_filter`. Important enums cover power schemes, scan status/type, SMPS request sources, low-latency causes, thermal/TDLS state, queue status, and MVM status bits.

The header exports prototypes for lifecycle (`iwl_mvm_up`, `iwl_mvm_stop_device`, `iwl_run_init_mvm_ucode`, D3 load/resume), host commands (`iwl_mvm_send_cmd*`), NVM/regulatory (`iwl_nvm_init`, `iwl_mvm_update_mcc`, `iwl_mvm_init_mcc`), PHY contexts, MAC contexts, links, bindings, scanning, rate scaling, power, WoWLAN, BT coexistence, beacon filtering, SMPS, low latency, thermal, FTM, TDLS, PTP, SAR/PPAG/BIOS tables, RFI, channel switching, and mac80211 callbacks. Inline helpers gate firmware features and API variants such as MLD, new RX/TX station APIs, CDB, LAR, RLC offload, scan capabilities, quota format, ultra-high-band channel info, and MEI integration.

## Control Flow
This header does not implement a single runtime flow; it wires together flows implemented in sibling files. `ops.c` allocates `struct iwl_mvm`, initializes locks/work, sets transport callbacks, and dispatches firmware RX notifications to handlers declared here. mac80211 callbacks declared at the end of the file enter interface, station, scan, channel context, TX, key, FTM, and power flows. Firmware command builders in other files use the inline capability helpers to select command versions and data layout.

## State And Persistence
`struct iwl_mvm` is the top-level runtime state for the op-mode and stores transport/firmware/mac80211 handles, locks, notification wait state, NVM data and sections, firmware runtime, station/vif mappings, scan state, debugfs blobs, PHY contexts, time events, firmware key tables, WoWLAN/net-detect state, thermal/BT/TCM state, quota history, queue identifiers, power flags, regulatory state, TDLS/FTM/PTP/time-sync/ACS survey state, and restart/error buffers. `struct iwl_mvm_vif` and `struct iwl_mvm_vif_link_info` persist per-interface and per-link firmware IDs, AP station IDs, BSSID, queues, beacon/probe-response data, power/beacon-filter flags, CSA/ROC/session protection fields, IPv6 offload addresses, keys, and debugfs overrides. Most persistence is in kernel memory; NVM sections, regulatory results, firmware key tables, and MEI CSME ownership data mirror hardware/firmware state and must be rebuilt across restart.

## Dependencies And Integration Points
Depends heavily on mac80211/cfg80211, the iwlwifi transport layer, firmware runtime/debug APIs, firmware command definitions, NVM parsing, ACPI/UEFI, MEI coexistence, thermal, PTP, and Linux networking structures. It is the integration point between MVM implementation files and external callback tables: `iwl_mvm_hw_ops`, `iwl_mvm_mld_hw_ops`, and op-mode callbacks in `ops.c`.

## Risks And Edge Cases
The header encodes many firmware-version compatibility decisions; incorrect feature gating can select the wrong command size or field layout. State fields have mixed locking requirements: `mvm->mutex`, RCU, spinlocks, wiphy lock, and workqueues all appear in the contracts. Per-link MLO state coexists with legacy `deflink`, so callers must use the correct link path. Queue constants and firmware IDs use sentinel values, and accidental reuse can stall TX or remove the wrong station. Debugfs and compile-time feature guards change struct contents and helper behavior.

## Test Signals
Build with combinations of `CONFIG_IWLWIFI_DEBUGFS`, `CONFIG_PM_SLEEP`, `CONFIG_THERMAL`, `CONFIG_IWLWIFI_KUNIT_TESTS`, `CONFIG_IWLMEI`, and LED support. Exercise firmware capability matrices for old/new RX, old/new TX, MLD/non-MLD, CDB, RLC offload, LAR, quota versions, and ultra-high-band channel info. Runtime signals include successful mac80211 registration, interface add/remove, scan, association, channel switch, power-save update, firmware restart, WoWLAN, PTP registration, and clean teardown without lockdep or RCU warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h -->
