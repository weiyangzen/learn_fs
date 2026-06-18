# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-op-mode.h

Purpose: Defines the operational-mode abstraction between the iwlwifi driver/transport layer and mac80211/firmware-policy implementations.

Important APIs and types: `enum iwl_fw_error_type`, `enum iwl_fw_error_context`, `struct iwl_fw_error_dump_mode`, `struct iwl_op_mode_ops`, `iwl_opmode_register()`, `iwl_opmode_deregister()`, `struct iwl_op_mode`, and inline wrappers for stop, RX, RSS RX, queue full/not-full, RF-kill, skb free, NIC error, dump/error, NIC config, WiMAX, debug timepoints, powered-off, and dump callbacks.

Control flow: Driver code registers an opmode, starts it after transport allocation, then transport invokes wrappers on RX, queue state, RF-kill, errors, and debug events. Wrappers enforce sleep expectations with `might_sleep()` where needed and guard optional callbacks.

State and persistence: `struct iwl_op_mode` stores an ops pointer and aligned private data. Error dump mode carries reset reason and context, including abort semantics when stop/reset races occur.

Dependencies and integration points: Includes netdevice/debugfs and debug TLV definitions. Transport core uses it for firmware errors and reset handling; opmodes use it to bridge firmware APIs to mac80211.

Risks: Context requirements are strict: RX/queue callbacks cannot sleep, dump callbacks may sleep, and `IWL_ERR_CONTEXT_ABORT` must be checked after locks. `rx_rss` is mandatory for multi-queue-capable hardware. Callback recursion into iwlmei or transport contexts can deadlock if contracts are violated.

Test signals: Opmode registration lifecycle, RX and RSS dispatch, RF-kill state changes, reset/error dump race handling, queue-full callbacks with BH disabled, and optional callback absence.
