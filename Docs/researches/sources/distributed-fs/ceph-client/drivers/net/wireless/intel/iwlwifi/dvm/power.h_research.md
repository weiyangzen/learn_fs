# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.h

## Purpose

`power.h` declares the DVM power-management state container and public power-mode functions. It is the interface between the broad driver state in `dev.h`, firmware power commands in `commands.h`, and the implementation in `power.c`.

## Important APIs, Types, and Functions

`struct iwl_power_mgr` stores the currently applied sleep command, the next sleep command deferred during scanning, a debug sleep-level override, and whether bus power management is supported/enabled. The declared functions are `iwl_power_set_mode()`, `iwl_power_update_mode()`, and `iwl_power_initialize()`.

## Control Flow

Callers initialize `priv->power_data` once during op-mode start, then call `iwl_power_update_mode()` when firmware becomes alive or when mac80211/power/thermal state changes. Lower-level callers that already prepared a command can call `iwl_power_set_mode()` directly, normally while holding `priv->mutex`.

## State and Persistence Behavior

The header has no storage of its own, but `struct iwl_power_mgr` persists in `struct iwl_priv`. Its fields represent both software cache and pending firmware state, so callers must treat them as part of the device lifecycle and reset/reinitialize them on full teardown.

## Dependencies and Integration Points

The header includes `commands.h` for `struct iwl_powertable_cmd` and is included by `dev.h`. It integrates with `power.c`, `main.c`, `lib.c` WoWLAN flow, thermal throttling, mac80211 configuration, and firmware command dispatch.

## Risks and Edge Cases

The API contract is mostly implicit: `iwl_power_set_mode()` requires the driver mutex and may defer during scans. New callers must not assume an immediate firmware update just because the cached next command changed. The debug override is an integer and should stay in the valid power-index range or be reset to `-1`.

## Test Signals

Compile all users for prototype drift, run lockdep around direct `iwl_power_set_mode()` callers, and validate that initialization sets `debug_sleep_level_override = -1`, detects bus PM support, and clears cached sleep command state.
