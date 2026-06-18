# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/alive.h

Purpose: Defines firmware ALIVE notifications, debug pointer layouts, SKU/platform metadata, card-state flags, init-flow extension command, radio-version notification, and firmware error-recovery command ABI.

Important APIs and types: `struct iwl_alive_ntf_v3`, `iwl_alive_ntf_v7`, and `iwl_alive_ntf` represent versioned ALIVE payloads with LMAC/UMAC debug data, SKU, IMR, and platform ID. `struct iwl_lmac_alive`, `iwl_umac_alive`, and debug-address structs expose firmware error/event/log pointers. Enums define firmware type/subtype, card-state flags, extended init flags, and error-recovery flags.

Control flow: No executable flow; these structures are consumed by firmware loading and notification handlers to validate firmware state, collect debug addresses, and decide rfkill/card-state handling.

State and persistence: Header owns no state. ALIVE payload values become runtime device pointers and capability metadata in driver state.

Dependencies and integration points: Used by `commands.h` legacy `UCODE_ALIVE_NTFY`, DVM and MVM firmware startup, debug dump collection, card-state notification handling, and recovery command submission.

Risks: Versioned structs have different LMAC counts and trailing fields; handlers must use firmware API version/capability before casting. Status constants (`0xCAFE`/`0xDEAD`) and rfkill bits are firmware ABI. Debug addresses are device SRAM offsets and must not be treated as host pointers.

Test signals: Parse alive v3/v7/current notifications, dual-LMAC devices, rfkill flag handling, IMR enabled/disabled, platform ID presence, init extended cfg command submission, card-state CT-kill/rfkill flags, and error-recovery command flags.
