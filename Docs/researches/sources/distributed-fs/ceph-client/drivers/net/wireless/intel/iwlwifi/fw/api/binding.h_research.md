# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/binding.h

Purpose: Defines firmware binding-context commands and time-quota allocation commands for associating MAC contexts with PHY contexts and scheduler airtime quotas.

Important APIs and types: `struct iwl_binding_cmd_v1` and `iwl_binding_cmd` carry binding ID/color, action, up to three MAC IDs, PHY ID, and optional LMAC ID. `IWL_BINDING_CMD_SIZE_V1` supports old firmware sizing. `struct iwl_time_quota_cmd_v1` and `iwl_time_quota_cmd` carry up to four binding quota entries, with v2 adding low-latency flags from `enum iwl_quota_low_latency`.

Control flow: No local execution. Runtime MAC/PHY context code sends add/modify/remove binding commands and then time-quota commands so firmware can schedule active roles.

State and persistence: No driver state here. Firmware stores binding and quota state until modified or removed.

Dependencies and integration points: Includes firmware file/image headers and relies on context ID/color/action definitions from `context.h`. Used by MVM context management, multi-MAC operation, CDB dual-band scheduling, and low-latency policy.

Risks: Binding table limits (`MAX_MACS_IN_BINDING`, `MAX_BINDINGS`) must match firmware. v1/v2 command size selection is required for older firmware. Quotas are absolute TU values and incorrect balancing can starve contexts.

Test signals: Add/modify/remove bindings on single and dual LMAC devices, v1/v2 command version selection, zero/auxiliary fourth quota on non-CDB, low-latency TX/RX flags, and quota saturation at `IWL_MVM_MAX_QUOTA`.
