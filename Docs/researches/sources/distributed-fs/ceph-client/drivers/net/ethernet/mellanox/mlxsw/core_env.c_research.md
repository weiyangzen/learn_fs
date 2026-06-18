# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_env.c

## Purpose
`core_env.c` manages transceiver/module environment state for mlxsw devices. It supports ethtool module info and EEPROM reads/writes, module resets, module power-mode policy, module temperature thresholds and overheat counters, plug and temperature-warning events, module type validation, and line-card activation/inactivation integration.

## Important APIs, Types, And Functions
- `struct mlxsw_env` owns the core pointer, bus info, maximum modules per slot, slot count including main board, maximum EEPROM transaction length, `line_cards_lock`, and per-slot `struct mlxsw_env_line_card` pointers.
- `struct mlxsw_env_line_card` stores active state, current module count, and flexible per-module `struct mlxsw_env_module_info` records.
- `struct mlxsw_env_module_info` caches overheat counter, current overheat state, number of mapped ports, number of administratively up ports, power-mode policy, and module type from PMTM.
- EEPROM APIs include `mlxsw_env_get_module_info()`, `mlxsw_env_get_module_eeprom()`, `mlxsw_env_get_module_eeprom_by_page()`, and `mlxsw_env_set_module_eeprom_by_page()`. They validate active line cards and module type, query MCIA, split reads/writes by hardware transaction length, process MCIA status, and handle SFP/QSFP/CMIS paging.
- Thermal APIs include `mlxsw_env_module_temp_thresholds_get()`, `mlxsw_env_module_overheat_counter_get()`, `mlxsw_env_module_has_temp_sensor()`, `mlxsw_env_temp_event_set()`, and MTWE event work.
- Reset and power APIs include `mlxsw_env_reset_module()`, `mlxsw_env_get_module_power_mode()`, `mlxsw_env_set_module_power_mode()`, `mlxsw_env_module_port_up()`, and `mlxsw_env_module_port_down()`.
- Mapping APIs `mlxsw_env_module_port_map()` and `mlxsw_env_module_port_unmap()` track how many ports share a module, which gates reset behavior.
- Initialization/finalization are `mlxsw_env_init()` and `mlxsw_env_fini()`. They allocate line-card/module caches, register linecard event ops, register MTWE/PMPE trap listeners, enable module events, cache module types, query MCIA transaction length, and clean up with ordered-workqueue flushes.

## Control Flow
Initialization queries MGPIR for module count and slot count. For modular systems, it allocates `num_of_slots + 1` line-card records and uses the maximum modules per slot; for non-modular systems, slot zero gets the main-board module count immediately. All module power policies default to high. It registers linecard active/inactive callbacks, temperature-warning and module-plug event listeners, enables PMAOS operation-state and MTMP temperature events for slot zero, queries module types through PMTM, detects whether 128-byte MCIA transactions are supported through MCAM, and marks the main board active.

EEPROM read flow first validates that the line card is active and the module type supports EEPROM access. Legacy ethtool reads detect cable identifier and use `mlxsw_env_query_module_eeprom()` in a loop, which clamps each transaction to `max_eeprom_len`, avoids crossing low-page boundaries, chooses I2C low/high address, adjusts QSFP/CMIS upper-page offsets, queries MCIA, checks status, and copies returned bytes. Page-based ethtool reads/writes use caller-provided page/bank/I2C address and loop until requested length is processed.

Power-mode flow is policy-driven. `HIGH` keeps modules high-power. `AUTO` transitions to low power when no mapped port is administratively up and back to high power when the first port goes up. Applying hardware power mode disables the module through PMAOS, writes the low-power override through PMMP, then re-enables the module; failure tries to restore the previous state. If a line card is inactive, policy is cached and applied by `mlxsw_env_got_active()`.

Event flow uses core trap listeners. MTWE temperature warnings are copied into heap work items; ordered work compares sensor warning bits to cached `is_overheat`, increments overheat counters only on no-warning to warning transitions, and clears state on recovery. PMPE plug events for plugged/enabled modules schedule work that clears overheat state, checks for a temperature sensor, and enables MTMP events. Linecard activation queries module count, enables module events, caches module types, marks active, and reapplies cached power policies.

## State And Persistence Behavior
Runtime state is cached in `mlxsw_env` and protected by `line_cards_lock`. Overheat counters persist only for the lifetime of the driver instance. Power-mode policy is cached per module and applied to hardware when possible; inactive line cards retain the desired policy until activation. Port map/up counters coordinate reset and auto-power decisions but are not persisted. EEPROM data and module hardware state are external device/module state reached through registers.

## Dependencies And Integration Points
The file integrates with Linux ethtool module APIs, SFP constants, netlink extack, mutexes, and mlxsw core trap/workqueue helpers. It depends on register definitions for MCIA, MTMP, MTBR, PMAOS, PMMP, MCION, PMPE, MGPIR, PMTM, and MCAM. It registers `mlxsw_linecards_event_ops` with the linecard subsystem and uses `mlxsw_core_env()` to retrieve the environment handle from core.

## Risks And Edge Cases
- Linecard/module indexing must stay within `num_of_slots` and `max_module_count`; PMPE validates with `WARN_ON_ONCE()`, but most public APIs assume valid caller indices.
- `mlxsw_env_module_event_disable()` is empty, so event disable relies mostly on unregister/fini and inactive flags. Future event additions need explicit disable handling.
- MTWE only supports the main board, so temperature warning work always updates slot zero even though other paths are slot-aware.
- Reset is rejected if any port using the module is administratively up or if multiple ports share the module without the shared reset flag.
- Power-mode transitions manipulate module enable state. Partial failures attempt rollback but can still leave hardware inconsistent if register writes fail repeatedly.
- EEPROM page and offset calculations differ for SFP, QSFP, and CMIS. Boundary mistakes can read wrong pages or overrun a caller request.
- Module type validation rejects twisted-pair modules for EEPROM/reset/power operations, so callers must surface `-EINVAL`/`-EOPNOTSUPP` clearly.

## Test Signals
Test non-modular and modular init paths, linecard active/inactive callbacks, EEPROM reads across low-page boundary and with 48-byte vs 128-byte MCIA limits, CMIS flat and paged module info, MCIA status-to-extack mapping, reset rejection for up/shared modules, auto power transitions on first port up and last port down, inactive-linecard policy caching, MTWE overheat counter transitions, PMPE plug event temperature enablement, and finalization with ordered work flushed before listener unregister/free.
