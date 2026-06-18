# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/hw_table.c

## Purpose

`sf/hw_table.c` owns mlx5 SF hardware-function-id allocation. It maps user SF numbers to software indexes and firmware function IDs for local and external controllers, registers devlink resources that expose maximum SF capacity, allocates/deallocates SFs in firmware, and handles deferred recycling after VHCA detach events.

## Important APIs, Types, and Functions

`struct mlx5_sf_hw` records user SF number, allocation state, and pending-delete state for one software slot. `struct mlx5_sf_hwc_table` stores the per-controller slot array, max function count, and base hardware function id. `struct mlx5_sf_hw_table` wraps local and external controller tables with `table_lock`.

Public functions are `mlx5_sf_sw_to_hw_id()`, `mlx5_sf_hw_table_sf_alloc()`, `mlx5_sf_hw_table_sf_free()`, `mlx5_sf_hw_table_sf_deferred_free()`, `mlx5_sf_hw_table_init()`, `mlx5_sf_hw_table_cleanup()`, `mlx5_sf_hw_notifier_init()`, `mlx5_sf_hw_notifier_cleanup()`, `mlx5_sf_hw_table_destroy()`, and `mlx5_sf_hw_table_supported()`.

## Control Flow

Initialization requires VHCA event support, queries local max SFs and external HPF SF capacity/base id, registers devlink resources `max_local_SFs` and `max_external_SFs`, allocates the table, initializes local/external slot arrays, and stores it in `dev->priv.sf_hw_table`. Allocation locks the table, finds a free software slot while rejecting duplicate user `sfnum`, computes the hardware function id, sends `ALLOC_SF`, writes the software function id with `mlx5_modify_vhca_sw_id()`, arms VHCA events for external-controller SFs, traces allocation, and returns the software id.

Immediate free locks, computes hardware id, sends `DEALLOC_SF`, and clears slot state. Deferred free queries VHCA state; if already ALLOCATED, it deallocates immediately and clears allocation, otherwise it marks `pending_delete`. The VHCA notifier listens for ALLOCATED events, maps function id back to the right controller table and software id, and deallocates any allocated slot marked pending delete. Destroy force-deallocates all still allocated local and external SFs, covering missed firmware events.

## State and Persistence Behavior

Driver state is `dev->priv.sf_hw_table`, slot arrays, allocation bits, user SF numbers, and pending-delete bits. Firmware state is the allocated SF function, its software id, event arm state, and eventual VHCA state. Devlink resource registration persists visible max-SF capacities until cleanup unregisters resources.

## Dependencies and Integration Points

The file depends on SF command wrappers, VHCA event/query/arm helpers, eswitch external controller capacity query, devlink resource APIs, SF tracepoints, and `mlx5_sf_devlink.c` as the primary allocator user.

## Risks and Edge Cases

Duplicate detection is per controller table, so the same user SF number may be valid on separate controller domains. Deferred free relies on receiving a later ALLOCATED event; `mlx5_sf_hw_table_destroy()` is the safety net for missed events. `mlx5_sf_hw_table_sf_deferred_free()` ignores query errors except for unlocking, leaving state unchanged; repeated delete/retry behavior should be checked. Devlink resource registration failure is logged but not fatal, so management visibility may be missing even when SFs work.

## Test Signals

Test allocation until local and external tables are full, duplicate `sfnum`, command failure rollback after `ALLOC_SF` and `MODIFY_VHCA_STATE`, deferred free while SF is IN_USE, ALLOCATED event recycling, destroy with pending slots, and devlink resource presence. Tracepoints should show alloc, deferred free, and final free with matching hardware ids.
