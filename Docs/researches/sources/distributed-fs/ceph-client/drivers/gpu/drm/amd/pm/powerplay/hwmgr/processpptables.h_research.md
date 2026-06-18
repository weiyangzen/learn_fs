# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.h

## Purpose

This header declares the public interface for the legacy PowerPlay table parser implemented in `processpptables.c`.

## Important APIs, Types, and Functions

`pptable_funcs` is the parser function table. `pp_tables_hw_clock_info_callback` is the ASIC callback type used to translate raw ATOM clock-info entries into a `pp_hw_power_state`. `pp_tables_get_num_of_entries()`, `pp_tables_get_entry()`, and `pp_tables_get_response_times()` expose the main read APIs for hwmgr backends.

## Control Flow and State

The header carries no executable logic. It defines a callback-driven flow: the generic parser handles BIOS table walking and non-clock fields, while the ASIC backend handles hardware-specific clock-info records.

## Dependencies and Integration

It forward-declares `pp_hwmgr`, `pp_power_state`, and `pp_hw_power_state` and relies on `struct pp_table_func` from included hwmgr context. It is included by SMU10 and other hwmgr files that need table enumeration or parser function-table assignment.

## Risks and Test Signals

The generic callback design keeps table walking reusable but makes correctness depend on matching the callback to the table format and ASIC. Compile coverage checks signature compatibility. Runtime signals are successful `get_num_of_entries`, per-state conversion, response-time reads, and boot-state patch behavior in ASIC backends.
