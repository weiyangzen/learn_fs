# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pagealloc.c

## Purpose

`pagealloc.c` is the mlx5 firmware-page allocator. mlx5 firmware asks the host for 4 KiB adapter pages during boot, initialization, VF/SF enablement, and runtime events; this file allocates host pages, maps them for DMA, tracks the sub-4K slices handed to firmware, and reclaims them when firmware returns pages or when teardown forces recovery.

## Important APIs, Types, and Functions

Key local state is `struct fw_page`, an RB-tree node keyed by DMA page address with a `bitmask` and `free_count` for `MLX5_NUM_4K_IN_PAGE` adapter pages, plus `struct mlx5_pages_req`, the work item used for asynchronous page-request EQ events. The per-function RB roots live in `dev->priv.page_root_xa`; reusable partially free system pages are linked through `dev->priv.free_list`.

Exported or lifecycle functions are `mlx5_pagealloc_init()`, `mlx5_pagealloc_start()`, `mlx5_pagealloc_stop()`, `mlx5_pagealloc_cleanup()`, `mlx5_satisfy_startup_pages()`, `mlx5_reclaim_startup_pages()`, and `mlx5_wait_for_pages()`. Core helpers include `give_pages()`, `reclaim_pages()`, `release_all_pages()`, `alloc_system_page()`, `alloc_4k()`, `free_4k()`, `insert_page()`, `find_fw_page()`, and the EQ notifier `req_pages_handler()`.

## Control Flow

Startup calls `mlx5_satisfy_startup_pages()`, which issues `QUERY_PAGES` for boot or init pages and, if firmware requests pages, calls `give_pages()`. `give_pages()` allocates an input buffer large enough for all PAS entries, repeatedly obtains 4K adapter addresses from existing partially free host pages or allocates/maps a new system page, and sends `MANAGE_PAGES` with `MLX5_PAGES_GIVE`. On command failure it returns every not-yet-accepted 4K slice to software state and optionally notifies firmware with `MLX5_PAGES_CANT_GIVE`.

Runtime requests arrive through the `PAGE_REQUEST` EQ notifier. `req_pages_handler()` decodes function id, EC-function and release-all flags, clamps large negative reclaim requests to firmware limits, allocates a `mlx5_pages_req` with `GFP_ATOMIC`, and queues it on the single threaded page allocator workqueue. `pages_work_handler()` then serializes give, reclaim, or release-all behavior outside interrupt context.

Reclaim uses `MANAGE_PAGES` with `MLX5_PAGES_TAKE`; returned PAS entries are passed to `free_4k()`. If firmware is already gone and `mlx5_cmd_do()` returns `-ENXIO`, `reclaim_pages_cmd()` fabricates output entries from the driver's own RB-tree so the host can forcibly unmap/free pages. `mlx5_reclaim_startup_pages()` walks every function root in the xarray and repeatedly asks firmware for optimal batches until each root is empty or timeout expires.

## State and Persistence Behavior

The file mutates long-lived `dev->priv` state: `page_root_xa`, `free_list`, `pg_wq`, `pg_nb`, aggregate `fw_pages`, per-function-type `page_counters[]`, and diagnostic counters such as `fw_pages_alloc_failed`, `give_pages_dropped`, and `reclaim_pages_discard`. Function identity combines firmware function id and embedded CPU flag into an xarray key; this lets host PF, VF, EC VF, SF, and self pages be reclaimed independently.

The backing storage is ordinary allocated pages DMA-mapped bidirectionally. Firmware only persists the PAS entries it accepted. The driver persists exact subpage ownership in memory and relies on teardown paths to reclaim or force-free anything not returned cleanly.

## Dependencies and Integration Points

This code depends on the mlx5 command interface (`QUERY_PAGES`, `MANAGE_PAGES`), EQ notifier registration, timeout helpers, debugfs page counters, DMA mapping APIs, Linux xarray/RB-tree/list primitives, and device role helpers such as `mlx5_core_is_ecpf()`, `mlx5_core_max_vfs()`, and `mlx5_sf_max_functions()`. SR-IOV teardown calls `mlx5_wait_for_pages()` against VF and EC-VF counters, so page accounting here directly affects VF disable/unload behavior.

## Risks and Edge Cases

The RB-tree comparison is inverted from the usual left-less/right-greater convention but is internally consistent; future edits must preserve matching traversal in insert and lookup. `alloc_system_page()` remaps the same page when DMA address zero is returned and only unmaps the zero mapping later; this unusual retry path is worth regression testing on IOMMUs that can hand out address 0. `free_4k()` trusts firmware-returned PAS entries to point at known tracked pages and only warns if not found. `release_all_pages()` bypasses firmware and adjusts counters based on allocated subpage count, so it must only run when firmware has declared release-all or teardown owns the device.

## Test Signals

Useful signals are boot/init page satisfaction, VF/SF enable-disable loops, EC-PF page accounting, firmware page-request EQ injection, forced internal-error reclaim where firmware commands return `-ENXIO`, debugfs page counters returning to zero, and `mlx5_wait_for_pages()` not timing out during SR-IOV teardown. Fault injection should cover allocation failure, DMA mapping failure, `MANAGE_PAGES` remote IO errors, oversized reclaim events, and duplicate PAS insertion.
