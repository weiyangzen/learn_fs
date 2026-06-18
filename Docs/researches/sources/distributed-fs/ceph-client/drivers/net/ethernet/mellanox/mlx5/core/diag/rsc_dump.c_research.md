# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.c

## Purpose

`rsc_dump.c` implements mlx5 firmware resource dumps. It discovers supported dump segment types from the firmware menu, creates a physical-address mkey for dump DMA, builds resource dump commands, and exposes an iterator-style API for callers to fetch dump pages.

## Important APIs, Types, and Functions

- `mlx5_rsc_dump_create()` allocates `struct mlx5_rsc_dump` if `MLX5_CAP_DEBUG(resource_dump)` is present.
- `mlx5_rsc_dump_init()` allocates a PD, creates a PA mkey, and reads the firmware dump menu.
- `mlx5_rsc_dump_cleanup()` destroys the mkey and deallocates the PD.
- `mlx5_rsc_dump_destroy()` frees software state.
- `mlx5_rsc_dump_cmd_create()` builds a command for a requested `struct mlx5_rsc_key`.
- `mlx5_rsc_dump_next()` triggers one dump page and returns whether more dump data remains.
- `mlx5_rsc_dump_menu()` reads menu pages and fills `fw_segment_type[]`.

## Control Flow

Initialization creates hardware resources and reads the menu using a special menu segment type. Menu parsing maps firmware segment names to local `enum mlx5_sgmt_type` indexes and records firmware segment IDs. Callers create a command with resource type/index/count/size, then repeatedly call `mlx5_rsc_dump_next()`. Each trigger DMA maps the provided page, fills mkey/address in the command, accesses `MLX5_REG_RESOURCE_DUMP`, validates the firmware sequence number, unmaps the page, and returns `more_dump`.

## State and Persistence Behavior

Persistent state in `dev->rsc_dump` includes PD number, mkey, number of menu items, and the firmware segment type map. Command state stores the firmware resource dump command buffer and requested memory size; firmware updates the command buffer with sequence, size, and continuation flags across calls.

## Dependencies and Integration Points

Depends on mlx5 debug capabilities, core PD/mkey APIs, DMA mapping, firmware register access, Linux pages, and segment definitions from `<linux/mlx5/rsc_dump.h>`. It is used by Ethernet health dumping (`en/health.c`) and other diagnostics.

## Risks and Edge Cases

- `mlx5_rsc_dump_cmd_create()` rejects segment type zero except for menu, so firmware using zero for a real segment would be treated unsupported.
- Menu parsing compares string names; unknown names are ignored.
- `cmd->mem_size` comes from the key and must not exceed the actual mapped page size used by callers.
- Sequence mismatch returns `-EIO`, indicating lost or corrupted dump continuation.
- Cleanup assumes init succeeded enough to create mkey/PD when `dev->rsc_dump` is non-null; lifecycle callers must pair correctly.

## Test Signals

Run resource dump init on capable and incapable devices. Dump menu and known resources such as QP/CQ/MKEY. Exercise multi-page dumps and verify sequence increments. Fault-inject DMA mapping, mkey creation, menu read, and register access failures.
