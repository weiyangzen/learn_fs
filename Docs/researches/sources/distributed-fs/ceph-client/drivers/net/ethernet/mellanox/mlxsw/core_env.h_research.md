# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.h

## Purpose
`core_env.h` declares the mlxsw environment/module management interface used by port drivers and ethtool integration. It exposes module EEPROM, reset, power-mode, thermal threshold, overheat counter, port mapping/up-down accounting, and environment lifecycle APIs while keeping `struct mlxsw_env` private.

## Important APIs, Types, And Functions
- `mlxsw_env_module_temp_thresholds_get()` retrieves module temperature thresholds.
- `mlxsw_env_get_module_info()` and `mlxsw_env_get_module_eeprom()` implement legacy ethtool module-info and EEPROM access.
- `mlxsw_env_get_module_eeprom_by_page()` and `mlxsw_env_set_module_eeprom_by_page()` implement page/bank-aware module EEPROM access.
- `mlxsw_env_reset_module()` handles ethtool PHY reset flags for modules.
- `mlxsw_env_get_module_power_mode()` and `mlxsw_env_set_module_power_mode()` expose ethtool module power-mode policy and current mode.
- `mlxsw_env_module_overheat_counter_get()` reports cached overheat transition counts.
- `mlxsw_env_module_port_map()`, `mlxsw_env_module_port_unmap()`, `mlxsw_env_module_port_up()`, and `mlxsw_env_module_port_down()` let port code report module sharing and administrative state.
- `mlxsw_env_init()` and `mlxsw_env_fini()` manage environment subsystem lifetime.

## Control Flow
The header's API shape makes port drivers call map/unmap as ports are associated with modules, port_up/down as administrative state changes, ethtool handlers call info/EEPROM/reset/power methods, and core lifecycle code call init/fini during device registration and unregister.

## State And Persistence Behavior
All persistent implementation state is hidden behind opaque `struct mlxsw_env`, returned from `mlxsw_env_init()` and destroyed by `mlxsw_env_fini()`. The public functions mutate per-module cached state and hardware state through the core pointer.

## Dependencies And Integration Points
The header includes Linux ethtool declarations and forward-declares ethtool structures. It depends on callers having valid `struct mlxsw_core`, `struct net_device`, slot index, and module index values. It is consumed by port drivers that implement ethtool module operations and by `core.c` for environment lifecycle.

## Risks And Edge Cases
- Public APIs accept raw slot/module numbers; caller-side validation matters because the implementation often assumes valid ranges.
- Port map/up counters must be balanced. Missing `unmap` or `port_down` calls can block resets or keep modules high-power.
- Page-based EEPROM writes can alter module state; users need extack feedback and hardware capability checks.

## Test Signals
Compile users for every ethtool hook, balanced map/unmap/up/down paths, init/fini pairing in core registration, error propagation through extack for page operations, and reset/power-mode behavior from port administrative state.
