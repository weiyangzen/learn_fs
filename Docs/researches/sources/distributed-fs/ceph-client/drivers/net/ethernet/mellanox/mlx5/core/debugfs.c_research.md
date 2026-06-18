# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/debugfs.c

## Purpose

`debugfs.c` builds the mlx5 debugfs surface for core device state. It creates the global `mlx5` debugfs root, per-device debugfs directories, command-interface statistics, firmware page counters, VHCA ID reporting, and dynamic per-resource trees for QPs, EQs, and CQs.

The file is diagnostic-only, but its reads are active: QP/EQ/CQ files issue firmware queries or CQ queries when users read debugfs entries.

## Important APIs, Types, and Functions

- `mlx5_register_debugfs()` / `mlx5_unregister_debugfs()` create and remove the global `mlx5_debugfs_root`.
- `mlx5_debugfs_get_dev_root()` returns `dev->priv.dbg.dbg_root`.
- `mlx5_qp_debugfs_init()`, `mlx5_eq_debugfs_init()`, `mlx5_cq_debugfs_init()`, and matching cleanup routines create resource subdirectories.
- `mlx5_cmdif_debugfs_init()` creates `commands/`, `slots_inuse`, and one directory per known command opcode with counters such as `n`, `average`, `failed`, and last failure fields.
- `mlx5_pages_debugfs_init()` exposes firmware page counters for PF/VF/SF/host-PF allocations and failure/drop accounting.
- `mlx5_debug_qp_add/remove()`, `mlx5_debug_eq_add/remove()`, and `mlx5_debug_cq_add/remove()` attach per-object debug entries through `add_res_tree()`.
- `qp_read_field()`, `eq_read_field()`, and `cq_read_field()` are read callbacks that query firmware or core CQ state and convert fields into text.

Key local structures are `struct mlx5_rsc_debug` and `struct mlx5_field_desc`, which connect a debugfs file back to a resource object and field index.

## Control Flow

Device setup creates top-level directories first, then command/page/resource directories. Command debugfs initializes `dev->cmd.stats` as an xarray, allocates one `struct mlx5_cmd_stats` per known opcode, and creates counter files under the opcode name. Cleanup removes the command tree, frees every xarray value, and destroys the xarray.

For resource objects, callers add an object after QP/EQ/CQ creation. `add_res_tree()` allocates a flexible `mlx5_rsc_debug`, creates a directory named by the resource number, then creates one file per field. File reads recover the owning `mlx5_rsc_debug` from the embedded field descriptor, dispatch by resource type, query hardware if needed, and return either a hex value or string.

## State and Persistence Behavior

Persistent state lives in debugfs dentries stored under `dev->priv.dbg`, command statistics in `dev->cmd.stats`, and per-object `qp->dbg`, `eq->dbg`, and `cq->dbg` pointers. `reset_write()` mutates command statistics by zeroing counters under `stats->lock`. Page counter files directly expose live fields in `dev->priv`.

Debugfs entries do not persist across driver unload. Resource file reads are snapshots and may return zero if allocation/query fails.

## Dependencies and Integration Points

The file depends on Linux debugfs, simple file operations, xarray, mlx5 command query helpers, CQ query helpers, QP/EQ/CQ core structures, and `lib/eq.h`. It integrates with QP/CQ/EQ allocation paths, command execution accounting, firmware page management, and VHCA capability reporting.

## Risks and Edge Cases

- `add_res_tree()` uses `sprintf(resn, "0x%x", rsn)` into a 32-byte buffer; resource numbers are bounded enough for current use, but `snprintf` would be more defensive.
- `dbg_read()` reconstructs the parent `mlx5_rsc_debug` with pointer arithmetic from a flexible array member. Layout changes to `struct mlx5_rsc_debug` or field allocation must preserve this assumption.
- `mlx5_debug_eq_remove()` removes `eq->dbg` but does not clear it, unlike QP/CQ removal. Repeated remove calls depend on outer lifecycle not reusing the stale pointer.
- QP/EQ/CQ reads issue firmware operations from debugfs read context and may fail during teardown, reset, or device error.
- Command stats cleanup frees xarray values after removing debugfs; readers must be excluded by debugfs removal semantics.

## Test Signals

Build with debugfs enabled, mount debugfs, load/unload mlx5, and verify `mlx5/` tree removal. Exercise QP/CQ/EQ creation and destruction while reading entries. Run command failures and confirm command stats and reset behavior. Use fault injection for allocation failures in `mlx5_cmdif_alloc_stats()` and `add_res_tree()`.
