<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c

## Purpose
Implements the MVM op-mode module registration, device/op-mode startup and teardown, transport callback table, firmware notification dispatch, async notification worker model, debug dump sanitization, MEI/CSME ownership callbacks, queue backpressure handling, RF-kill/CT-kill state handling, and firmware error/restart hooks.

## Important APIs, Types, And Functions
Module entry points are `iwl_mvm_init` and `iwl_mvm_exit`. The op-mode callbacks are `iwl_op_mode_mvm_start`, `iwl_op_mode_mvm_stop`, `iwl_mvm_rx`, `iwl_mvm_rx_mq`, `iwl_mvm_rx_mq_rss`, `iwl_mvm_stop_device`, `iwl_mvm_set_hw_ctkill_state`, and helpers in `IWL_MVM_COMMON_OPS`. Important private structures include `struct iwl_rx_handlers`, `enum iwl_rx_handler_context`, `struct iwl_async_handler_entry`, `struct iwl_mvm_frob_txf_data`, and `mei_ops`. It exports command-name arrays `iwl_mvm_groups` for debug/KUnit command decoding.

## Control Flow
Module initialization registers rate control and the `"iwlmvm"` op-mode. `iwl_op_mode_mvm_start` allocates mac80211 HW with MLD or legacy ops, initializes `struct iwl_mvm`, firmware runtime, BIOS/UEFI tables, rate API version checks, RX/TX API selection, queue IDs, locks, lists, work items, notification waits, transport configuration, PHY DB, scan command buffer, thermal/TCM/time-sync state, MEI registration, NVM acquisition, and finally mac80211/debugfs registration. NVM acquisition uses CSME data when available, otherwise starts hardware, runs INIT firmware, initializes MCC/regulatory data, and stops the device.

Firmware RX dispatch first handles fast-path MPDU/PHY/data-path notifications, otherwise `iwl_mvm_rx_common` logs time points, checks debug triggers, wakes notification waiters, validates notification size, and either calls sync handlers directly or steals the RX page into an async handler list. Async work drains matching contexts with or without `mvm->mutex`, or through wiphy work when both wiphy and MVM locking are required. Queue state callbacks map hardware queues back to station/TID TXQs and stop/wake mac80211 queues or run pending TXQ transmission.

Stop and error paths unregister MEI/mac80211, cancel workers, exit LEDs/thermal/PTP, free scan/mcast/error/NVM/PHY DB/runtime allocations, leave the transport op-mode, and free HW. Firmware errors abort waits, delete debug timers, dump logs unless suppressed, set restart-request status, collect dumps with mutex protection, and request mac80211 restart only for supported regular-fw cases.

## State And Persistence
Creates and owns the lifetime of `struct iwl_mvm` and most fields declared in `mvm.h`: locks, workqueues, status bits, notification wait data, queue maps, scan buffers, PHY DB, firmware runtime, NVM data, MEI state, thermal/TCM/PTP state, debugfs state, and error recovery buffers. Hardware/firmware state is started and stopped through the transport. Debug dump sanitizers overwrite key material in captured TX FIFOs, host commands, and firmware memory dumps before persistence in debug dumps.

## Dependencies And Integration Points
Depends on Linux module/mac80211/cfg80211, iwlwifi op-mode registration, transport configuration, firmware runtime/debug APIs, PHY DB, NVM/regulatory helpers, rate control, scan/time-event/FTM/thermal/BT/MEI/time-sync subsystems, and all firmware notification handlers registered in `iwl_mvm_rx_handlers`. It is the main integration point between transport callbacks and MVM subsystems.

## Risks And Edge Cases
Startup has many partially initialized unwind paths; missing a cleanup leaks runtime, PHY DB, scan buffers, or MEI registration. Rate API consistency checks must match firmware command/notification versions. Async RX handlers steal RX pages and rely on context-specific locking; wrong context can deadlock or race. RF-kill during INIT must abort notification waits without double-stopping unified firmware. Queue mapping differs between old DQA and new TVQM APIs. Dump sanitization must avoid leaking encryption keys while not corrupting unrelated debug data. CSME-owned devices can defer mac80211 registration until SAP connection work completes.

## Test Signals
Exercise module load/unload, start failure at each allocation/init phase, CSME-owned startup with deferred SAP work, NVM from firmware and MEI, old/new RX APIs, old/new TX queue APIs, MLD and non-MLD registration, async notification contexts, unknown/short notifications, queue full/not-full callbacks, RF-kill and CT-kill changes, firmware crash/restart, debug dump collection/sanitization, and clean op-mode stop with no pending work or lockdep reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c -->
