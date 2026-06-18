# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/hcmd.h

Purpose: Provides the central MLD host-command send wrappers used by the rest of the op-mode. It standardizes locking, D3 safety, RF-kill behavior, and PDU command construction around `iwl_trans_send_cmd()`.

Important APIs/types/functions: `iwl_mld_send_cmd()`, `__iwl_mld_send_cmd_with_flags_pdu()`, `iwl_mld_send_cmd_with_flags_pdu()`, `iwl_mld_send_cmd_pdu()`, and `iwl_mld_send_cmd_empty()`.

Control flow: Synchronous commands assert that `wiphy->mtx` is held, while async commands skip that lockdep assertion. With PM sleep enabled, sending any command after entering D3 warns and returns `-EIO`. Every command is marked `CMD_SEND_IN_RFKILL` because this op-mode does not support devices that must shut down immediately on RF-kill. The PDU macros construct a stack `iwl_host_cmd` with inferred data length when the caller omits an explicit length.

State/persistence: The helper does not own persistent state, but it gates command emission on `mld->fw_status.in_d3` and mutates `cmd->flags` before transport submission.

Dependencies/integration: Included broadly by firmware, interface, key, LED, MCC, low-latency, and link code. It depends on `struct iwl_mld`, `struct iwl_host_cmd`, command flags, and transport command semantics.

Risks: Async callers are responsible for lifetime of payload buffers. The varargs macro infers `sizeof(*(data))`, so pointer type mistakes can silently send a wrong length unless an explicit length is supplied. Allowing send-in-RF-kill is intentional for this hardware family but would be unsafe if reused for a different transport contract.

Test signals: Compile-time coverage should exercise explicit and inferred PDU lengths. Runtime lockdep should flag synchronous command sends without `wiphy->mtx`, and PM tests should verify D3 command rejection.
