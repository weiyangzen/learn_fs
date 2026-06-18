<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h

## Purpose
`spectrum_dpipe.h` declares the Spectrum dpipe lifecycle API and stable devlink dpipe table names.

## Important APIs, Types, and Functions
The header declares `mlxsw_sp_dpipe_init()` and `mlxsw_sp_dpipe_fini()`, and defines table-name macros `MLXSW_SP_DPIPE_TABLE_NAME_ERIF`, `MLXSW_SP_DPIPE_TABLE_NAME_HOST4`, `MLXSW_SP_DPIPE_TABLE_NAME_HOST6`, and `MLXSW_SP_DPIPE_TABLE_NAME_ADJ`.

## Control Flow
There is no execution path in the header. It defines the initialization and teardown contract implemented by `spectrum_dpipe.c` and consumed by Spectrum core device bring-up/teardown.

## State and Persistence Behavior
The header stores no state. The names it defines become user-visible devlink table identifiers and therefore should remain stable.

## Dependencies and Integration Points
The declarations require `struct mlxsw_sp` from the Spectrum core headers included by users. The table names are consumed by dpipe table registration, resource assignment, and userspace devlink commands.

## Risks and Edge Cases
Changing table-name macros would break userspace scripts and tests that refer to existing devlink dpipe tables. Missing init/fini calls would leave dpipe headers or tables unregistered.

## Test Signals
Compile coverage plus `devlink dpipe table show` confirming the four expected table names are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h -->
