<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h

## Purpose
Defines the DEVX object wrapper shared by mlx5 DEVX implementation and other mlx5 IB subsystems, and provides DEVX lifecycle prototypes or stubs depending on `CONFIG_INFINIBAND_USER_ACCESS`.

## Important APIs, Types, And Functions
- `MLX5_MAX_DESTROY_INBOX_SIZE_DW` sizes the embedded destroy mailbox to the largest currently needed destroy command (`delete_fte_in`).
- `struct devx_obj` stores object ownership (`ib_dev`, `obj_id`), destroy command (`dinlen`, `dinbox`), flags, object-specific state (`mkey`, `core_dct`, `core_cq`, or `flow_counter_bulk_size`), and event subscription list.
- `mlx5_ib_devx_create()` / `mlx5_ib_devx_destroy()` manage firmware user contexts.
- `mlx5_ib_devx_init()` / `mlx5_ib_devx_cleanup()` manage device-level DEVX event infrastructure.
- `mlx5_ib_ufile_hw_cleanup()` supports hardware cleanup of DEVX objects during uverbs file teardown.
- Stubs return `-EOPNOTSUPP` or no-op when user access is disabled.

## Control Flow
The header has no direct runtime flow. Build-time `#if IS_ENABLED(CONFIG_INFINIBAND_USER_ACCESS)` selects real DEVX declarations or inline no-op fallbacks, allowing the rest of mlx5 IB to compile when uverbs user access is not enabled.

## State And Persistence
`struct devx_obj` instances persist for the lifetime of DEVX uverbs objects. The embedded destroy mailbox persists the exact command needed to free the hardware object during cleanup, while the union stores auxiliary kernel state for special object classes.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` for mlx5 IB private types and core object wrappers. `devx_obj` is consumed by `devx.c` and by flow steering code that accepts DEVX objects as flow destinations or counters.

## Risks And Edge Cases
The destroy inbox size must remain large enough for every destroy command emitted by `devx_obj_build_destroy_cmd()`. The union relies on flags/opcode context to interpret the active member correctly. If user access is disabled, callers must handle `mlx5_ib_devx_create()` returning `-EOPNOTSUPP`.

## Test Signals
Build with `CONFIG_INFINIBAND_USER_ACCESS=y`, `m`, and disabled to verify real and stub paths. Compile-time checks should cover `struct devx_obj` users in DEVX and flow steering. Runtime tests should validate that every created DEVX object has a correct destroy mailbox within the configured size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/devx.h -->
