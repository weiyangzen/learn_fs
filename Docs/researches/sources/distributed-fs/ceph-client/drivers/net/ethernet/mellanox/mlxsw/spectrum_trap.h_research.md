# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.h

## Purpose

`spectrum_trap.h` defines the Spectrum-specific trap subsystem state and ASIC operation hooks used by `spectrum_trap.c` and core Spectrum initialization.

## Important APIs, Types, And Functions

`struct mlxsw_sp_trap` stores arrays of trap policer, group, and trap items; their counts; the reserved thin policer hardware id; the maximum number of hardware policers; and a flexible policer usage bitmap. `struct mlxsw_sp_trap_ops` lets each ASIC generation return additional group and trap item arrays through `groups_init` and `traps_init`.

The header exports `mlxsw_sp1_trap_ops` and `mlxsw_sp2_trap_ops`. Spectrum-1 and Spectrum-2 share the common trap table from the C file but differ in sampling and buffer-drop trap capabilities.

## Control Flow

Core initialization allocates `struct mlxsw_sp_trap` with enough bitmap storage for supported policers, assigns the appropriate `trap_ops`, and lets `spectrum_trap.c` concatenate common and ASIC-specific arrays during devlink trap initialization.

## State And Persistence

State is runtime-only and belongs to the driver instance. The flexible bitmap tracks hardware policer allocation across the reserved dummy policer and devlink-visible policers.

## Dependencies And Integration Points

The header includes Linux list and devlink headers and forward-relies on item structures defined privately in `spectrum_trap.c`. It is integrated with devlink callbacks in the mlxsw core driver ops.

## Risks And Edge Cases

The flexible bitmap must be allocated with enough trailing storage for `max_policers`; undersized allocation would corrupt memory. ASIC ops must provide arrays whose lifetime outlives initialization because the C file copies them immediately but relies on accurate counts.

## Test Signals

Compile coverage should catch mismatches between ops and implementation. Runtime signals are correct trap sets for Spectrum-1 versus Spectrum-2 and correct policer bitmap accounting during init/fini. No local executable tests were run for this research item.
