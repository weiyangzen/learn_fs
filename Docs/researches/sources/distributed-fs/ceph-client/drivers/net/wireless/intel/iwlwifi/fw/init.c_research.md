<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c

Purpose: initializes firmware runtime state and sends early runtime configuration commands.

Important APIs/functions: `iwl_fw_runtime_init()` wires runtime pointers, sanitize/op-mode hooks, dump work items, and debugfs. `iwl_fw_runtime_suspend()`/`iwl_fw_runtime_resume()` emit INI D3 timepoints and manage timestamp work. `iwl_set_soc_latency()` sends `SOC_CONFIGURATION_CMD`. `iwl_configure_rxq()` sends `RFH_QUEUE_CONFIG_CMD` for non-default RX queues on newer devices.

Control flow: runtime init zeroes the struct, sets `FW_DBG_INVALID`, initializes each delayed dump worker with its index, then calls debugfs registration. SOC latency builds flags from integrated/discrete configuration, LTR delay, low-latency XTAL, and command version. RX queue config skips single-queue and pre-22000 devices, then gathers per-queue DMA addresses from transport before sending one host command.

State and persistence: initializes `struct iwl_fw_runtime` and mutates timestamp/dump work state. Configuration persists in firmware/transport until reset.

Dependencies/integration: depends on transport info/config, firmware command-version lookup, runtime ops, debugfs gate, and data-path/system command definitions.

Risks/test signals: initialization order is important because dump workers and debugfs can later reference runtime fields. Test init teardown paths, D3 suspend/resume timepoints, SoC latency flags for integrated vs discrete devices, command version thresholds, multi-RXQ DMA data failures, and command send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c -->
