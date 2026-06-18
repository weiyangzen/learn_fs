# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/debugfs.c

## Purpose
`lag/debugfs.c` exposes mlx5 LAG state through debugfs. It creates read-only files for LAG type, port-selection mode, active/disabled state, mode flags, port mapping, and member device names.

## Important APIs, Types, And Functions
- Show handlers `type_show`, `port_sel_mode_show`, `state_show`, `flags_show`, `mapping_show`, and `members_show` read `struct mlx5_lag` under `ldev->lock`.
- `get_str_mode_type` maps internal LAG modes to user-readable strings.
- `mlx5_ldev_add_debugfs` creates the `lag` debugfs directory and files under the mlx5 device debugfs root.
- `mlx5_ldev_remove_debugfs` recursively removes the directory.

## Control Flow And State
When a LAG-capable mdev is added, `lag.c` calls `mlx5_ldev_add_debugfs`. Each file uses `file->private` as the core device, resolves `mlx5_lag_dev`, locks the LAG object, snapshots or prints state, then unlocks. Inactive LAG returns `-EINVAL` for type, port-selection mode, flags, and mapping, while state always prints active or disabled.

## Dependencies And Integration Points
The file depends on Linux debugfs/seq_file helpers and `lag.h` functions such as `mlx5_get_str_port_sel_mode`, `mlx5_infer_tx_enabled`, and LAG iteration macros. It integrates only with diagnostic/debug paths and has no effect on LAG behavior.

## Risks And Edge Cases
Debugfs readers race with LAG teardown unless removal happens early and locking/lifetime are respected; `lag.c` removes debugfs early during mdev removal. Mapping output differs for hash-based and queue-affinity modes, so tools must parse both formats. Inactive mode returning `-EINVAL` is expected.

## Test Signals
Check debugfs file creation/removal on LAG-capable devices, correct output in disabled, RoCE, SR-IOV, multipath, and MPESW modes, hash and non-hash mapping formats, shared FDB flags, and safe reads during bond changes/removal.
