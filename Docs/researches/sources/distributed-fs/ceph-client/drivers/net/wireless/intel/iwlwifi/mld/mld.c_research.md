# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.c

Purpose: Defines the MLD op-mode module and its transport-facing `iwl_op_mode_ops`. It registers the `iwlmld` op-mode, constructs/destructs the main MLD object, configures transport command groups, starts initial firmware to read NVM, registers mac80211 hardware, and handles transport callbacks for queues, RF-kill, errors, dumps, reset, and power-off.

Important APIs/types/functions: module init/exit `iwl_mld_init()`/`iwl_mld_exit()`, `iwl_construct_mld()`, `iwl_op_mode_mld_start()`, `iwl_op_mode_mld_stop()`, `iwl_mld_configure_trans()`, firmware runtime ops, command-name group arrays `iwl_mld_groups`, queue callbacks, `iwl_mld_nic_error()`, `iwl_mld_sw_reset()`, `iwl_mld_dump_error()`, `iwl_mld_restart_nic()`, and `iwl_mld_ops`.

Control flow: Module init registers the op-mode. Start allocates `ieee80211_hw` with private op-mode plus MLD storage, initializes MLD structures/work, constructs firmware runtime, reads BIOS/UEFI policy, configures regulatory and transport settings, starts firmware under RTNL and wiphy locks with retries, reads NVM, flushes async handlers, stops firmware, initializes LED/scan/low-latency, registers mac80211 HW, initializes debugfs/thermal/PTP, and returns op-mode. Stop removes PTP/LED/thermal, stops low-latency/time-sync under wiphy lock, unregisters mac80211, frees firmware runtime and allocations, leaves transport op-mode, and frees HW.

State/persistence: Initializes and frees top-level persistent state in `struct iwl_mld`: transport/config/firmware/HW pointers, fw runtime, notification waits, async handler list/work, TXQ add list/work, RX queue sync waitqueue, NVM data, scan command, low-latency counters, LED, thermal, PTP, multicast filter, channel survey, and error recovery buffer. Error paths set `fw_status.in_hw_restart`, `do_not_dump_once`, scan abort state, and error recovery buffer for later firmware recovery.

Dependencies/integration: Integrates Linux module lifecycle, iwlwifi op-mode registry, transport configuration, UEFI/BIOS tables, firmware runtime debug, mac80211 HW registration, NVM parsing, LED/scan/low-latency/thermal/PTP/time-sync subsystems, and all command group name tables used by transport/debug.

Risks: Start error unwinding must free only initialized resources and leave transport op-mode. Initial firmware is started only to obtain NVM, then stopped before mac80211 registration. Command group arrays must remain sorted for binary search. Queue-full handling for unmapped internal queues stops all mac80211 queues. Error/restart paths must abort scan before restart to satisfy mac80211.

Test signals: Tests should cover op-mode start failure at each allocation/init stage, firmware load retry and NVM read failure, stop cleanup idempotence, command group lookup coverage, queue full/not-full mapping, RF-kill updates, NIC error dump/restart behavior, SW reset restart gating, and PM powered-off handling.
