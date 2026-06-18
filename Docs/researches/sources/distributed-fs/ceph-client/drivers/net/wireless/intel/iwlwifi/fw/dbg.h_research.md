<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h

Purpose: public firmware-debug interface for the iwlwifi firmware runtime. It declares dump descriptors, debug recording parameters, collection entry points, trigger helpers, timestamp helpers, error table setters, and runtime predicates used by op-mode code.

Important APIs/types: `struct iwl_fw_dump_desc` wraps trigger metadata with a flexible payload; `struct iwl_fw_dbg_params` stores DBGC register values for stop/restart. The header exposes all major collection functions from `dbg.c`, `iwl_fwrt_dump_error_logs()` from `dump.c`, and small helpers such as `iwl_fw_dbg_type_on()`, `iwl_fw_dbg_is_d3_debug_enabled()`, `iwl_fw_dbg_is_paging_enabled()`, `iwl_fw_flush_dumps()`, `iwl_fw_error_collect()`, and `iwl_fwrt_update_fw_versions()`.

Control flow: trigger macros enforce constant trigger ids with `BUILD_BUG_ON`, check legacy-vs-INI mode, VIF type, stop configuration masks, occurrence suppression windows, and then dispatch to collection. `iwl_fw_error_collect()` branches between legacy assert descriptor collection and synchronous INI timepoint collection based on `iwl_trans_dbg_ini_valid()`.

State and persistence: helper logic reads and updates `fwrt->dump.conf`, `fwrt->dump.non_collect_ts_start[]`, transport debug recording state under debugfs builds, error table addresses, and firmware version fields captured from ALIVE notifications.

Dependencies/integration: this header ties together `runtime.h`, firmware file/error-dump contracts, debug TLV APIs, cfg80211 interface types, ALIVE structs, PRPH/IO helpers, and command IDs. It is included by runtime initialization, dump/error paths, debugfs, and op-mode trigger code.

Risks/test signals: macro-heavy trigger checks can silently suppress dumps if config ids, VIF types, or no-collect windows are wrong. Build coverage with and without `CONFIG_IWLWIFI_DEBUGFS`, legacy and INI firmware, D3 debug, paging-enabled firmware, and multi-LMAC ALIVE error tables are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h -->
