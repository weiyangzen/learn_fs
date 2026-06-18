<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h

## Purpose

This header defines the command-provider interface used by `fs_core.c` to operate on flow steering objects. It abstracts firmware-managed, software-managed, and hardware-steering implementations behind `struct mlx5_flow_cmds`.

## Important APIs, types, and functions

- `struct mlx5_flow_cmds` contains callbacks for flow table/group/FTE lifecycle, root updates, packet reformat and modify-header contexts, namespace peer/create/destroy, match definer lifecycle, and capability reporting.
- Flow counter helpers are declared separately: alloc, bulk alloc, free, query, bulk query length, and bulk query.
- Provider selectors `mlx5_fs_cmd_get_default()` and `mlx5_fs_cmd_get_fw_cmds()` return command vtables.
- Misc command helpers set L2 silent mode and TX flow table root.
- `mlx5_fs_cmd_is_fw_term_table()` identifies termination tables by `MLX5_FLOW_TABLE_TERMINATION`.

## Control flow

The header has no runtime control flow. It defines callback signatures and utility declarations used by root namespaces to dispatch operations.

## State and persistence

No state is stored here. The vtable contract governs how `fs_core.c` persists software objects into firmware or alternate steering backends.

## Dependencies and integration points

It includes `fs_core.h` for object and enum definitions. Firmware implementation lives in `fs_cmd.c`; alternate command providers for DR/HWS are selected by `fs_core.c` when namespace mode changes.

## Risks

The callback contract is broad and stateful: implementations must update IDs, honor root/table/vport metadata, and keep software and hardware synchronized. Adding a callback requires all providers and stubs to be updated. The inline termination-table helper only checks a flag, so it assumes flags accurately reflect firmware object semantics.

## Test signals

Build tests should cover all providers. Runtime tests should exercise switching FDB namespace modes, command-provider fallback, termination table detection, and every callback path through `fs_core.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h -->
