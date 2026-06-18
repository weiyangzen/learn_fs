# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.h

Purpose: Defines DVM thermal throttling constants, states, restriction/transition structures, management state, and public thermal-throttling APIs.

Important APIs and types: `enum iwl_antenna_ok` models allowed antenna/stream use. `enum iwl_tt_state` defines normal, two throttled, and CT-kill states. `struct iwl_tt_restriction` encodes TX/RX stream and HT permissions. `struct iwl_tt_trans` encodes temperature ranges and next states. `struct iwl_tt_mgmt` stores current state, advanced-mode flag, power mode, optional previous temperature, tables, CT-kill toggle, and timers. Public prototypes expose current mode queries, restrictions, CT-kill handlers, initialization, and cleanup.

Control flow: This header has no executable flow; it is the ABI between DVM core code, TX/rate-control decisions, power management, and `tt.c` implementation.

State and persistence: The header owns no storage but defines the runtime `priv->thermal_throttle` layout. No durable persistence exists; state is reconstructed at driver start and cleaned at exit.

Dependencies and integration points: Includes DVM `commands.h` for thermal thresholds and power indices. Consumers use these declarations to gate HT support, choose TX antenna restrictions, and react to firmware CT-kill/card-state signals.

Risks: Changing enum order or struct layout can break table indexing in `tt.c`. `tt_previous_temp` exists only under `CONFIG_IWLWIFI_DEBUG`, so code must not rely on it outside that configuration. Timer fields require correct lifetime management by the implementation.

Test signals: Compile both debug and non-debug builds, advanced and legacy thermal configs, and all users of `iwl_ht_enabled()` and `iwl_tx_ant_restriction()`.
