<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c

## Purpose

This file implements the firmware-backed `struct mlx5_flow_cmds` vtable for flow steering. It translates in-memory flow steering objects into mlx5 firmware commands for flow tables, groups, entries, counters, packet reformat contexts, modify-header contexts, match definers, and root table updates. It also provides stub commands for unsupported/software-only table types.

## Important APIs, types, and functions

- `mlx5_flow_cmds` is populated with firmware implementations; `mlx5_flow_cmd_stubs` provides no-op or unsupported behavior.
- Flow table functions create/destroy/modify tables and update roots, including FDB shared-LAG peer propagation.
- Flow group functions create/destroy groups with vport/other-eswitch metadata.
- `mlx5_cmd_set_fte()` is the central FTE encoder: it writes match values, actions, VLAN push fields, packet reformat IDs, modify-header IDs, crypto, ASO flow-meter controls, destination lists, extended destinations, and counters.
- Flow counter APIs allocate/free/query single and bulk counters.
- Packet reformat and modify-header allocators validate capability limits, allocate firmware contexts, and store resource owner/id.
- Match definer helpers create/destroy general objects of type `MATCH_DEFINER`.
- `mlx5_fs_cmd_get_default()` chooses firmware commands for real table types and stubs otherwise.

## Control flow

Creation functions fill command input buffers with device/table metadata and execute firmware commands. On flow table create, the table size is allocated from `fs_ft_pool`; failure returns the size to the pool. FTE create/update share `mlx5_cmd_set_fte()` with different opmods and modify masks. Root update programs `SET_FLOW_TABLE_ROOT`, with special handling for IB underlay QPNs and shared FDB LAG peers. Resource allocation APIs allocate firmware objects and deallocation APIs best-effort destroy them.

## State and persistence

The file mutates firmware state and writes identifiers back into software objects (`ft->id`, `ft->max_fte`, `fg->id`, reformat/modify-header/definer IDs). Flow counter statistics live in firmware until queried or cleared elsewhere. Table-size pool accounting is software state tied to successful create/destroy.

## Dependencies and integration points

It depends on generated IFC command layouts, `mlx5_cmd_exec*`, device capability macros, `fs_core.h` object definitions, `fs_ft_pool`, e-switch/LAG helpers, and packet reformat ID adapters for DR/HWS ownership. `fs_core.c` calls this vtable through each root namespace.

## Risks

Encoding mistakes in `mlx5_cmd_set_fte()` can misprogram forwarding, counters, VLAN, reformat, modify-header, crypto, or ASO behavior. Extended-destination support is capability-sensitive and limited by `log_max_fdb_encap_uplink`. Shared FDB LAG root update must roll back peers and master root on failure. Deallocators ignore command failures, so firmware leaks are possible on persistent command errors. Stub commands make unsupported table types appear software-only; callers must not expect hardware effects.

## Test signals

Tests should cover table create/destroy pool accounting, miss-table modification, root updates with and without underlay QPNs, shared FDB LAG peer rollback, FTE create/update/delete for every destination type, multi-counter limits, extended encapsulated destinations, packet reformat size validation, modify-header action limits per namespace, match definer lifecycle, and silent L2/TX-root commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c -->
