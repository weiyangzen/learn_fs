# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.c

## Purpose

This file implements the older generic ATOM PPLIB PowerPlay table parser. It initializes `hwmgr->dyn_state`, platform descriptors, thermal controller data, fan parameters, overdrive limits, DPM2 parameters, clock/voltage dependencies, phase shedding, and VCE state access for pre-v1.0 table layouts.

## Important APIs, Types, and Functions

The public APIs are `pp_tables_get_response_times()`, `pp_tables_get_num_of_entries()`, `pp_tables_get_entry()`, and the exported `pptable_funcs`. `pp_tables_get_entry()` supports both pre-format-6 fixed state entries and format-6 variable DPM-level entries, calls `init_non_clock_fields()`, and delegates clock-info parsing to an ASIC callback.

Internal helpers derive extended-header offsets for VCE, UVD, SAMU, ACP, PowerTune, PPM, and SCLK/VDDGFX tables; allocate normalized dependency tables; map BIOS platform caps; parse thermal/fan table revisions; read firmware-info overdrive limits; parse CAC leakage and phase shedding tables; and expose VCE state records through the `pp_table_func` callbacks.

## Control Flow and State

`pp_tables_initialize()` skips most work for `CHIP_RAVEN`, otherwise marks `need_pp_table_upload`, fetches and caches the PowerPlay table, maps caps, initializes thermal/overdrive/dependency/DPM2/phase-shedding state, and returns the first failing result. `pp_tables_uninitialize()` frees all dynamically allocated `hwmgr->dyn_state` subtables. `get_powerplay_table()` uses a static dummy table for Raven and otherwise caches the ATOM PowerPlayInfo table in `hwmgr->soft_pp_table`.

## Dependencies and Integration

The parser depends on `pptable.h` legacy ATOM layouts, `smu_atom_get_data_table`, endian helpers, kernel allocation, AMDGPU PCI/device identity, hwmgr capability helpers, and ASIC callbacks for clock-info conversion. SMU10 still wires `hwmgr->pptable_func = &pptable_funcs`, so this legacy parser participates in Raven-family power-state enumeration even while other data comes from SMU tables.

## Risks and Test Signals

The code performs extensive offset arithmetic on firmware data with uneven validation. Several range checks use `entry_index > count` instead of `>= count`. VCE/UVD/SAMU/ACP offset helpers assume extended-header sizes encode table presence correctly. Raven has a dummy table but initialization and cleanup return early, so consumers must tolerate missing dyn_state subtables. Test signals include boot-time PP_ASSERT output, sane sysfs DPM levels, correct VCE/UVD clock dependency exposure, and clean unload without leaks.
