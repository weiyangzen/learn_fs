# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/pd.c

## Purpose
`pd.c` manages protection domains, XRC domains, user access regions (UARs), and BlueFlame doorbell mappings for mlx4. These resources are the low-level handles that RDMA and Ethernet queues use to isolate memory access, map doorbell pages, and obtain write-combining BlueFlame registers.

## Important APIs, types, and functions
- PD allocation is exposed by `mlx4_pd_alloc()` and `mlx4_pd_free()`.
- XRC domain allocation uses `__mlx4_xrcd_alloc()`, `mlx4_xrcd_alloc()`, `__mlx4_xrcd_free()`, and `mlx4_xrcd_free()`.
- Table setup and teardown are `mlx4_init_pd_table()`, `mlx4_cleanup_pd_table()`, `mlx4_init_xrcd_table()`, and `mlx4_cleanup_xrcd_table()`.
- UAR handling is `mlx4_uar_alloc()`, `mlx4_uar_free()`, `mlx4_init_uar_table()`, and `mlx4_cleanup_uar_table()`.
- BlueFlame allocation and release are `mlx4_bf_alloc()` and `mlx4_bf_free()`.
- Important state types include `struct mlx4_uar`, `struct mlx4_bf`, `priv->pd_bitmap`, `priv->xrcd_bitmap`, `priv->uar_table.bitmap`, `priv->bf_list`, `priv->bf_mutex`, and `priv->bf_mapping`.

## Control flow and integration
PD and native XRC allocation are direct bitmap operations. Multi-function XRC allocation is delegated to the master with wrapped `RES_XRCD` commands. UAR allocation reserves a UAR bitmap index, converts it to a BAR2 page frame number, and handles slave devices by folding the index into the visible BAR size.

BlueFlame allocation first reuses a partially free UAR from `priv->bf_list`. If none exists, it preserves a firmware-reserved UAR margin, allocates a new `struct mlx4_uar`, reserves a UAR, maps the regular page with `ioremap()`, maps the write-combining BlueFlame page through `io_mapping_map_wc()`, and then hands out one register slice by setting a bit in `free_bf_bmap`. Freeing clears that bit, returns non-full UARs to the list, and fully unmaps/frees the UAR when the last BlueFlame slice is released.

## State and persistence behavior
The file owns in-memory bitmap state for PDs, XRCDs, and UARs. `struct mlx4_uar` stores the allocated index, PFN, normal mapping, write-combining mapping, BlueFlame free-bit map, and list linkage. `struct mlx4_bf` stores the selected UAR, register pointer, offset, and buffer size. There is no disk persistence, but BAR mappings and write-combining mappings persist until explicit free or driver teardown.

## Dependencies
This code depends on mlx4 bitmap helpers, PCI BAR resources, `dev->caps` sizing fields, `mlx4_get_num_reserved_uar()`, Linux `ioremap()`/`iounmap()`, `io_mapping_map_wc()`/`io_mapping_unmap()`, mutexes, and multi-function command wrappers.

## Risks
- BlueFlame allocation must keep `priv->bf_list` and `free_bf_bmap` consistent under `bf_mutex`; a missed list update can hide or double-allocate a register slice.
- Error labels in the UAR mapping path must unmap and free in exact reverse order.
- Slave UAR PFN folding depends on BAR2 size and `uar_page_size`; wrong sizing maps the wrong doorbell page.
- The reserved UAR threshold protects firmware/internal use; relaxing it can starve reserved pages.
- XRC and UAR release failures in multi-function mode are only logged, leaving cleanup dependent on the master.

## Test signals
Tests should cover PD/XRCD bitmap exhaustion and reuse, UAR allocation on master and slave devices, BlueFlame allocation until a page is full, freeing slices in different orders, injected map failures at `ioremap()` and `io_mapping_map_wc()`, and module teardown with no leaked UAR mappings.
